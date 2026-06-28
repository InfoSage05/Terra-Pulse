from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any

class AreaDemographicsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    year: int
    population: Optional[int] = None
    population_density: Optional[float] = None
    deprivation_index: Optional[float] = None
    age_profile_json: Optional[Dict[str, Any]] = None
    source_name: str
