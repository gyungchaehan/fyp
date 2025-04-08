import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
import keras
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.models import Sequential
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import Bidirectional

from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Read the CSV file
data = pd.read_csv(r"C:\Users\akumarag\Desktop\crude_oil_historical_data.csv")

early_stop = EarlyStopping(monitor='val_loss',patience=10,restore_best_weights=True)
# Use relevant features: open, high, low, close, adj close, volume
# Here, we will drop the 'date' column for modeling purposes.
features = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
data_features = data[features]

# Scale the data using MinMaxScaler to scale values between 0 and 1.
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(data_features)

# 2. Create Sequences for the LSTM Model
# ---------------------------------------

# Define how many past days to use for prediction (sequence length)
sequence_length = 60

# Create the sequences:
# For each sample, X will be the past 60 days of features,
# and y will be the "close" price on the next day.
X = []
y = []
for i in range(sequence_length, len(scaled_data)):
    X.append(scaled_data[i-sequence_length:i, :])
    # The target is the "close" price, which is the 4th column (index 3) in our features list.
    y.append(scaled_data[i, 3])
X = np.array(X)
y = np.array(y)

# Split the data into training and testing sets (e.g., 80% train, 20% test)
train_size = int(0.8 * len(X))
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

# 3. Build the LSTM Model
# -----------------------

model = Sequential()

# First LSTM layer with return_sequences=True to stack another LSTM layer
model.add(Bidirectional(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2]))))
model.add(Dropout(0.2)) # Dropout for regularization

# Second LSTM layer; no need to return sequences here
model.add(LSTM(units=50, return_sequences=False))
model.add(Dropout(0.2))

# Dense layers to map to our final output
model.add(Dense(units=25))
model.add(Dense(units=1)) # Output layer: predicts the "close" price

# Compile the model using Mean Squared Error loss and the Adam optimizer
model.compile(optimizer='adam', loss='mean_squared_error')
model.summary()

# 4. Train the Model
# ------------------

history = model.fit(
X_train,
y_train,
epochs=100, # Adjust the number of epochs as needed
batch_size=32, # Adjust the batch size if needed
validation_data=(X_test, y_test),
callbacks=[early_stop]
)

model.save('lstm_model.h5')
print("Model saved as lstm_model.h5")

# 5. Make Predictions and Plot the Results
# -----------------------------------------

# Get the model's predictions for the test set
predictions = model.predict(X_test)

# Because we scaled all features together, we need to inverse transform the predictions for the "close" price.
# We'll create a dummy array with the same number of features, fill in the predictions at the "close" column index (3),
# then apply the inverse transform and extract the "close" column.

# Create an array of zeros for the full feature set for the predictions.
predictions_extended = np.zeros((predictions.shape[0], len(features)))
# Place the predicted "close" price in the correct column (index 3)
predictions_extended[:, 3] = predictions[:, 0]
# Inverse transform and extract the "close" price column
predicted_close_prices = scaler.inverse_transform(predictions_extended)[:, 3]

# Do the same for the actual y_test values
y_test_extended = np.zeros((y_test.shape[0], len(features)))
y_test_extended[:, 3] = y_test
actual_close_prices = scaler.inverse_transform(y_test_extended)[:, 3]

print("Predicted Close Prices:")
print(predicted_close_prices)

print("Actual Close Prices")
print(actual_close_prices)

# 6. Calculate Regression Metrics (Accuracy) # ------------------------------------------- 
mse = mean_squared_error(actual_close_prices, predicted_close_prices)
rmse = np.sqrt(mse)
mae = mean_absolute_error(actual_close_prices, predicted_close_prices)
r2 = r2_score(actual_close_prices, predicted_close_prices)
print("\nRegression Metrics:")
print("Mean Squared Error (MSE):", mse)
print("Root Mean Squared Error (RMSE):", rmse)
print("Mean Absolute Error (MAE):", mae)
print("R-squared (R²):", r2)
//
Regression Metrics:
Mean Squared Error (MSE): 2.030671081112444
Root Mean Squared Error (RMSE): 1.425016168719655
Mean Absolute Error (MAE): 1.1456676000949846
R-squared (R�): 0.9012305557908172
