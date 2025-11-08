# LOKI Compliance Platform - Troubleshooting Guide

**Document Version:** 1.0
**Last Updated:** November 2025

---

## Quick Diagnosis

| Symptom | Likely Cause | Quick Fix |
|---------|-------------|-----------|
| "Invalid API key" error | Expired or incorrect key | Regenerate API key in portal |
| Slow validation (>30s) | Large document or network issue | Split document into chunks |
| Application won't launch | Missing permissions | Run as administrator (Windows) or grant permissions (macOS) |
| 429 Rate Limit Error | Too many requests | Implement exponential backoff |
| Validation hangs | Claude API timeout | Check anthropic.com status |
| No corrections available | Manual review required | See violation details for guidance |

---

## Installation Issues

### Windows: Application Won't Install

**Symptom:** Installer fails or shows error message

**Solutions:**
1. **Run as Administrator:**
   ```powershell
   Right-click LOKI-Setup.exe → Run as administrator
   ```

2. **Disable Antivirus Temporarily:**
   - Windows Defender may block unsigned installers
   - Add exception for LOKI installer

3. **Check Disk Space:**
   ```powershell
   Get-PSDrive C | Select-Object Used,Free
   ```
   Requires 2GB minimum free space

4. **Install Visual C++ Redistributable:**
   ```powershell
   # Download and install
   https://aka.ms/vs/17/release/vc_redist.x64.exe
   ```

### macOS: "Cannot Open LOKI" Error

**Symptom:** macOS blocks application from opening

**Solution:**
```bash
# Remove quarantine attribute
xattr -cr /Applications/LOKI.app

# Or via System Preferences:
# Security & Privacy → General → Click "Open Anyway"
```

### Linux: AppImage Won't Run

**Symptom:** Double-click does nothing or permission denied

**Solutions:**
```bash
# Make executable
chmod +x LOKI-1.0.0.AppImage

# Install FUSE if missing
sudo apt install libfuse2  # Ubuntu/Debian
sudo yum install fuse-libs # RHEL/CentOS

# Run from terminal to see errors
./LOKI-1.0.0.AppImage
```

---

## Authentication & API Issues

### Invalid API Key Error

**Symptom:**
```json
{
  "error": {
    "code": "invalid_api_key",
    "message": "The provided API key is invalid or expired"
  }
}
```

**Diagnosis:**
```bash
# Test API key
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.loki-compliance.com/v1/health
```

**Solutions:**
1. **Verify Key Format:**
   - Should start with `lok_live_` (48 characters total)
   - No extra spaces or newlines

2. **Check Key Status:**
   - Log in to portal.loki-compliance.com
   - Navigate to Settings → API Keys
   - Verify key is Active (not Expired or Revoked)

3. **Regenerate Key:**
   ```bash
   # Via portal: Settings → API Keys → Create New Key
   # Update environment variable
   export ANTHROPIC_API_KEY="sk-ant-api03-NEW_KEY"
   ```

### Rate Limit Exceeded (429)

**Symptom:**
```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Try again in 45 seconds",
    "retry_after": 45
  }
}
```

**Rate Limits by Plan:**
- Starter: 10/min
- Professional: 30/min
- Enterprise: Custom

**Solutions:**

**1. Implement Exponential Backoff:**
```python
import time
import requests

def api_call_with_retry(url, headers, data, max_retries=3):
    for attempt in range(max_retries):
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            wait_time = retry_after * (2 ** attempt)  # Exponential backoff
            print(f"Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
            continue

        return response

    raise Exception("Max retries exceeded")
```

**2. Batch Requests:**
```python
# Instead of 100 individual calls
for doc in documents:
    validate(doc)

# Queue and process in batches
from collections import deque
import time

queue = deque(documents)
processed = []

while queue:
    batch = [queue.popleft() for _ in range(min(10, len(queue)))]

    for doc in batch:
        result = validate(doc)
        processed.append(result)

    if queue:
        time.sleep(60)  # Wait 1 minute between batches
```

**3. Upgrade Plan:**
Contact sales@highlandai.com for higher rate limits

---

## Validation Issues

### Validation Takes Too Long (>30 seconds)

**Symptoms:**
- Request times out
- Application hangs during validation

