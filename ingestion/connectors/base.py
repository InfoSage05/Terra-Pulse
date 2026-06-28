import abc
import os
import json
from datetime import datetime
from pydantic import ValidationError
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ingestion.utils.logging_config import setup_logger

class BaseConnector(abc.ABC):
    """
    Abstract base class for all data connectors.
    Defines the standard fetch -> validate -> load pipeline.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = setup_logger(self.__class__.__name__)
        self.source_name = self.get_source_name()
        
        # Ensure dead letter directory exists
        self.dead_letter_dir = os.path.join(
            os.path.dirname(__file__), '../../data/dead_letter'
        )
        os.makedirs(self.dead_letter_dir, exist_ok=True)
        
        # Stats
        self.stats = {
            "fetched": 0,
            "validated": 0,
            "rejected": 0,
            "upserted": 0,
            "errors": 0
        }

    @abc.abstractmethod
    def get_source_name(self) -> str:
        """Return the source name (e.g., 'ppr', 'osm')."""
        pass

    @abc.abstractmethod
    def fetch(self) -> list[dict]:
        """Fetch raw data from the source. Returns a list of dictionaries."""
        pass

    @abc.abstractmethod
    def validate(self, raw_record: dict) -> object | None:
        """
        Validate a single raw record against its Pydantic schema.
        Returns the validated Pydantic object, or None if validation fails.
        """
        pass

    @abc.abstractmethod
    def load(self, validated_record: object) -> bool:
        """
        Load a single validated record into the database (upsert).
        Returns True if successful, False otherwise.
        """
        pass

    def run(self):
        """Execute the full pipeline and report summary."""
        self.logger.info(f"Starting ingestion for {self.source_name}")
        
        raw_data = []
        try:
            raw_data = self.fetch()
            self.stats["fetched"] = len(raw_data)
        except Exception as e:
            self.logger.error(f"Failed to fetch data: {e}")
            return
            
        for record in raw_data:
            try:
                validated = self.validate(record)
                if validated:
                    self.stats["validated"] += 1
                    if self.load(validated):
                        self.stats["upserted"] += 1
                    else:
                        self.stats["errors"] += 1
                else:
                    self._dead_letter(record, "Validation failed")
            except Exception as e:
                self.logger.error(f"Unexpected error processing record: {e}")
                self._dead_letter(record, str(e))
                self.stats["errors"] += 1
                
        # Final commit for the batch
        try:
            self.db.commit()
        except SQLAlchemyError as e:
            self.logger.error(f"Final commit failed: {e}")
            self.db.rollback()
            
        self.print_summary()

    def _dead_letter(self, record: dict, reason: str):
        """Write invalid record to a dead letter file."""
        self.stats["rejected"] += 1
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.source_name}_{timestamp}_{self.stats['rejected']}.json"
        filepath = os.path.join(self.dead_letter_dir, filename)
        
        dead_letter_payload = {
            "source": self.source_name,
            "timestamp": datetime.now().isoformat(),
            "reason": reason,
            "record": record
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(dead_letter_payload, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to write dead letter: {e}")

    def print_summary(self):
        """Print execution summary."""
        self.logger.info("--- Ingestion Summary ---")
        self.logger.info(f"Source:    {self.source_name}")
        self.logger.info(f"Fetched:   {self.stats['fetched']}")
        self.logger.info(f"Validated: {self.stats['validated']}")
        self.logger.info(f"Rejected:  {self.stats['rejected']}")
        self.logger.info(f"Upserted:  {self.stats['upserted']}")
        self.logger.info(f"Errors:    {self.stats['errors']}")
        self.logger.info("-------------------------")
