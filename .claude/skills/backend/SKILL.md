---
name: backend
description: Guidelines and instructions for the Backend Layer, including known problems to fix.
---

# Backend Layer Guidelines

When working on the Backend Layer for TerraPulse, strictly adhere to the following rules:

1. **Framework**: Use FastAPI to serve a strict REST API.
2. **Endpoints**:
   - Price predictions: `POST /v1/predict/price`
   - Structured area scores: `GET /v1/areas/{id}/score`
3. **Review Gate Passthrough (CRITICAL)**: The `/v1/areas/{id}/score` endpoint MUST preserve the `needs_human_review` boolean from the Agents layer. Never silently average a flagged signal into a clean score.
4. **Stateless Inference**: Endpoints must run fast inference on-request by querying active models directly from the file registry. Cache score outputs in Redis for fast map rendering.

## Known Backend Problems to Fix ASAP
- **Redis cache invalidation is a no-op**: `clear_redis_cache()` deletes keys in Redis, but the backend currently uses NO Redis at all. Either wire Redis into the backend for caching scores, or drop the invalidation code entirely.
