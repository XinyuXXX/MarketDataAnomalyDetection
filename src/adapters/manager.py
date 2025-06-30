"""
Data Source Manager - Manages all data source adapters
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from src.adapters.base import BaseDataAdapter
from src.adapters.gemfire_adapter import GemfireAdapter
from src.adapters.mssql_adapter import MSSQLAdapter
from src.models.data_models import DataSourceConfig, DataSourceType, MarketDataPoint
from src.config.settings import Settings


logger = logging.getLogger(__name__)


class DataSourceManager:
    """Manages all data source adapters"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.adapters: Dict[str, BaseDataAdapter] = {}
        self._health_check_task = None
        self._health_check_interval = 60  # seconds
        
    async def initialize(self) -> bool:
        """Initialize all configured data sources"""
        try:
            logger.info("Initializing data source manager...")
            
            # Load data source configurations
            configs = await self._load_data_source_configs()
            
            # Initialize adapters
            for config in configs:
                adapter = self._create_adapter(config)
                if adapter:
                    success = await adapter.initialize()
                    if success:
                        self.adapters[config.name] = adapter
                        logger.info(f"Initialized adapter: {config.name}")
                    else:
                        logger.error(f"Failed to initialize adapter: {config.name}")
            
            # Start health check task
            self._health_check_task = asyncio.create_task(self._health_check_loop())
            
            logger.info(f"Data source manager initialized with {len(self.adapters)} adapters")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing data source manager: {e}")
            return False
    
    async def shutdown(self) -> bool:
        """Shutdown all adapters"""
        try:
            logger.info("Shutting down data source manager...")
            
            # Cancel health check task
            if self._health_check_task:
                self._health_check_task.cancel()
                try:
                    await self._health_check_task
                except asyncio.CancelledError:
                    pass
            
            # Shutdown all adapters
            for name, adapter in self.adapters.items():
                try:
                    await adapter.shutdown()
                    logger.info(f"Shutdown adapter: {name}")
                except Exception as e:
                    logger.error(f"Error shutting down adapter {name}: {e}")
            
            self.adapters.clear()
            logger.info("Data source manager shutdown complete")
            return True
            
        except Exception as e:
            logger.error(f"Error shutting down data source manager: {e}")
            return False
    
    def _create_adapter(self, config: DataSourceConfig) -> Optional[BaseDataAdapter]:
        """Create adapter instance based on configuration"""
        try:
            if config.type == DataSourceType.GEMFIRE:
                return GemfireAdapter(config)
            elif config.type == DataSourceType.MSSQL:
                return MSSQLAdapter(config)
            elif config.type == DataSourceType.HBASE:
                # TODO: Implement HBase adapter
                logger.warning(f"HBase adapter not yet implemented")
                return None
            elif config.type == DataSourceType.EOD:
                # TODO: Implement EOD adapter
                logger.warning(f"EOD adapter not yet implemented")
                return None
            else:
                logger.error(f"Unknown data source type: {config.type}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating adapter for {config.name}: {e}")
            return None
    
    async def _load_data_source_configs(self) -> List[DataSourceConfig]:
        """Load data source configurations"""
        # For now, create default configurations based on settings
        configs = []
        
        # Gemfire configuration
        if hasattr(self.settings, 'gemfire'):
            gemfire_config = DataSourceConfig(
                name="gemfire_cache",
                type=DataSourceType.GEMFIRE,
                connection_params={
                    "locators": self.settings.gemfire.locators,
                    "username": self.settings.gemfire.username,
                    "password": self.settings.gemfire.password,
                    "regions": ["market_data", "quotes", "trades"]
                },
                expected_symbols=["AAPL", "GOOGL", "MSFT", "TSLA"],
                update_frequency_minutes=1,
                enable_missing_data_detection=True,
                enable_price_movement_detection=True,
                enable_stale_data_detection=True
            )
            configs.append(gemfire_config)
        
        # MSSQL configuration
        if hasattr(self.settings, 'mssql'):
            mssql_config = DataSourceConfig(
                name="mssql_historical",
                type=DataSourceType.MSSQL,
                connection_params={
                    "server": self.settings.mssql.server,
                    "database": self.settings.mssql.database,
                    "username": self.settings.mssql.username,
                    "password": self.settings.mssql.password,
                    "driver": self.settings.mssql.driver
                },
                expected_symbols=["AAPL", "GOOGL", "MSFT", "TSLA"],
                update_frequency_minutes=60,  # Historical data updates less frequently
                enable_missing_data_detection=True,
                enable_price_movement_detection=False,  # Not for historical analysis
                enable_stale_data_detection=True
            )
            configs.append(mssql_config)
        
        return configs
    
    async def get_latest_data(self, symbols: List[str], source_names: List[str] = None) -> List[MarketDataPoint]:
        """Get latest data from specified sources"""
        try:
            all_data = []
            
            # Determine which adapters to query
            adapters_to_query = {}
            if source_names:
                for name in source_names:
                    if name in self.adapters:
                        adapters_to_query[name] = self.adapters[name]
            else:
                adapters_to_query = self.adapters
            
            # Query all adapters concurrently
            tasks = []
            for name, adapter in adapters_to_query.items():
                if adapter.is_connected():
                    task = adapter.get_latest_data(symbols)
                    tasks.append((name, task))
            
            # Wait for all tasks to complete
            for name, task in tasks:
                try:
                    data = await task
                    all_data.extend(data)
                    logger.debug(f"Got {len(data)} data points from {name}")
                except Exception as e:
                    logger.error(f"Error getting data from {name}: {e}")
            
            return all_data
            
        except Exception as e:
            logger.error(f"Error getting latest data: {e}")
            return []
    
    async def get_historical_data(
        self, 
        symbols: List[str], 
        start_time: datetime, 
        end_time: datetime,
        source_names: List[str] = None
    ) -> List[MarketDataPoint]:
        """Get historical data from specified sources"""
        try:
            all_data = []
            
            # Determine which adapters to query
            adapters_to_query = {}
            if source_names:
                for name in source_names:
                    if name in self.adapters:
                        adapters_to_query[name] = self.adapters[name]
            else:
                adapters_to_query = self.adapters
            
            # Query adapters that support historical data
            tasks = []
            for name, adapter in adapters_to_query.items():
                if adapter.is_connected():
                    task = adapter.get_historical_data(symbols, start_time, end_time)
                    tasks.append((name, task))
            
            # Wait for all tasks to complete
            for name, task in tasks:
                try:
                    data = await task
                    all_data.extend(data)
                    logger.debug(f"Got {len(data)} historical data points from {name}")
                except Exception as e:
                    logger.error(f"Error getting historical data from {name}: {e}")
            
            return all_data
            
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return []
    
    def get_adapter(self, name: str) -> Optional[BaseDataAdapter]:
        """Get adapter by name"""
        return self.adapters.get(name)
    
    def get_all_adapters(self) -> Dict[str, BaseDataAdapter]:
        """Get all adapters"""
        return self.adapters.copy()
    
    def is_healthy(self) -> bool:
        """Check if all adapters are healthy"""
        if not self.adapters:
            return False
        
        return all(adapter.is_connected() for adapter in self.adapters.values())
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get detailed health status"""
        status = {
            "overall_healthy": self.is_healthy(),
            "total_adapters": len(self.adapters),
            "connected_adapters": sum(1 for adapter in self.adapters.values() if adapter.is_connected()),
            "adapters": {}
        }
        
        for name, adapter in self.adapters.items():
            status["adapters"][name] = {
                "connected": adapter.is_connected(),
                "last_heartbeat": adapter.get_last_heartbeat().isoformat() if adapter.get_last_heartbeat() else None,
                "type": adapter.type.value,
                "supported_symbols": adapter.get_supported_symbols()
            }
        
        return status
    
    async def _health_check_loop(self):
        """Periodic health check for all adapters"""
        while True:
            try:
                logger.debug("Running health check for all adapters...")
                
                for name, adapter in self.adapters.items():
                    try:
                        healthy = await adapter.heartbeat()
                        if not healthy:
                            logger.warning(f"Adapter {name} failed health check")
                    except Exception as e:
                        logger.error(f"Health check error for {name}: {e}")
                
                await asyncio.sleep(self._health_check_interval)
                
            except asyncio.CancelledError:
                logger.info("Health check loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(self._health_check_interval)
