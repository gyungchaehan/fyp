import pytest
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from keras.models import Model
from keras.layers import Input, Dense, GRU, Bidirectional
from keras import backend as K  
import os
import tempfile
from bigru import OilPricePredictor
import shutil

# Constants
SEED = 42
INPUT_LENGTH = 14
OUTPUT_LENGTH = 1
DATA_PATH = "input_bigru.csv"

# -------------------------------
# Test Data Generation
# -------------------------------

def generate_test_data(num_samples=100):
    """Generate synthetic oil price data with sentiment scores"""
    dates = pd.date_range(start='2020-01-01', periods=num_samples)
    data = {
        'date': dates,
        'vader_score': np.random.uniform(-1, 1, num_samples),
        'predicted_price': np.cumsum(np.random.normal(0, 1, num_samples)) + 50,
        'actual_price': np.cumsum(np.random.normal(0, 0.8, num_samples)) + 50
    }
    return pd.DataFrame(data)

# -------------------------------
# Test Cases
# -------------------------------

def test_data_loading_and_feature_engineering():
    """Test data loading and feature engineering pipeline"""
    test_data = generate_test_data(50)
    
    # Save to temp CSV
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp:
        test_data.to_csv(tmp.name, index=False)
        tmp_path = tmp.name
    
    # Initialize predictor and test loading
    predictor = OilPricePredictor()
    loaded_data = predictor.load_data(tmp_path)
    
    # Test basic loading
    assert isinstance(loaded_data, pd.DataFrame)
    assert set(['date', 'vader_score', 'predicted_price', 'actual_price']).issubset(loaded_data.columns)
    
    # Test feature engineering
    engineered_data = predictor.add_features(loaded_data)
    expected_features = [
        'vader_score', 'predicted_price', 'predicted_price_change',
        'predicted_moving_avg_3', 'predicted_moving_avg_7', 'predicted_volatility',
        'vader_diff', 'vader_moving_avg', 'vader_volatility', 'prediction_error',
        'predicted_price_lag1', 'predicted_price_lag2', 'vader_price_interaction',
        'actual_price'
    ]
    assert list(engineered_data.columns) == expected_features
    assert engineered_data.isna().sum().sum() == 0
    
    # Cleanup
    os.unlink(tmp_path)

def test_normalization():
    """Test data normalization"""
    test_data = generate_test_data(100)
    predictor = OilPricePredictor()
    
    # First test that feature engineering works
    engineered_data = predictor.add_features(test_data)
    assert not engineered_data.isnull().values.any(), "There should be no NaNs after feature engineering"
    
    # Test normalization
    features, label = predictor.normalize_data(engineered_data)
    
    # Test feature scaling range
    assert features.shape[1] == engineered_data.shape[1] - 1  # minus label column
    assert np.allclose(features.min(axis=0), -1, atol=1e-6), f"Features should min at -1, got {features.min()}"
    assert np.allclose(features.max(axis=0), 1, atol=1e-6), f"Features should max at 1, got {features.max()}"
    
    # Test label scaling (StandardScaler should produce mean~0, std~1)
    assert abs(label.mean()) < 0.1, f"Labels should be centered near 0, got mean {label.mean()}"
    assert 0.9 < label.std() < 1.1, f"Labels should have std~1, got {label.std()}"

def test_sequence_creation():
    """Test time series sequence generation"""
    test_data = generate_test_data(200)
    engineered_data = OilPricePredictor().add_features(test_data)
    predictor = OilPricePredictor()
    features, label = predictor.normalize_data(engineered_data)
    X_train, X_test, y_train, y_test = predictor.create_sequences(features, label)
    
    # Test sequence shapes
    assert X_train.shape[0] == y_train.shape[0]
    assert X_test.shape[0] == y_test.shape[0]
    assert X_train.shape[1] == INPUT_LENGTH
    assert X_train.shape[2] == engineered_data.shape[1] - 1  # num features
    
    # Test train-test split ratio (~80-20)
    assert 0.75 <= X_train.shape[0] / (X_train.shape[0] + X_test.shape[0]) <= 0.85

