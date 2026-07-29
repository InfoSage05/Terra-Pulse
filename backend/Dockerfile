FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwright (used by ingestion/connectors/ppr_connector.py to drive the
# PSRA download form past its bot-defense JS challenge) needs its own
# browser binary plus OS-level shared libs, neither of which pip installs.
RUN playwright install --with-deps chromium

# Copy source code (preserving module structure)
COPY backend/ ./backend/
COPY shared/ ./shared/
COPY storage/ ./storage/
COPY models_layer/ ./models_layer/
COPY agents_layer/ ./agents_layer/
COPY ingestion/ ./ingestion/

# Set PYTHONPATH so absolute imports work
ENV PYTHONPATH=/app

# Expose FastAPI port
EXPOSE 8000

# Apply any pending DB migrations, then run FastAPI via Uvicorn.
# run_migrations.py is idempotent (tracks applied files in schema_migrations),
# so it is safe to run on every container start.
CMD ["sh", "-c", "python storage/scripts/run_migrations.py && uvicorn backend.app.main:app --host 0.0.0.0 --port 8000"]
