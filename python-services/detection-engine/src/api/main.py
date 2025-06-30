from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Market Data Anomaly Detection Engine",
    description="Python-based anomaly detection algorithms",
    version="1.0.0"
)

class MarketDataPoint(BaseModel):
    symbol: str
    timestamp: datetime
    source: str
    data_type: str
    payload: Dict[str, Any]
    price: float = None
    volume: float = None

class AnomalyResult(BaseModel):
    symbol: str
    anomaly_type: str
    severity: str
    detected_at: datetime
    description: str
    details: Dict[str, Any]

@app.get("/")
async def root():
    return {"message": "Market Data Anomaly Detection Engine", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "UP", "service": "detection-engine", "timestamp": datetime.now()}

@app.post("/detect/missing-data")
async def detect_missing_data(data_points: List[MarketDataPoint]) -> List[AnomalyResult]:
    """Detect missing data anomalies"""
    from src.algorithms.missing_data_detector import MissingDataDetector

    detector = MissingDataDetector()
    anomalies = detector.detect(data_points)
    return anomalies

@app.post("/detect/price-movement")
async def detect_price_movement(data_points: List[MarketDataPoint]) -> List[AnomalyResult]:
    """Detect price movement anomalies"""
    from src.algorithms.price_movement_detector import PriceMovementDetector

    detector = PriceMovementDetector()
    anomalies = detector.detect(data_points)
    return anomalies

@app.post("/detect/ml-anomalies")
async def detect_ml_anomalies(data_points: List[MarketDataPoint]) -> List[AnomalyResult]:
    """Detect anomalies using machine learning models"""
    try:
        import sys
        sys.path.append('../ml-models/src')
        from anomaly_ml_model import get_ml_model, get_time_series_model

        # Convert to dict format
        data_dicts = [dp.dict() for dp in data_points]

        # Get ML model results
        ml_model = get_ml_model()
        ml_anomalies = ml_model.predict_anomalies(data_dicts)

        # Get time series model results
        ts_model = get_time_series_model()
        ts_anomalies = ts_model.detect_time_series_anomalies(data_dicts)

        # Combine results
        all_anomalies = ml_anomalies + ts_anomalies

        # Convert to AnomalyResult format
        results = []
        for anomaly in all_anomalies:
            result = AnomalyResult(
                symbol=anomaly['symbol'],
                anomaly_type=anomaly['anomaly_type'],
                severity=anomaly['severity'],
                detected_at=datetime.fromisoformat(anomaly['detected_at']),
                description=anomaly['description'],
                details=anomaly['details']
            )
            results.append(result)

        return results

    except Exception as e:
        logger.error(f"Error in ML anomaly detection: {e}")
        return []

@app.post("/train-ml-model")
async def train_ml_model(training_data: List[MarketDataPoint]) -> Dict[str, Any]:
    """Train the ML model with new data"""
    try:
        import sys
        sys.path.append('../ml-models/src')
        from anomaly_ml_model import get_ml_model

        # Convert to dict format
        data_dicts = [dp.dict() for dp in training_data]

        # Train model
        ml_model = get_ml_model()
        success = ml_model.train(data_dicts)

        return {
            "success": success,
            "message": f"Model trained with {len(training_data)} samples" if success else "Training failed",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error training ML model: {e}")
        return {
            "success": False,
            "message": f"Training failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8085)