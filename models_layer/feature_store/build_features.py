import pandas as pd
from sqlalchemy import text
from storage.scripts.db_connect import engine

def get_area_features() -> pd.DataFrame:
    """
    Fetches and aggregates area-level features for model training and inference.
    Returns a DataFrame with one row per area.
    """
    query = """
    WITH price_agg AS (
        SELECT area_id, AVG(price_eur) as avg_price, COUNT(id) as sales_count
        FROM property_sales
        GROUP BY area_id
    ),
    amenity_agg AS (
        SELECT area_id, COUNT(id) as amenity_count
        FROM amenities
        GROUP BY area_id
    ),
    crime_agg AS (
        SELECT area_id, SUM(count) as total_crime
        FROM crime_stats
        GROUP BY area_id
    ),
    demo_latest AS (
        SELECT DISTINCT ON (area_id) area_id, population, deprivation_index
        FROM area_demographics
        ORDER BY area_id, year DESC
    ),
    agent_summary AS (
        SELECT DISTINCT ON (area_id) area_id, livability_signal, confidence, needs_human_review
        FROM area_agent_summaries
        ORDER BY area_id, ingested_at DESC
    )
    SELECT 
        a.id as area_id,
        a.name as area_name,
        a.area_type,
        a.county,
        COALESCE(p.avg_price, 0) as avg_price,
        COALESCE(p.sales_count, 0) as sales_count,
        COALESCE(am.amenity_count, 0) as amenity_count,
        COALESCE(c.total_crime, 0) as total_crime,
        d.population,
        d.deprivation_index,
        agt.livability_signal,
        agt.confidence as agent_confidence,
        agt.needs_human_review
    FROM areas a
    LEFT JOIN price_agg p ON a.id = p.area_id
    LEFT JOIN amenity_agg am ON a.id = am.area_id
    LEFT JOIN crime_agg c ON a.id = c.area_id
    LEFT JOIN demo_latest d ON a.id = d.area_id
    LEFT JOIN agent_summary agt ON a.id = agt.area_id
    """
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)
    return df
