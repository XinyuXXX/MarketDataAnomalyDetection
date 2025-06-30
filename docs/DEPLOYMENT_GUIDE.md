# Deployment Guide

## Overview

This guide covers deployment strategies for the Market Data Anomaly Detection System across different environments.

## Prerequisites

### System Requirements
- **CPU**: 4+ cores recommended
- **Memory**: 8GB+ RAM recommended
- **Storage**: 50GB+ available space
- **Network**: Stable internet connection for data sources

### Software Requirements
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Java**: 17+ (for local development)
- **Python**: 3.9+ (for local development)
- **Maven**: 3.6+ (for building Java services)

## Environment Setup

### Development Environment

#### 1. Clone Repository
```bash
git clone https://github.com/XinyuXXX/MarketDataAnomalyDetection.git
cd MarketDataAnomalyDetection
```

#### 2. Environment Configuration
Create `.env` file:
```bash
# Database Configuration
POSTGRES_DB=anomaly_detection
POSTGRES_USER=admin
POSTGRES_PASSWORD=secure_password

# Redis Configuration
REDIS_PASSWORD=redis_password

# API Configuration
API_SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# External Services
EOD_API_TOKEN=your-eod-api-token
GEMFIRE_LOCATORS=localhost:10334

# Pulsar Configuration
PULSAR_SERVICE_URL=pulsar://localhost:6650
PULSAR_ADMIN_URL=http://localhost:8080
```

#### 3. Build Services
```bash
# Build Java services
cd java-services
mvn clean package -DskipTests
cd ..

# Install Python dependencies
cd python-services/detection-engine
pip install -r requirements.txt
cd ../ml-models
pip install -r requirements.txt
cd ../..
```

#### 4. Start Infrastructure
```bash
# Start infrastructure services
docker-compose -f infrastructure/docker-compose.yml up -d

# Wait for services to be ready
./scripts/wait-for-services.sh
```

#### 5. Start Application Services
```bash
# Start all services
./start-system.sh

# Or start individual services
java -jar java-services/api-gateway/target/api-gateway-1.0.0.jar &
java -jar java-services/data-ingestion-service/target/data-ingestion-service-1.0.0.jar &
# ... other services
```

#### 6. Verify Deployment
```bash
# Run system tests
python3 test-complete-system.py

# Check service health
curl http://localhost:8080/health
curl http://localhost:8081/health
curl http://localhost:8082/health
```

### Production Environment

#### 1. Infrastructure Preparation

##### Docker Swarm Setup
```bash
# Initialize swarm
docker swarm init

# Add worker nodes
docker swarm join --token <token> <manager-ip>:2377
```

##### Kubernetes Setup
```bash
# Create namespace
kubectl create namespace anomaly-detection

# Apply configurations
kubectl apply -f k8s/
```

#### 2. Production Configuration

##### Environment Variables
```bash
# Production .env
ENVIRONMENT=production
LOG_LEVEL=INFO

# Database (use external managed database)
POSTGRES_HOST=your-rds-endpoint.amazonaws.com
POSTGRES_PORT=5432
POSTGRES_DB=anomaly_detection_prod
POSTGRES_USER=prod_user
POSTGRES_PASSWORD=secure_prod_password

# Redis (use external managed Redis)
REDIS_HOST=your-elasticache-endpoint.amazonaws.com
REDIS_PORT=6379
REDIS_PASSWORD=secure_redis_password

# Pulsar (use external managed Pulsar)
PULSAR_SERVICE_URL=pulsar://your-pulsar-cluster:6650
PULSAR_ADMIN_URL=http://your-pulsar-admin:8080

# Security
API_SECRET_KEY=production-secret-key
JWT_SECRET=production-jwt-secret
SSL_ENABLED=true

# Monitoring
GRAFANA_ADMIN_PASSWORD=secure_grafana_password
PROMETHEUS_RETENTION=30d
```

##### Production Docker Compose
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  api-gateway:
    image: anomaly-detection/api-gateway:latest
    environment:
      - SPRING_PROFILES_ACTIVE=production
      - JAVA_OPTS=-Xmx2g -Xms1g
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

#### 3. SSL/TLS Configuration

##### Nginx Reverse Proxy
```nginx
# /etc/nginx/sites-available/anomaly-detection
server {
    listen 443 ssl http2;
    server_name api.anomaly-detection.com;
    
    ssl_certificate /etc/ssl/certs/anomaly-detection.crt;
    ssl_certificate_key /etc/ssl/private/anomaly-detection.key;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 4. Database Migration
```bash
# Run database migrations
docker run --rm \
  -e POSTGRES_HOST=your-db-host \
  -e POSTGRES_USER=your-db-user \
  -e POSTGRES_PASSWORD=your-db-password \
  anomaly-detection/migrations:latest
