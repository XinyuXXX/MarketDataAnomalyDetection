import React from 'react';
import { Row, Col, Card, Statistic, Progress, Tag } from 'antd';
import {
  AlertOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  ClockCircleOutlined,
  DatabaseOutlined,
  ThunderboltOutlined,
  HeartOutlined
} from '@ant-design/icons';
import { SystemMetrics } from '../types';

interface MetricsOverviewProps {
  metrics: SystemMetrics | null;
  loading: boolean;
}

const MetricsOverview: React.FC<MetricsOverviewProps> = ({ metrics, loading }) => {
  if (!metrics) {
    return null;
  }

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'healthy': return '#52c41a';
      case 'warning': return '#faad14';
      case 'critical': return '#ff4d4f';
      default: return '#d9d9d9';
    }
  };

  const getHealthIcon = (health: string) => {
    switch (health) {
      case 'healthy': return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'warning': return <ExclamationCircleOutlined style={{ color: '#faad14' }} />;
      case 'critical': return <AlertOutlined style={{ color: '#ff4d4f' }} />;
      default: return <HeartOutlined />;
    }
  };

  const resolvedPercentage = metrics.totalAnomalies > 0 
    ? Math.round((metrics.resolvedAnomalies / metrics.totalAnomalies) * 100)
    : 0;

  const acknowledgedPercentage = metrics.totalAnomalies > 0
    ? Math.round((metrics.acknowledgedAnomalies / metrics.totalAnomalies) * 100)
    : 0;

  return (
    <Row gutter={[24, 24]} style={{ marginBottom: 24 }}>
      {/* Total Anomalies */}
      <Col xs={24} sm={12} md={8} lg={6}>
        <Card className="metric-card">
          <Statistic
            title="Total Anomalies"
            value={metrics.totalAnomalies}
            prefix={<AlertOutlined />}
            valueStyle={{ color: '#1890ff' }}
          />
        </Card>
      </Col>

      {/* Critical Anomalies */}
      <Col xs={24} sm={12} md={8} lg={6}>
        <Card className="metric-card">
          <Statistic
            title="Critical"
            value={metrics.criticalAnomalies}
            prefix={<ExclamationCircleOutlined />}
            valueStyle={{ color: '#ff4d4f' }}
          />
        </Card>
      </Col>

      {/* High Anomalies */}
      <Col xs={24} sm={12} md={8} lg={6}>
        <Card className="metric-card">
          <Statistic
            title="High Priority"
            value={metrics.highAnomalies}
            prefix={<AlertOutlined />}
            valueStyle={{ color: '#ff7a45' }}
          />
        </Card>
      </Col>

      {/* Medium Anomalies */}
      <Col xs={24} sm={12} md={8} lg={6}>
        <Card className="metric-card">
          <Statistic
            title="Medium Priority"
            value={metrics.mediumAnomalies}
            prefix={<ClockCircleOutlined />}
            valueStyle={{ color: '#ffa940' }}
          />
        </Card>
      </Col>

      {/* Resolution Rate */}
      <Col xs={24} sm={12} md={8} lg={6}>
        <Card className="metric-card">
          <Statistic
            title="Resolution Rate"
            value={resolvedPercentage}
            suffix="%"
            prefix={<CheckCircleOutlined />}
            valueStyle={{ color: '#52c41a' }}
          />
          <Progress
            percent={resolvedPercentage}
            showInfo={false}
            strokeColor="#52c41a"
            size="small"
            style={{ marginTop: 8 }}
          />
        </Card>
      </Col>

      {/* Acknowledgment Rate */}
      <Col xs={24} sm={12} md={8} lg={6}>
        <Card className="metric-card">
          <Statistic
            title="Acknowledged"
            value={acknowledgedPercentage}
            suffix="%"
            prefix={<ExclamationCircleOutlined />}
            valueStyle={{ color: '#faad14' }}
          />
          <Progress
            percent={acknowledgedPercentage}
            showInfo={false}
            strokeColor="#faad14"
            size="small"
            style={{ marginTop: 8 }}
          />
        </Card>
      </Col>

      {/* Data Sources */}
      <Col xs={24} sm={12} md={8} lg={6}>
        <Card className="metric-card">
          <Statistic
            title="Active Sources"
            value={metrics.dataSourcesActive}
            prefix={<DatabaseOutlined />}
            valueStyle={{ color: '#722ed1' }}
          />
        </Card>
      </Col>

      {/* System Health */}
      <Col xs={24} sm={12} md={8} lg={6}>
        <Card className="metric-card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <div style={{ fontSize: '14px', color: '#8c8c8c', marginBottom: '4px' }}>
                System Health
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                {getHealthIcon(metrics.systemHealth)}
                <Tag color={getHealthColor(metrics.systemHealth)}>
                  {metrics.systemHealth.toUpperCase()}
                </Tag>
              </div>
            </div>
          </div>
        </Card>
      </Col>

      {/* Processing Stats */}
      <Col xs={24} sm={12} md={12} lg={12}>
        <Card className="metric-card">
          <Row gutter={16}>
            <Col span={12}>
              <Statistic
                title="Messages Processed"
                value={metrics.messagesProcessed}
                prefix={<ThunderboltOutlined />}
                valueStyle={{ color: '#13c2c2' }}
              />
            </Col>
            <Col span={12}>
              <Statistic
                title="Avg Latency"
                value={metrics.processingLatency}
                suffix="ms"
                prefix={<ClockCircleOutlined />}
                valueStyle={{ 
                  color: metrics.processingLatency > 100 ? '#ff4d4f' : '#52c41a' 
                }}
              />
            </Col>
          </Row>
        </Card>
      </Col>

      {/* Severity Distribution */}
      <Col xs={24} sm={12} md={12} lg={12}>
        <Card className="metric-card" title="Severity Distribution">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>Critical</span>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Progress
                  percent={metrics.totalAnomalies > 0 ? (metrics.criticalAnomalies / metrics.totalAnomalies) * 100 : 0}
                  showInfo={false}
                  strokeColor="#ff4d4f"
                  size="small"
                  style={{ width: '100px' }}
                />
                <span style={{ minWidth: '30px', textAlign: 'right' }}>
                  {metrics.criticalAnomalies}
                </span>
              </div>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>High</span>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Progress
                  percent={metrics.totalAnomalies > 0 ? (metrics.highAnomalies / metrics.totalAnomalies) * 100 : 0}
                  showInfo={false}
                  strokeColor="#ff7a45"
                  size="small"
                  style={{ width: '100px' }}
                />
                <span style={{ minWidth: '30px', textAlign: 'right' }}>
                  {metrics.highAnomalies}
                </span>
              </div>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>Medium</span>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Progress
                  percent={metrics.totalAnomalies > 0 ? (metrics.mediumAnomalies / metrics.totalAnomalies) * 100 : 0}
                  showInfo={false}
                  strokeColor="#ffa940"
                  size="small"
                  style={{ width: '100px' }}
                />
                <span style={{ minWidth: '30px', textAlign: 'right' }}>
                  {metrics.mediumAnomalies}
                </span>
              </div>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>Low</span>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Progress
                  percent={metrics.totalAnomalies > 0 ? (metrics.lowAnomalies / metrics.totalAnomalies) * 100 : 0}
                  showInfo={false}
                  strokeColor="#52c41a"
                  size="small"
                  style={{ width: '100px' }}
                />
                <span style={{ minWidth: '30px', textAlign: 'right' }}>
                  {metrics.lowAnomalies}
                </span>
              </div>
            </div>
          </div>
        </Card>
      </Col>
    </Row>
  );
};

export default MetricsOverview;
