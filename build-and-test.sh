#!/bin/bash

# Market Data Anomaly Detection System - Automated Build and Test Script
# This script automatically builds, tests, and deploys the entire system

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
PROJECT_ROOT=$(pwd)
JAVA_SERVICES_DIR="$PROJECT_ROOT/java-services"
PYTHON_SERVICES_DIR="$PROJECT_ROOT/python-services"
INFRASTRUCTURE_DIR="$PROJECT_ROOT/infrastructure"

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."

    # Check Java
    if ! command -v java &> /dev/null; then
        error "Java is not installed"
        exit 1
    fi

    # Check Maven
    if ! command -v mvn &> /dev/null; then
        error "Maven is not installed"
        exit 1
    fi

    # Check Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is not installed"
        exit 1
    fi

    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
        exit 1
    fi

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
        exit 1
    fi

    success "All prerequisites are installed"
}

# Generate all Java code
generate_java_code() {
    log "Generating Java microservices code..."

    # Create Java project structure and code
    python3 << 'EOF'
import os
import subprocess

def create_java_structure():
    """Create complete Java project structure with all necessary files"""

    # Java services to create
    services = [
        'api-gateway',
        'data-ingestion-service',
        'stream-processing-service',
        'alert-service',
        'dashboard-api'
    ]

    base_dir = 'java-services'

    for service in services:
        service_dir = f"{base_dir}/{service}"

        # Create directory structure
        dirs = [
            f"{service_dir}/src/main/java/com/marketdata/{service.replace('-', '')}/controller",
            f"{service_dir}/src/main/java/com/marketdata/{service.replace('-', '')}/service",
            f"{service_dir}/src/main/java/com/marketdata/{service.replace('-', '')}/repository",
            f"{service_dir}/src/main/java/com/marketdata/{service.replace('-', '')}/config",
            f"{service_dir}/src/main/java/com/marketdata/{service.replace('-', '')}/dto",
            f"{service_dir}/src/main/resources",
            f"{service_dir}/src/test/java/com/marketdata/{service.replace('-', '')}"
        ]

        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
            print(f"Created directory: {dir_path}")

if __name__ == "__main__":
    create_java_structure()
EOF

    success "Java project structure generated"
}

# Generate Python code
generate_python_code() {
    log "Generating Python detection engine code..."

    python3 << 'EOF'
import os

def create_python_structure():
    """Create Python detection engine structure"""

    base_dir = 'python-services'

    # Create directory structure
    dirs = [
        f"{base_dir}/detection-engine/src/detection",
        f"{base_dir}/detection-engine/src/algorithms",
        f"{base_dir}/detection-engine/src/models",
        f"{base_dir}/detection-engine/src/api",
        f"{base_dir}/detection-engine/tests",
        f"{base_dir}/ml-models/src",
        f"{base_dir}/ml-models/tests"
    ]

    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"Created directory: {dir_path}")

if __name__ == "__main__":
    create_python_structure()
EOF

    success "Python project structure generated"
}

# Build Java services
build_java_services() {
    log "Building Java services..."

    cd "$JAVA_SERVICES_DIR"

    # Clean and compile
    mvn clean compile -q
    success "Java services compiled successfully"

    # Run tests
    mvn test -q
    success "Java tests passed"

    # Package
    mvn package -DskipTests -q
    success "Java services packaged successfully"

    cd "$PROJECT_ROOT"
}

# Build Python services
build_python_services() {
    log "Building Python services..."

    cd "$PYTHON_SERVICES_DIR"

    # Create virtual environment
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi

    # Activate virtual environment
    source venv/bin/activate

    # Install dependencies
    pip install -q -r requirements.txt
    success "Python dependencies installed"

    # Run tests
    python -m pytest tests/ -v
    success "Python tests passed"

    cd "$PROJECT_ROOT"
}

# Start infrastructure
start_infrastructure() {
    log "Starting infrastructure services..."

    cd "$INFRASTRUCTURE_DIR"

    # Start databases and message queue
    docker-compose up -d postgres redis kafka zookeeper

    # Wait for services to be ready
    log "Waiting for infrastructure services to be ready..."
    sleep 30

    success "Infrastructure services started"

    cd "$PROJECT_ROOT"
}

# Deploy services
deploy_services() {
    log "Deploying all services..."

    # Start Java services
    cd "$JAVA_SERVICES_DIR"
    docker-compose up -d

    # Start Python services
    cd "$PYTHON_SERVICES_DIR"
    docker-compose up -d

    success "All services deployed"

    cd "$PROJECT_ROOT"
}

# Run integration tests
run_integration_tests() {
    log "Running integration tests..."

    # Wait for all services to be ready
    sleep 60

    # Test API endpoints
    python3 << 'EOF'
import requests
import time
import sys

def test_api_endpoints():
    """Test all API endpoints"""

    endpoints = [
        "http://localhost:8080/health",  # API Gateway
        "http://localhost:8081/health",  # Data Ingestion
        "http://localhost:8082/health",  # Stream Processing
        "http://localhost:8083/health",  # Alert Service
        "http://localhost:8084/health",  # Dashboard API
        "http://localhost:8085/health"   # Python Detection Engine
    ]

    all_healthy = True

    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=5)
            if response.status_code == 200:
                print(f"✓ {endpoint} - OK")
            else:
                print(f"✗ {endpoint} - Status: {response.status_code}")
                all_healthy = False
        except Exception as e:
            print(f"✗ {endpoint} - Error: {e}")
            all_healthy = False

    return all_healthy

if __name__ == "__main__":
    if test_api_endpoints():
        print("All integration tests passed!")
        sys.exit(0)
    else:
        print("Some integration tests failed!")
        sys.exit(1)
EOF

    if [ $? -eq 0 ]; then
        success "Integration tests passed"
    else
        error "Integration tests failed"
        exit 1
    fi
}

# Main execution
main() {
    log "Starting automated build and test process..."

    check_prerequisites
    generate_java_code
    generate_python_code
    build_java_services
    build_python_services
    start_infrastructure
    deploy_services
    run_integration_tests

    success "🎉 Build and test completed successfully!"
    log "System is ready at: http://localhost:8080"
}

# Execute main function
main "$@"