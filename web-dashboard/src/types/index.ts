export interface MarketDataPoint {
  symbol: string;
  timestamp: string;
  source: DataSourceType;
  dataType: string;
  price?: number;
  volume?: number;
  payload?: Record<string, any>;
  receivedAt?: string;
  processedAt?: string;
}

export interface AnomalyData {
  id: string;
  symbol: string;
  anomalyType: AnomalyType;
  severity: SeverityLevel;
  detectedAt: string;
  dataTimestamp: string;
  description: string;
  details: Record<string, any>;
  dataSource: DataSourceType;
  dataType: string;
  expectedValue?: number;
  actualValue?: number;
  threshold?: number;
  acknowledged: boolean;
  resolved: boolean;
  resolvedAt?: string;
}

export enum DataSourceType {
  GEMFIRE_CACHE = 'GEMFIRE_CACHE',
  EOD_DATA = 'EOD_DATA',
  MSSQL = 'MSSQL',
  HBASE = 'HBASE',
  REAL_TIME_FEED = 'REAL_TIME_FEED',
  HISTORICAL_DATA = 'HISTORICAL_DATA'
}

export enum AnomalyType {
  MISSING_DATA = 'MISSING_DATA',
  PRICE_MOVEMENT = 'PRICE_MOVEMENT',
  DATA_STALE = 'DATA_STALE',
  VOLUME_SPIKE = 'VOLUME_SPIKE',
  ML_DETECTED = 'ML_DETECTED',
  PRICE_ZSCORE = 'PRICE_ZSCORE',
  VOLUME_ZSCORE = 'VOLUME_ZSCORE'
}

export enum SeverityLevel {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

export interface SystemMetrics {
  totalAnomalies: number;
  criticalAnomalies: number;
  highAnomalies: number;
  mediumAnomalies: number;
  lowAnomalies: number;
  acknowledgedAnomalies: number;
  resolvedAnomalies: number;
  dataSourcesActive: number;
  messagesProcessed: number;
  processingLatency: number;
  systemHealth: 'healthy' | 'warning' | 'critical';
}

export interface ChartDataPoint {
  timestamp: string;
  value: number;
  anomaly?: boolean;
  severity?: SeverityLevel;
  symbol?: string;
}

export interface FilterOptions {
  symbols: string[];
  anomalyTypes: AnomalyType[];
  severityLevels: SeverityLevel[];
  dataSources: DataSourceType[];
  dateRange: [string, string];
  acknowledged?: boolean;
  resolved?: boolean;
}

export interface ServiceHealth {
  service: string;
  status: 'UP' | 'DOWN' | 'WARNING';
  timestamp: string;
  details?: Record<string, any>;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: string;
  total?: number;
  limit?: number;
  offset?: number;
}

export interface AnomalyListResponse {
  anomalies: AnomalyData[];
  total: number;
  limit: number;
  offset: number;
}

export interface WebSocketMessage {
  type: 'anomaly' | 'metrics' | 'health';
  data: any;
  timestamp: string;
}

export interface DashboardConfig {
  refreshInterval: number;
  maxDataPoints: number;
  defaultTimeRange: number; // hours
  enableRealTime: boolean;
  theme: 'light' | 'dark';
}

export interface AnomalyStats {
  symbol: string;
  count: number;
  lastAnomaly: string;
  severity: SeverityLevel;
  trend: 'increasing' | 'decreasing' | 'stable';
}

export interface TimeSeriesData {
  symbol: string;
  data: ChartDataPoint[];
  anomalies: AnomalyData[];
}

export interface AlertRule {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  conditions: {
    anomalyType: AnomalyType;
    severity: SeverityLevel;
    symbols?: string[];
    threshold?: number;
  };
  actions: {
    email?: boolean;
    webhook?: string;
    notification?: boolean;
  };
}

export interface UserPreferences {
  defaultSymbols: string[];
  defaultTimeRange: number;
  enableNotifications: boolean;
  theme: 'light' | 'dark';
  refreshInterval: number;
}

// Chart configuration types
export interface ChartConfig {
  type: 'line' | 'bar' | 'scatter' | 'area';
  title: string;
  xAxis: string;
  yAxis: string;
  color: string;
  showGrid: boolean;
  showLegend: boolean;
  height: number;
}

// Export utility types
export type AnomalySeverityColor = {
  [key in SeverityLevel]: string;
};

export type AnomalyTypeIcon = {
  [key in AnomalyType]: string;
};

export type DataSourceIcon = {
  [key in DataSourceType]: string;
};
