from pydantic import BaseModel, ConfigDict, Field
from datetime import date
from typing import Optional

class PropertySaleSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sale_date: date
    price_eur: float = Field(gt=0)
    address_raw: str
    address_normalized: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    source_name: str
    source_record_id: Optional[str] = None
