# LOKI Compliance Platform - System Administration Manual

**Document Version:** 1.0
**Last Updated:** November 2025
**Target Audience:** System Administrators, IT Managers, DevOps Engineers

---

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation & Deployment](#installation--deployment)
- [Configuration Management](#configuration-management)
- [User Management](#user-management)
- [Module Administration](#module-administration)
- [Monitoring & Logging](#monitoring--logging)
- [Backup & Recovery](#backup--recovery)
- [Performance Tuning](#performance-tuning)
- [Security Hardening](#security-hardening)
- [Troubleshooting](#troubleshooting)

---

## System Requirements

### Desktop Application

**Minimum Requirements:**
- **OS:** Windows 10 (build 1809+), macOS 10.15+, Ubuntu 20.04+
- **CPU:** Dual-core 2.0 GHz
- **RAM:** 4GB
- **Storage:** 2GB available space
- **Network:** Broadband internet (100 Mbps+)

**Recommended Requirements:**
- **CPU:** Quad-core 3.0 GHz+
- **RAM:** 8GB+
- **Storage:** 10GB SSD
- **Network:** Gigabit ethernet or Wi-Fi 6

### API Server

**Minimum Requirements:**
- **OS:** Ubuntu 20.04 LTS, Windows Server 2019, RHEL 8+
- **CPU:** 4 cores
- **RAM:** 8GB
- **Storage:** 20GB SSD
- **Python:** 3.8+

**Recommended Production:**
- **CPU:** 8+ cores
- **RAM:** 16GB+
- **Storage:** 100GB SSD (NVMe)
- **Python:** 3.10+
- **Load Balancer:** NGINX or AWS ALB

### Database

**SQLite (Default):**
- Suitable for single-user desktop or small teams (<10 users)
- Max 1GB audit data before performance degrades

**PostgreSQL (Recommended for Enterprise):**
- Multi-user support
- Horizontal scaling
- Advanced audit capabilities

---

## Installation & Deployment

### Desktop Installation

**Windows:**
```powershell
# Download installer
Invoke-WebRequest -Uri "https://downloads.loki-compliance.com/v1.0.0/LOKI-Setup.exe" -OutFile "LOKI-Setup.exe"

# Silent install for all users
.\LOKI-Setup.exe /S /AllUsers

# Install to custom directory
.\LOKI-Setup.exe /S /D=C:\CustomPath\LOKI

# Create desktop shortcut
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$Home\Desktop\LOKI.lnk")
$Shortcut.TargetPath = "C:\Program Files\LOKI\LOKI.exe"
$Shortcut.Save()
```

**macOS:**
```bash
# Download and mount DMG
curl -O https://downloads.loki-compliance.com/v1.0.0/LOKI-1.0.0.dmg
hdiutil attach LOKI-1.0.0.dmg

# Copy to Applications
cp -R "/Volumes/LOKI/LOKI.app" /Applications/

# Unmount
hdiutil detach "/Volumes/LOKI"

# Grant permissions (if needed)
xattr -cr /Applications/LOKI.app
```

**Linux:**
```bash
# Download AppImage
wget https://downloads.loki-compliance.com/v1.0.0/LOKI-1.0.0.AppImage

# Make executable
chmod +x LOKI-1.0.0.AppImage

# Move to /opt
sudo mv LOKI-1.0.0.AppImage /opt/LOKI.AppImage

# Create desktop entry
cat <<EOF | sudo tee /usr/share/applications/loki.desktop
[Desktop Entry]
Type=Application
Name=LOKI Interceptor
Exec=/opt/LOKI.AppImage
Icon=/opt/loki-icon.png
Categories=Office;Utility;
EOF
```

### API Server Deployment

**Option 1: Standalone Server**

```bash
# Clone repository
git clone https://github.com/HighlandAI/loki-interceptor.git
cd loki-interceptor

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add ANTHROPIC_API_KEY and other settings

# Initialize database
python -m backend.scripts.init_db

# Start server
python backend/server.py --host 0.0.0.0 --port 5002
```

**Option 2: Docker Deployment**

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ ./backend/
COPY .env .

# Expose port
EXPOSE 5002

# Run server
CMD ["python", "backend/server.py", "--host", "0.0.0.0", "--port", "5002"]
```

```bash
# Build image
docker build -t loki-api:1.0.0 .

# Run container
docker run -d \
  --name loki-api \
  -p 5002:5002 \
  -e ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY} \
  -v loki-data:/app/backend/data \
  loki-api:1.0.0

# Check logs
docker logs -f loki-api
```

**Option 3: Kubernetes Deployment**

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: loki-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: loki-api
  template:
    metadata:
      labels:
        app: loki-api
    spec:
      containers:
      - name: loki
        image: loki-api:1.0.0
        ports:
        - containerPort: 5002
        env:
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: loki-secrets
              key: anthropic-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5002
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: loki-api-service
spec:
  selector:
    app: loki-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5002
  type: LoadBalancer
```

```bash
# Apply configuration
kubectl apply -f k8s/deployment.yaml

# Create secrets
kubectl create secret generic loki-secrets \
  --from-literal=anthropic-api-key=${ANTHROPIC_API_KEY}

# Check status
kubectl get pods -l app=loki-api
kubectl logs -f deployment/loki-api
```

---

## Configuration Management

### Environment Variables

**Core Settings:**
```bash
# .env
ANTHROPIC_API_KEY=sk-ant-api03-...      # Required: Claude API key
CLAUDE_MODEL=claude-3-5-sonnet-20241022  # AI model to use
LOG_LEVEL=INFO                           # DEBUG, INFO, WARNING, ERROR
MAX_TOKENS=4096                          # Max tokens per AI request
TEMPERATURE=0.0                          # AI temperature (0.0 = deterministic)

# Database
DATABASE_URL=sqlite:///backend/data/audit.db  # SQLite path
# DATABASE_URL=postgresql://user:pass@host:5432/loki  # PostgreSQL

# API Server
API_HOST=0.0.0.0
API_PORT=5002
API_WORKERS=4                            # Gunicorn workers
CORS_ORIGINS=*                           # Allowed CORS origins

# Security
API_KEY_ROTATION_DAYS=90                 # Auto-rotate keys
SESSION_SECRET=random-secret-key
JWT_SECRET=another-random-secret

# Performance
CACHE_ENABLED=true
CACHE_TTL=3600                           # Cache lifetime (seconds)
RATE_LIMIT_PER_MINUTE=30
MAX_DOCUMENT_SIZE=100000                 # Max characters

# Audit
AUDIT_ENABLED=true
AUDIT_RETENTION_DAYS=90
AUDIT_ENCRYPT=true
```

### Configuration File

**config/loki.yaml:**
```yaml
application:
  name: LOKI Interceptor
  version: 1.0.0
  environment: production

modules:
  enabled:
    - fca_uk
    - gdpr_uk
    - tax_uk
    - nda_uk
    - hr_scottish

  config:
    fca_uk:
      sensitivity: strict
      auto_correct: true
    gdpr_uk:
      enable_dpo_check: true
      default_retention: 365

validation:
  severity_threshold: LOW
  return_details: true
  include_suggestions: true

correction:
  auto_apply: false
  preserve_formatting: true
  max_iterations: 3

api:
  timeout: 30
  retry_attempts: 3
  retry_delay: 1

logging:
  level: INFO
  format: json
  output: /var/log/loki/app.log
  rotate: daily
  retention: 30
```

### Loading Configuration

```python
import yaml
import os
from pathlib import Path

class Config:
    def __init__(self, config_file='config/loki.yaml'):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        with open(self.config_file, 'r') as f:
            config = yaml.safe_load(f)

        # Override with environment variables
        config['api_key'] = os.environ.get('ANTHROPIC_API_KEY')
        config['database_url'] = os.environ.get('DATABASE_URL', config.get('database_url'))

        return config

    def get(self, key, default=None):
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k)
            if value is None:
                return default
        return value

# Usage
config = Config()
api_key = config.get('api_key')
modules = config.get('modules.enabled')
```

---

## User Management

### Creating Users (Enterprise)

```bash
# Add new user
python -m backend.scripts.user_management add \
  --email user@company.com \
  --role analyst \
  --plan professional

# List users
python -m backend.scripts.user_management list

# Update user
python -m backend.scripts.user_management update \
  --email user@company.com \
  --role admin

# Disable user
python -m backend.scripts.user_management disable \
  --email user@company.com

# Reset password
python -m backend.scripts.user_management reset-password \
  --email user@company.com
```

### Role-Based Access Control

**Roles:**
```yaml
roles:
  viewer:
    permissions:
      - read:documents
      - read:reports

  analyst:
    permissions:
      - read:documents
      - write:documents
      - validate:documents
      - correct:documents

  admin:
    permissions:
      - "*:*"  # All permissions

  api_user:
    permissions:
      - api:validate
      - api:correct
```

**Implementing RBAC:**
```python
from functools import wraps
from flask import request, jsonify

def require_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user(request)
            if not user.has_permission(permission):
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/api/validate', methods=['POST'])
@require_permission('api:validate')
def validate_document():
    # Handle validation
    pass
```

---

## Module Administration

### Enabling/Disabling Modules

```bash
# List modules
loki modules list

# Enable module
loki modules enable fca_uk

# Disable module
loki modules disable hr_scottish

# Update module
loki modules update fca_uk --version 1.1.0
```

### Custom Rule Configuration

```python
# custom_rules.py
from backend.core.gate_registry import GateRegistry

registry = GateRegistry()

# Add custom gate
registry.register_gate(
    module='custom',
    gate_id='company_branding',
    name='Company Branding Compliance',
    check_function=check_company_branding,
    severity='MEDIUM'
)

def check_company_branding(text, context):
    violations = []

    # Check for old company name
    if 'OldCompanyName' in text:
        violations.append({
            'pattern': 'outdated_branding',
            'text': 'OldCompanyName',
            'reason': 'Use new company name: NewCompanyName',
            'severity': 'MEDIUM'
        })

    return violations
```

### Module Updates

```bash
# Check for updates
loki modules check-updates

# Update all modules
loki modules update-all

# Rollback module
loki modules rollback fca_uk --version 1.0.0
```

---

## Monitoring & Logging

### Application Logging

**Configure Logging:**
```python
import logging
from logging.handlers import RotatingFileHandler

# Create logger
logger = logging.getLogger('loki')
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
console_handler.setFormatter(console_formatter)

# File handler with rotation
file_handler = RotatingFileHandler(
    '/var/log/loki/app.log',
    maxBytes=10485760,  # 10MB
    backupCount=10
)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('[%(asctime)s] %(levelname)s [%(name)s]: %(message)s')
file_handler.setFormatter(file_formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
```

### Monitoring Metrics

**Prometheus Integration:**
```python
from prometheus_client import Counter, Histogram, start_http_server

# Define metrics
validation_counter = Counter('loki_validations_total', 'Total validations')
validation_duration = Histogram('loki_validation_duration_seconds', 'Validation duration')
correction_counter = Counter('loki_corrections_total', 'Total corrections')

# Instrument code
@validation_duration.time()
def validate_document(text, modules):
    validation_counter.inc()
    # Validation logic
    return result

# Start metrics server
start_http_server(8000)
```

**Grafana Dashboard:**
```json
{
  "dashboard": {
    "title": "LOKI Compliance Metrics",
    "panels": [
      {
        "title": "Validations per Minute",
        "targets": [{
          "expr": "rate(loki_validations_total[1m])"
        }]
      },
      {
        "title": "Average Validation Duration",
        "targets": [{
          "expr": "rate(loki_validation_duration_seconds_sum[5m]) / rate(loki_validation_duration_seconds_count[5m])"
        }]
      }
    ]
  }
}
```

### Health Checks

```python
@app.route('/health')
def health_check():
    checks = {
        'api': check_api_health(),
        'database': check_database_health(),
        'ai_provider': check_claude_health()
    }

    overall = 'healthy' if all(c['status'] == 'ok' for c in checks.values()) else 'unhealthy'

    return jsonify({
        'status': overall,
        'checks': checks,
        'timestamp': datetime.utcnow().isoformat()
    }), 200 if overall == 'healthy' else 503

def check_database_health():
    try:
        db.execute('SELECT 1')
        return {'status': 'ok', 'latency_ms': 5}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}
```

---

## Backup & Recovery

### Database Backup

**SQLite Backup:**
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/var/backups/loki"
DB_PATH="/app/backend/data/audit.db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
sqlite3 $DB_PATH ".backup '$BACKUP_DIR/audit_$TIMESTAMP.db'"

# Compress backup
gzip $BACKUP_DIR/audit_$TIMESTAMP.db

# Delete backups older than 30 days
find $BACKUP_DIR -name "*.db.gz" -mtime +30 -delete

echo "Backup completed: audit_$TIMESTAMP.db.gz"
```

**PostgreSQL Backup:**
```bash
#!/bin/bash
# pg_backup.sh

pg_dump -h localhost -U loki_user -d loki_db | gzip > /var/backups/loki/loki_$(date +%Y%m%d_%H%M%S).sql.gz
```

**Schedule Backups:**
```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /opt/loki/scripts/backup.sh

# Weekly full backup on Sunday at 3 AM
0 3 * * 0 /opt/loki/scripts/full_backup.sh
```

### Disaster Recovery

**Restore from Backup:**
```bash
# Stop LOKI service
systemctl stop loki

# Restore SQLite
gunzip -c /var/backups/loki/audit_20251108.db.gz > /app/backend/data/audit.db

# Restore PostgreSQL
gunzip -c /var/backups/loki/loki_20251108.sql.gz | psql -h localhost -U loki_user -d loki_db

# Restart service
systemctl start loki
```

---

## Performance Tuning

### API Server Optimization

**Gunicorn Configuration:**
```python
# gunicorn.conf.py
import multiprocessing

bind = "0.0.0.0:5002"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"  # Async workers
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = "/var/log/loki/access.log"
errorlog = "/var/log/loki/error.log"
loglevel = "info"

# Process naming
proc_name = "loki-api"

# Server mechanics
preload_app = True
daemon = False
```

**NGINX Reverse Proxy:**
```nginx
# /etc/nginx/sites-available/loki
upstream loki_backend {
    least_conn;
    server 127.0.0.1:5002;
    server 127.0.0.1:5003;
    server 127.0.0.1:5004;
}

server {
    listen 80;
    server_name api.loki-compliance.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.loki-compliance.com;

    ssl_certificate /etc/ssl/certs/loki.crt;
    ssl_certificate_key /etc/ssl/private/loki.key;

    # Performance
    client_max_body_size 10M;
    keepalive_timeout 65;
    gzip on;
    gzip_types application/json text/plain;

    location / {
        proxy_pass http://loki_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
}
```

### Database Optimization

**SQLite Tuning:**
```python
import sqlite3

conn = sqlite3.connect('audit.db')
conn.execute('PRAGMA journal_mode=WAL')  # Write-ahead logging
conn.execute('PRAGMA synchronous=NORMAL')
conn.execute('PRAGMA cache_size=10000')  # 10MB cache
conn.execute('PRAGMA temp_store=MEMORY')
```

**PostgreSQL Tuning:**
```sql
-- postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 2MB
min_wal_size = 1GB
max_wal_size = 4GB
```

---

## Security Hardening

### HTTPS/TLS Configuration

```bash
# Generate SSL certificate with Let's Encrypt
certbot certonly --nginx -d api.loki-compliance.com

# Auto-renewal
echo "0 0 * * * certbot renew --quiet" | crontab -
```

### Firewall Configuration

```bash
# UFW (Ubuntu)
ufw allow 22/tcp     # SSH
ufw allow 443/tcp    # HTTPS
ufw allow 5002/tcp   # LOKI API (if exposing directly)
ufw enable

# iptables
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
iptables -A INPUT -p tcp --dport 5002 -j ACCEPT
iptables -A INPUT -j DROP
```

### API Key Rotation

```python
# Automated key rotation
import schedule
import time

def rotate_api_keys():
    # Get keys older than 90 days
    old_keys = db.api_keys.find({'created_at': {'$lt': datetime.now() - timedelta(days=90)}})

    for key in old_keys:
        # Generate new key
        new_key = generate_api_key()

        # Send notification
        send_email(
            to=key['user_email'],
            subject='LOKI API Key Rotation',
            body=f'Your API key has been rotated. New key: {new_key}'
        )

        # Update database
        db.api_keys.update_one(
            {'_id': key['_id']},
            {'$set': {'key': new_key, 'created_at': datetime.now()}}
        )

# Schedule weekly check
schedule.every().sunday.at("02:00").do(rotate_api_keys)
```

---

## Troubleshooting

### Common Admin Issues

**1. High Memory Usage**
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head

# Solution: Reduce workers or increase RAM
# gunicorn.conf.py
workers = 2  # Reduce workers
max_requests = 1000
max_requests_jitter = 50
```

**2. Slow API Response**
```bash
# Check API performance
curl -w "@curl-format.txt" -o /dev/null -s https://api.loki-compliance.com/health

# curl-format.txt
time_namelookup: %{time_namelookup}\n
time_connect: %{time_connect}\n
time_total: %{time_total}\n

# Solution: Add caching, optimize database queries
```

**3. Database Locks**
```sql
-- PostgreSQL: Find blocking queries
SELECT * FROM pg_locks WHERE NOT granted;

-- Kill blocking query
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE pid = [blocking_pid];
```

---

*Last Updated: November 2025*
*Version: 1.0*
