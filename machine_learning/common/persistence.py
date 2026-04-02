from pathlib import Path

import joblib

from machine_learning.common.config import (
    DEFAULT_TEST_RATIO,
    DEFAULT_VALIDATION_RATIO,
    DEFAULT_WINDOW_SIZE,
    SAVED_MODELS_DIR,
    SCATS_DATA_PATH,
    SEQUENCE_MODEL_TYPES,
    TABULAR_MODEL_TYPES,
)


def build_model_bundle(
    model,
    model_name,
    model_type,
    scalers,
    window_size=DEFAULT_WINDOW_SIZE,
    data_path=SCATS_DATA_PATH,
    test_ratio=DEFAULT_TEST_RATIO,
    validation_ratio=DEFAULT_VALIDATION_RATIO,
):
    return {
        "model": model,
        "model_name": model_name,
        "model_type": model_type,
        "scalers": scalers,
        "window_size": window_size,
        "data_path": data_path,
        "test_ratio": test_ratio,
        "validation_ratio": validation_ratio,
    }


def get_default_model_paths(model_type, base_dir=SAVED_MODELS_DIR):
    base_path = Path(base_dir)
    extension = ".keras" if model_type in SEQUENCE_MODEL_TYPES else ".pkl"
    model_path = base_path / f"{model_type}{extension}"
    metadata_path = base_path / f"{model_type}_metadata.pkl"
    return model_path, metadata_path


def save_model_bundle(model_bundle, model_path=None, metadata_path=None):
    model_type = model_bundle["model_type"]
    default_model_path, default_metadata_path = get_default_model_paths(model_type)
    model_path = Path(model_path) if model_path is not None else default_model_path
    metadata_path = Path(metadata_path) if metadata_path is not None else default_metadata_path

    model_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)

    model = model_bundle["model"]
    metadata = {key: value for key, value in model_bundle.items() if key != "model"}

    if model_type in SEQUENCE_MODEL_TYPES:
        model.save(model_path)
    elif model_type in TABULAR_MODEL_TYPES:
        joblib.dump(model, model_path)
    else:
        raise ValueError(f"Unsupported model type: {model_type}")

    joblib.dump(metadata, metadata_path)

    return {
        "model_path": str(model_path),
        "metadata_path": str(metadata_path),
    }


def load_model_bundle(model_type, model_path=None, metadata_path=None):
    default_model_path, default_metadata_path = get_default_model_paths(model_type)
    model_path = Path(model_path) if model_path is not None else default_model_path
    metadata_path = Path(metadata_path) if metadata_path is not None else default_metadata_path

    metadata = joblib.load(metadata_path)

    if metadata["model_type"] in SEQUENCE_MODEL_TYPES:
        from tensorflow import keras

        model = keras.models.load_model(model_path)
    elif metadata["model_type"] in TABULAR_MODEL_TYPES:
        model = joblib.load(model_path)
    else:
        raise ValueError(f"Unsupported model type: {metadata['model_type']}")

    metadata["model"] = model
    metadata["model_path"] = str(model_path)
    metadata["metadata_path"] = str(metadata_path)
    return metadata

