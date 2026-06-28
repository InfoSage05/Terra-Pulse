# TerraPulse

An agentic AI platform for analyzing housing prices and neighborhood conditions.

## Data Ingestion & Storage Layer

This repository contains the foundation for TerraPulse, focusing specifically on the robust ETL pipeline and geospatial database storage.

### Prerequisites
- Docker & Docker Compose
- Python 3.11+

### Quickstart (Local Development)

1. **Spin up the database**
   ```bash
   docker-compose up -d
   ```

2. **Setup virtual environment**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   ```bash
   cp .env.example .env
   ```

5. **Run Database Migrations & Seeds**
   Use `psql` or your preferred tool to execute the SQL files in `storage/migrations/` sequentially against the `terrapulse` database.
   ```bash
   # Note: Depending on your psql setup
   psql -h localhost -U terrapulse -d terrapulse -f storage/migrations/001_init_postgis.sql
   # (repeat for 002 to 006)
   ```
   Run the area seeder:
   ```bash
   python storage/seeds/seed_areas.py
   ```
   Verify DB connection:
   ```bash
   python storage/scripts/db_connect.py
   ```

6. **Run Data Ingestion**
   Execute the ETL jobs. Rejected rows are automatically pushed to `data/dead_letter/`.
   ```bash
   # Run all connectors
   python ingestion/jobs/run_ingestion.py --source all
   
   # Run specific connectors
   python ingestion/jobs/run_ingestion.py --source ppr --source osm
   ```
