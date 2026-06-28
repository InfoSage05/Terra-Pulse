from pydantic import BaseModel, ConfigDict
from typing import Optional

class AmenitySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    amenity_type: str
    name: Optional[str] = None
    lat: float
    lon: float
    osm_id: int
    source_name: str
