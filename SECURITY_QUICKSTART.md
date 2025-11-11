# LOKI Interceptor - Security Features Quick Start

## Overview

LOKI Interceptor now includes enterprise-grade security features to protect against OWASP Top 10 vulnerabilities and common attack vectors.

---

## Key Features

### 1. Input Sanitization

**Location:** `backend/security/sanitizer.py`

**Protects Against:**
- SQL Injection
- XSS (Cross-Site Scripting)
- Command Injection
- Path Traversal
- LDAP Injection
- Template Injection
- Unicode-based attacks

**Usage:**

```python
from backend.security import InputSanitizer, InputType

sanitizer = InputSanitizer()

# Sanitize general text
result = sanitizer.sanitize(
    user_input,
    input_type=InputType.TEXT,
    max_length=10000
)

if not result.is_safe:
    print(f"Security violations: {result.violations}")
    raise ValueError("Unsafe input")

safe_text = result.sanitized
```

**Quick Function:**

```python
from backend.security import sanitize_input

# Raises ValueError if unsafe
safe_text = sanitize_input(user_input, input_type=InputType.TEXT)
```

**Input Types:**
- `InputType.TEXT` - General text
- `InputType.EMAIL` - Email addresses
- `InputType.URL` - URLs
- `InputType.FILENAME` - Filenames
- `InputType.HTML` - HTML content
- `InputType.ALPHANUMERIC` - Letters and numbers only
- `InputType.UUID` - UUIDs
- `InputType.API_KEY` - API keys

---

### 2. Distributed Rate Limiting

**Location:** `backend/security/rate_limiter.py`

**Features:**
- Multiple strategies (sliding window, token bucket, fixed window, adaptive)
- Redis-backed for multi-instance deployment
- Per-IP, per-user, per-API-key scopes
- Automatic violator blocking

**Usage:**

```python
from backend.security.rate_limiter import (
    DistributedRateLimiter,
    RateLimitConfig,
    RateLimitScope,
    RateLimitStrategy,
    rate_limit_decorator
)

# Initialize
limiter = DistributedRateLimiter(redis_client)

# Check limit manually
config = RateLimitConfig(
    requests=100,
    window_seconds=3600,
    strategy=RateLimitStrategy.SLIDING_WINDOW,
    scope=RateLimitScope.PER_IP
)

identifier = limiter.get_identifier(RateLimitScope.PER_IP)
result = limiter.check_rate_limit(identifier, config)

if not result.allowed:
    print(f"Rate limited. Retry after {result.retry_after} seconds")

# Or use decorator
@app.route('/api/endpoint')
@rate_limit_decorator(config)
def my_endpoint():
    return jsonify({'status': 'ok'})
```

**Predefined Limits:**

```python
from backend.security.rate_limiter import RATE_LIMITS

# Use predefined tier limits
RATE_LIMITS['free_tier']        # 100 req/hour
RATE_LIMITS['starter']          # 1000 req/hour
RATE_LIMITS['professional']     # 10000 req/hour
RATE_LIMITS['enterprise']       # 100000 req/hour
RATE_LIMITS['strict']           # 10 req/min (with blocking)
```

---

### 3. API Key Management

**Location:** `backend/security/auth_manager.py`

**Features:**
- Automatic key rotation
- Key expiration
- Scope-based permissions
- Secure credential encryption
- Usage tracking and audit trail

**Usage:**

```python
from backend.security.auth_manager import (
    APIKeyManager,
    RotationPolicy,
    SecureCredentialStore
)

# Initialize
manager = APIKeyManager()

# Generate API key
plain_key, api_key = manager.generate_key(
    name="Production Key",
    scopes=['read:validation', 'write:validation'],
    expires_in_days=90,
    rotation_policy=RotationPolicy.QUARTERLY
)

print(f"API Key: {plain_key}")  # Save this! Only shown once
print(f"Key ID: {api_key.key_id}")

# Validate API key
is_valid, key_obj, error = manager.validate_key(
    plain_key,
    required_scopes=['write:validation']
)

if not is_valid:
    print(f"Invalid: {error}")

# Rotate key
new_plain_key, new_key = manager.rotate_key(
    old_key_id=api_key.key_id,
    grace_period_days=7
)

# Check keys needing rotation
needs_rotation = manager.check_rotation_needed()
for key in needs_rotation:
    print(f"Key {key.name} needs rotation (age: {key._days_until_expiration()} days)")

# Auto-rotate all
rotated = manager.auto_rotate_keys(grace_period_days=7)
```

**Secure Credential Storage:**

```python
from backend.security.auth_manager import SecureCredentialStore

store = SecureCredentialStore(master_key="your-master-key")

# Encrypt and store
store.store_credential('api_key', 'sk-ant-secret-key', storage_dict)

# Retrieve and decrypt
api_key = store.retrieve_credential('api_key', storage_dict)
```