```

#### 5. Production Deployment
```bash
# Deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Or deploy with Kubernetes
kubectl apply -f k8s/production/
```

## Scaling Strategies

### Horizontal Scaling

#### Docker Compose Scaling
```bash
# Scale specific services
docker-compose up --scale stream-processing-service=3
docker-compose up --scale data-ingestion-service=2

# Scale all services
docker-compose up --scale api-gateway=2 \
                  --scale data-ingestion-service=3 \
                  --scale stream-processing-service=5
```

#### Kubernetes Scaling
```bash
# Manual scaling
kubectl scale deployment stream-processing-service --replicas=5

# Auto-scaling
kubectl autoscale deployment stream-processing-service \
  --cpu-percent=70 --min=2 --max=10
```

### Vertical Scaling

#### Resource Limits
```yaml
# docker-compose.yml
services:
  stream-processing-service:
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 2G
          cpus: '1.0'
```

#### JVM Tuning
```bash
# Environment variables for Java services
JAVA_OPTS="-Xmx4g -Xms2g -XX:+UseG1GC -XX:MaxGCPauseMillis=200"
```

## Monitoring Setup

### Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'anomaly-detection'
    static_configs:
      - targets: ['api-gateway:8080', 'data-ingestion:8081']
    metrics_path: '/actuator/prometheus'
```

### Grafana Dashboards
```bash
# Import pre-built dashboards
curl -X POST \
  http://admin:password@localhost:3000/api/dashboards/db \
  -H 'Content-Type: application/json' \
  -d @monitoring/grafana-dashboard.json
```

### Log Aggregation
```yaml
# docker-compose.yml
services:
  api-gateway:
    logging:
      driver: "fluentd"
      options:
        fluentd-address: localhost:24224
        tag: anomaly-detection.api-gateway
```

## Backup and Recovery

### Database Backup
```bash
# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)

pg_dump -h $POSTGRES_HOST -U $POSTGRES_USER $POSTGRES_DB \
  | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete
```

### Configuration Backup
```bash
# Backup configuration files
tar -czf config_backup_$(date +%Y%m%d).tar.gz \
  shared/config/ \
  infrastructure/ \
  .env
```

### Disaster Recovery
```bash
# Restore from backup
gunzip -c backup_20240101_120000.sql.gz | \
  psql -h $POSTGRES_HOST -U $POSTGRES_USER $POSTGRES_DB

# Restart services
docker-compose restart
```

## Security Hardening

### Network Security
```bash
# Firewall rules (iptables)
iptables -A INPUT -p tcp --dport 443 -j ACCEPT  # HTTPS
iptables -A INPUT -p tcp --dport 80 -j ACCEPT   # HTTP (redirect to HTTPS)
iptables -A INPUT -p tcp --dport 22 -j ACCEPT   # SSH
iptables -A INPUT -j DROP                       # Drop all other traffic
```

### Container Security
```dockerfile
# Use non-root user
FROM openjdk:17-jre-slim
RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser

# Security scanning
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*
```

### Secrets Management
```bash
# Use Docker secrets
echo "secure_password" | docker secret create postgres_password -

# Reference in compose file
services:
  postgres:
    secrets:
      - postgres_password
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/postgres_password
```

## Performance Optimization

### JVM Optimization
```bash
# Production JVM settings
JAVA_OPTS="-server \
  -Xmx4g -Xms4g \
  -XX:+UseG1GC \
  -XX:MaxGCPauseMillis=200 \
  -XX:+UseStringDeduplication \
  -XX:+OptimizeStringConcat"
```

### Database Optimization
```sql
-- PostgreSQL optimization
ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET effective_cache_size = '6GB';
ALTER SYSTEM SET maintenance_work_mem = '512MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
SELECT pg_reload_conf();
```

### Pulsar Optimization
```bash
# Pulsar broker configuration
managedLedgerDefaultEnsembleSize=3
managedLedgerDefaultWriteQuorum=2
managedLedgerDefaultAckQuorum=2
managedLedgerCacheSizeMB=1024
```

## Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check logs
docker-compose logs service-name

# Check resource usage
docker stats

# Check port conflicts
netstat -tulpn | grep :8080
```

#### High Memory Usage
```bash
# Check Java heap usage
jstat -gc <pid>

# Analyze heap dump
jmap -dump:format=b,file=heap.hprof <pid>
```

#### Database Connection Issues
```bash
# Test database connectivity
pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT

# Check connection pool
curl http://localhost:8080/actuator/metrics/hikaricp.connections
```

### Health Checks
```bash
# Comprehensive health check script
#!/bin/bash
services=("api-gateway:8080" "data-ingestion:8081" "stream-processing:8082")

for service in "${services[@]}"; do
  if curl -f "http://$service/health" > /dev/null 2>&1; then
    echo "✅ $service is healthy"
  else
    echo "❌ $service is unhealthy"
  fi
done
```

This deployment guide provides comprehensive coverage for deploying the system in various environments with proper security, monitoring, and scaling considerations.
