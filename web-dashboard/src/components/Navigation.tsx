import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, Typography } from 'antd';
import {
  DashboardOutlined,
  AlertOutlined,
  HeartOutlined
} from '@ant-design/icons';

const { Title } = Typography;

const Navigation: React.FC = () => {
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: <Link to="/">Dashboard</Link>,
    },
    {
      key: '/health',
      icon: <HeartOutlined />,
      label: <Link to="/health">System Health</Link>,
    },
  ];

  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
        <Title level={3} style={{ color: 'white', margin: 0 }}>
          <AlertOutlined style={{ marginRight: '8px' }} />
          Market Data Anomaly Detection
        </Title>
        <div className="real-time-indicator">
          <div className="dot"></div>
          Live
        </div>
      </div>

      <Menu
        theme="dark"
        mode="horizontal"
        selectedKeys={[location.pathname]}
        items={menuItems}
        style={{
          backgroundColor: 'transparent',
          borderBottom: 'none',
          minWidth: '300px'
        }}
      />
    </div>
  );
};

export default Navigation;
