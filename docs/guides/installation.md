# Installation Guide

Complete installation guide for LOKI Interceptor.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation Methods](#installation-methods)
3. [Configuration](#configuration)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.8 | 3.10+ |
| RAM | 4 GB | 8 GB |
| Disk | 2 GB | 10 GB SSD |
| OS | Windows/macOS/Linux | Ubuntu 20.04+ |

### Required Software

- **Git** - Version control
- **Python** - Programming language
- **pip** - Python package manager
- **curl** (optional) - For testing API

### Optional Software

- **Docker** - Container runtime
- **Docker Compose** - Multi-container orchestration
- **Postman** - API testing tool

---

## Installation Methods

### Method 1: Local Installation (Recommended for Development)

#### Step 1: Clone Repository

```bash
# Clone the main repository
git clone https://github.com/Johnobhoy88/loki-interceptor.git
cd loki-interceptor

# Or clone your fork
git clone https://github.com/YOUR_USERNAME/loki-interceptor.git
cd loki-interceptor
```

#### Step 2: Create Virtual Environment

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows (Command Prompt)
python -m venv venv
venv\Scripts\activate

# Windows (PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1

# Verify activation (should show "venv" prefix)
which python  # macOS/Linux
where python  # Windows
```

#### Step 3: Upgrade pip

```bash
# macOS/Linux/Windows
python -m pip install --upgrade pip

# Verify
pip --version
```

#### Step 4: Install Dependencies

```bash
# Standard installation
pip install -r requirements.txt

# Or with extras
pip install -r requirements.txt  # All packages

# For development
pip install -r requirements-dev.txt
```

**Note**: If installation fails:
```bash
# Try with no cache
pip install --no-cache-dir -r requirements.txt

# Or install step by step
pip install fastapi uvicorn pydantic anthropic requests
```

#### Step 5: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API key
nano .env  # or use your preferred editor

# On Windows
copy .env.example .env
```

Edit `.env`:
```env
# Required
ANTHROPIC_API_KEY=your_api_key_here

# Optional - defaults shown
CLAUDE_MODEL=claude-3-5-sonnet-20241022
LOG_LEVEL=INFO
MAX_TOKENS=4096
TEMPERATURE=0.0
```

#### Step 6: Verify Installation

```bash
# Test Python imports
python -c "from backend.core.document_validator import DocumentValidator"

# Should print nothing and exit successfully
# If error appears, dependencies not installed correctly
```

---

### Method 2: Docker Installation (Recommended for Production)

#### Step 1: Install Docker

```bash
# macOS
brew install docker
docker --version

# Ubuntu/Debian
sudo apt update
sudo apt install docker.io
sudo docker --version

# Windows - Download Docker Desktop
# https://www.docker.com/products/docker-desktop
```

#### Step 2: Clone Repository

```bash
git clone https://github.com/Johnobhoy88/loki-interceptor.git
cd loki-interceptor
```

#### Step 3: Build Docker Image

```bash
# Build image
docker build -t loki-interceptor:1.0.0 -f backend/Dockerfile .

# Verify build
docker image ls | grep loki
```

#### Step 4: Create `.env` File

```bash
# Copy example
cp .env.example .env

# Edit with your API key
nano .env
```

#### Step 5: Run Docker Container

```bash
# Basic run
docker run \
  -e ANTHROPIC_API_KEY=your_key_here \
  -p 8000:8000 \
  loki-interceptor:1.0.0

# With logging
docker run \
  -e ANTHROPIC_API_KEY=your_key_here \
  -p 8000:8000 \
  -v $(pwd)/logs:/app/logs \
  loki-interceptor:1.0.0

# In background
docker run -d \
  -e ANTHROPIC_API_KEY=your_key_here \
  -p 8000:8000 \
  --name loki \
  loki-interceptor:1.0.0
```

#### Step 6: Using Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Restart
docker-compose restart
```

---

### Method 3: Cloud Platform Installation

#### AWS EC2

```bash
# Launch Ubuntu 20.04 instance
# Connect via SSH

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3.10 python3-pip -y

# Clone and install
git clone https://github.com/Johnobhoy88/loki-interceptor.git
cd loki-interceptor
pip install -r requirements.txt

# Copy environment
cp .env.example .env
# Edit .env with your API key

# Run
python -m backend.api.main
```

#### Google Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/loki

# Deploy
gcloud run deploy loki \
  --image gcr.io/PROJECT_ID/loki \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --set-env-vars ANTHROPIC_API_KEY=your_key
```

#### Azure App Service

```bash
# Create resource group
az group create --name loki-rg --location eastus

# Create App Service plan
az appservice plan create \
  --name loki-plan \
  --resource-group loki-rg \
  --sku B2

# Deploy
az webapp deployment source config-zip \
  --resource-group loki-rg \
  --name loki-api \
  --src deployment.zip
```

---

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | Yes | - | Your Anthropic API key |
| `CLAUDE_MODEL` | No | `claude-3-5-sonnet-20241022` | Claude model to use |
| `LOG_LEVEL` | No | `INFO` | Logging level |
| `MAX_TOKENS` | No | `4096` | Maximum tokens |
| `TEMPERATURE` | No | `0.0` | Model temperature |
| `CACHE_ENABLED` | No | `true` | Enable caching |
| `CACHE_TTL` | No | `3600` | Cache TTL (seconds) |
| `CACHE_MAX_SIZE` | No | `1000` | Max cache entries |
| `UVICORN_HOST` | No | `127.0.0.1` | API host |
| `UVICORN_PORT` | No | `8000` | API port |

### Basic Configuration

```bash
# Minimal setup
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# Start
python -m backend.api.main
```

### Advanced Configuration

```env
# API Configuration
ANTHROPIC_API_KEY=your_key_here
CLAUDE_MODEL=claude-3-5-sonnet-20241022
MAX_TOKENS=4096
TEMPERATURE=0.0

# Server Configuration
UVICORN_HOST=0.0.0.0
UVICORN_PORT=8000
UVICORN_WORKERS=4

# Cache Configuration
CACHE_ENABLED=true
CACHE_TTL=3600
CACHE_MAX_SIZE=1000

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json

# CORS Configuration
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60
```

---

## Verification

### Check Installation

```bash
# Test imports
python << 'EOF'
from backend.core.document_validator import DocumentValidator
from backend.core.document_corrector import DocumentCorrector
print("✓ All imports successful")
EOF

# Output should be: ✓ All imports successful
```

### Start the API

```bash
# Development mode (with auto-reload)
python -m backend.api.main

# Should show:
# 🚀 Starting LOKI Interceptor API...
# INFO:     Application startup complete [uvicorn]
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Test Health Endpoint

```bash
# In another terminal
curl http://localhost:8000/api/health

# Should return:
# {
#   "status": "healthy",
#   "version": "1.0.0",
#   "modules_loaded": 5,
#   "uptime_seconds": 2.5
# }
```

### Test Validation

```bash
curl -X POST http://localhost:8000/api/v1/validate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is a test document",
    "document_type": "financial",
    "modules": ["fca_uk"]
  }'

# Should return validation results
```

### View API Documentation

Open in browser:
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

---

## Troubleshooting

### Import Errors

```bash
# Error: ModuleNotFoundError: No module named 'backend'

# Solution 1: Activate virtual environment
source venv/bin/activate

# Solution 2: Install dependencies
pip install -r requirements.txt

# Solution 3: Check Python path
python -c "import sys; print(sys.path)"
```

### Missing API Key

```bash
# Error: KeyError: 'ANTHROPIC_API_KEY'

# Solution 1: Create .env file
cp .env.example .env

# Solution 2: Add API key
echo "ANTHROPIC_API_KEY=your_key" >> .env

# Solution 3: Export as environment variable
export ANTHROPIC_API_KEY=your_key
python -m backend.api.main
```

### Port Already in Use

```bash
# Error: Address already in use

# Solution 1: Kill existing process
lsof -i :8000
kill -9 <PID>

# Solution 2: Use different port
UVICORN_PORT=8001 python -m backend.api.main

# Solution 3: Check what's using the port
netstat -tulpn | grep 8000
```

### Virtual Environment Issues

```bash
# Error: (venv) prompt not showing

# Solution 1: Verify activation
which python  # Should show venv path

# Solution 2: Re-activate
source venv/bin/activate

# Solution 3: Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Next Steps

After installation:

1. **Read** [User Manual](user-manual.md)
2. **Run** a [Quick Start](../INDEX.md#quick-start)
3. **Check** [API Examples](../api/examples.md)
4. **Review** [Deployment Guide](../deployment/README.md) for production setup

---

**See also**: [Configuration Guide](configuration.md) | [Troubleshooting](../troubleshooting/README.md)

**Version**: 1.0.0
**Last Updated**: 2025-11-11
