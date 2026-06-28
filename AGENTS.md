# AGENTS.md — TerraPulse

This file is the instruction set for the coding agent (GLM) working on this repository.
Read this fully before writing any code. Follow the scope boundaries exactly — do not
build layers that are explicitly marked out of scope for this phase.

---

## 1. Project overview

**TerraPulse** is an agentic AI platform for analysing housing prices and neighbourhood
conditions, starting with Dublin, Ireland, and designed from day one to extend to all
of Ireland without rework. It combines housing market data with urban and social-context
signals (crime, schools, transport, deprivation, amenities) and presents the results as
interactive overlays on a map. The long-term system has six layers: Ingestion, Storage,
Model Training, Agents, Backend (FastAPI), and Frontend (React + Maps).

**This phase covers ONLY two layers: Ingestion and Storage.** Do not scaffold or implement
the Model Training, Agents, Backend, or Frontend layers yet. You may create empty
placeholder directories for them (already present in the repo structure below) but write
no logic inside them. Stay inside `ingestion/` and `storage/` plus shared root-level config.

---

## 2. Scope for this task

Build:
1. A working **data ingestion layer** that pulls real data from the sources listed in
   Section 4, validates it against strict schemas, and writes clean output to disk and
   to the database.
2. A working **storage layer**: Postgres + PostGIS schema, migrations, and a thin data
   access layer (no ORM business logic beyond CRUD — keep it simple).

Do NOT build:
- ML models or training scripts
- Agent/LLM logic
- FastAPI endpoints
- Frontend code

The deliverable is: I can run one command, it pulls real Dublin data from at least 3 of
the sources below, validates it, and I can query it back out of Postgres with correct
area-level joins.

---

## 3. Design principles (non-negotiable)

- **Schema-first.** Every connector's output must be validated against a Pydantic model
  before it is allowed to reach storage. If validation fails, the record goes to a
  dead-letter log (a JSON file under `data/dead_letter/`), not into the database, and the
  pipeline does not crash.
- **Idempotent.** Re-running a connector on the same source data must not create
  duplicate rows. Use upserts keyed on a natural key (e.g. PPR: date + address + price;
  OSM: OSM element ID).
- **Source-traceable.** Every row in storage carries `source_name`, `source_url_or_id`,
  and `ingested_at`. We must always be able to say where a number came from.
- **Config over hardcoding.** Area boundaries, source URLs, and API keys live in config
  files / `.env`, never inline in code.
- **Built for scale beyond Dublin.** Tables and connectors must be designed so that adding
  Cork, Galway, Limerick etc. later is a config change (new area boundary + new source
  rows), not a schema change. Do not hardcode "Dublin" into table or column names.
- **No silent failures.** Every connector run produces a summary log: records fetched,
  records validated, records rejected, records upserted.

---

## 4. Data sources for this phase

Implement connectors for these sources. Build in this priority order — stop and confirm
with me before moving past source 4 if time is short.

1. **Residential Property Price Register (PSRA)** — official source of all residential
   property sales in Ireland since 2010 (date, price, address).
   - Primary: https://www.propertypriceregister.ie/ (CSV download)
   - Note: raw PSRA CSVs are CP1252-encoded and the site's SSL config is known to be
     finicky — handle encoding explicitly, do not assume UTF-8.
   - Easier alternative for clean JSON: the community-run unofficial API wrapper at
     https://github.com/civictech-ie/price-register (hosted instance at
     priceregister.civictech.ie) — evaluate this first since it removes the encoding
     pain; fall back to raw CSV parsing if it doesn't cover what we need.
   - Dublin-specific subset is also listed on data.gov.ie:
     https://data.gov.ie/dataset/dublin-residential-property-price-register

2. **OpenStreetMap (Overpass API)** — schools, hospitals, GP surgeries, supermarkets,
   parks, police stations, public transport stops, by bounding box per area.
   - Overpass API endpoint: https://overpass-api.de/api/interpreter
   - Use `overpy` or raw Overpass QL queries. Tag reference: amenity=school,
     amenity=hospital, amenity=doctors, amenity=supermarket, leisure=park,
     amenity=police, highway=bus_stop, railway=stop (for Luas/DART).

3. **CSO (Central Statistics Office Ireland)** — population density, age profile,
   Pobal HP deprivation index (standard Irish deprivation measure), by Small Area.
   - Data portal: https://data.cso.ie/
   - Open data: https://www.cso.ie/en/statistics/

4. **Crime statistics** — recorded crime by Garda Division (not finer-grained than
   division — note this limitation in the connector's docstring and in storage, since
   it means crime data joins at a coarser area level than other metrics).
   - CSO Garda recorded crime statistics: https://data.cso.ie/ (search "recorded crime")

5. **Transport / commute data** (lower priority — implement only if time remains)
   - Dublin Bus / Luas / TFI open data portal: https://www.transportforireland.ie/
   - National Transport Authority GTFS feed: https://www.transportforireland.ie/transitData/PT_Data.html

For each connector, write the source URL, last-checked date, and any access
restrictions (rate limits, auth required) into a `SOURCES.md` file at the repo root,
since these links and terms can change.

---

## 5. Codebase structure (full project — build only the bolded parts now)

