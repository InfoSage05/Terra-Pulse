import argparse
import sys
import os
import glob
import json
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy import text
from storage.scripts.db_connect import get_db
from storage.models.db_models import AreaAgentSummary, Area
from agents_layer.text_sources.council_news_connector import CouncilNewsConnector
from agents_layer.pipeline import run_pipeline_for_area
from agents_layer.llm_client import LLMClient
from ingestion.utils.logging_config import setup_logger

logger = setup_logger("run_agent_pipeline")

# crime_stats rows are keyed by Garda division, not area_id (the Crime connector
# doesn't geocode to areas - that's an ingestion-layer gap, out of scope here).
# To still get a *real*, area-varying crime_trend signal for the Fuse review-gate
# (instead of a hardcoded constant), map each seeded Dublin postal
# district/suburb to its real-world Garda division so we can pull an actual
# division-level trend from crime_stats. Approximate but grounded in real
# Dublin Garda division boundaries.
_AREA_TO_GARDA_DIVISION = {
    "Dublin 1": "D.M.R. North Central Garda Division",
    "Dublin 3": "D.M.R. North Central Garda Division",
    "Dublin 7": "D.M.R. North Central Garda Division",
    "Dublin 8": "D.M.R. South Central Garda Division",
    "Dublin 10": "D.M.R. South Central Garda Division",
    "Dublin 12": "D.M.R. South Central Garda Division",
    "Dublin 20": "D.M.R. South Central Garda Division",
    "Dublin 22": "D.M.R. South Central Garda Division",
    "Dublin 24": "D.M.R. South Central Garda Division",
    "Dublin 6": "D.M.R. Southern Garda Division",
    "Dublin 6W": "D.M.R. Southern Garda Division",
    "Dublin 14": "D.M.R. Southern Garda Division",
    "Dublin 16": "D.M.R. Southern Garda Division",
    "Dublin 5": "D.M.R. Northern Garda Division",
    "Dublin 9": "D.M.R. Northern Garda Division",
    "Dublin 11": "D.M.R. Northern Garda Division",
    "Dublin 13": "D.M.R. Northern Garda Division",
    "Dublin 17": "D.M.R. Northern Garda Division",
    "Dublin 19": "D.M.R. Northern Garda Division",
    "Dublin 15": "D.M.R. Western Garda Division",
    "Blackrock": "D.M.R. Eastern Garda Division",
    "Dún Laoghaire": "D.M.R. Eastern Garda Division",
    "Dublin 18": "D.M.R. Eastern Garda Division",
    "Dublin 2": "D.M.R. South Central Garda Division",
    "Dublin 4": "D.M.R. Eastern Garda Division",
}


def _compute_crime_trend(db, area_id: int) -> float:
    """Real division-level crime trend: recent (2023-2024 avg) vs prior (2020-2022 avg), as a fraction change."""
    area = db.query(Area).filter(Area.id == area_id).first()
    division = _AREA_TO_GARDA_DIVISION.get(area.name) if area else None
    if not division:
        return 0.0

    row = db.execute(text("""
        WITH recent AS (
            SELECT SUM(count) AS c FROM crime_stats
            WHERE garda_division = :division AND year IN (2023, 2024)
        ), prior AS (
            SELECT SUM(count) AS c FROM crime_stats
            WHERE garda_division = :division AND year IN (2020, 2021, 2022)
        )
        SELECT recent.c AS recent_c, prior.c AS prior_c FROM recent, prior
    """), {"division": division}).first()

    if not row or not row.prior_c or not row.recent_c:
        return 0.0

    recent_avg = row.recent_c / 2.0
    prior_avg = row.prior_c / 3.0
    if prior_avg == 0:
        return 0.0
    return float((recent_avg - prior_avg) / prior_avg)


