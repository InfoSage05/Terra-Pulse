from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from backend.app.db.session import get_db
from backend.app.services.neighborhood_service import get_neighborhoods, get_featured_neighborhoods

router = APIRouter()

@router.get("/", response_model=List[Dict[str, Any]])
async def read_neighborhoods(
    sort_by: str = Query("median_sold_price", pattern="^(median_sold_price|average_sold_price|avg_asking_price|locality)$"),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
):
    return await get_neighborhoods(db, sort_by=sort_by, limit=limit)

@router.get("/featured", response_model=Dict[str, Any])
async def read_featured_neighborhoods(
    limit: int = Query(8, le=20),
    db: AsyncSession = Depends(get_db),
):
    return await get_featured_neighborhoods(db, limit=limit)
