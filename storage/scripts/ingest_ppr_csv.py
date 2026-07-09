"""Run PPR ingestion: live scrape + CSV import fallback"""
import os, sys, csv, json
from datetime import datetime, date
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.dialects.postgresql import insert
from storage.scripts.db_connect import get_db
from storage.models.db_models import PropertySale, Area, IngestionRun

def parse_date(d):
    try:
        return datetime.strptime(d, '%d/%m/%Y').date()
    except:
        return None

def import_csv(csv_path):
    db = next(get_db())
    row_count = 0
    for row in csv.DictReader(open(csv_path, encoding='utf-8')):
        sale_date = parse_date(row['Date of Sale (dd/mm/yyyy)'])
        if not sale_date:
            continue
        price_str = row['Price (Euro)'].replace('€', '').replace(',', '').replace('**', '').strip()
        try:
            price = float(price_str)
        except:
            continue
        stmt = insert(PropertySale).values(
            sale_date=sale_date,
            price_eur=price,
            address_raw=row.get('Address', '').strip(),
            source_name='ppr',
        )
        upsert = stmt.on_conflict_do_update(
            constraint='uq_property_sales_date_address_price',
            set_={'ingested_at': datetime.now()}
        )
        try:
            db.execute(upsert)
            row_count += 1
        except Exception as e:
            print(f"  Insert error: {e}")
    db.commit()
    db.close()
    return row_count

# Path to our already-scraped CSV
csv_paths = [
    '/mnt/e/FTP/terrapulse/data/exports/ppr_dublin_master.csv',
    '/mnt/e/FTP/terrapulse/data/raw/ppr/manual_pulls/ppr_dublin_2026_clean.csv',
]

total = 0
for path in csv_paths:
    if os.path.exists(path):
        print(f"Importing {path}...")
        count = import_csv(path)
        print(f"  Imported {count} records")
        total += count

print(f"\nTotal imported: {total}")

# Verify
from storage.scripts.db_connect import get_db
db = next(get_db())
count = db.query(PropertySale).filter(PropertySale.source_name == 'ppr').count()
years = db.query(PropertySale.sale_date).distinct().order_by(PropertySale.sale_date.desc()).limit(5).all()
print(f"Total PPR records in DB: {count}")
print(f"Most recent dates: {[r[0] for r in years]}")
db.close()
