"""
One-off backfill script: resolves `area_id` for existing `property_sales`
rows that were ingested before geocoding was wired up in PPRConnector
(see ingestion/connectors/ppr_connector.py and
ingestion/utils/geocoding.py::resolve_area_id_from_address).

Usage:
    python -m storage.scripts.backfill_geocoding [--batch-size 1000] [--dry-run]

Safe to re-run: only rows with area_id IS NULL are touched, and each row is
updated with a plain UPDATE (no upsert/constraint interaction).
"""
import os
import sys
import argparse

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy import func
from storage.scripts.db_connect import get_db
from storage.models.db_models import PropertySale
from ingestion.utils.geocoding import resolve_area_id_from_address
from ingestion.utils.logging_config import setup_logger

logger = setup_logger("backfill_geocoding")


def backfill(batch_size: int = 1000, dry_run: bool = False) -> dict:
    db_gen = get_db()
    db = next(db_gen)

    stats = {"total_null": 0, "resolved": 0, "unresolved": 0}

    try:
        stats["total_null"] = db.query(func.count(PropertySale.id)).filter(
            PropertySale.area_id.is_(None)
        ).scalar()
        logger.info(f"Found {stats['total_null']} property_sales rows with area_id IS NULL.")

        if stats["total_null"] == 0:
            return stats

        last_id = 0
        processed = 0
        while True:
            rows = (
                db.query(PropertySale)
                .filter(PropertySale.area_id.is_(None), PropertySale.id > last_id)
                .order_by(PropertySale.id)
                .limit(batch_size)
                .all()
            )
            if not rows:
                break

            for row in rows:
                area_id = resolve_area_id_from_address(db, row.address_raw)
                if area_id:
                    stats["resolved"] += 1
                    if not dry_run:
                        row.area_id = area_id
                else:
                    stats["unresolved"] += 1
                last_id = row.id

            processed += len(rows)
            if not dry_run:
                db.commit()
            else:
                db.rollback()

            logger.info(
                f"Processed {processed}/{stats['total_null']} rows "
                f"(resolved so far: {stats['resolved']}, unresolved so far: {stats['unresolved']})"
            )

    except Exception as e:
        logger.error(f"Backfill failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backfill area_id for property_sales rows missing geocoding.")
    parser.add_argument('--batch-size', type=int, default=1000, help="Rows to process per DB round-trip.")
    parser.add_argument('--dry-run', action='store_true', help="Resolve and report, but do not write changes.")
    args = parser.parse_args()

    result = backfill(batch_size=args.batch_size, dry_run=args.dry_run)

    total = result["total_null"]
    resolved = result["resolved"]
    unresolved = result["unresolved"]
    rate = (resolved / total * 100) if total else 0.0

    print("\n--- Geocoding Backfill Summary ---")
    print(f"Rows with area_id IS NULL (before run): {total}")
    print(f"Resolved:                               {resolved} ({rate:.1f}%)")
    print(f"Left unresolved (no district/area match): {unresolved}")
    if args.dry_run:
        print("(dry run - no changes were written)")
    print("-----------------------------------")
