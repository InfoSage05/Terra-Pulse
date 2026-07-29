from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from shared.model_contract import AreaScoreOutput
from backend.app.db.session import get_db
from backend.app.services.score_service import get_area_score

router = APIRouter()

@router.get("/{area_id}/score", response_model=AreaScoreOutput)
async def read_area_score(area_id: int, db: AsyncSession = Depends(get_db)):
    score = await get_area_score(db, area_id)
    if score is None:
        raise HTTPException(status_code=404, detail="Area not found")
    return score
