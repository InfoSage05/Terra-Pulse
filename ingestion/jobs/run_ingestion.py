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

def run_connectors(sources: list[str]) -> dict:
    """
    Run the requested connectors. Each connector creates and updates its own
    `ingestion_runs` row (via BaseConnector.run()). Returns an aggregate of
    each connector's stats dict, keyed by source name, for callers that want
    an overall summary (e.g. the scheduled refresh job).
    """
    db_gen = get_db()
    db = next(db_gen)

    aggregate_stats = {}

    try:
        if 'ppr' in sources or 'all' in sources:
            connector = PPRConnector(db)
            connector.run()
            aggregate_stats['ppr'] = dict(connector.stats)

        if 'osm' in sources or 'all' in sources:
            connector = OSMConnector(db)
            connector.run()
            aggregate_stats['osm'] = dict(connector.stats)

        if 'cso' in sources or 'all' in sources:
            connector = CSOConnector(db)
            connector.run()
            aggregate_stats['cso'] = dict(connector.stats)

        if 'crime' in sources or 'all' in sources:
            connector = CrimeConnector(db)
            connector.run()
            aggregate_stats['crime'] = dict(connector.stats)

    except Exception as e:
        logger.error(f"Ingestion job failed: {e}")
    finally:
        db.close()

    return aggregate_stats

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
