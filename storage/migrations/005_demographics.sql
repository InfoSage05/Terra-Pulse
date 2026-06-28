CREATE TABLE IF NOT EXISTS area_demographics (
    id SERIAL PRIMARY KEY,
    area_id INTEGER REFERENCES areas(id),
    year INTEGER NOT NULL,
    population INTEGER,
    population_density DOUBLE PRECISION,
    deprivation_index DOUBLE PRECISION,
    age_profile_json JSONB,
    source_name VARCHAR(100) NOT NULL,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(area_id, year)
);

CREATE INDEX IF NOT EXISTS idx_demographics_area_id ON area_demographics(area_id);
