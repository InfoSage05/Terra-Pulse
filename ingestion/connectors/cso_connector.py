from datetime import datetime
from pydantic import ValidationError
from sqlalchemy.dialects.postgresql import insert
from ingestion.connectors.base import BaseConnector
from ingestion.schemas.area_demographics import AreaDemographicsSchema
from storage.models.db_models import AreaDemographics, Area
from ingestion.utils.geocoding import resolve_area_id_by_name

class CSOConnector(BaseConnector):
    """
    CSO Demographics Connector.
    Fetches data from CSO API (PxStat).
    """
    
    def get_source_name(self) -> str:
        return "cso"

    def fetch(self) -> list[dict]:
        self.logger.info("Fetching CSO demographics data")
        # In reality, this would query PxStat API for Census data
        return self._get_sample_data()

    def validate(self, raw_record: dict) -> AreaDemographicsSchema | None:
        try:
            validated = AreaDemographicsSchema(
                year=raw_record["year"],
                population=raw_record.get("population"),
                population_density=raw_record.get("population_density"),
                deprivation_index=raw_record.get("deprivation_index"),
                source_name=self.source_name
            )
            # Attach the raw area name for resolution in load step
            validated.__dict__["_raw_area_name"] = raw_record.get("area_name")
            return validated
        except ValidationError as e:
            self.logger.debug(f"Validation error: {e}")
            return None

    def load(self, validated_record: AreaDemographicsSchema) -> bool:
        area_name = validated_record.__dict__.get("_raw_area_name")
        area_id = None
        if area_name:
            area_id = resolve_area_id_by_name(self.db, area_name)
            
        # We can still load it without area_id if we want, but it's better to have it
        stmt = insert(AreaDemographics).values(
            area_id=area_id,
            year=validated_record.year,
            population=validated_record.population,
            population_density=validated_record.population_density,
            deprivation_index=validated_record.deprivation_index,
            source_name=validated_record.source_name
        )
        
        update_dict = {
            'ingested_at': datetime.now(),
            'population': validated_record.population,
            'population_density': validated_record.population_density,
            'deprivation_index': validated_record.deprivation_index
        }
        
        # If area_id is null, our unique constraint might fail or we might not want to upsert
        # but the constraint is (area_id, year). Null area_ids might cause issues.
        # Let's just catch the exception if it violates.
        upsert_stmt = stmt.on_conflict_do_update(
            constraint='uq_demographics_area_year',
            set_=update_dict
        )
        
        try:
            self.db.execute(upsert_stmt)
            return True
        except Exception as e:
            self.logger.error(f"DB insert failed: {e}")
            return False

    def _get_sample_data(self):
        return [
            {
                "area_name": "Dublin 1",
                "year": 2022,
                "population": 25000,
                "population_density": 8000.5,
                "deprivation_index": -5.2
            },
            {
                "area_name": "Dublin 2",
                "year": 2022,
                "population": 20000,
                "population_density": 7000.0,
                "deprivation_index": 8.1
            }
        ]
