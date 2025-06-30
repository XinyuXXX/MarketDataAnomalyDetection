import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Any

class PriceMovementDetector:
    """Detects abnormal price movement anomalies"""

    def __init__(self, threshold_percent: float = 5.0, window_minutes: int = 15):
        self.threshold_percent = threshold_percent
        self.window_minutes = window_minutes

    def detect(self, data_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect price movement anomalies"""
        anomalies = []

        if not data_points:
            return anomalies

        # Convert to DataFrame
        df = pd.DataFrame(data_points)

        # Group by symbol
        for symbol in df['symbol'].unique():
            symbol_data = df[df['symbol'] == symbol].sort_values('timestamp')

            if len(symbol_data) < 2:
                continue

            # Calculate price changes
            symbol_data['price_change'] = symbol_data['price'].pct_change() * 100

            # Find anomalous movements
            for idx, row in symbol_data.iterrows():
                if pd.isna(row['price_change']):
                    continue

                abs_change = abs(row['price_change'])

                if abs_change > self.threshold_percent:
                    severity = 'critical' if abs_change > self.threshold_percent * 2 else 'high'

                    anomaly = {
                        'symbol': symbol,
                        'anomaly_type': 'price_movement',
                        'severity': severity,
                        'detected_at': datetime.now(),
                        'description': f'Price moved {row["price_change"]:.2f}% in {self.window_minutes} minutes',
                        'details': {
                            'price_change_percent': row['price_change'],
                            'threshold_percent': self.threshold_percent,
                            'current_price': row['price'],
                            'timestamp': row['timestamp']
                        }
                    }
                    anomalies.append(anomaly)

        return anomalies