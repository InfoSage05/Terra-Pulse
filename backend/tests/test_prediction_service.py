from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services import prediction_service
from shared.model_contract import PricePredictionInput

client = TestClient(app)


async def test_predict_price_no_active_model_raises_value_error(async_db_session):
    with patch("backend.app.services.prediction_service.get_active_model_metadata", return_value=None):
        with pytest.raises(ValueError, match="No active price model available"):
            await prediction_service.predict_price(async_db_session, PricePredictionInput(area_id=1))


async def test_predict_price_missing_artifact_raises_value_error(async_db_session):
    fake_meta = type("FakeMeta", (), {"version": "v1"})()
    with patch("backend.app.services.prediction_service.get_active_model_metadata", return_value=fake_meta), \
         patch("backend.app.services.prediction_service.load_model_artifact", return_value=None):
        with pytest.raises(ValueError, match="Active model artifact not found"):
            await prediction_service.predict_price(async_db_session, PricePredictionInput(area_id=1))


def test_predict_price_endpoint_maps_value_error_to_400():
    """The router (backend/app/api/v1/predict.py) must translate a
    prediction_service ValueError - either failure path above - into an
    HTTP 400, not a raw 500."""
    with patch("backend.app.api.v1.predict.predict_price", side_effect=ValueError("No active price model available")):
        response = client.post(
            "/v1/predict/price",
            headers={"X-API-Key": "dev_secret_key"},
            json={"area_id": 1},
        )
    assert response.status_code == 400
    assert "No active price model available" in response.json()["detail"]


def test_predict_price_endpoint_area_not_found_maps_to_404():
    with patch("backend.app.api.v1.predict.predict_price", return_value=None):
        response = client.post(
            "/v1/predict/price",
            headers={"X-API-Key": "dev_secret_key"},
            json={"area_id": 999999},
        )
    assert response.status_code == 404
