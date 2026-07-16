import json
import os
import pickle
from typing import Dict, Optional

from shared.model_contract import ModelMetadata, ModelType

REGISTRY_DIR = os.path.join(os.path.dirname(__file__), "models")
REGISTRY_INDEX = os.path.join(REGISTRY_DIR, "registry.json")

def _load_index() -> Dict[str, dict]:
    if not os.path.exists(REGISTRY_INDEX):
        return {}
    with open(REGISTRY_INDEX, "r") as f:
        return json.load(f)

def _save_index(index: Dict[str, dict]):
    os.makedirs(REGISTRY_DIR, exist_ok=True)
    with open(REGISTRY_INDEX, "w") as f:
        json.dump(index, f, indent=2)

def _registry_key(model_type, version: str) -> str:
    # Versions are second-precision timestamps generated independently by
    # each training script, so two different model_types can generate the
    # same version string if they finish training within the same second.
    # Keying purely by version would let one silently overwrite the other's
    # registry entry, so the key must include model_type too.
    type_str = model_type.value if hasattr(model_type, "value") else model_type
    return f"{type_str}:{version}"

def save_model(metadata: ModelMetadata, model_artifact: any = None) -> None:
    index = _load_index()

    if metadata.is_active:
        # Deactivate previous active model of this type
        for key, meta_dict in index.items():
            if meta_dict["model_type"] == metadata.model_type and meta_dict.get("is_active"):
                meta_dict["is_active"] = False

    index[_registry_key(metadata.model_type, metadata.version)] = metadata.model_dump(mode="json")
    _save_index(index)

    if model_artifact is not None:
        model_path = os.path.join(REGISTRY_DIR, f"{metadata.model_type}_{metadata.version}.pkl")
        with open(model_path, "wb") as f:
            pickle.dump(model_artifact, f)

def get_active_model_metadata(model_type: ModelType) -> Optional[ModelMetadata]:
    index = _load_index()
    for key, meta_dict in index.items():
        if meta_dict["model_type"] == model_type and meta_dict.get("is_active"):
            return ModelMetadata(**meta_dict)
    return None

def load_model_artifact(model_type: ModelType, version: str) -> any:
    model_path = os.path.join(REGISTRY_DIR, f"{model_type}_{version}.pkl")
    if not os.path.exists(model_path):
        return None
    with open(model_path, "rb") as f:
        return pickle.load(f)
