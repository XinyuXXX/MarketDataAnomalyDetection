"""
Base adapter interface for data sources
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncIterator
from datetime import datetime
import logging

from src.models.data_models import MarketDataPoint, DataSourceConfig, DataSourceType, DataType


logger = logging.getLogger(__name__)


class BaseDataAdapter(ABC):
    """Base class for all data source adapters"""
    
    def __init__(self, config: DataSourceConfig):
        self.config = config
        self.name = config.name
        self.type = config.type
        self.connection_params = config.connection_params
        self._connected = False
        self._last_heartbeat = None
        
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to the data source"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Close connection to the data source"""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if connection is alive"""
        pass
    
    @abstractmethod
    async def get_latest_data(self, symbols: List[str], limit: int = 100) -> List[MarketDataPoint]:
        """Get latest data points for specified symbols"""
        pass
    
    @abstractmethod
    async def get_historical_data(
        self, 
        symbols: List[str], 
        start_time: datetime, 
        end_time: datetime,
        limit: int = 1000
    ) -> List[MarketDataPoint]:
        """Get historical data for specified symbols and time range"""
        pass
    
    @abstractmethod
    async def stream_data(self, symbols: List[str]) -> AsyncIterator[MarketDataPoint]:
        """Stream real-time data for specified symbols"""
        pass
    
    async def heartbeat(self) -> bool:
        """Send heartbeat to check connection health"""
        try:
            result = await self.test_connection()
            self._last_heartbeat = datetime.utcnow()
            return result
        except Exception as e:
            logger.error(f"Heartbeat failed for {self.name}: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if adapter is connected"""
        return self._connected
    
    def get_last_heartbeat(self) -> Optional[datetime]:
        """Get timestamp of last successful heartbeat"""
        return self._last_heartbeat
    
    def get_supported_symbols(self) -> List[str]:
        """Get list of supported symbols"""
        return self.config.expected_symbols
    
    def get_update_frequency(self) -> int:
        """Get expected update frequency in minutes"""
        return self.config.update_frequency_minutes
    
    async def initialize(self) -> bool:
        """Initialize the adapter"""
        try:
            logger.info(f"Initializing adapter: {self.name}")
            success = await self.connect()
            if success:
                logger.info(f"Adapter {self.name} initialized successfully")
            else:
                logger.error(f"Failed to initialize adapter: {self.name}")
            return success
        except Exception as e:
            logger.error(f"Error initializing adapter {self.name}: {e}")
            return False
    
    async def shutdown(self) -> bool:
        """Shutdown the adapter"""
        try:
            logger.info(f"Shutting down adapter: {self.name}")
            success = await self.disconnect()
            if success:
                logger.info(f"Adapter {self.name} shutdown successfully")
            else:
                logger.error(f"Failed to shutdown adapter: {self.name}")
            return success
        except Exception as e:
            logger.error(f"Error shutting down adapter {self.name}: {e}")
            return False
    
    def _parse_data_point(self, raw_data: Dict[str, Any], symbol: str, timestamp: datetime) -> MarketDataPoint:
        """Parse raw data into MarketDataPoint"""
        # Extract common fields
        price = None
        volume = None
        
        # Try to extract price from common field names
        for price_field in ['price', 'last_price', 'close', 'value']:
            if price_field in raw_data:
                try:
                    price = float(raw_data[price_field])
                    break
                except (ValueError, TypeError):
                    continue
        
        # Try to extract volume from common field names
        for volume_field in ['volume', 'size', 'quantity']:
            if volume_field in raw_data:
                try:
                    volume = float(raw_data[volume_field])
                    break
                except (ValueError, TypeError):
                    continue
        
        # Determine data type based on payload
        data_type = self._determine_data_type(raw_data)
        
        return MarketDataPoint(
            symbol=symbol,
            timestamp=timestamp,
            source=self.type,
            data_type=data_type,
            payload=raw_data,
            price=price,
            volume=volume
        )
    
    def _determine_data_type(self, raw_data: Dict[str, Any]) -> DataType:
        """Determine data type based on payload structure"""
        # Simple heuristic based on field names
        if any(field in raw_data for field in ['bid', 'ask', 'bid_size', 'ask_size']):
            return DataType.QUOTE
        elif any(field in raw_data for field in ['trade_price', 'trade_size', 'trade_time']):
            return DataType.TRADE
        elif 'volume' in raw_data:
            return DataType.VOLUME
        elif any(field in raw_data for field in ['price', 'last_price', 'close']):
            return DataType.PRICE
        else:
            return DataType.REFERENCE
