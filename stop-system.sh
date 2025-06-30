#!/bin/bash

# Stop script for Market Data Anomaly Detection System

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

main() {
    echo "🛑 Stopping Market Data Anomaly Detection System..."
    echo "=================================================="
    
    # Stop Python services
    log "Stopping Python services..."
    cd python-services
    docker-compose down 2>/dev/null || true
    cd ..
    success "Python services stopped"
    
    # Stop Java services
    log "Stopping Java services..."
    cd java-services
    docker-compose down 2>/dev/null || true
    cd ..
    success "Java services stopped"
    
    # Stop infrastructure
    log "Stopping infrastructure services..."
    cd infrastructure
    docker-compose down 2>/dev/null || true
    cd ..
    success "Infrastructure services stopped"
    
    # Remove network
    log "Removing Docker network..."
    docker network rm anomaly-detection-network 2>/dev/null || true
    success "Docker network removed"
    
    echo ""
    echo "✅ System stopped successfully!"
}

main "$@"
