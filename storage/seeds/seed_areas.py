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
# These coords are very rough approximations, laid out on a grid across the
# Dublin bounding box (53.2,-6.4 to 53.4,-6.1) so each district still gets a
# distinct, non-overlapping cell for PostGIS point-in-polygon lookups
# (resolve_area_id_by_point), even though the shapes don't reflect real
# boundaries. Postal district list and name-matching coverage (Dublin 1-24,
# plus 6W) was derived from the real 250k-row PPR export - see
# ingestion/utils/geocoding.py::extract_dublin_postal_district.
def _grid_polygon(col: int, row: int, cell: float = 0.028) -> str:
    lon0 = -6.40 + col * cell
    lat0 = 53.20 + row * cell
    lon1 = lon0 + cell
    lat1 = lat0 + cell
    return f"POLYGON(({lon0} {lat0}, {lon1} {lat0}, {lon1} {lat1}, {lon0} {lat1}, {lon0} {lat0}))"

# (name, grid_col, grid_row) - grid is roughly 10 cols x 7 rows across the Dublin bbox
_POSTAL_DISTRICT_GRID = [
    ("Dublin 1", 5, 5), ("Dublin 2", 5, 4), ("Dublin 3", 6, 5), ("Dublin 4", 5, 3),
    ("Dublin 5", 7, 5), ("Dublin 6", 4, 3), ("Dublin 6W", 3, 3), ("Dublin 7", 4, 5),
    ("Dublin 8", 4, 4), ("Dublin 9", 6, 6), ("Dublin 10", 2, 4), ("Dublin 11", 4, 6),
    ("Dublin 12", 3, 4), ("Dublin 13", 8, 6), ("Dublin 14", 5, 2), ("Dublin 15", 2, 6),
    ("Dublin 16", 4, 2), ("Dublin 17", 7, 6), ("Dublin 18", 6, 1), ("Dublin 19", 8, 5),
    ("Dublin 20", 2, 5), ("Dublin 22", 1, 4), ("Dublin 24", 2, 3),
]

DUBLIN_AREAS = [
    {"name": name, "area_type": "postal_district", "county": "Dublin", "geom": _grid_polygon(col, row)}
    for name, col, row in _POSTAL_DISTRICT_GRID
] + [
    # A few named suburbs outside the postal-district numbering scheme
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
