import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Tag, Button, Space, Progress, Descriptions, Alert } from 'antd';
import {
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  CloseCircleOutlined,
  ReloadOutlined,
  HeartOutlined,
  DatabaseOutlined,
  CloudServerOutlined,
  ApiOutlined
} from '@ant-design/icons';
import moment from 'moment';
import { API } from '../services/api';
import { ServiceHealth } from '../types';

const SystemHealth: React.FC = () => {
  const [services, setServices] = useState<ServiceHealth[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadServiceHealth();
  }, []);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(loadServiceHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadServiceHealth = async () => {
    setLoading(true);
    try {
      const healthData = await API.getServiceHealth();
      setServices(healthData);
    } catch (error) {
      console.error('Error loading service health:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'UP': return '#52c41a';
      case 'WARNING': return '#faad14';
      case 'DOWN': return '#ff4d4f';
      default: return '#d9d9d9';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'UP': return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'WARNING': return <ExclamationCircleOutlined style={{ color: '#faad14' }} />;
      case 'DOWN': return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />;
      default: return <HeartOutlined />;
    }
  };

  const getServiceIcon = (serviceName: string) => {
    if (serviceName.includes('api')) return <ApiOutlined />;
    if (serviceName.includes('data')) return <DatabaseOutlined />;
    return <CloudServerOutlined />;
  };

  const getServiceDisplayName = (serviceName: string) => {
    const nameMap: Record<string, string> = {
      'api-gateway': 'API Gateway',
      'data-ingestion-service': 'Data Ingestion',
      'stream-processing-service': 'Stream Processing',
      'alert-service': 'Alert Service',
      'dashboard-api': 'Dashboard API',
      'detection-engine': 'Detection Engine'
    };
    return nameMap[serviceName] || serviceName;
  };

  const getOverallHealth = () => {
    if (services.length === 0) return 'unknown';
    
    const downServices = services.filter(s => s.status === 'DOWN').length;
    const warningServices = services.filter(s => s.status === 'WARNING').length;
    
    if (downServices > 0) return 'critical';
    if (warningServices > 0) return 'warning';
    return 'healthy';
  };

  const getHealthPercentage = () => {
    if (services.length === 0) return 0;
    const upServices = services.filter(s => s.status === 'UP').length;
    return Math.round((upServices / services.length) * 100);
  };

  const overallHealth = getOverallHealth();
  const healthPercentage = getHealthPercentage();

  return (
    <div>
      {/* Overall System Health */}
      <Card
        title={
          <Space>
            <HeartOutlined />
            System Health Overview
            <Button
              icon={<ReloadOutlined />}
              onClick={loadServiceHealth}
              loading={loading}
              size="small"
            >
              Refresh
            </Button>
          </Space>
        }
        style={{ marginBottom: 24 }}
      >
        <Row gutter={[24, 24]}>
          <Col xs={24} sm={12} md={8}>
            <Card className="metric-card">
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '48px', marginBottom: '16px' }}>
                  {getStatusIcon(overallHealth === 'healthy' ? 'UP' : 
                                overallHealth === 'warning' ? 'WARNING' : 'DOWN')}
                </div>
                <h3>Overall Status</h3>
                <Tag 
                  color={getStatusColor(overallHealth === 'healthy' ? 'UP' : 
                                      overallHealth === 'warning' ? 'WARNING' : 'DOWN')}
                  style={{ fontSize: '16px', padding: '4px 12px' }}
                >
                  {overallHealth.toUpperCase()}
                </Tag>
              </div>
            </Card>
          </Col>
          
          <Col xs={24} sm={12} md={8}>
            <Card className="metric-card">
              <div style={{ textAlign: 'center' }}>
                <Progress
                  type="circle"
                  percent={healthPercentage}
                  strokeColor={healthPercentage >= 80 ? '#52c41a' : 
                              healthPercentage >= 60 ? '#faad14' : '#ff4d4f'}
                  size={120}
                />
                <h3 style={{ marginTop: '16px' }}>Service Availability</h3>
                <p>{services.filter(s => s.status === 'UP').length} of {services.length} services running</p>
              </div>
            </Card>
          </Col>
          
          <Col xs={24} sm={12} md={8}>
            <Card className="metric-card">
              <Descriptions column={1} size="small">
                <Descriptions.Item label="Total Services">{services.length}</Descriptions.Item>
                <Descriptions.Item label="Healthy">
                  <span style={{ color: '#52c41a' }}>
                    {services.filter(s => s.status === 'UP').length}
                  </span>
                </Descriptions.Item>
                <Descriptions.Item label="Warning">
                  <span style={{ color: '#faad14' }}>
                    {services.filter(s => s.status === 'WARNING').length}
                  </span>
                </Descriptions.Item>
                <Descriptions.Item label="Down">
                  <span style={{ color: '#ff4d4f' }}>
                    {services.filter(s => s.status === 'DOWN').length}
                  </span>
                </Descriptions.Item>
                <Descriptions.Item label="Last Updated">
                  {moment().format('HH:mm:ss')}
                </Descriptions.Item>
              </Descriptions>
            </Card>
          </Col>
        </Row>
      </Card>

      {/* Service Status Cards */}
      <Row gutter={[24, 24]}>
        {services.map((service) => (
          <Col xs={24} sm={12} md={8} lg={6} key={service.service}>
            <Card
              className="metric-card"
              style={{
                borderLeft: `4px solid ${getStatusColor(service.status)}`,
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                    {getServiceIcon(service.service)}
                    <strong>{getServiceDisplayName(service.service)}</strong>
                  </div>
                  
                  <div style={{ marginBottom: '8px' }}>
                    <Tag color={getStatusColor(service.status)}>
                      {getStatusIcon(service.status)}
                      <span style={{ marginLeft: '4px' }}>{service.status}</span>
                    </Tag>
                  </div>
                  
                  <div style={{ fontSize: '12px', color: '#8c8c8c' }}>
                    Last check: {moment(service.timestamp).format('HH:mm:ss')}
                  </div>
                  
                  {service.details && (
                    <div style={{ marginTop: '8px', fontSize: '12px' }}>
                      {service.details.message && (
                        <div style={{ color: service.status === 'WARNING' ? '#faad14' : '#ff4d4f' }}>
                          {service.details.message}
                        </div>
                      )}
                      {service.details.error && (
                        <div style={{ color: '#ff4d4f' }}>
                          Error: {service.details.error}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      {/* System Alerts */}
      {services.some(s => s.status === 'DOWN') && (
        <Alert
          message="Critical Services Down"
          description={
            <div>
              The following services are currently down:
              <ul style={{ marginTop: '8px', marginBottom: 0 }}>
                {services
                  .filter(s => s.status === 'DOWN')
                  .map(s => (
                    <li key={s.service}>{getServiceDisplayName(s.service)}</li>
                  ))}
              </ul>
            </div>
          }
          type="error"
          showIcon
          style={{ marginTop: 24 }}
        />
      )}

      {services.some(s => s.status === 'WARNING') && !services.some(s => s.status === 'DOWN') && (
        <Alert
          message="Service Warnings"
          description={
            <div>
              The following services have warnings:
              <ul style={{ marginTop: '8px', marginBottom: 0 }}>
                {services
                  .filter(s => s.status === 'WARNING')
                  .map(s => (
                    <li key={s.service}>
                      {getServiceDisplayName(s.service)}
                      {s.details?.message && `: ${s.details.message}`}
                    </li>
                  ))}
              </ul>
            </div>
          }
          type="warning"
          showIcon
          style={{ marginTop: 24 }}
        />
      )}

      {services.every(s => s.status === 'UP') && services.length > 0 && (
        <Alert
          message="All Systems Operational"
          description="All services are running normally."
          type="success"
          showIcon
          style={{ marginTop: 24 }}
        />
      )}
    </div>
  );
};

export default SystemHealth;
