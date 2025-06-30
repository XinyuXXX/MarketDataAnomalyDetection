#!/usr/bin/env python3
"""
Web Dashboard Demo Script
演示Web Dashboard的功能和特性
"""

import time
import json
import random
from datetime import datetime, timedelta

def print_banner():
    """打印演示横幅"""
    print("=" * 80)
    print("🌐 Market Data Anomaly Detection - Web Dashboard Demo")
    print("=" * 80)
    print()

def demo_dashboard_features():
    """演示Dashboard的主要功能"""
    print("📊 Dashboard Features Overview:")
    print()
    
    features = [
        {
            "name": "Real-time Anomaly Monitoring",
            "description": "Live updates of detected anomalies with auto-refresh every 30 seconds",
            "components": ["Dashboard.tsx", "MetricsOverview.tsx"]
        },
        {
            "name": "Interactive Data Visualization", 
            "description": "Multiple chart types: timeline, bar charts, pie charts, scatter plots",
            "components": ["AnomalyChart.tsx", "Recharts integration"]
        },
        {
            "name": "Advanced Filtering System",
            "description": "Filter by symbol, type, severity, date range, and status",
            "components": ["FilterPanel.tsx", "Multi-select controls"]
        },
        {
            "name": "Anomaly Management",
            "description": "Acknowledge and resolve anomalies with detailed tracking",
            "components": ["AnomalyDetails.tsx", "Status management"]
        },
        {
            "name": "System Health Monitoring",
            "description": "Real-time monitoring of all backend services",
            "components": ["SystemHealth.tsx", "Service status indicators"]
        },
        {
            "name": "Responsive Design",
            "description": "Works seamlessly on desktop, tablet, and mobile devices",
            "components": ["Ant Design", "CSS Grid/Flexbox"]
        }
    ]
    
    for i, feature in enumerate(features, 1):
        print(f"{i}. 🎯 {feature['name']}")
        print(f"   📝 {feature['description']}")
        print(f"   🔧 Components: {', '.join(feature['components'])}")
        print()

def demo_mock_data():
    """演示Mock数据结构"""
    print("🔬 Mock Data Examples:")
    print()
    
    # 模拟异常数据
    mock_anomaly = {
        "id": "anomaly-demo-001",
        "symbol": "AAPL",
        "anomalyType": "PRICE_MOVEMENT",
        "severity": "high",
        "detectedAt": datetime.now().isoformat(),
        "dataTimestamp": datetime.now().isoformat(),
        "description": "Unusual price movement: 6.5% increase in 5 minutes",
        "details": {
            "priceChangePct": 6.5,
            "threshold": 5.0,
            "previousPrice": 150.25,
            "currentPrice": 160.02
        },
        "dataSource": "EOD_DATA",
        "dataType": "price",
        "acknowledged": False,
        "resolved": False
    }
    
    print("📈 Sample Anomaly Data:")
    print(json.dumps(mock_anomaly, indent=2))
    print()
    
    # 模拟系统指标
    mock_metrics = {
        "totalAnomalies": 156,
        "criticalAnomalies": 12,
        "highAnomalies": 34,
        "mediumAnomalies": 67,
        "lowAnomalies": 43,
        "acknowledgedAnomalies": 89,
        "resolvedAnomalies": 134,
        "dataSourcesActive": 4,
        "messagesProcessed": 45678,
        "processingLatency": 45,
        "systemHealth": "healthy"
    }
    
    print("📊 Sample System Metrics:")
    print(json.dumps(mock_metrics, indent=2))
    print()

def demo_api_endpoints():
    """演示API端点"""
    print("🔌 API Integration:")
    print()
    
    endpoints = [
        {
            "method": "GET",
            "path": "/api/v1/anomalies",
            "description": "Fetch anomalies with filtering",
            "params": "symbols, types, severity, from, to, limit, offset"
        },
        {
            "method": "GET", 
            "path": "/api/v1/anomalies/{id}",
            "description": "Get single anomaly details",
            "params": "id"
        },
        {
            "method": "POST",
            "path": "/api/v1/anomalies/{id}/acknowledge",
            "description": "Acknowledge an anomaly",
            "params": "acknowledged_by, notes"
        },
        {
            "method": "POST",
            "path": "/api/v1/anomalies/{id}/resolve", 
            "description": "Resolve an anomaly",
            "params": "resolved_by, resolution_notes"
        },
        {
            "method": "GET",
            "path": "/api/v1/metrics",
            "description": "Get system metrics",
            "params": "None"
        },
        {
            "method": "GET",
            "path": "/health",
            "description": "Service health check",
            "params": "None"
        }
    ]
    
    for endpoint in endpoints:
        print(f"🌐 {endpoint['method']} {endpoint['path']}")
        print(f"   📝 {endpoint['description']}")
        print(f"   📋 Parameters: {endpoint['params']}")
        print()

