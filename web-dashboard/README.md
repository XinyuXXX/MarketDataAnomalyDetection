# Market Data Anomaly Detection - Web Dashboard

A modern React-based web dashboard for visualizing and managing market data anomalies in real-time.

## 🌟 Features

### Real-time Visualization
- **Live Anomaly Monitoring**: Real-time updates of detected anomalies
- **Interactive Charts**: Timeline, severity distribution, symbol analysis
- **Responsive Design**: Works on desktop, tablet, and mobile devices

### Comprehensive Analytics
- **Multiple Chart Types**: Line charts, bar charts, pie charts, scatter plots
- **Filtering & Search**: Advanced filtering by symbol, type, severity, date range
- **Data Export**: Export anomaly data for further analysis

### Anomaly Management
- **Detailed Views**: Comprehensive anomaly information and technical details
- **Status Management**: Acknowledge and resolve anomalies
- **Timeline Tracking**: Full audit trail of anomaly lifecycle

### System Monitoring
- **Service Health**: Real-time monitoring of all backend services
- **Performance Metrics**: System performance and processing statistics
- **Alert Dashboard**: Visual indicators for system issues

## 🛠️ Technology Stack

- **Frontend Framework**: React 18 with TypeScript
- **UI Library**: Ant Design 5.x
- **Charts**: Recharts for data visualization
- **HTTP Client**: Axios for API communication
- **Routing**: React Router v6
- **Build Tool**: Create React App with TypeScript template
- **Styling**: CSS-in-JS with Ant Design theming

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm
- Backend services running (API Gateway on port 8080)

### Development Setup

1. **Install Dependencies**
   ```bash
   cd web-dashboard
   npm install
   ```

2. **Start Development Server**
   ```bash
   npm start
   ```
   
   The dashboard will be available at `http://localhost:3000`

3. **Using the Startup Script**
   ```bash
   # From project root
   ./start-web-dashboard.sh dev
   ```

### Production Build

```bash
# Build for production
npm run build

# Or using the startup script
./start-web-dashboard.sh build
```

### Docker Deployment

```bash
# Build and run with Docker
./start-web-dashboard.sh docker

# Or manually
docker build -t anomaly-dashboard .
docker run -p 3000:3000 anomaly-dashboard
```

## 📱 User Interface

### Dashboard Overview
- **Metrics Cards**: Key performance indicators and anomaly counts
- **Real-time Charts**: Visual representation of anomaly trends
- **Anomaly Table**: Sortable and filterable list of recent anomalies
- **Filter Panel**: Advanced filtering options

### Anomaly Details Page
- **Comprehensive Information**: All anomaly metadata and technical details
- **Action Buttons**: Acknowledge and resolve anomalies
- **Timeline View**: Visual representation of anomaly lifecycle
- **Related Data**: Context and historical information

### System Health Page
- **Service Status**: Real-time status of all backend services
- **Health Metrics**: System performance indicators
- **Alert Notifications**: Visual alerts for system issues

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the web-dashboard directory:

```bash
# API Configuration
REACT_APP_API_URL=http://localhost:8080/api/v1

# Development Configuration
PORT=3000
GENERATE_SOURCEMAP=false

# Feature Flags
REACT_APP_ENABLE_MOCK_DATA=false
REACT_APP_ENABLE_REAL_TIME=true
```

### API Integration

The dashboard integrates with the backend API services:

- **Anomaly API**: Fetch, filter, and manage anomalies
- **Metrics API**: System performance and statistics
- **Health API**: Service health monitoring

### Mock Data Mode

For development without backend services:

```typescript
// In src/services/api.ts
export const API = process.env.NODE_ENV === 'development' ? MockAPI : AnomalyAPI;
```

## 📊 Dashboard Components

### MetricsOverview
- Total anomaly counts by severity
- Resolution and acknowledgment rates
- System health indicators
- Processing statistics

### AnomalyChart
- Timeline view of anomaly occurrences
- Severity distribution charts
- Symbol-based analysis
- Anomaly type breakdown

### FilterPanel
- Date range selection with quick presets
- Multi-select filters for symbols, types, severity
- Status filters (acknowledged, resolved)
- Real-time filter application

### AnomalyTable
- Sortable columns with pagination
- Status indicators and action buttons
- Responsive design for mobile devices
- Export functionality

## 🎨 Theming & Customization

### Ant Design Theme

```typescript
// In src/index.tsx
<ConfigProvider
  theme={{
    token: {
      colorPrimary: '#1890ff',
      borderRadius: 6,
    },
  }}
>
```

### Custom Styles

```css
/* In src/index.css */
.dashboard-container {
  min-height: 100vh;
  background-color: #f0f2f5;
}

.metric-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
}
```

## 🔄 Real-time Updates

### Auto-refresh
- Dashboard data refreshes every 30 seconds
- Health status updates every 30 seconds
- Visual indicators for live data

### WebSocket Integration (Future)
```typescript
// Planned WebSocket integration
const socket = io('ws://localhost:8080');
socket.on('anomaly', (data) => {
  // Handle real-time anomaly updates
});
```

## 📱 Responsive Design

### Breakpoints
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

### Mobile Optimizations
- Collapsible navigation
- Touch-friendly controls
- Optimized chart sizes
- Simplified layouts

## 🧪 Testing

### Unit Tests
```bash
npm test
```

### E2E Tests (Future)
```bash
npm run test:e2e
```

### Component Testing
```bash
npm run test:components
```

## 🚀 Deployment

### Development
```bash
./start-web-dashboard.sh dev
```

### Production
```bash
./start-web-dashboard.sh build
```

### Docker
```bash
./start-web-dashboard.sh docker
```

### Nginx Configuration
The included `nginx.conf` provides:
- React Router support
- API proxy configuration
- Static asset caching
- Security headers

## 🔍 Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Verify backend services are running
   - Check API_URL configuration
   - Ensure CORS is properly configured

2. **Charts Not Displaying**
   - Check data format compatibility
   - Verify Recharts dependencies
   - Check console for JavaScript errors

3. **Build Failures**
   - Clear node_modules and reinstall
   - Check Node.js version compatibility
   - Verify TypeScript configuration

### Debug Mode
```bash
# Enable debug logging
REACT_APP_DEBUG=true npm start
```

## 📈 Performance

### Optimization Features
- Code splitting with React.lazy
- Memoized components with React.memo
- Efficient re-rendering with useMemo/useCallback
- Lazy loading of chart components

### Bundle Analysis
```bash
npm run build
npx serve -s build
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
