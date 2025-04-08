import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Bidirectional, GRU, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import matplotlib.pyplot as plt

# Load and preprocess data
def load_and_preprocess_data(filepath):
    # Load CSV file
    df = pd.read_csv(filepath)
    
    # Convert date column to datetime if exists
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
    
    # Fill missing values if any
    df = df.ffill().bfill()
    
    return df

# Prepare sequences for time series prediction
def create_sequences(data, input_length, output_length):
    X, y = [], []
    for i in range(len(data) - input_length - output_length + 1):
        X.append(data[i:i+input_length])
        y.append(data[i+input_length:i+input_length+output_length, -1])  # Only predict actual_oil_price
    
    return np.array(X), np.array(y)

# Build BiGRU model
def build_bigru_model(input_shape, output_length):
    model = Sequential([
        Bidirectional(GRU(128, return_sequences=True), input_shape=input_shape),
        Dropout(0.3),
        Bidirectional(GRU(64)),
        Dropout(0.3),
        Dense(64, activation='relu'),
        Dense(output_length)
    ])
    
    optimizer = Adam(learning_rate=0.001)
    model.compile(optimizer=optimizer, loss='mse', metrics=['mae'])
    
    return model

# Main function
def main():
    # Configuration
    DATA_PATH = 'oil_price_data.csv'  # Replace with your CSV file path
    INPUT_LENGTH = 30  # Number of past days to use for prediction
    OUTPUT_LENGTH = 7   # Number of future days to predict
    TEST_SIZE = 0.2
    RANDOM_STATE = 42
    BATCH_SIZE = 32
    EPOCHS = 100
    
    # Load and preprocess data
    df = load_and_preprocess_data(DATA_PATH)
    
    # Select relevant columns
    data = df[['sentiment_score', 'lstm_feature_score', 'actual_oil_price']].values
    
    # Normalize data
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data)
    
    # Create sequences
    X, y = create_sequences(data_scaled, INPUT_LENGTH, OUTPUT_LENGTH)
    
    # Split into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, shuffle=False
    )
    
    # Build model
    model = build_bigru_model((INPUT_LENGTH, X_train.shape[2]), OUTPUT_LENGTH)
    
    # Callbacks
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
        ModelCheckpoint('best_model.h5', save_best_only=True, monitor='val_loss')
    ]
    
    # Train model
    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=callbacks,
        verbose=1
    )
    
    # Evaluate model
    train_loss = model.evaluate(X_train, y_train, verbose=0)
    test_loss = model.evaluate(X_test, y_test, verbose=0)
    print(f"Train Loss: {train_loss[0]}, Train MAE: {train_loss[1]}")
    print(f"Test Loss: {test_loss[0]}, Test MAE: {test_loss[1]}")
    
    # Plot training history
    plt.figure(figsize=(12, 6))
    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title('Model Loss Progress')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend()
    plt.show()
    
    # Make predictions
    predictions = model.predict(X_test)
    
    # Inverse transform predictions and actual values
    # We need to create dummy arrays for inverse scaling
    dummy_array = np.zeros((len(predictions), data.shape[1]))
    dummy_array[:, -1] = predictions[:, 0]  # Assuming we're showing the first predicted day
    predictions_inv = scaler.inverse_transform(dummy_array)[:, -1]
    
    dummy_array[:, -1] = y_test[:, 0]
    y_test_inv = scaler.inverse_transform(dummy_array)[:, -1]
    
    # Plot predictions vs actual
    plt.figure(figsize=(14, 6))
    plt.plot(y_test_inv, label='Actual Prices')
    plt.plot(predictions_inv, label='Predicted Prices')
    plt.title('Oil Price Prediction')
    plt.ylabel('Price')
    plt.xlabel('Time Steps')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()
    