**Causes:**
1. Document too large (>100,000 characters)
2. Network latency
3. Claude API slow response

**Solutions:**

**1. Split Large Documents:**
```python
def split_document(text, max_chars=80000):
    """Split document into processable chunks"""
    chunks = []
    words = text.split()
    current_chunk = []
    current_length = 0

    for word in words:
        word_length = len(word) + 1  # +1 for space
        if current_length + word_length > max_chars:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = word_length
        else:
            current_chunk.append(word)
            current_length += word_length

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

# Process chunks
text = load_large_document()
chunks = split_document(text)

all_violations = []
for i, chunk in enumerate(chunks):
    print(f"Processing chunk {i+1}/{len(chunks)}...")
    result = loki.validate(chunk, 'financial_promotion', ['fca_uk'])
    all_violations.extend(result.violations)
```

**2. Increase Timeout:**
```python
# Python requests
response = requests.post(url, json=data, timeout=120)  # 120 seconds

# JavaScript fetch
const controller = new AbortController();
const timeout = setTimeout(() => controller.abort(), 120000);

fetch(url, {
  signal: controller.signal,
  ...options
}).finally(() => clearTimeout(timeout));
```

**3. Check Network:**
```bash
# Test latency to Claude API
ping api.anthropic.com

# Test API connectivity
curl -w "@curl-format.txt" -o /dev/null -s \
  https://api.anthropic.com/v1/messages

# curl-format.txt
time_namelookup: %{time_namelookup}
time_connect: %{time_connect}
time_total: %{time_total}
```

### No Violations Detected (False Negative)

**Symptom:** Document has obvious compliance issues, but validation returns PASS

**Diagnosis:**
```python
# Enable debug mode
loki = LokiClient(api_key='...', debug=True)
result = loki.validate(text, document_type, modules)

# Check which modules ran
print(result.modules_checked)

# Check gate statuses
for module, data in result.modules.items():
    print(f"{module}: {data['status']}")
    for gate, gate_data in data['gates'].items():
        print(f"  {gate}: {gate_data['status']}")
```

**Solutions:**

**1. Verify Correct Modules Selected:**
```python
# Wrong: Using GDPR module for financial document
result = loki.validate(text, 'financial_promotion', ['gdpr_uk'])

# Correct: Use FCA module
result = loki.validate(text, 'financial_promotion', ['fca_uk'])
```

**2. Check Document Type:**
```python
# Document type must match content
# Wrong:
result = loki.validate(privacy_policy_text, 'financial_promotion', ['gdpr_uk'])

# Correct:
result = loki.validate(privacy_policy_text, 'privacy_policy', ['gdpr_uk'])
```

**3. Lower Sensitivity Threshold:**
```python
# May be filtering out low/medium violations
result = loki.validate(
    text,
    document_type,
    modules,
    options={'severity_threshold': 'LOW'}  # Include all severities
)
```

### Too Many False Positives

**Symptom:** Validation flags legitimate compliant content

**Solutions:**

**1. Adjust Sensitivity:**
```python
# Only flag CRITICAL and HIGH
result = loki.validate(
    text,
    document_type,
    modules,
    options={'severity_threshold': 'HIGH'}
)
```

**2. Create Custom Exceptions (Enterprise):**
```python
# Add exception for specific pattern
from backend.core.correction_patterns import CorrectionPatternRegistry

registry = CorrectionPatternRegistry()
registry.add_exception(
    module='fca_uk',
    pattern='risk_warning',
    exception_text='your specific approved wording',
    reason='Pre-approved by legal team'
)
```

---

## Correction Issues

### Corrections Not Applied

**Symptom:** Correction endpoint returns success, but text unchanged

**Diagnosis:**
```python
response = loki.correct(text, document_type, modules)
print(f"Original length: {len(text)}")
print(f"Corrected length: {len(response.corrected_text)}")
print(f"Corrections applied: {response.summary.corrections_applied}")

# Check if corrections were actually applied
for correction in response.corrections:
    print(f"Applied: {correction['applied']}")
    if not correction['applied']:
        print(f"Reason not applied: {correction.get('skip_reason')}")
```

**Solutions:**

