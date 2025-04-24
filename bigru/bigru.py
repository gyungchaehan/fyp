import os
import sys
import warnings
import random
import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.metrics import (
    mean_squared_error, 
    mean_absolute_error, 
    r2_score, 
    mean_absolute_percentage_error
)
from keras.models import Model, load_model
from keras.layers import (
    Layer, Dense, Dropout, GRU, Bidirectional, 
    Lambda, Input, Multiply, LayerNormalization
)
from keras import metrics, regularizers
from keras import backend as K
from tensorflow.keras.callbacks import ModelCheckpoint, CSVLogger, EarlyStopping
from tensorflow.keras.optimizers import Adam
from joblib import dump
from pathlib import Path

# Constants
SEED = 42
INPUT_LENGTH = 14
OUTPUT_LENGTH = 1
DATA_PATH = "input_bigru.csv"

# Set random seeds for reproducibility
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

# Suppress warnings if not in debug mode
if not sys.warnoptions:
    warnings.simplefilter('ignore')


class OilPricePredictor:
    def __init__(self, base_dir=Path('.')):
        self.feature_scaler = None
        self.label_scaler = None
        self.model = None
        self.base_dir = base_dir
        self.best_model_path = self.base_dir / 'best_model'
        self.model_artifacts_path = self.base_dir / 'model_artifacts'
        
        # Create directories if they don't exist
        self.best_model_path.mkdir(parents=True, exist_ok=True)
        self.model_artifacts_path.mkdir(parents=True, exist_ok=True)


    def load_data(self, filepath):
        """Load dataset from CSV file"""
        return pd.read_csv(filepath)

    def add_features(self, dataset):
        """Feature engineering for oil price prediction"""
        df = dataset.copy()
        
        # Date handling
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')

        # Price features
        df['predicted_price_change'] = df['predicted_price'].pct_change()
        df['predicted_moving_avg_3'] = df['predicted_price'].rolling(3).mean()
        df['predicted_moving_avg_7'] = df['predicted_price'].rolling(7).mean()
        df['predicted_volatility'] = df['predicted_price'].rolling(5).std()

        # Sentiment features
        df['vader_diff'] = df['vader_score'].diff()
        df['vader_moving_avg'] = df['vader_score'].rolling(3).mean()
        df['vader_volatility'] = df['vader_score'].rolling(5).std()

        # Error features
        df['prediction_error'] = df['predicted_price'] - df['actual_price']
        
        # Lag features
        df['predicted_price_lag1'] = df['predicted_price'].shift(1)
        df['predicted_price_lag2'] = df['predicted_price'].shift(2)

        # Interaction features
        df['vader_price_interaction'] = df['vader_score'] * df['predicted_price'].pct_change()

        # Cleanup
        df = df.dropna().drop(columns=['date'])
        
        # Final column ordering
        columns = [
            'vader_score', 'predicted_price', 'predicted_price_change',
            'predicted_moving_avg_3', 'predicted_moving_avg_7', 'predicted_volatility',
            'vader_diff', 'vader_moving_avg', 'vader_volatility', 'prediction_error',
            'predicted_price_lag1', 'predicted_price_lag2', 'vader_price_interaction',
            'actual_price'
        ]
        
        return df[columns]

    def normalize_data(self, dataset):
        """Normalize features and labels"""
        features = dataset.drop(columns=['actual_price']).values.astype('float32')
        label = dataset[['actual_price']].values.astype('float32')

        self.feature_scaler = MinMaxScaler(feature_range=(-1, 1))
        self.label_scaler = StandardScaler()

        features_scaled = self.feature_scaler.fit_transform(features)
        label_scaled = self.label_scaler.fit_transform(label)

        return features_scaled, label_scaled

    def create_sequences(self, features, label):
        """Create time series sequences for training"""
        X, y = [], []

        for i in range(INPUT_LENGTH, len(features) - OUTPUT_LENGTH + 1):
            X.append(features[i - INPUT_LENGTH:i])
            y.append(label[i + OUTPUT_LENGTH - 1:i + OUTPUT_LENGTH])

        x_dataset, y_dataset = np.array(X), np.array(y)
        
        # Time-based split (80-20)
        split_idx = int(len(x_dataset) * 0.8)
        
        return (
            x_dataset[:split_idx], 
            x_dataset[split_idx:], 
            y_dataset[:split_idx], 
            y_dataset[split_idx:]
        )

    def build_model(self, input_shape):
        """Build BiGRU model with attention mechanism"""
        input_layer = Input(shape=input_shape, name='input_layer')
        
        # Attention mechanism
        att_weights = Dense(
            input_shape[1], 
            activation='sigmoid', 
            kernel_regularizer=regularizers.l2(0.01),
            name='attention_weights'
        )(input_layer)
        
        vader_mask = Lambda(
            lambda x: K.cast(K.not_equal(x, 0), K.floatx()),
            output_shape=(input_shape[0], 1),
            name='vader_mask'
        )(input_layer[:, :, 0:1])
        
        masked_att = Multiply(name='masked_attention')([att_weights, vader_mask])
        weighted_input = Multiply(name='weighted_features')([input_layer, masked_att])
        
        # BiGRU layers
        bigru = Bidirectional(
            GRU(64, return_sequences=False),
            merge_mode='concat',
            name='bidirectional_gru'
        )(weighted_input)
        
        bigru = LayerNormalization(name='gru_layer_norm')(bigru)
        bigru = Dropout(0.2, name='gru_dropout')(bigru)
        
        # Dense layers
        dense = Dense(
            32, 
            activation='selu',
            kernel_regularizer=regularizers.l2(0.01),
            name='feature_transformation'
        )(bigru)
        dense = Dropout(0.2, name='transformation_dropout')(dense)
        
        # Output
        output = Dense(1, activation='linear', name='output')(dense)
        
        model = Model(inputs=input_layer, outputs=output)
        
        model.compile(
            optimizer=Adam(learning_rate=0.001), 
            loss=tf.keras.losses.Huber(),
            metrics=[
                metrics.MeanSquaredError(),
                metrics.RootMeanSquaredError(),
                metrics.MeanAbsoluteError(),  
            ]
        )
        
        return model

    def train_model(self, X_train, y_train, X_test, y_test):
        """Train the model with callbacks"""
        callbacks = [
            ModelCheckpoint(
                self.best_model_path / 'best_model.h5',  
                monitor='val_loss',
                save_best_only=True,
                verbose=0
            ),
            EarlyStopping(
                monitor='val_loss',
                patience=15,
                restore_best_weights=True
            ),
            CSVLogger(self.best_model_path / 'training_log.csv')
        ]

        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_test, y_test),
            epochs=300,
            callbacks=callbacks,
            shuffle=False,
            verbose=1
        )

        return history

    def evaluate(self, X_test, y_test):
        """Evaluate model performance"""
        # Load best model
        best_model = load_model('best_model/best_model.h5')
        
        # Make predictions
        y_pred = best_model.predict(X_test)
        y_pred = self.label_scaler.inverse_transform(y_pred)
        y_true = self.label_scaler.inverse_transform(y_test.reshape(-1, 1))

        # Calculate metrics
        metrics = {
            'MSE': mean_squared_error(y_true, y_pred),
            'RMSE': np.sqrt(mean_squared_error(y_true, y_pred)),
            'MAE': mean_absolute_error(y_true, y_pred),
            'MAPE': mean_absolute_percentage_error(y_true, y_pred),
            'R2': r2_score(y_true, y_pred)
        }

        # Save results
        results_df = pd.DataFrame({
            'Actual_Price': y_true.flatten(),
            'Predicted_Price': y_pred.flatten()
        })
        results_df.to_csv(self.best_model_path / 'predictions_results.csv', index=False)

        metrics_df = pd.DataFrame(list(metrics.items()), columns=['Metric', 'Value'])
        metrics_df.to_csv(self.best_model_path / 'metrics_results.csv', index=False)

        return metrics, y_true, y_pred

    def run_pipeline(self):
        """Complete training pipeline"""
        # Load and preprocess data
        dataset = self.load_data(DATA_PATH)
        dataset = self.add_features(dataset)
        features, label = self.normalize_data(dataset)
        
        # Save scalers
        os.makedirs('model_artifacts', exist_ok=True)
        dump(self.feature_scaler, self.model_artifacts_path / 'feature_scaler.joblib')
        dump(self.label_scaler, self.model_artifacts_path / 'label_scaler.joblib')
        
        # Prepare sequences
        X_train, X_test, y_train, y_test = self.create_sequences(features, label)
        
        # Build and train model
        self.model = self.build_model((X_train.shape[1], X_train.shape[2]))
        self.model.summary()
        
        history = self.train_model(X_train, y_train, X_test, y_test)
        print(f"Training stopped after {len(history.history['loss'])} epochs")
        
        # Evaluate
        metrics, y_true, y_pred = self.evaluate(X_test, y_test)
        
        print("\nEvaluation Metrics:")
        for metric, value in metrics.items():
            print(f"{metric}: {value:.4f}")


if __name__ == "__main__":
    predictor = OilPricePredictor()
    predictor.run_pipeline()