from shared.model_contract import ModelMetadata

from models_layer.registry.registry import get_active_model_metadata

def evaluate_and_promote(new_metadata: ModelMetadata) -> ModelMetadata:
    """
    Compares the new model against the active one.
    Updates `is_active` to True if it's better or if no active model exists.
    """
    active_meta = get_active_model_metadata(new_metadata.model_type)
    
    if not active_meta:
        print(f"[{new_metadata.model_type.value}] No active model found. Promoting new model to active.")
        new_metadata.is_active = True
        return new_metadata
        
    print(f"[{new_metadata.model_type.value}] Comparing new model (metric: {new_metadata.metric_value:.4f}) with active model (metric: {active_meta.metric_value:.4f})")
    
    # Lower is better for MAE/RMSE
    if "MAE" in new_metadata.metric_name or "RMSE" in new_metadata.metric_name:
        is_better = new_metadata.metric_value < active_meta.metric_value
    else:
        # Higher is better for accuracy or scores
        is_better = new_metadata.metric_value > active_meta.metric_value
        
    if is_better:
        print(f"[{new_metadata.model_type.value}] New model is better. Promoting to active.")
        new_metadata.is_active = True
    else:
        print(f"[{new_metadata.model_type.value}] WARNING: New model is worse. Not promoting. Retaining version: {active_meta.version}")
        new_metadata.is_active = False
        
    return new_metadata
