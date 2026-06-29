from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from shared.model_contract import PricePredictionInput, PricePredictionOutput
from backend.app.db.session import get_db
from backend.app.services.prediction_service import predict_price

router = APIRouter()

@router.post("/price", response_model=PricePredictionOutput)
def create_price_prediction(input_data: PricePredictionInput, db: Session = Depends(get_db)):
    try:
        prediction = predict_price(db, input_data)
        if prediction is None:
            raise HTTPException(status_code=404, detail="Area not found")
        return prediction
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
