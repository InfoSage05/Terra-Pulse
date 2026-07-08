import csv
import io
import os
import glob
from datetime import datetime
from pydantic import ValidationError
from ingestion.connectors.base import BaseConnector
from ingestion.schemas.property_sale import PropertySaleSchema
from storage.models.db_models import PropertySale
from sqlalchemy.dialects.postgresql import insert

class PPRConnector(BaseConnector):
    """
    Property Price Register Connector.
    Reads CP1252-encoded CSVs from data/raw/ppr/manual_pulls/, validates, and loads.
    This uses the fallback manual-pull mechanism as the official Domino site
    resists automated CSV export via plain POST requests.
    """
    
    def get_source_name(self) -> str:
        return "ppr"

    def fetch(self) -> list[dict]:
        # Look for CSVs in the manual_pulls directory
        raw_dir = os.path.join(os.path.dirname(__file__), '../../data/raw/ppr/manual_pulls/')
        search_pattern = os.path.join(raw_dir, "*.csv")
        files = glob.glob(search_pattern)
        
        if not files:
            self.logger.info(f"No PPR CSV files found in {raw_dir}. Please place manual exports there.")
            return []
            
        raw_data = []
        for file_path in files:
            self.logger.info(f"Reading PPR data from {file_path}")
            try:
                # The PSRA CSV uses CP1252 encoding
                with open(file_path, 'r', encoding='cp1252') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        raw_data.append(row)
            except Exception as e:
                self.logger.error(f"Failed to read file {file_path}: {e}")
                
        return raw_data

    def validate(self, raw_record: dict) -> PropertySaleSchema | None:
        try:
            # Expected CSV columns: Date of Sale (dd/mm/yyyy), Address, Price (Euro) etc.
            # We need to clean the price string (remove € and commas)
            price_str = raw_record.get('Price (Euro)', '0').replace('€', '').replace(',', '').strip()
            # If the CSV has slightly different headers, try lowercase or different variations if needed.
            if 'Price (Euro)' not in raw_record and 'Price' in raw_record:
                price_str = raw_record.get('Price', '0').replace('€', '').replace(',', '').strip()

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

    def load(self, validated_record: PropertySaleSchema) -> bool:
        stmt = insert(PropertySale).values(
            sale_date=validated_record.sale_date,
            price_eur=validated_record.price_eur,
            address_raw=validated_record.address_raw,
            source_name=validated_record.source_name,
            # we omit area_id/lat/lon for now as we don't have geocoding yet
        )
        
        # Idempotent upsert based on natural key (sale_date, address_raw, price_eur)
        update_dict = {
            'ingested_at': datetime.now()
        }
        
        upsert_stmt = stmt.on_conflict_do_update(
            constraint='uq_property_sales_date_address_price',
            set_=update_dict
        )
        
        try:
            self.db.execute(upsert_stmt)
            return True
        except Exception as e:
            self.logger.error(f"DB insert failed: {e}")
            return False
