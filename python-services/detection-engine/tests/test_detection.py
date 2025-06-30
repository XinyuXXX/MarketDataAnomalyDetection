import pytest
from src.algorithms.missing_data_detector import MissingDataDetector
from src.algorithms.price_movement_detector import PriceMovementDetector
from datetime import datetime, timedelta

class TestMissingDataDetector:
    """Test missing data detection algorithm"""

    def test_no_missing_data(self):
        """Test when there is no missing data"""
        detector = MissingDataDetector(threshold_minutes=30)

        # Create test data with no gaps
        data_points = [
            {
                'symbol': 'AAPL',
                'timestamp': (datetime.now() - timedelta(minutes=i)).isoformat(),
                'price': 150.0 + i
            }
            for i in range(5)
        ]

        anomalies = detector.detect(data_points)
        assert len(anomalies) == 0

    def test_missing_data_detected(self):
        """Test when missing data is detected"""
        detector = MissingDataDetector(threshold_minutes=30)

        # Create test data with a gap
        now = datetime.now()
        data_points = [
            {
                'symbol': 'AAPL',
                'timestamp': now.isoformat(),
                'price': 150.0
            },
            {
                'symbol': 'AAPL',
                'timestamp': (now - timedelta(hours=2)).isoformat(),  # 2 hour gap
                'price': 149.0
            }
        ]

        anomalies = detector.detect(data_points)
        assert len(anomalies) == 1
        assert anomalies[0]['anomaly_type'] == 'missing_data'

class TestPriceMovementDetector:
    """Test price movement detection algorithm"""

    def test_normal_price_movement(self):
        """Test normal price movement (no anomaly)"""
        detector = PriceMovementDetector(threshold_percent=5.0)

        data_points = [
            {'symbol': 'AAPL', 'timestamp': datetime.now().isoformat(), 'price': 150.0},
            {'symbol': 'AAPL', 'timestamp': datetime.now().isoformat(), 'price': 151.0}  # 0.67% change
        ]

        anomalies = detector.detect(data_points)
        assert len(anomalies) == 0

    def test_abnormal_price_movement(self):
        """Test abnormal price movement (anomaly detected)"""
        detector = PriceMovementDetector(threshold_percent=5.0)

        data_points = [
            {'symbol': 'AAPL', 'timestamp': datetime.now().isoformat(), 'price': 150.0},
            {'symbol': 'AAPL', 'timestamp': datetime.now().isoformat(), 'price': 160.0}  # 6.67% change
        ]

        anomalies = detector.detect(data_points)
        assert len(anomalies) == 1
        assert anomalies[0]['anomaly_type'] == 'price_movement'
        assert anomalies[0]['severity'] in ['high', 'critical']