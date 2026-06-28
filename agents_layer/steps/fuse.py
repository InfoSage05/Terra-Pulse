from typing import Dict, Any
import uuid
from agents_layer.schemas.score_result import ScoreResult
from agents_layer.schemas.fused_summary import FusedSummary

def run_fuse(score: ScoreResult, run_id: str, model_name: str, structured_data: Dict[str, Any], source_count: int) -> FusedSummary:
    """
    Step 3: Fuse + Review Gate
    Deterministic comparison logic (NO LLM call).
    Compares qualitative agent signal to structured data and flags for human review if they conflict.
    """
    needs_human_review = False
    
    # 1. Low confidence check
    if score.confidence < 0.3:
        needs_human_review = True
        
    # 2. Conflict detection logic
    agent_positive = score.livability_signal > 0.2
    agent_negative = score.livability_signal < -0.2
    
    # Example logic: if agent is positive but crime is rising fast (say >20%), that's a conflict.
    # In a real scenario, structured_data would contain computed trends (e.g. crime_growth_rate).
    # We will simulate a simple rule:
    crime_trend = structured_data.get('crime_trend', 0.0) # > 0 means rising crime
    price_trend = structured_data.get('price_trend', 0.0) # > 0 means rising prices
    
    # If agent is very positive but crime is rising fast (> 10%)
    if agent_positive and crime_trend > 0.1:
        needs_human_review = True
        
    # If agent is very negative but prices are booming (> 10%)
    if agent_negative and price_trend > 0.1:
        needs_human_review = True

    fused = FusedSummary(
        area_id=score.area_id,
        run_id=run_id,
        summary=score.summary,
        livability_signal=score.livability_signal,
        confidence=score.confidence,
        flags=score.flags,
        needs_human_review=needs_human_review,
        structured_data_snapshot=structured_data,
        source_count=source_count,
        model_name=model_name,
        source_name="agent_pipeline"
    )
    
    return fused
