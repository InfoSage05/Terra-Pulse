from pydantic import BaseModel, ConfigDict
from typing import List
from enum import Enum

class TopicEnum(str, Enum):
    development = "development"
    crime_incident = "crime_incident"
    amenity_change = "amenity_change"
    transport_change = "transport_change"
    general = "general"

class SentimentEnum(str, Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"
    mixed = "mixed"

class ExtractionResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    topics: List[TopicEnum]
    key_facts: List[str]
    sentiment: SentimentEnum
    mentioned_entities: List[str]
