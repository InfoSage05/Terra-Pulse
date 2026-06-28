from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from storage.models.db_models import Area

def resolve_area_id_by_name(db: Session, area_name: str) -> Optional[int]:
    """
    Look up area by exact name match.
    """
    area = db.query(Area.id).filter(Area.name.ilike(f"%{area_name}%")).first()
    return area[0] if area else None

def resolve_area_id_by_point(db: Session, lat: float, lon: float) -> Optional[int]:
    """
    Look up area_id by finding which Area polygon contains the given lat/lon.
    Uses PostGIS ST_Contains.
    """
    query = text("""
        SELECT id FROM areas
        WHERE ST_Contains(geometry, ST_SetSRID(ST_Point(:lon, :lat), 4326))
        LIMIT 1;
    """)
    result = db.execute(query, {"lat": lat, "lon": lon}).first()
    return result[0] if result else None
