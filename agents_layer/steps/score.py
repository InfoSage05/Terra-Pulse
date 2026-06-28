import os
import json
from datetime import datetime
from typing import List
from agents_layer.llm_client import LLMClient
from agents_layer.schemas.extraction_result import ExtractionResult
from agents_layer.schemas.score_result import ScoreResult, FlagEnum
from ingestion.utils.logging_config import setup_logger

logger = setup_logger("score_step")

def run_score(extractions: List[ExtractionResult], area_id: int, llm_client: LLMClient, confidence_threshold: float = 0.3) -> ScoreResult | None:
    """
    Step 2: Score / Summarise
    Aggregates extraction results, generates a cohesive summary, and scores the area.
    """
    if not extractions:
        return None
        
    extractions_json = [ext.model_dump() for ext in extractions]
    
    prompt = f"""Summarize and score the livability trajectory of an area based on the following extracted signals from various sources.
    
    Area ID: {area_id}
    Extracted Data:
    {json.dumps(extractions_json, indent=2)}
    
    Instructions for livability_signal:
    - -1.0 means strongly negative trajectory (e.g., rising crime, closures)
    - 0.0 means neutral or stable
    - 1.0 means strongly positive trajectory (e.g., new amenities, development)
    
    Provide a fresh 2-3 sentence summary in plain English.
    Rate your confidence from 0.0 to 1.0 based on the volume and consistency of the provided sources.
    """
    
    result = llm_client.generate_structured(prompt=prompt, schema_class=ScoreResult, retry_count=1)
    
    if not result:
        _dead_letter_score({"area_id": area_id, "extractions_count": len(extractions)}, "Failed to generate valid score from LLM")
        return None
        
    # Enforce logic: if confidence < threshold, add 'low_source_count' flag.
    if result.confidence < confidence_threshold:
        if FlagEnum.low_source_count not in result.flags:
            result.flags.append(FlagEnum.low_source_count)
            
    # Also enforce area_id matches what was passed in
    result.area_id = area_id
    
    return result

def _dead_letter_score(record: dict, reason: str):
    """Write invalid score generation to a dead letter file."""
    dead_letter_dir = os.path.join(
        os.path.dirname(__file__), '../../data/dead_letter/agent_score/'
    )
    os.makedirs(dead_letter_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    filename = f"score_fail_{timestamp}.json"
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
