import json
import os
import pickle
import threading
from typing import Dict, Optional

from shared.model_contract import ModelMetadata, ModelType

REGISTRY_DIR = os.path.join(os.path.dirname(__file__), "models")
REGISTRY_INDEX = os.path.join(REGISTRY_DIR, "registry.json")

# In-process cache of unpickled model artifacts, keyed the same way as the
# registry index (f"{model_type}:{version}"). Avoids re-reading + re-unpickling
# the same bytes from disk on every /v1/predict/price request. Guarded by a
# lock because FastAPI runs sync route handlers in a threadpool, so concurrent
# requests can race on cache population - a plain dict without the lock could
# have two threads unpickle the same file simultaneously (wasteful but not
# unsafe) or, worse, interleave a read with the del/pop below during
# invalidation. The lock is only held for dict access, never for the pickle
# I/O itself's surrounding disk read of a *different* key, so contention is
# minimal.
_artifact_cache: Dict[str, any] = {}
_artifact_cache_lock = threading.Lock()

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
        # Deactivate previous active model of this type, and evict its
        # cached artifact - it can no longer be reached via
        # get_active_model_metadata() -> load_model_artifact(), so keeping
        # it cached would just leak memory over a long-running process.
        for key, meta_dict in index.items():
            if meta_dict["model_type"] == metadata.model_type and meta_dict.get("is_active"):
                meta_dict["is_active"] = False
                with _artifact_cache_lock:
                    _artifact_cache.pop(key, None)

    own_key = _registry_key(metadata.model_type, metadata.version)
    index[own_key] = metadata.model_dump(mode="json")
    _save_index(index)

    if model_artifact is not None:
        model_path = os.path.join(REGISTRY_DIR, f"{metadata.model_type}_{metadata.version}.pkl")
        with open(model_path, "wb") as f:
            pickle.dump(model_artifact, f)
        # Same (model_type, version) can legitimately be re-saved with a new
        # artifact (e.g. a training script re-run against the same-second
        # version string) - evict rather than serve the stale unpickled copy.
        with _artifact_cache_lock:
            _artifact_cache.pop(own_key, None)

def get_active_model_metadata(model_type: ModelType) -> Optional[ModelMetadata]:
    index = _load_index()
    for key, meta_dict in index.items():
        if meta_dict["model_type"] == model_type and meta_dict.get("is_active"):
            return ModelMetadata(**meta_dict)
    return None

def load_model_artifact(model_type: ModelType, version: str) -> any:
    cache_key = _registry_key(model_type, version)

    with _artifact_cache_lock:
        cached = _artifact_cache.get(cache_key)
    if cached is not None:
        return cached

    model_path = os.path.join(REGISTRY_DIR, f"{model_type}_{version}.pkl")
    if not os.path.exists(model_path):
        return None
    with open(model_path, "rb") as f:
        artifact = pickle.load(f)

    with _artifact_cache_lock:
        # Another thread may have populated this key while we were reading
        # from disk (see module-level comment) - last write wins, both
        # unpickled the same bytes so this is harmless.
        _artifact_cache[cache_key] = artifact
    return artifact
