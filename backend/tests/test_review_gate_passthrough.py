"""Review Gate Passthrough tests.

Two layers of coverage on purpose:
  1. A router-level test with score_service mocked out - fast, catches
     regressions in the route/response-model wiring alone.
  2. `test_review_gate_passthrough_live` below, which exercises the *real*
     score_service.get_area_score against a live Postgres row (see
     conftest.py's `review_flagged_area` fixture) - this is the one that
     would actually catch a regression inside `_compute_area_score` itself
     (e.g. someone "simplifying" the SELECT and dropping needs_human_review,
     or averaging it into another score), which the mocked test above
     cannot see since it replaces that function entirely.
"""
from fastapi.testclient import TestClient
from unittest.mock import patch
from datetime import datetime
from backend.app.main import app
from shared.model_contract import AreaScoreOutput

client = TestClient(app)


def test_review_gate_passthrough():
    with patch("backend.app.api.v1.scores.get_area_score") as mock_get_score:
        mock_get_score.return_value = AreaScoreOutput(
            area_id=1,
            affordability_score=80.0,
            safety_score=90.0,
            livability_score=75.0,
            livability_confidence=0.8,
            needs_human_review=True,
            model_versions_used={},
            last_updated=datetime.now()
        )

        response = client.get("/v1/areas/1/score", headers={"X-API-Key": "dev_secret_key"})
        assert response.status_code == 200
        data = response.json()

        assert data["needs_human_review"] is True


def test_review_gate_passthrough_live(review_flagged_area):
    """Real DB row, real score_service - no mocking of the scoring logic."""
    area_id = review_flagged_area

    response = client.get(f"/v1/areas/{area_id}/score", headers={"X-API-Key": "dev_secret_key"})
    assert response.status_code == 200
    data = response.json()

    assert data["area_id"] == area_id
    assert data["needs_human_review"] is True
    # Guard against the "averaged away" failure mode: a flagged summary must
    # never be silently folded into a clean-looking livability_score - the
    # flag has to travel alongside the score, not replace or blend into it.
    assert data["livability_score"] is not None
    assert data["agent_summary"] == "Qualitative signal disagrees with hard metrics."
