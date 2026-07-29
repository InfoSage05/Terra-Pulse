---
name: backend
description: Guidelines and instructions for the Backend Layer, including known problems to fix.
---

# Backend Layer Guidelines

When working on the Backend Layer for TerraPulse, strictly adhere to the following rules:

1. **Framework**: FastAPI, fully async (async def routes, SQLAlchemy `AsyncSession` via `asyncpg` - see `backend/app/db/session.py`).
2. **Endpoints**:
   - Price predictions: `POST /v1/predict/price`
   - Structured area scores: `GET /v1/areas/{id}/score`
   - Liveness/readiness: `GET /health`, `GET /ready` (outside `api_router`, no API key required)
3. **Review Gate Passthrough (CRITICAL)**: The `/v1/areas/{id}/score` endpoint MUST preserve the `needs_human_review` boolean from the Agents layer. Never silently average a flagged signal into a clean score. Covered by both a mocked router test and a live-DB test in `backend/tests/test_review_gate_passthrough.py`.
4. **Stateless Inference**: Endpoints run fast inference on-request by querying active models from the file registry (`models_layer/registry/registry.py`), which caches unpickled artifacts in-process keyed by `(model_type, version)` - see "Caching Contract" below.
5. **Scoring formulas live in `shared/scoring_formulas.py`**, not inline in `score_service.py` - training scripts and the backend must both import from there so a tuning change only has to happen once.

## Caching & Model Registry Contract

Redis caching (`backend/app/core/cache.py`) is real and wired in, fail-soft
(a Redis outage falls back to computing live from Postgres, never breaks
the API):

| Cache key pattern | Written by | TTL setting |
|---|---|---|
| `area_scores:{area_id}` | `score_service.get_area_score` | `AREA_SCORE_CACHE_TTL_SECONDS` (default 3600s) |
| `area_list:areas:{limit}:{offset}` | `area_service.get_areas` | `AREA_LIST_CACHE_TTL_SECONDS` (default 900s) |
| `area_list:summary` | `area_service.get_area_summaries` | same |
| `area_list:neighborhoods:{sort_by}:{limit}` | `neighborhood_service.get_neighborhoods` | same |
| `area_list:neighborhoods_featured:{limit}` | `neighborhood_service.get_featured_neighborhoods` | same |

Both prefixes (`area_scores:*`, `area_list:*`) are swept by
`ingestion/jobs/scheduled_refresh.py::clear_redis_cache()` after every
ingestion run - a new cache key pattern MUST use one of these two prefixes
(via `area_score_key()`/`area_list_key()` in `core/cache.py`) or it will
never be invalidated by a data refresh.

`models_layer/registry/registry.py::load_model_artifact` additionally
caches unpickled model artifacts in an in-process dict (not Redis - this
one avoids repeated disk I/O within a single backend process, not
cross-process staleness), evicted when a new version of that `model_type`
is activated via `save_model()`.

## Known Backend Problems (resolved)

- ~~Redis cache invalidation is a no-op~~ - resolved; see the contract table above.
- ~~No automated migration runner~~ - resolved; `storage/scripts/run_migrations.py` is idempotent (tracks applied files in a `schema_migrations` table) and runs on every `backend`/`scheduler` container start (`backend/Dockerfile`).
