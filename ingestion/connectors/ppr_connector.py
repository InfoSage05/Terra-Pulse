import csv
import io
import os
import json
import glob
import tempfile
from datetime import datetime
from pydantic import ValidationError
from ingestion.connectors.base import BaseConnector
from ingestion.schemas.property_sale import PropertySaleSchema
from storage.models.db_models import PropertySale
from sqlalchemy.dialects.postgresql import insert
class PPRConnector(BaseConnector):
    """
    Property Price Register Connector.
    Uses Playwright (headless Chromium) to interact with the PSRA IBM Domino 
    system, submitting the form for 'Dublin' in the current year and 
    intercepting the CSV download.
    """
    
    def get_source_name(self) -> str:
        return "ppr"

    def fetch(self) -> list[dict]:
        self.logger.info("Starting PPR extraction via PPR-ALL.zip download...")
        raw_data = []
        
        url = 'https://www.propertypriceregister.ie/website/npsra/ppr/npsra-ppr.nsf/Downloads/PPR-ALL.zip/$FILE/PPR-ALL.zip'
        
        try:
            import requests
            import urllib3
            import zipfile
            import io
            
            urllib3.disable_warnings()
            self.logger.info(f"Downloading {url}")
            
            # Use requests to download the ZIP directly, bypassing IBM Domino Bot challenge
            resp = requests.get(url, verify=False)
            resp.raise_for_status()
            
            self.logger.info("Extracting ZIP in memory...")
            with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
                csv_filename = z.namelist()[0]
                self.logger.info(f"Parsing CSV {csv_filename}...")
                
                with z.open(csv_filename) as f:
                    # The CSV encoding is cp1252. We decode as we read.
                    text_stream = io.TextIOWrapper(f, encoding='cp1252')
                    reader = csv.DictReader(text_stream)
                    
                    for row in reader:
                        # Only ingest Dublin data for now, per requirements
                        county = row.get('County', '').strip().lower()
                        if county == 'dublin':
                            raw_data.append(row)
                            
            self.logger.info(f"Successfully downloaded and filtered {len(raw_data)} Dublin records.")
            
        except Exception as e:
            self.logger.error(f"PPR extraction failed: {e}")
            
        return raw_data

    def validate(self, raw_record: dict) -> PropertySaleSchema | None:
        try:
            # The Price column often contains a Euro symbol which can parse weirdly.
            # We dynamically find the key containing 'Price'
            price_key = next((k for k in raw_record.keys() if k and 'Price' in k and 'Not Full' not in k), None)
            price_str = raw_record.get(price_key, '0') if price_key else '0'
            price_str = price_str.replace('€', '').replace('\ufffd', '').replace(',', '').strip()

            date_str = raw_record.get('Date of Sale (dd/mm/yyyy)', '')
            
            try:
                price_val = float(price_str)
                # Parse date assuming DD/MM/YYYY
                date_val = datetime.strptime(date_str, '%d/%m/%Y').date()
            except ValueError:
                return None
                
            validated = PropertySaleSchema(
                sale_date=date_val,
                price_eur=price_val,
                address_raw=raw_record.get('Address', '').strip(),
                source_name=self.source_name
            )
            return validated
        except ValidationError as e:
            self.logger.debug(f"Validation error: {e}")
            return None

    def run(self):
        # We override run to intercept validated records for per-run export
        self.validated_records_for_export = []
        super().run()
        
        # Now dump the per-run files
        if self.validated_records_for_export:
            run_date = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_dir = os.path.join(os.path.dirname(__file__), '../../data/processed/ppr')
            os.makedirs(export_dir, exist_ok=True)
            
            csv_path = os.path.join(export_dir, f'ppr_dublin_{run_date}.csv')
            json_path = os.path.join(export_dir, f'ppr_dublin_{run_date}.json')
            
            # JSON dump
            with open(json_path, 'w', encoding='utf-8') as f:
                # We dump dicts
                json_data = [r.model_dump() for r in self.validated_records_for_export]
                # date serialization
                def default_serializer(obj):
                    if hasattr(obj, 'isoformat'): return obj.isoformat()
                    raise TypeError
                json.dump(json_data, f, indent=2, default=default_serializer)
                
            # CSV dump
            with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                if json_data:
                    writer = csv.DictWriter(f, fieldnames=list(json_data[0].keys()))
                    writer.writeheader()
                    for row in json_data:
                        writer.writerow(row)
                        
            self.logger.info(f"Exported {len(self.validated_records_for_export)} processed records to {export_dir}")

    def load(self, validated_record: PropertySaleSchema) -> bool:
        stmt = insert(PropertySale).values(
            sale_date=validated_record.sale_date,
            price_eur=validated_record.price_eur,
            address_raw=validated_record.address_raw,
            source_name=validated_record.source_name,
        )
        
        # Idempotent upsert based on natural key
        update_dict = {
            'ingested_at': datetime.now()
        }
        
        upsert_stmt = stmt.on_conflict_do_update(
            constraint='uq_property_sales_date_address_price',
            set_=update_dict
        )
        
        try:
            self.db.execute(upsert_stmt)
            if hasattr(self, 'validated_records_for_export'):
                self.validated_records_for_export.append(validated_record)
            return True
        except Exception as e:
            self.logger.error(f"DB insert failed: {e}")
            return False
