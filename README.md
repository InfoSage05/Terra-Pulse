# TerraPulse

TerraPulse is an agentic AI platform for analyzing housing prices and neighborhood conditions in Dublin (with architecture ready to expand across Ireland). It combines structured data (property sales, amenities, crime, demographics) with unstructured text (agent-driven qualitative summaries) to provide unified scores and price predictions for specific geographic areas.

## Architecture Overview

TerraPulse is built on a 5-layer pipeline:

1. **Ingestion & Storage**: Postgres + PostGIS database populated by robust Python ETL connectors.
2. **Agents Layer**: An LLM-powered pipeline that extracts qualitative summaries and flags contradictions (`needs_human_review`). It uses an OpenAI-compatible client configured for OpenRouter or Groq, with exponential backoff and JSON-mode structured parsing.
3. **Models Layer**: Offline generation of Price Predictions (LightGBM) and formula-based Affordability/Safety scores.
4. **Backend**: FastAPI providing typed endpoints for areas, scores, predictions, and property listings.
5. **Frontend**: A React + Vite + Google Maps application visualizing the data. The map view supports both area choropleth overlays and a Zillow-style property search/listings interface.

*For complete details, see [docs/architecture.md](docs/architecture.md).*

---

## Prerequisites

To run the **full stack**:

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) with Docker Compose
- A valid [Google Maps API Key](https://developers.google.com/maps/documentation/javascript/get-api-key) with the **Maps JavaScript API** enabled and billing attached
- An [OpenRouter API Key](https://openrouter.ai/) (only needed for running the agent pipeline; frontend/backend do not need it)

To run the **frontend alone** (mock data):

- [Node.js 20+](https://nodejs.org/)
- A Google Maps API Key

---

## Quick Start — Frontend Only (No Docker Required)

The frontend includes realistic mock data so you can explore the entire UI without a running backend or database.

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd terrapulse
   ```

2. **Configure the frontend environment**
   ```bash
   cp .env.example .env
   # Edit .env and set VITE_GOOGLE_MAPS_API_KEY=your_actual_key
   ```

3. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   ```

4. **Start the dev server**
   ```bash
   npm run dev
   ```

5. **Open the app**
   - Home page: http://localhost:5173
   - Search/map view: http://localhost:5173/search
   - Areas directory: http://localhost:5173/areas

> If Google Maps does not load, check that the Maps JavaScript API is enabled for your key, billing is active, and `localhost` is allowed in your key's HTTP referrer restrictions.

---

## Quick Start — Full Stack (Docker)

This runs Postgres + PostGIS, Redis, the FastAPI backend, and the Vite frontend together.

1. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and set:
   #   VITE_GOOGLE_MAPS_API_KEY=your_actual_key
   #   OPENROUTER_API_KEY=your_key   (only if running agents)
   ```

2. **Start the infrastructure**
   ```bash
   docker-compose up -d postgres redis
   docker compose ps
   ```
   Wait until `postgres` shows as `healthy`.

3. **Run migrations**
   ```bash
   for f in storage/migrations/*.sql; do
     docker-compose exec postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "/app/$f"
   done
   ```

4. **Seed area boundaries**
   ```bash
   docker-compose exec backend python storage/seeds/seed_areas.py
   ```

5. **Run ingestion**
   ```bash
   # At minimum, fetch real property sales
   docker-compose exec backend python ingestion/jobs/run_ingestion.py --source ppr
   ```

6. **Start the backend and frontend**
   ```bash
   docker-compose up -d backend frontend
   ```

7. **Access the app**
   - Frontend: http://localhost:5173
   - Backend API Docs: http://localhost:8000/docs

---

## Backend Development (Without Docker)

If you prefer running Python directly:

1. **Install Python dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Start Postgres + Redis**
   You must provide your own Postgres 15+ with PostGIS and Redis instances. Set `DATABASE_URL` and `REDIS_URL` in `.env`.

3. **Run migrations and seed**
   ```bash
   psql "$DATABASE_URL" -f storage/migrations/001_init_postgis.sql
   # ... repeat for 002 through 007
   python storage/seeds/seed_areas.py
   ```

4. **Run ingestion**
   ```bash
   python ingestion/jobs/run_ingestion.py --source ppr
   ```

5. **Start the backend**
   ```bash
   python -m uvicorn backend.app.main:app --reload --port 8000
   ```

---

## Running Tests

### Frontend tests
```bash
cd frontend
npm install
npx vitest run
```

### Backend tests
```bash
# With Docker
docker-compose exec backend pytest backend/tests/

# Without Docker (requires DATABASE_URL)
pytest backend/tests/
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in at least the required values:

| Variable | Required for | Description |
|----------|-------------|-------------|
| `DATABASE_URL` | Backend + ingestion | Postgres connection string |
| `POSTGRES_USER` | Docker | Postgres user |
| `POSTGRES_PASSWORD` | Docker | Postgres password |
| `POSTGRES_DB` | Docker | Postgres database name |
| `REDIS_URL` | Backend caching | Redis connection string |
| `VITE_GOOGLE_MAPS_API_KEY` | Frontend | Google Maps JavaScript API key |
| `VITE_API_BASE_URL` | Frontend | Base URL for backend API (default: `http://localhost:8000`) |
| `OPENROUTER_API_KEY` | Agent pipeline | OpenRouter key for LLM summarization |
| `MODEL_REGISTRY_PATH` | Backend prediction | Path to persisted model registry |

---

## Project Structure

```
terrapulse/
├── backend/             # FastAPI application
├── frontend/            # React + Vite + Google Maps
├── ingestion/           # ETL connectors (PPR, OSM, CSO, crime)
├── storage/             # Postgres migrations, SQLAlchemy models, seeds
├── agents_layer/        # LLM-driven area summarization
├── models_layer/        # LightGBM price prediction + scoring
├── shared/              # Pydantic contracts shared across layers
└── data/                # Raw/processed/dead-letter output
```

---

## Known Limitations

- **Coverage**: Data ingestion is currently bounded to Dublin, though the schema is designed for Ireland-wide expansion.
- **Crime Data Resolution**: Garda crime statistics are only available at the division level, not finer neighborhood granularity.
- **Agent Text Sources**: Unstructured agent summaries are limited to the text sources scraped during ingestion; the agent does not perform live web searches during inference.
- **Mock Data Mode**: The frontend can run with mock data when no backend is available, so some displayed numbers are illustrative rather than live.

---

## License

[Add your license here]
