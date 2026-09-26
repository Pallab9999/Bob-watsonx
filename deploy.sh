#!/bin/bash

# MCP Server Deployment Script
# This script sets up and deploys the MCP Server for watsonx Orchestrate

set -e

echo "=========================================="
echo "MCP Server Deployment Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PYTHON_VERSION="3.8"
VENV_DIR="venv"
PORT=${MCP_PORT:-8000}
HOST=${MCP_HOST:-0.0.0.0}

# Functions
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[i]${NC} $1"
}

# Check Python version
check_python() {
    print_info "Checking Python installation..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_status "Python $PYTHON_VERSION found"
}

# Create virtual environment
create_venv() {
    print_info "Creating virtual environment..."
    
    if [ -d "$VENV_DIR" ]; then
        print_info "Virtual environment already exists"
    else
        python3 -m venv "$VENV_DIR"
        print_status "Virtual environment created"
    fi
}

# Activate virtual environment
activate_venv() {
    print_info "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    print_status "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    print_info "Installing dependencies..."
    pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt
    print_status "Dependencies installed"
}

# Run tests
run_tests() {
    print_info "Running unit tests..."
    
    if pytest tests/ -v --tb=short; then
        print_status "All tests passed"
    else
        print_error "Some tests failed"
        exit 1
    fi
}

# Start server
start_server() {
    print_info "Starting MCP Server..."
    print_info "Server will run on http://$HOST:$PORT"
    
    export MCP_HOST=$HOST
    export MCP_PORT=$PORT
    
    python src/mcp_server/main.py
}

# Validate server
validate_server() {
    print_info "Validating server..."
    
    sleep 2
    
    if python src/mcp_server/client.py http://localhost:$PORT; then
        print_status "Server validation successful"
    else
        print_error "Server validation failed"
        exit 1
    fi
}

# Main deployment flow
main() {
    case "${1:-start}" in
        setup)
            check_python
            create_venv
            activate_venv
            install_dependencies
            print_status "Setup completed successfully"
            ;;
        test)
            activate_venv
            run_tests
            ;;
        start)
            activate_venv
            start_server
            ;;
        validate)
            validate_server
            ;;
        full)
            check_python
            create_venv
            activate_venv
            install_dependencies
            run_tests
            start_server
            ;;
        *)
            echo "Usage: $0 {setup|test|start|validate|full}"
            echo ""
            echo "Commands:"
            echo "  setup    - Set up the project (create venv, install dependencies)"
            echo "  test     - Run unit tests"
            echo "  start    - Start the MCP server"
            echo "  validate - Validate the running server"
            echo "  full     - Run full deployment (setup, test, start)"
            exit 1
            ;;
    esac
}

main "$@"

# Made with Bob