def demo_chart_types():
    """演示图表类型"""
    print("📈 Chart Visualization Types:")
    print()
    
    charts = [
        {
            "type": "Timeline Chart",
            "description": "Shows anomaly occurrences over time with severity breakdown",
            "library": "Recharts LineChart",
            "features": ["Multi-line display", "Time-based X-axis", "Severity color coding"]
        },
        {
            "type": "Severity Distribution",
            "description": "Pie chart and bar chart showing anomaly distribution by severity",
            "library": "Recharts PieChart + BarChart",
            "features": ["Interactive legends", "Percentage labels", "Color-coded severity"]
        },
        {
            "type": "Symbol Analysis",
            "description": "Horizontal bar chart showing top symbols with most anomalies",
            "library": "Recharts BarChart",
            "features": ["Horizontal layout", "Top 10 symbols", "Count-based sorting"]
        },
        {
            "type": "Anomaly Types",
            "description": "Pie chart breakdown of different anomaly types",
            "library": "Recharts PieChart",
            "features": ["Type-based grouping", "Percentage display", "Interactive tooltips"]
        }
    ]
    
    for chart in charts:
        print(f"📊 {chart['type']}")
        print(f"   📝 {chart['description']}")
        print(f"   🔧 Library: {chart['library']}")
        print(f"   ✨ Features: {', '.join(chart['features'])}")
        print()

def demo_responsive_design():
    """演示响应式设计"""
    print("📱 Responsive Design Features:")
    print()
    
    breakpoints = [
        {
            "device": "Mobile (< 768px)",
            "features": [
                "Collapsible navigation",
                "Stacked metric cards",
                "Touch-friendly controls",
                "Simplified chart layouts",
                "Horizontal scrolling tables"
            ]
        },
        {
            "device": "Tablet (768px - 1024px)",
            "features": [
                "Grid-based layout",
                "Optimized chart sizes",
                "Touch and mouse support",
                "Adaptive navigation",
                "Flexible card arrangements"
            ]
        },
        {
            "device": "Desktop (> 1024px)",
            "features": [
                "Full feature set",
                "Multi-column layouts",
                "Hover interactions",
                "Keyboard shortcuts",
                "Advanced filtering panels"
            ]
        }
    ]
    
    for bp in breakpoints:
        print(f"📱 {bp['device']}")
        for feature in bp['features']:
            print(f"   ✅ {feature}")
        print()

def demo_deployment_options():
    """演示部署选项"""
    print("🚀 Deployment Options:")
    print()
    
    options = [
        {
            "method": "Development Mode",
            "command": "./start-web-dashboard.sh dev",
            "description": "Hot reload, development tools, mock data",
            "port": "3000"
        },
        {
            "method": "Production Build",
            "command": "./start-web-dashboard.sh build",
            "description": "Optimized build, minified assets, production ready",
            "port": "N/A (static files)"
        },
        {
            "method": "Docker Container",
            "command": "./start-web-dashboard.sh docker",
            "description": "Containerized deployment with Nginx",
            "port": "3000"
        },
        {
            "method": "Docker Compose",
            "command": "docker-compose up web-dashboard",
            "description": "Full stack deployment with backend services",
            "port": "3000"
        }
    ]
    
    for option in options:
        print(f"🐳 {option['method']}")
        print(f"   💻 Command: {option['command']}")
        print(f"   📝 Description: {option['description']}")
        print(f"   🌐 Port: {option['port']}")
        print()

def demo_technology_stack():
    """演示技术栈"""
    print("🛠️ Technology Stack:")
    print()
    
    stack = {
        "Frontend Framework": {
            "React 18": "Modern React with hooks and concurrent features",
            "TypeScript": "Type-safe JavaScript for better development experience"
        },
        "UI Library": {
            "Ant Design 5.x": "Enterprise-class UI components",
            "CSS-in-JS": "Styled components with theme support"
        },
        "Data Visualization": {
            "Recharts": "Composable charting library built on React components",
            "D3.js": "Underlying data visualization engine"
        },
        "HTTP Client": {
            "Axios": "Promise-based HTTP client with interceptors",
            "Request/Response": "Automatic JSON parsing and error handling"
        },
        "Routing": {
            "React Router v6": "Declarative routing for React applications",
            "Navigation": "Programmatic and declarative navigation"
        },
        "Build Tools": {
            "Create React App": "Zero-configuration React build setup",
            "Webpack": "Module bundler with hot reload"
        },
        "Deployment": {
            "Docker": "Multi-stage builds for production optimization",
            "Nginx": "High-performance web server with API proxy"
        }
    }
    
    for category, technologies in stack.items():
        print(f"📦 {category}")
        for tech, description in technologies.items():
            print(f"   🔧 {tech}: {description}")
        print()

def main():
    """主演示函数"""
    print_banner()
    
    demos = [
        ("Dashboard Features", demo_dashboard_features),
        ("Mock Data Examples", demo_mock_data),
        ("API Integration", demo_api_endpoints),
        ("Chart Visualizations", demo_chart_types),
        ("Responsive Design", demo_responsive_design),
        ("Deployment Options", demo_deployment_options),
        ("Technology Stack", demo_technology_stack)
    ]
    
    for i, (title, demo_func) in enumerate(demos, 1):
        print(f"🎯 {i}. {title}")
        print("-" * 60)
        demo_func()
        
        if i < len(demos):
            print("⏳ Press Enter to continue to next demo...")
            input()
            print()
    
    print("=" * 80)
    print("🎉 Web Dashboard Demo Complete!")
    print()
    print("📋 Quick Start Commands:")
    print("1. Install dependencies: cd web-dashboard && npm install")
    print("2. Start development: ./start-web-dashboard.sh dev")
    print("3. Build production: ./start-web-dashboard.sh build")
    print("4. Run with Docker: ./start-web-dashboard.sh docker")
    print()
    print("🌐 Access URL: http://localhost:3000")
    print("📚 Documentation: web-dashboard/README.md")
    print("=" * 80)

if __name__ == "__main__":
    main()
