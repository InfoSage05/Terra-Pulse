import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from shared.model_contract import AreaScoreOutput, ModelType
from shared.scoring_formulas import affordability_score, safety_score
from models_layer.registry.registry import get_active_model_metadata
from backend.app.core.cache import area_score_key, cache_get, cache_set
from backend.app.core.config import settings

logger = logging.getLogger("terrapulse.backend.score_service")


async def get_area_score(db: AsyncSession, area_id: int) -> Optional[AreaScoreOutput]:
    cache_key = area_score_key(area_id)
    cached = cache_get(cache_key)
    if cached is not None:
        try:
            return AreaScoreOutput.model_validate_json(cached)
        except Exception as e:
            # Corrupt/incompatible cache entry - ignore it and recompute live.
            logger.warning(f"Failed to deserialize cached area score for area_id={area_id}: {e}")

    score = await _compute_area_score(db, area_id)
    if score is not None:
        cache_set(cache_key, score.model_dump_json(), ttl_seconds=settings.AREA_SCORE_CACHE_TTL_SECONDS)
    return score


async def _compute_area_score(db: AsyncSession, area_id: int) -> Optional[AreaScoreOutput]:
    # Check if area exists
    area = (await db.execute(text("SELECT id FROM areas WHERE id = :area_id"), {"area_id": area_id})).scalar()
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
            SELECT livability_signal, confidence, needs_human_review, summary FROM area_agent_summaries WHERE area_id = :area_id ORDER BY ingested_at DESC LIMIT 1
        )
        SELECT
            COALESCE((SELECT avg_price FROM price_agg), 0) as avg_price,
            COALESCE((SELECT total_crime FROM crime_agg), 0) as total_crime,
            (SELECT population FROM demo_latest) as population,
            (SELECT deprivation_index FROM demo_latest) as deprivation_index,
            (SELECT livability_signal FROM agent_summary) as livability_signal,
            (SELECT confidence FROM agent_summary) as agent_confidence,
            (SELECT needs_human_review FROM agent_summary) as needs_human_review,
            (SELECT summary FROM agent_summary) as agent_summary
    """)

    row = (await db.execute(query, {"area_id": area_id})).first()
    if not row:
        return AreaScoreOutput(
            area_id=area_id,
            affordability_score=None,
            safety_score=None,
            livability_score=None,
            livability_confidence=None,
            needs_human_review=False,
            agent_summary=None,
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
    agent_summary = row.agent_summary if hasattr(row, 'agent_summary') else None

    aff_score = affordability_score(avg_price, dep_index) if affordability_meta else None

    saf_score = safety_score(total_crime, population) if safety_meta else None

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
        agent_summary=agent_summary,
        model_versions_used=versions,
        last_updated=datetime.now()
    )
