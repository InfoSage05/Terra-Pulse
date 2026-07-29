---
name: ingestion
description: Guidelines and instructions for the Storage & Ingestion layer, including known problems to fix.
---

# Ingestion & Storage Layer Guidelines

When working on the Storage & Ingestion Layer for TerraPulse, strictly adhere to the following rules:

1. **Storage Tech Stack**: Use PostgreSQL with PostGIS for relational storage and geospatial operations (`ST_Contains`). Use SQLAlchemy for the data access layer.
2. **Validation**: All external data must pass strictly typed Pydantic validation schemas. This is a Schema-First approach.
3. **Dead Letter Queue (DLQ)**: If a record fails validation or DB insertion, do NOT crash the pipeline. Serialize the failed record as JSON and store it in `data/dead_letter/`.
4. **Idempotency**: Connectors run synchronously, performing upserts based on natural composite keys.
5. **PPR Ingestion Rules**: Do NOT attempt form submission for the official PSRA site. Instead, use a direct "DOWNLOAD ALL" endpoint (`PPR-ALL.zip`) to bypass form submission.
6. **Scheduling**: A background `APScheduler` job (`scheduled_refresh.py`) periodically runs connectors, exports data to `data/exports/ppr_dublin_master.csv`, logs runs, and invalidates Redis scores.

## Known Ingestion Problems to Fix ASAP
- **PPR downloads full national zip every run**: Re-downloaded daily just to keep Dublin. Needs incremental/delta logic.
- **PPR rows are not geocoded**: `area_id`, `lat`, `lon` are NULL in `property_sales` after ingestion. Must be geocoded.
- **Redundant CSV copies, no cleanup**: Per-run files accumulate in `data/processed/ppr/`. Only the master export should be canonical. Implement cleanup.
- **CSO & Crime connectors are stubs**: `cso_connector.py` and `crime_connector.py` return fake data. Must call real endpoints (CSO PxStat HPM04, CJA01, SAPS).
- **`ingestion_runs` never records row counts**: `rows_fetched`, `rows_upserted`, `rows_dead_lettered` stay at 0. Must be updated during ingestion.
