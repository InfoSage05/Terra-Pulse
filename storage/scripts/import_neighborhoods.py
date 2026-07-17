"""
Import the neighborhood property pricing data from your friend's Google Sheet.
Reads data/raw/neighborhoods/property_pricing.csv and upserts into the
neighborhood_data table.
"""
import csv
import re
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from storage.scripts.db_connect import SessionLocal

def parse_eur(val: str) -> float | None:
    if not val:
        return None
    val = val.strip().replace('\u20ac', '').replace('$', '').replace(',', '').strip()
    if not val or val in ('\u2014', '-', 'N/A'):
        return None
    try:
        return float(val)
    except ValueError:
        return None

def main():
    csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw', 'neighborhoods', 'property_pricing.csv')
    if not os.path.exists(csv_path):
        print(f"CSV not found at {csv_path}")
        sys.exit(1)

    db = SessionLocal()
    try:
        with open(csv_path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            imported = 0
            skipped = 0
            for row in reader:
                locality = row.get('Locality', '').strip()
                if not locality:
                    skipped += 1
                    continue

                median = parse_eur(row.get('Median Sold Price (\u20ac)', ''))
                average = parse_eur(row.get('Average Sold Price (\u20ac)', ''))
                asking = parse_eur(row.get('Avg Asking Price (\u20ac)', ''))

                from sqlalchemy import text

                db.execute(text("""
                    INSERT INTO neighborhood_data (locality, eircode_district, median_sold_price, average_sold_price, avg_asking_price, data_source)
                    VALUES (:locality, :eircode, :median, :average, :asking, :source)
                    ON CONFLICT (locality) DO UPDATE SET
                        eircode_district = EXCLUDED.eircode_district,
                        median_sold_price = EXCLUDED.median_sold_price,
                        average_sold_price = EXCLUDED.average_sold_price,
                        avg_asking_price = EXCLUDED.avg_asking_price,
                        data_source = EXCLUDED.data_source
                """), {
                    "locality": locality,
                    "eircode": row.get('Eircode / District', '').strip() or None,
                    "median": median,
                    "average": average,
                    "asking": asking,
                    "source": row.get('Data Source', '').strip() or None,
                })
                imported += 1

            db.commit()
        print(f"Imported {imported} neighborhoods (skipped {skipped})")
    finally:
        db.close()

if __name__ == '__main__':
    main()
