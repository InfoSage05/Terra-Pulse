import os
import json
import logging
from typing import Type, TypeVar, Any
from pydantic import BaseModel, ValidationError
import anthropic

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

class LLMClient:
    """
    Thin wrapper around the Anthropic API client.
    Handles the API call, retries on transient errors, and enforces JSON-only output.
    """
    
    def __init__(self, model_name: str = "claude-3-5-sonnet-20240620"):
        self.model_name = model_name
        
        # Check for API key
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            logger.warning("ANTHROPIC_API_KEY is not set. API calls will fail unless mocked.")
            
        self.client = anthropic.Anthropic(api_key=api_key)

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
        Retries once if validation fails.
        """
        system_prompt = f"""You are a data extraction assistant.
You must respond with ONLY valid JSON matching the following schema.
No preamble, no markdown fences, no conversational text.

Schema:
{schema_class.model_json_schema()}
"""
        
        current_prompt = prompt
        
        for attempt in range(retry_count + 1):
            try:
                # If we don't have an API key, we should not attempt a real call.
                # Here we could raise an error or return None.
                if not os.environ.get("ANTHROPIC_API_KEY"):
                    raise ValueError("Missing ANTHROPIC_API_KEY")

                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=1024,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": current_prompt}
                    ]
                )
                
                raw_text = response.content[0].text
                clean_json = self._clean_json_response(raw_text)
                
                # Try to parse and validate
                data_dict = json.loads(clean_json)
                validated_obj = schema_class.model_validate(data_dict)
                return validated_obj
                
            except json.JSONDecodeError as e:
                error_msg = f"Failed to parse JSON. Error: {e}\nRaw output: {raw_text}"
                logger.warning(f"Attempt {attempt + 1}: {error_msg}")
                current_prompt = prompt + f"\n\nPrevious attempt failed with JSONDecodeError: {e}. Ensure you output strictly valid JSON."
                
            except ValidationError as e:
                error_msg = f"Failed Pydantic validation. Error: {e}\nRaw output: {raw_text}"
                logger.warning(f"Attempt {attempt + 1}: {error_msg}")
                current_prompt = prompt + f"\n\nPrevious attempt failed schema validation: {e}. Fix the structure to match the schema exactly."
                
            except Exception as e:
                logger.error(f"LLM API call failed: {e}")
                # Don't retry on Auth/Network errors for this simple wrapper
                break
                
        logger.error(f"Failed to generate valid structured data after {retry_count + 1} attempts.")
        return None
