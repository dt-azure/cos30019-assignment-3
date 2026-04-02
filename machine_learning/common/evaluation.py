import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error


def inverse_transform_by_site(values, site_ids, scalers):
    values = np.asarray(values).reshape(-1, 1)
    site_ids = np.asarray(site_ids)
    restored = np.empty_like(values, dtype=float)

    for site_id in np.unique(site_ids):
        site_mask = site_ids == site_id
        restored[site_mask] = scalers[site_id].inverse_transform(values[site_mask])

    return restored


def build_results(
    model_name,
    predictions,
    actual_values,
    test_site_ids,
    scalers,
    training_time_sec,
    train_loss=None,
    val_loss=None,
):
    predicted_original = inverse_transform_by_site(predictions, test_site_ids, scalers)
    actual_original = inverse_transform_by_site(actual_values, test_site_ids, scalers)

    mae = mean_absolute_error(actual_original, predicted_original)
    mse = mean_squared_error(actual_original, predicted_original)
    rmse = np.sqrt(mse)

    sample_predictions = predicted_original[:5].flatten().tolist()
    sample_actual = actual_original[:5].flatten().tolist()

    return {
        "model": model_name,
        "train_loss": None if train_loss is None else float(train_loss),
        "val_loss": None if val_loss is None else float(val_loss),
        "mae": float(mae),
        "mse": float(mse),
        "rmse": float(rmse),
        "training_time_sec": float(training_time_sec),
        "sample_predictions": sample_predictions,
        "sample_actual": sample_actual,
    }

