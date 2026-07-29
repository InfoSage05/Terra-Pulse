import re
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


# Matches Irish Dublin postal districts embedded in a free-text address, e.g.
# "10 Some Street, Dublin 4", "Apt 2, Dublin 6W", "Dublin 24, Co. Dublin".
# Group 1 captures the district number/suffix (e.g. "4", "6W", "24").
_DUBLIN_DISTRICT_RE = re.compile(r"\bDublin\s*0?(\d{1,2}[WwEe]?)\b", re.IGNORECASE)


def extract_dublin_postal_district(address: Optional[str]) -> Optional[str]:
    """
    Extract a Dublin postal district (e.g. "Dublin 4", "Dublin 6W") from a raw
    address string. Returns the normalized district name (matching the
    naming convention used in `areas.name`, e.g. seed_areas.py) or None if no
    postal district could be found in the address.
    """
    if not address:
        return None

    match = _DUBLIN_DISTRICT_RE.search(address)
    if not match:
        return None

    suffix = match.group(1).upper()
    return f"Dublin {suffix}"


def resolve_area_id_from_address(db: Session, address: Optional[str]) -> Optional[int]:
    """
    Best-effort area resolution for a raw address string. Currently supports
    Dublin postal districts (the granularity `areas` are seeded at). Falls
    back to a plain fuzzy name match against the whole address if no
    postal district pattern is found (covers suburb-named areas like
    "Blackrock" or "Dun Laoghaire" that appear directly in the address).
    """
    district = extract_dublin_postal_district(address)
    if district:
        area_id = resolve_area_id_by_name(db, district)
        if area_id:
            return area_id

    if not address:
        return None

    # Fall back to checking whether any known suburb-style area name appears
    # verbatim in the address (e.g. "12 Main St, Blackrock, Co. Dublin").
    areas = db.query(Area.id, Area.name).filter(Area.area_type != 'postal_district').all()
    address_lower = address.lower()
    for area_id, area_name in areas:
        if area_name and area_name.lower() in address_lower:
            return area_id

    return None

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
