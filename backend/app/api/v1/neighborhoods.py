from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from backend.app.db.session import get_db
from sqlalchemy import text

router = APIRouter()

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
