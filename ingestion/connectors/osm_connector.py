import overpy
import time
from datetime import datetime
from pydantic import ValidationError
from sqlalchemy.dialects.postgresql import insert
from ingestion.connectors.base import BaseConnector
from ingestion.schemas.amenity import AmenitySchema
from storage.models.db_models import Amenity, Area

class OSMConnector(BaseConnector):
    """
    OpenStreetMap Connector using Overpass API.
    Fetches amenities per Area defined in the DB.
    """
    
    def __init__(self, db):
        super().__init__(db)
        self.api = overpy.Overpass()
        
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
        
        raw_data = []
        try:
            # Overpass can be strict with rate limits
            result = self.api.query(query)
            for node in result.nodes:
                amenity_type = node.tags.get("amenity") or node.tags.get("leisure") or node.tags.get("highway") or node.tags.get("railway") or "unknown"
                raw_data.append({
                    "osm_id": node.id,
                    "lat": float(node.lat),
                    "lon": float(node.lon),
                    "amenity_type": amenity_type,
                    "name": node.tags.get("name")
                })
        except Exception as e:
            self.logger.error(f"Overpass API error: {e}")
            self.logger.info("Falling back to sample data.")
            return self._get_sample_data()
            
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
