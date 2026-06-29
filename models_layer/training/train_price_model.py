import os
import pandas as pd
import numpy as np
import lightgbm as lgb
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

from models_layer.feature_store.build_features import get_area_features
from shared.model_contract import ModelMetadata, ModelType
from models_layer.registry.registry import save_model
from models_layer.evaluation.evaluate import evaluate_and_promote

def train_price_model():
    print("Training price prediction model...")
    df = get_area_features()
    
    # We want to predict avg_price, so we need areas with sales data
    df_train = df[df['sales_count'] > 0].copy()
    
    if df_train.empty:
        print("No training data available for price model.")
        return
        
    features = ['amenity_count', 'total_crime', 'population', 'deprivation_index']
    
    # Fill missing values for features
    for col in features:
        if df_train[col].isnull().all():
            df_train[col] = 0
        else:
            df_train[col] = df_train[col].fillna(df_train[col].median())
    
    X = df_train[features]
    y = df_train['avg_price']
    
    if len(df_train) < 5:
        X_train, X_test = X, X
        y_train, y_test = y, y
    else:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = lgb.LGBMRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    print(f"Price model trained. MAE: {mae:.2f}")
    
    version = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    
    metadata = ModelMetadata(
        model_type=ModelType.PRICE_PREDICTION,
        version=version,
        trained_at=datetime.now(),
        training_row_count=len(df_train),
        feature_names=features,
        metric_name="MAE",
        metric_value=mae,
        is_active=False
    )
    
    metadata = evaluate_and_promote(metadata)
    save_model(metadata, model)

if __name__ == "__main__":
    train_price_model()
