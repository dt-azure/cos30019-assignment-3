import numpy as np
import pandas as pd


def predict_traffic(model, recent_values, scaler, model_type, window_size=4):
    scaled_window = prepare_recent_values(recent_values, scaler, window_size)
    feature_names = getattr(model, "feature_name_", None) if model_type == "lightgbm" else None
    model_input = reshape_prediction_input(scaled_window, model_type, feature_names=feature_names)

    if model_type in {"lstm", "gru"}:
        prediction = model.predict(model_input, verbose=0)
    elif model_type == "lightgbm":
        prediction = model.predict(model_input)
    else:
        raise ValueError(f"Unsupported model type: {model_type}")

    prediction = np.asarray(prediction).reshape(-1, 1)
    return float(scaler.inverse_transform(prediction)[0, 0])


def predict_lstm(model, recent_values, scaler, window_size=4):
    return predict_traffic(model, recent_values, scaler, "lstm", window_size)


def predict_gru(model, recent_values, scaler, window_size=4):
    return predict_traffic(model, recent_values, scaler, "gru", window_size)


def predict_lightgbm(model, recent_values, scaler, window_size=4):
    return predict_traffic(model, recent_values, scaler, "lightgbm", window_size)


def predict_from_bundle(model_bundle, recent_values, site_id=None, scaler=None):
    selected_scaler = scaler

    if selected_scaler is None:
        if site_id is None:
            raise ValueError("Provide either a scaler or a site_id for prediction.")
        selected_scaler = model_bundle["scalers"][site_id]

    return predict_traffic(
        model=model_bundle["model"],
        recent_values=recent_values,
        scaler=selected_scaler,
        model_type=model_bundle["model_type"],
        window_size=model_bundle["window_size"],
    )


def prepare_recent_values(recent_values, scaler, window_size):
    recent_values = np.asarray(recent_values, dtype=float).reshape(-1)

    if recent_values.size < window_size:
        raise ValueError(
            f"Need at least {window_size} recent values, got {recent_values.size}."
        )

    recent_window = recent_values[-window_size:].reshape(-1, 1)
    return scaler.transform(recent_window)


def reshape_prediction_input(scaled_window, model_type, feature_names=None):
    if model_type in {"lstm", "gru"}:
        return scaled_window.reshape(1, scaled_window.shape[0], 1)

    if model_type == "lightgbm":
        tabular_input = scaled_window.reshape(1, scaled_window.shape[0])
        if feature_names:
            return pd.DataFrame(tabular_input, columns=feature_names)
        return tabular_input

    raise ValueError(f"Unsupported model type: {model_type}")
