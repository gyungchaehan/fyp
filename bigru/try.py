from tensorflow.keras.models import load_model
import numpy as np

# Load your pretrained LSTM model
lstm_model = load_model('lstm_model.h5')

# # Generate LSTM features (assuming you have sequential data)
# lstm_features = lstm_model.predict("crude_oil_historical_data.csv")

print(lstm_model)