# TerraPulse Architecture

This document outlines the architectural decisions and pipeline flow for the TerraPulse platform. The system is designed as a rigid, unidirectional pipeline composed of five distinct layers.

## 1. Storage & Ingestion Layer
- **Storage**: PostgreSQL with PostGIS for relational storage and geospatial operations (`ST_Contains` for point-in-polygon). SQLAlchemy handles the data access layer.
- **Schema-First Validation**: All data fetched from external sources must pass strictly typed Pydantic validation schemas.
- **Dead Letter Queue (DLQ)**: Any record failing validation or database insertion is serialized as JSON and stored in `data/dead_letter/`. The pipeline never crashes due to a bad record.
- **Idempotency**: Connectors run synchronously, performing upserts based on natural composite keys.
- **Property Price Register (PPR) Ingestion & Scheduling**: The official PSRA site is built on IBM Domino and utilizes F5 Application Security Manager (TSPD) bot challenges. Submitting the search form via a simple POST request fails due to these challenges, and automating a headless browser reveals that the search results page doesn't even contain a direct CSV export button. Instead, the `PPRConnector` relies on a direct "DOWNLOAD ALL" endpoint (`PPR-ALL.zip`) which bypasses the form submission entirely. A background `APScheduler` job (`scheduled_refresh.py`) periodically runs all connectors, exports a maintained master dataset (`data/exports/ppr_dublin_master.csv`), logs runs to the `ingestion_runs` table, and automatically invalidates Redis scores to ensure fresh data propagation.
## 2. Agents Layer (Unstructured Data)
- **Sequential Pipeline**: Processes unstructured text via a 3-step pipeline (Extract -> Score -> Fuse). 
- **Open-Source Provider Migration**: We migrated the LLM client from Anthropic to an OpenAI-compatible SDK (defaulting to OpenRouter/Groq with `meta-llama/llama-3-8b-instruct:free`). This removes proprietary lock-in, avoids paid API key dependencies for evaluators, and ensures the pipeline can run freely or self-hosted in the future.
- **Strict Typed Contracts**: Each LLM step is forced to output JSON matching Pydantic schemas (enhanced by `response_format={"type": "json_object"}`). 
- **Review Gate Rule (CRITICAL)**: The final Fuse step uses hardcoded logic to compare the agent's qualitative livability signal against structured metrics. Disagreements automatically flag the summary for human review by setting `needs_human_review = True`. 

## 3. Models Layer
- **Sequential Evaluation**: Machine learning models (Price Prediction using LightGBM) and rule-based models (Affordability, Safety, Livability) are versioned and stored in `models_layer/registry/models`.
- **Promotion Rule**: A model is only promoted to active (`is_active=True`) if it strictly outperforms the current active model in its specific metric.
- **Scoring Formulas**:
  - **Affordability**: `Score = max(0, 100 - (Price / 10000) * 0.6 - (Deprivation * 10) * 0.4)`
  - **Safety**: `Score = max(0, 100 - (Crime / Population * 1000) * 2)`

## 4. Backend Layer (FastAPI)
- **API Interface**: A strict REST API serves area data, price predictions (`POST /v1/predict/price`), and structured area scores (`GET /v1/areas/{id}/score`).
- **Review Gate Passthrough (CRITICAL)**: The `/v1/areas/{id}/score` endpoint preserves the `needs_human_review` boolean from Phase 2. It must never silently average a flagged signal into a clean score.
- **Stateless Inference**: Endpoints run fast inference on-request by querying active models directly from the file registry, caching score outputs in Redis for fast map rendering.

## 5. Frontend Layer (React & Leaflet)
- **Map View Architecture**: Powered by React, Vite, TailwindCSS, and `react-leaflet`. `MapPage.tsx` manages the state for active overlays and the selected area detail side-panel.
- **Choropleth Visualisation**: Generic `ScoreLayer.tsx` dynamically colors GeoJSON polygons fetched from PostGIS based on one of four scores: Price, Affordability, Safety, or Livability.
- **Review Flag UI Rule (CRITICAL)**: To fulfill the contract from Phase 2/3, any area where `needs_human_review = True` receives an unmissable visual warning marker both on the map directly (`AreaMarker.tsx`) and within the side panel (`ReviewFlagBanner.tsx`), explicitly stating that qualitative data disagrees with hard metrics.
