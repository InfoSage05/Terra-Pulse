CREATE TABLE IF NOT EXISTS property_sales (
    id SERIAL PRIMARY KEY,
    area_id INTEGER REFERENCES areas(id),
    sale_date DATE NOT NULL,
    price_eur NUMERIC(15, 2) NOT NULL,
    address_raw TEXT NOT NULL,
    address_normalized TEXT,
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    source_name VARCHAR(100) NOT NULL,
    source_record_id VARCHAR(255),
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(sale_date, address_raw, price_eur)
);

CREATE INDEX IF NOT EXISTS idx_property_sales_area_id ON property_sales(area_id);
CREATE INDEX IF NOT EXISTS idx_property_sales_sale_date ON property_sales(sale_date);
