from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional

import json

def get_areas(db: Session, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    query = text("""
        SELECT a.id, a.name, a.area_type, a.county, ST_AsGeoJSON(a.geometry) as geometry
        FROM areas a
        ORDER BY a.id
        LIMIT :limit OFFSET :offset
    """)
    result = db.execute(query, {"limit": limit, "offset": offset})
    
    areas = []
    for row in result:
        row_dict = dict(row._mapping)
        if row_dict.get("geometry"):
            row_dict["geometry"] = json.loads(row_dict["geometry"])
        areas.append(row_dict)
    return areas


def get_area_summaries(db: Session) -> List[Dict[str, Any]]:
    query = text("""
        SELECT 
            a.id, a.name, a.area_type, a.county,
            COALESCE(ps.avg_price, 0) as avg_price,
            COALESCE(ps.sales_count, 0) as property_count
        FROM areas a
        LEFT JOIN LATERAL (
            SELECT 
                ROUND(AVG(price_eur))::int as avg_price,
                COUNT(*)::int as sales_count
            FROM property_sales
            WHERE area_id = a.id AND price_eur > 0
        ) ps ON true
        ORDER BY ps.sales_count DESC NULLS LAST
    """)
    result = db.execute(query)
    return [dict(row._mapping) for row in result]

def get_area_by_id(db: Session, area_id: int) -> Optional[Dict[str, Any]]:
    query = text("""
        SELECT id, name, area_type, county, ST_AsGeoJSON(geometry) as geometry
        FROM areas
        WHERE id = :area_id
    """)
    result = db.execute(query, {"area_id": area_id}).first()
    if not result:
        return None
    
    # Also fetch latest metrics summary
    metrics_query = text("""
        WITH price_agg AS (
            SELECT AVG(price_eur) as avg_price, COUNT(id) as sales_count FROM property_sales WHERE area_id = :area_id
        ),
        amenity_agg AS (
            SELECT COUNT(id) as amenity_count FROM amenities WHERE area_id = :area_id
        ),
        crime_agg AS (
            SELECT SUM(count) as total_crime FROM crime_stats WHERE area_id = :area_id
        ),
        demo_latest AS (
            SELECT population, deprivation_index FROM area_demographics WHERE area_id = :area_id ORDER BY year DESC LIMIT 1
        )
        SELECT 
            (SELECT avg_price FROM price_agg) as avg_price,
            (SELECT sales_count FROM price_agg) as sales_count,
            (SELECT amenity_count FROM amenity_agg) as amenity_count,
            (SELECT total_crime FROM crime_agg) as total_crime,
            (SELECT population FROM demo_latest) as population,
            (SELECT deprivation_index FROM demo_latest) as deprivation_index
    """)
    metrics = db.execute(metrics_query, {"area_id": area_id}).first()
    
    area_dict = dict(result._mapping)
    if area_dict.get("geometry"):
        area_dict["geometry"] = json.loads(area_dict["geometry"])
        
    if metrics:
        area_dict["metrics"] = dict(metrics._mapping)
    return area_dict
