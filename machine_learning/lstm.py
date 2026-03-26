from utils.parse_data import parse_scats_data, create_training_data_for_all_sites, normalize_data
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers

SCATS_DATA_PATH = "data/scats_data_october_2006.xls"

def lstm(path):
    series = parse_scats_data(path)
    scaled_series, scalers = normalize_data(series)
    X, y = create_training_data_for_all_sites(scaled_series)

    # Build model
    model = keras.Sequential([
        layers.LSTM(50, input_shape=(4, 1)),
        layers.Dense(1)
    ])

    # Compile model
    model.compile(
        optimizer='adam',
        loss='mse'
    )

    # Train model
    history = model.fit(
        X,
        y,
        epochs=10,
        batch_size=32,
        validation_split=0.2
    )

    predictions = model.predict(X[:5])

    # Inverse scaling (because MinMaxScaler was used)
    predictions = scalers[970].inverse_transform(predictions)
    actual = scalers[970].inverse_transform(y[:5])

    for i in range(5):
        print(f"Predicted: {predictions[i][0]:.2f}, Actual: {actual[i][0]:.2f}")

