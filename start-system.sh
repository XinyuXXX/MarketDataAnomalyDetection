#!/bin/bash

# One-click start script for Market Data Anomaly Detection System
# This script generates code, builds, and starts the entire system automatically

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

error() {
    echo -e "${RED}❌${NC} $1"
}

# Main execution
main() {
    echo "🚀 Starting Market Data Anomaly Detection System..."
    echo "=================================================="
    
    # Step 1: Generate all code
    log "Step 1: Generating code..."
    python3 generate-code.py
    success "Code generation completed"
    
    # Step 2: Create Docker network
    log "Step 2: Creating Docker network..."
    docker network create anomaly-detection-network 2>/dev/null || true
    success "Docker network ready"
    
    # Step 3: Start infrastructure
    log "Step 3: Starting infrastructure services..."
    cd infrastructure
    docker-compose up -d
    cd ..
    success "Infrastructure services started"
    
    # Step 4: Build and start Java services
    log "Step 4: Building Java services..."
    cd java-services
    mvn clean package -DskipTests -q
    success "Java services built"
    
    log "Starting Java services..."
    docker-compose up -d
    cd ..
    success "Java services started"
    
    # Step 5: Start Python services
    log "Step 5: Starting Python services..."
    cd python-services
    docker-compose up -d
    cd ..
    success "Python services started"
    
    # Step 6: Wait for services to be ready
    log "Step 6: Waiting for services to be ready..."
    sleep 30
    
    # Step 7: Run tests
    log "Step 7: Running integration tests..."
    python3 run-tests.py
    
    echo ""
    echo "🎉 System is ready!"
    echo "=================================================="
    echo "📊 Service URLs:"
    echo "   API Gateway:      http://localhost:8080"
    echo "   Data Ingestion:   http://localhost:8081"
    echo "   Stream Processing: http://localhost:8082"
    echo "   Alert Service:    http://localhost:8083"
    echo "   Dashboard API:    http://localhost:8084"
    echo "   Detection Engine: http://localhost:8085"
    echo "   Grafana:          http://localhost:3000 (admin/admin)"
    echo "   Prometheus:       http://localhost:9090"
    echo ""
    echo "🔧 Management Commands:"
    echo "   Stop system:      docker-compose down (in each service directory)"
    echo "   View logs:        docker-compose logs -f [service-name]"
    echo "   Restart service:  docker-compose restart [service-name]"
    echo ""
}

# Cleanup function
cleanup() {
    echo ""
    warning "Cleaning up..."
    cd infrastructure && docker-compose down 2>/dev/null || true
    cd ../java-services && docker-compose down 2>/dev/null || true  
    cd ../python-services && docker-compose down 2>/dev/null || true
    cd ..
}

# Trap cleanup on exit
trap cleanup EXIT

# Execute main function
main "$@"
