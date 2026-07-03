from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, List

class ModelType(str, Enum):
    PRICE_PREDICTION = "price_prediction"
    AFFORDABILITY_SCORE = "affordability_score"
    SAFETY_SCORE = "safety_score"
    LIVABILITY_SCORE = "livability_score"

class ModelMetadata(BaseModel):
    model_type: ModelType
    version: str              # e.g. "2026-06-29_v1"
    trained_at: datetime
    training_row_count: int
    feature_names: List[str]
    metric_name: str           # e.g. "MAE", "RMSE"
    metric_value: float
    is_active: bool             # only one version per model_type should be active at a time

class PricePredictionInput(BaseModel):
    area_id: int
    # Phase 1 data does not support property-level features like property_type or size_sqm.
    # Therefore, prediction relies solely on area-level metrics.

class PricePredictionOutput(BaseModel):
    area_id: int
    predicted_price_eur: float
    confidence_interval_low: float
    confidence_interval_high: float
    model_version: str          # must match an entry in the model registry

class AreaScoreOutput(BaseModel):
    area_id: int
    affordability_score: Optional[float]   # 0-100, null if insufficient data
    safety_score: Optional[float]
    livability_score: Optional[float]       # blends structured score + agent livability_signal
    livability_confidence: Optional[float]  # carried through from area_agent_summaries.confidence
    needs_human_review: bool             # carried through from Phase 2's flag
    agent_summary: Optional[str] = None    # unstructured agent-generated summary text
    model_versions_used: Dict[str, str]   # which model version produced each sub-score
    last_updated: datetime

class PropertyListing(BaseModel):
    id: int
    area_id: int
    address_raw: str
    price_eur: float
    sale_date: str
    property_type: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
