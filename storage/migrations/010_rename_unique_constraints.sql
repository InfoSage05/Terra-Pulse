-- The connectors' upsert logic (ingestion/connectors/*.py) does
-- `ON CONFLICT ON CONSTRAINT <name>` against explicit constraint names
-- (uq_property_sales_date_address_price, uq_amenities_osmid_type,
-- uq_demographics_area_year, uq_crime_stats_area_div_year_cat), but the
-- original migrations (003/004/005/006) declared these as bare UNIQUE(...)
-- column constraints, so Postgres auto-generated its own default names
-- instead. Every upsert has therefore failed with "constraint ... does not
-- exist" since day one - rename to what the connector code expects.

ALTER TABLE property_sales
    RENAME CONSTRAINT property_sales_sale_date_address_raw_price_eur_key
    TO uq_property_sales_date_address_price;

ALTER TABLE amenities
    RENAME CONSTRAINT amenities_osm_id_amenity_type_key
    TO uq_amenities_osmid_type;

ALTER TABLE area_demographics
    RENAME CONSTRAINT area_demographics_area_id_year_key
    TO uq_demographics_area_year;

ALTER TABLE crime_stats
    RENAME CONSTRAINT crime_stats_area_id_garda_division_year_crime_category_key
    TO uq_crime_stats_area_div_year_cat;
