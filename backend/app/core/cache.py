"""Redis cache wrapper for the backend.

Provides a thin, fail-soft wrapper around the `redis` client so that a Redis
outage never breaks the API - callers should treat every method here as
"best effort": on any failure it logs a warning and returns None / False so
the caller can fall back to computing the result live from Postgres.

Key patterns written here MUST match the patterns invalidated by
`ingestion/jobs/scheduled_refresh.py::clear_redis_cache()`:
    - "area_scores:{area_id}" -> matches "area_scores:*"
    - "area_list:{name}" -> matches "area_list:*", used by area_service.py
      and neighborhood_service.py for the /v1/areas and /v1/neighborhoods
      list endpoints.
"""
import datetime
import decimal
import logging
from typing import Optional

import redis

from backend.app.core.config import settings

logger = logging.getLogger("terrapulse.backend.cache")

AREA_SCORE_KEY_PREFIX = "area_scores"
AREA_LIST_KEY_PREFIX = "area_list"


def _make_client() -> Optional["redis.Redis"]:
    try:
        client = redis.Redis.from_url(settings.REDIS_URL, socket_connect_timeout=1, socket_timeout=1)
        client.ping()
        return client
    except Exception as e:
        logger.warning(f"Redis unavailable ({settings.REDIS_URL}): {e}. Caching disabled, falling back to live queries.")
        return None


# A single lazily-initialized client, re-checked on each call in case Redis
# comes back up after being down (cheap since redis-py pools connections).
_client: Optional["redis.Redis"] = None
_client_checked = False


def get_redis_client() -> Optional["redis.Redis"]:
    global _client, _client_checked
    if _client is not None:
        return _client
    # Re-attempt connection lazily rather than caching a permanent failure,
    # so Redis coming back online is picked up without a backend restart.
    _client = _make_client()
    _client_checked = True
    return _client


def area_score_key(area_id: int) -> str:
    return f"{AREA_SCORE_KEY_PREFIX}:{area_id}"


def area_list_key(name: str) -> str:
    """`name` should already encode any distinguishing query params, e.g.
    area_list_key(f"areas:{limit}:{offset}") - different param combos are
    different cache entries, all still swept by clear_redis_cache()'s
    "area_list:*" glob."""
    return f"{AREA_LIST_KEY_PREFIX}:{name}"


def json_default(obj):
    """`default=` callback for json.dumps() when caching raw SQL result rows.

    Postgres NUMERIC columns (e.g. neighborhood_data.median_sold_price) come
    back as decimal.Decimal via psycopg2, and DATE columns as datetime.date -
    neither is JSON-serializable by default, unlike the FastAPI response path
    (which runs everything through jsonable_encoder). Raises TypeError for
    anything else, matching json.dumps()'s normal behavior for unknown types.
    """
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def cache_get(key: str) -> Optional[str]:
    client = get_redis_client()
    if client is None:
        return None
    try:
        value = client.get(key)
        if value is None:
            return None
        return value.decode("utf-8") if isinstance(value, bytes) else value
    except Exception as e:
        logger.warning(f"Redis GET failed for key={key}: {e}")
        return None


def cache_set(key: str, value: str, ttl_seconds: Optional[int] = None) -> bool:
    client = get_redis_client()
    if client is None:
        return False
    try:
        client.set(key, value, ex=ttl_seconds)
        return True
    except Exception as e:
        logger.warning(f"Redis SET failed for key={key}: {e}")
        return False
