from datetime import datetime
from collections import defaultdict
import requests
from pydantic import ValidationError
from sqlalchemy.dialects.postgresql import insert
from ingestion.connectors.base import BaseConnector
from ingestion.schemas.crime_stat import CrimeStatSchema
from storage.models.db_models import CrimeStat
from ingestion.utils.geocoding import resolve_area_id_by_name
from ingestion.utils.jsonstat import iter_jsonstat_cells, label_for

# CSO PxStat table CJQ06: "Recorded crime incidents" by Quarter / Garda
# Division / Type of Offence. Verified live against the PxStat API
# (https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/CJQ06/JSON-stat/2.0/en)
# on 2026-07-17: this is real quarterly Garda-recorded-crime data broken
# down by the 28 Garda Divisions and ~85 offence types/subtypes (we keep
# only the 16 top-level 2-digit offence groups to match the granularity the
# rest of the pipeline expects). CJA01 (mentioned in some docs) only has
# national-level totals with no Garda Division breakdown, so it can't
# populate `garda_division` - CJQ06 is used instead.
CRIME_TABLE_ID = "CJQ06"
CRIME_DATASET_URL = (
    f"https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/"
    f"{CRIME_TABLE_ID}/JSON-stat/2.0/en"
)
GEO_DIM = "C02481V03160"     # Garda Division
OFFENCE_DIM = "C02480V03003"  # Type of Offence
QUARTER_DIM = "TLIST(Q1)"


class CrimeConnector(BaseConnector):
    """
    Garda Crime Statistics Connector.
    Fetches real quarterly recorded-crime data from the CSO PxStat API
    (table CJQ06), aggregated to yearly totals per Garda Division per
    top-level offence category.
    Note: Data is available only at the Garda Division level,
    so it joins at a coarser area level than other metrics.
    """

    def get_source_name(self) -> str:
        return "crime"

    def fetch(self) -> list[dict]:
        self.logger.info(f"Fetching Garda Crime data from PxStat table {CRIME_TABLE_ID}")
        try:
            resp = requests.get(CRIME_DATASET_URL, timeout=30)
            resp.raise_for_status()
            dataset = resp.json()
            raw_data = self._parse_crime_dataset(dataset)
            if not raw_data:
                raise ValueError("Parsed 0 records from CSO CJQ06 response")
            self.logger.info(f"Fetched {len(raw_data)} yearly crime records from CSO.")
            return raw_data
        except Exception as e:
            self.logger.error(f"CSO PxStat API request failed: {e}")
            self.logger.info("Falling back to sample data.")
            return self._get_sample_data()

    def _parse_crime_dataset(self, dataset: dict) -> list[dict]:
        """
        Parse the CJQ06 JSON-stat 2.0 cube (quarterly, per Garda Division,
        per detailed offence type) into yearly totals per Garda Division per
        top-level offence category, by summing the four quarters and all
        offence subtypes under each top-level 2-digit category code.
        """
        yearly_totals = defaultdict(float)

        for dim_codes, value in iter_jsonstat_cells(dataset):
            offence_code = dim_codes[OFFENCE_DIM]
            if len(offence_code) != 2:
                # Skip detailed subtype breakdowns (e.g. "0111"); keep only
                # the 16 top-level offence groups (e.g. "01").
                continue

            quarter_code = dim_codes[QUARTER_DIM]  # e.g. "20234"
            year = int(quarter_code[:4])
            garda_division = label_for(dataset, GEO_DIM, dim_codes[GEO_DIM])
            crime_category = label_for(dataset, OFFENCE_DIM, offence_code)

            key = (garda_division, year, crime_category)
            yearly_totals[key] += value

        raw_data = []
        for (garda_division, year, crime_category), count in yearly_totals.items():
            raw_data.append({
                "garda_division": garda_division,
                "year": year,
                "crime_category": crime_category,
                "count": int(count),
            })
        return raw_data

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
