import os
import json
from datetime import datetime
from agents_layer.llm_client import LLMClient
from agents_layer.schemas.extraction_result import ExtractionResult
from ingestion.utils.logging_config import setup_logger

logger = setup_logger("extract_step")

def run_extract(raw_text: str, area_id: int, llm_client: LLMClient) -> ExtractionResult | None:
    """
    Step 1: Extract
    Turns raw unstructured text into structured fields: topics, key_facts, sentiment, mentioned_entities.
    """
    prompt = f"""Extract key information from the following text regarding a specific geographic area.
    
Text:
{raw_text}
"""
    
    result = llm_client.generate_structured(prompt=prompt, schema_class=ExtractionResult, retry_count=1)
    
    if not result:
        _dead_letter_extract({"text": raw_text, "area_id": area_id}, "Failed to generate valid extraction from LLM")
        return None
        
    return result

def _dead_letter_extract(record: dict, reason: str):
    """Write invalid extraction to a dead letter file."""
    dead_letter_dir = os.path.join(
        os.path.dirname(__file__), '../../data/dead_letter/agent_extract/'
    )
    os.makedirs(dead_letter_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    filename = f"extract_fail_{timestamp}.json"
    filepath = os.path.join(dead_letter_dir, filename)
    
    payload = {
        "timestamp": datetime.now().isoformat(),
        "reason": reason,
        "record": record
    }
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to write dead letter: {e}")
