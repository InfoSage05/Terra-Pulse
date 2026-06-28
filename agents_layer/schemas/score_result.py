from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from enum import Enum

class FlagEnum(str, Enum):
    low_source_count = "low_source_count"
    conflicting_signals = "conflicting_signals"
    recent_negative_news = "recent_negative_news"
    # Add more as needed
    
class ScoreResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    area_id: int
    summary: str
    livability_signal: float # -1.0 to 1.0
    confidence: float # 0.0 to 1.0
    flags: List[FlagEnum]
