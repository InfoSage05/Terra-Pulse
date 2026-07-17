from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
from backend.app.db.session import get_db
import re

router = APIRouter()

def _extract_district_number(eircode_district: str) -> str | None:
    m = re.search(r'\bD(\d{1,2}[EW]?)\b', eircode_district or '')
    if not m:
        return None
    suffix = m.group(1).upper()
    return f"Dublin {suffix}"

@router.get("/", response_model=List[Dict[str, Any]])
def read_neighborhoods(
    sort_by: str = Query("median_sold_price", regex="^(median_sold_price|average_sold_price|avg_asking_price|locality)$"),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    order_map = {
        "median_sold_price": "median_sold_price DESC NULLS LAST",
        "average_sold_price": "average_sold_price DESC NULLS LAST",
        "avg_asking_price": "avg_asking_price DESC NULLS LAST",
        "locality": "locality ASC",
    }
    order_by = order_map.get(sort_by, "median_sold_price DESC NULLS LAST")

    rows = db.execute(text(f"""
        SELECT locality, eircode_district, median_sold_price, average_sold_price, avg_asking_price, data_source
        FROM neighborhood_data
        ORDER BY {order_by}
        LIMIT :limit
    """), {"limit": limit}).fetchall()

    return [dict(row._mapping) for row in rows]

@router.get("/featured", response_model=Dict[str, Any])
def read_featured_neighborhoods(
    limit: int = Query(8, le=20),
    db: Session = Depends(get_db),
):
    rows = db.execute(text("""
        SELECT locality, eircode_district, median_sold_price, average_sold_price, avg_asking_price, data_source
        FROM neighborhood_data
        WHERE median_sold_price IS NOT NULL
        ORDER BY locality
    """)).fetchall()

    hoods = []
    for row in rows:
        hood = dict(row._mapping)
        hood["ppr_avg_price"] = None
        hood["ppr_sales_count"] = None
        hood["ppr_latest_sale"] = None

        district_name = _extract_district_number(hood.get("eircode_district") or "")
        if district_name:
            ppr = db.execute(text("""
                SELECT ROUND(AVG(ps.price_eur))::int as avg_price,
                       COUNT(*) as sales_count,
                       MAX(ps.sale_date) as latest_sale
                FROM property_sales ps
                JOIN areas a ON a.id = ps.area_id
                WHERE a.name = :area_name AND ps.price_eur > 0
            """), {"area_name": district_name}).first()

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

    ppr_summary = db.execute(text("""
        SELECT COUNT(*) as total, MAX(sale_date) as latest, COUNT(*) FILTER (WHERE area_id IS NOT NULL) as linked
        FROM property_sales
    """)).first()

    return {
        "neighborhoods": hoods,
        "ppr_total_sales": ppr_summary.total,
        "ppr_linked_sales": ppr_summary.linked,
        "ppr_latest_sale": str(ppr_summary.latest) if ppr_summary.latest else None,
    }
