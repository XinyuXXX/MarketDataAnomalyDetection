import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Statistic, Table, Tag, Button, Space, DatePicker, Select, Input, message } from 'antd';
import {
  AlertOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  ClockCircleOutlined,
  ReloadOutlined,
  EyeOutlined
} from '@ant-design/icons';
import { Link } from 'react-router-dom';
import moment from 'moment';
import AnomalyChart from './AnomalyChart';
import MetricsOverview from './MetricsOverview';
import FilterPanel from './FilterPanel';
import { API } from '../services/api';
import { AnomalyData, SystemMetrics, FilterOptions, SeverityLevel, AnomalyType } from '../types';

const { RangePicker } = DatePicker;
const { Option } = Select;
const { Search } = Input;

const Dashboard: React.FC = () => {
  const [anomalies, setAnomalies] = useState<AnomalyData[]>([]);
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState<Partial<FilterOptions>>({
    dateRange: [
      moment().subtract(24, 'hours').toISOString(),
      moment().toISOString()
    ]
  });
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  });

  // Load data
  const loadData = async () => {
    setLoading(true);
    try {
      const [anomaliesResponse, metricsResponse] = await Promise.all([
        API.getAnomalies(filters, pagination.pageSize, (pagination.current - 1) * pagination.pageSize),
        API.getSystemMetrics()
      ]);

      setAnomalies(anomaliesResponse.anomalies);
      setPagination(prev => ({
        ...prev,
        total: anomaliesResponse.total
      }));
      setMetrics(metricsResponse);
    } catch (error) {
      message.error('Failed to load data');
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [filters, pagination.current, pagination.pageSize]);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, [filters, pagination.current, pagination.pageSize]);

  const handleFilterChange = (newFilters: Partial<FilterOptions>) => {
    setFilters(newFilters);
    setPagination(prev => ({ ...prev, current: 1 }));
  };

  const handleTableChange = (paginationInfo: any) => {
    setPagination({
      current: paginationInfo.current,
      pageSize: paginationInfo.pageSize,
      total: pagination.total
    });
  };

  const getSeverityColor = (severity: SeverityLevel): string => {
    const colors = {
      critical: '#ff4d4f',
      high: '#ff7a45',
      medium: '#ffa940',
      low: '#52c41a'
    };
    return colors[severity] || '#d9d9d9';
  };

  const getAnomalyTypeIcon = (type: AnomalyType) => {
    const icons = {
      MISSING_DATA: <ClockCircleOutlined />,
      PRICE_MOVEMENT: <AlertOutlined />,
      DATA_STALE: <ExclamationCircleOutlined />,
      VOLUME_SPIKE: <AlertOutlined />,
      ML_DETECTED: <AlertOutlined />,
      PRICE_ZSCORE: <AlertOutlined />,
      VOLUME_ZSCORE: <AlertOutlined />
    };
    return icons[type] || <AlertOutlined />;
  };

  const columns = [
    {
      title: 'Symbol',
      dataIndex: 'symbol',
      key: 'symbol',
      width: 100,
      render: (symbol: string) => <strong>{symbol}</strong>
    },
    {
      title: 'Type',
      dataIndex: 'anomalyType',
      key: 'anomalyType',
      width: 150,
      render: (type: AnomalyType) => (
        <Space>
          {getAnomalyTypeIcon(type)}
          {type.replace('_', ' ')}
        </Space>
      )
    },
    {
      title: 'Severity',
      dataIndex: 'severity',
      key: 'severity',
      width: 100,
      render: (severity: SeverityLevel) => (
        <Tag color={getSeverityColor(severity)}>
          {severity.toUpperCase()}
        </Tag>
      )
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true
    },
    {
      title: 'Detected At',
      dataIndex: 'detectedAt',
      key: 'detectedAt',
      width: 180,
      render: (date: string) => moment(date).format('YYYY-MM-DD HH:mm:ss')
    },
    {
      title: 'Status',
      key: 'status',
      width: 120,
      render: (record: AnomalyData) => {
        if (record.resolved) {
          return <Tag color="green"><CheckCircleOutlined /> Resolved</Tag>;
        }
        if (record.acknowledged) {
          return <Tag color="orange"><ExclamationCircleOutlined /> Acknowledged</Tag>;
        }
        return <Tag color="red"><AlertOutlined /> New</Tag>;
      }
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 100,
      render: (record: AnomalyData) => (
        <Link to={`/anomaly/${record.id}`}>
          <Button type="link" icon={<EyeOutlined />} size="small">
            View
          </Button>
        </Link>
      )
    }
  ];

  return (
    <div>
      {/* Metrics Overview */}
      <MetricsOverview metrics={metrics} loading={loading} />

      {/* Filter Panel */}
      <FilterPanel
        filters={filters}
        onFilterChange={handleFilterChange}
        loading={loading}
      />

      {/* Charts */}
      <Row gutter={[24, 24]} style={{ marginBottom: 24 }}>
        <Col span={24}>
          <AnomalyChart anomalies={anomalies} loading={loading} />
        </Col>
      </Row>

      {/* Anomalies Table */}
      <Card
        title={
          <Space>
            <AlertOutlined />
            Recent Anomalies
            <Button
              icon={<ReloadOutlined />}
              onClick={loadData}
              loading={loading}
              size="small"
            >
              Refresh
            </Button>
          </Space>
        }
        className="chart-container"
      >
        <Table
          columns={columns}
          dataSource={anomalies}
          rowKey="id"
          loading={loading}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) =>
              `${range[0]}-${range[1]} of ${total} anomalies`,
          }}
          onChange={handleTableChange}
          scroll={{ x: 1000 }}
          className="responsive-table"
        />
      </Card>
    </div>
  );
};

export default Dashboard;
