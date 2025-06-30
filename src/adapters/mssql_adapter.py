"""
MSSQL database adapter for historical market data
"""

import asyncio
import pyodbc
from typing import List, Dict, Any, Optional, AsyncIterator
from datetime import datetime, timedelta
import logging
import pandas as pd

from src.adapters.base import BaseDataAdapter
from src.models.data_models import MarketDataPoint, DataSourceConfig, DataSourceType


logger = logging.getLogger(__name__)


class MSSQLAdapter(BaseDataAdapter):
    """Adapter for MSSQL database"""
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self._connection = None
        self._connection_string = None
        
    async def connect(self) -> bool:
        """Connect to MSSQL database"""
        try:
            # Build connection string
            server = self.connection_params.get('server', 'localhost')
            database = self.connection_params.get('database', 'MarketData')
            username = self.connection_params.get('username', 'sa')
            password = self.connection_params.get('password', '')
            driver = self.connection_params.get('driver', 'ODBC Driver 17 for SQL Server')
            
            self._connection_string = (
                f"DRIVER={{{driver}}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"UID={username};"
                f"PWD={password};"
                "TrustServerCertificate=yes;"
            )
            
            # Test connection
            await asyncio.get_event_loop().run_in_executor(
                None, self._test_sync_connection
            )
            
            self._connected = True
            logger.info(f"Connected to MSSQL database: {database}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MSSQL: {e}")
            self._connected = False
            return False
    
    def _test_sync_connection(self):
        """Test connection synchronously"""
        conn = pyodbc.connect(self._connection_string)
        conn.close()
    
    async def disconnect(self) -> bool:
        """Disconnect from MSSQL"""
        try:
            if self._connection:
                self._connection.close()
                self._connection = None
            
            self._connected = False
            logger.info("Disconnected from MSSQL")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from MSSQL: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """Test MSSQL connection"""
        try:
            if not self._connected:
                return False
            
            # Execute simple query
            result = await self._execute_query("SELECT 1 as test")
            return len(result) > 0
            
        except Exception as e:
            logger.error(f"MSSQL connection test failed: {e}")
            return False
    
    async def get_latest_data(self, symbols: List[str], limit: int = 100) -> List[MarketDataPoint]:
        """Get latest data from MSSQL"""
        try:
            if not self._connected:
                raise Exception("Not connected to MSSQL")
            
            # Build query for latest data
            symbols_str = "', '".join(symbols)
            query = f"""
            SELECT TOP {limit} 
                symbol, timestamp, price, volume, 
                bid, ask, data_type, payload
            FROM market_data 
            WHERE symbol IN ('{symbols_str}')
            ORDER BY timestamp DESC
            """
            
            rows = await self._execute_query(query)
            data_points = []
            
            for row in rows:
                # Parse payload if it's JSON
                payload = {}
                if row.get('payload'):
                    try:
                        import json
                        payload = json.loads(row['payload'])
                    except:
                        payload = {'raw_data': row['payload']}
                
                # Add other fields to payload
                payload.update({
                    'price': row.get('price'),
                    'volume': row.get('volume'),
                    'bid': row.get('bid'),
                    'ask': row.get('ask'),
                    'data_type': row.get('data_type', 'price')
                })
                
                data_point = self._parse_data_point(
                    payload,
                    row['symbol'],
                    row['timestamp']
                )
                data_points.append(data_point)
            
            return data_points
            
        except Exception as e:
            logger.error(f"Error getting latest data from MSSQL: {e}")
            return []
    
    async def get_historical_data(
        self, 
        symbols: List[str], 
        start_time: datetime, 
        end_time: datetime,
        limit: int = 1000
    ) -> List[MarketDataPoint]:
        """Get historical data from MSSQL"""
        try:
            if not self._connected:
                raise Exception("Not connected to MSSQL")
            
            symbols_str = "', '".join(symbols)
            query = f"""
            SELECT TOP {limit}
                symbol, timestamp, price, volume,
                bid, ask, data_type, payload
            FROM market_data 
            WHERE symbol IN ('{symbols_str}')
                AND timestamp >= ?
                AND timestamp <= ?
            ORDER BY timestamp DESC
            """
            
            rows = await self._execute_query(query, (start_time, end_time))
            data_points = []
            
            for row in rows:
                # Parse payload
                payload = {}
                if row.get('payload'):
                    try:
                        import json
                        payload = json.loads(row['payload'])
                    except:
                        payload = {'raw_data': row['payload']}
                
                payload.update({
                    'price': row.get('price'),
                    'volume': row.get('volume'),
                    'bid': row.get('bid'),
                    'ask': row.get('ask'),
                    'data_type': row.get('data_type', 'price')
                })
                
                data_point = self._parse_data_point(
                    payload,
                    row['symbol'],
                    row['timestamp']
                )
                data_points.append(data_point)
            
            return data_points
            
        except Exception as e:
            logger.error(f"Error getting historical data from MSSQL: {e}")
            return []
    
    async def stream_data(self, symbols: List[str]) -> AsyncIterator[MarketDataPoint]:
        """Stream data from MSSQL (polling-based)"""
        try:
            if not self._connected:
                raise Exception("Not connected to MSSQL")
            
            logger.info(f"Starting MSSQL data stream for symbols: {symbols}")
            last_timestamp = datetime.utcnow() - timedelta(minutes=5)
            
            while self._connected:
                # Get new data since last check
                new_data = await self.get_historical_data(
                    symbols, 
                    last_timestamp, 
                    datetime.utcnow(),
                    limit=100
                )
                
                for data_point in new_data:
                    if data_point.timestamp > last_timestamp:
                        yield data_point
                        last_timestamp = max(last_timestamp, data_point.timestamp)
                
                # Wait before next poll
                await asyncio.sleep(30)  # Poll every 30 seconds
                
        except Exception as e:
            logger.error(f"Error streaming data from MSSQL: {e}")
    
    async def _execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute SQL query asynchronously"""
        def _sync_execute():
            conn = pyodbc.connect(self._connection_string)
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Get column names
            columns = [column[0] for column in cursor.description]
            
            # Fetch all rows
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))
            
            conn.close()
            return result
        
        return await asyncio.get_event_loop().run_in_executor(None, _sync_execute)
    
    async def insert_data(self, data_points: List[MarketDataPoint]) -> bool:
        """Insert data points into MSSQL"""
        try:
            if not data_points:
                return True
            
            def _sync_insert():
                conn = pyodbc.connect(self._connection_string)
                cursor = conn.cursor()
                
                insert_query = """
                INSERT INTO market_data 
                (symbol, timestamp, price, volume, bid, ask, data_type, payload, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                for dp in data_points:
                    import json
                    payload_json = json.dumps(dp.payload)
                    
                    # Extract bid/ask from payload
                    bid = dp.payload.get('bid')
                    ask = dp.payload.get('ask')
                    
                    cursor.execute(insert_query, (
                        dp.symbol,
                        dp.timestamp,
                        dp.price,
                        dp.volume,
                        bid,
                        ask,
                        dp.data_type.value,
                        payload_json,
                        dp.source.value
                    ))
                
                conn.commit()
                conn.close()
            
            await asyncio.get_event_loop().run_in_executor(None, _sync_insert)
            logger.info(f"Inserted {len(data_points)} data points into MSSQL")
            return True
            
        except Exception as e:
            logger.error(f"Error inserting data into MSSQL: {e}")
            return False
