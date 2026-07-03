from fastapi import APIRouter, Depends, HTTPException, Query
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
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Paginated property listings feed for the Zillow-style search UI."""
    from sqlalchemy import text

    base_query = "SELECT id, area_id, address_raw, price_eur, sale_date, lat, lon FROM property_sales WHERE 1=1"
    params: dict = {}

    if area_id is not None:
        base_query += " AND area_id = :area_id"
        params["area_id"] = area_id
    if min_price is not None:
        base_query += " AND price_eur >= :min_price"
        params["min_price"] = min_price
    if max_price is not None:
        base_query += " AND price_eur <= :max_price"
        params["max_price"] = max_price

    base_query += " ORDER BY sale_date DESC LIMIT :limit OFFSET :offset"
    params["limit"] = limit
    params["offset"] = offset

    rows = db.execute(text(base_query), params).fetchall()

    return [
        PropertyListing(
            id=row.id,
            area_id=row.area_id if row.area_id else 0,
            address_raw=row.address_raw or "",
            price_eur=float(row.price_eur) if row.price_eur else 0,
            sale_date=str(row.sale_date) if row.sale_date else "",
            property_type=None,
            lat=float(row.lat) if row.lat else None,
            lon=float(row.lon) if row.lon else None,
        )
        for row in rows
    ]
