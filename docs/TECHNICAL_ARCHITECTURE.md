# Technical Architecture Documentation

## System Overview

The Market Data Anomaly Detection System is built using a hybrid microservices architecture that combines Java and Python services to leverage the strengths of both ecosystems.

## Architecture Principles

### 1. Microservices Architecture
- **Service Independence**: Each service can be developed, deployed, and scaled independently
- **Technology Diversity**: Java for high-performance processing, Python for ML algorithms
- **Fault Isolation**: Failure in one service doesn't cascade to others
- **Scalability**: Individual services can be scaled based on demand

### 2. Event-Driven Architecture
- **Apache Pulsar**: Central message broker for all inter-service communication
- **Asynchronous Processing**: Non-blocking operations for better throughput
- **Event Sourcing**: All data changes are captured as events
- **Real-time Processing**: Sub-second latency for anomaly detection

### 3. Domain-Driven Design
- **Bounded Contexts**: Clear service boundaries based on business domains
- **Shared Kernel**: Common data models and utilities
- **Anti-Corruption Layer**: Data adapters prevent external system coupling

## Service Architecture

### Java Services (Spring Boot 3.2)

#### 1. API Gateway Service (Port 8080)
**Purpose**: Single entry point for all client requests

**Responsibilities**:
- Request routing and load balancing
- Authentication and authorization
- Rate limiting and throttling
- Request/response transformation
- Circuit breaker pattern implementation

**Key Components**:
```java
@RestController
public class GatewayController {
    // Route management
    // Security filters
    // Load balancing logic
}
```

**Dependencies**:
- Spring Cloud Gateway
- Spring Security
- Resilience4j

#### 2. Data Ingestion Service (Port 8081)
**Purpose**: Multi-source data collection and normalization

**Responsibilities**:
- Data source adapter management
- Data validation and enrichment
- Protocol translation (REST, TCP, File)
- Data quality checks
- Pulsar message publishing

**Key Components**:
```java
// Data source adapters
public interface DataSourceAdapter {
    CompletableFuture<List<MarketDataPoint>> fetchData();
}

// Implementations
@Component
public class EODDataAdapter implements DataSourceAdapter
@Component  
public class GemfireAdapter implements DataSourceAdapter
```

**Supported Data Sources**:
- EOD Historical Data API
- Apache Geode/Gemfire Cache
- Microsoft SQL Server
- Apache HBase
- File-based sources (CSV, JSON)

#### 3. Stream Processing Service (Port 8082)
**Purpose**: Real-time data stream processing and routing

**Responsibilities**:
- Pulsar message consumption
- Data transformation and enrichment
- Anomaly detection orchestration
- Result aggregation and forwarding
- Performance monitoring

**Key Components**:
```java
@Service
public class MarketDataStreamProcessor {
    // Pulsar consumer management
    // Anomaly detection coordination
    // Result publishing
}
```

**Processing Pipeline**:
1. Consume from `market-data-stream` topic
2. Validate and enrich data
3. Call Python detection engine
4. Publish results to `anomaly-alerts` topic

#### 4. Alert Service (Port 8083)
**Purpose**: Alert management and notification delivery

**Responsibilities**:
- Alert rule evaluation
- Notification routing (email, SMS, webhook)
- Alert escalation and acknowledgment
- Alert history and analytics

**Key Components**:
```java
@Service
public class AlertService {
    // Rule engine
    // Notification providers
    // Escalation logic
}
```

#### 5. Dashboard API Service (Port 8084)
**Purpose**: Backend API for monitoring dashboards

**Responsibilities**:
- Metrics aggregation and querying
- Historical data analysis
- Real-time data streaming
- User management and preferences

### Python Services (FastAPI)

#### 1. Detection Engine Service (Port 8085)
**Purpose**: Core anomaly detection algorithms

**Responsibilities**:
- Statistical anomaly detection
- Machine learning model inference
- Feature engineering
- Model training coordination

**Key Algorithms**:
```python
class MissingDataDetector:
    """Detects gaps in time series data"""
    
class PriceMovementDetector:
    """Detects unusual price volatility"""
    
class DataStalenessDetector:
    """Detects outdated data"""
```

**API Endpoints**:
- `POST /detect/missing-data`
- `POST /detect/price-movement`
- `POST /detect/ml-anomalies`
- `POST /train-ml-model`

#### 2. ML Models Service
**Purpose**: Machine learning model management

**Components**:
```python
class AnomalyMLModel:
    """Isolation Forest based anomaly detection"""
    
class TimeSeriesAnomalyModel:
    """Statistical time series analysis"""
```

**Features**:
- Unsupervised learning with Isolation Forest
- Time series statistical analysis
- Feature engineering for market data
- Model persistence and versioning

## Data Architecture

### Data Models

#### Core Data Transfer Objects (DTOs)
```java
public class MarketDataPoint {
    private String symbol;
    private LocalDateTime timestamp;
    private DataSourceType source;
    private String dataType;
    private Double price;
    private Double volume;
    private Map<String, Object> payload;
    // ... getters/setters
}

public class AnomalyDto {
    private String id;
    private String symbol;
    private AnomalyType anomalyType;
    private String severity;
    private LocalDateTime detectedAt;
    private String description;
    private Map<String, Object> details;
    // ... getters/setters
}
```

