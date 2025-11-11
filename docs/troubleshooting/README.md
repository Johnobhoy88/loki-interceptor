# Troubleshooting Guide

Common issues and solutions for LOKI Interceptor.

## Table of Contents
1. [Installation Issues](#installation-issues)
2. [API Issues](#api-issues)
3. [Validation Issues](#validation-issues)
4. [Correction Issues](#correction-issues)
5. [Performance Issues](#performance-issues)
6. [Deployment Issues](#deployment-issues)
7. [Getting Help](#getting-help)

---

## Installation Issues

### Python Version Error

**Problem**: `Python 3.8+ required`

**Solution**:
```bash
# Check Python version
python --version

# Install correct version
# On macOS
brew install python@3.10

# On Ubuntu
sudo apt install python3.10

# Use specific version
python3.10 -m venv venv
```

### Virtual Environment Issues

**Problem**: `ModuleNotFoundError: No module named 'backend'`

**Solution**:
```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Verify activation (should show venv prefix)
which python

# Reinstall dependencies
pip install -r requirements.txt
```

### Dependency Conflicts

**Problem**: `ERROR: pip's dependency resolver does not currently take into account all the packages`

**Solution**:
```bash
# Create fresh virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# If still failing, try:
pip install --no-cache-dir -r requirements.txt
```

### Missing Anthropic API Key

**Problem**: `KeyError: 'ANTHROPIC_API_KEY'`

**Solution**:
```bash
# Check if .env exists
ls -la .env

# If not, create it
cp .env.example .env

# Edit and add your API key
nano .env

# Verify it's loaded
echo $ANTHROPIC_API_KEY

# If using docker, pass as env var
docker run -e ANTHROPIC_API_KEY=your_key_here loki:latest
```

---

## API Issues

### Server Won't Start

**Problem**: `Address already in use`

**Solution**:
```bash
# Find process on port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use different port
UVICORN_PORT=8001 python -m backend.api.main
```

### Connection Refused

**Problem**: `curl: (7) Failed to connect to localhost port 8000`

**Solution**:
```bash
# Check if server is running
ps aux | grep python

# Start server
python -m backend.api.main

# Check firewall
sudo ufw allow 8000/tcp

# For remote access, bind to 0.0.0.0
python -m backend.api.main --host 0.0.0.0
```

### Slow Response Times

**Problem**: API responses take >5 seconds

**Solution**:
```bash
# Check system resources
top  # or htop

# Reduce cache size (uses less memory)
CACHE_MAX_SIZE=100 python -m backend.api.main

# Increase workers
UVICORN_WORKERS=8 python -m backend.api.main

# Reduce max tokens
MAX_TOKENS=2048 python -m backend.api.main
```

### CORS Errors

**Problem**: `Access to XMLHttpRequest blocked by CORS policy`

**Solution**:

In `backend/api/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Add your frontend URL
        "https://yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Rate Limit Errors

**Problem**: `429 Too Many Requests`

**Solution**:
```bash
# Increase rate limit
RATE_LIMIT_REQUESTS=1000 python -m backend.api.main

# Or implement client-side backoff
import time
for attempt in range(3):
    try:
        response = requests.post(url, json=data)
        break
    except Exception as e:
        time.sleep(2 ** attempt)
```

---

## Validation Issues

### No Modules Loaded

**Problem**: `modules_loaded: 0` in health check

**Solution**:
```bash
# Check module directory exists
ls -la backend/modules/

# Verify module files
ls backend/modules/fca_uk/gates/

# Check for import errors
python -c "from backend.modules import fca_uk"

# Restart server
# Modules should load on startup
python -m backend.api.main
```

### Gates Not Running

**Problem**: `gates_checked: 0`

**Solution**:
```python
# Verify modules are specified
result = validator.validate_document(
    text="...",
    document_type="financial",
    modules=["fca_uk"]  # Must specify modules
)

# Check if module name is correct
print(engine.modules.keys())
# Should output: dict_keys(['fca_uk', 'gdpr_uk', ...])
```

### Validation Too Strict

**Problem**: Most documents fail validation

**Solution**:
```python
# Check which gates are failing
for module in results['modules']:
    for gate in module['gates']:
        if not gate['passed']:
            print(f"Failed: {gate['gate_name']}")

# Review legal sources
for gate in module['gates']:
    print(f"{gate['gate_name']}: {gate['legal_source']}")

# May be operating within scope - confirm requirements
```

### Wrong Risk Level

**Problem**: Document marked HIGH risk but seems fine

**Solution**:
```python
# Analyze module distribution
for module in results['modules']:
    print(f"{module['module_name']}:")
    print(f"  Failed: {module['gates_failed']}/{module['gates_checked']}")

# Risk calculation:
# - If >60% gates failed: CRITICAL
# - If 30-60% failed: HIGH
# - If 10-30% failed: MEDIUM
# - If <10% failed: LOW

# May need to disable certain modules
modules = ["fca_uk"]  # Instead of all 5
```

---

## Correction Issues

### No Corrections Applied

**Problem**: `issues_corrected: 0`

**Solution**:
```python
# Verify validation_results are passed
response = requests.post(
    'http://localhost:8000/api/v1/correct',
    json={
        "text": "Your document...",
        "validation_results": validation_results,  # Must include this
        "auto_apply": True
    }
)

# Check confidence threshold
# Increase to apply more corrections
"confidence_threshold": 0.5  # Lower = more corrections

# Check auto_apply flag
"auto_apply": True  # Must be true to apply
```

### Low Confidence Corrections

**Problem**: `confidence: 0.3` on corrections

**Solution**:
```python
# Review the pattern
for correction in result['corrections']:
    print(f"{correction['reason']}")
    print(f"Pattern: {correction['pattern']}")
    print(f"Confidence: {correction['confidence']}")

# Low confidence may indicate:
# - Rare or edge case
# - Unclear applicability
# - Pattern needs tuning

# Set threshold higher to filter
"confidence_threshold": 0.8
```

### Corrections Don't Fix Issue

**Problem**: Issue persists after correction

**Solution**:
```python
# Validate corrected text
corrected = result['corrected_text']

validation_v2 = validator.validate_document(
    corrected,
    "financial",
    ["fca_uk"]
)

# Check if fixed
if validation_v2['overall_risk'] != 'LOW':
    # May need manual intervention
    # Check suggestions for manual fixes
    for gate in validation_v2['modules'][0]['gates']:
        if not gate['passed']:
            print(f"Still failing: {gate['message']}")
```

### Text Corruption

**Problem**: Corrected text is malformed

**Solution**:
```python
# Verify original text is valid
assert isinstance(original_text, str)
assert len(original_text) > 0

# Check correction result
if len(corrected) < len(original) * 0.5:
    print("Warning: Text significantly reduced")

# Enable preserve_formatting
"preserve_formatting": True

# Use lower max iterations
"max_iterations": 1
```

---

## Performance Issues

### Slow Validation (>5 seconds)

**Problem**: Validation taking too long

**Solution**:
```bash
# Reduce modules (each module adds ~500ms)
modules=["fca_uk"]  # Instead of all 5

# Enable caching
"use_cache": true

# Reduce document size (if possible)
# Limit to most relevant 5000 characters

# Increase workers
UVICORN_WORKERS=8
```

### High Memory Usage

**Problem**: Memory usage >1GB

**Solution**:
```bash
# Reduce cache size
CACHE_MAX_SIZE=50

# Reduce workers
UVICORN_WORKERS=2

# Monitor memory
watch -n 1 'ps aux | grep python'

# Set memory limits (Docker)
docker run -m 512m loki:latest
```

### CPU Bottleneck

**Problem**: High CPU usage

**Solution**:
```bash
# Reduce token limit
MAX_TOKENS=2048

# Use simpler patterns
# Avoid complex regex
# Review TEMPERATURE=0.5

# Scale horizontally
# Add more servers behind load balancer
```

### Cache Effectiveness Low

**Problem**: `cache_hit_rate: 0.05`

**Solution**:
```python
# Cache works on exact text matches
# Normalize input first
text = text.strip().lower()

# Enable caching in requests
"use_cache": true

# Monitor cache
stats = requests.get('http://localhost:8000/api/v1/stats')
print(stats['cache']['hit_rate'])

# If still low, documents likely very similar
# Consider caching at application layer
```

---

## Deployment Issues

### Docker Build Fails

**Problem**: `Error: failed to build`

**Solution**:
```bash
# Check Dockerfile exists
ls -la backend/Dockerfile

# Build with verbose output
docker build --verbose -t loki:latest -f backend/Dockerfile .

# Check Docker daemon
docker ps

# Clean up and rebuild
docker system prune
docker build -t loki:latest -f backend/Dockerfile .
```

### Container Exits Immediately

**Problem**: Container starts then stops

**Solution**:
```bash
# Check logs
docker logs <container_id>

# Run interactively
docker run -it loki:latest /bin/bash

# Check if ANTHROPIC_API_KEY is set
docker inspect loki | grep -i env

# Ensure API key is passed
docker run -e ANTHROPIC_API_KEY=xxx loki:latest
```

### Health Check Failing

**Problem**: `health: unhealthy`

**Solution**:
```bash
# Test health endpoint directly
curl http://localhost:8000/api/health

# Check logs for startup errors
docker logs <container_id>

# Increase startup delay
docker run --health-start-period=60s loki:latest

# Verify port is accessible
docker inspect -f '{{range $p, $conf := .NetworkSettings.Ports}}{{$p}} -> {{(index $conf 0).HostPort}}{{end}}' <container>
```

### Cloud Deployment Fails

**Problem**: AWS/GCP deployment not working

**Solution**:

For **AWS**:
```bash
# Create IAM user with AmazonEC2FullAccess

# Configure AWS CLI
aws configure

# Create security group
aws ec2 create-security-group \
  --group-name loki-sg \
  --description "LOKI API"

# Allow port 8000
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxx \
  --protocol tcp \
  --port 8000 \
  --cidr 0.0.0.0/0
```

For **GCP**:
```bash
# Set project
gcloud config set project PROJECT_ID

# Create firewall rule
gcloud compute firewall-rules create allow-loki \
  --allow tcp:8000

# Deploy
gcloud run deploy loki \
  --image gcr.io/PROJECT_ID/loki \
  --platform managed \
  --set-env-vars ANTHROPIC_API_KEY=xxx
```

---

## Getting Help

### Debug Logging

```bash
# Enable debug logging
LOG_LEVEL=DEBUG python -m backend.api.main

# Save logs to file
python -m backend.api.main > logs/debug.log 2>&1

# Monitor logs in real-time
tail -f logs/debug.log
```

### Common Patterns

```python
# Test validation
text = "Test text"
result = validator.validate_document(text, "financial", ["fca_uk"])
print(f"Result: {result['validation']['status']}")

# Test API
import requests
r = requests.get('http://localhost:8000/api/health')
print(r.json())

# Check modules
engine = get_engine()
print(f"Loaded modules: {list(engine.modules.keys())}")
```

### Report an Issue

When reporting issues, include:
1. Python version: `python --version`
2. OS: `uname -a`
3. Error message (full traceback)
4. Steps to reproduce
5. Expected vs actual behavior
6. Relevant logs

**File issue at**: https://github.com/Johnobhoy88/loki-interceptor/issues

---

## FAQ

**Q: Why is validation slow on large documents?**
A: Processing scales with document length. Use caching or split large documents.

**Q: Can I run multiple instances?**
A: Yes, use a load balancer (nginx) to distribute requests.

**Q: How do I backup validation history?**
A: Export from `/api/v1/history/validations` endpoint or database.

**Q: Why are some corrections not applied?**
A: Check confidence threshold and auto_apply flag.

---

**See also**: [FAQ](faq.md) | [Performance Analysis](performance.md) | [API Reference](../api/README.md)

**Version**: 1.0.0
**Last Updated**: 2025-11-11
