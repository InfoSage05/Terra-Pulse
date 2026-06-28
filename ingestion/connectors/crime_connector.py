from datetime import datetime
from pydantic import ValidationError
from sqlalchemy.dialects.postgresql import insert
from ingestion.connectors.base import BaseConnector
from ingestion.schemas.crime_stat import CrimeStatSchema
from storage.models.db_models import CrimeStat
from ingestion.utils.geocoding import resolve_area_id_by_name

class CrimeConnector(BaseConnector):
    """
    Garda Crime Statistics Connector.
    Note: Data is available only at the Garda Division level, 
    so it joins at a coarser area level than other metrics.
    """
    
    def get_source_name(self) -> str:
        return "crime"

    def fetch(self) -> list[dict]:
        self.logger.info("Fetching Garda Crime data")
        return self._get_sample_data()

    def validate(self, raw_record: dict) -> CrimeStatSchema | None:
        try:
            validated = CrimeStatSchema(
                garda_division=raw_record["garda_division"],
                year=raw_record["year"],
                crime_category=raw_record["crime_category"],
                count=raw_record["count"],
                source_name=self.source_name
            )
            return validated
        except ValidationError as e:
            self.logger.debug(f"Validation error: {e}")
            return None

    def load(self, validated_record: CrimeStatSchema) -> bool:
        # Try to find a matching area_id (Garda division)
        area_id = resolve_area_id_by_name(self.db, validated_record.garda_division)
            
        stmt = insert(CrimeStat).values(
            area_id=area_id,
            garda_division=validated_record.garda_division,
            year=validated_record.year,
            crime_category=validated_record.crime_category,
            count=validated_record.count,
            source_name=validated_record.source_name
        )
        
        update_dict = {
            'ingested_at': datetime.now(),
            'count': validated_record.count
        }
        
        upsert_stmt = stmt.on_conflict_do_update(
            constraint='uq_crime_stats_area_div_year_cat',
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
                "garda_division": "D.M.R. North Central",
                "year": 2023,
                "crime_category": "Burglary",
                "count": 150
            },
            {
                "garda_division": "D.M.R. South Central",
                "year": 2023,
                "crime_category": "Burglary",
                "count": 210
            }
        ]
