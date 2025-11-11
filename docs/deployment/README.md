# Deployment Guide

Production deployment guide for LOKI Interceptor API.

## Table of Contents
1. [Deployment Options](#deployment-options)
2. [System Requirements](#system-requirements)
3. [Quick Start](#quick-start)
4. [Docker Deployment](#docker-deployment)
5. [Cloud Deployment](#cloud-deployment)
6. [Production Configuration](#production-configuration)
7. [Monitoring & Logging](#monitoring--logging)
8. [Troubleshooting](#troubleshooting)

---

## Deployment Options

### Option 1: Local Development
- **Best for**: Development and testing
- **Setup time**: 5 minutes
- **Requirements**: Python 3.8+
- [Quick Start](#quick-start)

### Option 2: Docker Container
- **Best for**: Isolated environments
- **Setup time**: 10 minutes
- **Requirements**: Docker installed
- [Docker Deployment](#docker-deployment)

### Option 3: Cloud Platform
- **Best for**: Production environments
- **Setup time**: 20-30 minutes
- **Options**: AWS, GCP, Azure
- [Cloud Deployment](#cloud-deployment)

---

## System Requirements

### Minimum Specifications
| Component | Requirement |
|-----------|-------------|
| CPU | 2 cores |
| RAM | 4 GB |
| Disk | 2 GB |
| OS | Linux, macOS, Windows |
| Python | 3.8+ |

### Recommended Specifications
| Component | Recommendation |
|-----------|----------------|
| CPU | 4+ cores |
| RAM | 8+ GB |
| Disk | 10+ GB SSD |
| OS | Ubuntu 20.04 LTS |
| Python | 3.10+ |

---

## Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/Johnobhoy88/loki-interceptor.git
cd loki-interceptor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create configuration
cp .env.example .env
```

### 2. Configuration

Edit `.env`:

```env
# Required
ANTHROPIC_API_KEY=your_api_key_here

# Optional (defaults shown)
CLAUDE_MODEL=claude-3-5-sonnet-20241022
LOG_LEVEL=INFO
MAX_TOKENS=4096
TEMPERATURE=0.0
CACHE_ENABLED=true
CACHE_TTL=3600
```

### 3. Start Server

```bash
# Development with auto-reload
python -m backend.api.main

# Production (see section below)
gunicorn -w 4 -b 0.0.0.0:8000 backend.api.main:app
```

### 4. Verify Installation

```bash
# Check health
curl http://localhost:8000/api/health

# View API docs
# Open http://localhost:8000/api/docs
```

---

## Docker Deployment

### Build Docker Image

```bash
# Build
docker build -t loki-interceptor:1.0.0 -f backend/Dockerfile .

# Tag
docker tag loki-interceptor:1.0.0 loki-interceptor:latest
```

### Run Container

```bash
docker run \
  -e ANTHROPIC_API_KEY=your_key_here \
  -e LOG_LEVEL=INFO \
  -p 8000:8000 \
  loki-interceptor:latest
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: backend/Dockerfile
    container_name: loki-api
    ports:
      - "8000:8000"
    environment:
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      LOG_LEVEL: ${LOG_LEVEL:-INFO}
      CLAUDE_MODEL: ${CLAUDE_MODEL:-claude-3-5-sonnet-20241022}
      CACHE_ENABLED: "true"
      CACHE_TTL: "3600"
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  logs:
  data:
```

### Start with Docker Compose

```bash
# Create .env file
cp .env.example .env

# Start services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

---

## Cloud Deployment

### AWS EC2

```bash
# 1. Launch EC2 instance (Ubuntu 20.04)
# Instance type: t3.medium (minimum)

# 2. Connect and setup
ssh -i your-key.pem ubuntu@your-instance-ip

# 3. Install dependencies
sudo apt update
sudo apt install python3.10 python3-pip git

# 4. Clone and configure
git clone https://github.com/Johnobhoy88/loki-interceptor.git
cd loki-interceptor
pip install -r requirements.txt
cp .env.example .env

# 5. Create systemd service
sudo tee /etc/systemd/system/loki.service > /dev/null <<EOF
[Unit]
Description=LOKI Interceptor API
After=network.target

[Service]
Type=notify
User=ubuntu
WorkingDirectory=/home/ubuntu/loki-interceptor
ExecStart=/home/ubuntu/.venv/bin/python -m backend.api.main
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 6. Start service
sudo systemctl enable loki
sudo systemctl start loki
```

### AWS Fargate

```yaml
# task-definition.json
{
  "family": "loki-interceptor",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "your-account.dkr.ecr.us-east-1.amazonaws.com/loki:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "hostPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "LOG_LEVEL",
          "value": "INFO"
        }
      ],
      "secrets": [
        {
          "name": "ANTHROPIC_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:account:secret:loki/api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/loki",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Google Cloud Run

```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/loki

# Deploy
gcloud run deploy loki \
  --image gcr.io/PROJECT_ID/loki \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --set-env-vars ANTHROPIC_API_KEY=your_key \
  --allow-unauthenticated
```

### Azure App Service

```bash
# Create resource group
az group create \
  --name loki-rg \
  --location eastus

# Create App Service plan
az appservice plan create \
  --name loki-plan \
  --resource-group loki-rg \
  --sku B2

# Deploy from GitHub
az webapp create \
  --resource-group loki-rg \
  --plan loki-plan \
  --name loki-api \
  --deployment-source-url https://github.com/Johnobhoy88/loki-interceptor
```

---

## Production Configuration

### Environment Variables

```env
# Core
ANTHROPIC_API_KEY=your_production_key

# API
UVICORN_HOST=0.0.0.0
UVICORN_PORT=8000
UVICORN_WORKERS=4
UVICORN_LOG_LEVEL=info

# Model
CLAUDE_MODEL=claude-3-5-sonnet-20241022
MAX_TOKENS=4096
TEMPERATURE=0.0

# Cache
CACHE_ENABLED=true
CACHE_TTL=3600
CACHE_MAX_SIZE=1000

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/loki/api.log

# Security
CORS_ORIGINS=https://yourdomain.com
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60
```

### Gunicorn Configuration

Create `gunicorn.conf.py`:

```python
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
max_requests = 1000
max_requests_jitter = 100
timeout = 120
keepalive = 5
accesslog = "/var/log/loki/access.log"
errorlog = "/var/log/loki/error.log"
loglevel = "info"
```

### Nginx Configuration

```nginx
upstream loki {
    server localhost:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/m;
    limit_req zone=api_limit burst=10 nodelay;

    # Compression
    gzip on;
    gzip_types application/json;
    gzip_min_length 1000;

    location / {
        proxy_pass http://loki;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /api/health {
        proxy_pass http://loki;
        access_log off;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

---

## Monitoring & Logging

### Health Checks

```bash
# Basic health check
curl http://localhost:8000/api/health

# Expected response
{
  "status": "healthy",
  "version": "1.0.0",
  "modules_loaded": 5,
  "uptime_seconds": 3600
}
```

### Logging Setup

```python
import logging
from logging.handlers import RotatingFileHandler

# Create logger
logger = logging.getLogger(__name__)

# File handler with rotation
handler = RotatingFileHandler(
    '/var/log/loki/api.log',
    maxBytes=10485760,  # 10MB
    backupCount=10
)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
```

### Metrics Collection

```python
from prometheus_client import Counter, Histogram

# Request metrics
request_count = Counter(
    'loki_requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'loki_request_duration_seconds',
    'Request duration',
    ['method', 'endpoint']
)

# Validation metrics
validations_total = Counter(
    'loki_validations_total',
    'Total validations',
    ['module', 'result']
)

corrections_total = Counter(
    'loki_corrections_total',
    'Total corrections',
    ['success']
)
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
UVICORN_PORT=8001 python -m backend.api.main
```

### Memory Issues

```bash
# Monitor memory usage
watch -n 1 'ps aux | grep python'

# Reduce cache size
CACHE_MAX_SIZE=100 python -m backend.api.main

# Limit workers
UVICORN_WORKERS=2 python -m backend.api.main
```

### API Key Errors

```bash
# Verify key is set
echo $ANTHROPIC_API_KEY

# Test API key
curl -H "Authorization: Bearer $ANTHROPIC_API_KEY" \
  https://api.anthropic.com/v1/messages
```

### Connection Issues

```bash
# Test connectivity
curl -v http://localhost:8000/api/health

# Check firewall
sudo ufw allow 8000/tcp

# Test remote connection
curl -v http://your-server-ip:8000/api/health
```

---

## Security Considerations

1. **API Keys**: Use environment variables, never commit to repo
2. **CORS**: Configure for your domain only
3. **HTTPS**: Use SSL/TLS in production
4. **Rate Limiting**: Implement per-IP limits
5. **Input Validation**: All inputs are validated
6. **Logging**: Don't log sensitive data

---

**See also**: [Docker Deployment](docker.md) | [Cloud Deployment](cloud.md) | [Configuration](configuration.md)

**Version**: 1.0.0
**Last Updated**: 2025-11-11