def _compute_price_trend(db, area_id: int) -> float:
    """Real area-level price trend from property_sales: recent (2024+) avg vs prior (2021-2023) avg."""
    row = db.execute(text("""
        WITH recent AS (
            SELECT AVG(price_eur) AS p FROM property_sales
            WHERE area_id = :area_id AND sale_date >= '2024-01-01'
        ), prior AS (
            SELECT AVG(price_eur) AS p FROM property_sales
            WHERE area_id = :area_id AND sale_date BETWEEN '2021-01-01' AND '2023-12-31'
        )
        SELECT recent.p AS recent_p, prior.p AS prior_p FROM recent, prior
    """), {"area_id": area_id}).first()

    if not row or not row.prior_p or not row.recent_p:
        return 0.0
    return float((row.recent_p - row.prior_p) / row.prior_p)


def get_structured_data_snapshot(db, area_id: int) -> dict:
    """
    Real structured-data snapshot from Phase 1 tables, used by the Fuse step's
    review-gate to compare against the agent's qualitative livability signal.
    crime_trend comes from crime_stats via a Garda-division mapping (crime_stats
    isn't geocoded to area_id yet); price_trend comes directly from area-geocoded
    property_sales.
    """
    return {
        "crime_trend": _compute_crime_trend(db, area_id),
        "price_trend": _compute_price_trend(db, area_id),
    }

def run_agent_pipeline(area_id: int, run_connector: bool = True):
    db_gen = get_db()
    db = next(db_gen)

    try:
        # 1. Run the connector to fetch fresh text if needed. The connector
        # fetches sample articles for ALL seeded areas in one call, so batch
        # callers (run_agents.py) should fetch once upfront and pass
        # run_connector=False here to avoid re-writing duplicate raw files
        # per area.
        if run_connector:
            connector = CouncilNewsConnector(db)
            connector.run()

        # 2. Gather raw texts for this area_id. Each source costs one LLM
        # Extract call against a rate-limited free-tier pool shared across
        # all areas, so cap how many we send per area rather than sending
        # every accumulated file (repeated connector runs otherwise pile up
        # duplicate sources per area over time - see PROCESSED_RUNS_TO_KEEP-
        # style cleanup note in ppr_connector.py for the analogous issue).
        MAX_SOURCES_PER_AREA = 3
        raw_dir = os.path.join(os.path.dirname(__file__), '../../data/raw/council_news/')
        search_pattern = os.path.join(raw_dir, f"area_{area_id}_*.json")
        files = sorted(glob.glob(search_pattern), reverse=True)[:MAX_SOURCES_PER_AREA]

        raw_texts = []
        for file in files:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                raw_texts.append(data.get("content", ""))
                
        if not raw_texts:
            logger.info(f"No raw texts found for area_id {area_id}. Skipping pipeline.")
            return
            
        # 3. Get structured data snapshot
        structured_data = get_structured_data_snapshot(db, area_id)
        
        # 4. Run the Agent Pipeline
        llm_client = LLMClient()
        fused_summary = run_pipeline_for_area(
            area_id=area_id,
            raw_texts=raw_texts,
            structured_data=structured_data,
            llm_client=llm_client
        )
        
        if fused_summary:
            # 5. Save to DB
            summary_record = AreaAgentSummary(
                area_id=fused_summary.area_id,
                run_id=fused_summary.run_id,
                summary=fused_summary.summary,
                livability_signal=fused_summary.livability_signal,
                confidence=fused_summary.confidence,
                flags=fused_summary.flags,
                needs_human_review=fused_summary.needs_human_review,
                structured_data_snapshot=fused_summary.structured_data_snapshot,
                source_count=fused_summary.source_count,
                model_name=fused_summary.model_name,
                source_name=fused_summary.source_name
            )
            db.add(summary_record)
            db.commit()
            logger.info(f"Saved AreaAgentSummary for area_id {area_id} to database.")
            
    except Exception as e:
        logger.error(f"Agent pipeline failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run TerraPulse Agent Pipeline.")
    parser.add_argument(
        '--area-id',
        type=int,
        required=True,
        help="The ID of the area to process."
    )
    
    args = parser.parse_args()
    
    logger.info(f"Starting agent pipeline for area_id: {args.area_id}")
    run_agent_pipeline(args.area_id)
    logger.info("Agent pipeline finished.")
