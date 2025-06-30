import axios, { AxiosResponse } from 'axios';
import {
  AnomalyData,
  AnomalyListResponse,
  SystemMetrics,
  ServiceHealth,
  FilterOptions,
  ApiResponse,
  MarketDataPoint,
  TimeSeriesData
} from '../types';

// API base configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for authentication
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export class AnomalyAPI {
  // Get anomalies with filtering
  static async getAnomalies(
    filters?: Partial<FilterOptions>,
    limit = 100,
    offset = 0
  ): Promise<AnomalyListResponse> {
    const params = new URLSearchParams();
    
    if (filters?.symbols?.length) {
      params.append('symbols', filters.symbols.join(','));
    }
    if (filters?.anomalyTypes?.length) {
      params.append('types', filters.anomalyTypes.join(','));
    }
    if (filters?.severityLevels?.length) {
      params.append('severity', filters.severityLevels.join(','));
    }
    if (filters?.dataSources?.length) {
      params.append('sources', filters.dataSources.join(','));
    }
    if (filters?.dateRange) {
      params.append('from', filters.dateRange[0]);
      params.append('to', filters.dateRange[1]);
    }
    if (filters?.acknowledged !== undefined) {
      params.append('acknowledged', filters.acknowledged.toString());
    }
    if (filters?.resolved !== undefined) {
      params.append('resolved', filters.resolved.toString());
    }
    
    params.append('limit', limit.toString());
    params.append('offset', offset.toString());

    const response: AxiosResponse<AnomalyListResponse> = await apiClient.get(
      `/anomalies?${params.toString()}`
    );
    return response.data;
  }

  // Get single anomaly details
  static async getAnomalyById(id: string): Promise<AnomalyData> {
    const response: AxiosResponse<AnomalyData> = await apiClient.get(`/anomalies/${id}`);
    return response.data;
  }

  // Acknowledge anomaly
  static async acknowledgeAnomaly(
    id: string,
    acknowledgedBy: string,
    notes?: string
  ): Promise<ApiResponse<any>> {
    const response: AxiosResponse<ApiResponse<any>> = await apiClient.post(
      `/anomalies/${id}/acknowledge`,
      { acknowledged_by: acknowledgedBy, notes }
    );
    return response.data;
  }

  // Resolve anomaly
  static async resolveAnomaly(
    id: string,
    resolvedBy: string,
    resolutionNotes?: string
  ): Promise<ApiResponse<any>> {
    const response: AxiosResponse<ApiResponse<any>> = await apiClient.post(
      `/anomalies/${id}/resolve`,
      { resolved_by: resolvedBy, resolution_notes: resolutionNotes }
    );
    return response.data;
  }

  // Get system metrics
  static async getSystemMetrics(): Promise<SystemMetrics> {
    const response: AxiosResponse<SystemMetrics> = await apiClient.get('/metrics');
    return response.data;
  }

  // Get service health
  static async getServiceHealth(): Promise<ServiceHealth[]> {
    const services = [
      'api-gateway',
      'data-ingestion-service',
      'stream-processing-service',
      'alert-service',
      'dashboard-api',
      'detection-engine'
    ];

    const healthChecks = await Promise.allSettled(
      services.map(async (service) => {
        try {
          const response = await axios.get(`http://localhost:${this.getServicePort(service)}/health`);
          return {
            service,
            status: 'UP' as const,
            timestamp: new Date().toISOString(),
            details: response.data
          };
        } catch (error) {
          return {
            service,
            status: 'DOWN' as const,
            timestamp: new Date().toISOString(),
            details: { error: error instanceof Error ? error.message : 'Unknown error' }
          };
        }
      })
    );

    return healthChecks.map((result, index) => 
      result.status === 'fulfilled' ? result.value : {
        service: services[index],
        status: 'DOWN' as const,
        timestamp: new Date().toISOString(),
        details: { error: 'Service unreachable' }
      }
    );
  }

  private static getServicePort(service: string): number {
    const portMap: Record<string, number> = {
      'api-gateway': 8080,
      'data-ingestion-service': 8081,
      'stream-processing-service': 8082,
      'alert-service': 8083,
      'dashboard-api': 8084,
      'detection-engine': 8085
    };
    return portMap[service] || 8080;
  }

  // Get time series data for charts
  static async getTimeSeriesData(
    symbol: string,
    from: string,
    to: string
  ): Promise<TimeSeriesData> {
    const response: AxiosResponse<TimeSeriesData> = await apiClient.get(
      `/timeseries/${symbol}?from=${from}&to=${to}`
    );
    return response.data;
  }

  // Ingest sample data (for testing)
  static async ingestSampleData(dataPoint: MarketDataPoint): Promise<ApiResponse<any>> {
    const response: AxiosResponse<ApiResponse<any>> = await apiClient.post(
      '/ingest',
      dataPoint
    );
    return response.data;
  }

  // Get available symbols
  static async getAvailableSymbols(): Promise<string[]> {
    const response: AxiosResponse<string[]> = await apiClient.get('/symbols');
    return response.data;
  }

  // Get anomaly statistics
  static async getAnomalyStats(
    timeRange: string = '24h'
  ): Promise<Record<string, any>> {
    const response: AxiosResponse<Record<string, any>> = await apiClient.get(
      `/stats/anomalies?range=${timeRange}`
    );
    return response.data;
  }
}

