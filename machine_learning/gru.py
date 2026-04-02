from utils.parse_data import parse_scats_data, create_training_data_for_all_sites, normalize_data
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
import time

SCATS_DATA_PATH = "data/scats_data_october_2006.xls"


def gru(path):
    print("\n========== GRU MODEL ==========")

    # Load and prepare data
    series = parse_scats_data(path)
    scaled_series, scalers = normalize_data(series)
    X, y = create_training_data_for_all_sites(scaled_series)

    X = np.array(X)
    y = np.array(y)

    print(f"Original X shape: {X.shape}")
    print(f"Original y shape: {y.shape}")

    # Ensure correct shape for GRU: (samples, timesteps, features)
    if len(X.shape) == 2:
        X = X.reshape((X.shape[0], X.shape[1], 1))

    # Ensure y is 2D for inverse_transform later
    if len(y.shape) == 1:
        y = y.reshape(-1, 1)

    print(f"Reshaped X shape: {X.shape}")
    print(f"Reshaped y shape: {y.shape}")

    # Build model
    model = keras.Sequential([
        keras.Input(shape=(X.shape[1], X.shape[2])),
        layers.GRU(50),
        layers.Dense(1)
    ])

    # Compile model
    model.compile(
        optimizer="adam",
        loss="mse"
    )

    print("\nModel summary:")
    model.summary()

    # Train model
    start_time = time.time()

    history = model.fit(
        X,
        y,
        epochs=5,
        batch_size=32,
        validation_split=0.2,
        verbose=1
    )

    end_time = time.time()
    training_time = end_time - start_time

    # Predict on all data for evaluation
    pred_all = model.predict(X, verbose=0)

    # Keeping same scaler logic as your LSTM version for fair comparison
    pred_all_inv = scalers[970].inverse_transform(pred_all)
    y_all_inv = scalers[970].inverse_transform(y)

    # Metrics
    mae = mean_absolute_error(y_all_inv, pred_all_inv)
    mse = mean_squared_error(y_all_inv, pred_all_inv)
    rmse = np.sqrt(mse)

    # Final losses
    final_train_loss = history.history["loss"][-1]
    final_val_loss = history.history["val_loss"][-1]

    print("\n========== EVALUATION ==========")
    print(f"Final Train Loss: {final_train_loss:.6f}")
    print(f"Final Val Loss:   {final_val_loss:.6f}")
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

    # Return everything needed for later comparison
    results = {
        "model": "GRU",
        "train_loss": float(final_train_loss),
        "val_loss": float(final_val_loss),
        "mae": float(mae),
        "mse": float(mse),
        "rmse": float(rmse),
        "training_time_sec": float(training_time),
        "sample_predictions": sample_pred[:5].flatten().tolist(),
        "sample_actual": sample_actual[:5].flatten().tolist()
    }

    return model, results


if __name__ == "__main__":
    model, results = gru(SCATS_DATA_PATH)

    print("\n========== RESULTS DICTIONARY ==========")
    for key, value in results.items():
        print(f"{key}: {value}")