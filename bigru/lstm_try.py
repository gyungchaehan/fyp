from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler

# Normalize oil prices
scaler = MinMaxScaler()
scaled_prices = scaler.fit_transform(combined[['Close']]) # CHANGE THIS TO THE DATASET

# Create sequences (X: 10 days of prices, y: next day's price)
SEQ_LENGTH = 10
X, y = [], []
for i in range(len(scaled_prices) - SEQ_LENGTH):
    X.append(scaled_prices[i:i+SEQ_LENGTH])
    y.append(scaled_prices[i+SEQ_LENGTH])
X, y = np.array(X), np.array(y)

# Train LSTM
model = Sequential([
    LSTM(64, return_sequences=False, input_shape=(SEQ_LENGTH, 1)),
    Dense(1)
])
model.compile(optimizer='adam', loss='mse')
model.fit(X, y, epochs=50, batch_size=32)

# Get LSTM predictions for ALL aligned dates (shifted by SEQ_LENGTH)
lstm_features = model.predict(X)  # Shape: (N - SEQ_LENGTH, 1)

# Pad with NaN for the first SEQ_LENGTH days (no predictions)
lstm_features_padded = np.vstack([
    np.full((SEQ_LENGTH, 1), np.nan),  # No predictions for first SEQ_LENGTH days
    lstm_features
])

# Add to DataFrame
combined['lstm_features'] = lstm_features_padded