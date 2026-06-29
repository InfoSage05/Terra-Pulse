# Architecture: Ingestion & Storage Layers

This document outlines the architectural decisions for the data ingestion and storage layers of the TerraPulse platform.

## Design Principles

1. **Schema-First Validation**: All data fetched from external sources must pass strictly typed Pydantic validation schemas.
2. **Dead Letter Queue (DLQ)**: Any record failing validation or database insertion is serialized as JSON and stored in `data/dead_letter/`. The pipeline will never crash due to a bad record.
3. **Idempotency**: Connectors are designed to be run repeatedly on the same source data without duplicating rows. Upserts are performed based on natural composite keys.
4. **Source Traceability**: Every table includes `source_name` and `ingested_at` columns.
5. **Configurable Boundaries**: The concept of an "Area" is completely decoupled from any hardcoded strings. The system maps coordinates to areas using PostGIS `ST_Contains` spatial joins, allowing easy expansion beyond Dublin.

## Storage Layer
- **PostgreSQL + PostGIS**: Used for primary relational storage and geospatial operations.
- **SQLAlchemy**: Used for the Data Access Layer without heavy ORM business logic.
- **Migrations**: Plain SQL files numbered sequentially.

### Core Schema
- `areas`: Stores the `geometry` (POLYGON) for regions (e.g., postal districts).
- `property_sales`: Records housing transactions.
- `amenities`: Point data for hospitals, schools, parks, etc.
- `area_demographics`: Census-level demographic data mapped to areas.
- `crime_stats`: Garda reported crime by division.

## Ingestion Layer
- **BaseConnector**: An abstract base class defining the `fetch -> validate -> load` ETL pipeline.
- Connectors run synchronously, parsing inputs and yielding valid `Pydantic` models that map to SQLAlchemy inserts.
- **Error Handling**: Connectors log summaries (Fetched, Validated, Upserted, Rejected, Errors) directly to standard output upon completion.

## Agents Layer
- **Sequential Pipeline**: Processes unstructured text via a 3-step pipeline (Extract -> Score -> Fuse). No multi-agent swarms.
- **Strict Typed Contracts**: Each LLM step is forced to output JSON matching Pydantic schemas. Invalid outputs are retried once, then dead-lettered.
- **Deterministic Review Gate**: The final Fuse step uses hardcoded logic to compare the agent's qualitative livability signal against structured metrics. Disagreements automatically flag the summary for human review (
eeds_human_review = True).

## Models Layer
- **Sequential Evaluation**: Machine learning models (e.g. Price Prediction using LightGBM) and rule-based models (Affordability, Safety, Livability) are versioned and stored in `models_layer/registry/models`.
- **Promotion Rule**: A model is only promoted to active (`is_active=True`) if it strictly outperforms the current active model in its specific metric.
- **Scoring Formulas**:
  - Affordability: `Score = max(0, 100 - (Price / 10000) * 0.6 - (Deprivation * 10) * 0.4)`
  - Safety: `Score = max(0, 100 - (Crime / Population * 1000) * 2)`

## Backend Layer (FastAPI)
- **API Interface**: A strict REST API serves area data, price predictions (`POST /v1/predict/price`), and structured area scores (`GET /v1/areas/{id}/score`).
- **Review Gate Passthrough**: The `/v1/areas/{id}/score` endpoint preserves the `needs_human_review` boolean from Phase 2 unstructured processing. It must never silently average a flagged signal into a clean score.
- **Stateless Inference**: Endpoints run fast inference on-request by querying active models directly from the file registry.
