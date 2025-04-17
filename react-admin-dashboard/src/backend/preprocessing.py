# preprocessing.py
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import pandas as pd
import numpy as np
import os
import json
import csv
from datetime import datetime, timedelta
from collections import defaultdict
# from tensorflow.keras.models import load_model
import tensorflow as tf



class DataPreprocessor:
    def __init__(self):
        self.lstm_scaler = MinMaxScaler(feature_range=(0, 1))
        self.bigru_feature_scaler = MinMaxScaler(feature_range=(-1,1))
        self.bigru_label_scaler = StandardScaler()
        self.sequence_length = 14  # You can make this configurable
        self.actual_prices = None
        self.vader_scores = None
        self.lstm_prices = None
        self.lstm_model = None
        self.bigru_dataset = None
        self.bigru_model = None
        self.final_prices = None
        self._load_lstm_model()
        self._load_bigru_model()
    
    def _load_lstm_model(self):
        try:
            model_path = 'model/lstm_model.h5'
            if os.path.exists(model_path):
                self.lstm_model = tf.keras.models.load_model(model_path)
                print("LSTM model loaded successfully")
            else:
                print(f"Warning: Model file not found at {model_path}")
        except Exception as e:
            print(f"Error loading LSTM model: {str(e)}")
            self.lstm_model = None

    def _load_bigru_model(self):
        try:
            model_path = 'model/bigru_model.h5'
            if os.path.exists(model_path):
                self.bigru_model = tf.keras.models.load_model(model_path)
                print("BiGRU model loaded successfully")
            else:
                print(f"Warning: Model file not found at {model_path}")
        except Exception as e:
            print(f"Error loading BiGRU model: {str(e)}")
            self.bigru_model = None

    def process_new_prices(self, new_data_path):
        try:
            if not os.path.exists(new_data_path):
                raise FileNotFoundError(f"Input file not found: {new_data_path}")
                
            real_time_filtered = pd.read_csv(new_data_path, skiprows=3, header=None)
            real_time_filtered.columns = ['Date', 'Close', 'High', 'Low', 'Open', 'Volume']
            real_time_filtered['Adj Close'] = real_time_filtered['Close']
            real_time_filtered = real_time_filtered[['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]

            # Try to load preprocessed data if exists
            if os.path.exists("data/preprocessed_oil_prices.csv"):
                try:
                    preprocessed_data = pd.read_csv("data/preprocessed_oil_prices.csv")
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

    def process_vader_scores(self, input_jsonl_path, preprocessed_path='data/preprocessed_vader_scores.csv'):
        # Step 1: Convert JSONL to temporary CSV
        temp_csv_path = 'temp_vader_scores.csv'
        with open(input_jsonl_path, 'r', encoding='utf-8') as jsonl_file, \
            open(temp_csv_path, 'w', newline='', encoding='utf-8') as csv_file:
            
            writer = csv.writer(csv_file)
            writer.writerow(['uuid', 'published_at', 'vader_score'])
            
            for line in jsonl_file:
                try:
                    data = json.loads(line.strip())
                    writer.writerow([
                        data.get('uuid'),
                        data.get('published_at'),
                        data.get('vader_score')
                    ])
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON line: {line[:50]}...")

        # Step 2: Remove duplicates
        df = pd.read_csv(temp_csv_path)
        df.drop_duplicates(subset=['uuid'], keep='first', inplace=True)
        unique_csv_path = 'unique_vader_scores.csv'
        df.to_csv(unique_csv_path, index=False)

        # Step 3: Process scores and handle existing data
        with open(unique_csv_path, 'r') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        
        # Date range setup from published_at
        df['published_at'] = pd.to_datetime(df['published_at'], errors='coerce')  # Convert to datetime
        start_date = df['published_at'].min()
        start_date = start_date.replace(tzinfo=None)  # Get the minimum date
        end_date = df['published_at'].max() 
        end_date = end_date.replace(tzinfo=None)   # Get the maximum date

        # Create a date range based on the start and end dates
        date_range = pd.date_range(start=start_date, end=end_date).to_list()
        # Initialize with existing data if available
        date_scores = defaultdict(list)
        existing_dates = set()

        if os.path.exists(preprocessed_path):
            with open(preprocessed_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        date = datetime.strptime(row['date'], '%Y-%m-%d')
                        existing_dates.add(date)
                        if row['avg_vader_score']:
                            date_scores[date].append(float(row['avg_vader_score']))
                    except (ValueError, KeyError):
                        continue
        

        # Process new data
        for row in data:
            try:
                date_str = row['published_at'][:10]
                date = datetime.strptime(date_str, '%Y-%m-%d')
                if row['vader_score']:
                    date_scores[date].append(float(row['vader_score']))
            except (ValueError, KeyError):
                continue
        
        # Calculate daily averages (combining existing and new data)
        results = []
        for date in date_range:
            date_str = date.strftime('%Y-%m-%d')
            if date in date_scores:
                # For dates with both existing and new data, we combine all scores
                avg_score = sum(date_scores[date]) / len(date_scores[date])
                results.append([date_str, round(avg_score, 4)])
            elif date in existing_dates:
                # For dates that only exist in preprocessed data (no new data)
                # We keep the original average score
                continue  # These will be added from the existing file
            else:
                results.append([date_str, 0.0])

        # Combine with existing data
        if os.path.exists(preprocessed_path):
            existing_df = pd.read_csv(preprocessed_path)
            new_df = pd.DataFrame(results, columns=['date', 'avg_vader_score'])
            
            # Merge and keep the combined averages where dates overlap
            combined_df = pd.concat([existing_df, new_df])
            combined_df['date'] = pd.to_datetime(combined_df['date'])
            combined_df = combined_df.groupby('date', as_index=False).mean()
            combined_df = combined_df.sort_values('date')
            combined_df['avg_vader_score'] = combined_df['avg_vader_score'].round(4)
            self.vader_scores = combined_df
        else:
            new_df = pd.DataFrame(results, columns=['date', 'avg_vader_score'])
            self.vader_scores = new_df
        
        os.remove(temp_csv_path)
        os.remove(unique_csv_path)
        return self.vader_scores

    def predict_for_lstm(self):
        features = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']  

        if self.actual_prices is None:
            raise ValueError("actual_prices has not been set")
            
        data = self.actual_prices.copy()
      
        if 'Date' in data.columns:
            data['Date'] = pd.to_datetime(data['Date'])
            data.set_index('Date', inplace=True)
        data.sort_index(inplace=True)

        full_date_range = pd.date_range(start=data.index.min(), end=data.index.max(), freq='D')
        data = data.reindex(full_date_range)
        data_interpolated = data.interpolate(method='time')
        data_features = data_interpolated[features]
        scaled_data = self.lstm_scaler.fit_transform(data_features)

        X = []
        y = []
        for i in range(self.sequence_length, len(scaled_data)):
            X.append(scaled_data[i-self.sequence_length:i, :])
            y.append(scaled_data[i, 3])
        X = np.array(X)
        y = np.array(y)
        
        print("reached")
        predictions = self.lstm_model.predict(X)
        predictions_extended = np.zeros((predictions.shape[0], len(features)))
        predictions_extended[:, 3] = predictions[:, 0]  # Insert the predicted "Close" at index 3.
        predicted_close_prices = self.lstm_scaler.inverse_transform(predictions_extended)[:, 3]
        # Get last 20
        self.lstm_prices = predicted_close_prices[-27:]
        return self.lstm_prices

    def make_bigru_dataset(self):
        # 1. Process and interpolate actual prices (last 20 days)
        data = self.actual_prices.copy()
        
        # Ensure Date is properly set as index
        if 'Date' in data.columns:
            data['Date'] = pd.to_datetime(data['Date'])
            data.set_index('Date', inplace=True)
        data.sort_index(inplace=True)

        # Handle missing dates
        full_date_range = pd.date_range(start=data.index.min(), end=data.index.max(), freq='D')
        data = data.reindex(full_date_range)
        data_interpolated = data.interpolate(method='time')[-27:]
        
        # 2. Prepare Vader scores (last 20 days)
        vader_scores = self.vader_scores[-27:].copy().rename(columns={'avg_vader_score': 'vader_score'})
        
        # 3. Prepare LSTM predictions (last 20 days)
        lstm_prices = pd.Series(self.lstm_prices, name='predicted_price')
        
        # 4. Combine all data - ensuring date alignment
        combined_df = pd.DataFrame({
            'vader_score': vader_scores['vader_score'].values,
            'predicted_price': lstm_prices.values,
            'actual_price': data_interpolated['Close'],
        })
        
        # Ensure correct column order
        combined_df = combined_df[['vader_score', 'predicted_price', 'actual_price']]
        self.bigru_dataset = combined_df
        print(self.bigru_dataset.shape)
        return self.bigru_dataset

    def predict_for_bigru(self):
        INPUT_LENGTH = 14
        OUTPUT_LENGTH = 1

        df = self.bigru_dataset.copy()
        df['predicted_price_change'] = df['predicted_price'].pct_change()
        df['predicted_moving_avg_3'] = df['predicted_price'].rolling(3).mean()
        df['predicted_moving_avg_7'] = df['predicted_price'].rolling(7).mean()
        df['predicted_volatility'] = df['predicted_price'].rolling(5).std()

        df['vader_diff'] = df['vader_score'].diff()
        df['vader_moving_avg'] = df['vader_score'].rolling(3).mean()
        df['vader_volatility'] = df['vader_score'].rolling(5).std()

        df['prediction_error'] = df['predicted_price'] - df['actual_price']
        
        df['actual_price_lag1'] = df['actual_price'].shift(1)
        df['actual_price_lag2'] = df['actual_price'].shift(2)

        df['vader_price_interaction'] = df['vader_score'] * df['predicted_price'].pct_change()
        # drop empty ones
        df = df.dropna()
        feature = df.drop(columns=['actual_price']).values.astype('float32')
        label = df[['actual_price']].values.astype('float32')
        feature_scaled = self.bigru_feature_scaler.fit_transform(feature)
        label_scaled = self.bigru_label_scaler.fit_transform(label)

        X, y = [], []

        for i in range(INPUT_LENGTH, len(feature_scaled) - OUTPUT_LENGTH + 1):
            X.append(feature_scaled[i - INPUT_LENGTH:i])
            y.append(label_scaled[i + OUTPUT_LENGTH - 1 : i + OUTPUT_LENGTH])

        X = np.array(X)
        y = np.array(y)
        predictions = self.bigru_model.predict(X)
        self.final_prices = self.bigru_label_scaler.inverse_transform(predictions)
        return self.final_prices

