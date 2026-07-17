import os
import json
import logging
import time
from typing import Type, TypeVar
from pydantic import BaseModel, ValidationError
from openai import OpenAI, APIError, APIConnectionError, RateLimitError

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

# OpenRouter's free-tier (":free" suffix) models are backed by shared,
# frequently-saturated upstream providers and return 429s often (confirmed
# empirically - see agents_layer notes). To keep the pipeline usable despite
# this, LLMClient will fall back through a short list of other known-good
# free models if the configured primary model is rate-limited/unavailable,
# rather than giving up outright. All candidates are free, non-proprietary
# models available on OpenRouter, consistent with the "no paid LLM
# dependencies" project rule.
DEFAULT_OPENROUTER_FALLBACK_MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "qwen/qwen3-next-80b-a3b-instruct:free",
    "nousresearch/hermes-3-llama-3.1-405b:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "openai/gpt-oss-20b:free",
]

# Groq's free tier runs on its own LPU infrastructure with its own quota -
# it does NOT share OpenRouter's congested free-model pool, so trying Groq
# first meaningfully offloads pressure from OpenRouter rather than just
# adding another candidate to the same bottleneck. Both are open-source
# models, consistent with the "no paid LLM dependencies" project rule.
DEFAULT_GROQ_FALLBACK_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]


