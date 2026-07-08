CREATE TABLE IF NOT EXISTS ingestion_runs (
    id SERIAL PRIMARY KEY,
    source_name VARCHAR(255) NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    finished_at TIMESTAMP WITH TIME ZONE,
    rows_fetched INTEGER DEFAULT 0,
    rows_upserted INTEGER DEFAULT 0,
    rows_dead_lettered INTEGER DEFAULT 0,
    status VARCHAR(50) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_ingestion_runs_source_name ON ingestion_runs(source_name);
CREATE INDEX IF NOT EXISTS idx_ingestion_runs_started_at ON ingestion_runs(started_at);
