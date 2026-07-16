import time
import requests
from datetime import datetime
from pydantic import ValidationError
from sqlalchemy.dialects.postgresql import insert
from ingestion.connectors.base import BaseConnector
from ingestion.schemas.amenity import AmenitySchema
from storage.models.db_models import Amenity, Area

# Overpass API requires a descriptive User-Agent identifying the client;
# requests' default UA (and overpy's urllib-based client, which sends none
# at all) gets rejected with HTTP 406 Not Acceptable. See:
# https://wiki.openstreetmap.org/wiki/Overpass_API#Introduction
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OVERPASS_HEADERS = {
    "User-Agent": "TerraPulse-Ingestion/1.0 (livability data platform; contact: shubhamkumar28436@gmail.com)"
}


class OSMConnector(BaseConnector):
    """
    OpenStreetMap Connector using the Overpass API.
    Fetches amenities per Area defined in the DB.
    """

    def get_source_name(self) -> str:
        return "osm"

    def fetch(self) -> list[dict]:
        self.logger.info("Fetching OSM data via Overpass API")

        # In a real implementation, we would extract the bounding box from the Area geometry.
        # For this prototype, we'll use a hardcoded bounding box for central Dublin to avoid
        # complex PostGIS bounding box queries inside the Python script.
        # Format: (south, west, north, east)
        # Dublin bbox approx: 53.2,-6.4,53.4,-6.1
        bbox = "53.2,-6.4,53.4,-6.1"

        query = f"""
        [out:json][timeout:25];
        (
          node["amenity"="school"]({bbox});
          node["amenity"="hospital"]({bbox});
          node["amenity"="doctors"]({bbox});
          node["amenity"="supermarket"]({bbox});
          node["leisure"="park"]({bbox});
          node["amenity"="police"]({bbox});
          node["highway"="bus_stop"]({bbox});
          node["railway"="stop"]({bbox});
        );
        out body;
        """

        try:
            raw_data = self._query_overpass(query)
            self.logger.info(f"Fetched {len(raw_data)} raw OSM nodes.")
            return raw_data
        except Exception as e:
            self.logger.error(f"Overpass API error: {e}")
            self.logger.info("Falling back to sample data.")
            return self._get_sample_data()

    def _query_overpass(self, query: str, max_retries: int = 3) -> list[dict]:
        """
        Query the Overpass API directly via requests (bypassing overpy, whose
        urllib-based client omits a User-Agent header and gets a 406 from
        Overpass). Parses the raw Overpass JSON response ourselves.
        """
        last_exc = None
        for attempt in range(1, max_retries + 1):
            try:
                resp = requests.post(
                    OVERPASS_URL,
                    data={"data": query},
                    headers=OVERPASS_HEADERS,
                    timeout=60,
                )
                if resp.status_code == 429 or resp.status_code >= 500:
                    # Rate limited or server overloaded - retry with backoff.
                    raise requests.exceptions.RequestException(
                        f"Overpass returned {resp.status_code}, retrying"
                    )
                resp.raise_for_status()
                payload = resp.json()
                break
            except Exception as e:
                last_exc = e
                self.logger.warning(f"Overpass request attempt {attempt}/{max_retries} failed: {e}")
                if attempt < max_retries:
                    time.sleep(2 * attempt)
        else:
            raise last_exc

        raw_data = []
        for element in payload.get("elements", []):
            if element.get("type") != "node":
                continue
            tags = element.get("tags", {}) or {}
            amenity_type = (
                tags.get("amenity")
                or tags.get("leisure")
                or tags.get("highway")
                or tags.get("railway")
                or "unknown"
            )
            raw_data.append({
                "osm_id": element["id"],
                "lat": float(element["lat"]),
                "lon": float(element["lon"]),
                "amenity_type": amenity_type,
                "name": tags.get("name"),
            })
        return raw_data

    def validate(self, raw_record: dict) -> AmenitySchema | None:
        try:
            validated = AmenitySchema(
                amenity_type=raw_record["amenity_type"],
                name=raw_record.get("name"),
                lat=raw_record["lat"],
                lon=raw_record["lon"],
                osm_id=raw_record["osm_id"],
                source_name=self.source_name
            )
            return validated
        except ValidationError as e:
            self.logger.debug(f"Validation error: {e}")
            return None

    def load(self, validated_record: AmenitySchema) -> bool:
        stmt = insert(Amenity).values(
            amenity_type=validated_record.amenity_type,
            name=validated_record.name,
            lat=validated_record.lat,
            lon=validated_record.lon,
            osm_id=validated_record.osm_id,
            source_name=validated_record.source_name
        )
        
        update_dict = {
            'ingested_at': datetime.now(),
            'name': validated_record.name,
            'lat': validated_record.lat,
            'lon': validated_record.lon
        }
        
        upsert_stmt = stmt.on_conflict_do_update(
            constraint='uq_amenities_osmid_type',
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
                "osm_id": 123456,
                "lat": 53.3498,
                "lon": -6.2603,
                "amenity_type": "school",
                "name": "Sample School"
            },
            {
                "osm_id": 654321,
                "lat": 53.3300,
                "lon": -6.2500,
                "amenity_type": "hospital",
                "name": "Sample Hospital"
            }
        ]
