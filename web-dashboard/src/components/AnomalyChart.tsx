import React, { useMemo } from 'react';
import { Card, Select, Row, Col } from 'antd';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter
} from 'recharts';
import { BarChartOutlined } from '@ant-design/icons';
import moment from 'moment';
import { AnomalyData, SeverityLevel } from '../types';

const { Option } = Select;

interface AnomalyChartProps {
  anomalies: AnomalyData[];
  loading: boolean;
}

const AnomalyChart: React.FC<AnomalyChartProps> = ({ anomalies, loading }) => {
  const [chartType, setChartType] = React.useState<'timeline' | 'severity' | 'symbols' | 'types'>('timeline');

  // Process data for timeline chart
  const timelineData = useMemo(() => {
    const hourlyData: Record<string, any> = {};
    
    anomalies.forEach(anomaly => {
      const hour = moment(anomaly.detectedAt).format('YYYY-MM-DD HH:00');
      if (!hourlyData[hour]) {
        hourlyData[hour] = {
          time: hour,
          total: 0,
          critical: 0,
          high: 0,
          medium: 0,
          low: 0
        };
      }
      
      hourlyData[hour].total++;
      hourlyData[hour][anomaly.severity]++;
    });

    return Object.values(hourlyData).sort((a: any, b: any) => 
      moment(a.time).valueOf() - moment(b.time).valueOf()
    );
  }, [anomalies]);

  // Process data for severity distribution
  const severityData = useMemo(() => {
    const severityCount: Record<SeverityLevel, number> = {
      critical: 0,
      high: 0,
      medium: 0,
      low: 0
    };

    anomalies.forEach(anomaly => {
      severityCount[anomaly.severity]++;
    });

    return Object.entries(severityCount).map(([severity, count]) => ({
      severity: severity.charAt(0).toUpperCase() + severity.slice(1),
      count,
      percentage: anomalies.length > 0 ? Math.round((count / anomalies.length) * 100) : 0
    }));
  }, [anomalies]);

  // Process data for symbol distribution
  const symbolData = useMemo(() => {
    const symbolCount: Record<string, number> = {};
    
    anomalies.forEach(anomaly => {
      symbolCount[anomaly.symbol] = (symbolCount[anomaly.symbol] || 0) + 1;
    });

    return Object.entries(symbolCount)
      .map(([symbol, count]) => ({ symbol, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10); // Top 10 symbols
  }, [anomalies]);

  // Process data for anomaly types
  const typeData = useMemo(() => {
    const typeCount: Record<string, number> = {};
    
    anomalies.forEach(anomaly => {
      const type = anomaly.anomalyType.replace('_', ' ');
      typeCount[type] = (typeCount[type] || 0) + 1;
    });

    return Object.entries(typeCount).map(([type, count]) => ({
      type,
      count,
      percentage: anomalies.length > 0 ? Math.round((count / anomalies.length) * 100) : 0
    }));
  }, [anomalies]);

  const severityColors = {
    Critical: '#ff4d4f',
    High: '#ff7a45',
    Medium: '#ffa940',
    Low: '#52c41a'
  };

  const typeColors = ['#1890ff', '#52c41a', '#faad14', '#f759ab', '#13c2c2', '#722ed1'];

  const formatTooltipTime = (value: string) => {
    return moment(value).format('MMM DD, HH:mm');
  };

  const renderChart = () => {
    switch (chartType) {
      case 'timeline':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={timelineData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="time" 
                tickFormatter={(value) => moment(value).format('MM/DD HH:mm')}
              />
              <YAxis />
              <Tooltip 
                labelFormatter={formatTooltipTime}
                formatter={(value: number, name: string) => [value, name.charAt(0).toUpperCase() + name.slice(1)]}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="total" 
                stroke="#1890ff" 
                strokeWidth={2}
                name="Total"
              />
              <Line 
                type="monotone" 
                dataKey="critical" 
                stroke="#ff4d4f" 
                strokeWidth={2}
                name="Critical"
              />
              <Line 
                type="monotone" 
                dataKey="high" 
                stroke="#ff7a45" 
                strokeWidth={2}
                name="High"
              />
              <Line 
                type="monotone" 
                dataKey="medium" 
                stroke="#ffa940" 
                strokeWidth={2}
                name="Medium"
              />
              <Line 
                type="monotone" 
                dataKey="low" 
                stroke="#52c41a" 
                strokeWidth={2}
                name="Low"
              />
            </LineChart>
          </ResponsiveContainer>
        );

      case 'severity':
        return (
          <Row gutter={24}>
            <Col span={12}>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={severityData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ severity, percentage }) => `${severity}: ${percentage}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="count"
                  >
                    {severityData.map((entry, index) => (
                      <Cell 
                        key={`cell-${index}`} 
                        fill={severityColors[entry.severity as keyof typeof severityColors]} 
                      />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Col>
            <Col span={12}>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={severityData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="severity" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#1890ff" />
                </BarChart>
              </ResponsiveContainer>
            </Col>
          </Row>
        );

      case 'symbols':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={symbolData} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="symbol" type="category" width={80} />
              <Tooltip />
              <Bar dataKey="count" fill="#1890ff" />
            </BarChart>
          </ResponsiveContainer>
        );

      case 'types':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <PieChart>
              <Pie
                data={typeData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ type, percentage }) => `${type}: ${percentage}%`}
                outerRadius={120}
                fill="#8884d8"
                dataKey="count"
              >
                {typeData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={typeColors[index % typeColors.length]} 
                  />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        );

      default:
        return null;
    }
  };

  return (
    <Card
      title={
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>
            <BarChartOutlined style={{ marginRight: 8 }} />
            Anomaly Analytics
          </span>
          <Select
            value={chartType}
            onChange={setChartType}
            style={{ width: 200 }}
          >
            <Option value="timeline">Timeline View</Option>
            <Option value="severity">Severity Distribution</Option>
            <Option value="symbols">Top Symbols</Option>
            <Option value="types">Anomaly Types</Option>
          </Select>
        </div>
      }
      className="chart-container"
      loading={loading}
    >
      {renderChart()}
    </Card>
  );
};

export default AnomalyChart;
