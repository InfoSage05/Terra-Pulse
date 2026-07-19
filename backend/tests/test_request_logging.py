"""Guards the request-logging contract in backend/app/middleware/request_logging.py:
the raw API key must never appear in log output, only "present"/"missing"."""
import logging

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)
SECRET_KEY = "dev_secret_key"


def test_request_logging_never_leaks_raw_api_key(caplog):
    with caplog.at_level(logging.INFO, logger="backend"):
        client.get("/v1/areas/", headers={"X-API-Key": SECRET_KEY})

    for record in caplog.records:
        assert SECRET_KEY not in record.getMessage()
        request_info = getattr(record, "request_info", {})
        assert SECRET_KEY not in str(request_info)
        assert request_info.get("api_key_id") in (None, "present", "missing")
