import pandas as pd
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from shared.model_contract import AreaScoreOutput, ModelType
from models_layer.registry.registry import get_active_model_metadata

def get_area_score(db: Session, area_id: int) -> Optional[AreaScoreOutput]:
    # Check if area exists
    area = db.execute(text("SELECT id FROM areas WHERE id = :area_id"), {"area_id": area_id}).scalar()
    if not area:
        return None
        
    # Get active model versions
    affordability_meta = get_active_model_metadata(ModelType.AFFORDABILITY_SCORE)
    safety_meta = get_active_model_metadata(ModelType.SAFETY_SCORE)
    livability_meta = get_active_model_metadata(ModelType.LIVABILITY_SCORE)
    
    versions = {}
    if affordability_meta: versions["affordability"] = affordability_meta.version
    if safety_meta: versions["safety"] = safety_meta.version
    if livability_meta: versions["livability"] = livability_meta.version
    
    # Query feature metrics for scoring
    query = text("""
        WITH price_agg AS (
            SELECT AVG(price_eur) as avg_price FROM property_sales WHERE area_id = :area_id
        ),
        crime_agg AS (
            SELECT SUM(count) as total_crime FROM crime_stats WHERE area_id = :area_id
        ),
        demo_latest AS (
            SELECT population, deprivation_index FROM area_demographics WHERE area_id = :area_id ORDER BY year DESC LIMIT 1
        ),
        agent_summary AS (
            SELECT livability_signal, confidence, needs_human_review FROM area_agent_summaries WHERE area_id = :area_id ORDER BY ingested_at DESC LIMIT 1
        )
        SELECT 
            COALESCE((SELECT avg_price FROM price_agg), 0) as avg_price,
            COALESCE((SELECT total_crime FROM crime_agg), 0) as total_crime,
            (SELECT population FROM demo_latest) as population,
            (SELECT deprivation_index FROM demo_latest) as deprivation_index,
            (SELECT livability_signal FROM agent_summary) as livability_signal,
            (SELECT confidence FROM agent_summary) as agent_confidence,
            (SELECT needs_human_review FROM agent_summary) as needs_human_review
    """)
    
    row = db.execute(query, {"area_id": area_id}).first()
    if not row:
        return AreaScoreOutput(
            area_id=area_id,
            affordability_score=None,
            safety_score=None,
            livability_score=None,
            livability_confidence=None,
            needs_human_review=False,
            model_versions_used=versions,
            last_updated=datetime.now()
        )
        
    avg_price = row.avg_price
    total_crime = row.total_crime
    population = row.population
    dep_index = row.deprivation_index
    liv_signal = row.livability_signal
    agent_conf = row.agent_confidence
    needs_review = row.needs_human_review if row.needs_human_review is not None else False
    
    aff_score = None
    if affordability_meta and avg_price > 0 and dep_index is not None:
        # Re-apply formula or use a precomputed one. For now we use the raw values
        aff_score = max(0, 100 - (avg_price / 10000) * 0.6 - (dep_index * 10) * 0.4)
        
    saf_score = None
    if safety_meta and total_crime is not None and population:
        crime_rate = (total_crime / population) * 1000
        saf_score = max(0, 100 - (crime_rate * 2))
        
    liv_score = None
    if livability_meta and liv_signal is not None:
        liv_score = (liv_signal + 1.0) * 50 # scale -1.0 to 1.0 -> 0 to 100
    
    return AreaScoreOutput(
        area_id=area_id,
        affordability_score=aff_score,
        safety_score=saf_score,
        livability_score=liv_score,
        livability_confidence=agent_conf,
        needs_human_review=needs_review,
        model_versions_used=versions,
        last_updated=datetime.now()
    )
