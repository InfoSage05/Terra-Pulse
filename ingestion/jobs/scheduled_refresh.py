import os
import sys
import logging
from datetime import datetime
import redis

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from storage.scripts.db_connect import get_db
from storage.models.db_models import IngestionRun
from ingestion.jobs.run_ingestion import run_connectors
from storage.scripts.export_master_csv import export_master_files
from ingestion.utils.logging_config import setup_logger

logger = setup_logger("scheduled_refresh")

def clear_redis_cache():
    redis_url = os.environ.get("REDIS_URL", "redis://redis:6379/0")
    try:
        r = redis.Redis.from_url(redis_url)
        # Invalidate area scores and any lists
        keys_to_delete = r.keys("area_scores:*") + r.keys("area_list:*")
        if keys_to_delete:
            r.delete(*keys_to_delete)
        logger.info(f"Cleared {len(keys_to_delete)} keys from Redis cache.")
    except Exception as e:
        logger.error(f"Failed to clear Redis cache: {e}")

def run_scheduled_ingestion():
    logger.info("Starting scheduled ingestion job...")
    
    db_gen = get_db()
    db = next(db_gen)
    
    # This is an orchestration-level record covering the whole scheduled job
    # (export + cache invalidation). Each individual connector additionally
    # creates its own 'ppr'/'osm'/'cso'/'crime' ingestion_runs row with real
    # per-source metrics (see BaseConnector.run()).
    run_record = IngestionRun(
        source_name='scheduled_refresh',
        started_at=datetime.now(),
        status='running'
    )
    db.add(run_record)
    db.commit()

    try:
        # 1. Run the connectors (this handles PPR from manual_pulls)
        aggregate_stats = run_connectors(['all'])

        # Roll up per-connector stats onto the orchestration record so it
        # reflects real totals rather than staying at zero.
        run_record.rows_fetched = sum(s.get('fetched', 0) for s in aggregate_stats.values())
        run_record.rows_upserted = sum(s.get('upserted', 0) for s in aggregate_stats.values())
        run_record.rows_dead_lettered = sum(
            s.get('rejected', 0) + s.get('errors', 0) for s in aggregate_stats.values()
        )

        # 2. Export master CSV
        export_master_files()

        # 3. Clear Redis Cache
        # Option (b): We explicitly invalidate the keys so the frontend doesn't serve stale data.
        clear_redis_cache()

        run_record.status = 'completed'
        logger.info("Scheduled ingestion job completed successfully.")

    except Exception as e:
        run_record.status = 'failed'
        logger.error(f"Scheduled ingestion job failed: {e}")

    finally:
        run_record.finished_at = datetime.now()
        db.commit()
        db.close()

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    # Default schedule: 3am daily
    scheduler.add_job(
        run_scheduled_ingestion, 
        CronTrigger(hour=3, minute=0),
        id='daily_refresh',
        replace_existing=True
    )
    
    logger.info("Starting APScheduler for TerraPulse Scheduled Refresh. Press Ctrl+C to exit.")
    
    # Run once on startup for testing if an env var is set, or just run the scheduler
    if os.environ.get("RUN_ON_STARTUP") == "1":
        run_scheduled_ingestion()
        
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
