# PLATINUM LAUNCH GUIDE

**LOKI Enterprise Compliance Platform - Production Deployment Guide**

Version: 1.0.0-PLATINUM
Last Updated: 2025-11-11
Status: PRODUCTION READY

---

## Table of Contents

1. [Overview](#overview)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [System Requirements](#system-requirements)
4. [Installation Guide](#installation-guide)
5. [Configuration](#configuration)
6. [Health Checks](#health-checks)
7. [Deployment Strategies](#deployment-strategies)
8. [Post-Deployment Verification](#post-deployment-verification)
9. [Monitoring & Observability](#monitoring--observability)
10. [Troubleshooting](#troubleshooting)
11. [Rollback Procedures](#rollback-procedures)
12. [Security Hardening](#security-hardening)

---

## Overview

The LOKI PLATINUM platform is an enterprise-grade compliance orchestration system featuring:

- **Zero-downtime** startup and shutdown
- **Self-healing** capabilities with automatic recovery
- **Comprehensive monitoring** with health checks and telemetry
- **Feature flags** for gradual rollouts
- **Circuit breakers** for graceful degradation
- **Multi-tenant** support with RBAC
- **Advanced compliance** modules (FCA, GDPR, Tax, Employment)

---

## Pre-Deployment Checklist

### Critical Requirements

- [ ] **Python 3.8+** installed
- [ ] **PostgreSQL 12+** configured and accessible
- [ ] **Redis 6+** configured and accessible
- [ ] **SSL certificates** obtained for production
- [ ] **Environment variables** configured
- [ ] **Database migrations** completed
- [ ] **Backup strategy** in place
- [ ] **Monitoring tools** integrated (optional but recommended)

### Security Requirements

- [ ] **JWT secret** generated (minimum 32 characters)
- [ ] **Database passwords** secured
- [ ] **API keys** rotated from defaults
- [ ] **Encryption keys** generated
- [ ] **Firewall rules** configured
- [ ] **HTTPS/TLS** enabled
- [ ] **Rate limiting** configured
- [ ] **Audit logging** enabled

### Infrastructure Requirements

- [ ] **CPU**: Minimum 2 cores (4+ recommended for production)
- [ ] **Memory**: Minimum 2GB RAM (8GB+ recommended for production)
- [ ] **Disk**: 20GB+ free space
- [ ] **Network**: Stable internet connection
- [ ] **Ports**: 8000 (API), 5432 (PostgreSQL), 6379 (Redis) accessible

---

## System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| Operating System | Linux (Ubuntu 20.04+, CentOS 8+, Debian 10+) |
| Python | 3.8 or higher |
| PostgreSQL | 12.x or higher |
| Redis | 6.x or higher |
| CPU | 2 cores |
| RAM | 2GB |
| Disk | 20GB free space |

### Recommended Production Requirements

| Component | Requirement |
|-----------|-------------|
| Operating System | Linux (Ubuntu 22.04 LTS) |
| Python | 3.11 or higher |
| PostgreSQL | 14.x or higher |
| Redis | 7.x or higher |
| CPU | 4+ cores |
| RAM | 8GB+ |
| Disk | 100GB+ SSD |
| Load Balancer | NGINX or similar |

---

## Installation Guide

### Step 1: System Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip \
    postgresql postgresql-contrib redis-server \
    git build-essential libpq-dev

# Start services
sudo systemctl start postgresql
sudo systemctl start redis-server
sudo systemctl enable postgresql
sudo systemctl enable redis-server
```

### Step 2: Database Setup

```bash
# Create PostgreSQL database and user
sudo -u postgres psql << EOF
CREATE DATABASE loki;
CREATE USER loki_user WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE loki TO loki_user;
ALTER DATABASE loki OWNER TO loki_user;
\q
EOF
```

### Step 3: Application Setup

```bash
# Clone repository
cd /opt
sudo git clone https://github.com/yourorg/loki-interceptor.git
cd loki-interceptor

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-security.txt
pip install -r requirements-nlp.txt
```

### Step 4: Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit configuration (see Configuration section)
nano .env

# Validate configuration
python cli/loki_admin.py config validate
```

### Step 5: Database Migrations

```bash
# Run database migrations
alembic upgrade head

# Verify migrations
alembic current
```

### Step 6: Run System Checks

```bash
# Run comprehensive system diagnostics
./scripts/system_check.sh

# All checks should pass before proceeding
```

---

## Configuration

### Environment Variables

Create `/opt/loki-interceptor/.env` with the following:

```bash
# Environment
ENVIRONMENT=production
DEBUG=false

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=loki
DB_USER=loki_user
DB_PASSWORD=your_secure_password
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
REDIS_DB=0

# API Server
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Security
JWT_SECRET=your_32_character_minimum_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRY=3600
ENCRYPTION_KEY=your_encryption_key_here
API_KEY_HEADER=X-API-Key

# Monitoring (Optional)
LOG_LEVEL=INFO
SENTRY_DSN=https://your-sentry-dsn
DATADOG_API_KEY=your_datadog_key
JAEGER_ENDPOINT=http://localhost:14268/api/traces

# Feature Flags
ENABLE_ADVANCED_ANALYTICS=true
ENABLE_REAL_TIME_MONITORING=true
```

### Platform Configuration File (Optional)

Create `/etc/loki/config.yml`:

```yaml
database:
  host: localhost
  port: 5432
  name: loki
  pool_size: 20

redis:
  host: localhost
  port: 6379
  max_connections: 100

api:
  workers: 8
  timeout: 120
  rate_limit: 1000

compliance:
  enabled_modules:
    - fca_uk
    - fca_advanced
    - gdpr_uk
    - gdpr_advanced
    - tax_uk
    - uk_employment
  strict_mode: true

performance:
  enable_caching: true
  enable_compression: true
  max_workers: 8
  circuit_breaker_threshold: 5
```

---

## Health Checks

### Pre-Deployment Health Check

```bash
# Activate virtual environment
source /opt/loki-interceptor/venv/bin/activate

# Run health check
python cli/loki_admin.py health check

# Expected output:
# Overall Status: HEALTHY
# All components should show [HEALTHY] status
```

### Continuous Monitoring

The platform automatically runs health checks every 30 seconds once started:

- **Database connectivity**
- **Redis connectivity**
- **System resources** (CPU, Memory, Disk)
- **Circuit breaker states**
- **Error rates**

### Health Check API Endpoint

```bash
# Check health via API
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "checks": [...],
  "uptime": 1234.56
}
```

---

## Deployment Strategies

### Strategy 1: Direct Deployment

**Best for**: Development, staging environments

```bash
# Start the platform
cd /opt/loki-interceptor
source venv/bin/activate
python -m backend.platform.orchestrator
```

### Strategy 2: Systemd Service (Recommended for Production)

Create `/etc/systemd/system/loki.service`:

```ini
[Unit]
Description=LOKI Enterprise Compliance Platform
After=network.target postgresql.service redis.service
Requires=postgresql.service redis.service

[Service]
Type=simple
User=loki
Group=loki
WorkingDirectory=/opt/loki-interceptor
Environment="PATH=/opt/loki-interceptor/venv/bin"
EnvironmentFile=/opt/loki-interceptor/.env
ExecStart=/opt/loki-interceptor/venv/bin/python -m backend.platform.orchestrator
ExecStop=/bin/kill -TERM $MAINPID
Restart=always
RestartSec=10

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/loki-interceptor/logs

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
# Create loki user
sudo useradd -r -s /bin/false loki
sudo chown -R loki:loki /opt/loki-interceptor

# Enable service
sudo systemctl daemon-reload
sudo systemctl enable loki.service
sudo systemctl start loki.service

# Check status
sudo systemctl status loki.service
```

### Strategy 3: Docker Deployment

```bash
# Build Docker image
docker build -t loki-platform:platinum .

# Run container
docker run -d \
  --name loki-platform \
  --env-file .env \
  -p 8000:8000 \
  --restart unless-stopped \
  loki-platform:platinum

# Check logs
docker logs -f loki-platform
```

### Strategy 4: Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/namespace.yml
kubectl apply -f k8s/configmap.yml
kubectl apply -f k8s/secrets.yml
kubectl apply -f k8s/deployment.yml
kubectl apply -f k8s/service.yml
kubectl apply -f k8s/ingress.yml

# Verify deployment
kubectl get pods -n loki
kubectl logs -f deployment/loki-platform -n loki
```

---

## Post-Deployment Verification

### 1. Service Verification

```bash
# Check if service is running
sudo systemctl status loki.service

# Or check process
ps aux | grep python | grep orchestrator
```

### 2. Health Check Verification

```bash
# CLI health check
python cli/loki_admin.py health check

# API health check
curl http://localhost:8000/health
```

### 3. Feature Flags Verification

```bash
# List all feature flags
python cli/loki_admin.py flags list

# Verify critical flags are enabled
python cli/loki_admin.py flags list --enabled-only
```

### 4. Metrics Verification

```bash
# Check metrics summary
python cli/loki_admin.py metrics summary

# Export metrics
python cli/loki_admin.py metrics export --output /tmp/metrics.json
```

### 5. Functional Testing

```bash
# Run integration tests
pytest tests/integration/ -v

# Run compliance module tests
pytest tests/compliance/ -v

# Run end-to-end tests
pytest tests/ -m e2e
```

### 6. Performance Testing

```bash
# Run load tests
pytest tests/load/test_concurrent.py -v

# Benchmark performance
python benchmark_correction_engine.py
```

---

## Monitoring & Observability

### Built-in Monitoring

The platform includes comprehensive monitoring:

1. **Health Monitoring**
   - Automatic health checks every 30 seconds
   - Component-level health status
   - Self-healing capabilities

2. **Telemetry**
   - Request metrics (count, latency, errors)
   - System metrics (CPU, memory, disk)
   - Compliance check metrics
   - Custom business metrics

3. **Error Tracking**
   - Comprehensive error logging
   - Error rate monitoring
   - Circuit breaker status
   - Recovery attempt tracking

### External Monitoring Integration

#### Sentry (Error Tracking)

```bash
# Set in .env
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

#### Datadog (Metrics & APM)

```bash
# Set in .env
DATADOG_API_KEY=your_datadog_api_key
```

#### Jaeger (Distributed Tracing)

```bash
# Set in .env
JAEGER_ENDPOINT=http://jaeger:14268/api/traces
```

### Monitoring Dashboards

Access built-in dashboards:

- **Health Dashboard**: `http://your-domain/admin/health`
- **Metrics Dashboard**: `http://your-domain/admin/metrics`
- **Errors Dashboard**: `http://your-domain/admin/errors`

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed

**Symptoms**: Health check shows database as unhealthy

**Solution**:
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -h localhost -U loki_user -d loki

# Check credentials in .env
```

#### 2. Redis Connection Failed

**Symptoms**: Health check shows Redis as unhealthy

**Solution**:
```bash
# Check Redis is running
sudo systemctl status redis-server

# Test connection
redis-cli ping

# Check Redis configuration
```

#### 3. High Memory Usage

**Symptoms**: System shows degraded health, memory > 80%

**Solution**:
```bash
# Check memory usage
python cli/loki_admin.py system status

# Adjust workers in .env
API_WORKERS=2  # Reduce from 4

# Restart service
sudo systemctl restart loki.service
```

#### 4. Circuit Breaker Open

**Symptoms**: Service unavailable errors

**Solution**:
```bash
# Check circuit breaker status
python cli/loki_admin.py errors stats

# Reset circuit breaker
python cli/loki_admin.py errors reset-breaker <service-name>
```

### Debug Mode

Enable debug logging:

```bash
# Temporarily enable debug mode
export DEBUG=true
export LOG_LEVEL=DEBUG

# Restart service
sudo systemctl restart loki.service

# View logs
sudo journalctl -u loki.service -f
```

### Diagnostics Report

Generate comprehensive diagnostics:

```bash
# Generate diagnostics report
python cli/loki_admin.py system diagnostics --output /tmp/diagnostics.json

# Review report
cat /tmp/diagnostics.json | jq .
```

---

## Rollback Procedures

### Quick Rollback

```bash
# Stop current service
sudo systemctl stop loki.service

# Switch to previous version
cd /opt
sudo mv loki-interceptor loki-interceptor-new
sudo mv loki-interceptor-backup loki-interceptor

# Rollback database (if needed)
cd /opt/loki-interceptor
alembic downgrade -1

# Start service
sudo systemctl start loki.service

# Verify
python cli/loki_admin.py health check
```

### Database Rollback

```bash
# Show migration history
alembic history

# Rollback to specific version
alembic downgrade <revision>

# Verify current version
alembic current
```

### Feature Flag Rollback

```bash
# Disable problematic feature
python cli/loki_admin.py flags update <flag-name> --disabled

# Or update percentage for gradual rollout
python cli/loki_admin.py flags update <flag-name> --percentage 0
```

---

## Security Hardening

### 1. SSL/TLS Configuration

```bash
# Generate SSL certificate (Let's Encrypt)
sudo certbot certonly --standalone -d your-domain.com

# Configure NGINX with SSL
sudo nano /etc/nginx/sites-available/loki
```

NGINX configuration:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. Firewall Configuration

```bash
# Configure UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 443/tcp
sudo ufw enable
```

### 3. Rate Limiting

Enable rate limiting in `.env`:

```bash
ENABLE_RATE_LIMITING=true
RATE_LIMIT=100  # requests per minute
RATE_LIMIT_PERIOD=60  # seconds
```

### 4. Audit Logging

Enable comprehensive audit logging:

```bash
ENABLE_AUDIT_LOGGING=true
AUDIT_LOG_PATH=/var/log/loki/audit.log
```

### 5. Secret Rotation

```bash
# Generate new JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update .env
JWT_SECRET=new_secret_here

# Restart service
sudo systemctl restart loki.service
```

---

## Production Deployment Checklist

### Pre-Launch (T-7 days)

- [ ] Run full system diagnostics
- [ ] Complete security audit
- [ ] Load test with expected traffic
- [ ] Backup strategy tested and verified
- [ ] Monitoring dashboards configured
- [ ] Alerting rules configured
- [ ] Documentation reviewed and updated
- [ ] Team training completed

### Launch Day (T-0)

- [ ] Final health check passed
- [ ] Database backup completed
- [ ] Rollback plan reviewed
- [ ] Monitoring active
- [ ] Team on standby
- [ ] Deploy to production
- [ ] Verify all systems operational
- [ ] Monitor for 1 hour post-deployment

### Post-Launch (T+1 week)

- [ ] Review error rates
- [ ] Analyze performance metrics
- [ ] Collect user feedback
- [ ] Fine-tune configuration
- [ ] Update documentation
- [ ] Schedule retrospective

---

## Support & Contacts

- **Technical Support**: support@loki-platform.com
- **Emergency Hotline**: +44 (0) 20 XXXX XXXX
- **Documentation**: https://docs.loki-platform.com
- **Status Page**: https://status.loki-platform.com

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0-PLATINUM | 2025-11-11 | Initial PLATINUM release |

---

**END OF PLATINUM LAUNCH GUIDE**

For additional support and detailed technical documentation, please refer to:
- `PLATINUM_FEATURES.md` - Complete feature inventory
- `SYSTEM_ARCHITECTURE.md` - Technical architecture details
- `API_DOCUMENTATION.md` - API reference
- `SECURITY_AUDIT_REPORT.md` - Security details