export class MockAPI {
  // Mock data for development
  static async getAnomalies(
    filters?: Partial<FilterOptions>,
    limit = 100,
    offset = 0
  ): Promise<AnomalyListResponse> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));

    const mockAnomalies: AnomalyData[] = [
      {
        id: 'anomaly-1',
        symbol: 'AAPL',
        anomalyType: 'PRICE_MOVEMENT' as any,
        severity: 'high' as any,
        detectedAt: new Date(Date.now() - 3600000).toISOString(),
        dataTimestamp: new Date(Date.now() - 3600000).toISOString(),
        description: 'Unusual price movement: 6.5% increase in 5 minutes',
        details: {
          priceChangePct: 6.5,
          threshold: 5.0,
          previousPrice: 150.25,
          currentPrice: 160.02
        },
        dataSource: 'EOD_DATA' as any,
        dataType: 'price',
        expectedValue: 150.25,
        actualValue: 160.02,
        threshold: 5.0,
        acknowledged: false,
        resolved: false
      },
      {
        id: 'anomaly-2',
        symbol: 'GOOGL',
        anomalyType: 'MISSING_DATA' as any,
        severity: 'critical' as any,
        detectedAt: new Date(Date.now() - 7200000).toISOString(),
        dataTimestamp: new Date(Date.now() - 7200000).toISOString(),
        description: 'Data gap detected: 45 minutes missing',
        details: {
          gapDurationMinutes: 45,
          expectedFrequencyMinutes: 5,
          lastDataTimestamp: new Date(Date.now() - 10800000).toISOString()
        },
        dataSource: 'GEMFIRE_CACHE' as any,
        dataType: 'price',
        acknowledged: true,
        resolved: false
      },
      {
        id: 'anomaly-3',
        symbol: 'MSFT',
        anomalyType: 'VOLUME_SPIKE' as any,
        severity: 'medium' as any,
        detectedAt: new Date(Date.now() - 1800000).toISOString(),
        dataTimestamp: new Date(Date.now() - 1800000).toISOString(),
        description: 'Volume spike detected: 300% above average',
        details: {
          volumeIncrease: 300,
          averageVolume: 1000000,
          currentVolume: 4000000
        },
        dataSource: 'EOD_DATA' as any,
        dataType: 'volume',
        acknowledged: false,
        resolved: false
      }
    ];

    return {
      anomalies: mockAnomalies.slice(offset, offset + limit),
      total: mockAnomalies.length,
      limit,
      offset
    };
  }

  static async getSystemMetrics(): Promise<SystemMetrics> {
    await new Promise(resolve => setTimeout(resolve, 300));

    return {
      totalAnomalies: 156,
      criticalAnomalies: 12,
      highAnomalies: 34,
      mediumAnomalies: 67,
      lowAnomalies: 43,
      acknowledgedAnomalies: 89,
      resolvedAnomalies: 134,
      dataSourcesActive: 4,
      messagesProcessed: 45678,
      processingLatency: 45,
      systemHealth: 'healthy'
    };
  }

  static async getServiceHealth(): Promise<ServiceHealth[]> {
    await new Promise(resolve => setTimeout(resolve, 200));

    return [
      {
        service: 'api-gateway',
        status: 'UP',
        timestamp: new Date().toISOString()
      },
      {
        service: 'data-ingestion-service',
        status: 'UP',
        timestamp: new Date().toISOString()
      },
      {
        service: 'stream-processing-service',
        status: 'UP',
        timestamp: new Date().toISOString()
      },
      {
        service: 'alert-service',
        status: 'WARNING',
        timestamp: new Date().toISOString(),
        details: { message: 'High memory usage' }
      },
      {
        service: 'dashboard-api',
        status: 'UP',
        timestamp: new Date().toISOString()
      },
      {
        service: 'detection-engine',
        status: 'UP',
        timestamp: new Date().toISOString()
      }
    ];
  }
}

// Use mock API in development, real API in production
export const API = process.env.NODE_ENV === 'development' ? MockAPI : AnomalyAPI;
