# API Documentation

## Overview

The Market Data Anomaly Detection System provides RESTful APIs for data ingestion, anomaly detection, and system monitoring. All APIs follow REST conventions and return JSON responses.

## Base URLs

| Service | Base URL | Description |
|---------|----------|-------------|
| API Gateway | `http://localhost:8080/api/v1` | Main API entry point |
| Data Ingestion | `http://localhost:8081` | Direct data ingestion |
| Stream Processing | `http://localhost:8082` | Stream processing status |
| Alert Service | `http://localhost:8083` | Alert management |
| Dashboard API | `http://localhost:8084` | Dashboard backend |
| Detection Engine | `http://localhost:8085` | Python ML service |

## Authentication

### API Key Authentication
```bash
curl -H "X-API-Key: your-api-key" \
     -H "Content-Type: application/json" \
     http://localhost:8080/api/v1/health
```

### JWT Token Authentication
```bash
curl -H "Authorization: Bearer your-jwt-token" \
     -H "Content-Type: application/json" \
     http://localhost:8080/api/v1/anomalies
```

## Data Ingestion APIs

### Ingest Single Data Point
**Endpoint**: `POST /api/v1/ingest`

**Request Body**:
```json
{
  "symbol": "AAPL",
  "timestamp": "2024-01-01T10:00:00Z",
  "source": "EOD_DATA",
  "dataType": "price",
  "price": 150.25,
  "volume": 1000000,
  "payload": {
    "open": 149.50,
    "high": 151.00,
    "low": 149.00,
    "close": 150.25
  }
}
```

**Response**:
```json
{
  "success": true,
  "message_id": "pulsar-message-id-12345",
  "timestamp": "2024-01-01T10:00:01Z"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8081/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "price": 150.25,
    "volume": 1000000,
    "timestamp": "2024-01-01T10:00:00Z"
  }'
```

### Batch Data Ingestion
**Endpoint**: `POST /api/v1/ingest/batch`

**Request Body**:
```json
[
  {
    "symbol": "AAPL",
    "price": 150.25,
    "volume": 1000000,
    "timestamp": "2024-01-01T10:00:00Z"
  },
  {
    "symbol": "GOOGL",
    "price": 2800.50,
    "volume": 500000,
    "timestamp": "2024-01-01T10:00:00Z"
  }
]
```

**Response**:
```json
{
  "success": true,
  "message_ids": ["msg-1", "msg-2"],
  "count": 2,
  "timestamp": "2024-01-01T10:00:01Z"
}
```

## Anomaly Detection APIs

### Detect Missing Data
**Endpoint**: `POST /detect/missing-data`

**Request Body**:
```json
[
  {
    "symbol": "AAPL",
    "timestamp": "2024-01-01T10:00:00Z",
    "price": 150.25
  },
  {
    "symbol": "AAPL", 
    "timestamp": "2024-01-01T08:00:00Z",
    "price": 149.50
  }
]
```

**Response**:
```json
[
  {
    "symbol": "AAPL",
    "anomaly_type": "missing_data",
    "severity": "high",
    "detected_at": "2024-01-01T10:00:01Z",
    "description": "Data gap detected: 2 hours missing",
    "details": {
      "gap_duration_minutes": 120,
      "expected_frequency_minutes": 30,
      "last_data_timestamp": "2024-01-01T08:00:00Z"
    }
  }
]
```

### Detect Price Movement Anomalies
**Endpoint**: `POST /detect/price-movement`

**Request Body**:
```json
[
  {
    "symbol": "AAPL",
    "timestamp": "2024-01-01T10:00:00Z",
    "price": 150.25
  },
  {
    "symbol": "AAPL",
    "timestamp": "2024-01-01T10:01:00Z", 
    "price": 160.00
  }
]
```

