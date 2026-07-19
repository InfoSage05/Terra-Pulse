"""Liveness/readiness endpoints. Deliberately outside `api_router` (no
X-API-Key required) since orchestrators/load balancers hit these directly,
often without any credentials configured.
"""
from fastapi import APIRouter, Response, status
from sqlalchemy import text

from backend.app.core.cache import get_redis_client
from backend.app.db.session import get_db

router = APIRouter()


@router.get("/health")
def health():
    """Liveness only - the process is up and serving requests. No
    dependency checks, so this never fails just because Postgres or Redis
    is having a bad day; that's what /ready is for."""
    return {"status": "ok"}


@router.get("/ready")
async def ready(response: Response):
    """Readiness - checks Postgres (required) and Redis (optional, since
    caching is designed to fail soft - see backend/app/core/cache.py).
    Redis being down degrades performance but never breaks correctness, so
    it must not fail readiness on its own; only a broken Postgres does."""
    checks = {"db": "ok", "redis": "ok"}

    try:
        async for db in get_db():
            await db.execute(text("SELECT 1"))
            break
    except Exception:
        checks["db"] = "down"

    redis_client = get_redis_client()
    if redis_client is None:
        checks["redis"] = "degraded"
    else:
        try:
            redis_client.ping()
        except Exception:
            checks["redis"] = "degraded"

    if checks["db"] != "ok":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return checks
