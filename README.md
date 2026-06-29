# TerraPulse

TerraPulse is an agentic AI platform for analyzing housing prices and neighborhood conditions in Dublin (with architecture ready to expand across Ireland). It combines structured data (property sales, amenities, crime, demographics) with unstructured text (agent-driven qualitative summaries) to provide unified scores and price predictions for specific geographic areas.

## Architecture Overview

TerraPulse is built on a 5-layer pipeline:
1. **Ingestion & Storage**: Postgres + PostGIS database populated by robust Python ETL connectors.
2. **Agents Layer**: An LLM-powered pipeline that extracts qualitative summaries and flags contradictions (`needs_human_review`).
3. **Models Layer**: Offline/batch generation of Price Predictions (LightGBM) and formula-based Affordability/Safety scores.
4. **Backend**: FastAPI providing typed, read-only endpoints for the map.
5. **Frontend**: A React, Vite, and Leaflet (OpenStreetMap) application visualizing the data.

*For complete details, see [docs/architecture.md](docs/architecture.md).*

## Prerequisites

- **Docker & Docker Compose** (for running the stack locally)
- **Anthropic/OpenAI API Key** (for the Agent pipeline)

## Quickstart

Follow these exact steps to start the application from a clean clone.

1. **Configure Environment**
   Copy the example environment file and fill in your API keys:
   ```bash
   cp .env.example .env
   # Edit .env and set ANTHROPIC_API_KEY and VITE_GOOGLE_MAPS_KEY
   ```

2. **Start the Stack**
   Bring up Postgres (with PostGIS), Redis, the FastAPI Backend, and the Vite Frontend:
   ```bash
   docker-compose up -d --build
   ```

3. **Initialize the Database**
   Run the database migrations and seed the initial area boundaries:
   ```bash
   # Run migrations from inside the backend container (requires alembic configured)
   docker-compose exec backend sh -c "cd storage && alembic upgrade head"
   
   # Seed areas (Dublin boundaries)
   docker-compose exec backend python storage/seeds/seed_areas.py
   ```

4. **Run the Data Pipeline**
   Populate the database with data, run the agent summaries, and train the models:
   ```bash
   # 1. Run Data Ingestion
   docker-compose exec backend python ingestion/jobs/run_ingestion.py --source all
   
   # 2. Run Agent Pipeline
   docker-compose exec backend python agents_layer/jobs/run_agents.py
   
   # 3. Train & Evaluate Models
   docker-compose exec backend python models_layer/jobs/train_models.py
   ```

5. **Access the Application**
   - **Frontend Map**: http://localhost:5173
   - **Backend API Docs**: http://localhost:8000/docs

## Running Tests

Tests are integrated and can be run across the stack:

```bash
# Backend / Pipeline Tests
docker-compose exec backend pytest backend/tests/

# Frontend Tests
docker-compose exec frontend npx vitest run
```

## Known Limitations

- **Coverage**: Currently limited to Dublin area data. The schema supports expansion, but data ingestion is currently bounded to Dublin boundaries.
- **Crime Data Resolution**: Garda crime statistics are only available at the division level, not finer neighborhood granularity.
- **Agent Text Sources**: The unstructured agent summaries are strictly limited to whatever community text, news, and local forums were scraped during ingestion. The agent does not perform live web searches during inference.
