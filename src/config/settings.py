"""
Configuration settings for the Market Data Anomaly Detection System
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseSettings, Field
from functools import lru_cache
import os


class DatabaseSettings(BaseSettings):
    """Database configuration"""
    url: str = Field(default="postgresql://admin:password123@localhost:5432/anomaly_detection")
    pool_size: int = Field(default=10)
    max_overflow: int = Field(default=20)
    echo: bool = Field(default=False)

    class Config:
        env_prefix = "DATABASE_"


class RedisSettings(BaseSettings):
    """Redis configuration"""
    url: str = Field(default="redis://localhost:6379")
    db: int = Field(default=0)
    max_connections: int = Field(default=10)

    class Config:
        env_prefix = "REDIS_"


class KafkaSettings(BaseSettings):
    """Kafka configuration"""
    bootstrap_servers: str = Field(default="localhost:9092")
    consumer_group: str = Field(default="anomaly_detection")
    auto_offset_reset: str = Field(default="latest")

    class Config:
        env_prefix = "KAFKA_"


class GemfireSettings(BaseSettings):
    """Gemfire configuration"""
    locators: str = Field(default="localhost:10334")
    username: Optional[str] = None
    password: Optional[str] = None
    pool_name: str = Field(default="anomaly_detection_pool")

    class Config:
        env_prefix = "GEMFIRE_"


class MSSQLSettings(BaseSettings):
    """MSSQL configuration"""
    server: str = Field(default="localhost")
    database: str = Field(default="MarketData")
    username: str = Field(default="sa")
    password: str = Field(default="Password123")
    driver: str = Field(default="ODBC Driver 17 for SQL Server")

    class Config:
        env_prefix = "MSSQL_"


class HBaseSettings(BaseSettings):
    """HBase configuration"""
    host: str = Field(default="localhost")
    port: int = Field(default=9090)
    timeout: int = Field(default=30000)
    table_prefix: str = Field(default="market_data")

    class Config:
        env_prefix = "HBASE_"


class AlertingSettings(BaseSettings):
    """Alerting configuration"""
    smtp_server: str = Field(default="smtp.gmail.com")
    smtp_port: int = Field(default=587)
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    default_recipients: List[str] = Field(default_factory=list)
    
    # Twilio settings for SMS
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_number: Optional[str] = None
    
    # Webhook settings
    webhook_urls: List[str] = Field(default_factory=list)

    class Config:
        env_prefix = "ALERTING_"


class DetectionSettings(BaseSettings):
    """Detection engine configuration"""
    # Data missing detection
    missing_data_threshold_minutes: int = Field(default=30)
    
    # Price movement detection
    price_movement_threshold_percent: float = Field(default=5.0)
    price_movement_window_minutes: int = Field(default=15)
    
    # Data stale detection
    stale_data_threshold_minutes: int = Field(default=60)
    
    # Batch processing
    batch_size: int = Field(default=1000)
    max_workers: int = Field(default=4)

    class Config:
        env_prefix = "DETECTION_"


class Settings(BaseSettings):
    """Main application settings"""
    app_name: str = Field(default="Market Data Anomaly Detection System")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")
    
    # Component settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    kafka: KafkaSettings = Field(default_factory=KafkaSettings)
    gemfire: GemfireSettings = Field(default_factory=GemfireSettings)
    mssql: MSSQLSettings = Field(default_factory=MSSQLSettings)
    hbase: HBaseSettings = Field(default_factory=HBaseSettings)
    alerting: AlertingSettings = Field(default_factory=AlertingSettings)
    detection: DetectionSettings = Field(default_factory=DetectionSettings)

    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize nested settings with environment variables
        self.database = DatabaseSettings()
        self.redis = RedisSettings()
        self.kafka = KafkaSettings()
        self.gemfire = GemfireSettings()
        self.mssql = MSSQLSettings()
        self.hbase = HBaseSettings()
        self.alerting = AlertingSettings()
        self.detection = DetectionSettings()


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
