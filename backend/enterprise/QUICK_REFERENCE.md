# LOKI Enterprise - Quick Reference Card

## Installation

```bash
cd backend/enterprise
pip install -r requirements.txt
```

## Database Setup

```bash
# Create database
python migrate.py create-db --database-url postgresql://localhost/postgres

# Run migrations
python migrate.py migrate --database-url postgresql://localhost/loki_db

# Rollback (WARNING: Deletes all data)
python migrate.py rollback --database-url postgresql://localhost/loki_db
```

## Environment Variables (.env)

```env
# Required
DATABASE_URL=postgresql://user:pass@localhost:5432/loki_db
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-secret-key-32-chars-minimum

# Optional (with defaults)
ENVIRONMENT=development
DEBUG=true
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
RATE_LIMIT_ENABLED=true
AUDIT_RETENTION_DAYS=365
```

## Quick Start Code

### Initialize Managers

```python
from backend.enterprise import *
from backend.enterprise.config import load_config
import psycopg2, redis

config = load_config()
db = psycopg2.connect(config.database.url)
cache = redis.from_url(config.redis.url)

org_mgr = OrganizationManager(db, cache)
auth_mgr = AuthManager(db, cache)
rbac_mgr = RBACManager(db)
audit_log = AuditLogger(db, cache)
security_mgr = SecurityManager(cache)
```

### Create Organization

```python
org = org_mgr.create_organization(
    name="Acme Corp",
    tier=SubscriptionTier.PROFESSIONAL,
    owner_user_id="user-123"
)
```

### Generate JWT Tokens

```python
access = auth_mgr.token_manager.create_access_token(
    user_id="user-123", org_id=org.id
)
refresh = auth_mgr.token_manager.create_refresh_token(
    user_id="user-123", org_id=org.id
)
```

### Create API Key

```python
key, api_key_obj = auth_mgr.api_key_manager.generate_api_key(
    user_id="user-123",
    org_id=org.id,
    name="Production API",
    scopes=["read", "write"]
)
# Save 'key' - only shown once!
```

### Assign Role

```python
admin_role = rbac_mgr.get_role_by_name(RoleName.ADMIN.value)
rbac_mgr.assign_role_to_user(
    user_id="user-123",
    role_id=admin_role.id,
    org_id=org.id
)
```

### Check Permission

```python
# Check
has_perm = rbac_mgr.check_permission(
    user_id="user-123",
    org_id=org.id,
    permission=Permission.DOC_DELETE
)

# Require (raises PermissionError if denied)
rbac_mgr.require_permission(
    user_id="user-123",
    org_id=org.id,
    permission=Permission.DOC_DELETE
)
```

### Log Audit Event

```python
# Simple log
audit_log.log(
    action=AuditAction.DOC_CREATED,
    user_id="user-123",
    org_id=org.id,
    resource_type="document",
    resource_id="doc-456"
)

# Log with state change
audit_log.log_change(
    action=AuditAction.ORG_UPDATED,
    user_id="user-123",
    org_id=org.id,
    resource_type="organization",
    resource_id=org.id,
    before={"status": "trial"},
    after={"status": "active"}
)
```

### Search Audit Logs

```python
events = audit_log.search(
    org_id=org.id,
    action=AuditAction.LOGIN,
    start_date=datetime.now() - timedelta(days=7)
)
```

### Rate Limiting

```python
config = RateLimitConfig(
    requests=100,
    window_seconds=3600,
    strategy=RateLimitStrategy.SLIDING_WINDOW
)

result = security_mgr.rate_limiter.check_rate_limit(
    identifier="user-123",
    config=config
)

if result['allowed']:
    # Process request
    pass
else:
    # Rate limited
    retry_after = result['retry_after']
```

### Request Signing

```python
# Sign request
signature = security_mgr.request_signer.sign_request(
    method="POST",
    path="/api/docs",
    body='{"title":"Test"}',
    timestamp=int(time.time())
)

# Verify request
is_valid = security_mgr.request_signer.verify_request(
    signature=signature,
    method="POST",
    path="/api/docs",
    body='{"title":"Test"}',
    timestamp=timestamp
)
```

### CSRF Protection

```python
# Generate token
csrf_token = security_mgr.csrf_protection.generate_token(
    session_id=session_id
)

# Validate token
is_valid = security_mgr.csrf_protection.validate_token(
    session_id=session_id,
    token=csrf_token
)
```

## Predefined Roles & Permissions

| Role               | Permissions                          | Use Case                    |
|--------------------|--------------------------------------|-----------------------------|
| Super Admin        | system:admin (all)                   | Platform administrators     |
| Admin              | 23 permissions                       | Organization admins         |
| Compliance Officer | 16 permissions                       | Compliance team             |
| Auditor            | 10 read-only permissions             | External auditors           |
| Viewer             | 4 basic read permissions             | Stakeholders                |

### Key Permissions

```python
# Organization
Permission.ORG_VIEW
Permission.ORG_UPDATE
Permission.ORG_MANAGE_USERS

# Documents
Permission.DOC_VIEW
Permission.DOC_CREATE
Permission.DOC_DELETE
Permission.DOC_ANALYZE

# Compliance
Permission.COMPLIANCE_VIEW
Permission.COMPLIANCE_RUN
Permission.COMPLIANCE_CONFIGURE

# Audit
Permission.AUDIT_VIEW
Permission.AUDIT_EXPORT

# Users
Permission.USER_CREATE
Permission.USER_DELETE
Permission.USER_INVITE
```

