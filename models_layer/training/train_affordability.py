from datetime import datetime
from models_layer.feature_store.build_features import get_area_features
from shared.model_contract import ModelMetadata, ModelType
from models_layer.registry.registry import save_model
from models_layer.evaluation.evaluate import evaluate_and_promote

def compute_affordability_model():
    print("Computing affordability model (rule-based)...")
    df = get_area_features()
    
    valid_df = df[(df['avg_price'] > 0) & (df['deprivation_index'].notnull())].copy()
    if valid_df.empty:
        print("No valid data for affordability model.")
        return
        
    metric_value = len(valid_df) / len(df)
    
    version = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    
    metadata = ModelMetadata(
        model_type=ModelType.AFFORDABILITY_SCORE,
        version=version,
        trained_at=datetime.now(),
        training_row_count=len(valid_df),
        feature_names=['avg_price', 'deprivation_index'],
        metric_name="Coverage",
        metric_value=metric_value,
        is_active=False
    )
    
    metadata = evaluate_and_promote(metadata)
    save_model(metadata, None)

if __name__ == "__main__":
    compute_affordability_model()
