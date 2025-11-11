#!/bin/bash
# Local development startup script
# Starts LOKI with Docker Compose for local development

set -e

echo "=================================="
echo "LOKI Local Development Setup"
echo "=================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠ Please update .env with your API keys before continuing"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker."
    exit 1
fi

echo "✓ Docker is running"

# Pull latest images if requested
if [ "$1" == "--pull" ]; then
    echo ""
    echo "Pulling latest images..."
    docker-compose pull
fi

# Build images
echo ""
echo "Building images..."
docker-compose build

# Start services
echo ""
echo "Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo ""
echo "Waiting for services to be healthy..."
sleep 10

# Check service health
echo ""
echo "Checking service health..."

check_service() {
    local service=$1
    local url=$2
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -f "$url" > /dev/null 2>&1; then
            echo "✓ $service is healthy"
            return 0
        fi
        echo "  Attempt $attempt/$max_attempts: $service not ready yet..."
        sleep 2
        ((attempt++))
    done

    echo "❌ $service failed to become healthy"
    return 1
}

check_service "Backend" "http://localhost:5002/health"
check_service "Frontend" "http://localhost/health"

# Show logs
echo ""
echo "=================================="
echo "LOKI is running!"
echo "=================================="
echo "Backend API:  http://localhost:5002"
echo "Frontend UI:  http://localhost"
echo "Prometheus:   http://localhost:9090 (if monitoring profile enabled)"
echo "Grafana:      http://localhost:3000 (if monitoring profile enabled)"
echo ""
echo "To view logs:    docker-compose logs -f"
echo "To stop:         docker-compose down"
echo "To restart:      docker-compose restart"
echo "=================================="