## Subscription Tiers

| Tier         | Max Users | Storage | API Limit/hr | Features                    |
|--------------|-----------|---------|--------------|------------------------------|
| Free         | 10        | 10 GB   | 100          | Basic compliance            |
| Starter      | 50        | 100 GB  | 1,000        | + API access, analytics     |
| Professional | 200       | 500 GB  | 10,000       | + Custom rules, support     |
| Enterprise   | Unlimited | ∞       | 100,000      | + SSO, audit, SLA           |

## Common Audit Actions

```python
# Authentication
AuditAction.LOGIN
AuditAction.LOGOUT
AuditAction.LOGIN_FAILED

# Users
AuditAction.USER_CREATED
AuditAction.USER_UPDATED
AuditAction.USER_DELETED

# Documents
AuditAction.DOC_CREATED
AuditAction.DOC_VIEWED
AuditAction.DOC_UPDATED
AuditAction.DOC_DELETED

# Roles
AuditAction.ROLE_ASSIGNED
AuditAction.ROLE_REVOKED

# Access
AuditAction.ACCESS_GRANTED
AuditAction.ACCESS_DENIED
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=backend.enterprise --cov-report=html

# Specific test file
pytest tests/test_auth.py -v

# Specific test
pytest tests/test_auth.py::TestTokenManager::test_create_access_token -v
```

## Flask Middleware Pattern

```python
@app.before_request
def security_middleware():
    # 1. Extract & verify token
    token = request.headers.get('Authorization', '')[7:]
    payload = auth_mgr.token_manager.verify_token(token)
    g.user_id = payload['sub']
    g.org_id = payload['org_id']

    # 2. Set tenant context
    TenantContext.set_current_org(g.org_id)

    # 3. Rate limiting
    rate_result = security_mgr.rate_limiter.check_rate_limit(...)
    if not rate_result['allowed']:
        abort(429)

    # 4. CSRF validation (POST/PUT/DELETE)
    if request.method in ['POST', 'PUT', 'DELETE']:
        csrf_token = request.headers.get('X-CSRF-Token')
        if not security_mgr.csrf_protection.validate_token(...):
            abort(403)

@app.teardown_request
def cleanup(error=None):
    TenantContext.clear()
```

## Decorator Pattern

```python
from functools import wraps

def require_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            rbac_mgr.require_permission(
                g.user_id, g.org_id, permission
            )
            return f(*args, **kwargs)
        return decorated
    return decorator

@app.route('/documents', methods=['POST'])
@require_permission(Permission.DOC_CREATE)
def create_document():
    # Permission already checked
    pass
```

## Compliance Reporting

```python
from backend.enterprise.audit_trail import ComplianceReporter

reporter = ComplianceReporter(audit_log)

# Access control report
access_report = reporter.generate_access_report(
    org_id="org-123",
    start_date=datetime(2025, 1, 1),
    end_date=datetime(2025, 1, 31)
)

# Complete compliance package
package = reporter.generate_compliance_package(
    org_id="org-123",
    start_date=start,
    end_date=end
)
# Returns: access_report, change_report, security_report, audit_log_export
```

## Troubleshooting

### Token Expired
```python
try:
    payload = auth_mgr.token_manager.verify_token(token)
except jwt.InvalidTokenError as e:
    # Use refresh token to get new access token
    new_access, new_refresh = auth_mgr.token_manager.refresh_access_token(
        refresh_token
    )
```

### Permission Denied
```python
try:
    rbac_mgr.require_permission(user_id, org_id, Permission.DOC_DELETE)
except PermissionError:
    # Check user's roles
    roles = rbac_mgr.get_user_roles(user_id, org_id)
    # Assign appropriate role or grant resource-level permission
```

### Rate Limited
```python
result = security_mgr.rate_limiter.check_rate_limit(identifier, config)
if not result['allowed']:
    retry_after = result['retry_after']
    # Wait or return 429 with Retry-After header
```

## Security Checklist

- [ ] Set strong JWT_SECRET_KEY (32+ characters)
- [ ] Enable HTTPS in production (HSTS header)
- [ ] Configure CORS appropriately
- [ ] Set up Redis authentication
- [ ] Enable PostgreSQL SSL
- [ ] Rotate API keys regularly
- [ ] Configure rate limits per tier
- [ ] Set up audit log retention
- [ ] Enable row-level security
- [ ] Configure backups
- [ ] Set up monitoring/alerts

## File Locations

```
C:\Users\jpmcm.DESKTOP-CQ0CL93\OneDrive\Desktop\HighlandAI\LOKI_EXPERIMENTAL_V2\backend\enterprise\

Core Modules:
  multi_tenant.py          # Organizations & tenants
  auth.py                  # Authentication
  rbac.py                  # Roles & permissions
  audit_trail.py           # Audit logging
  security.py              # Security features

Configuration:
  config.py                # Config management
  requirements.txt         # Dependencies
  .env                     # Environment vars (create this)

Utilities:
  migrate.py               # Database migrations
  example_integration.py   # Flask integration

Documentation:
  README.md                # Full documentation
  IMPLEMENTATION_SUMMARY.md # Implementation details
  QUICK_REFERENCE.md       # This file

Tests:
  tests/test_*.py          # Unit tests
```

## Support

For detailed documentation, see `README.md`
For implementation details, see `IMPLEMENTATION_SUMMARY.md`
For working examples, see `example_integration.py`
