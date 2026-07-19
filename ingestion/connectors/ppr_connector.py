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
from ingestion.utils.geocoding import resolve_area_id_from_address
from storage.models.db_models import PropertySale
from sqlalchemy.dialects.postgresql import insert

# Number of most-recent per-run CSV/JSON export pairs to retain under
# data/processed/ppr/. Older pairs are deleted on each run to avoid
# unbounded disk growth.
PROCESSED_RUNS_TO_KEEP = 10
class PPRConnector(BaseConnector):
    """
    Property Price Register Connector.

    Uses Playwright (headless Chromium) to drive the PSRA/IBM Domino
    "PPRDownloads" form at propertypriceregister.ie: the front page is
    behind an F5 bot-defense JS challenge (TSPD cookies), so a plain
    `requests` call to any deep URL - including the old direct
    'PPR-ALL.zip' link - gets rejected with a 400 "Unknown Command
    Exception" from the Domino server before it ever reaches the form
    handler. A real browser is required to pass the JS challenge and to
    exercise the actual download form (County/Year/Month selects -> POST
    -> a per-request "CLICK HERE TO DOWNLOAD THE FILE" link).

    We submit the form for County=Dublin and the current calendar year
    (Month=ALL), which both keeps us scoped to the data we care about and
    avoids the old behaviour of re-downloading the entire national
    'PPR-ALL.zip' on every run just to filter down to Dublin - the site
    itself filters by county/year for us and hands back a small
    Dublin-only CSV (a few thousand rows for the current year, vs. the
    national file's hundreds of thousands).
    """

    DOWNLOADS_URL = 'https://www.propertypriceregister.ie/website/npsra/pprweb.nsf/PPRDownloads?OpenForm'
    BASE_URL = 'https://www.propertypriceregister.ie'
    USER_AGENT = (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/120.0 Safari/537.36'
    )

    def get_source_name(self) -> str:
        return "ppr"

    def fetch(self) -> list[dict]:
        self.logger.info("Starting PPR extraction via PPRDownloads form (Playwright)...")
        raw_data = []

        try:
            from playwright.sync_api import sync_playwright

            year = str(datetime.now().year)

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                try:
                    ctx = browser.new_context(
                        ignore_https_errors=True,
                        accept_downloads=True,
                        user_agent=self.USER_AGENT,
                    )
                    page = ctx.new_page()

                    self.logger.info(f"Loading {self.DOWNLOADS_URL}")
                    page.goto(self.DOWNLOADS_URL, timeout=60000)
                    # Let the F5/TSPD bot-defense JS challenge finish and the
                    # real form render.
                    page.wait_for_selector('#County', timeout=30000)

                    page.select_option('#County', 'Dublin')
                    page.select_option('#Year', year)
                    page.select_option('#StartMonth', 'ALL')

                    self.logger.info(f"Submitting download form for Dublin/{year}/ALL...")
                    page.click('input[type="submit"]')

                    download_link = page.wait_for_selector(
                        'a:has-text("CLICK HERE TO DOWNLOAD THE FILE")', timeout=30000
                    )

                    csv_bytes = None
                    try:
                        with page.expect_download(timeout=30000) as dl_info:
                            download_link.click()
                        download = dl_info.value
                        tmp_path = download.path()
                        with open(tmp_path, 'rb') as f:
                            csv_bytes = f.read()
                    except Exception:
                        # Some environments don't fire a Playwright "download"
                        # event for inline content-disposition; fall back to
                        # fetching the resolved href directly with the
                        # browser's own (already-authenticated) request
                        # context, which carries the TSPD/session cookies.
                        href = download_link.get_attribute('href')
                        file_url = href if href.startswith('http') else self.BASE_URL + href
                        self.logger.info(f"Falling back to direct fetch of {file_url}")
                        api_resp = ctx.request.get(file_url)
                        if not api_resp.ok:
                            raise RuntimeError(
                                f"Download fallback failed: HTTP {api_resp.status}"
                            )
                        csv_bytes = api_resp.body()
                finally:
                    browser.close()

            if not csv_bytes:
                raise RuntimeError("No CSV content retrieved from PPR download form.")

            self.logger.info("Parsing downloaded Dublin CSV...")
            # The CSV encoding is cp1252.
            text_stream = io.StringIO(csv_bytes.decode('cp1252'))
            reader = csv.DictReader(text_stream)

            for row in reader:
                # The form already scopes the file to Dublin, but keep the
                # defensive filter in case the site ever changes behaviour.
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
                
            address_raw = raw_record.get('Address', '').strip()
            area_id = resolve_area_id_from_address(self.db, address_raw)

            validated = PropertySaleSchema(
                sale_date=date_val,
                price_eur=price_val,
                address_raw=address_raw,
                area_id=area_id,
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

            self._cleanup_old_exports(export_dir)

    def _cleanup_old_exports(self, export_dir: str):
        """
        Retention policy: keep only the most recent PROCESSED_RUNS_TO_KEEP
        per-run CSV/JSON export pairs in export_dir, deleting older ones.
        """
        try:
            csv_files = sorted(
                glob.glob(os.path.join(export_dir, 'ppr_dublin_*.csv')),
                key=os.path.getmtime,
                reverse=True
            )
            stale_csv_files = csv_files[PROCESSED_RUNS_TO_KEEP:]
            for csv_path in stale_csv_files:
                base = os.path.splitext(csv_path)[0]
                json_path = base + '.json'
                for path in (csv_path, json_path):
                    if os.path.exists(path):
                        os.remove(path)
                        self.logger.debug(f"Removed stale export file: {path}")

            if stale_csv_files:
                self.logger.info(
                    f"Cleaned up {len(stale_csv_files)} old export run(s), "
                    f"keeping the {PROCESSED_RUNS_TO_KEEP} most recent."
                )
        except Exception as e:
            self.logger.error(f"Failed to clean up old exports: {e}")

    def load(self, validated_record: PropertySaleSchema) -> bool:
        stmt = insert(PropertySale).values(
            sale_date=validated_record.sale_date,
            price_eur=validated_record.price_eur,
            address_raw=validated_record.address_raw,
            area_id=validated_record.area_id,
            source_name=validated_record.source_name,
        )

        # Idempotent upsert based on natural key
        update_dict = {
            'ingested_at': datetime.now(),
            'area_id': validated_record.area_id,
        }
        
        upsert_stmt = stmt.on_conflict_do_update(
            constraint='uq_property_sales_date_address_price',
            set_=update_dict
        )
        
        # Let exceptions propagate - BaseConnector.run() wraps each record's
        # load() in a SAVEPOINT and handles rollback/logging there, so a bad
        # row doesn't poison the rest of the connector's shared session.
        self.db.execute(upsert_stmt)
        if hasattr(self, 'validated_records_for_export'):
            self.validated_records_for_export.append(validated_record)
        return True
