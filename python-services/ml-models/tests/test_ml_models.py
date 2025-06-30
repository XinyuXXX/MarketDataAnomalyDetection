"""
Tests for ML anomaly detection models
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from anomaly_ml_model import AnomalyMLModel, TimeSeriesAnomalyModel


class TestAnomalyMLModel:
    """Test cases for AnomalyMLModel"""
    
    def setup_method(self):
        """Setup test data"""
        self.model = AnomalyMLModel(contamination=0.1)
        
        # Generate sample training data
        self.training_data = self._generate_sample_data(1000, include_anomalies=True)
        
        # Generate test data
        self.test_data = self._generate_sample_data(100, include_anomalies=False)
        self.anomaly_data = self._generate_anomaly_data(10)
    
    def _generate_sample_data(self, n_samples: int, include_anomalies: bool = False):
        """Generate sample market data"""
        data = []
        symbols = ['AAPL', 'GOOGL', 'MSFT']
        base_time = datetime.now() - timedelta(days=30)
        
        for i in range(n_samples):
            symbol = np.random.choice(symbols)
            
            # Normal price and volume
            price = 100 + np.random.normal(0, 5)
            volume = 1000 + np.random.normal(0, 200)
            
            # Add anomalies occasionally
            if include_anomalies and np.random.random() < 0.05:
                price *= np.random.choice([0.5, 2.0])  # Price spike/drop
                volume *= np.random.choice([0.1, 10.0])  # Volume spike/drop
            
            data.append({
                'symbol': symbol,
                'timestamp': (base_time + timedelta(minutes=i)).isoformat(),
                'price': max(0.01, price),  # Ensure positive price
                'volume': max(1, volume)    # Ensure positive volume
            })
        
        return data
    
    def _generate_anomaly_data(self, n_samples: int):
        """Generate obvious anomaly data"""
        data = []
        base_time = datetime.now()
        
        for i in range(n_samples):
            data.append({
                'symbol': 'AAPL',
                'timestamp': (base_time + timedelta(minutes=i)).isoformat(),
                'price': 1000 + np.random.normal(0, 100),  # Very high price
                'volume': 100000 + np.random.normal(0, 10000)  # Very high volume
            })
        
        return data
    
    def test_feature_preparation(self):
        """Test feature preparation"""
        features_df = self.model.prepare_features(self.training_data)
        
        assert not features_df.empty
        assert len(features_df) == len(self.training_data)
        assert all(col in features_df.columns for col in self.model.feature_columns)
    
    def test_model_training(self):
        """Test model training"""
        success = self.model.train(self.training_data)
        
        assert success
        assert self.model.is_trained
    
    def test_anomaly_prediction(self):
        """Test anomaly prediction"""
        # Train model first
        self.model.train(self.training_data)
        
        # Test on normal data
        normal_anomalies = self.model.predict_anomalies(self.test_data)
        
        # Test on anomaly data
        anomaly_results = self.model.predict_anomalies(self.anomaly_data)
        
        # Should detect more anomalies in anomaly data
        assert len(anomaly_results) >= len(normal_anomalies)
    
    def test_model_save_load(self):
        """Test model save and load"""
        # Train model
        self.model.train(self.training_data)
        
        # Save model
        model_path = '/tmp/test_anomaly_model.pkl'
        success = self.model.save_model(model_path)
        assert success
        
        # Create new model and load
        new_model = AnomalyMLModel()
        success = new_model.load_model(model_path)
        assert success
        assert new_model.is_trained
        
        # Clean up
        os.remove(model_path)


class TestTimeSeriesAnomalyModel:
    """Test cases for TimeSeriesAnomalyModel"""
    
    def setup_method(self):
        """Setup test data"""
        self.model = TimeSeriesAnomalyModel(window_size=10)
        self.test_data = self._generate_time_series_data()
    
    def _generate_time_series_data(self):
        """Generate time series data with anomalies"""
        data = []
        base_time = datetime.now() - timedelta(hours=1)
        
        # Generate normal data
        for i in range(50):
            price = 100 + np.sin(i * 0.1) * 5 + np.random.normal(0, 1)
            volume = 1000 + np.random.normal(0, 100)
            
            data.append({
                'symbol': 'AAPL',
                'timestamp': (base_time + timedelta(minutes=i)).isoformat(),
                'price': price,
                'volume': volume
            })
        
        # Add obvious anomalies
        anomaly_indices = [25, 35, 45]
        for idx in anomaly_indices:
            data[idx]['price'] *= 2  # Price spike
            data[idx]['volume'] *= 5  # Volume spike
        
        return data
    
    def test_time_series_anomaly_detection(self):
        """Test time series anomaly detection"""
        anomalies = self.model.detect_time_series_anomalies(self.test_data)
        
        # Should detect some anomalies
        assert len(anomalies) > 0
        
        # Check anomaly structure
        for anomaly in anomalies:
            assert 'symbol' in anomaly
            assert 'anomaly_type' in anomaly
            assert 'severity' in anomaly
            assert 'detected_at' in anomaly
            assert 'details' in anomaly
            assert 'z_score' in anomaly['details']


def test_model_integration():
    """Test integration between models"""
    # Generate test data
    data = []
    base_time = datetime.now()
    
    for i in range(100):
        data.append({
            'symbol': 'AAPL',
            'timestamp': (base_time + timedelta(minutes=i)).isoformat(),
            'price': 100 + np.random.normal(0, 5),
            'volume': 1000 + np.random.normal(0, 200)
        })
    
    # Test ML model
    ml_model = AnomalyMLModel()
    ml_model.train(data)
    ml_anomalies = ml_model.predict_anomalies(data[-10:])
    
    # Test time series model
    ts_model = TimeSeriesAnomalyModel()
    ts_anomalies = ts_model.detect_time_series_anomalies(data)
    
    # Both models should work without errors
    assert isinstance(ml_anomalies, list)
    assert isinstance(ts_anomalies, list)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
