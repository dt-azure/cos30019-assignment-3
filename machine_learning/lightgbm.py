import time

from lightgbm import LGBMRegressor
import pandas as pd

from machine_learning.common.config import (
    DEFAULT_TEST_RATIO,
    DEFAULT_VALIDATION_RATIO,
    DEFAULT_WINDOW_SIZE,
    SCATS_DATA_PATH,
)
from machine_learning.common.data_pipeline import (
    load_and_split_data,
    reshape_for_tabular_model,
    reshape_targets_for_tabular_model,
)
from machine_learning.common.evaluation import build_results
from machine_learning.common.persistence import (
    build_model_bundle,
    get_default_model_paths,
    load_model_bundle,
    save_model_bundle,
)

MODEL_NAME = "LightGBM"
MODEL_TYPE = "lightgbm"
DEFAULT_MODEL_PATH, DEFAULT_METADATA_PATH = get_default_model_paths(MODEL_TYPE)


def build_lightgbm_model():
    return LGBMRegressor(
        objective="regression",
        n_estimators=100,
        learning_rate=0.1,
        num_leaves=31,
        random_state=42,
        n_jobs=-1,
    )


def build_feature_frame(features, window_size):
    columns = [f"lag_{index + 1}" for index in range(window_size)]
    return pd.DataFrame(features, columns=columns)


def train_lightgbm(
    path=SCATS_DATA_PATH,
    window_size=DEFAULT_WINDOW_SIZE,
    test_ratio=DEFAULT_TEST_RATIO,
    validation_ratio=DEFAULT_VALIDATION_RATIO,
    epochs=None,
    batch_size=None,
    save=False,
    model_path=None,
    metadata_path=None,
):
    print("\n========== LIGHTGBM MODEL ==========")

    data = load_and_split_data(
        path=path,
        window_size=window_size,
        test_ratio=test_ratio,
        validation_ratio=validation_ratio,
    )

    X_train = build_feature_frame(
        reshape_for_tabular_model(data["X_train"]),
        window_size=window_size,
    )
    y_train = reshape_targets_for_tabular_model(data["y_train"])
    X_test = build_feature_frame(
        reshape_for_tabular_model(data["X_test"]),
        window_size=window_size,
    )
    y_test = data["y_test"]

    print(f"Train X shape: {X_train.shape}")
    print(f"Test X shape:  {X_test.shape}")

    model = build_lightgbm_model()

    start_time = time.time()
    model.fit(X_train, y_train)
    training_time = time.time() - start_time

    predictions = model.predict(X_test)

    results = build_results(
        model_name=MODEL_NAME,
        predictions=predictions,
        actual_values=y_test,
        test_site_ids=data["test_site_ids"],
        scalers=data["scalers"],
        training_time_sec=training_time,
        train_loss=None,
        val_loss=None,
    )

    model_bundle = build_model_bundle(
        model=model,
        model_name=MODEL_NAME,
        model_type=MODEL_TYPE,
        scalers=data["scalers"],
        window_size=window_size,
        data_path=path,
        test_ratio=test_ratio,
        validation_ratio=validation_ratio,
    )

    if save:
        model_bundle.update(save_lightgbm_model(model_bundle, model_path, metadata_path))

    return model_bundle, results


def lightgbm_model(path=SCATS_DATA_PATH, **kwargs):
    return train_lightgbm(path=path, **kwargs)


def save_lightgbm_model(model_bundle, model_path=None, metadata_path=None):
    return save_model_bundle(
        model_bundle,
        model_path=model_path or DEFAULT_MODEL_PATH,
        metadata_path=metadata_path or DEFAULT_METADATA_PATH,
    )


def load_lightgbm_model(model_path=None, metadata_path=None):
    return load_model_bundle(
        MODEL_TYPE,
        model_path=model_path or DEFAULT_MODEL_PATH,
        metadata_path=metadata_path or DEFAULT_METADATA_PATH,
    )


if __name__ == "__main__":
    model_bundle, results = train_lightgbm(SCATS_DATA_PATH)

    print("\n========== RESULTS DICTIONARY ==========")
    for key, value in results.items():
        print(f"{key}: {value}")

    print("\nModel bundle keys:")
    print(sorted(model_bundle.keys()))
