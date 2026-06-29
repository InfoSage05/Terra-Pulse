import pandas as pd
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from shared.model_contract import PricePredictionInput, PricePredictionOutput, ModelType
from models_layer.registry.registry import get_active_model_metadata, load_model_artifact

def predict_price(db: Session, input_data: PricePredictionInput) -> Optional[PricePredictionOutput]:
    meta = get_active_model_metadata(ModelType.PRICE_PREDICTION)
    if not meta:
        raise ValueError("No active price model available")
        
    model = load_model_artifact(ModelType.PRICE_PREDICTION, meta.version)
    if not model:
        raise ValueError("Active model artifact not found")
        
    # Get features for area
    query = text("""
        WITH amenity_agg AS (
            SELECT COUNT(id) as amenity_count FROM amenities WHERE area_id = :area_id
        ),
        crime_agg AS (
            SELECT SUM(count) as total_crime FROM crime_stats WHERE area_id = :area_id
        ),
        demo_latest AS (
            SELECT population, deprivation_index FROM area_demographics WHERE area_id = :area_id ORDER BY year DESC LIMIT 1
        )
        SELECT 
            COALESCE((SELECT amenity_count FROM amenity_agg), 0) as amenity_count,
            COALESCE((SELECT total_crime FROM crime_agg), 0) as total_crime,
            (SELECT population FROM demo_latest) as population,
            (SELECT deprivation_index FROM demo_latest) as deprivation_index
    """)
    
    row = db.execute(query, {"area_id": input_data.area_id}).first()
    if not row:
        return None # Area doesn't exist
        
    features = {
        'amenity_count': row.amenity_count or 0,
        'total_crime': row.total_crime or 0,
        'population': row.population or 0,
        'deprivation_index': row.deprivation_index or 0
    }
    
    X = pd.DataFrame([features])[meta.feature_names]
    
    predicted = float(model.predict(X)[0])
    
    # We use a static confidence interval for this iteration (e.g. +/- MAE)
    mae = meta.metric_value
    
    return PricePredictionOutput(
        area_id=input_data.area_id,
        predicted_price_eur=predicted,
        confidence_interval_low=predicted - mae,
        confidence_interval_high=predicted + mae,
        model_version=meta.version
    )
