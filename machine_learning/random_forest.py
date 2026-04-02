from utils.parse_data import parse_scats_data, create_training_data_for_all_sites, normalize_data
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.ensemble import RandomForestRegressor
import numpy as np
import time

SCATS_DATA_PATH = "data/scats_data_october_2006.xls"


def random_forest(path):
    print("\n========== RANDOM FOREST MODEL ==========")

    # Load and prepare data
    series = parse_scats_data(path)
    scaled_series, scalers = normalize_data(series)
    X, y = create_training_data_for_all_sites(scaled_series)

    X = np.array(X)
    y = np.array(y)

    print(f"Original X shape: {X.shape}")
    print(f"Original y shape: {y.shape}")

    # Random Forest expects 2D input: (samples, features)
    if len(X.shape) == 3:
        X = X.reshape((X.shape[0], X.shape[1] * X.shape[2]))

    # Flatten y to 1D for sklearn
    if len(y.shape) == 2:
        y = y.ravel()

    print(f"Reshaped X shape: {X.shape}")
    print(f"Reshaped y shape: {y.shape}")

    # Build model
    model = RandomForestRegressor(
        n_estimators=50,
        max_depth=None,
        random_state=42,
        n_jobs=-1
    )

    # Train model
    start_time = time.time()
    model.fit(X, y)
    end_time = time.time()
    training_time = end_time - start_time

    # Predict on all data for evaluation
    pred_all = model.predict(X)

    # Reshape for inverse_transform
    pred_all = pred_all.reshape(-1, 1)
    y = y.reshape(-1, 1)

    # Keeping same scaler logic as your LSTM/GRU for fair comparison
    pred_all_inv = scalers[970].inverse_transform(pred_all)
    y_all_inv = scalers[970].inverse_transform(y)

    # Metrics
    mae = mean_absolute_error(y_all_inv, pred_all_inv)
    mse = mean_squared_error(y_all_inv, pred_all_inv)
    rmse = np.sqrt(mse)

    print("\n========== EVALUATION ==========")
    print("Train Loss: N/A (not applicable for Random Forest)")
    print("Val Loss:   N/A (not applicable for Random Forest)")
    print(f"MAE:              {mae:.4f}")
    print(f"MSE:              {mse:.4f}")
    print(f"RMSE:             {rmse:.4f}")
    print(f"Training Time:    {training_time:.2f} seconds")

    # Show first 5 predictions
    print("\n========== SAMPLE PREDICTIONS (FIRST 5) ==========")
    sample_pred = pred_all_inv[:5]
    sample_actual = y_all_inv[:5]

    for i in range(5):
        print(
            f"Sample {i+1}: Predicted = {sample_pred[i][0]:.2f}, "
            f"Actual = {sample_actual[i][0]:.2f}"
        )

    results = {
        "model": "Random Forest",
        "train_loss": None,
        "val_loss": None,
        "mae": float(mae),
        "mse": float(mse),
        "rmse": float(rmse),
        "training_time_sec": float(training_time),
        "sample_predictions": sample_pred[:5].flatten().tolist(),
        "sample_actual": sample_actual[:5].flatten().tolist()
    }

    return model, results


if __name__ == "__main__":
    model, results = random_forest(SCATS_DATA_PATH)

    print("\n========== RESULTS DICTIONARY ==========")
    for key, value in results.items():
        print(f"{key}: {value}")