**Response**:
```json
[
  {
    "symbol": "AAPL",
    "anomaly_type": "price_movement",
    "severity": "critical",
    "detected_at": "2024-01-01T10:01:01Z",
    "description": "Unusual price movement: 6.49% increase",
    "details": {
      "price_change_percent": 6.49,
      "threshold_percent": 5.0,
      "previous_price": 150.25,
      "current_price": 160.00
    }
  }
]
```

### ML-based Anomaly Detection
**Endpoint**: `POST /detect/ml-anomalies`

**Request Body**:
```json
[
  {
    "symbol": "AAPL",
    "timestamp": "2024-01-01T10:00:00Z",
    "price": 150.25,
    "volume": 1000000
  }
]
```

**Response**:
```json
[
  {
    "symbol": "AAPL",
    "anomaly_type": "ml_detected",
    "severity": "medium",
    "detected_at": "2024-01-01T10:00:01Z",
    "description": "ML model detected anomaly (score: -0.234)",
    "details": {
      "anomaly_score": -0.234,
      "model_type": "isolation_forest",
      "features_used": ["price", "volume", "price_change_pct"]
    }
  }
]
```

### Train ML Model
**Endpoint**: `POST /train-ml-model`

**Request Body**:
```json
[
  {
    "symbol": "AAPL",
    "timestamp": "2024-01-01T10:00:00Z",
    "price": 150.25,
    "volume": 1000000
  }
]
```

**Response**:
```json
{
  "success": true,
  "message": "Model trained with 1000 samples",
  "timestamp": "2024-01-01T10:00:01Z"
}
```

## Query APIs

### Get Anomalies
**Endpoint**: `GET /api/v1/anomalies`

**Query Parameters**:
- `symbol` (optional): Filter by symbol
- `from` (optional): Start date (ISO 8601)
- `to` (optional): End date (ISO 8601)
- `severity` (optional): Filter by severity (low, medium, high, critical)
- `type` (optional): Filter by anomaly type
- `limit` (optional): Maximum results (default: 100)
- `offset` (optional): Pagination offset (default: 0)

**Example Request**:
```bash
GET /api/v1/anomalies?symbol=AAPL&from=2024-01-01&to=2024-01-02&severity=high
```

**Response**:
```json
{
  "anomalies": [
    {
      "id": "anomaly-12345",
      "symbol": "AAPL",
      "anomaly_type": "price_movement",
      "severity": "high",
      "detected_at": "2024-01-01T10:00:01Z",
      "data_timestamp": "2024-01-01T10:00:00Z",
      "description": "Unusual price movement detected",
      "acknowledged": false,
      "resolved": false
    }
  ],
  "total": 1,
  "limit": 100,
  "offset": 0
}
```

### Get Anomaly Details
**Endpoint**: `GET /api/v1/anomalies/{anomaly_id}`

**Response**:
```json
{
  "id": "anomaly-12345",
  "symbol": "AAPL",
  "anomaly_type": "price_movement",
  "severity": "high",
  "detected_at": "2024-01-01T10:00:01Z",
  "data_timestamp": "2024-01-01T10:00:00Z",
  "description": "Unusual price movement detected",
  "details": {
    "price_change_percent": 6.49,
    "threshold_percent": 5.0,
    "previous_price": 150.25,
    "current_price": 160.00
  },
  "acknowledged": false,
  "resolved": false,
  "data_source": "EOD_DATA"
}
```

## Alert Management APIs

### Acknowledge Anomaly
**Endpoint**: `POST /api/v1/anomalies/{anomaly_id}/acknowledge`

**Request Body**:
```json
{
  "acknowledged_by": "user@example.com",
  "notes": "Investigating the price movement"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Anomaly acknowledged",
  "timestamp": "2024-01-01T10:05:00Z"
}
```

### Resolve Anomaly
**Endpoint**: `POST /api/v1/anomalies/{anomaly_id}/resolve`

**Request Body**:
```json
{
  "resolved_by": "user@example.com",
  "resolution_notes": "False positive - market news caused expected movement"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Anomaly resolved",
  "timestamp": "2024-01-01T10:10:00Z"
}
```

## Health Check APIs