---

### 4. Security Headers & CORS

**Location:** `backend/middleware/security_headers.py`

**Headers Applied:**
- Content-Security-Policy
- X-Frame-Options
- X-Content-Type-Options
- X-XSS-Protection
- Strict-Transport-Security (HSTS)
- Referrer-Policy
- Permissions-Policy

**Usage:**

```python
from backend.middleware import setup_security_middleware

# Quick setup
setup_security_middleware(
    app,
    allowed_origins=['https://yourdomain.com'],
    strict_mode=True
)

# Custom configuration
from backend.middleware import (
    SecurityHeadersMiddleware,
    CORSConfig,
    SecurityHeadersConfig,
    CSPDirective
)

cors_config = CORSConfig(
    enabled=True,
    allowed_origins=['https://app.example.com'],
    allow_credentials=False,
    allowed_methods=['GET', 'POST', 'OPTIONS'],
    allowed_headers=['Content-Type', 'Authorization', 'X-API-Key']
)

headers_config = SecurityHeadersConfig(
    content_security_policy={
        CSPDirective.DEFAULT_SRC.value: ["'self'"],
        CSPDirective.SCRIPT_SRC.value: ["'self'"],
        CSPDirective.STYLE_SRC.value: ["'self'"],
    },
    x_frame_options="DENY",
    strict_transport_security="max-age=31536000; includeSubDomains"
)

middleware = SecurityHeadersMiddleware(
    app,
    cors_config=cors_config,
    headers_config=headers_config
)
```

**Route-Specific CORS:**

```python
from backend.middleware.security_headers import cors_decorator

@app.route('/api/public')
@cors_decorator(allowed_origins=['*'])
def public_endpoint():
    return jsonify({'data': 'public'})
```

---

## Integration Examples

### Example 1: Secure API Endpoint

```python
from flask import Flask, request, jsonify
from backend.security import InputSanitizer, InputType
from backend.security.rate_limiter import rate_limit_decorator, RATE_LIMITS
from backend.security.auth_manager import APIKeyManager

app = Flask(__name__)
sanitizer = InputSanitizer()
key_manager = APIKeyManager()

@app.route('/api/validate', methods=['POST'])
@rate_limit_decorator(RATE_LIMITS['professional'])
def validate_endpoint():
    # 1. Validate API key
    api_key = request.headers.get('x-api-key')
    is_valid, key_obj, error = key_manager.validate_key(
        api_key,
        required_scopes=['write:validation']
    )

    if not is_valid:
        return jsonify({'error': error}), 401

    # 2. Sanitize input
    data = request.json
    text_result = sanitizer.sanitize(
        data.get('text'),
        input_type=InputType.TEXT,
        max_length=50000
    )

    if not text_result.is_safe:
        return jsonify({
            'error': 'Invalid input',
            'violations': text_result.violations
        }), 400

    # 3. Process with safe data
    safe_text = text_result.sanitized

    # Your validation logic here...
    result = {'status': 'validated', 'text': safe_text}

    return jsonify(result), 200
```

### Example 2: Full Application Setup

```python
from flask import Flask
from backend.security import InputSanitizer
from backend.security.rate_limiter import DistributedRateLimiter
from backend.security.auth_manager import APIKeyManager
from backend.middleware import setup_security_middleware
import redis

app = Flask(__name__)

# Setup Redis for distributed rate limiting
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Initialize security components
sanitizer = InputSanitizer()
rate_limiter = DistributedRateLimiter(redis_client)
api_key_manager = APIKeyManager()

# Setup security middleware
setup_security_middleware(
    app,
    allowed_origins=[
        'https://app.yourdomain.com',
        'https://admin.yourdomain.com'
    ],
    strict_mode=True
)

# Your routes here...
```

---

## Running Security Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all security tests
pytest tests/security/ -v

# Run with markers
pytest -m security         # All security tests
pytest -m penetration      # Penetration tests only

# Run with coverage
pytest tests/security/ --cov=backend/security --cov-report=html

# Run specific test file
pytest tests/security/test_penetration.py -v
pytest tests/security/test_injection.py -v
pytest tests/security/test_rate_limiting.py -v
```

---

## Security Monitoring

### Check for Exposed Keys

```python
from backend.security.auth_manager import scan_for_exposed_keys

text = "My key is sk-ant-api03-abc123..."
exposed = scan_for_exposed_keys(text)

if exposed:
    print(f"WARNING: Found exposed keys: {exposed}")
