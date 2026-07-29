import uuid
from typing import List, Dict, Any
from agents_layer.llm_client import LLMClient
from agents_layer.steps.extract import run_extract
from agents_layer.steps.score import run_score
from agents_layer.steps.fuse import run_fuse
from agents_layer.schemas.fused_summary import FusedSummary
from ingestion.utils.logging_config import setup_logger

logger = setup_logger("agent_pipeline")

def run_pipeline_for_area(
    area_id: int, 
    raw_texts: List[str], 
    structured_data: Dict[str, Any],
    llm_client: LLMClient
) -> FusedSummary | None:
    """
    Orchestrates extract -> score -> fuse for one area.
    """
    logger.info(f"Starting agent pipeline for area_id {area_id} with {len(raw_texts)} sources.")
    
    run_id = str(uuid.uuid4())

    # Step 1: Extract
    extractions = []
    for text in raw_texts:
        ext = run_extract(text, area_id, llm_client)
        if ext:
            extractions.append(ext)
            
    if not extractions:
        logger.warning(f"No valid extractions produced for area_id {area_id}. Aborting pipeline.")
        return None
        
    # Step 2: Score / Summarise
    score_result = run_score(extractions, area_id, llm_client)
    if not score_result:
        logger.warning(f"Scoring failed for area_id {area_id}. Aborting pipeline.")
        return None
        
    # Step 3: Fuse
    # Read model_name AFTER the LLM calls above, since LLMClient may have
    # fallen back to a different model than the one it was configured with
    # (self.model_name is updated in place on a successful fallback call).
    fused_summary = run_fuse(
        score=score_result,
        run_id=run_id,
        model_name=llm_client.model_name,
        structured_data=structured_data,
        source_count=len(raw_texts)
    )
    
    logger.info(f"Pipeline completed for area_id {area_id}. Needs review: {fused_summary.needs_human_review}")
    return fused_summary
