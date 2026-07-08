import csv
import io
import os
import glob
import tempfile
from datetime import datetime
from pydantic import ValidationError
from ingestion.connectors.base import BaseConnector
from ingestion.schemas.property_sale import PropertySaleSchema
from storage.models.db_models import PropertySale
from sqlalchemy.dialects.postgresql import insert
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

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
        self.logger.info("Starting headless browser for PPR extraction...")
        raw_data = []
        
        target_county = "Dublin"
        # For demonstration, we'll pull the current year.
        target_year = str(datetime.now().year)
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                
                self.logger.info(f"Navigating to PPR to fetch data for {target_county} {target_year}...")
                page.goto("https://www.propertypriceregister.ie/website/npsra/pprweb.nsf/PPR?OpenForm", timeout=60000)
                
                # Wait for the anti-bot challenge to pass and the real page to load
                self.logger.info("Waiting for page load (handling anti-bot redirect if necessary)...")
                page.wait_for_selector("select[name='County']", timeout=30000)
                
                # Select options
                page.select_option("select[name='County']", target_county)
                page.select_option("select[name='Year']", target_year)
                
                self.logger.info("Clicking Search...")
                # The search button is an input element
                page.locator("input[value='Perform Search']").first.click()
                
                self.logger.info("Waiting for search results...")
                # Wait for the download button to appear
                page.wait_for_selector("a:has-text('Download Results')", timeout=60000)
                
                self.logger.info("Triggering CSV download...")
                with page.expect_download(timeout=60000) as download_info:
                    page.locator("a:has-text('Download Results')").first.click()
                    
                download = download_info.value
                
                with tempfile.TemporaryDirectory() as tmpdir:
                    tmp_path = os.path.join(tmpdir, 'ppr_export.csv')
                    download.save_as(tmp_path)
                    
                    self.logger.info("Reading downloaded CSV data...")
                    with open(tmp_path, 'r', encoding='cp1252') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            raw_data.append(row)
                
                browser.close()
                self.logger.info(f"Successfully scraped {len(raw_data)} records using Playwright.")
                
        except PlaywrightTimeoutError:
            self.logger.error("Playwright timed out while trying to interact with the PPR page.")
        except Exception as e:
            self.logger.error(f"Playwright automation failed: {e}")
            
        return raw_data

    def validate(self, raw_record: dict) -> PropertySaleSchema | None:
        try:
            # Expected CSV columns: Date of Sale (dd/mm/yyyy), Address, Price (Euro) etc.
            price_str = raw_record.get('Price (Euro)', '0').replace('€', '').replace(',', '').strip()
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
            return True
        except Exception as e:
            self.logger.error(f"DB insert failed: {e}")
            return False
