import pytest
from agents_layer.steps.fuse import run_fuse
from agents_layer.schemas.score_result import ScoreResult, FlagEnum

def test_fuse_disagreement_catches_needs_human_review():
    # Setup a mock ScoreResult that is highly positive
    score = ScoreResult(
        area_id=1,
        summary="This area is thriving with new amenities and great community spirit.",
        livability_signal=0.8,  # Highly positive
        confidence=0.9,
        flags=[]
    )
    
    # Setup mock structured data that shows a contradictory negative trend (e.g., crime rising 20%)
    structured_data = {
        "crime_trend": 0.20,
        "price_trend": -0.05
    }
    
    # Run the deterministic fuse step
    fused = run_fuse(
        score=score,
        run_id="test-run-123",
        model_name="test-model",
        structured_data=structured_data,
        source_count=3
    )
    
    # The contradictory signals (agent positive, but structured data says crime rising) 
    # should trigger the needs_human_review flag.
    assert fused.needs_human_review is True
    assert fused.livability_signal == 0.8
    assert fused.structured_data_snapshot == structured_data

def test_fuse_agreement_does_not_flag():
    # Setup a mock ScoreResult that is positive
    score = ScoreResult(
        area_id=1,
        summary="This area is thriving.",
        livability_signal=0.6,
        confidence=0.8,
        flags=[]
    )
    
    # Setup mock structured data that aligns (crime dropping, prices stable)
    structured_data = {
        "crime_trend": -0.10,
        "price_trend": 0.05
    }
    
    fused = run_fuse(
        score=score,
        run_id="test-run-123",
        model_name="test-model",
        structured_data=structured_data,
        source_count=3
    )
    
    # Should not be flagged
    assert fused.needs_human_review is False

def test_fuse_low_confidence_flags_review():
    # Setup a mock ScoreResult that has low confidence
    score = ScoreResult(
        area_id=1,
        summary="Not much info here.",
        livability_signal=0.0,
        confidence=0.2, # Below 0.3 threshold
        flags=[FlagEnum.low_source_count]
    )
    
    structured_data = {
        "crime_trend": 0.0,
        "price_trend": 0.0
    }
    
    fused = run_fuse(
        score=score,
        run_id="test-run-123",
        model_name="test-model",
        structured_data=structured_data,
        source_count=1
    )
    
    assert fused.needs_human_review is True
