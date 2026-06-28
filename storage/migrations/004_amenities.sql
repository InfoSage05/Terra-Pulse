CREATE TABLE IF NOT EXISTS amenities (
    id SERIAL PRIMARY KEY,
    area_id INTEGER REFERENCES areas(id),
    amenity_type VARCHAR(100) NOT NULL,
    name VARCHAR(255),
    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL,
    osm_id BIGINT,
    source_name VARCHAR(100) NOT NULL,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(osm_id, amenity_type)
);

CREATE INDEX IF NOT EXISTS idx_amenities_area_id ON amenities(area_id);
CREATE INDEX IF NOT EXISTS idx_amenities_type ON amenities(amenity_type);
