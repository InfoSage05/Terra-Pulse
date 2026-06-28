from pydantic import BaseModel, ConfigDict

class CrimeStatSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    garda_division: str
    year: int
    crime_category: str
    count: int
    source_name: str
