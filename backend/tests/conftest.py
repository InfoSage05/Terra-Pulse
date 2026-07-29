"""Shared pytest fixtures for backend integration tests.

Integration tests need a real Postgres+PostGIS instance - the same
`postgis/postgis:15-3.3` service CI spins up (see .github/workflows/ci.yml)
and `docker compose up -d postgres redis` provides locally, both reachable
on localhost. DATABASE_URL/REDIS_URL must be forced to localhost *before*
storage.scripts.db_connect (or backend.app.core.config.settings) is first
imported, since both cache their connection lazily on first use and the
repo's root .env points at the in-network "postgres"/"redis" hostnames
that only resolve inside the docker-compose network.
"""
import os

os.environ.setdefault("DATABASE_URL", "postgresql://terrapulse:password@localhost:5432/terrapulse")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

import pytest
from sqlalchemy import text

from storage.scripts.db_connect import get_engine, get_session_factory

import backend.app.db.session as backend_db_session


@pytest.fixture()
def db_session():
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(autouse=True)
def _reset_async_engine():
    """backend.app.db.session caches its asyncpg engine/pool at module
    scope, but asyncpg connections are bound to the event loop they were
    created on. pytest-asyncio (asyncio_mode=auto) gives each async test
    function its own event loop, so a cached engine from a prior test would
    error with "attached to a different loop" on the next one - force a
    fresh engine per test instead."""
    backend_db_session._engine = None
    backend_db_session._AsyncSessionLocal = None
    yield
    backend_db_session._engine = None
    backend_db_session._AsyncSessionLocal = None


@pytest.fixture()
async def async_db_session():
    async with backend_db_session.get_async_session_factory()() as session:
        yield session


@pytest.fixture()
def review_flagged_area(db_session):
    """Insert a minimal area + agent summary with needs_human_review=True,
    with enough supporting rows for the affordability/safety formulas to
    produce non-null scores, and clean up afterwards."""
    engine = get_engine()
    with engine.begin() as conn:
        area_id = conn.execute(
            text(
                "INSERT INTO areas (name, area_type, county, geometry) "
                "VALUES (:name, 'postal_district', 'Dublin', "
                "ST_GeomFromText('POLYGON((-6.30 53.34, -6.29 53.34, -6.29 53.35, -6.30 53.35, -6.30 53.34))', 4326)) "
                "RETURNING id"
            ),
            {"name": "__TestReviewGateArea__"},
        ).scalar()

        conn.execute(
            text(
                "INSERT INTO property_sales (area_id, address_raw, price_eur, sale_date, source_name) "
                "VALUES (:area_id, '1 Test Street', 350000, '2026-01-01', 'test_fixture')"
            ),
            {"area_id": area_id},
        )
        conn.execute(
            text(
                "INSERT INTO crime_stats (area_id, garda_division, year, crime_category, count, source_name) "
                "VALUES (:area_id, 'Test Division', 2026, 'Test Offence', 10, 'test_fixture')"
            ),
            {"area_id": area_id},
        )
        conn.execute(
            text(
                "INSERT INTO area_demographics (area_id, year, population, deprivation_index, source_name) "
                "VALUES (:area_id, 2026, 5000, 1.5, 'test_fixture')"
            ),
            {"area_id": area_id},
        )
        conn.execute(
            text(
                "INSERT INTO area_agent_summaries "
                "(area_id, run_id, livability_signal, confidence, needs_human_review, summary, source_count, model_name, ingested_at) "
                "VALUES (:area_id, gen_random_uuid(), -0.8, 0.9, TRUE, 'Qualitative signal disagrees with hard metrics.', 1, 'test_fixture', NOW())"
            ),
            {"area_id": area_id},
        )

    try:
        yield area_id
    finally:
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM area_agent_summaries WHERE area_id = :area_id"), {"area_id": area_id})
            conn.execute(text("DELETE FROM area_demographics WHERE area_id = :area_id"), {"area_id": area_id})
            conn.execute(text("DELETE FROM crime_stats WHERE area_id = :area_id"), {"area_id": area_id})
            conn.execute(text("DELETE FROM property_sales WHERE area_id = :area_id"), {"area_id": area_id})
            conn.execute(text("DELETE FROM areas WHERE id = :area_id"), {"area_id": area_id})
