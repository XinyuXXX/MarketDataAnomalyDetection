import React from 'react';
import { Card, Row, Col, Select, DatePicker, Switch, Button, Space } from 'antd';
import { FilterOutlined, ClearOutlined } from '@ant-design/icons';
import moment from 'moment';
import { FilterOptions, AnomalyType, SeverityLevel, DataSourceType } from '../types';

const { RangePicker } = DatePicker;
const { Option } = Select;

interface FilterPanelProps {
  filters: Partial<FilterOptions>;
  onFilterChange: (filters: Partial<FilterOptions>) => void;
  loading: boolean;
}

const FilterPanel: React.FC<FilterPanelProps> = ({ filters, onFilterChange, loading }) => {
  const handleSymbolChange = (symbols: string[]) => {
    onFilterChange({ ...filters, symbols });
  };

  const handleAnomalyTypeChange = (anomalyTypes: AnomalyType[]) => {
    onFilterChange({ ...filters, anomalyTypes });
  };

  const handleSeverityChange = (severityLevels: SeverityLevel[]) => {
    onFilterChange({ ...filters, severityLevels });
  };

  const handleDataSourceChange = (dataSources: DataSourceType[]) => {
    onFilterChange({ ...filters, dataSources });
  };

  const handleDateRangeChange = (dates: any) => {
    if (dates && dates.length === 2) {
      onFilterChange({
        ...filters,
        dateRange: [dates[0].toISOString(), dates[1].toISOString()]
      });
    }
  };

  const handleAcknowledgedChange = (acknowledged: boolean) => {
    onFilterChange({ ...filters, acknowledged });
  };

  const handleResolvedChange = (resolved: boolean) => {
    onFilterChange({ ...filters, resolved });
  };

  const handleClearFilters = () => {
    onFilterChange({
      dateRange: [
        moment().subtract(24, 'hours').toISOString(),
        moment().toISOString()
      ]
    });
  };

  const handleQuickDateRange = (hours: number) => {
    onFilterChange({
      ...filters,
      dateRange: [
        moment().subtract(hours, 'hours').toISOString(),
        moment().toISOString()
      ]
    });
  };

  const commonSymbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'META', 'NVDA', 'NFLX'];

  return (
    <Card
      title={
        <Space>
          <FilterOutlined />
          Filters
        </Space>
      }
      className="filter-panel"
      extra={
        <Button
          icon={<ClearOutlined />}
          onClick={handleClearFilters}
          size="small"
        >
          Clear All
        </Button>
      }
    >
      <Row gutter={[16, 16]}>
        {/* Date Range */}
        <Col xs={24} sm={12} md={8} lg={6}>
          <div style={{ marginBottom: 8 }}>
            <strong>Time Range</strong>
          </div>
          <RangePicker
            value={
              filters.dateRange
                ? [moment(filters.dateRange[0]), moment(filters.dateRange[1])]
                : undefined
            }
            onChange={handleDateRangeChange}
            showTime
            format="YYYY-MM-DD HH:mm"
            style={{ width: '100%' }}
          />
          <div style={{ marginTop: 8 }}>
            <Space wrap>
              <Button size="small" onClick={() => handleQuickDateRange(1)}>
                1h
              </Button>
              <Button size="small" onClick={() => handleQuickDateRange(6)}>
                6h
              </Button>
              <Button size="small" onClick={() => handleQuickDateRange(24)}>
                24h
              </Button>
              <Button size="small" onClick={() => handleQuickDateRange(168)}>
                7d
              </Button>
            </Space>
          </div>
        </Col>

        {/* Symbols */}
        <Col xs={24} sm={12} md={8} lg={6}>
          <div style={{ marginBottom: 8 }}>
            <strong>Symbols</strong>
          </div>
          <Select
            mode="multiple"
            placeholder="Select symbols"
            value={filters.symbols}
            onChange={handleSymbolChange}
            style={{ width: '100%' }}
            maxTagCount={2}
          >
            {commonSymbols.map(symbol => (
              <Option key={symbol} value={symbol}>
                {symbol}
              </Option>
            ))}
          </Select>
        </Col>

        {/* Anomaly Types */}
        <Col xs={24} sm={12} md={8} lg={6}>
          <div style={{ marginBottom: 8 }}>
            <strong>Anomaly Types</strong>
          </div>
          <Select
            mode="multiple"
            placeholder="Select types"
            value={filters.anomalyTypes}
            onChange={handleAnomalyTypeChange}
            style={{ width: '100%' }}
            maxTagCount={2}
          >
            <Option value={AnomalyType.MISSING_DATA}>Missing Data</Option>
            <Option value={AnomalyType.PRICE_MOVEMENT}>Price Movement</Option>
            <Option value={AnomalyType.DATA_STALE}>Data Stale</Option>
            <Option value={AnomalyType.VOLUME_SPIKE}>Volume Spike</Option>
            <Option value={AnomalyType.ML_DETECTED}>ML Detected</Option>
            <Option value={AnomalyType.PRICE_ZSCORE}>Price Z-Score</Option>
            <Option value={AnomalyType.VOLUME_ZSCORE}>Volume Z-Score</Option>
          </Select>
        </Col>

        {/* Severity Levels */}
        <Col xs={24} sm={12} md={8} lg={6}>
          <div style={{ marginBottom: 8 }}>
            <strong>Severity</strong>
          </div>
          <Select
            mode="multiple"
            placeholder="Select severity"
            value={filters.severityLevels}
            onChange={handleSeverityChange}
            style={{ width: '100%' }}
            maxTagCount={2}
          >
            <Option value={SeverityLevel.CRITICAL}>
              <span style={{ color: '#ff4d4f' }}>Critical</span>
            </Option>
            <Option value={SeverityLevel.HIGH}>
              <span style={{ color: '#ff7a45' }}>High</span>
            </Option>
            <Option value={SeverityLevel.MEDIUM}>
              <span style={{ color: '#ffa940' }}>Medium</span>
            </Option>
            <Option value={SeverityLevel.LOW}>
              <span style={{ color: '#52c41a' }}>Low</span>
            </Option>
          </Select>
        </Col>

        {/* Data Sources */}
        <Col xs={24} sm={12} md={8} lg={6}>
          <div style={{ marginBottom: 8 }}>
            <strong>Data Sources</strong>
          </div>
          <Select
            mode="multiple"
            placeholder="Select sources"
            value={filters.dataSources}
            onChange={handleDataSourceChange}
            style={{ width: '100%' }}
            maxTagCount={2}
          >
            <Option value={DataSourceType.EOD_DATA}>EOD Data</Option>
            <Option value={DataSourceType.GEMFIRE_CACHE}>Gemfire Cache</Option>
            <Option value={DataSourceType.MSSQL}>MS SQL Server</Option>
            <Option value={DataSourceType.HBASE}>HBase</Option>
            <Option value={DataSourceType.REAL_TIME_FEED}>Real-time Feed</Option>
            <Option value={DataSourceType.HISTORICAL_DATA}>Historical Data</Option>
          </Select>
        </Col>

        {/* Status Filters */}
        <Col xs={24} sm={12} md={8} lg={6}>
          <div style={{ marginBottom: 8 }}>
            <strong>Status</strong>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>Show Acknowledged</span>
              <Switch
                checked={filters.acknowledged}
                onChange={handleAcknowledgedChange}
                size="small"
              />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>Show Resolved</span>
              <Switch
                checked={filters.resolved}
                onChange={handleResolvedChange}
                size="small"
              />
            </div>
          </div>
        </Col>
      </Row>
    </Card>
  );
};

export default FilterPanel;
