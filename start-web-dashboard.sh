#!/bin/bash

# Market Data Anomaly Detection - Web Dashboard Startup Script

set -e

echo "🚀 Starting Market Data Anomaly Detection Web Dashboard..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Node.js is installed
check_nodejs() {
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 16+ to continue."
        exit 1
    fi
    
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 16 ]; then
        print_error "Node.js version 16+ is required. Current version: $(node --version)"
        exit 1
    fi
    
    print_success "Node.js $(node --version) detected"
}

# Check if npm is installed
check_npm() {
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install npm to continue."
        exit 1
    fi
    
    print_success "npm $(npm --version) detected"
}

# Install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    cd web-dashboard
    
    if [ ! -d "node_modules" ]; then
        npm install
        print_success "Dependencies installed successfully"
    else
        print_status "Dependencies already installed, checking for updates..."
        npm update
        print_success "Dependencies updated"
    fi
    
    cd ..
}

# Start development server
start_dev_server() {
    print_status "Starting development server..."
    cd web-dashboard
    
    # Set environment variables
    export REACT_APP_API_URL=http://localhost:8080/api/v1
    export PORT=3000
    
    print_success "Web Dashboard starting at http://localhost:3000"
    print_status "API endpoint: $REACT_APP_API_URL"
    print_warning "Make sure the backend services are running!"
    
    # Start the development server
    npm start
}

# Build for production
build_production() {
    print_status "Building for production..."
    cd web-dashboard
    
    # Set environment variables for production
    export REACT_APP_API_URL=http://localhost:8080/api/v1
    
    npm run build
    print_success "Production build completed in web-dashboard/build/"
    
    cd ..
}

# Start with Docker
start_docker() {
    print_status "Starting with Docker..."
    
    # Build and start the web dashboard container
    docker-compose -f infrastructure/docker-compose.yml up --build web-dashboard
}

# Main execution
main() {
    echo "=================================================="
    echo "  Market Data Anomaly Detection Web Dashboard"
    echo "=================================================="
    echo ""
    
    # Parse command line arguments
    case "${1:-dev}" in
        "dev"|"development")
            print_status "Starting in development mode..."
            check_nodejs
            check_npm
            install_dependencies
            start_dev_server
            ;;
        "build"|"production")
            print_status "Building for production..."
            check_nodejs
            check_npm
            install_dependencies
            build_production
            ;;
        "docker")
            print_status "Starting with Docker..."
            start_docker
            ;;
        "help"|"-h"|"--help")
            echo "Usage: $0 [dev|build|docker|help]"
            echo ""
            echo "Commands:"
            echo "  dev        Start development server (default)"
            echo "  build      Build for production"
            echo "  docker     Start with Docker"
            echo "  help       Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                 # Start development server"
            echo "  $0 dev             # Start development server"
            echo "  $0 build           # Build for production"
            echo "  $0 docker          # Start with Docker"
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Use '$0 help' for usage information."
            exit 1
            ;;
    esac
}

# Trap Ctrl+C and cleanup
cleanup() {
    print_warning "Shutting down..."
    exit 0
}

trap cleanup SIGINT SIGTERM

# Run main function
main "$@"
