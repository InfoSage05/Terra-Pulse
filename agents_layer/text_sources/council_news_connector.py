import os
import json
from datetime import datetime
from pydantic import BaseModel, ValidationError
from ingestion.connectors.base import BaseConnector
from ingestion.utils.geocoding import resolve_area_id_by_name

class RawArticleSchema(BaseModel):
    area_id: int
    title: str
    content: str
    url: str
    source_name: str
    published_date: str

class CouncilNewsConnector(BaseConnector):
    """
    Scrapes official council news feeds for the Dublin area.
    Reuses the BaseConnector pattern to fetch, validate, and store raw text.
    """
    
    def get_source_name(self) -> str:
        return "council_news"

    def fetch(self) -> list[dict]:
        self.logger.info("Fetching Dublin City Council & South Dublin County Council news")
        return self._get_sample_data()

    def validate(self, raw_record: dict) -> RawArticleSchema | None:
        try:
            validated = RawArticleSchema(
                area_id=raw_record["area_id"],
                title=raw_record["title"],
                content=raw_record["content"],
                url=raw_record["url"],
                source_name=self.source_name,
                published_date=raw_record["published_date"]
            )
            return validated
        except ValidationError as e:
            self.logger.debug(f"Validation error: {e}")
            return None

    def load(self, validated_record: RawArticleSchema) -> bool:
        """
        For text sources, 'load' means saving the validated raw text to disk 
        for the agent pipeline to process later.
        """
        raw_dir = os.path.join(
            os.path.dirname(__file__), '../../../data/raw/council_news/'
        )
        os.makedirs(raw_dir, exist_ok=True)
        
        # Simple file-based storage using area_id and timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f"area_{validated_record.area_id}_{timestamp}.json"
        filepath = os.path.join(raw_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(validated_record.model_dump_json(indent=2))
            return True
        except Exception as e:
            self.logger.error(f"Failed to save raw text: {e}")
            return False

    def _get_sample_data(self):
        # We simulate finding two articles for Dublin 1
        db_gen = self.db
        area_id = resolve_area_id_by_name(db_gen, "Dublin 1") or 1
        
        return [
            {
                "area_id": area_id,
                "title": "New Community Center in Dublin 1",
                "content": "Dublin City Council is pleased to announce the opening of a new community center in Dublin 1. This state-of-the-art facility will provide youth programs and adult education classes.",
                "url": "https://www.dublincity.ie/news/new-community-center",
                "published_date": "2023-10-01"
            },
            {
                "area_id": area_id,
                "title": "Anti-Social Behavior Enforcement",
                "content": "Recent increases in anti-social behavior in Dublin 1 have led the council to increase security patrols and install new CCTV cameras in the area.",
                "url": "https://www.dublincity.ie/news/security-update",
                "published_date": "2023-10-15"
            }
        ]
