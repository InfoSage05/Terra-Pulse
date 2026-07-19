import pytest

from backend.app.services.area_service import get_area_by_id, get_area_summaries, get_areas


async def test_get_areas_returns_seeded_rows(async_db_session):
    areas = await get_areas(async_db_session, limit=100, offset=0)
    assert isinstance(areas, list)
    assert len(areas) > 0
    assert {"id", "name", "area_type", "county", "geometry"} <= areas[0].keys()


async def test_get_areas_respects_limit(async_db_session):
    areas = await get_areas(async_db_session, limit=1, offset=0)
    assert len(areas) == 1


async def test_get_area_by_id_found(async_db_session, review_flagged_area):
    area = await get_area_by_id(async_db_session, review_flagged_area)
    assert area is not None
    assert area["id"] == review_flagged_area
    assert area["name"] == "__TestReviewGateArea__"
    assert "metrics" in area
    assert area["metrics"]["population"] == 5000


async def test_get_area_by_id_not_found(async_db_session):
    area = await get_area_by_id(async_db_session, area_id=-1)
    assert area is None


async def test_get_area_summaries_returns_rows(async_db_session):
    summaries = await get_area_summaries(async_db_session)
    assert isinstance(summaries, list)
    assert len(summaries) > 0
    assert {"id", "name", "avg_price", "property_count"} <= summaries[0].keys()
