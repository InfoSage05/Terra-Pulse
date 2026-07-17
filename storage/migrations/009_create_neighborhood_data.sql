-- 009_create_neighborhood_data.sql
CREATE TABLE IF NOT EXISTS neighborhood_data (
    id SERIAL PRIMARY KEY,
    locality TEXT NOT NULL UNIQUE,
    eircode_district TEXT,
    median_sold_price NUMERIC,
    average_sold_price NUMERIC,
    sales_last_12_months INTEGER,
    latest_sale DATE,
    avg_asking_price NUMERIC,
    data_source TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
