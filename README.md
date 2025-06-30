# Market Data Anomaly Detection System

[![Java](https://img.shields.io/badge/Java-17+-orange.svg)](https://openjdk.java.net/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.2-green.svg)](https://spring.io/projects/spring-boot)
[![Apache Pulsar](https://img.shields.io/badge/Apache%20Pulsar-3.1-red.svg)](https://pulsar.apache.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docs.docker.com/compose/)

A comprehensive, enterprise-grade market data anomaly detection system built with microservices architecture, supporting real-time stream processing and machine learning-based anomaly detection.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │    │  Stream Process │    │ Anomaly Engine  │
│                 │    │                 │    │                 │
│ • EOD Data      │───▶│ Apache Pulsar   │───▶│ ML Models       │
│ • Gemfire Cache │    │ Real-time       │    │ Statistical     │
│ • MSSQL         │    │ Processing      │    │ Detection       │
│ • HBase         │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Data Ingestion  │    │ Stream Processor│    │ Alert Service   │
│ Service (Java)  │    │ Service (Java)  │    │ (Java)          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────┐
                    │   API Gateway   │
                    │   (Java)        │
                    └─────────────────┘
```

## 🚀 Key Features

### Real-time Processing
- **Apache Pulsar** stream processing for high-throughput data ingestion
- **Microservices architecture** with Spring Boot 3.2
- **Multi-source data adapters** (EOD Data, Gemfire Cache, MSSQL, HBase)
- **Real-time anomaly detection** with sub-second latency

### Machine Learning
- **Isolation Forest** for unsupervised anomaly detection
- **Time Series Analysis** with statistical methods
- **Feature Engineering** for market data patterns
- **Model Training** and inference pipelines

### Anomaly Detection Types
- **Missing Data Detection** - Identifies data gaps and delays
- **Price Movement Detection** - Detects unusual price volatility
- **Data Staleness Detection** - Monitors data freshness
- **Volume Anomalies** - Identifies unusual trading volumes
- **ML-based Detection** - Advanced pattern recognition

### Enterprise Features
- **Containerized deployment** with Docker Compose
- **Health monitoring** and metrics collection
- **Configurable detection rules** via YAML
- **RESTful APIs** for integration
- **Scalable microservices** architecture

## 📁 Project Structure

```
MarketDataAnomalyDetection/
├── java-services/                 # Java microservices
│   ├── common/                   # Shared DTOs and enums
│   ├── api-gateway/              # API Gateway service
│   ├── data-ingestion-service/   # Data ingestion with adapters
│   ├── stream-processing-service/ # Pulsar stream processing
│   ├── alert-service/            # Alert management
│   └── dashboard-api/            # Dashboard backend API
├── python-services/              # Python services
│   ├── detection-engine/         # Core detection algorithms
│   └── ml-models/               # Machine learning models
├── shared/                       # Shared configurations
│   └── config/                  # YAML configuration files
├── infrastructure/               # Infrastructure as code
│   └── docker-compose.yml       # Container orchestration
├── scripts/                      # Utility scripts
└── docs/                        # Documentation
```

## 🛠️ Technology Stack

### Backend Services
- **Java 17+** with Spring Boot 3.2
- **Python 3.9+** with FastAPI
- **Apache Pulsar 3.1** for stream processing
- **Maven** for Java dependency management

### Machine Learning
- **scikit-learn** for ML algorithms
- **pandas** for data manipulation
- **numpy** for numerical computing
- **joblib** for model persistence

### Infrastructure
- **Docker & Docker Compose** for containerization
- **PostgreSQL** for persistent storage
- **Redis** for caching
- **Grafana** for monitoring dashboards

### Data Sources
- **EOD Historical Data API** for market data
- **Apache Geode/Gemfire** cache integration
- **Microsoft SQL Server** connector
- **Apache HBase** NoSQL database

## 🚀 Quick Start

### Prerequisites
- Java 17+
- Python 3.9+
- Maven 3.6+
- Docker & Docker Compose

### 1. Clone Repository
```bash
git clone https://github.com/XinyuXXX/MarketDataAnomalyDetection.git
cd MarketDataAnomalyDetection
```

### 2. Build Java Services
```bash
cd java-services
mvn clean package
cd ..
```

### 3. Install Python Dependencies
```bash
cd python-services/detection-engine
pip install -r requirements.txt
cd ../ml-models
pip install -r requirements.txt
cd ../..
```

### 4. Start Infrastructure
```bash
cd infrastructure
docker-compose up -d
cd ..
```

### 5. Run System Test
```bash
python3 test-complete-system.py
```

### 6. Start Services
```bash
./start-system.sh
```

## 📊 Service Endpoints

| Service | Port | Health Check | Description |
|---------|------|--------------|-------------|
| API Gateway | 8080 | `/health` | Main API entry point |
| Data Ingestion | 8081 | `/health` | Data source adapters |
| Stream Processing | 8082 | `/health` | Real-time processing |
| Alert Service | 8083 | `/health` | Alert management |
| Dashboard API | 8084 | `/health` | Dashboard backend |
| Detection Engine | 8085 | `/health` | Python ML service |

## 🔧 Configuration

### Data Sources Configuration
Edit `shared/config/data_sources.yaml`:
```yaml
data_sources:
  eod_data:
    enabled: true
    api_url: "https://eodhistoricaldata.com/api"
    api_token: "your_token_here"
  
  gemfire:
    enabled: true
    locators: "localhost[10334]"
    region: "MarketDataRegion"
```

### Detection Rules Configuration
Edit `shared/config/detection_rules.yaml`:
```yaml
detection_rules:
  missing_data:
    threshold_minutes: 30
    severity: "high"
  
  price_movement:
    threshold_percent: 5.0
    window_size: 10
```

## 🧪 Testing

### Run Complete System Test
```bash
python3 test-complete-system.py
```

### Run Individual Tests
```bash
# Java tests
cd java-services
mvn test

# Python tests
cd python-services/detection-engine
pytest tests/

cd ../ml-models
pytest tests/
```

### Demo Mode
```bash
python3 demo.py
```

## 📈 Monitoring

### Health Checks
- All services expose `/health` endpoints
- Comprehensive health status including dependencies
- Automatic service discovery

### Metrics
- Pulsar message processing metrics
- Detection algorithm performance
- Data source adapter statistics

### Dashboards
- Grafana dashboards for system monitoring
- Real-time anomaly visualization
- Performance metrics tracking

## 🔄 Data Flow

1. **Data Ingestion**: Multiple adapters collect data from various sources
2. **Stream Processing**: Pulsar processes data in real-time
3. **Anomaly Detection**: ML models and statistical methods detect anomalies
4. **Alert Generation**: Anomalies trigger configurable alerts
5. **API Access**: RESTful APIs provide access to results

## 🚀 Deployment

### Development
```bash
./start-system.sh
```

### Production
```bash
docker-compose -f infrastructure/docker-compose.prod.yml up -d
```

### Scaling
```bash
docker-compose up --scale stream-processing-service=3
```

## 📚 API Documentation

### Ingest Data
```bash
POST /api/v1/ingest
Content-Type: application/json

{
  "symbol": "AAPL",
  "price": 150.25,
  "volume": 1000000,
  "timestamp": "2024-01-01T10:00:00"
}
```

### Get Anomalies
```bash
GET /api/v1/anomalies?symbol=AAPL&from=2024-01-01&to=2024-01-02
```

### Health Status
```bash
GET /health
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/XinyuXXX/MarketDataAnomalyDetection/issues)
- **Discussions**: [GitHub Discussions](https://github.com/XinyuXXX/MarketDataAnomalyDetection/discussions)

## 🏆 Acknowledgments

- Apache Pulsar community for excellent streaming platform
- Spring Boot team for robust microservices framework
- scikit-learn contributors for ML algorithms
- Docker team for containerization technology