def test_model_architecture():
    """Test BiGRU model architecture with attention mechanism"""
    predictor = OilPricePredictor()
    input_shape = (INPUT_LENGTH, 13)  # 13 features after engineering
    model = predictor.build_model(input_shape)
    
    # Get all layers with their names
    layer_dict = {layer.name: layer for layer in model.layers}
    
    # 1. Test critical components exist
    assert 'input_layer' in layer_dict
    assert 'bidirectional_gru' in layer_dict
    assert 'output' in layer_dict
    
    # 2. Verify attention mechanism components
    assert 'attention_weights' in layer_dict, "Attention weights layer missing"
    assert 'vader_mask' in layer_dict, "Vader mask layer missing"
    assert 'masked_attention' in layer_dict, "Masked attention layer missing"
    assert 'weighted_features' in layer_dict, "Feature weighting layer missing"
    
    # 3. Verify attention layer properties
    attention_layer = layer_dict['attention_weights']
    assert isinstance(attention_layer, tf.keras.layers.Dense)
    assert attention_layer.activation.__name__ == 'sigmoid'
    assert attention_layer.units == input_shape[1]  # Should match sequence length
    
    # 4. Verify Vader mask properties
    mask_layer = layer_dict['vader_mask']
    assert isinstance(mask_layer, tf.keras.layers.Lambda)
    
    # 5. Verify the full attention flow
    # Check that masked_attention combines weights and mask
    masked_layer = layer_dict['masked_attention']
    assert isinstance(masked_layer, tf.keras.layers.Multiply)
    
    # 6. Verify BiGRU layer
    bigru_layer = layer_dict['bidirectional_gru']
    assert isinstance(bigru_layer, tf.keras.layers.Bidirectional)
    assert isinstance(bigru_layer.layer, tf.keras.layers.GRU)
    assert bigru_layer.layer.units == 64
    assert bigru_layer.merge_mode == 'concat'
    
    # 7. Test output shape
    assert model.output_shape == (None, 1), "Incorrect output shape"

def test_training_and_evaluation(tmpdir):
    """Test model training and evaluation pipeline"""
    from pathlib import Path
    
    # Convert tmpdir to Path object
    tmp_path = Path(tmpdir)
    
    # Create fresh directories
    model_dir = tmp_path / 'best_model'
    artifacts_dir = tmp_path / 'model_artifacts'
    
    shutil.rmtree(model_dir, ignore_errors=True)
    shutil.rmtree(artifacts_dir, ignore_errors=True)
    
    model_dir.mkdir()
    artifacts_dir.mkdir()
    
    # Generate test data
    test_data = generate_test_data(150)
    test_file = tmp_path / "test_data.csv"
    test_data.to_csv(str(test_file), index=False)
    
    # Initialize predictor with test directories
    predictor = OilPricePredictor()
    predictor.DATA_PATH = str(test_file)
    predictor.best_model_path = model_dir  # Override save paths
    predictor.model_artifacts_path = artifacts_dir
    
    # Run full pipeline
    predictor.run_pipeline()
        
    # --- File Existence Checks ---
    assert (model_dir / 'best_model.h5').exists(), "Model file missing"
    assert (model_dir / 'training_log.csv').exists(), "Training log missing"
    assert (model_dir / 'predictions_results.csv').exists(), "Predictions missing"
    assert (model_dir / 'metrics_results.csv').exists(), "Metrics missing"
    assert (artifacts_dir / 'feature_scaler.joblib').exists(), "Feature scaler missing"
    assert (artifacts_dir / 'label_scaler.joblib').exists(), "Label scaler missing"
    
    # --- Metrics File Content Validation ---
    metrics_df = pd.read_csv(model_dir / 'metrics_results.csv')
    
    # 1. Check all required metrics are present
    required_metrics = {'MSE', 'RMSE', 'MAE', 'MAPE', 'R2'}
    assert required_metrics.issubset(metrics_df['Metric'].values), \
        f"Missing metrics. Expected: {required_metrics}, Found: {set(metrics_df['Metric'].values)}"
    
    # 2. Check metric values are reasonable
    metrics_dict = dict(zip(metrics_df['Metric'], metrics_df['Value']))
    
    assert metrics_dict['MSE'] >= 0, "MSE should be non-negative"
    assert metrics_dict['RMSE'] >= 0, "RMSE should be non-negative"
    assert metrics_dict['MAE'] >= 0, "MAE should be non-negative"
    assert 0 <= metrics_dict['MAPE'] <= 100, "MAPE should be between 0-100"
    assert -1 <= metrics_dict['R2'] <= 1, "R² should be between -1 and 1"
    
    # 3. Verify RMSE ≈ sqrt(MSE) within tolerance
    assert np.isclose(
        metrics_dict['RMSE'],
        np.sqrt(metrics_dict['MSE']),
        rtol=0.01
    ), "RMSE should approximately equal sqrt(MSE)"
    
    # --- Predictions File Validation ---
    preds_df = pd.read_csv(tmp_path / 'best_model/predictions_results.csv')
    
    # 1. Check required columns
    assert {'Actual_Price', 'Predicted_Price'}.issubset(preds_df.columns)
    
    # 2. Check no null values
    assert not preds_df.isnull().values.any(), "Predictions contain null values"
    
    # 3. Check reasonable value ranges
    assert (preds_df['Actual_Price'] > 0).all(), "Prices should be positive"
    assert (preds_df['Predicted_Price'] > 0).all(), "Predictions should be positive"
    
# -------------------------------
# Main Test Execution
# -------------------------------

if __name__ == "__main__":
    # Run tests with temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        test_data_loading_and_feature_engineering()
        test_normalization()
        test_sequence_creation()
        test_model_architecture()
        test_training_and_evaluation(tmpdir)
    
    print("All tests passed successfully!")