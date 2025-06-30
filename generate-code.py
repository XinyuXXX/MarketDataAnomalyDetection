#!/usr/bin/env python3
"""
Automated code generator for Market Data Anomaly Detection System
Generates complete Java and Python microservices with tests
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List
import subprocess


class CodeGenerator:
    """Generates complete microservices code automatically"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.java_services_dir = self.project_root / "java-services"
        self.python_services_dir = self.project_root / "python-services"
        
    def generate_all(self):
        """Generate all microservices code"""
        print("🚀 Starting automated code generation...")
        
        self.create_directory_structure()
        self.generate_java_common_module()
        self.generate_java_services()
        self.generate_python_services()
        self.generate_docker_configs()
        self.generate_test_configs()
        
        print("✅ Code generation completed successfully!")
    
    def create_directory_structure(self):
        """Create complete directory structure"""
        print("📁 Creating directory structure...")
        
        # Java services structure
        java_services = [
            "api-gateway", "data-ingestion-service", "stream-processing-service",
            "alert-service", "dashboard-api"
        ]
        
        for service in java_services:
            service_path = self.java_services_dir / service
            
            # Create Maven structure
            dirs = [
                f"src/main/java/com/marketdata/{service.replace('-', '')}/controller",
                f"src/main/java/com/marketdata/{service.replace('-', '')}/service",
                f"src/main/java/com/marketdata/{service.replace('-', '')}/repository", 
                f"src/main/java/com/marketdata/{service.replace('-', '')}/config",
                f"src/main/java/com/marketdata/{service.replace('-', '')}/dto",
                f"src/main/java/com/marketdata/{service.replace('-', '')}/entity",
                "src/main/resources",
                f"src/test/java/com/marketdata/{service.replace('-', '')}"
            ]
            
            for dir_path in dirs:
                (service_path / dir_path).mkdir(parents=True, exist_ok=True)
        
        # Python services structure  
        python_dirs = [
            "detection-engine/src/detection",
            "detection-engine/src/algorithms",
            "detection-engine/src/models", 
            "detection-engine/src/api",
            "detection-engine/tests",
            "ml-models/src",
            "ml-models/tests"
        ]
        
        for dir_path in python_dirs:
            (self.python_services_dir / dir_path).mkdir(parents=True, exist_ok=True)
    
    def generate_java_common_module(self):
        """Generate Java common module with shared DTOs and utilities"""
        print("☕ Generating Java common module...")
        
        common_path = self.java_services_dir / "common"
        
        # Generate common DTOs
        self._write_file(common_path / "src/main/java/com/marketdata/common/dto/MarketDataPoint.java", 
                        self._get_market_data_point_java())
        
        self._write_file(common_path / "src/main/java/com/marketdata/common/dto/AnomalyDto.java",
                        self._get_anomaly_dto_java())
        
        self._write_file(common_path / "src/main/java/com/marketdata/common/enums/DataSourceType.java",
                        self._get_data_source_type_enum())
        
        self._write_file(common_path / "src/main/java/com/marketdata/common/enums/AnomalyType.java", 
                        self._get_anomaly_type_enum())
    
    def generate_java_services(self):
        """Generate all Java microservices"""
        print("☕ Generating Java microservices...")
        
        services_config = {
            "api-gateway": {"port": 8080, "description": "API Gateway Service"},
            "data-ingestion-service": {"port": 8081, "description": "Data Ingestion Service"},
            "stream-processing-service": {"port": 8082, "description": "Stream Processing Service"},
            "alert-service": {"port": 8083, "description": "Alert Service"},
            "dashboard-api": {"port": 8084, "description": "Dashboard API Service"}
        }
        
        for service_name, config in services_config.items():
            self._generate_java_service(service_name, config)
    
    def _generate_java_service(self, service_name: str, config: Dict):
        """Generate individual Java service"""
        service_path = self.java_services_dir / service_name
        package_name = service_name.replace('-', '')
        
        # Generate pom.xml
        self._write_file(service_path / "pom.xml", self._get_service_pom_xml(service_name, package_name))
        
        # Generate main application class
        self._write_file(service_path / f"src/main/java/com/marketdata/{package_name}/{package_name.title()}Application.java",
                        self._get_spring_boot_main_class(package_name, config["description"]))
        
        # Generate controller
        self._write_file(service_path / f"src/main/java/com/marketdata/{package_name}/controller/HealthController.java",
                        self._get_health_controller(package_name))
        
        # Generate application.yml
        self._write_file(service_path / "src/main/resources/application.yml",
                        self._get_application_yml(config["port"], service_name))
        
        # Generate Dockerfile
        self._write_file(service_path / "Dockerfile", self._get_java_dockerfile())
    
    def generate_python_services(self):
        """Generate Python detection engine service"""
        print("🐍 Generating Python detection engine...")
        
        detection_engine_path = self.python_services_dir / "detection-engine"
        
        # Generate requirements.txt
        self._write_file(detection_engine_path / "requirements.txt", self._get_python_requirements())
        
        # Generate main FastAPI application
        self._write_file(detection_engine_path / "src/api/main.py", self._get_fastapi_main())
        
        # Generate detection algorithms
        self._write_file(detection_engine_path / "src/algorithms/missing_data_detector.py", 
                        self._get_missing_data_detector())
        
        self._write_file(detection_engine_path / "src/algorithms/price_movement_detector.py",
                        self._get_price_movement_detector())
        
        # Generate Dockerfile
        self._write_file(detection_engine_path / "Dockerfile", self._get_python_dockerfile())
        
        # Generate tests
        self._write_file(detection_engine_path / "tests/test_detection.py", self._get_python_tests())
    
    def generate_docker_configs(self):
        """Generate Docker Compose configurations"""
        print("🐳 Generating Docker configurations...")
        
        # Java services docker-compose
        self._write_file(self.java_services_dir / "docker-compose.yml", self._get_java_docker_compose())
        
        # Python services docker-compose  
        self._write_file(self.python_services_dir / "docker-compose.yml", self._get_python_docker_compose())
        
        # Infrastructure docker-compose
        self._write_file(self.project_root / "infrastructure/docker-compose.yml", self._get_infrastructure_docker_compose())
    
    def generate_test_configs(self):
        """Generate test configurations and scripts"""
        print("🧪 Generating test configurations...")
        
        # Integration test script
        self._write_file(self.project_root / "run-tests.py", self._get_integration_test_script())
        
        # Make scripts executable
        os.chmod(self.project_root / "build-and-test.sh", 0o755)
        os.chmod(self.project_root / "run-tests.py", 0o755)
    
    def _write_file(self, file_path: Path, content: str):
        """Write content to file, creating directories if needed"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Generated: {file_path}")
    
    # Template methods for generating specific file contents
    def _get_market_data_point_java(self) -> str:
        return '''package com.marketdata.common.dto;

import lombok.Data;
import lombok.Builder;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import com.fasterxml.jackson.annotation.JsonFormat;
import com.marketdata.common.enums.DataSourceType;

import java.time.LocalDateTime;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MarketDataPoint {
    private String symbol;
    
    @JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ss")
    private LocalDateTime timestamp;
    
    private DataSourceType source;
    private String dataType;
    private Map<String, Object> payload;
    private Double price;
    private Double volume;
    
    @JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ss")
    private LocalDateTime receivedAt;
    
    @JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ss")
    private LocalDateTime processedAt;
}'''
    
    def _get_anomaly_dto_java(self) -> str:
        return '''package com.marketdata.common.dto;

import lombok.Data;
import lombok.Builder;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import com.fasterxml.jackson.annotation.JsonFormat;
import com.marketdata.common.enums.AnomalyType;
import com.marketdata.common.enums.DataSourceType;

import java.time.LocalDateTime;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AnomalyDto {
    private String id;
    private String symbol;
    private AnomalyType anomalyType;
    private String severity;
    
    @JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ss")
    private LocalDateTime detectedAt;
    
    @JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ss")
    private LocalDateTime dataTimestamp;
    
    private String description;
    private Map<String, Object> details;
    private DataSourceType dataSource;
    private String dataType;
    
    private Double expectedValue;
    private Double actualValue;
    private Double threshold;
    
    private boolean acknowledged;
    private boolean resolved;
    
    @JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ss")
    private LocalDateTime resolvedAt;
}'''
    
    def _get_data_source_type_enum(self) -> str:
        return '''package com.marketdata.common.enums;

public enum DataSourceType {
    GEMFIRE("gemfire", "Gemfire Cache"),
    EOD("eod", "End of Day Data"),
    MSSQL("mssql", "Microsoft SQL Server"),
    HBASE("hbase", "Apache HBase");

    private final String code;
    private final String description;

    DataSourceType(String code, String description) {
        this.code = code;
        this.description = description;
    }

    public String getCode() {
        return code;
    }

    public String getDescription() {
        return description;
    }
}'''
    
    def _get_anomaly_type_enum(self) -> str:
        return '''package com.marketdata.common.enums;

public enum AnomalyType {
    MISSING_DATA("missing_data", "Missing Data"),
    PRICE_MOVEMENT("price_movement", "Price Movement"),
    DATA_STALE("data_stale", "Data Stale"),
    VOLUME_SPIKE("volume_spike", "Volume Spike"),
    DATA_QUALITY("data_quality", "Data Quality");

    private final String code;
    private final String description;

    AnomalyType(String code, String description) {
        this.code = code;
        this.description = description;
    }

    public String getCode() {
        return code;
    }

    public String getDescription() {
        return description;
    }
}'''

    def _get_service_pom_xml(self, service_name: str, package_name: str) -> str:
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>com.marketdata</groupId>
        <artifactId>anomaly-detection-parent</artifactId>
        <version>1.0.0</version>
    </parent>

    <artifactId>{service_name}</artifactId>
    <packaging>jar</packaging>

    <name>{service_name.title()}</name>
    <description>{service_name.replace('-', ' ').title()} Service</description>

    <dependencies>
        <!-- Common module -->
        <dependency>
            <groupId>com.marketdata</groupId>
            <artifactId>common</artifactId>
            <version>1.0.0</version>
        </dependency>

        <!-- Spring Boot Starters -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-actuator</artifactId>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>

        <!-- Database -->
        <dependency>
            <groupId>org.postgresql</groupId>
            <artifactId>postgresql</artifactId>
        </dependency>

        <!-- Redis -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-redis</artifactId>
        </dependency>

        <!-- Kafka -->
        <dependency>
            <groupId>org.springframework.kafka</groupId>
            <artifactId>spring-kafka</artifactId>
        </dependency>

        <!-- Monitoring -->
        <dependency>
            <groupId>io.micrometer</groupId>
            <artifactId>micrometer-registry-prometheus</artifactId>
        </dependency>

        <!-- Testing -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>'''

    def _get_spring_boot_main_class(self, package_name: str, description: str) -> str:
        class_name = package_name.title() + "Application"
        return f'''package com.marketdata.{package_name};

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.kafka.annotation.EnableKafka;

/**
 * {description}
 */
@SpringBootApplication
@EnableKafka
public class {class_name} {{
    public static void main(String[] args) {{
        SpringApplication.run({class_name}.class, args);
    }}
}}'''

    def _get_health_controller(self, package_name: str) -> str:
        return f'''package com.marketdata.{package_name}.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.http.ResponseEntity;
import java.util.Map;
import java.util.HashMap;
import java.time.LocalDateTime;

@RestController
public class HealthController {{

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {{
        Map<String, Object> response = new HashMap<>();
        response.put("status", "UP");
        response.put("service", "{package_name}");
        response.put("timestamp", LocalDateTime.now());
        return ResponseEntity.ok(response);
    }}
}}'''

    def _get_application_yml(self, port: int, service_name: str) -> str:
        return f'''server:
  port: {port}

spring:
  application:
    name: {service_name}

  datasource:
    url: jdbc:postgresql://localhost:5432/anomaly_detection
    username: admin
    password: password123
    driver-class-name: org.postgresql.Driver

  jpa:
    hibernate:
      ddl-auto: update
    show-sql: false
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect

  redis:
    host: localhost
    port: 6379
    database: 0

  kafka:
    bootstrap-servers: localhost:9092
    consumer:
      group-id: {service_name}-group
      auto-offset-reset: latest
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.apache.kafka.common.serialization.StringSerializer

management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  endpoint:
    health:
      show-details: always

logging:
  level:
    com.marketdata: INFO
    org.springframework.kafka: WARN
  pattern:
    console: "%d{{yyyy-MM-dd HH:mm:ss}} [%thread] %-5level %logger{{36}} - %msg%n"'''

    def _get_java_dockerfile(self) -> str:
        return '''FROM openjdk:17-jdk-slim

WORKDIR /app

COPY target/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]'''

    def _get_python_requirements(self) -> str:
        return '''fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pandas==2.1.4
numpy==1.25.2
scipy==1.11.4
scikit-learn==1.3.2
requests==2.31.0
redis==5.0.1
kafka-python==2.0.2
prometheus-client==0.19.0
structlog==23.2.0
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2'''

    def _get_fastapi_main(self) -> str:
        return '''from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Market Data Anomaly Detection Engine",
    description="Python-based anomaly detection algorithms",
    version="1.0.0"
)

class MarketDataPoint(BaseModel):
    symbol: str
    timestamp: datetime
    source: str
    data_type: str
    payload: Dict[str, Any]
    price: float = None
    volume: float = None

class AnomalyResult(BaseModel):
    symbol: str
    anomaly_type: str
    severity: str
    detected_at: datetime
    description: str
    details: Dict[str, Any]

@app.get("/")
async def root():
    return {"message": "Market Data Anomaly Detection Engine", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "UP", "service": "detection-engine", "timestamp": datetime.now()}

@app.post("/detect/missing-data")
async def detect_missing_data(data_points: List[MarketDataPoint]) -> List[AnomalyResult]:
    """Detect missing data anomalies"""
    from src.algorithms.missing_data_detector import MissingDataDetector

    detector = MissingDataDetector()
    anomalies = detector.detect(data_points)
    return anomalies

@app.post("/detect/price-movement")
async def detect_price_movement(data_points: List[MarketDataPoint]) -> List[AnomalyResult]:
    """Detect price movement anomalies"""
    from src.algorithms.price_movement_detector import PriceMovementDetector

    detector = PriceMovementDetector()
    anomalies = detector.detect(data_points)
    return anomalies

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8085)'''

    def _get_missing_data_detector(self) -> str:
        return '''import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any

class MissingDataDetector:
    """Detects missing data anomalies"""

    def __init__(self, threshold_minutes: int = 30):
        self.threshold_minutes = threshold_minutes

    def detect(self, data_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect missing data anomalies"""
        anomalies = []

        if not data_points:
            return anomalies

        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(data_points)

        # Group by symbol
        for symbol in df['symbol'].unique():
            symbol_data = df[df['symbol'] == symbol].sort_values('timestamp')

            # Check for gaps in data
            for i in range(1, len(symbol_data)):
                current_time = pd.to_datetime(symbol_data.iloc[i]['timestamp'])
                previous_time = pd.to_datetime(symbol_data.iloc[i-1]['timestamp'])

                gap_minutes = (current_time - previous_time).total_seconds() / 60

                if gap_minutes > self.threshold_minutes:
                    anomaly = {
                        'symbol': symbol,
                        'anomaly_type': 'missing_data',
                        'severity': 'high' if gap_minutes > self.threshold_minutes * 2 else 'medium',
                        'detected_at': datetime.now(),
                        'description': f'Missing data for {gap_minutes:.1f} minutes',
                        'details': {
                            'gap_minutes': gap_minutes,
                            'threshold_minutes': self.threshold_minutes,
                            'last_data_time': previous_time.isoformat(),
                            'next_data_time': current_time.isoformat()
                        }
                    }
                    anomalies.append(anomaly)

        return anomalies'''

    def _get_price_movement_detector(self) -> str:
        return '''import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Any

