import os
import sys
import csv
import json
from datetime import date, datetime

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from storage.scripts.db_connect import get_db
from storage.models.db_models import PropertySale, Area
from ingestion.utils.logging_config import setup_logger

logger = setup_logger("export_master_csv")

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def export_master_files():
    db_gen = get_db()
    db = next(db_gen)
    
    exports_dir = os.path.join(os.path.dirname(__file__), '../../data/exports/')
    os.makedirs(exports_dir, exist_ok=True)
    
    csv_path = os.path.join(exports_dir, 'ppr_dublin_master.csv')
    json_path = os.path.join(exports_dir, 'ppr_dublin_master.json')
    
    try:
        # We join PropertySale with Area to get area_name.
        # But we do a LEFT OUTER JOIN in case area_id is null (e.g. no geocoding yet)
        query = db.query(PropertySale, Area.name.label('area_name'))\
                  .outerjoin(Area, PropertySale.area_id == Area.id)\
                  .filter(PropertySale.source_name == 'ppr')\
                  .yield_per(1000)
                  
        results = []
        for row, area_name in query:
            results.append({
                'area_id': row.area_id,
                'area_name': area_name,
                'sale_date': row.sale_date,
                'price_eur': row.price_eur,
                'address_raw': row.address_raw,
                'address_normalized': row.address_normalized,
                'lat': row.lat,
                'lon': row.lon,
                'source_name': row.source_name,
                'ingested_at': row.ingested_at
            })
            
        logger.info(f"Fetched {len(results)} records for master export.")
        
        # Write CSV
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            if results:
                fieldnames = list(results[0].keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for record in results:
                    writer.writerow(record)
            logger.info(f"Successfully wrote {csv_path}")
            
        # Write JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, default=json_serial, indent=2)
            logger.info(f"Successfully wrote {json_path}")
            
    except Exception as e:
        logger.error(f"Failed to export master files: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    export_master_files()
