import sys
import warnings
import os
if not sys.warnoptions:
    warnings.simplefilter('ignore')
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from keras.layers import Layer, Dense, Dropout, GRU, Bidirectional, Lambda, Input, Conv1D, Multiply, Add, Permute, LayerNormalization, GlobalAveragePooling1D
from keras.models import *
from keras import metrics
from tensorflow.keras.callbacks import ModelCheckpoint
from keras.models import load_model
from tensorflow.keras.callbacks import CSVLogger
from tensorflow.keras.optimizers import Adam
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, mean_absolute_percentage_error
from keras import regularizers
import keras.backend as K

import random
seed_value = 42
np.random.seed(seed_value)
random.seed(seed_value)
tf.random.set_seed(seed_value)


def load_data(filepath):
    df = pd.read_csv(filepath)
    return df

def add_features(dataset):
    df = pd.DataFrame(dataset, columns=['date', 'vader_score', 'predicted_price', 'actual_price'])
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

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
    df = df.drop(columns=['date'])

    df.to_csv("enhanced_input.csv", index=False)

    return df.values

def normalization(dataset):
    feature1 = dataset[:,0:2].astype('float32')
    feature2 = dataset[:,3:].astype('float32')
    label = dataset[:,2].reshape(-1,1).astype('float32')
    feature_scaler = MinMaxScaler(feature_range=(-1, 1))
    label_scaler = StandardScaler()
    
    feature1_scaled = feature_scaler.fit_transform(feature1)
    feature2_scaled = feature_scaler.fit_transform(feature2)
    label_scaled = label_scaler.fit_transform(label)

    features_scaled = np.concatenate([feature1_scaled, feature2_scaled], axis=1)
    
    return features_scaled, label_scaled, feature_scaler, label_scaler

def sequence_and_split(features, label):
    X, y = [], []

    for i in range(INPUT_LENGTH, len(features) - OUTPUT_LENGTH + 1):
        X.append(features[i - INPUT_LENGTH:i])
        y.append(label[i + OUTPUT_LENGTH - 1 : i + OUTPUT_LENGTH])

    x_dataset, y_dataset = np.array(X), np.array(y)
    # PROPER time series split (80-20)
    # split_idx = int(len(x_dataset) * 0.8)
    
    # X_train = x_dataset[:split_idx]
    # y_train = y_dataset[:split_idx]
    
    # X_test = x_dataset[split_idx:]
    # y_test = y_dataset[split_idx:]
    
    return x_dataset, y_dataset

def build_bigru_model(input_row, input_col):
    input_layer = Input(shape=(input_row, input_col)) #None, 7, 2

    att = Dense(input_col, activation='sigmoid', kernel_regularizer=regularizers.l2(0.01))(input_layer)  # Simplified attention
    # vader_mask = Lambda(lambda x: K.cast(K.greater(x, 0), K.floatx()))(input_layer[:, :, 0:1]) 
    vader_mask = Lambda(
        lambda x: K.cast(K.greater(x, 0), K.floatx()),
        output_shape=(input_row, 1)
    )(input_layer[:, :, 0:1])  # Extract the first feature for the mask

    att = Multiply()([att, vader_mask])  
    input_layer = Multiply()([input_layer, att])  

    bigru1 = Bidirectional(GRU(64, return_sequences=False), merge_mode='concat')(input_layer) # None, 7, 128
    bigru1 = LayerNormalization()(bigru1)
    bigru1 = Dropout(0.2)(bigru1)
    
    dense = Dense(32, activation='selu', kernel_regularizer=regularizers.l2(0.01))(bigru1)
    dense = Dropout(0.2)(dense)

    output = Dense(1, activation='linear')(bigru1)
    model = Model(inputs=input_layer, outputs=output)
    model.compile(optimizer=Adam(learning_rate=0.001),
                loss=tf.keras.losses.Huber(),
                metrics=[
                    metrics.MeanSquaredError(),
                    metrics.RootMeanSquaredError(),
                    metrics.MeanAbsoluteError(),  
                ])
    return model

