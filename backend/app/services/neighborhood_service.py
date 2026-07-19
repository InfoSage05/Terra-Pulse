import json
import re
from typing import Any, Dict, List

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.cache import area_list_key, cache_get, cache_set, json_default
from backend.app.core.config import settings

_ORDER_MAP = {
    "median_sold_price": "median_sold_price DESC NULLS LAST",
    "average_sold_price": "average_sold_price DESC NULLS LAST",
    "avg_asking_price": "avg_asking_price DESC NULLS LAST",
    "locality": "locality ASC",
}


def _extract_district_number(eircode_district: str) -> str | None:
    m = re.search(r'\bD(\d{1,2}[EW]?)\b', eircode_district or '')
    if not m:
        return None
    suffix = m.group(1).upper()
    return f"Dublin {suffix}"


async def get_neighborhoods(db: AsyncSession, sort_by: str, limit: int) -> List[Dict[str, Any]]:
    cache_key = area_list_key(f"neighborhoods:{sort_by}:{limit}")
    cached = cache_get(cache_key)
    if cached is not None:
        return json.loads(cached)

    result = await _get_neighborhoods(db, sort_by, limit)
    cache_set(cache_key, json.dumps(result, default=json_default), ttl_seconds=settings.AREA_LIST_CACHE_TTL_SECONDS)
    return result


async def _get_neighborhoods(db: AsyncSession, sort_by: str, limit: int) -> List[Dict[str, Any]]:
    order_by = _ORDER_MAP.get(sort_by, _ORDER_MAP["median_sold_price"])

    rows = (await db.execute(text(f"""
        SELECT locality, eircode_district, median_sold_price, average_sold_price, avg_asking_price, data_source
        FROM neighborhood_data
        ORDER BY {order_by}
        LIMIT :limit
    """), {"limit": limit})).fetchall()

    return [dict(row._mapping) for row in rows]


async def get_featured_neighborhoods(db: AsyncSession, limit: int) -> Dict[str, Any]:
    cache_key = area_list_key(f"neighborhoods_featured:{limit}")
    cached = cache_get(cache_key)
    if cached is not None:
        return json.loads(cached)

    result = await _get_featured_neighborhoods(db, limit)
    cache_set(cache_key, json.dumps(result, default=json_default), ttl_seconds=settings.AREA_LIST_CACHE_TTL_SECONDS)
    return result


async def _get_featured_neighborhoods(db: AsyncSession, limit: int) -> Dict[str, Any]:
    rows = (await db.execute(text("""
        SELECT locality, eircode_district, median_sold_price, average_sold_price, avg_asking_price, data_source
        FROM neighborhood_data
        WHERE median_sold_price IS NOT NULL
        ORDER BY locality
    """))).fetchall()

    # Single aggregated PPR query instead of one query per row (previously
    # N+1-shaped: a per-neighborhood SELECT keyed on district_name inside
    # the loop below). All Dublin-postal-district PPR aggregates are fetched
    # once and joined in Python.
    ppr_rows = (await db.execute(text("""
        SELECT a.name as area_name,
               ROUND(AVG(ps.price_eur))::int as avg_price,
               COUNT(*) as sales_count,
               MAX(ps.sale_date) as latest_sale
        FROM property_sales ps
        JOIN areas a ON a.id = ps.area_id
        WHERE ps.price_eur > 0
        GROUP BY a.name
    """))).fetchall()
    ppr_by_area_name = {row.area_name: row for row in ppr_rows}

    hoods = []
    for row in rows:
        hood = dict(row._mapping)
        hood["ppr_avg_price"] = None
        hood["ppr_sales_count"] = None
        hood["ppr_latest_sale"] = None

        district_name = _extract_district_number(hood.get("eircode_district") or "")
        ppr = ppr_by_area_name.get(district_name) if district_name else None
        if ppr:
            hood["ppr_avg_price"] = ppr.avg_price
            hood["ppr_sales_count"] = ppr.sales_count
            hood["ppr_latest_sale"] = str(ppr.latest_sale) if ppr.latest_sale else None

        hoods.append(hood)

    hoods.sort(key=lambda h: h.get("ppr_sales_count") or 0, reverse=True)

    district_best = {}
    for h in hoods:
        district_name = _extract_district_number(h.get("eircode_district") or "")
        if not district_name:
            continue
        if district_name not in district_best:
            district_best[district_name] = h
        else:
            curr_best = district_best[district_name]
            curr_med = float(curr_best.get("median_sold_price") or 0)
            this_med = float(h.get("median_sold_price") or 0)
            if this_med > curr_med:
                district_best[district_name] = h

    sorted_hoods = sorted(district_best.values(), key=lambda h: h.get("ppr_sales_count") or 0, reverse=True)
    hoods = sorted_hoods[:limit]

    ppr_summary = (await db.execute(text("""
        SELECT COUNT(*) as total, MAX(sale_date) as latest, COUNT(*) FILTER (WHERE area_id IS NOT NULL) as linked
        FROM property_sales
    """))).first()

    return {
        "neighborhoods": hoods,
        "ppr_total_sales": ppr_summary.total,
        "ppr_linked_sales": ppr_summary.linked,
        "ppr_latest_sale": str(ppr_summary.latest) if ppr_summary.latest else None,
    }
