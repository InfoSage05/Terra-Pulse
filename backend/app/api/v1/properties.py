from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.db.session import get_db
from shared.model_contract import PropertyListing

router = APIRouter()

@router.get("/", response_model=List[PropertyListing])
def read_properties(
    area_id: Optional[int] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    property_type: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None, regex="^(price_asc|price_desc|recent)$"),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    from sqlalchemy import text

    where_clauses = ["1=1"]
    params: dict = {}

    if area_id is not None:
        where_clauses.append("ps.area_id = :area_id")
        params["area_id"] = area_id
    if min_price is not None:
        where_clauses.append("ps.price_eur >= :min_price")
        params["min_price"] = min_price
    if max_price is not None:
        where_clauses.append("ps.price_eur <= :max_price")
        params["max_price"] = max_price

    where_sql = " AND ".join(where_clauses)

    order_map = {
        "price_asc": "ps.price_eur ASC",
        "price_desc": "ps.price_eur DESC",
        "recent": "ps.sale_date DESC",
    }
    order_by = order_map.get(sort_by, "ps.sale_date DESC")

    base_query = f"""
        SELECT ps.id, ps.area_id, a.name as area_name, ps.address_raw, ps.price_eur,
               ps.sale_date, ps.lat, ps.lon
        FROM property_sales ps
        LEFT JOIN areas a ON a.id = ps.area_id
        WHERE {where_sql}
        ORDER BY {order_by}
        LIMIT :limit OFFSET :offset
    """
    params["limit"] = limit
    params["offset"] = offset

    rows = db.execute(text(base_query), params).fetchall()

    return [
        PropertyListing(
            id=row.id,
            area_id=row.area_id if row.area_id else 0,
            area_name=row.area_name if hasattr(row, 'area_name') and row.area_name else None,
            address_raw=row.address_raw or "",
            price_eur=float(row.price_eur) if row.price_eur else 0,
            sale_date=str(row.sale_date) if row.sale_date else "",
            property_type=None,
            lat=float(row.lat) if row.lat else None,
            lon=float(row.lon) if row.lon else None,
        )
        for row in rows
    ]
