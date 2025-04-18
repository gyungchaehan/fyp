# bigru.py
import pandas as pd
import numpy as np
import os
import json
import csv
from datetime import datetime, timedelta
from collections import defaultdict
from joblib import load
import tensorflow as tf
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, mean_absolute_percentage_error

class BiGRUPredictor:
    def __init__(self):
        self.bigru_feature_scaler = load('model/feature_scaler.joblib')
        self.bigru_label_scaler = load('model/label_scaler.joblib')
        self.sequence_length = 14  # Configurable sequence length
        self.vader_scores = None
        self.lstm_prices = None
        self.bigru_dataset = None
        self.final_prices = None
        self.bigru_model = None
        self._load_bigru_model()

    def _load_bigru_model(self):
        """Load the BiGRU model from file"""
        try:
            model_path = 'model/bigru_model.h5'
            if os.path.exists(model_path):
                self.bigru_model = tf.keras.models.load_model(model_path)
                print("BiGRU model loaded successfully")
            else:
                raise FileNotFoundError(f"Model file not found at {model_path}")
        except Exception as e:
            print(f"Error loading BiGRU model: {str(e)}")
            self.bigru_model = None
            raise

    def process_vader_scores(self, input_jsonl_path="data_mock/new_news_data.jsonl", preprocessed_path='data_mock/preprocessed_vader_scores.csv'):
        """
        Process Vader sentiment scores from JSONL file
        
        Args:
            input_jsonl_path: Path to input JSONL file with sentiment data
            preprocessed_path: Path to existing preprocessed Vader scores
            
        Returns:
            Processed DataFrame of Vader scores
        """
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
        
        # Date processing
        df['published_at'] = pd.to_datetime(df['published_at'], errors='coerce')
        start_date = df['published_at'].min().replace(tzinfo=None)
        end_date = df['published_at'].max().replace(tzinfo=None)
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
        
        # Calculate daily averages
        results = []
        for date in date_range:
            date_str = date.strftime('%Y-%m-%d')
            if date in date_scores:
                avg_score = sum(date_scores[date]) / len(date_scores[date])
                results.append([date_str, round(avg_score, 4)])
            elif date in existing_dates:
                continue  # Keep original from preprocessed file
            else:
                results.append([date_str, 0.0])

        # Combine with existing data
        if os.path.exists(preprocessed_path):
            existing_df = pd.read_csv(preprocessed_path)
            new_df = pd.DataFrame(results, columns=['date', 'avg_vader_score'])
            combined_df = pd.concat([existing_df, new_df])
            combined_df['date'] = pd.to_datetime(combined_df['date'])
            combined_df = combined_df.groupby('date', as_index=False).mean()
            combined_df = combined_df.sort_values('date')
            combined_df['avg_vader_score'] = combined_df['avg_vader_score'].round(4)
            self.vader_scores = combined_df
        else:
            new_df = pd.DataFrame(results, columns=['date', 'avg_vader_score'])
            self.vader_scores = new_df
        
        # Cleanup temp files
        os.remove(temp_csv_path)
        os.remove(unique_csv_path)
        return self.vader_scores
    
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

    def set_lstm_prices(self, input):
        self.lstm_prices = input

    def make_bigru_dataset(self):
        """
        Prepare dataset for BiGRU prediction
        
        Args:
            actual_prices: DataFrame of actual oil prices
            lstm_prices: Array of LSTM predicted prices
            
        Returns:
            Prepared DataFrame for BiGRU model
        """
        # Process and interpolate actual prices (last 27 days)
        data = self.actual_prices.copy()
        if 'Date' in data.columns:
            data['Date'] = pd.to_datetime(data['Date'])
            data.set_index('Date', inplace=True)
        data.sort_index(inplace=True)

        # Handle missing dates
        full_date_range = pd.date_range(start=data.index.min(), end=data.index.max(), freq='D')
        data = data.reindex(full_date_range)
        data_interpolated = data.interpolate(method='time')[-27:]
        
        # Prepare Vader scores (last 27 days)
        vader_scores = self.vader_scores[-27:].copy().rename(columns={'avg_vader_score': 'vader_score'})
        
        # Prepare LSTM predictions (last 27 days)
        lstm_prices_series = pd.Series(self.lstm_prices, name='predicted_price')
        
        # Combine all data
        self.bigru_dataset = pd.DataFrame({
            'vader_score': vader_scores['vader_score'].values,
            'predicted_price': lstm_prices_series.values,
            'actual_price': data_interpolated['Close'],
        })[['vader_score', 'predicted_price', 'actual_price']]
        
        return self.bigru_dataset

    def predict_for_bigru(self):
        """
        Generate predictions using the BiGRU model
        
        Returns:
            numpy array of final predicted prices
        """
        if self.bigru_dataset is None:
            raise ValueError("No dataset available - run make_bigru_dataset() first")
        if self.bigru_model is None:
            raise ValueError("BiGRU model failed to load")

        OUTPUT_LENGTH = 1
        df = self.bigru_dataset.copy()
        
        # Feature engineering
        df['predicted_price_change'] = df['predicted_price'].pct_change()
        df['predicted_moving_avg_3'] = df['predicted_price'].expanding(min_periods=3).mean()
        df['predicted_moving_avg_7'] = df['predicted_price'].expanding(min_periods=7).mean()
        df['predicted_volatility'] = df['predicted_price'].expanding(min_periods=5).std()
        df['vader_diff'] = df['vader_score'].diff()
        df['vader_moving_avg'] = df['vader_score'].expanding(min_periods=3).mean()
        df['vader_volatility'] = df['vader_score'].expanding(min_periods=5).std()
        df['prediction_error'] = df['predicted_price'] - df['actual_price']
        df['actual_price_lag1'] = df['actual_price'].shift(1)
        df['actual_price_lag2'] = df['actual_price'].shift(2)
        df['vader_price_interaction'] = df['vader_score'] * df['predicted_price'].pct_change()
        
        # Clean and prepare data
        df = df.dropna()
        features = df.drop(columns=['actual_price']).values.astype('float32')
        labels = df[['actual_price']].values.astype('float32')
        
        # Scale features
        feature_scaled = self.bigru_feature_scaler.transform(features)
        label_scaled = self.bigru_label_scaler.transform(labels)

        # Create sequences
        X, y = [], []
        for i in range(self.sequence_length, len(feature_scaled) - OUTPUT_LENGTH + 1):
            X.append(feature_scaled[i - self.sequence_length:i])
            y.append(label_scaled[i + OUTPUT_LENGTH - 1 : i + OUTPUT_LENGTH])

        X = np.array(X)
        y = np.array(y)

        # Make predictions
        predictions = self.bigru_model.predict(X)
        self.final_prices = self.bigru_label_scaler.inverse_transform(predictions)
        
        # Apply error correction
        correction_window = 5
        if len(self.final_prices) > correction_window:
            prices_1d = self.final_prices.flatten()
            ma_correction = pd.Series(prices_1d).rolling(correction_window, min_periods=1).mean().values
            self.final_prices = (0.85 * self.final_prices + 0.15 * ma_correction.reshape(-1, 1))
        
        # Calculate metrics
        y_pred_test = self.final_prices
        actual_prices = self.bigru_label_scaler.inverse_transform(y.reshape(-1,1))
        metrics_dict = {
            'MSE': mean_squared_error(actual_prices, y_pred_test),
            'RMSE': np.sqrt(mean_squared_error(actual_prices, y_pred_test)),
            'MAE': mean_absolute_error(actual_prices, y_pred_test),
            'MAPE': mean_absolute_percentage_error(actual_prices, y_pred_test),
            'R2': r2_score(actual_prices, y_pred_test)
        }

        print("\nEvaluation Metrics:")
        for metric, value in metrics_dict.items():
            print(f"{metric}: {value:.4f}")
        
        return self.final_prices
    
    def process_bigru_output(self):
        last_6_rows = self.bigru_dataset.tail(6)

        dates = last_6_rows.index[-6:]  
        actual_prices = last_6_rows['actual_price'].values[-6:]  
        last_date = last_6_rows.index[-1]  
        next_date = last_date + timedelta(days=1) 

        predicted_prices = self.final_prices.flatten()  

        final_dataset = pd.DataFrame({
            'Date': list(dates) + [next_date], 
            'actual_prices': list(actual_prices) + [np.nan], 
            'predicted_prices': list(predicted_prices)  
        })

        response = {
            "actual_prices": [
                {"date": row['Date'].strftime('%Y-%m-%d'), "price": row['actual_prices']} 
                for _, row in final_dataset.iterrows() 
                if not pd.isna(row['actual_prices'])
            ],
            "predicted_prices": [
                {"date": row['Date'].strftime('%Y-%m-%d'), "price": row['predicted_prices']} 
                for _, row in final_dataset.iterrows()
            ]
        }  # Convert to list of records
        return response

    def run_bigru_pipeline(self, input_jsonl_path="data_mock/new_news_data.jsonl", \
                           preprocessed_path='data_mock/preprocessed_vader_scores.csv', \
                            new_data_path = "data_mock/real_time_oil_prices.csv", \
                            old_data_path = "data_mock/preprocessed_oil_prices.csv"):
        """
        Complete BiGRU prediction pipeline
        
        Args:
            input_jsonl_path: Path to JSONL file with sentiment data
            actual_prices: DataFrame of actual oil prices
            lstm_prices: Array of LSTM predicted prices
            preprocessed_path: Path to existing preprocessed Vader scores
            
        Returns:
            numpy array of final predicted prices
        """
        self.process_new_prices(new_data_path, old_data_path)
        self.process_vader_scores(input_jsonl_path, preprocessed_path)
        self.make_bigru_dataset()
        self.predict_for_bigru()
        return self.process_bigru_output()