import time

from tensorflow import keras
from tensorflow.keras import layers

from machine_learning.common.config import (
    DEFAULT_TEST_RATIO,
    DEFAULT_VALIDATION_RATIO,
    DEFAULT_WINDOW_SIZE,
    SCATS_DATA_PATH,
)
from machine_learning.common.data_pipeline import load_and_split_data
from machine_learning.common.evaluation import build_results
from machine_learning.common.persistence import (
    build_model_bundle,
    get_default_model_paths,
    load_model_bundle,
    save_model_bundle,
)

MODEL_NAME = "GRU"
MODEL_TYPE = "gru"
DEFAULT_MODEL_PATH, DEFAULT_METADATA_PATH = get_default_model_paths(MODEL_TYPE)


def build_gru_model(input_shape):
    model = keras.Sequential(
        [
            keras.Input(shape=input_shape),
            layers.GRU(50),
            layers.Dense(1),
        ]
    )

    model.compile(optimizer="adam", loss="mse")
    return model


def train_gru(
    path=SCATS_DATA_PATH,
    window_size=DEFAULT_WINDOW_SIZE,
    test_ratio=DEFAULT_TEST_RATIO,
    validation_ratio=DEFAULT_VALIDATION_RATIO,
    epochs=5,
    batch_size=32,
    save=False,
    model_path=None,
    metadata_path=None,
):
    print("\n========== GRU MODEL ==========")

    data = load_and_split_data(
        path=path,
        window_size=window_size,
        test_ratio=test_ratio,
        validation_ratio=validation_ratio,
    )

    X_train = data["X_train"]
    y_train = data["y_train"]
    X_val = data["X_val"]
    y_val = data["y_val"]
    X_test = data["X_test"]
    y_test = data["y_test"]
    validation_data = (X_val, y_val) if len(X_val) else None

    print(f"Train X shape: {X_train.shape}")
    print(f"Val X shape:   {X_val.shape}")
    print(f"Test X shape:  {X_test.shape}")

    model = build_gru_model((X_train.shape[1], X_train.shape[2]))

    start_time = time.time()
    history = model.fit(
        X_train,
        y_train,
        validation_data=validation_data,
        epochs=epochs,
        batch_size=batch_size,
        verbose=1,
        # Keep sample order fixed because the windows come from time series data.
        shuffle=False,
    )
    training_time = time.time() - start_time

    predictions = model.predict(X_test, verbose=0)
    final_train_loss = history.history["loss"][-1]
    final_val_loss = history.history.get("val_loss", [None])[-1]

    results = build_results(
        model_name=MODEL_NAME,
        predictions=predictions,
        actual_values=y_test,
        test_site_ids=data["test_site_ids"],
        scalers=data["scalers"],
        training_time_sec=training_time,
        train_loss=final_train_loss,
        val_loss=final_val_loss,
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
        model_bundle.update(save_gru_model(model_bundle, model_path, metadata_path))

    return model_bundle, results


def gru(path=SCATS_DATA_PATH, **kwargs):
    return train_gru(path=path, **kwargs)


def save_gru_model(model_bundle, model_path=None, metadata_path=None):
    return save_model_bundle(
        model_bundle,
        model_path=model_path or DEFAULT_MODEL_PATH,
        metadata_path=metadata_path or DEFAULT_METADATA_PATH,
    )


def load_gru_model(model_path=None, metadata_path=None):
    return load_model_bundle(
        MODEL_TYPE,
        model_path=model_path or DEFAULT_MODEL_PATH,
        metadata_path=metadata_path or DEFAULT_METADATA_PATH,
    )


if __name__ == "__main__":
    model_bundle, results = train_gru(SCATS_DATA_PATH)

    print("\n========== RESULTS DICTIONARY ==========")
    for key, value in results.items():
        print(f"{key}: {value}")

    print("\nModel bundle keys:")
    print(sorted(model_bundle.keys()))
