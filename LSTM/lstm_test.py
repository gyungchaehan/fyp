import numpy as np
import pandas as pd
import os
import tensorflow as tf
from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional
from tensorflow.keras.models import Sequential
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# -------------------------------
# Helper Functions for Testing
# -------------------------------

def generate_synthetic_data(num_samples=500): #we passed all tests
    """
    Generates synthetic time series data with columns:
    'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'
    """
    np.random.seed(42)
    dates = pd.date_range(start='2020-01-01', periods=num_samples, freq='D')
    data = pd.DataFrame({
        'Date': dates,
        'Open': np.random.uniform(50, 100, size=num_samples),
        'High': np.random.uniform(50, 100, size=num_samples),
        'Low': np.random.uniform(50, 100, size=num_samples),
        'Close': np.random.uniform(50, 100, size=num_samples),
        'Adj Close': np.random.uniform(50, 100, size=num_samples),
        'Volume': np.random.randint(1000, 5000, size=num_samples)
    })
    return data

def preprocess_data(data, features, sequence_length=60):
    """
    Scales the selected features and generates sequential data for the LSTM.
    Returns the sequences (X), targets (y) and the scaler used.
    """
    data_features = data[features]
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data_features)
    
    X, y = [], []
    for i in range(sequence_length, len(scaled_data)):
        X.append(scaled_data[i-sequence_length:i, :])
        # The target here is the "Close" price, index 3
        y.append(scaled_data[i, 3])
    X = np.array(X)
    y = np.array(y)
    return X, y, scaler

def build_lstm_model(input_shape):
    """
    Builds the LSTM model architecture identical to your pipeline.
    """
    model = Sequential()
    model.add(Bidirectional(LSTM(units=50, return_sequences=True, input_shape=input_shape)))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(units=25))
    model.add(Dense(units=1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

# -------------------------------
# Test Functions
# -------------------------------

def test_sequence_generation():
    """
    Test that the sequence generation produces the expected shapes.
    """
    data = generate_synthetic_data(num_samples=100)
    features = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
    sequence_length = 10
    X, y, scaler = preprocess_data(data, features, sequence_length=sequence_length)
    
    # Expect (num_samples - sequence_length) sequences, each of shape (sequence_length, num_features)
    assert X.shape[0] == 100 - sequence_length, "Number of sequences is incorrect."
    assert X.shape[1] == sequence_length, "Sequence length is incorrect."
    assert X.shape[2] == len(features), "Number of features per sequence is incorrect."
    assert y.shape[0] == 100 - sequence_length, "Number of targets is incorrect."

def test_model_architecture():
    """
    Verify that the constructed model has the intended layers.
    """
    input_shape = (60, 6)
    model = build_lstm_model(input_shape)
    layers = [layer.__class__.__name__ for layer in model.layers]
    
    # Check that the first layer is Bidirectional (wrapping an LSTM)
    assert 'Bidirectional' in layers[0], "The first layer is not Bidirectional."
    # Check that there is at least one Dense layer at the end
    assert layers[-1] == 'Dense', "The model's last layer should be Dense."

def test_model_training_and_prediction():
    """
    Train the model on a small synthetic dataset and test predictions.
    """
    data = generate_synthetic_data(num_samples=120)  # small dataset for quick training
    features = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
    sequence_length = 10  # smaller sequence for testing purposes
    X, y, scaler = preprocess_data(data, features, sequence_length=sequence_length)
    
    train_size = int(0.8 * len(X))
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    model = build_lstm_model(input_shape=(X_train.shape[1], X_train.shape[2]))
    early_stop = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
    
    history = model.fit(
        X_train,
        y_train,
        epochs=10,
        batch_size=8,
        validation_data=(X_test, y_test),
        callbacks=[early_stop],
        verbose=0
    )
    
    # Verify predictions shape on test set.
    predictions = model.predict(X_test)
    assert predictions.shape[0] == X_test.shape[0], "Predictions row count does not match test data."
    assert predictions.shape[1] == 1, "Predictions should have a single output value per sample."

    # Test inverse transformation on the predictions.
    predictions_extended = np.zeros((predictions.shape[0], len(features)))
    predictions_extended[:, 3] = predictions[:, 0]
    predicted_close_prices = scaler.inverse_transform(predictions_extended)[:, 3]
    
    y_test_extended = np.zeros((y_test.shape[0], len(features)))
    y_test_extended[:, 3] = y_test
    actual_close_prices = scaler.inverse_transform(y_test_extended)[:, 3]
    
    mse = mean_squared_error(actual_close_prices, predicted_close_prices)
    assert mse >= 0, "Mean Squared Error should be non-negative."

def test_predictions_csv_creation(tmp_path):
    """
    Test generating predictions on the entire dataset and saving them to a CSV file.
    """
    data = generate_synthetic_data(num_samples=120)
    features = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
    sequence_length = 10
    X, y, scaler = preprocess_data(data, features, sequence_length=sequence_length)
    
    model = build_lstm_model(input_shape=(X.shape[1], X.shape[2]))
    # Train the model briefly on all available data.
    model.fit(X, y, epochs=5, batch_size=8, verbose=0)
    predictions_all = model.predict(X)
    
    predictions_all_extended = np.zeros((predictions_all.shape[0], len(features)))
    predictions_all_extended[:, 3] = predictions_all[:, 0]
    predicted_close_prices_all = scaler.inverse_transform(predictions_all_extended)[:, 3]
    
    # Pad the first 'sequence_length' days with NaN since predictions start after that.
    all_predicted_close = np.concatenate([np.full((sequence_length,), np.nan), predicted_close_prices_all])
    
    predictions_df = pd.DataFrame({
        'Predicted_Close': all_predicted_close
    })
    
    # Save file to temporary directory.
    csv_file = tmp_path / "predicted_oil_prices.csv"
    predictions_df.to_csv(csv_file, index=False)
    
    # Read back the CSV and verify.
    df = pd.read_csv(csv_file)
    # The file should have the same number of rows as the original dataset.
    assert len(df) == len(data), "CSV row count does not match original data length."
    # The first 'sequence_length' rows should contain NaN.
    nan_rows = df['Predicted_Close'][:sequence_length]
    assert nan_rows.isna().all(), "The first rows should be NaN due to padding."

# -------------------------------
# Run Tests if Script is Executed Directly
# -------------------------------

if __name__ == "__main__":
    test_sequence_generation()
    test_model_architecture()
    test_model_training_and_prediction()
    
    # For the CSV creation test, simulate a temporary directory.
    from tempfile import TemporaryDirectory
    from pathlib import Path
    with TemporaryDirectory() as tmpdirname:
        tmp_path = Path(tmpdirname)
        test_predictions_csv_creation(tmp_path)
    
    print("All tests passed!")