```
terrapulse/
├── AGENTS.md                  ← this file
├── SOURCES.md                 ← (create) data source registry with URLs + access notes
├── README.md                  ← (create) project overview + setup instructions
├── .env.example                ← (create) all required env vars, no real secrets
├── docker-compose.yml          ← (create) Postgres + PostGIS + Redis for local dev
├── pyproject.toml / requirements.txt
│
├── **ingestion/**              ← BUILD THIS
│   ├── connectors/
│   │   ├── base.py             # abstract base connector: fetch() -> validate() -> load()
│   │   ├── ppr_connector.py    # Property Price Register
│   │   ├── osm_connector.py    # OpenStreetMap / Overpass amenities
│   │   ├── cso_connector.py    # CSO demographics + deprivation index
│   │   └── crime_connector.py  # Garda crime stats
│   ├── schemas/
│   │   ├── property_sale.py    # Pydantic model for a validated property sale record
│   │   ├── amenity.py           # Pydantic model for an OSM amenity record
│   │   ├── area_demographics.py
│   │   └── crime_stat.py
│   ├── jobs/
│   │   └── run_ingestion.py     # CLI entrypoint: run one or all connectors
│   ├── utils/
│   │   ├── geocoding.py         # address/lat-lon -> area_id resolution
│   │   └── logging_config.py
│   └── tests/
│       └── test_<connector>.py  # at least one test per connector using sample fixtures
│
├── **storage/**                ← BUILD THIS
│   ├── migrations/              # SQL migration files, numbered sequentially
│   │   ├── 001_init_postgis.sql
│   │   ├── 002_areas.sql
│   │   ├── 003_property_sales.sql
│   │   ├── 004_amenities.sql
│   │   ├── 005_demographics.sql
│   │   └── 006_crime_stats.sql
│   ├── models/
│   │   └── db_models.py         # SQLAlchemy models matching the migrations
│   ├── seeds/
│   │   └── seed_areas.py        # seeds the `areas` table with Dublin postal
│   │                             #   districts / Garda divisions as initial boundaries
│   └── scripts/
│       └── db_connect.py        # connection pool + session helper, read from .env
│
├── models_layer/                ← DO NOT BUILD YET (placeholder only)
├── agents_layer/                ← DO NOT BUILD YET (placeholder only)
├── backend/                      ← DO NOT BUILD YET (placeholder only)
├── frontend/                     ← DO NOT BUILD YET (placeholder only)
├── infra/                        ← DO NOT BUILD YET (placeholder only)
│
├── data/
│   ├── raw/                     # untouched source pulls, partitioned by source + date
│   ├── processed/                # validated, cleaned output
│   └── dead_letter/               # records that failed schema validation
└── docs/
    └── architecture.md            # (create) short doc restating this layer's design
```

---

## 6. Storage layer requirements

- **Database**: Postgres with the PostGIS extension enabled (for area boundary geometry
  and lat/lon point storage). Run via Docker Compose for local dev.
- **Core tables** (design these to be area-agnostic, not Dublin-specific):
  - `areas` — id, name, area_type (e.g. "postal_district", "garda_division",
    "small_area"), county, geometry (PostGIS polygon), created_at
  - `property_sales` — id, area_id (FK), sale_date, price_eur, address_raw,
    address_normalized, lat, lon, source_name, source_record_id, ingested_at
  - `amenities` — id, area_id (FK), amenity_type, name, lat, lon, osm_id, ingested_at
  - `area_demographics` — id, area_id (FK), year, population, population_density,
    deprivation_index, age_profile_json, source_name, ingested_at
  - `crime_stats` — id, area_id (FK), garda_division, year, crime_category, count,
    source_name, ingested_at
- All tables get a `source_name`, and a timestamp column for traceability, per the
  design principles above.
- Write migrations as plain numbered `.sql` files (not framework-specific migration
  tooling) so they're transparent and reviewable — keep it simple for this phase.
- Provide one helper script that connects to the DB and runs a sanity query (e.g. row
  counts per table) so I can verify ingestion worked end-to-end.

---

## 7. What "done" looks like for this phase

- [ ] `docker-compose up` brings up Postgres+PostGIS cleanly
- [ ] Migrations run cleanly against a fresh database
- [ ] `areas` table is seeded with real Dublin postal districts (at minimum: Dublin 1
      through Dublin 24, plus a few named suburbs like Blackrock, Dún Laoghaire)
- [ ] At least the PPR connector and the OSM connector run end-to-end: fetch real data
      → validate → upsert into Postgres, with a console summary of records processed
- [ ] Re-running a connector does not duplicate rows
- [ ] Invalid records are visibly logged to `data/dead_letter/`, not silently dropped
- [ ] `SOURCES.md` and `docs/architecture.md` exist and are accurate
- [ ] A short `README.md` lets a stranger run the whole ingestion pipeline from a clean
      clone in under 10 minutes

---

## 8. Working agreement

- Ask me before making any architectural decision not already specified above (e.g.
  choice of HTTP client library, exact Overpass query structure).
- If a data source above is dead, paywalled, or rate-limited beyond practical use,
  stop and tell me — do not silently substitute a different source without confirming.
- Prefer boring, explicit code over clever abstractions. This is a 1-2 day build, not
  a long-term maintained open-source library — but it still has to be correct and
  schema-validated per Section 3.
- Commit in small, logical chunks (one connector per commit, schema + migration
  together, etc.) so progress is reviewable.