**1. Enable Auto-Apply:**
```python
# Ensure auto_apply is enabled
response = loki.correct(
    text,
    document_type,
    modules,
    options={'auto_apply': True}  # Must be True
)
```

**2. Check for Manual Review Required:**
```json
{
  "corrections": [],
  "suggestions": [
    {
      "message": "Consider adding FCA authorization statement",
      "severity": "HIGH"
    }
  ]
}
```
Some violations cannot be auto-corrected and require manual intervention.

**3. Verify Validation Results:**
```python
# Correction requires validation results
validation = loki.validate(text, document_type, modules)

if validation.status == 'FAIL':
    correction = loki.correct(
        text,
        document_type,
        modules,
        validation_id=validation.document_id  # Link to validation
    )
```

### Corrections Break Document Formatting

**Symptom:** Corrected document has wrong formatting, missing line breaks

**Solution:**
```python
# Enable formatting preservation
correction = loki.correct(
    text,
    document_type,
    modules,
    options={'preserve_formatting': True}
)
```

---

## Desktop Application Issues

### Application Crashes on Startup

**Windows:**
```powershell
# Check event log
Get-EventLog -LogName Application -Source "LOKI" -Newest 10

# Run from command line to see errors
cd "C:\Program Files\LOKI"
.\LOKI.exe --debug
```

**macOS:**
```bash
# Check crash logs
ls ~/Library/Logs/DiagnosticReports/LOKI*

# Run from terminal
/Applications/LOKI.app/Contents/MacOS/LOKI --debug
```

**Linux:**
```bash
# Run with verbose logging
./LOKI.AppImage --debug --verbose 2>&1 | tee loki.log
```

**Common Fixes:**
1. Delete configuration file:
   ```bash
   # Windows
   del %APPDATA%\LOKI\config.json

   # macOS
   rm ~/Library/Application\ Support/LOKI/config.json

   # Linux
   rm ~/.config/LOKI/config.json
   ```

2. Reset database:
   ```bash
   # Backup first
   cp backend/data/audit.db backend/data/audit.db.backup

   # Delete database (will be recreated)
   rm backend/data/audit.db
   ```

### Cannot Upload Files

**Symptoms:**
- Drag-and-drop doesn't work
- File picker shows no files

**Solutions:**

**1. Check File Permissions:**
```bash
# Ensure LOKI has file access
# macOS: System Preferences → Security & Privacy → Privacy → Files and Folders
```

**2. Verify File Format:**
```python
# Supported formats
supported = ['.txt', '.md', '.html']

# Check file extension
if not any(filename.endswith(ext) for ext in supported):
    print("Unsupported file format")
```

**3. Check File Size:**
```python
import os

max_size = 10 * 1024 * 1024  # 10MB
file_size = os.path.getsize('document.txt')

if file_size > max_size:
    print(f"File too large: {file_size / 1024 / 1024:.2f}MB (max 10MB)")
```

---

## Database Issues

### "Database is locked" Error

**Symptom (SQLite):**
```
sqlite3.OperationalError: database is locked
```

**Solutions:**

**1. Close Other Connections:**
```bash
# Find processes using database
lsof backend/data/audit.db

# Kill process if necessary
kill -9 [PID]
```

**2. Enable WAL Mode:**
```python
import sqlite3

conn = sqlite3.connect('audit.db')
conn.execute('PRAGMA journal_mode=WAL')
conn.commit()
```

**3. Increase Timeout:**
```python
conn = sqlite3.connect('audit.db', timeout=30.0)
```

### Audit Log Growing Too Large

**Symptom:** audit.db file is multiple GB, slowing performance

**Solution:**
```python
# Cleanup old audit logs
from datetime import datetime, timedelta

def cleanup_old_audits(days=90):
    cutoff = datetime.now() - timedelta(days=days)

    conn = sqlite3.connect('backend/data/audit.db')
    cursor = conn.cursor()

    # Delete old records
    cursor.execute('''
        DELETE FROM audit_log
        WHERE timestamp < ?
    ''', (cutoff.isoformat(),))

    deleted = cursor.rowcount
    conn.commit()

    # Vacuum to reclaim space
    cursor.execute('VACUUM')
    conn.close()

    print(f"Deleted {deleted} old audit records")

# Run cleanup
cleanup_old_audits(days=90)
```