def evaluate_model(model, X_test, y_test, label_scaler, output_predictions_csv='predictions_results.csv', output_metrics_csv='metrics_results_att_bigru.csv'):
    # Make predictions
    prediction_test = model.predict(X_test)
    y_pred_test = label_scaler.inverse_transform(prediction_test)
    actual_prices = label_scaler.inverse_transform(y_test.reshape(-1, 1))

    # Create DataFrame with results
    results_df = pd.DataFrame({
        'Actual_Price': actual_prices.flatten(),
        'Predicted_Price': y_pred_test.flatten()
    })

    # Calculate metrics
    metrics_dict = {
        'MSE': mean_squared_error(actual_prices, y_pred_test),
        'RMSE': np.sqrt(mean_squared_error(actual_prices, y_pred_test)),
        'MAE': mean_absolute_error(actual_prices, y_pred_test),
        'MAPE': mean_absolute_percentage_error(actual_prices, y_pred_test),
        'R2': r2_score(actual_prices, y_pred_test)
    }

    # Save predictions to CSV (overwrite)
    # results_df.to_csv(output_predictions_csv, index=False)

    # Prepare metrics DataFrame
    metrics_df = pd.DataFrame(list(metrics_dict.items()), columns=['Metric', 'Value'])

    # Append metrics to CSV
    metrics_df.to_csv(output_metrics_csv, mode='a', index=False)

    return metrics_dict, actual_prices, y_pred_test

# Price Movement Direction Accuracy (PMDA)
def pmda_future(true_pri, pred_pri, days_ahead):
    true_pri = np.array(true_pri)
    pred_pri = np.array(pred_pri)

    # Ensure there are enough data points
    if len(true_pri) < days_ahead + 1 or len(pred_pri) < days_ahead:
        raise ValueError("Not enough data points for the specified days ahead.")

    # Calculate the price movements
    diff_true_price = np.diff(true_pri, n=days_ahead) 
    diff_pred_true_price = pred_pri - true_pri[:-days_ahead]  

    # Calculate PMDA
    count = np.sum(diff_true_price * diff_pred_true_price >= 0)  
    pmda = count / len(diff_true_price)  

    return pmda

if __name__ == "__main__":
    DATA_PATH = "input_bigru_latest.csv"
    INPUT_LENGTH = 14
    OUTPUT_LENGTH = 1

    dataset = load_data(DATA_PATH)
    dataset = add_features(dataset)
    features, label, feature_scaler, label_scaler = normalization(dataset)
    x,y = sequence_and_split(features, label)
    # input_row = int(X_train.shape[1]) 
    # input_col  = int(X_train.shape[2])
    # model = build_bigru_model(input_row, input_col)
    # model.summary()

    # callbacks = [ModelCheckpoint(
    #     'best_model.h5',
    #     monitor='val_loss',
    #     save_best_only=True,
    #     verbose=0
    # ), tf.keras.callbacks.EarlyStopping(
    #     monitor='val_loss',
    #     patience=15,
    #     restore_best_weights=True), CSVLogger('training_log.csv')]

    
    # # Training
    # history = model.fit(
    #     X_train, y_train, shuffle=False,
    #     validation_data=(X_test, y_test),
    #     epochs=300,  #Set high since early_stopping will intervene
    #     callbacks=callbacks,
    #     verbose = 1
    # )

    # # Check actual epochs used
    # print(f"Training stopped after {len(history.history['loss'])} epochs")

    # #Evaluation and Predicttion
    # print("Finished!!!!")
    best_model = load_model('best_model.h5')

    # eva = best_model.evaluate(X_test, y_test)
    # print("From .evaluate")
    # print('MSE = %.4f'%eva[1])
    # print("RMSE = %.4f"%eva[2])
    # print("MAE = %.4f"%eva[3])

    metrics_dict, actual_prices, pred_prices = evaluate_model(best_model, x, y, label_scaler)
    prediction_prices = pred_prices.tolist()
    pred_prices = list(x[0] for x in prediction_prices)
    print("\nEvaluation Metrics:")
    for metric, value in metrics_dict.items():
        print(f"{metric}: {value:.4f}")
    
    # PMDA = pmda_future(dataset[-X_test.shape[0]-OUTPUT_LENGTH:,-1], pred_prices, OUTPUT_LENGTH)
    # print('Direction Accuracy = %.4f'%PMDA)