```

### Monitor Rate Limit Violations

```python
# Check rate limiter stats (if implemented)
stats = rate_limiter.get_stats()
print(f"Blocked IPs: {stats.get('blocked_ips')}")
print(f"Violations: {stats.get('violations')}")
```

### API Key Usage Stats

```python
stats = api_key_manager.get_usage_stats()
print(f"Total keys: {stats['total_keys']}")
print(f"Active keys: {stats['active_keys']}")
print(f"Needs rotation: {stats['needs_rotation']}")
```

---

## Common Patterns

### Pattern 1: Validate All Inputs

```python
# Always sanitize user inputs
for field in ['text', 'email', 'url']:
    if field in data:
        result = sanitizer.sanitize(
            data[field],
            input_type=getattr(InputType, field.upper(), InputType.TEXT)
        )
        if not result.is_safe:
            return error_response(result.violations)
        data[field] = result.sanitized
```

### Pattern 2: Tier-Based Rate Limiting

```python
def get_rate_limit_for_user(user):
    tier_map = {
        'free': RATE_LIMITS['free_tier'],
        'starter': RATE_LIMITS['starter'],
        'pro': RATE_LIMITS['professional'],
        'enterprise': RATE_LIMITS['enterprise'],
    }
    return tier_map.get(user.tier, RATE_LIMITS['free_tier'])

@rate_limit_decorator(get_rate_limit_for_user(current_user))
def user_endpoint():
    pass
```

### Pattern 3: Automatic Key Rotation

```python
# Scheduled task (run daily)
def rotate_expiring_keys():
    keys_to_rotate = api_key_manager.check_rotation_needed()

    for key in keys_to_rotate:
        new_plain_key, new_key = api_key_manager.rotate_key(
            key.key_id,
            grace_period_days=7
        )

        # Notify user
        send_email(
            to=key.metadata.get('owner_email'),
            subject='API Key Rotated',
            body=f'New key: {new_plain_key}'
        )
```

---

## Troubleshooting

### Issue: Rate Limiting Too Strict

```python
# Increase limits
config = RateLimitConfig(
    requests=1000,  # Increase
    window_seconds=3600,
    burst_multiplier=2.0  # Allow more burst
)
```

### Issue: Input Validation Too Strict

```python
# Use permissive mode
sanitizer = InputSanitizer(level=SanitizationLevel.PERMISSIVE)

# Or allow specific content
result = sanitizer.sanitize(
    user_input,
    allow_html=True  # If HTML is expected
)
```

### Issue: CORS Blocking Requests

```python
# Check origin is in whitelist
cors_config.allowed_origins.append('https://newdomain.com')

# Or temporarily use wildcard (NOT for production!)
cors_config.allowed_origins = ['*']
```

---

## Best Practices

1. **Always validate API keys** before processing requests
2. **Always sanitize inputs** at the boundary (controller level)
3. **Use distributed rate limiting** in production (Redis)
4. **Rotate keys regularly** (quarterly at minimum)
5. **Monitor security logs** daily
6. **Run security tests** before deployment
7. **Keep dependencies updated** weekly
8. **Use HTTPS only** in production
9. **Implement proper logging** for security events
10. **Have an incident response plan**

---

## Migration Guide

### Migrating from Basic Security

```python
# OLD (basic security)
from core.security import SecurityManager, RateLimiter

security = SecurityManager()
rate_limiter = RateLimiter()

# NEW (enhanced security)
from backend.security import InputSanitizer
from backend.security.rate_limiter import DistributedRateLimiter
from backend.security.auth_manager import APIKeyManager

sanitizer = InputSanitizer()
rate_limiter = DistributedRateLimiter(redis_client)
api_key_manager = APIKeyManager()
```

### Adding to Existing Routes

```python
# Step 1: Add input sanitization
@app.route('/api/endpoint', methods=['POST'])
def my_endpoint():
    data = request.json

    # Add this
    result = sanitizer.sanitize(data.get('text'))
    if not result.is_safe:
        return jsonify({'error': 'Invalid input'}), 400

    # Rest of your code...

# Step 2: Add rate limiting decorator
@rate_limit_decorator(RATE_LIMITS['professional'])
@app.route('/api/endpoint', methods=['POST'])
def my_endpoint():
    # Your code...

# Step 3: Add API key validation
def my_endpoint():
    api_key = request.headers.get('x-api-key')
    is_valid, _, error = api_key_manager.validate_key(api_key)
    if not is_valid:
        return jsonify({'error': error}), 401

    # Your code...
```

---

## Additional Resources

- **Full Audit Report:** `/home/user/loki-interceptor/SECURITY_AUDIT_REPORT.md`
- **Test Suite:** `/home/user/loki-interceptor/tests/security/`
- **OWASP Top 10:** https://owasp.org/Top10/
- **Security Best Practices:** https://cheatsheetseries.owasp.org/

---

## Support

For security-related questions:
- Review the full security audit report
- Check test cases for examples
- Contact: security@loki-interceptor.com

**Remember: Security is a journey, not a destination. Keep your dependencies updated and run regular security scans!**
