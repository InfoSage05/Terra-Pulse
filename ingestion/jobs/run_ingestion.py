import argparse
import sys
import os
import logging

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from storage.scripts.db_connect import get_db
from ingestion.connectors import PPRConnector, OSMConnector, CSOConnector, CrimeConnector
from ingestion.utils.logging_config import setup_logger

logger = setup_logger("run_ingestion")

def run_connectors(sources: list[str]):
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        if 'ppr' in sources or 'all' in sources:
            PPRConnector(db).run()
            
        if 'osm' in sources or 'all' in sources:
            OSMConnector(db).run()
            
        if 'cso' in sources or 'all' in sources:
            CSOConnector(db).run()
            
        if 'crime' in sources or 'all' in sources:
            CrimeConnector(db).run()
            
    except Exception as e:
        logger.error(f"Ingestion job failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run TerraPulse data ingestion connectors.")
    parser.add_argument(
        '--source',
        action='append',
        choices=['ppr', 'osm', 'cso', 'crime', 'all'],
        help="Specify which data source(s) to ingest. Use multiple times or 'all'."
    )
    
    args = parser.parse_args()
    sources = args.source
    
    if not sources:
        logger.info("No sources specified. Defaulting to 'all'.")
        sources = ['all']
        
    logger.info(f"Starting ingestion jobs for sources: {sources}")
    run_connectors(sources)
    logger.info("Ingestion jobs finished.")
