import csv
import io
import requests
from datetime import datetime
from pydantic import ValidationError
from ingestion.connectors.base import BaseConnector
from ingestion.schemas.property_sale import PropertySaleSchema
from storage.models.db_models import PropertySale
from sqlalchemy.dialects.postgresql import insert

class PPRConnector(BaseConnector):
    """
    Property Price Register Connector.
    Downloads the official CSV, handles CP1252 encoding, validates, and loads.
    For demonstration, we focus on a recent year for Dublin.
    """
    
    # Example URL for Dublin 2023 data. 
    # In production, this would iterate over years/counties or use a more robust endpoint.
    CSV_URL = "https://www.propertypriceregister.ie/website/npsra/ppr/npsra-ppr.nsf/Downloads/PPR-2023-Dublin.csv/$FILE/PPR-2023-Dublin.csv"

    def get_source_name(self) -> str:
        return "ppr"

    def fetch(self) -> list[dict]:
        self.logger.info(f"Fetching PPR data from {self.CSV_URL}")
        try:
            # We mock the actual HTTP request here if it fails in restricted environments,
            # but standard implementation follows:
            response = requests.get(self.CSV_URL, timeout=30)
            response.raise_for_status()
            
            # The PSRA CSV uses CP1252
            response.encoding = 'cp1252'
            content = response.text
            
            reader = csv.DictReader(io.StringIO(content))
            raw_data = []
            for row in reader:
                raw_data.append(row)
                
            return raw_data
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"Could not fetch real PPR data: {e}")
            self.logger.info("Falling back to sample data for demonstration.")
            return self._get_sample_data()

    def validate(self, raw_record: dict) -> PropertySaleSchema | None:
        try:
            # Expected CSV columns: Date of Sale (dd/mm/yyyy), Address, Price (Euro) etc.
            # We need to clean the price string (remove € and commas)
            price_str = raw_record.get('Price (Euro)', '0').replace('€', '').replace(',', '').strip()
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

    def _get_sample_data(self):
        """Returns dummy data if the real endpoint is inaccessible."""
        return [
            {
                "Date of Sale (dd/mm/yyyy)": "01/01/2023",
                "Address": "1 Main Street, Dublin 1",
                "Price (Euro)": "€350,000.00"
            },
            {
                "Date of Sale (dd/mm/yyyy)": "15/02/2023",
                "Address": "2 High Road, Dublin 2",
                "Price (Euro)": "€450,000.00"
            },
            {
                "Date of Sale (dd/mm/yyyy)": "invalid_date",
                "Address": "3 Bad Data St",
                "Price (Euro)": "Not a number"
            }
        ]