**Automate Cleanup:**
```bash
# Add to crontab (run monthly)
0 0 1 * * python /path/to/cleanup_audits.py
```

---

## Network & Connectivity Issues

### Cannot Connect to Claude API

**Symptoms:**
- Validation fails with timeout
- "Unable to reach AI provider" error

**Diagnosis:**
```bash
# Test connectivity
curl -I https://api.anthropic.com/v1/messages

# Check DNS resolution
nslookup api.anthropic.com

# Test with verbose output
curl -v https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-3-5-sonnet-20241022","max_tokens":10,"messages":[{"role":"user","content":"test"}]}'
```

**Solutions:**

**1. Check Firewall:**
```bash
# Allow outbound HTTPS
sudo ufw allow out 443/tcp

# Check corporate firewall rules
```

**2. Configure Proxy:**
```python
# Set proxy in environment
export HTTPS_PROXY=http://proxy.company.com:8080

# Or in code
import os
os.environ['HTTPS_PROXY'] = 'http://proxy.company.com:8080'

loki = LokiClient(
    api_key='...',
    proxies={
        'https': 'http://proxy.company.com:8080'
    }
)
```

**3. Verify API Status:**
- Check https://status.anthropic.com
- Subscribe to status updates

### SSL Certificate Errors

**Symptom:**
```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Solutions:**

**1. Update CA Certificates:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ca-certificates

# macOS
brew install ca-certificates

# Windows
# Download latest certificates from:
https://curl.se/docs/caextract.html
```

**2. Configure Certificate Path:**
```python
import requests
import certifi

response = requests.post(
    url,
    json=data,
    verify=certifi.where()  # Use certifi's CA bundle
)
```

**3. Corporate SSL Inspection:**
```python
# If behind corporate SSL inspection
import os
os.environ['REQUESTS_CA_BUNDLE'] = '/path/to/corporate-ca-bundle.crt'
```

---

## Performance Issues

### High CPU Usage

**Diagnosis:**
```bash
# Linux
top -p $(pgrep LOKI)

# Windows
Get-Process LOKI | Select-Object CPU, WorkingSet

# macOS
top -pid $(pgrep LOKI)
```

**Solutions:**

**1. Reduce Concurrent Processing:**
```python
# Limit parallel validations
from concurrent.futures import ThreadPoolExecutor

max_workers = 2  # Reduce from default 4

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    results = executor.map(validate_document, documents)
```

**2. Enable Result Caching:**
```python
# Cache validation results
config = {
    'cache': {
        'enabled': True,
        'ttl': 3600  # 1 hour
    }
}
```

### High Memory Usage

**Diagnosis:**
```bash
# Check memory usage
ps aux --sort=-%mem | grep LOKI
```

**Solutions:**

**1. Process Documents in Batches:**
```python
# Instead of loading all documents
documents = [load_doc(f) for f in files]  # Loads all into memory

# Process one at a time
for file in files:
    doc = load_doc(file)
    result = validate(doc)
    save_result(result)
    del doc  # Free memory
```

**2. Increase Swap Space (Linux):**
```bash
# Create swap file
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## Getting Additional Help

### Before Contacting Support

1. **Collect Diagnostic Information:**
   ```bash
   # Generate support bundle
   loki diagnostics --output support-bundle.zip
   ```

2. **Check Logs:**
   ```bash
   # Application logs
   cat /var/log/loki/app.log | tail -100

   # Error logs
   cat /var/log/loki/error.log | tail -50
   ```

3. **Document Steps to Reproduce:**
   - What were you trying to do?
   - What happened instead?
   - Can you reproduce the issue?

### Contact Support

**Email:** support@highlandai.com

**Include:**
- LOKI version number
- Operating system and version
- Error messages (full text)
- Log files
- Support bundle (if requested)

**Priority Support (Professional/Enterprise):**
- Email: priority@highlandai.com
- Phone: +44 (0) 131 XXX XXXX
- Response time: 4 hours (business hours)

**Emergency Support (Enterprise):**
- 24/7 hotline: +44 (0) 131 XXX YYYY
- Dedicated Slack channel

---

*Last Updated: November 2025*
*Version: 1.0*