#### Enumerations
```java
public enum DataSourceType {
    GEMFIRE_CACHE("gemfire", "Gemfire Cache"),
    EOD_DATA("eod", "End of Day Data"),
    MSSQL("mssql", "Microsoft SQL Server"),
    HBASE("hbase", "Apache HBase");
}

public enum AnomalyType {
    MISSING_DATA,
    PRICE_MOVEMENT,
    DATA_STALE,
    VOLUME_SPIKE,
    ML_DETECTED
}
```

### Message Flow

#### Pulsar Topics
- `market-data-stream`: Raw market data ingestion
- `anomaly-alerts`: Detected anomalies
- `system-metrics`: Service health and performance
- `audit-events`: System audit trail

#### Message Schema
```json
{
  "schema": "market-data-v1",
  "data": {
    "symbol": "AAPL",
    "timestamp": "2024-01-01T10:00:00Z",
    "price": 150.25,
    "volume": 1000000,
    "source": "EOD_DATA"
  },
  "metadata": {
    "ingestion_time": "2024-01-01T10:00:01Z",
    "source_system": "data-ingestion-service"
  }
}
```

## Infrastructure Architecture

### Container Orchestration
```yaml
# docker-compose.yml structure
services:
  pulsar:           # Message broker
  postgres:         # Persistent storage
  redis:           # Caching layer
  grafana:         # Monitoring dashboards
  
  # Java services
  api-gateway:
  data-ingestion:
  stream-processing:
  alert-service:
  dashboard-api:
  
  # Python services
  detection-engine:
```

### Network Architecture
- **Internal Network**: Services communicate via Docker network
- **External Access**: Only API Gateway exposed publicly
- **Service Discovery**: Docker DNS for service resolution
- **Load Balancing**: Built into Docker Compose scaling

### Storage Architecture
- **PostgreSQL**: Persistent storage for configuration and historical data
- **Redis**: Caching for frequently accessed data
- **Pulsar**: Message persistence and replay capability
- **Local Storage**: Model files and temporary data

## Security Architecture

### Authentication & Authorization
- **JWT Tokens**: Stateless authentication
- **Role-Based Access Control**: Service-level permissions
- **API Keys**: External system integration

### Network Security
- **Internal Communication**: Encrypted service-to-service
- **External Access**: HTTPS only
- **Firewall Rules**: Minimal port exposure

### Data Security
- **Encryption at Rest**: Database and file encryption
- **Encryption in Transit**: TLS for all communications
- **Data Masking**: Sensitive data protection

## Monitoring & Observability

### Health Checks
```java
@RestController
public class HealthController {
    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        // Service health status
        // Dependency health checks
        // Performance metrics
    }
}
```

### Metrics Collection
- **Application Metrics**: Custom business metrics
- **System Metrics**: CPU, memory, disk usage
- **Pulsar Metrics**: Message throughput and latency
- **Database Metrics**: Query performance and connections

### Logging Strategy
- **Structured Logging**: JSON format for all services
- **Correlation IDs**: Request tracing across services
- **Log Levels**: Configurable per service
- **Centralized Logging**: Aggregated log collection

## Performance Characteristics

### Throughput
- **Data Ingestion**: 10,000+ messages/second
- **Anomaly Detection**: Sub-second processing
- **API Response**: <100ms for most endpoints

### Scalability
- **Horizontal Scaling**: All services support multiple instances
- **Auto-scaling**: Based on CPU and memory usage
- **Load Distribution**: Even distribution across instances

### Reliability
- **Circuit Breakers**: Prevent cascade failures
- **Retry Logic**: Automatic retry with exponential backoff
- **Health Checks**: Automatic service recovery
- **Data Persistence**: No data loss guarantees

## Development & Deployment

### Build Pipeline
```bash
# Java services
mvn clean package

# Python services  
pip install -r requirements.txt
pytest tests/

# Docker images
docker-compose build

# System testing
python3 test-complete-system.py
```

### Deployment Strategy
- **Blue-Green Deployment**: Zero-downtime deployments
- **Rolling Updates**: Gradual service updates
- **Canary Releases**: Risk-free feature rollouts
- **Rollback Capability**: Quick reversion to previous versions

### Configuration Management
- **Environment Variables**: Runtime configuration
- **YAML Files**: Complex configuration structures
- **Secret Management**: Secure credential storage
- **Feature Flags**: Runtime feature toggling

This architecture provides a robust, scalable, and maintainable foundation for enterprise-grade market data anomaly detection.

## Technology Decisions

### Why Apache Pulsar over Kafka?
- **Multi-tenancy**: Better isolation for different data sources
- **Geo-replication**: Built-in cross-datacenter replication
- **Storage Architecture**: Separation of serving and storage layers
- **Performance**: Lower latency for real-time processing

### Why Hybrid Java/Python Architecture?
- **Java**: High-performance stream processing and enterprise integration
- **Python**: Rich ML ecosystem and rapid algorithm development
- **Best of Both**: Leverage strengths of each technology stack

### Why Spring Boot 3.2?
- **Native Compilation**: GraalVM support for faster startup
- **Reactive Programming**: Better resource utilization
- **Observability**: Built-in metrics and tracing
- **Security**: Comprehensive security framework
