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
