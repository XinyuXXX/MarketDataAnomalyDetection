"""
Gemfire Cache data adapter
"""

import asyncio
import json
from typing import List, Dict, Any, Optional, AsyncIterator
from datetime import datetime, timedelta
import logging

from src.adapters.base import BaseDataAdapter
from src.models.data_models import MarketDataPoint, DataSourceConfig, DataSourceType


logger = logging.getLogger(__name__)


class GemfireAdapter(BaseDataAdapter):
    """Adapter for Gemfire Cache data source"""
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self._client = None
        self._regions = {}
        self._cache = None
        
    async def connect(self) -> bool:
        """Connect to Gemfire cluster"""
        try:
            # Note: This is a simplified implementation
            # In practice, you would use the actual Gemfire Python client
            logger.info(f"Connecting to Gemfire at {self.connection_params.get('locators')}")
            
            # Simulate connection setup
            await asyncio.sleep(0.1)  # Simulate connection time
            
            # Initialize regions based on configuration
            regions = self.connection_params.get('regions', ['market_data'])
            for region_name in regions:
                self._regions[region_name] = f"region_{region_name}"
            
            self._connected = True
            logger.info(f"Connected to Gemfire successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Gemfire: {e}")
            self._connected = False
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Gemfire"""
        try:
            if self._client:
                # Close client connection
                pass
            
            self._connected = False
            self._regions.clear()
            logger.info("Disconnected from Gemfire")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from Gemfire: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """Test Gemfire connection"""
        try:
            if not self._connected:
                return False
            
            # Simulate connection test
            await asyncio.sleep(0.01)
            return True
            
        except Exception as e:
            logger.error(f"Gemfire connection test failed: {e}")
            return False
    
    async def get_latest_data(self, symbols: List[str], limit: int = 100) -> List[MarketDataPoint]:
        """Get latest data from Gemfire cache"""
        try:
            if not self._connected:
                raise Exception("Not connected to Gemfire")
            
            data_points = []
            
            for symbol in symbols:
                # Simulate getting data from cache
                # In practice, you would query the actual Gemfire region
                cache_key = f"market_data:{symbol}"
                
                # Simulate cached data
                cached_data = await self._get_from_cache(cache_key)
                if cached_data:
                    for data in cached_data[:limit]:
                        data_point = self._parse_data_point(
                            data, 
                            symbol, 
                            datetime.fromisoformat(data.get('timestamp', datetime.utcnow().isoformat()))
                        )
                        data_points.append(data_point)
            
            return data_points
            
        except Exception as e:
            logger.error(f"Error getting latest data from Gemfire: {e}")
            return []
    
    async def get_historical_data(
        self, 
        symbols: List[str], 
        start_time: datetime, 
        end_time: datetime,
        limit: int = 1000
    ) -> List[MarketDataPoint]:
        """Get historical data from Gemfire (limited support)"""
        try:
            # Gemfire is primarily a cache, so historical data might be limited
            # This would typically delegate to another data source
            logger.warning("Gemfire has limited historical data support")
            
            # For now, return recent cached data within the time range
            recent_data = await self.get_latest_data(symbols, limit)
            
            # Filter by time range
            filtered_data = [
                dp for dp in recent_data 
                if start_time <= dp.timestamp <= end_time
            ]
            
            return filtered_data[:limit]
            
        except Exception as e:
            logger.error(f"Error getting historical data from Gemfire: {e}")
            return []
    
    async def stream_data(self, symbols: List[str]) -> AsyncIterator[MarketDataPoint]:
        """Stream real-time data from Gemfire"""
        try:
            if not self._connected:
                raise Exception("Not connected to Gemfire")
            
            logger.info(f"Starting Gemfire data stream for symbols: {symbols}")
            
            while self._connected:
                # Simulate real-time data streaming
                for symbol in symbols:
                    # In practice, you would set up cache listeners
                    # or poll the cache for updates
                    
                    # Simulate getting updated data
                    updated_data = await self._get_cache_updates(symbol)
                    
                    if updated_data:
                        for data in updated_data:
                            data_point = self._parse_data_point(
                                data, 
                                symbol, 
                                datetime.fromisoformat(data.get('timestamp', datetime.utcnow().isoformat()))
                            )
                            yield data_point
                
                # Wait before next poll
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error streaming data from Gemfire: {e}")
    
    async def _get_from_cache(self, cache_key: str) -> List[Dict[str, Any]]:
        """Get data from Gemfire cache"""
        # Simulate cache lookup
        # In practice, this would use the Gemfire client API
        
        # Generate sample data
        sample_data = [
            {
                'timestamp': (datetime.utcnow() - timedelta(minutes=i)).isoformat(),
                'price': 100.0 + i * 0.1,
                'volume': 1000 + i * 10,
                'bid': 99.9 + i * 0.1,
                'ask': 100.1 + i * 0.1,
                'source': 'gemfire_cache'
            }
            for i in range(5)
        ]
        
        return sample_data
    
    async def _get_cache_updates(self, symbol: str) -> List[Dict[str, Any]]:
        """Get cache updates for a symbol"""
        # Simulate cache updates
        # In practice, this would use cache event listeners
        
        # Randomly generate updates
        import random
        if random.random() < 0.3:  # 30% chance of update
            return [{
                'timestamp': datetime.utcnow().isoformat(),
                'price': 100.0 + random.uniform(-5, 5),
                'volume': random.randint(100, 10000),
                'bid': 99.9 + random.uniform(-5, 5),
                'ask': 100.1 + random.uniform(-5, 5),
                'source': 'gemfire_cache',
                'symbol': symbol
            }]
        
        return []
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'connected': self._connected,
            'regions': list(self._regions.keys()),
            'last_heartbeat': self._last_heartbeat.isoformat() if self._last_heartbeat else None
        }