class LLMClient:
    """
    Thin wrapper around the OpenAI-compatible API clients for Groq and
    OpenRouter. Handles the API call, retries on transient errors, enforces
    JSON-only output, and falls back across multiple free models/providers
    if the primary one is rate-limited upstream. When both GROQ_API_KEY and
    OPENROUTER_API_KEY are set, Groq's models are tried first (separate,
    less-congested quota), with OpenRouter's model list as a second line of
    fallback - this spreads load across two independent free tiers instead
    of hammering one.
    """

    def __init__(self, model_name: str = None):
        self.model_name = model_name or os.environ.get("OPENROUTER_MODEL", "meta-llama/llama-3-8b-instruct:free")

        # Free-tier models (on either provider) can hang far longer than a
        # normal API call under load; without an explicit timeout the SDK's
        # default (up to 10 minutes) lets one stuck call stall the whole
        # pipeline instead of failing fast into the next fallback.
        common_client_kwargs = dict(timeout=30.0, max_retries=0)

        # Build the ordered list of (client, model) candidates to try. Groq
        # first (separate quota from OpenRouter's shared free pool), then
        # OpenRouter (configured/primary model first, then its fallback
        # list). Either provider is optional - only its configured API key
        # needs to be present.
        self.model_candidates = []

        groq_api_key = os.environ.get("GROQ_API_KEY")
        if groq_api_key:
            groq_client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=groq_api_key, **common_client_kwargs)
            env_groq_models = os.environ.get("GROQ_FALLBACK_MODELS")
            groq_models = [m.strip() for m in env_groq_models.split(",") if m.strip()] if env_groq_models else DEFAULT_GROQ_FALLBACK_MODELS
            self.model_candidates += [{"client": groq_client, "model": m} for m in groq_models]

        openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
        if openrouter_api_key:
            openrouter_client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=openrouter_api_key, **common_client_kwargs)
            env_or_fallbacks = os.environ.get("OPENROUTER_FALLBACK_MODELS")
            or_fallback_pool = [m.strip() for m in env_or_fallbacks.split(",") if m.strip()] if env_or_fallbacks else DEFAULT_OPENROUTER_FALLBACK_MODELS
            or_models = [self.model_name] + [m for m in or_fallback_pool if m != self.model_name]
            self.model_candidates += [{"client": openrouter_client, "model": m} for m in or_models]

        if not self.model_candidates:
            logger.warning("Neither GROQ_API_KEY nor OPENROUTER_API_KEY is set. API calls will fail.")

    def _clean_json_response(self, text: str) -> str:
        """Strip markdown fences from response if present."""
        text = text.strip()
        if text.startswith("```json"):
            text = text[len("```json"):]
        elif text.startswith("```"):
            text = text[len("```"):]
            
        if text.endswith("```"):
            text = text[:-3]
            
        return text.strip()

    def generate_structured(self, prompt: str, schema_class: Type[T], retry_count: int = 1) -> T | None:
        """
        Sends a prompt to the LLM and forces the output to match a Pydantic schema.
        Retries on JSON/schema validation failure (corrective re-prompt on the same
        model), and falls back to the next candidate model on rate-limit/connection
        errors, since OpenRouter's free models frequently get rate-limited upstream.
        """
        system_prompt = f"""You are a data extraction assistant.
You must respond with ONLY valid JSON matching the following schema.
No preamble, no markdown fences, no conversational text.

Schema:
{schema_class.model_json_schema()}
"""

        if not self.model_candidates:
            logger.error("Missing API Key (GROQ_API_KEY or OPENROUTER_API_KEY). Cannot call LLM.")
            return None

        raw_text = ""

        # OpenRouter's free-tier models are frequently all routed through the
        # same congested upstream provider - empirically, every candidate in
        # DEFAULT_OPENROUTER_FALLBACK_MODELS can 429 with the same
        # 'provider_name' in the same few seconds, so cycling models alone
        # doesn't help. Sweep the full candidate list (Groq models first,
        # then OpenRouter's) up to SWEEP_COUNT times, backing off between
        # sweeps using the Retry-After the API itself reports (capped), which
        # gives the shared pool a real chance to drain instead of hot-looping
        # into guaranteed repeat 429s.
        SWEEP_COUNT = 3
        MAX_BACKOFF_SECONDS = 25

        for sweep in range(SWEEP_COUNT):
            observed_retry_after = None

            # Outer loop: try each (client, model) candidate in order
            # (fallback on rate-limit/connection/API errors). Inner loop:
            # retry the SAME candidate with a corrective prompt on
            # JSON/schema validation failures.
            for candidate in self.model_candidates:
                client, model = candidate["client"], candidate["model"]
                current_prompt = prompt

                for attempt in range(retry_count + 1):
                    try:
                        response = client.chat.completions.create(
                            model=model,
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": current_prompt}
                            ],
                            response_format={"type": "json_object"},
                            max_tokens=1024,
                            temperature=0.0
                        )

                        if not response or not response.choices:
                            raise ValueError("Empty response (no choices) from API")

                        raw_text = response.choices[0].message.content or ""
                        clean_json = self._clean_json_response(raw_text)

                        # Try to parse and validate
                        data_dict = json.loads(clean_json)
                        validated_obj = schema_class.model_validate(data_dict)
                        # Remember which model actually produced this result so
                        # downstream callers (pipeline.py records this against
                        # the fused summary) report the true model used.
                        self.model_name = model
                        return validated_obj

                    except json.JSONDecodeError as e:
                        error_msg = f"Failed to parse JSON. Error: {e}\nRaw output: {raw_text}"
                        logger.warning(f"Model {model}, attempt {attempt + 1}: {error_msg}")
                        current_prompt = prompt + f"\n\nPrevious attempt failed with JSONDecodeError: {e}. Ensure you output strictly valid JSON."

                    except ValidationError as e:
                        error_msg = f"Failed Pydantic validation. Error: {e}\nRaw output: {raw_text}"
                        logger.warning(f"Model {model}, attempt {attempt + 1}: {error_msg}")
                        current_prompt = prompt + f"\n\nPrevious attempt failed schema validation: {e}. Fix the structure to match the schema exactly."

                    except RateLimitError as e:
                        retry_after = self._extract_retry_after(e)
                        if retry_after is not None:
                            observed_retry_after = max(observed_retry_after or 0, retry_after)
                        logger.warning(f"Model {model}, attempt {attempt + 1}: RateLimitError (retry_after={retry_after}). Trying next fallback model.")
                        break  # move to next candidate model immediately

                    except APIConnectionError as e:
                        logger.warning(f"Model {model}, attempt {attempt + 1}: APIConnectionError: {e}. Sleeping 2 seconds and retrying.")
                        time.sleep(2)

                    except APIError as e:
                        logger.error(f"Model {model}: OpenAI API Error: {e}. Trying next fallback model.")
                        break  # this model/provider may be broken; try the next one

                    except Exception as e:
                        logger.error(f"Model {model}: LLM API call failed: {e}. Trying next fallback model.")
                        break

            if sweep < SWEEP_COUNT - 1:
                backoff = min(observed_retry_after or 15, MAX_BACKOFF_SECONDS)
                logger.warning(f"All {len(self.model_candidates)} model(s) rate-limited/failed on sweep {sweep + 1}/{SWEEP_COUNT}. Backing off {backoff}s before retrying.")
                time.sleep(backoff)

        logger.error(f"Failed to generate valid structured data after {SWEEP_COUNT} sweep(s) of {len(self.model_candidates)} model(s).")
        return None

    @staticmethod
    def _extract_retry_after(error: RateLimitError) -> float | None:
        """Best-effort extraction of the API's suggested Retry-After (seconds) from a RateLimitError."""
        try:
            response = getattr(error, "response", None)
            header_val = response.headers.get("Retry-After") if response is not None else None
            if header_val is not None:
                return float(header_val)
        except (ValueError, AttributeError):
            pass
        try:
            body = getattr(error, "body", None) or {}
            metadata = body.get("error", {}).get("metadata", {}) if isinstance(body, dict) else {}
            if "retry_after_seconds" in metadata:
                return float(metadata["retry_after_seconds"])
        except (ValueError, AttributeError):
            pass
        return None
