import pytest
from unittest.mock import MagicMock
from agents_layer.steps.score import run_score
from agents_layer.schemas.score_result import ScoreResult, FlagEnum
from agents_layer.schemas.extraction_result import ExtractionResult, TopicEnum, SentimentEnum

def test_score_enforces_low_confidence_flag():
    # Setup mock
    mock_client = MagicMock()
    
    # Return a score with confidence < 0.3 but without the flag
    expected_result = ScoreResult(
        area_id=1,
        summary="Not enough data.",
        livability_signal=0.0,
        confidence=0.2,
        flags=[]
    )
    mock_client.generate_structured.return_value = expected_result
    
    # Provide a dummy extraction
    extractions = [
        ExtractionResult(
            topics=[TopicEnum.general],
            key_facts=["Just a test fact"],
            sentiment=SentimentEnum.neutral,
            mentioned_entities=[]
        )
    ]
    
    # Run score
    result = run_score(extractions=extractions, area_id=1, llm_client=mock_client, confidence_threshold=0.3)
    
    assert result is not None
    # The low_source_count flag should be appended by our logic
    assert FlagEnum.low_source_count in result.flags
    assert result.confidence == 0.2
    
def test_score_enforces_area_id():
    mock_client = MagicMock()
    
    # LLM hallucinates the wrong area_id (99 instead of 1)
    expected_result = ScoreResult(
        area_id=99,
        summary="Area 99 is great.",
        livability_signal=0.5,
        confidence=0.8,
        flags=[]
    )
    mock_client.generate_structured.return_value = expected_result
    
    extractions = [
        ExtractionResult(
            topics=[TopicEnum.general],
            key_facts=["Fact 1"],
            sentiment=SentimentEnum.positive,
            mentioned_entities=[]
        )
    ]
    
    # Run score asking for area_id 1
    result = run_score(extractions=extractions, area_id=1, llm_client=mock_client)
    
    assert result is not None
    # Our logic should override it to 1
    assert result.area_id == 1
