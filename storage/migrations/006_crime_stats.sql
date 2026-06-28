CREATE TABLE IF NOT EXISTS crime_stats (
    id SERIAL PRIMARY KEY,
    area_id INTEGER REFERENCES areas(id),
    garda_division VARCHAR(255) NOT NULL,
    year INTEGER NOT NULL,
    crime_category VARCHAR(255) NOT NULL,
    count INTEGER NOT NULL,
    source_name VARCHAR(100) NOT NULL,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(area_id, garda_division, year, crime_category)
);

CREATE INDEX IF NOT EXISTS idx_crime_stats_area_id ON crime_stats(area_id);
