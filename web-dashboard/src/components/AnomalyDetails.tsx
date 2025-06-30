import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card,
  Descriptions,
  Tag,
  Button,
  Space,
  Modal,
  Input,
  message,
  Spin,
  Alert,
  Timeline,
  Divider
} from 'antd';
import {
  ArrowLeftOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  AlertOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';
import moment from 'moment';
import { API } from '../services/api';
import { AnomalyData, SeverityLevel, AnomalyType } from '../types';

const { TextArea } = Input;

const AnomalyDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [anomaly, setAnomaly] = useState<AnomalyData | null>(null);
  const [loading, setLoading] = useState(true);
  const [acknowledgeModalVisible, setAcknowledgeModalVisible] = useState(false);
  const [resolveModalVisible, setResolveModalVisible] = useState(false);
  const [notes, setNotes] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    if (id) {
      loadAnomalyDetails(id);
    }
  }, [id]);

  const loadAnomalyDetails = async (anomalyId: string) => {
    setLoading(true);
    try {
      const data = await API.getAnomalyById(anomalyId);
      setAnomaly(data);
    } catch (error) {
      message.error('Failed to load anomaly details');
      console.error('Error loading anomaly details:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAcknowledge = async () => {
    if (!anomaly) return;

    setActionLoading(true);
    try {
      await API.acknowledgeAnomaly(anomaly.id, 'current-user', notes);
      message.success('Anomaly acknowledged successfully');
      setAcknowledgeModalVisible(false);
      setNotes('');
      // Reload data
      await loadAnomalyDetails(anomaly.id);
    } catch (error) {
      message.error('Failed to acknowledge anomaly');
      console.error('Error acknowledging anomaly:', error);
    } finally {
      setActionLoading(false);
    }
  };

  const handleResolve = async () => {
    if (!anomaly) return;

    setActionLoading(true);
    try {
      await API.resolveAnomaly(anomaly.id, 'current-user', notes);
      message.success('Anomaly resolved successfully');
      setResolveModalVisible(false);
      setNotes('');
      // Reload data
      await loadAnomalyDetails(anomaly.id);
    } catch (error) {
      message.error('Failed to resolve anomaly');
      console.error('Error resolving anomaly:', error);
    } finally {
      setActionLoading(false);
    }
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

  if (loading) {
    return (
      <div className="loading-container">
        <Spin size="large" />
      </div>
    );
  }

  if (!anomaly) {
    return (
      <Alert
        message="Anomaly Not Found"
        description="The requested anomaly could not be found."
        type="error"
        showIcon
        action={
          <Button onClick={() => navigate('/')}>
            Back to Dashboard
          </Button>
        }
      />
    );
  }

  return (
    <div>
      {/* Header */}
      <Card style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <Button
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate('/')}
            >
              Back to Dashboard
            </Button>
            <div>
              <h2 style={{ margin: 0 }}>
                {getAnomalyTypeIcon(anomaly.anomalyType)}
                <span style={{ marginLeft: 8 }}>
                  {anomaly.symbol} - {anomaly.anomalyType.replace('_', ' ')}
                </span>
              </h2>
              <Tag color={getSeverityColor(anomaly.severity)} style={{ marginTop: 8 }}>
                {anomaly.severity.toUpperCase()}
              </Tag>
            </div>
          </div>
          
          <Space>
            {!anomaly.acknowledged && (
              <Button
                type="primary"
                icon={<ExclamationCircleOutlined />}
                onClick={() => setAcknowledgeModalVisible(true)}
              >
                Acknowledge
              </Button>
            )}
            {!anomaly.resolved && (
              <Button
                type="primary"
                icon={<CheckCircleOutlined />}
                onClick={() => setResolveModalVisible(true)}
                style={{ backgroundColor: '#52c41a', borderColor: '#52c41a' }}
              >
                Resolve
              </Button>
            )}
          </Space>
        </div>
      </Card>

      {/* Anomaly Details */}
      <Card title="Anomaly Information" style={{ marginBottom: 24 }}>
        <Descriptions bordered column={2}>
          <Descriptions.Item label="ID">{anomaly.id}</Descriptions.Item>
          <Descriptions.Item label="Symbol">{anomaly.symbol}</Descriptions.Item>
          <Descriptions.Item label="Type">
            <Space>
              {getAnomalyTypeIcon(anomaly.anomalyType)}
              {anomaly.anomalyType.replace('_', ' ')}
            </Space>
          </Descriptions.Item>
          <Descriptions.Item label="Severity">
            <Tag color={getSeverityColor(anomaly.severity)}>
              {anomaly.severity.toUpperCase()}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Data Source">{anomaly.dataSource}</Descriptions.Item>
          <Descriptions.Item label="Data Type">{anomaly.dataType}</Descriptions.Item>
          <Descriptions.Item label="Detected At">
            {moment(anomaly.detectedAt).format('YYYY-MM-DD HH:mm:ss')}
          </Descriptions.Item>
          <Descriptions.Item label="Data Timestamp">
            {moment(anomaly.dataTimestamp).format('YYYY-MM-DD HH:mm:ss')}
          </Descriptions.Item>
          {anomaly.expectedValue && (
            <Descriptions.Item label="Expected Value">{anomaly.expectedValue}</Descriptions.Item>
          )}
          {anomaly.actualValue && (
            <Descriptions.Item label="Actual Value">{anomaly.actualValue}</Descriptions.Item>
          )}
          {anomaly.threshold && (
            <Descriptions.Item label="Threshold">{anomaly.threshold}</Descriptions.Item>
          )}
          <Descriptions.Item label="Status">
            {anomaly.resolved ? (
              <Tag color="green"><CheckCircleOutlined /> Resolved</Tag>
            ) : anomaly.acknowledged ? (
              <Tag color="orange"><ExclamationCircleOutlined /> Acknowledged</Tag>
            ) : (
              <Tag color="red"><AlertOutlined /> New</Tag>
            )}
          </Descriptions.Item>
          {anomaly.resolvedAt && (
            <Descriptions.Item label="Resolved At">
              {moment(anomaly.resolvedAt).format('YYYY-MM-DD HH:mm:ss')}
            </Descriptions.Item>
          )}
        </Descriptions>
      </Card>

      {/* Description */}
      <Card title="Description" style={{ marginBottom: 24 }}>
        <p>{anomaly.description}</p>
      </Card>

      {/* Technical Details */}
      {anomaly.details && Object.keys(anomaly.details).length > 0 && (
        <Card title="Technical Details" style={{ marginBottom: 24 }}>
          <pre style={{ backgroundColor: '#f5f5f5', padding: '16px', borderRadius: '4px' }}>
            {JSON.stringify(anomaly.details, null, 2)}
          </pre>
        </Card>
      )}

      {/* Timeline */}
      <Card title="Timeline">
        <Timeline>
          <Timeline.Item
            dot={<AlertOutlined style={{ color: getSeverityColor(anomaly.severity) }} />}
            color={getSeverityColor(anomaly.severity)}
          >
            <strong>Anomaly Detected</strong>
            <br />
            {moment(anomaly.detectedAt).format('YYYY-MM-DD HH:mm:ss')}
            <br />
            <span style={{ color: '#8c8c8c' }}>{anomaly.description}</span>
          </Timeline.Item>
          
          {anomaly.acknowledged && (
            <Timeline.Item
              dot={<ExclamationCircleOutlined style={{ color: '#faad14' }} />}
              color="#faad14"
            >
              <strong>Acknowledged</strong>
              <br />
              {moment(anomaly.detectedAt).format('YYYY-MM-DD HH:mm:ss')}
            </Timeline.Item>
          )}
          
          {anomaly.resolved && (
            <Timeline.Item
              dot={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
              color="#52c41a"
            >
              <strong>Resolved</strong>
              <br />
              {anomaly.resolvedAt && moment(anomaly.resolvedAt).format('YYYY-MM-DD HH:mm:ss')}
            </Timeline.Item>
          )}
        </Timeline>
      </Card>

      {/* Acknowledge Modal */}
      <Modal
        title="Acknowledge Anomaly"
        open={acknowledgeModalVisible}
        onOk={handleAcknowledge}
        onCancel={() => setAcknowledgeModalVisible(false)}
        confirmLoading={actionLoading}
      >
        <p>Are you sure you want to acknowledge this anomaly?</p>
        <TextArea
          placeholder="Add notes (optional)"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={4}
        />
      </Modal>

      {/* Resolve Modal */}
      <Modal
        title="Resolve Anomaly"
        open={resolveModalVisible}
        onOk={handleResolve}
        onCancel={() => setResolveModalVisible(false)}
        confirmLoading={actionLoading}
      >
        <p>Are you sure you want to resolve this anomaly?</p>
        <TextArea
          placeholder="Resolution notes (optional)"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={4}
        />
      </Modal>
    </div>
  );
};

export default AnomalyDetails;
