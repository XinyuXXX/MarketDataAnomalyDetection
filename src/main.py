"""
Market Data Anomaly Detection System - Main Application Entry Point
"""

import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.config.settings import get_settings
from src.api.routes import router as api_router
from src.detection.engine import AnomalyDetectionEngine
from src.adapters.manager import DataSourceManager


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Global instances
detection_engine = None
data_source_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global detection_engine, data_source_manager
    
    logger.info("Starting Market Data Anomaly Detection System...")
    
    # Initialize settings
    settings = get_settings()
    
    # Initialize data source manager
    data_source_manager = DataSourceManager(settings)
    await data_source_manager.initialize()
    
    # Initialize detection engine
    detection_engine = AnomalyDetectionEngine(settings, data_source_manager)
    await detection_engine.initialize()
    
    logger.info("System initialized successfully")
    
    yield
    
    # Cleanup
    logger.info("Shutting down system...")
    if detection_engine:
        await detection_engine.shutdown()
    if data_source_manager:
        await data_source_manager.shutdown()
    logger.info("System shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Market Data Anomaly Detection System",
    description="Enterprise-grade market data anomaly detection and monitoring system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Market Data Anomaly Detection System",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check system components
        health_status = {
            "status": "healthy",
            "components": {
                "detection_engine": detection_engine.is_healthy() if detection_engine else False,
                "data_sources": data_source_manager.is_healthy() if data_source_manager else False,
            }
        }
        
        # Overall health
        all_healthy = all(health_status["components"].values())
        health_status["status"] = "healthy" if all_healthy else "unhealthy"
        
        return health_status
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
