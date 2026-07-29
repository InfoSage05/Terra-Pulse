from datetime import datetime

import pytest

from models_layer.registry import registry
from shared.model_contract import ModelMetadata, ModelType


@pytest.fixture(autouse=True)
def isolated_registry(tmp_path, monkeypatch):
    """Point the registry at a throwaway directory and reset the
    in-process artifact cache so tests don't see each other's state or the
    real repo's models_layer/registry/models/registry.json."""
    monkeypatch.setattr(registry, "REGISTRY_DIR", str(tmp_path))
    monkeypatch.setattr(registry, "REGISTRY_INDEX", str(tmp_path / "registry.json"))
    registry._artifact_cache.clear()
    yield
    registry._artifact_cache.clear()


def _metadata(version: str, is_active: bool) -> ModelMetadata:
    return ModelMetadata(
        model_type=ModelType.PRICE_PREDICTION,
        version=version,
        trained_at=datetime.now(),
        training_row_count=10,
        feature_names=["x"],
        metric_name="MAE",
        metric_value=1.0,
        is_active=is_active,
    )


def test_load_model_artifact_is_cached_after_first_read(monkeypatch):
    registry.save_model(_metadata("v1", is_active=True), model_artifact={"weights": [1, 2, 3]})

    read_calls = []
    real_open = open

    def counting_open(path, mode="r", *args, **kwargs):
        if str(path).endswith(".pkl"):
            read_calls.append(path)
        return real_open(path, mode, *args, **kwargs)

    monkeypatch.setattr("builtins.open", counting_open)

    first = registry.load_model_artifact(ModelType.PRICE_PREDICTION, "v1")
    second = registry.load_model_artifact(ModelType.PRICE_PREDICTION, "v1")

    assert first == {"weights": [1, 2, 3]}
    assert second == {"weights": [1, 2, 3]}
    assert len(read_calls) == 1, "second load_model_artifact() call should hit the in-process cache, not disk"


def test_activating_new_version_evicts_previous_active_from_cache():
    registry.save_model(_metadata("v1", is_active=True), model_artifact={"v": 1})
    registry.load_model_artifact(ModelType.PRICE_PREDICTION, "v1")
    assert registry._registry_key(ModelType.PRICE_PREDICTION, "v1") in registry._artifact_cache

    registry.save_model(_metadata("v2", is_active=True), model_artifact={"v": 2})

    assert registry._registry_key(ModelType.PRICE_PREDICTION, "v1") not in registry._artifact_cache
    assert registry.get_active_model_metadata(ModelType.PRICE_PREDICTION).version == "v2"
    assert registry.load_model_artifact(ModelType.PRICE_PREDICTION, "v2") == {"v": 2}


def test_resaving_same_key_evicts_stale_cached_artifact():
    registry.save_model(_metadata("v1", is_active=False), model_artifact={"v": "stale"})
    assert registry.load_model_artifact(ModelType.PRICE_PREDICTION, "v1") == {"v": "stale"}

    registry.save_model(_metadata("v1", is_active=False), model_artifact={"v": "fresh"})

    assert registry.load_model_artifact(ModelType.PRICE_PREDICTION, "v1") == {"v": "fresh"}
