"""
Machine Learning models for anomaly detection
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta
import joblib
import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)


class AnomalyMLModel:
    """Machine Learning model for market data anomaly detection"""
    
    def __init__(self, contamination=0.1):
        self.contamination = contamination
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_columns = [
            'price', 'volume', 'price_change_pct', 'volume_change_pct',
            'price_volatility', 'volume_volatility', 'time_since_last_update'
        ]
    
    def prepare_features(self, data_points: List[Dict[str, Any]]) -> pd.DataFrame:
        """Prepare features for ML model"""
        if not data_points:
            return pd.DataFrame()
        
        df = pd.DataFrame(data_points)
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Calculate price changes
        df['price_change'] = df.groupby('symbol')['price'].diff()
        df['price_change_pct'] = df.groupby('symbol')['price'].pct_change() * 100
        
        # Calculate volume changes
        df['volume_change'] = df.groupby('symbol')['volume'].diff()
        df['volume_change_pct'] = df.groupby('symbol')['volume'].pct_change() * 100
        
        # Calculate rolling volatility (5-period)
        df['price_volatility'] = df.groupby('symbol')['price_change_pct'].rolling(5).std().reset_index(0, drop=True)
        df['volume_volatility'] = df.groupby('symbol')['volume_change_pct'].rolling(5).std().reset_index(0, drop=True)
        
        # Time since last update
        df['time_since_last_update'] = df.groupby('symbol')['timestamp'].diff().dt.total_seconds() / 60
        
        # Fill NaN values
        df = df.fillna(0)
        
        # Select feature columns
        feature_df = df[self.feature_columns].copy()
        
        return feature_df
    
    def train(self, training_data: List[Dict[str, Any]]) -> bool:
        """Train the ML model"""
        try:
            logger.info("Training anomaly detection ML model...")
            
            # Prepare features
            features_df = self.prepare_features(training_data)
            
            if features_df.empty:
                logger.error("No features available for training")
                return False
            
            # Scale features
            features_scaled = self.scaler.fit_transform(features_df)
            
            # Train model
            self.model.fit(features_scaled)
            self.is_trained = True
            
            logger.info(f"Model trained successfully with {len(features_df)} samples")
            return True
            
        except Exception as e:
            logger.error(f"Error training ML model: {e}")
            return False
    
    def predict_anomalies(self, data_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Predict anomalies using trained ML model"""
        if not self.is_trained:
            logger.warning("Model not trained yet")
            return []
        
        try:
            # Prepare features
            features_df = self.prepare_features(data_points)
            
            if features_df.empty:
                return []
            
            # Scale features
            features_scaled = self.scaler.transform(features_df)
            
            # Predict anomalies (-1 = anomaly, 1 = normal)
            predictions = self.model.predict(features_scaled)
            anomaly_scores = self.model.decision_function(features_scaled)
            
            # Create anomaly results
            anomalies = []
            df = pd.DataFrame(data_points)
            
            for i, (prediction, score) in enumerate(zip(predictions, anomaly_scores)):
                if prediction == -1:  # Anomaly detected
                    data_point = data_points[i]
                    
                    # Determine severity based on anomaly score
                    severity = self._get_severity_from_score(score)
                    
                    anomaly = {
                        'symbol': data_point['symbol'],
                        'anomaly_type': 'ml_detected',
                        'severity': severity,
                        'detected_at': datetime.now().isoformat(),
                        'data_timestamp': data_point['timestamp'],
                        'description': f'ML model detected anomaly (score: {score:.3f})',
                        'details': {
                            'anomaly_score': score,
                            'model_type': 'isolation_forest',
                            'features_used': self.feature_columns
                        }
                    }
                    anomalies.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error predicting anomalies: {e}")
            return []
    
    def _get_severity_from_score(self, score: float) -> str:
        """Determine severity based on anomaly score"""
        if score < -0.5:
            return 'critical'
        elif score < -0.3:
            return 'high'
        elif score < -0.1:
            return 'medium'
        else:
            return 'low'
    
    def save_model(self, filepath: str) -> bool:
        """Save trained model to file"""
        try:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'is_trained': self.is_trained,
                'feature_columns': self.feature_columns,
                'contamination': self.contamination
            }
            joblib.dump(model_data, filepath)
            logger.info(f"Model saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False
    
    def load_model(self, filepath: str) -> bool:
        """Load trained model from file"""
        try:
            model_data = joblib.load(filepath)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.is_trained = model_data['is_trained']
            self.feature_columns = model_data['feature_columns']
            self.contamination = model_data['contamination']
            logger.info(f"Model loaded from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False


class TimeSeriesAnomalyModel:
    """Time series specific anomaly detection model"""
    
    def __init__(self, window_size=20):
        self.window_size = window_size
        self.symbol_models = {}
    
    def detect_time_series_anomalies(self, data_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect time series anomalies using statistical methods"""
        anomalies = []
        
        # Group by symbol
        df = pd.DataFrame(data_points)
        
        for symbol in df['symbol'].unique():
            symbol_data = df[df['symbol'] == symbol].sort_values('timestamp')
            
            if len(symbol_data) < self.window_size:
                continue
            
            # Detect price anomalies using z-score
            price_anomalies = self._detect_zscore_anomalies(
                symbol_data, 'price', symbol, 'price_zscore'
            )
            anomalies.extend(price_anomalies)
            
            # Detect volume anomalies
            if 'volume' in symbol_data.columns:
                volume_anomalies = self._detect_zscore_anomalies(
                    symbol_data, 'volume', symbol, 'volume_zscore'
                )
                anomalies.extend(volume_anomalies)
        
        return anomalies
    
    def _detect_zscore_anomalies(self, data: pd.DataFrame, column: str, 
                                symbol: str, anomaly_type: str) -> List[Dict[str, Any]]:
        """Detect anomalies using z-score method"""
        anomalies = []
        
        # Calculate rolling mean and std
        rolling_mean = data[column].rolling(window=self.window_size).mean()
        rolling_std = data[column].rolling(window=self.window_size).std()
        
        # Calculate z-scores
        z_scores = (data[column] - rolling_mean) / rolling_std
        
        # Detect anomalies (|z-score| > 3)
        anomaly_threshold = 3.0
        anomaly_indices = np.where(np.abs(z_scores) > anomaly_threshold)[0]
        
        for idx in anomaly_indices:
            if idx >= self.window_size:  # Ensure we have enough history
                z_score = z_scores.iloc[idx]
                data_point = data.iloc[idx]
                
                severity = 'critical' if abs(z_score) > 4 else 'high'
                
                anomaly = {
                    'symbol': symbol,
                    'anomaly_type': anomaly_type,
                    'severity': severity,
                    'detected_at': datetime.now().isoformat(),
                    'data_timestamp': data_point['timestamp'],
                    'description': f'{column} z-score anomaly: {z_score:.2f}',
                    'details': {
                        'z_score': z_score,
                        'value': data_point[column],
                        'rolling_mean': rolling_mean.iloc[idx],
                        'rolling_std': rolling_std.iloc[idx],
                        'window_size': self.window_size
                    }
                }
                anomalies.append(anomaly)
        
        return anomalies


# Global model instances
anomaly_ml_model = AnomalyMLModel()
time_series_model = TimeSeriesAnomalyModel()


def get_ml_model() -> AnomalyMLModel:
    """Get the global ML model instance"""
    return anomaly_ml_model


def get_time_series_model() -> TimeSeriesAnomalyModel:
    """Get the global time series model instance"""
    return time_series_model
