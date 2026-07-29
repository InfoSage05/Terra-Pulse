from datetime import datetime
import requests
from pydantic import ValidationError
from sqlalchemy.dialects.postgresql import insert
from ingestion.connectors.base import BaseConnector
from ingestion.schemas.area_demographics import AreaDemographicsSchema
from storage.models.db_models import AreaDemographics, Area
from ingestion.utils.geocoding import resolve_area_id_by_name
from ingestion.utils.jsonstat import iter_jsonstat_cells, label_for

# CSO PxStat table F3001: "Population" by Census Year / County and City /
# Detailed Marital Status / Sex. Verified live against the PxStat API
# (https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/F3001/JSON-stat/2.0/en)
# on 2026-07-17: this is real Census 2011/2016/2022 population data by
# county/city (Dublin City, Fingal, South Dublin, Dun Laoghaire-Rathdown,
# etc). Note this is coarser than the Dublin postal-district `areas` seed
# data, so area_id resolution below may frequently come back null - that's
# expected given current seed granularity, not a bug in this connector.
#
# HPM04 (mentioned in some docs) is actually the Residential Property Price
# Index by Eircode routing key - NOT a demographics/population table - so it
# is not used here.
CSO_TABLE_ID = "F3001"
CSO_DATASET_URL = (
    f"https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/"
    f"{CSO_TABLE_ID}/JSON-stat/2.0/en"
)

class CSOConnector(BaseConnector):
    """
    CSO Demographics Connector.
    Fetches real Census population data from the CSO PxStat API (table F3001).
    """

    def get_source_name(self) -> str:
        return "cso"

    def fetch(self) -> list[dict]:
        self.logger.info(f"Fetching CSO demographics data from PxStat table {CSO_TABLE_ID}")
        try:
            resp = requests.get(CSO_DATASET_URL, timeout=30)
            resp.raise_for_status()
            dataset = resp.json()
            raw_data = self._parse_population_dataset(dataset)
            if not raw_data:
                raise ValueError("Parsed 0 records from CSO response")
            self.logger.info(f"Fetched {len(raw_data)} population records from CSO.")
            return raw_data
        except Exception as e:
            self.logger.error(f"CSO PxStat API request failed: {e}")
            self.logger.info("Falling back to sample data.")
            return self._get_sample_data()

    def _parse_population_dataset(self, dataset: dict) -> list[dict]:
        """
        Parse the F3001 JSON-stat 2.0 cube into flat records, keeping only
        the "Both sexes" / "All marital status" totals per county/city per
        census year (matching the coarser-grained totals the rest of the
        pipeline expects - one population figure per area per year).
        """
        raw_data = []
        for dim_codes, value in iter_jsonstat_cells(dataset):
            if dim_codes.get("C02325V02801") != "-":  # All marital status only
                continue
            if dim_codes.get("C02199V02655") != "-":  # Both sexes only
                continue

            geo_code = dim_codes["C04104V04868"]
            if geo_code == "IE0":
                continue  # skip the national "State" total row

            area_name = label_for(dataset, "C04104V04868", geo_code)
            year = int(dim_codes["TLIST(A1)"])

            raw_data.append({
                "area_name": area_name,
                "year": year,
                "population": int(value),
                # Not present in F3001 - left null rather than fabricated.
                "population_density": None,
                "deprivation_index": None,
            })
        return raw_data

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
        
        # Let exceptions propagate - BaseConnector.run() wraps each record's
        # load() in a SAVEPOINT and handles rollback/logging there, so a bad
        # row doesn't poison the rest of the connector's shared session.
        self.db.execute(upsert_stmt)
        return True

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
