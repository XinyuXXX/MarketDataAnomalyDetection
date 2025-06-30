"""
Data models for the Market Data Anomaly Detection System
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
from pydantic import BaseModel, Field
from dataclasses import dataclass


class DataSourceType(str, Enum):
    """Data source types"""
    GEMFIRE = "gemfire"
    EOD = "eod"
    MSSQL = "mssql"
    HBASE = "hbase"


class DataType(str, Enum):
    """Market data types"""
    PRICE = "price"
    VOLUME = "volume"
    TRADE = "trade"
    QUOTE = "quote"
    ORDER_BOOK = "order_book"
    INDEX = "index"
    REFERENCE = "reference"


class AnomalyType(str, Enum):
    """Types of anomalies"""
    MISSING_DATA = "missing_data"
    PRICE_MOVEMENT = "price_movement"
    DATA_STALE = "data_stale"
    VOLUME_SPIKE = "volume_spike"
    DATA_QUALITY = "data_quality"


class Severity(str, Enum):
    """Anomaly severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MarketDataPoint(BaseModel):
    """Base market data point model"""
    symbol: str = Field(..., description="Financial instrument symbol")
    timestamp: datetime = Field(..., description="Data timestamp")
    source: DataSourceType = Field(..., description="Data source")
    data_type: DataType = Field(..., description="Type of market data")
    payload: Dict[str, Any] = Field(..., description="Raw data payload")
    
    # Common fields that might be extracted from payload
    price: Optional[float] = Field(None, description="Price value")
    volume: Optional[float] = Field(None, description="Volume value")
    
    # Metadata
    received_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DataSourceConfig(BaseModel):
    """Configuration for a data source"""
    name: str = Field(..., description="Data source name")
    type: DataSourceType = Field(..., description="Data source type")
    connection_params: Dict[str, Any] = Field(..., description="Connection parameters")
    
    # Data expectations
    expected_symbols: List[str] = Field(default_factory=list)
    expected_data_types: List[DataType] = Field(default_factory=list)
    update_frequency_minutes: int = Field(default=1, description="Expected update frequency")
    
    # Time windows
    market_open_time: str = Field(default="09:30", description="Market open time (HH:MM)")
    market_close_time: str = Field(default="16:00", description="Market close time (HH:MM)")
    timezone: str = Field(default="US/Eastern", description="Market timezone")
    
    # Anomaly detection settings
    enable_missing_data_detection: bool = Field(default=True)
    enable_price_movement_detection: bool = Field(default=True)
    enable_stale_data_detection: bool = Field(default=True)
    
    # Thresholds
    missing_data_threshold_minutes: Optional[int] = None
    price_movement_threshold_percent: Optional[float] = None
    stale_data_threshold_minutes: Optional[int] = None


class Anomaly(BaseModel):
    """Anomaly detection result"""
    id: Optional[str] = Field(None, description="Unique anomaly ID")
    symbol: str = Field(..., description="Affected symbol")
    anomaly_type: AnomalyType = Field(..., description="Type of anomaly")
    severity: Severity = Field(..., description="Severity level")
    
    # Timing
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    data_timestamp: datetime = Field(..., description="Timestamp of the anomalous data")
    
    # Details
    description: str = Field(..., description="Human-readable description")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional details")
    
    # Source information
    data_source: DataSourceType = Field(..., description="Source of the data")
    data_type: DataType = Field(..., description="Type of data")
    
    # Values
    expected_value: Optional[float] = Field(None, description="Expected value")
    actual_value: Optional[float] = Field(None, description="Actual value")
    threshold: Optional[float] = Field(None, description="Threshold that was breached")
    
    # Status
    acknowledged: bool = Field(default=False)
    resolved: bool = Field(default=False)
    resolved_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AlertRule(BaseModel):
    """Alert rule configuration"""
    id: Optional[str] = Field(None, description="Rule ID")
    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    
    # Conditions
    symbols: List[str] = Field(default_factory=list, description="Symbols to monitor (empty = all)")
    data_sources: List[DataSourceType] = Field(default_factory=list, description="Data sources to monitor")
    anomaly_types: List[AnomalyType] = Field(default_factory=list, description="Anomaly types to alert on")
    min_severity: Severity = Field(default=Severity.MEDIUM, description="Minimum severity to alert")
    
    # Notification settings
    email_recipients: List[str] = Field(default_factory=list)
    sms_recipients: List[str] = Field(default_factory=list)
    webhook_urls: List[str] = Field(default_factory=list)
    
    # Timing
    active_hours_start: str = Field(default="00:00", description="Start of active hours (HH:MM)")
    active_hours_end: str = Field(default="23:59", description="End of active hours (HH:MM)")
    timezone: str = Field(default="US/Eastern")
    
    # Rate limiting
    max_alerts_per_hour: int = Field(default=10)
    cooldown_minutes: int = Field(default=15)
    
    # Status
    enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


@dataclass
class DetectionResult:
    """Result of anomaly detection"""
    anomalies: List[Anomaly]
    processed_count: int
    processing_time_seconds: float
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


@dataclass
class SystemHealth:
    """System health status"""
    overall_status: str  # healthy, degraded, unhealthy
    components: Dict[str, bool]
    last_check: datetime
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}
