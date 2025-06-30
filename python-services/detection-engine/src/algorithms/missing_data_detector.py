import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any

class MissingDataDetector:
    """Detects missing data anomalies"""

    def __init__(self, threshold_minutes: int = 30):
        self.threshold_minutes = threshold_minutes

    def detect(self, data_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect missing data anomalies"""
        anomalies = []

        if not data_points:
            return anomalies

        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(data_points)

        # Group by symbol
        for symbol in df['symbol'].unique():
            symbol_data = df[df['symbol'] == symbol].sort_values('timestamp')

            # Check for gaps in data
            for i in range(1, len(symbol_data)):
                current_time = pd.to_datetime(symbol_data.iloc[i]['timestamp'])
                previous_time = pd.to_datetime(symbol_data.iloc[i-1]['timestamp'])

                gap_minutes = (current_time - previous_time).total_seconds() / 60

                if gap_minutes > self.threshold_minutes:
                    anomaly = {
                        'symbol': symbol,
                        'anomaly_type': 'missing_data',
                        'severity': 'high' if gap_minutes > self.threshold_minutes * 2 else 'medium',
                        'detected_at': datetime.now(),
                        'description': f'Missing data for {gap_minutes:.1f} minutes',
                        'details': {
                            'gap_minutes': gap_minutes,
                            'threshold_minutes': self.threshold_minutes,
                            'last_data_time': previous_time.isoformat(),
                            'next_data_time': current_time.isoformat()
                        }
                    }
                    anomalies.append(anomaly)

        return anomalies