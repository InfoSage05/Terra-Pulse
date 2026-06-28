CREATE TABLE IF NOT EXISTS area_agent_summaries (
    id SERIAL PRIMARY KEY,
    area_id INTEGER REFERENCES areas(id),
    run_id UUID NOT NULL,
    summary TEXT NOT NULL,
    livability_signal FLOAT NOT NULL,
    confidence FLOAT NOT NULL,
    flags JSONB,
    needs_human_review BOOLEAN NOT NULL DEFAULT FALSE,
    structured_data_snapshot JSONB,
    source_count INTEGER NOT NULL,
    model_name TEXT NOT NULL,
    source_name TEXT NOT NULL DEFAULT 'agent_pipeline',
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_agent_summaries_area ON area_agent_summaries(area_id);
CREATE INDEX IF NOT EXISTS idx_agent_summaries_review ON area_agent_summaries(needs_human_review);
