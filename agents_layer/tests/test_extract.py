import pytest
from unittest.mock import MagicMock
from agents_layer.steps.extract import run_extract
from agents_layer.schemas.extraction_result import ExtractionResult, TopicEnum, SentimentEnum

def test_extract_returns_validated_schema():
    # Setup a mock LLMClient
    mock_client = MagicMock()
    
    # Configure mock to return a valid ExtractionResult
    expected_result = ExtractionResult(
        topics=[TopicEnum.development, TopicEnum.general],
        key_facts=["New center opening.", "Youth programs added."],
        sentiment=SentimentEnum.positive,
        mentioned_entities=["Dublin City Council", "Dublin 1"]
    )
    mock_client.generate_structured.return_value = expected_result
    
    # Run extract
    result = run_extract(raw_text="Sample text", area_id=1, llm_client=mock_client)
    
    assert result is not None
    assert result.sentiment == SentimentEnum.positive
    assert len(result.topics) == 2
    mock_client.generate_structured.assert_called_once()
