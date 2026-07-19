from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from shared.model_contract import PricePredictionInput, PricePredictionOutput
from backend.app.db.session import get_db
from backend.app.services.prediction_service import predict_price

router = APIRouter()

@router.post("/price", response_model=PricePredictionOutput)
async def create_price_prediction(input_data: PricePredictionInput, db: AsyncSession = Depends(get_db)):
    try:
        prediction = await predict_price(db, input_data)
        if prediction is None:
            raise HTTPException(status_code=404, detail="Area not found")
        return prediction
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
