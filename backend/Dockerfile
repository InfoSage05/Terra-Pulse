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

# Run FastAPI via Uvicorn
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
