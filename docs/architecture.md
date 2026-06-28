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
