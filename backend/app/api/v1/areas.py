from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from backend.app.db.session import get_db
from backend.app.services.area_service import get_areas, get_area_by_id, get_area_summaries

router = APIRouter()

@router.get("/", response_model=List[Dict[str, Any]])
def read_areas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_areas(db, limit=limit, offset=skip)

@router.get("/summary", response_model=List[Dict[str, Any]])
def read_area_summaries(db: Session = Depends(get_db)):
    return get_area_summaries(db)

@router.get("/{area_id}", response_model=Dict[str, Any])
def read_area(area_id: int, db: Session = Depends(get_db)):
    area = get_area_by_id(db, area_id)
    if area is None:
        raise HTTPException(status_code=404, detail="Area not found")
    return area
