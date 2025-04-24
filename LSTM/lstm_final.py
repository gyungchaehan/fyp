import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional
from tensorflow.keras.models import Sequential
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# -------------------------------------------
# 1. Read CSV and Interpolate Missing Data
# -------------------------------------------
# Read the CSV file while parsing the 'Date' column as datetime.

data = pd.read_csv('updated_crude_oil.csv',parse_dates=['Date'])

# Set 'Date' as the index and sort by date.
data.set_index('Date', inplace=True)
data.sort_index(inplace=True)

# Reindex the DataFrame to cover every calendar day between the first and last date.
full_date_range = pd.date_range(start=data.index.min(), end=data.index.max(), freq='D')
data = data.reindex(full_date_range)

# Interpolate the missing values using time-based interpolation.
data_interpolated = data.interpolate(method='time')

# -------------------------------------------
# 2. Preprocess and Scale Data
# -------------------------------------------
# Select the relevant features.
features = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
data_features = data_interpolated[features]

# Scale the data using MinMaxScaler to scale values between 0 and 1.
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(data_features)

# -------------------------------------------
# 3. Create Sequences for the LSTM Model
# -------------------------------------------
# Define how many past days to use for prediction (sequence length)
sequence_length = 14

# For each sample, X contains the past 60 days of features,
# and y is the "Close" price of the next day (column index 3).
X = []
y = []
for i in range(sequence_length, len(scaled_data)):
    X.append(scaled_data[i-sequence_length:i, :])
    y.append(scaled_data[i, 3])
X = np.array(X)
y = np.array(y)

# -------------------------------------------
# 4. Split the Data into Training and Testing Sets
# -------------------------------------------
train_size = int(0.8 * len(X))
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]
print(X_train.shape)

# -------------------------------------------
# 5. Build the LSTM Model
# -------------------------------------------
model = Sequential()
# First LSTM layer with return_sequences=True to allow stacking.
model.add(Bidirectional(LSTM(units=50, return_sequences=True), input_shape=(X_train.shape[1], X_train.shape[2])))
model.add(Dropout(0.2))
# Second LSTM layer (no return_sequences needed).
model.add(LSTM(units=50, return_sequences=False))
model.add(Dropout(0.2))
# Dense layers to map to the final output.
model.add(Dense(units=25))
model.add(Dense(units=1))  # Output layer: predicts the "Close" price

# Compile the model using Mean Squared Error loss and the Adam optimizer.
model.build(input_shape=(X_train.shape[1], X_train.shape[2]))
model.compile(optimizer='adam', loss='mean_squared_error')
model.summary()

# -------------------------------------------
# 6. Train the Model
# -------------------------------------------
early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
history = model.fit(
    X_train,
    y_train,
    epochs=100,       # Adjust epochs as needed.
    batch_size=32,    # Adjust batch size if needed.
    validation_data=(X_test, y_test),
    callbacks=[early_stop]
)

model.save('lstm_model.h5')
print("Model saved as lstm_model.h5")

# -------------------------------------------
# 7. Make Predictions and Inverse Transform the Results
# -------------------------------------------
# Predict the test set.
predictions = model.predict(X_test)

# Since data was scaled across all features, create a dummy array to inverse transform the predictions.
predictions_extended = np.zeros((predictions.shape[0], len(features)))
predictions_extended[:, 3] = predictions[:, 0]  # Insert the predicted "Close" at index 3.
predicted_close_prices = scaler.inverse_transform(predictions_extended)[:, 3]

# Similarly inverse transform y_test.
y_test_extended = np.zeros((y_test.shape[0], len(features)))
y_test_extended[:, 3] = y_test
actual_close_prices = scaler.inverse_transform(y_test_extended)[:, 3]

print("Predicted Close Prices:")
print(predicted_close_prices)
print("Actual Close Prices:")
print(actual_close_prices)

# Calculate Regression Metrics.
mse = mean_squared_error(actual_close_prices, predicted_close_prices)
rmse = np.sqrt(mse)
mae = mean_absolute_error(actual_close_prices, predicted_close_prices)
r2 = r2_score(actual_close_prices, predicted_close_prices)
print("\nRegression Metrics:")
print("Mean Squared Error (MSE):", mse)
print("Root Mean Squared Error (RMSE):", rmse)
print("Mean Absolute Error (MAE):", mae)
print("R-squared (R²):", r2)

# -------------------------------------------
# 8. Generate Predictions for the Entire Dataset and Save to CSV
# -------------------------------------------
# Generate predictions for all sequences.
predictions_all = model.predict(X)

# Create the full feature set for inverse transformation.
predictions_all_extended = np.zeros((predictions_all.shape[0], len(features)))
predictions_all_extended[:, 3] = predictions_all[:, 0]
predicted_close_prices_all = scaler.inverse_transform(predictions_all_extended)[:, 3]

# Since predictions start from the index 'sequence_length', pad the first 'sequence_length' days with NaN.
all_predicted_close = np.concatenate([np.full((sequence_length,), np.nan), predicted_close_prices_all])

# Retrieve the corresponding dates. Note that after interpolation, the index is the full date range.
dates = data_interpolated.index
# Adjust dates to align with the predictions (all days in the full date range).
dates = dates[:len(all_predicted_close)]

# Create a DataFrame with dates and the predicted close prices.
predictions_df = pd.DataFrame({
    'Date': dates,
    'Predicted_Close': all_predicted_close
})

# Save the DataFrame to a CSV file.
predictions_df.to_csv('predicted_oil_prices_sq.csv', index=False)
print("Predicted prices for the entire dataset saved to predicted_oil_prices.csv")
