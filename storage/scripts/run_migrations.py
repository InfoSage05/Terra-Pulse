"""
Automated migration runner for TerraPulse.

Applies all SQL files in storage/migrations/ (in numeric-prefix order) against
the Postgres database pointed to by DATABASE_URL, tracking applied migrations
in a `schema_migrations` table so re-running is a no-op for files that were
already applied. Safe to run on every container startup.

Usage:
    python storage/scripts/run_migrations.py
    # or, inside the backend container:
    docker compose exec backend python storage/scripts/run_migrations.py
"""
import os
import re
import sys

# Add project root to Python path so this script works whether it's invoked
# directly (python storage/scripts/run_migrations.py) or as a module.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from storage.scripts.db_connect import get_engine

try:
    from ingestion.utils.logging_config import setup_logger
    logger = setup_logger("run_migrations")
except Exception:  # pragma: no cover - fallback if ingestion package unavailable
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("run_migrations")

MIGRATIONS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'migrations'))
MIGRATION_FILENAME_RE = re.compile(r'^(\d+)_.*\.sql$')

SCHEMA_MIGRATIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    filename VARCHAR(255) PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
"""


def discover_migrations(migrations_dir: str):
    """Return migration filenames sorted by their numeric prefix."""
    if not os.path.isdir(migrations_dir):
        raise FileNotFoundError(f"Migrations directory not found: {migrations_dir}")

    candidates = []
    for filename in os.listdir(migrations_dir):
        match = MIGRATION_FILENAME_RE.match(filename)
        if match:
            candidates.append((int(match.group(1)), filename))
        elif filename.endswith('.sql'):
            logger.warning(f"Skipping SQL file without a numeric prefix: {filename}")

    candidates.sort(key=lambda item: item[0])
    return [filename for _, filename in candidates]


def get_applied_migrations(conn) -> set:
    rows = conn.execute(text("SELECT filename FROM schema_migrations")).fetchall()
    return {row[0] for row in rows}


def apply_migration(conn, migrations_dir: str, filename: str):
    path = os.path.join(migrations_dir, filename)
    with open(path, 'r', encoding='utf-8') as f:
        sql = f.read()

    logger.info(f"Applying migration: {filename}")
    conn.execute(text(sql))
    conn.execute(
        text("INSERT INTO schema_migrations (filename) VALUES (:filename)"),
        {"filename": filename},
    )
    logger.info(f"Applied migration: {filename}")


def run_migrations():
    engine = get_engine()

    try:
        with engine.begin() as conn:
            conn.execute(text(SCHEMA_MIGRATIONS_TABLE_SQL))
    except OperationalError as e:
        logger.error(f"Could not connect to database to run migrations: {e}")
        raise

    migration_files = discover_migrations(MIGRATIONS_DIR)
    if not migration_files:
        logger.warning(f"No migration files found in {MIGRATIONS_DIR}")
        return

    with engine.connect() as conn:
        applied = get_applied_migrations(conn)

    pending = [f for f in migration_files if f not in applied]

    if not pending:
        logger.info(f"No pending migrations. {len(applied)} already applied, up to date.")
        return

    logger.info(f"Found {len(pending)} pending migration(s) out of {len(migration_files)} total.")

    applied_count = 0
    for filename in pending:
        # Each migration runs in its own transaction so one failure doesn't
        # roll back migrations that already succeeded in this run.
        with engine.begin() as conn:
            apply_migration(conn, MIGRATIONS_DIR, filename)
        applied_count += 1

    logger.info(f"Migration run complete. Applied {applied_count} migration(s).")


if __name__ == "__main__":
    try:
        run_migrations()
    except Exception as e:
        logger.error(f"Migration run failed: {e}")
        sys.exit(1)