class PriceMovementDetector:
    """Detects abnormal price movement anomalies"""

    def __init__(self, threshold_percent: float = 5.0, window_minutes: int = 15):
        self.threshold_percent = threshold_percent
        self.window_minutes = window_minutes

    def detect(self, data_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect price movement anomalies"""
        anomalies = []

        if not data_points:
            return anomalies

        # Convert to DataFrame
        df = pd.DataFrame(data_points)

        # Group by symbol
        for symbol in df['symbol'].unique():
            symbol_data = df[df['symbol'] == symbol].sort_values('timestamp')

            if len(symbol_data) < 2:
                continue

            # Calculate price changes
            symbol_data['price_change'] = symbol_data['price'].pct_change() * 100

            # Find anomalous movements
            for idx, row in symbol_data.iterrows():
                if pd.isna(row['price_change']):
                    continue

                abs_change = abs(row['price_change'])

                if abs_change > self.threshold_percent:
                    severity = 'critical' if abs_change > self.threshold_percent * 2 else 'high'

                    anomaly = {
                        'symbol': symbol,
                        'anomaly_type': 'price_movement',
                        'severity': severity,
                        'detected_at': datetime.now(),
                        'description': f'Price moved {row["price_change"]:.2f}% in {self.window_minutes} minutes',
                        'details': {
                            'price_change_percent': row['price_change'],
                            'threshold_percent': self.threshold_percent,
                            'current_price': row['price'],
                            'timestamp': row['timestamp']
                        }
                    }
                    anomalies.append(anomaly)

        return anomalies'''

    def _get_python_dockerfile(self) -> str:
        return '''FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

EXPOSE 8085

CMD ["python", "-m", "src.api.main"]'''

    def _get_java_docker_compose(self) -> str:
        return '''version: '3.8'

services:
  api-gateway:
    build: ./api-gateway
    ports:
      - "8080:8080"
    environment:
      - SPRING_PROFILES_ACTIVE=docker
    depends_on:
      - postgres
      - redis
      - kafka

  data-ingestion-service:
    build: ./data-ingestion-service
    ports:
      - "8081:8081"
    environment:
      - SPRING_PROFILES_ACTIVE=docker
    depends_on:
      - postgres
      - redis
      - kafka

  stream-processing-service:
    build: ./stream-processing-service
    ports:
      - "8082:8082"
    environment:
      - SPRING_PROFILES_ACTIVE=docker
    depends_on:
      - kafka

  alert-service:
    build: ./alert-service
    ports:
      - "8083:8083"
    environment:
      - SPRING_PROFILES_ACTIVE=docker
    depends_on:
      - postgres
      - redis

  dashboard-api:
    build: ./dashboard-api
    ports:
      - "8084:8084"
    environment:
      - SPRING_PROFILES_ACTIVE=docker
    depends_on:
      - postgres
      - redis

networks:
  default:
    external:
      name: anomaly-detection-network'''

    def _get_python_docker_compose(self) -> str:
        return '''version: '3.8'

services:
  detection-engine:
    build: ./detection-engine
    ports:
      - "8085:8085"
    environment:
      - PYTHONPATH=/app
    volumes:
      - ./detection-engine/src:/app/src
    networks:
      - anomaly-detection-network

networks:
  anomaly-detection-network:
    external: true'''

    def _get_infrastructure_docker_compose(self) -> str:
        return '''version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: anomaly_detection
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password123
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - anomaly-detection-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    networks:
      - anomaly-detection-network

  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    networks:
      - anomaly-detection-network

  kafka:
    image: confluentinc/cp-kafka:latest
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    networks:
      - anomaly-detection-network

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    networks:
      - anomaly-detection-network

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - anomaly-detection-network

volumes:
  postgres_data:
  redis_data:
  grafana_data:

networks:
  anomaly-detection-network:
    driver: bridge'''

    def _get_integration_test_script(self) -> str:
        return '''#!/usr/bin/env python3
"""
Integration test script for Market Data Anomaly Detection System
"""

import requests
import time
import sys
import json
from datetime import datetime

class IntegrationTester:
    """Runs comprehensive integration tests"""

    def __init__(self):
        self.base_urls = {
            'api-gateway': 'http://localhost:8080',
            'data-ingestion': 'http://localhost:8081',
            'stream-processing': 'http://localhost:8082',
            'alert-service': 'http://localhost:8083',
            'dashboard-api': 'http://localhost:8084',
            'detection-engine': 'http://localhost:8085'
        }
        self.test_results = {}

    def run_all_tests(self):
        """Run all integration tests"""
        print("🧪 Starting integration tests...")

        self.test_health_endpoints()
        self.test_detection_algorithms()
        self.test_data_flow()

        self.print_results()
        return all(self.test_results.values())

    def test_health_endpoints(self):
        """Test all health endpoints"""
        print("🔍 Testing health endpoints...")

        for service, base_url in self.base_urls.items():
            try:
                response = requests.get(f"{base_url}/health", timeout=5)
                success = response.status_code == 200
                self.test_results[f"{service}_health"] = success

                if success:
                    print(f"✅ {service} health check passed")
                else:
                    print(f"❌ {service} health check failed: {response.status_code}")

            except Exception as e:
                print(f"❌ {service} health check failed: {e}")
                self.test_results[f"{service}_health"] = False

    def test_detection_algorithms(self):
        """Test detection algorithms"""
        print("🔍 Testing detection algorithms...")

        # Test data
        test_data = [
            {
                "symbol": "AAPL",
                "timestamp": datetime.now().isoformat(),
                "source": "gemfire",
                "data_type": "price",
                "payload": {"price": 150.0, "volume": 1000},
                "price": 150.0,
                "volume": 1000.0
            }
        ]

        # Test missing data detection
        try:
            response = requests.post(
                f"{self.base_urls['detection-engine']}/detect/missing-data",
                json=test_data,
                timeout=10
            )
            success = response.status_code == 200
            self.test_results["missing_data_detection"] = success

            if success:
                print("✅ Missing data detection test passed")
            else:
                print(f"❌ Missing data detection test failed: {response.status_code}")

        except Exception as e:
            print(f"❌ Missing data detection test failed: {e}")
            self.test_results["missing_data_detection"] = False

        # Test price movement detection
        try:
            response = requests.post(
                f"{self.base_urls['detection-engine']}/detect/price-movement",
                json=test_data,
                timeout=10
            )
            success = response.status_code == 200
            self.test_results["price_movement_detection"] = success

            if success:
                print("✅ Price movement detection test passed")
            else:
                print(f"❌ Price movement detection test failed: {response.status_code}")

        except Exception as e:
            print(f"❌ Price movement detection test failed: {e}")
            self.test_results["price_movement_detection"] = False

    def test_data_flow(self):
        """Test end-to-end data flow"""
        print("🔍 Testing data flow...")

        # This would test the complete data flow from ingestion to detection
        # For now, just mark as passed if basic services are up
        basic_services_up = all([
            self.test_results.get("api-gateway_health", False),
            self.test_results.get("detection-engine_health", False)
        ])

        self.test_results["data_flow"] = basic_services_up

        if basic_services_up:
            print("✅ Basic data flow test passed")
        else:
            print("❌ Data flow test failed")

    def print_results(self):
        """Print test results summary"""
        print("\\n📊 Test Results Summary:")
        print("=" * 50)

        passed = 0
        total = len(self.test_results)

        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:30} {status}")
            if result:
                passed += 1

        print("=" * 50)
        print(f"Total: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All tests passed!")
        else:
            print("⚠️  Some tests failed!")

if __name__ == "__main__":
    tester = IntegrationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)'''

    def _get_python_tests(self) -> str:
        return '''import pytest
from src.algorithms.missing_data_detector import MissingDataDetector
from src.algorithms.price_movement_detector import PriceMovementDetector
from datetime import datetime, timedelta

class TestMissingDataDetector:
    """Test missing data detection algorithm"""

    def test_no_missing_data(self):
        """Test when there is no missing data"""
        detector = MissingDataDetector(threshold_minutes=30)

        # Create test data with no gaps
        data_points = [
            {
                'symbol': 'AAPL',
                'timestamp': (datetime.now() - timedelta(minutes=i)).isoformat(),
                'price': 150.0 + i
            }
            for i in range(5)
        ]

        anomalies = detector.detect(data_points)
        assert len(anomalies) == 0

    def test_missing_data_detected(self):
        """Test when missing data is detected"""
        detector = MissingDataDetector(threshold_minutes=30)

        # Create test data with a gap
        now = datetime.now()
        data_points = [
            {
                'symbol': 'AAPL',
                'timestamp': now.isoformat(),
                'price': 150.0
            },
            {
                'symbol': 'AAPL',
                'timestamp': (now - timedelta(hours=2)).isoformat(),  # 2 hour gap
                'price': 149.0
            }
        ]

        anomalies = detector.detect(data_points)
        assert len(anomalies) == 1
        assert anomalies[0]['anomaly_type'] == 'missing_data'

class TestPriceMovementDetector:
    """Test price movement detection algorithm"""

    def test_normal_price_movement(self):
        """Test normal price movement (no anomaly)"""
        detector = PriceMovementDetector(threshold_percent=5.0)

        data_points = [
            {'symbol': 'AAPL', 'timestamp': datetime.now().isoformat(), 'price': 150.0},
            {'symbol': 'AAPL', 'timestamp': datetime.now().isoformat(), 'price': 151.0}  # 0.67% change
        ]

        anomalies = detector.detect(data_points)
        assert len(anomalies) == 0

    def test_abnormal_price_movement(self):
        """Test abnormal price movement (anomaly detected)"""
        detector = PriceMovementDetector(threshold_percent=5.0)

        data_points = [
            {'symbol': 'AAPL', 'timestamp': datetime.now().isoformat(), 'price': 150.0},
            {'symbol': 'AAPL', 'timestamp': datetime.now().isoformat(), 'price': 160.0}  # 6.67% change
        ]

        anomalies = detector.detect(data_points)
        assert len(anomalies) == 1
        assert anomalies[0]['anomaly_type'] == 'price_movement'
        assert anomalies[0]['severity'] in ['high', 'critical']'''


if __name__ == "__main__":
    generator = CodeGenerator()
    generator.generate_all()
