import os
import sys
import logging

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy.orm import Session
from storage.scripts.db_connect import get_db
from storage.models.db_models import Area

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Basic seed data for Dublin postal districts
# In a real scenario, you'd load exact boundaries from a GeoJSON/Shapefile.
# For this phase, we use simple bounding boxes or polygons to represent the areas.
# These coords are very rough approximations.
DUBLIN_AREAS = [
    {"name": "Dublin 1", "area_type": "postal_district", "county": "Dublin", "geom": "POLYGON((-6.27 53.35, -6.24 53.35, -6.24 53.36, -6.27 53.36, -6.27 53.35))"},
    {"name": "Dublin 2", "area_type": "postal_district", "county": "Dublin", "geom": "POLYGON((-6.27 53.33, -6.24 53.33, -6.24 53.34, -6.27 53.34, -6.27 53.33))"},
    {"name": "Dublin 3", "area_type": "postal_district", "county": "Dublin", "geom": "POLYGON((-6.24 53.35, -6.20 53.35, -6.20 53.37, -6.24 53.37, -6.24 53.35))"},
    {"name": "Dublin 4", "area_type": "postal_district", "county": "Dublin", "geom": "POLYGON((-6.24 53.31, -6.18 53.31, -6.18 53.33, -6.24 53.33, -6.24 53.31))"},
    # Add a few suburbs
    {"name": "Blackrock", "area_type": "suburb", "county": "Dublin", "geom": "POLYGON((-6.19 53.29, -6.16 53.29, -6.16 53.31, -6.19 53.31, -6.19 53.29))"},
    {"name": "Dún Laoghaire", "area_type": "suburb", "county": "Dublin", "geom": "POLYGON((-6.15 53.28, -6.12 53.28, -6.12 53.30, -6.15 53.30, -6.15 53.28))"},
]

def seed_areas(db: Session):
    for area_data in DUBLIN_AREAS:
        # Check if exists
        existing = db.query(Area).filter(Area.name == area_data["name"]).first()
        if not existing:
            area = Area(
                name=area_data["name"],
                area_type=area_data["area_type"],
                county=area_data["county"],
                geometry=f"SRID=4326;{area_data['geom']}"
            )
            db.add(area)
            logger.info(f"Added area: {area_data['name']}")
        else:
            logger.info(f"Area already exists: {area_data['name']}")
    
    db.commit()

if __name__ == "__main__":
    db_gen = get_db()
    db = next(db_gen)
    try:
        logger.info("Starting area seeding...")
        seed_areas(db)
        logger.info("Area seeding completed.")
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        db.rollback()
    finally:
        db.close()
