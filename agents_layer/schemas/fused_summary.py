from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any
from .score_result import FlagEnum

class FusedSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    area_id: int
    run_id: str
    summary: str
    livability_signal: float
    confidence: float
    flags: List[FlagEnum]
    needs_human_review: bool
    structured_data_snapshot: Dict[str, Any]
    source_count: int
    model_name: str
    source_name: str = "agent_pipeline"
