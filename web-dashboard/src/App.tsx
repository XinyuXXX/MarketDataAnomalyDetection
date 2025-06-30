import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Layout } from 'antd';
import Dashboard from './components/Dashboard';
import AnomalyDetails from './components/AnomalyDetails';
import SystemHealth from './components/SystemHealth';
import Navigation from './components/Navigation';

const { Header, Content } = Layout;

const App: React.FC = () => {
  return (
    <Layout className="dashboard-container">
      <Header className="dashboard-header">
        <Navigation />
      </Header>
      <Content className="dashboard-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/anomaly/:id" element={<AnomalyDetails />} />
          <Route path="/health" element={<SystemHealth />} />
        </Routes>
      </Content>
    </Layout>
  );
};

export default App;
