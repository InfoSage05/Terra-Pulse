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
DEFAULT_FALLBACK_MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "qwen/qwen3-next-80b-a3b-instruct:free",
    "nousresearch/hermes-3-llama-3.1-405b:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "openai/gpt-oss-20b:free",
]


class LLMClient:
    """
    Thin wrapper around the OpenAI-compatible API client (OpenRouter/Groq).
    Handles the API call, retries on transient errors, enforces JSON-only
    output, and falls back across multiple free models if the primary one
    is rate-limited upstream.
    """

    def __init__(self, model_name: str = None):
        self.model_name = model_name or os.environ.get("OPENROUTER_MODEL", "meta-llama/llama-3-8b-instruct:free")

        # Build the ordered list of models to try: the configured/primary
        # model first, then the fallback candidates (deduped, primary kept
        # first). Extra fallbacks can be supplied via OPENROUTER_FALLBACK_MODELS
        # (comma-separated) to override the built-in list.
        env_fallbacks = os.environ.get("OPENROUTER_FALLBACK_MODELS")
        fallback_pool = [m.strip() for m in env_fallbacks.split(",") if m.strip()] if env_fallbacks else DEFAULT_FALLBACK_MODELS
        self.model_candidates = [self.model_name] + [m for m in fallback_pool if m != self.model_name]

        # Check for API key
        api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("GROQ_API_KEY")
        if not api_key:
            logger.warning("OPENROUTER_API_KEY / GROQ_API_KEY is not set. API calls will fail unless mocked.")
            api_key = "dummy_key_for_mocking"

        # Configure base_url based on which key is present (assuming OpenRouter by default)
        base_url = "https://openrouter.ai/api/v1" if os.environ.get("OPENROUTER_API_KEY") else "https://api.groq.com/openai/v1"

        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )

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

        if not (os.environ.get("OPENROUTER_API_KEY") or os.environ.get("GROQ_API_KEY")):
            logger.error("Missing API Key (OPENROUTER_API_KEY or GROQ_API_KEY). Cannot call LLM.")
            return None

        raw_text = ""

        # Outer loop: try each candidate model in order (fallback on
        # rate-limit/connection/API errors). Inner loop: retry the SAME model
        # with a corrective prompt on JSON/schema validation failures.
        for model in self.model_candidates:
            current_prompt = prompt

            for attempt in range(retry_count + 1):
                try:
                    response = self.client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": current_prompt}
                        ],
                        response_format={"type": "json_object"},
                        max_tokens=1024,
                        temperature=0.0
                    )

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
                    logger.warning(f"Model {model}, attempt {attempt + 1}: RateLimitError: {e}. Trying next fallback model.")
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

        logger.error(f"Failed to generate valid structured data after trying {len(self.model_candidates)} model(s).")
        return None
