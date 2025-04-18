# lstm.py
import pandas as pd
import numpy as np
import os
from joblib import load
import tensorflow as tf
from datetime import datetime

class LSTMPredictor:
    def __init__(self):
        self.lstm_scaler = load('model/lstm_feature_scaler.joblib')
        self.sequence_length = 14  # Configurable sequence length
        self.actual_prices = None
        self.lstm_prices = None
        self.lstm_model = None
        self._load_lstm_model()

    def _load_lstm_model(self):
        """Load the LSTM model from file"""
        try:
            model_path = 'model/lstm_model.h5'
            if os.path.exists(model_path):
                self.lstm_model = tf.keras.models.load_model(model_path)
                print("LSTM model loaded successfully")
            else:
                raise FileNotFoundError(f"Model file not found at {model_path}")
        except Exception as e:
            print(f"Error loading LSTM model: {str(e)}")
            self.lstm_model = None
            raise

    def process_new_prices(self, new_data_path = "data_mock/real_time_oil_prices.csv", old_data_path = "data_mock/preprocessed_oil_prices.csv"):
        """
        Process new price data and prepare for LSTM prediction
        
        Args:
            new_data_path: Path to CSV file with new price data
            
        Returns:
            Processed DataFrame of actual prices
        """
        try:
            if not os.path.exists(new_data_path):
                raise FileNotFoundError(f"Input file not found: {new_data_path}")
                
            # Load and format new data
            real_time_filtered = pd.read_csv(new_data_path, skiprows=3, header=None)
            real_time_filtered.columns = ['Date', 'Close', 'High', 'Low', 'Open', 'Volume']
            real_time_filtered['Adj Close'] = real_time_filtered['Close']
            real_time_filtered = real_time_filtered[['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]

            # Try to load and merge with existing preprocessed data
            if os.path.exists(old_data_path):
                try:
                    preprocessed_data = pd.read_csv(old_data_path)
                    self.actual_prices = pd.concat([preprocessed_data, real_time_filtered], ignore_index=True)
                except Exception as e:
                    print(f"Warning: Error loading preprocessed data, using only new data. Error: {str(e)}")
                    self.actual_prices = real_time_filtered
            else:
                print("Warning: preprocessed_oil_prices.csv not found, using only new data")
                self.actual_prices = real_time_filtered
            
            return self.actual_prices
        
        except Exception as e:
            print(f"Error in process_new_prices: {str(e)}")
            raise 

    def predict_for_lstm(self):
        """
        Generate predictions using the LSTM model
        
        Returns:
            numpy array of predicted prices for the last 27 days
        """
        if self.actual_prices is None:
            raise ValueError("No price data available - run process_new_prices() first")
        if self.lstm_model is None:
            raise ValueError("LSTM model failed to load")

        features = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']  
        data = self.actual_prices.copy()
      
        # Prepare time series data
        if 'Date' in data.columns:
            data['Date'] = pd.to_datetime(data['Date'])
            data.set_index('Date', inplace=True)
        data.sort_index(inplace=True)

        # Handle missing dates and interpolate
        full_date_range = pd.date_range(start=data.index.min(), end=data.index.max(), freq='D')
        data = data.reindex(full_date_range)
        data_interpolated = data.interpolate(method='time')
        data_features = data_interpolated[features]
        
        # Scale features and prepare sequences
        scaled_data = self.lstm_scaler.transform(data_features)

        X = []
        y = []
        for i in range(self.sequence_length, len(scaled_data)):
            X.append(scaled_data[i-self.sequence_length:i, :])
            y.append(scaled_data[i, 3])
        X = np.array(X)
        y = np.array(y)
        
        # Generate predictions
        predictions = self.lstm_model.predict(X)
        predictions_extended = np.zeros((predictions.shape[0], len(features)))
        predictions_extended[:, 3] = predictions[:, 0]  # Insert predicted "Close" at index 3
        predicted_close_prices = self.lstm_scaler.inverse_transform(predictions_extended)[:, 3]
        
        # Store and return last 27 predictions
        self.lstm_prices = predicted_close_prices[-27:]
        return self.lstm_prices

    def run_lstm_pipeline(self, new_data_path = "data_mock/real_time_oil_prices.csv", old_data_path = "data_mock/preprocessed_oil_prices.csv"):
        """
        Complete LSTM prediction pipeline
        
        Args:
            new_data_path: Path to CSV file with new price data
            
        Returns:
            numpy array of predicted prices for the last 27 days
        """
        self.process_new_prices(new_data_path, old_data_path)
        self.predict_for_lstm()
        return self.lstm_prices