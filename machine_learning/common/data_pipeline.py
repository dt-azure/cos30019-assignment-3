import numpy as np

from machine_learning.common.config import (
    DEFAULT_TEST_RATIO,
    DEFAULT_VALIDATION_RATIO,
    DEFAULT_WINDOW_SIZE,
    SCATS_DATA_PATH,
)
from utils.parse_data import create_training_data, normalize_data, parse_scats_data


def load_and_split_data(
    path=SCATS_DATA_PATH,
    window_size=DEFAULT_WINDOW_SIZE,
    test_ratio=DEFAULT_TEST_RATIO,
    validation_ratio=DEFAULT_VALIDATION_RATIO,
):
    series_by_site = parse_scats_data(path)
    scaled_series_by_site, scalers = normalize_data(series_by_site)

    train_features = []
    train_targets = []
    val_features = []
    val_targets = []
    test_features = []
    test_targets = []
    test_site_ids = []

    for site_id in sorted(scaled_series_by_site):
        site_series = scaled_series_by_site[site_id]
        split_data = split_site_series(
            site_series,
            window_size=window_size,
            test_ratio=test_ratio,
            validation_ratio=validation_ratio,
        )

        train_features.append(split_data["X_train"])
        train_targets.append(split_data["y_train"])
        val_features.append(split_data["X_val"])
        val_targets.append(split_data["y_val"])
        test_features.append(split_data["X_test"])
        test_targets.append(split_data["y_test"])
        test_site_ids.append(np.full(split_data["X_test"].shape[0], site_id))

    return {
        "X_train": np.concatenate(train_features, axis=0),
        "y_train": np.concatenate(train_targets, axis=0),
        "X_val": np.concatenate(val_features, axis=0),
        "y_val": np.concatenate(val_targets, axis=0),
        "X_test": np.concatenate(test_features, axis=0),
        "y_test": np.concatenate(test_targets, axis=0),
        "test_site_ids": np.concatenate(test_site_ids, axis=0),
        "scalers": scalers,
        "window_size": window_size,
        "test_ratio": test_ratio,
        "validation_ratio": validation_ratio,
        "data_path": path,
    }


def split_site_series(
    scaled_series,
    window_size=DEFAULT_WINDOW_SIZE,
    test_ratio=DEFAULT_TEST_RATIO,
    validation_ratio=DEFAULT_VALIDATION_RATIO,
):
    total_steps = len(scaled_series)
    minimum_steps = (window_size * 3) + 3

    if total_steps < minimum_steps:
        raise ValueError(
            f"Series is too short for train/validation/test split: "
            f"need at least {minimum_steps} steps, got {total_steps}."
        )

    # Hold out the latest samples for testing so evaluation stays chronological.
    test_start = _split_index(total_steps, test_ratio, window_size)

    train_val_series = scaled_series[:test_start]
    test_series = scaled_series[test_start - window_size:]

    if validation_ratio > 0:
        # Validation is carved from the tail of the training period for the same reason.
        val_start = _split_index(len(train_val_series), validation_ratio, window_size)
        train_series = train_val_series[:val_start]
        val_series = train_val_series[val_start - window_size:]
        X_val, y_val = create_training_data(val_series, window_size)
    else:
        train_series = train_val_series
        X_val = np.empty((0, window_size, scaled_series.shape[1]))
        y_val = np.empty((0, scaled_series.shape[1]))

    X_train, y_train = create_training_data(train_series, window_size)
    X_test, y_test = create_training_data(test_series, window_size)

    if len(X_train) == 0 or len(X_test) == 0:
        raise ValueError("Train/test split produced empty datasets.")

    return {
        "X_train": X_train,
        "y_train": y_train,
        "X_val": X_val,
        "y_val": y_val,
        "X_test": X_test,
        "y_test": y_test,
    }


def reshape_for_tabular_model(features):
    return features.reshape(features.shape[0], -1)


def reshape_targets_for_tabular_model(targets):
    return targets.reshape(-1)


def _split_index(total_steps, holdout_ratio, window_size):
    holdout_ratio = float(holdout_ratio)
    if not 0 < holdout_ratio < 1:
        raise ValueError("Split ratios must be between 0 and 1.")

    split_index = int(total_steps * (1 - holdout_ratio))
    split_index = max(split_index, window_size + 2)
    split_index = min(split_index, total_steps - 1)
    return split_index

