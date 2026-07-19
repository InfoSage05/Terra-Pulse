from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from backend.app.db.session import get_db
from backend.app.services.area_service import get_areas, get_area_by_id, get_area_summaries

router = APIRouter()

@router.get("/", response_model=List[Dict[str, Any]])
async def read_areas(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await get_areas(db, limit=limit, offset=skip)

@router.get("/summary", response_model=List[Dict[str, Any]])
async def read_area_summaries(db: AsyncSession = Depends(get_db)):
    return await get_area_summaries(db)

@router.get("/{area_id}", response_model=Dict[str, Any])
async def read_area(area_id: int, db: AsyncSession = Depends(get_db)):
    area = await get_area_by_id(db, area_id)
    if area is None:
        raise HTTPException(status_code=404, detail="Area not found")
    return area
