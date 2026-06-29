import sys
import os
import time
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from storage.scripts.db_connect import get_db
from storage.models.db_models import Area
from agents_layer.jobs.run_agent_pipeline import run_agent_pipeline
from ingestion.utils.logging_config import setup_logger

logger = setup_logger("run_agents_batch")

def run_all_agents():
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        areas = db.query(Area).all()
        logger.info(f"Found {len(areas)} areas to process.")
        
        for area in areas:
            logger.info(f"Processing area {area.id} - {area.name}")
            run_agent_pipeline(area.id)
            # Rate limiting sleep to respect free tier limits (Groq/OpenRouter)
            time.sleep(2)
            
    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_all_agents()
