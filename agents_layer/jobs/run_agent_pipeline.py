import argparse
import sys
import os
import glob
import json
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from storage.scripts.db_connect import get_db
from storage.models.db_models import AreaAgentSummary
from agents_layer.text_sources.council_news_connector import CouncilNewsConnector
from agents_layer.pipeline import run_pipeline_for_area
from agents_layer.llm_client import LLMClient
from ingestion.utils.logging_config import setup_logger

logger = setup_logger("run_agent_pipeline")

def get_structured_data_snapshot(db, area_id: int) -> dict:
    """Mock fetching structured data from Phase 1 tables for comparison."""
    # In a real implementation, we'd query crime_stats and property_sales
    return {
        "crime_trend": 0.15, # Mock: Crime went up 15%
        "price_trend": 0.05  # Mock: Prices went up 5%
    }

def run_agent_pipeline(area_id: int):
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # 1. Run the connector to fetch fresh text if needed
        connector = CouncilNewsConnector(db)
        connector.run()
        
        # 2. Gather raw texts for this area_id
        raw_dir = os.path.join(os.path.dirname(__file__), '../../data/raw/council_news/')
        search_pattern = os.path.join(raw_dir, f"area_{area_id}_*.json")
        files = glob.glob(search_pattern)
        
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