### Service Health
**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "UP",
  "service": "data-ingestion-service",
  "timestamp": "2024-01-01T10:00:00Z",
  "adapters": {
    "eod_data": {
      "healthy": true,
      "status": "connected",
      "last_successful_fetch": 1704110400000
    },
    "gemfire": {
      "healthy": true,
      "status": "connected",
      "last_successful_fetch": 1704110400000
    }
  }
}
```

### System Metrics
**Endpoint**: `GET /metrics`

**Response**:
```json
{
  "system": {
    "cpu_usage": 45.2,
    "memory_usage": 67.8,
    "disk_usage": 23.1
  },
  "application": {
    "messages_processed": 12345,
    "anomalies_detected": 23,
    "processing_latency_ms": 45
  },
  "timestamp": "2024-01-01T10:00:00Z"
}
```

## Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": {
      "field": "timestamp",
      "issue": "Invalid date format"
    },
    "timestamp": "2024-01-01T10:00:00Z",
    "request_id": "req-12345"
  }
}
```

### Common Error Codes
- `400 BAD_REQUEST`: Invalid request data
- `401 UNAUTHORIZED`: Authentication required
- `403 FORBIDDEN`: Insufficient permissions
- `404 NOT_FOUND`: Resource not found
- `429 TOO_MANY_REQUESTS`: Rate limit exceeded
- `500 INTERNAL_SERVER_ERROR`: Server error
- `503 SERVICE_UNAVAILABLE`: Service temporarily unavailable

## Rate Limiting

### Rate Limit Headers
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1704110400
```

### Rate Limits by Endpoint
- Data Ingestion: 1000 requests/minute
- Anomaly Detection: 500 requests/minute
- Query APIs: 2000 requests/minute
- Health Checks: Unlimited

## SDK Examples

### Python SDK
```python
import requests

class AnomalyDetectionClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
    
    def ingest_data(self, data_point):
        response = requests.post(
            f"{self.base_url}/ingest",
            json=data_point,
            headers=self.headers
        )
        return response.json()
    
    def get_anomalies(self, symbol=None, from_date=None, to_date=None):
        params = {}
        if symbol:
            params['symbol'] = symbol
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
            
        response = requests.get(
            f"{self.base_url}/anomalies",
            params=params,
            headers=self.headers
        )
        return response.json()

# Usage
client = AnomalyDetectionClient("http://localhost:8080/api/v1", "your-api-key")

# Ingest data
result = client.ingest_data({
    "symbol": "AAPL",
    "price": 150.25,
    "volume": 1000000,
    "timestamp": "2024-01-01T10:00:00Z"
})

# Get anomalies
anomalies = client.get_anomalies(symbol="AAPL", from_date="2024-01-01")
```

### Java SDK
```java
public class AnomalyDetectionClient {
    private final WebClient webClient;
    private final String apiKey;
    
    public AnomalyDetectionClient(String baseUrl, String apiKey) {
        this.apiKey = apiKey;
        this.webClient = WebClient.builder()
            .baseUrl(baseUrl)
            .defaultHeader("X-API-Key", apiKey)
            .build();
    }
    
    public Mono<IngestResponse> ingestData(MarketDataPoint dataPoint) {
        return webClient.post()
            .uri("/ingest")
            .bodyValue(dataPoint)
            .retrieve()
            .bodyToMono(IngestResponse.class);
    }
    
    public Mono<AnomalyResponse> getAnomalies(String symbol, LocalDate from, LocalDate to) {
        return webClient.get()
            .uri(uriBuilder -> uriBuilder
                .path("/anomalies")
                .queryParamIfPresent("symbol", Optional.ofNullable(symbol))
                .queryParamIfPresent("from", Optional.ofNullable(from))
                .queryParamIfPresent("to", Optional.ofNullable(to))
                .build())
            .retrieve()
            .bodyToMono(AnomalyResponse.class);
    }
}
```

This API documentation provides comprehensive coverage of all available endpoints and their usage patterns.
