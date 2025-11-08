# LOKI Enterprise Multi-Tenancy System

Production-ready enterprise features for the LOKI compliance platform, including multi-tenant organization management, authentication, role-based access control, comprehensive audit trails, and security hardening.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Modules](#modules)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Database Setup](#database-setup)
- [Testing](#testing)
- [Security Best Practices](#security-best-practices)
- [API Reference](#api-reference)

## Overview

The LOKI Enterprise system provides a complete multi-tenancy solution with:

- **Multi-Tenant Architecture**: Complete data isolation per organization
- **Authentication**: OAuth2, JWT tokens, API keys, session management
- **Authorization**: Role-based access control with 4 predefined roles
- **Audit Trails**: Comprehensive logging of all system activities
- **Security**: Request signing, CSRF protection, rate limiting, input validation

## Architecture

```
backend/enterprise/
├── __init__.py              # Package initialization & exports
├── multi_tenant.py          # Organization & tenant management
├── auth.py                  # Authentication system
├── rbac.py                  # Role-based access control
├── audit_trail.py           # Audit logging & compliance
├── security.py              # Security hardening
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── tests/                  # Unit tests
    ├── test_multi_tenant.py
    ├── test_auth.py
    ├── test_rbac.py
    ├── test_audit_trail.py
    └── test_security.py
```

## Modules

### 1. Multi-Tenant (`multi_tenant.py`)

**Organization Management**
- CRUD operations for organizations
- User-to-organization mappings
- Subscription tier management (Free, Starter, Professional, Enterprise)
- Data isolation enforcement
- PostgreSQL row-level security support

**Key Classes:**
- `Organization`: Organization entity
- `OrganizationManager`: Organization lifecycle management
- `TenantContext`: Request-scoped tenant isolation
- `UserOrganizationMapping`: User-org relationships

### 2. Authentication (`auth.py`)

**Features:**
- JWT access & refresh tokens
- API key generation with rotation
- Session management (Redis-backed)
- OAuth2 flow support (Google, Microsoft, GitHub, SAML)
- Multi-factor authentication ready

**Key Classes:**
- `TokenManager`: JWT token operations
- `APIKeyManager`: API key lifecycle
- `SessionManager`: Session handling
- `AuthManager`: Unified authentication

### 3. RBAC (`rbac.py`)

**Predefined Roles:**
- **Super Admin**: Full system access
- **Admin**: Organization-level full access
- **Compliance Officer**: Compliance operations & document management
- **Auditor**: Read-only access to everything
- **Viewer**: Basic read-only access

**Features:**
- 30+ granular permissions
- Custom role creation per organization
- Resource-level access control
- Permission inheritance
- Audit trail integration

**Key Classes:**
- `RBACManager`: Role & permission management
- `ResourceAccessControl`: Resource-level permissions
- `Role`: Role entity
- `Permission`: Permission enumeration

### 4. Audit Trail (`audit_trail.py`)

**Features:**
- Complete action logging (who, what, when, where)
- Before/after state tracking
- Searchable audit logs with filters
- Compliance report generation (SOC2, ISO27001, GDPR)
- Data retention policies
- Export to JSON/CSV

**Key Classes:**
- `AuditLogger`: Central logging system
- `AuditEvent`: Audit event entity
- `ComplianceReporter`: Compliance report generation

### 5. Security (`security.py`)

**Features:**
- HMAC-SHA256 request signing
- CSRF token generation & validation
- Distributed rate limiting (Redis-backed)
- Input validation & sanitization
- Security headers (HSTS, CSP, etc.)
- IP whitelisting/blacklisting

**Key Classes:**
- `SecurityManager`: Central security coordinator
- `RequestSigner`: Request signature verification
- `CSRFProtection`: CSRF token handling
- `RateLimiter`: Rate limiting (3 strategies)
- `InputValidator`: Input validation

## Installation

### 1. Install Dependencies

```bash
cd backend/enterprise
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create `.env` file:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/loki_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
JWT_SECRET_KEY=your-secret-key-here
API_SECRET_KEY=your-api-secret-here

# Session
SESSION_EXPIRE_HOURS=24

# Rate Limiting
RATE_LIMIT_ENABLED=true
```

### 3. Initialize Database

```bash
# Run PostgreSQL schema
psql -U user -d loki_db -f schema.sql
```

See [Database Setup](#database-setup) for complete SQL schemas.

## Quick Start

### Basic Setup

```python
from backend.enterprise import (
    OrganizationManager,
    AuthManager,
    RBACManager,
    AuditLogger,
    SecurityManager,
)

# Initialize managers
org_manager = OrganizationManager(db_connection=db, cache_backend=redis)
auth_manager = AuthManager(db_connection=db, cache_backend=redis)
rbac_manager = RBACManager(db_connection=db)
audit_logger = AuditLogger(db_connection=db)
security_manager = SecurityManager(cache_backend=redis)
```

### Create Organization

```python
# Create organization with owner
org = org_manager.create_organization(
    name="Acme Corporation",
    tier=SubscriptionTier.PROFESSIONAL,
    owner_user_id="user-123",
)

print(f"Created org: {org.id} with slug: {org.slug}")
```

### User Authentication

```python
# Generate JWT tokens
access_token = auth_manager.token_manager.create_access_token(
    user_id="user-123",
    org_id=org.id,
)

# Verify token
payload = auth_manager.token_manager.verify_token(
    access_token,
    TokenType.ACCESS,
)

# Create API key
plain_key, api_key = auth_manager.api_key_manager.generate_api_key(
    user_id="user-123",
    org_id=org.id,
    name="Production API Key",
    scopes=["read", "write"],
)
```

### Assign Roles

```python
# Assign admin role to user
admin_role = rbac_manager.get_role_by_name(RoleName.ADMIN.value)

rbac_manager.assign_role_to_user(
    user_id="user-123",
    role_id=admin_role.id,
    org_id=org.id,
)

# Check permission
has_permission = rbac_manager.check_permission(
    user_id="user-123",
    org_id=org.id,
    permission=Permission.DOC_DELETE,
)
```

### Audit Logging

```python
# Log user action
audit_logger.log(
    action=AuditAction.DOC_CREATED,
    user_id="user-123",
    org_id=org.id,
    resource_type="document",
    resource_id="doc-456",
    metadata={"filename": "contract.pdf"},
)

# Log state change
audit_logger.log_change(
    action=AuditAction.ORG_UPDATED,
    user_id="user-123",
    org_id=org.id,
    resource_type="organization",
    resource_id=org.id,
    before={"status": "trial"},
    after={"status": "active"},
)

# Search audit logs
events = audit_logger.search(
    org_id=org.id,
    action=AuditAction.DOC_CREATED,
    start_date=datetime.now() - timedelta(days=7),
)
```

### Rate Limiting

```python
# Create rate limit config
rate_config = RateLimitConfig(
    requests=100,
    window_seconds=3600,
    strategy=RateLimitStrategy.SLIDING_WINDOW,
)

# Check rate limit
result = security_manager.rate_limiter.check_rate_limit(
    identifier="user-123",
    config=rate_config,
)

if result['allowed']:
    # Process request
    pass
else:
    # Return 429 Too Many Requests
    print(f"Rate limited. Retry after {result['retry_after']} seconds")
```

## Configuration

### Subscription Tiers

Each tier has different limits and features:

| Tier         | Max Users | Max Storage | API Access | Rate Limit |
|--------------|-----------|-------------|------------|------------|
| Free         | 10        | 10 GB       | No         | 100/hour   |
| Starter      | 50        | 100 GB      | Yes        | 1000/hour  |
| Professional | 200       | 500 GB      | Yes        | 10k/hour   |
| Enterprise   | Unlimited | Unlimited   | Yes        | 100k/hour  |

### Rate Limiting Strategies

**1. Fixed Window**
- Simple counter reset at fixed intervals
- Pros: Simple, low memory
- Cons: Allows bursts at window boundaries

**2. Sliding Window**
- More accurate, prevents boundary bursts
- Pros: Accurate, fair
- Cons: Higher memory usage

**3. Token Bucket**
- Allows controlled bursts
- Pros: Flexible, handles traffic spikes
- Cons: More complex

## Usage Examples

### Tenant Isolation

```python
from backend.enterprise.multi_tenant import TenantContext

# Set tenant context for request
TenantContext.set_current_org("org-123")
TenantContext.set_user("user-456")

# All operations now scoped to org-123
current_org = TenantContext.require_org()

# Clear context after request
TenantContext.clear()
```

### Request Signing

```python
# Sign API request
timestamp = int(time.time())
signature = security_manager.request_signer.sign_request(
    method="POST",
    path="/api/documents",
    body=json.dumps({"title": "Contract"}),
    timestamp=timestamp,
)

# Client includes in headers:
# X-Signature: <signature>
# X-Timestamp: <timestamp>

# Server verifies
is_valid = security_manager.request_signer.verify_request(
    signature=request.headers['X-Signature'],
    method=request.method,
    path=request.path,
    body=request.get_data(as_text=True),
    timestamp=int(request.headers['X-Timestamp']),
)
```

### CSRF Protection

```python
# Generate token (on form render)
csrf_token = security_manager.csrf_protection.generate_token(
    session_id=session['id']
)

# Include in form: <input type="hidden" name="csrf_token" value="{{ csrf_token }}">

# Validate on submission
is_valid = security_manager.csrf_protection.validate_token(
    session_id=session['id'],
    token=request.form['csrf_token'],
)
```

### Compliance Reporting

```python
from backend.enterprise.audit_trail import ComplianceReporter

reporter = ComplianceReporter(audit_logger)

# Generate access control report
access_report = reporter.generate_access_report(
    org_id="org-123",
    start_date=datetime(2025, 1, 1),
    end_date=datetime(2025, 1, 31),
)

# Generate complete compliance package
compliance_package = reporter.generate_compliance_package(
    org_id="org-123",
    start_date=datetime(2025, 1, 1),
    end_date=datetime(2025, 1, 31),
)
```

## Database Setup

### PostgreSQL Schemas

All SQL schemas are included in the respective module files:

1. **Organizations & Users**: See `multi_tenant.py` (bottom)
2. **Authentication**: See `auth.py` (bottom)
3. **RBAC**: See `rbac.py` (bottom)
4. **Audit Events**: See `audit_trail.py` (bottom)

### Complete Schema Initialization

```sql
-- Run all schemas in order
\i multi_tenant_schema.sql
\i auth_schema.sql
\i rbac_schema.sql
\i audit_schema.sql

-- Enable row-level security
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;

-- Create initial super admin user
INSERT INTO users (email, username, password_hash, is_verified)
VALUES ('admin@loki.com', 'admin', 'hashed_password', true);
```

## Testing

### Run All Tests

```bash
# Run all unit tests
pytest backend/enterprise/tests/ -v

# With coverage
pytest backend/enterprise/tests/ --cov=backend.enterprise --cov-report=html

# Run specific test file
pytest backend/enterprise/tests/test_auth.py -v
```

### Test Coverage

Current test coverage includes:
- Multi-tenant operations
- Token generation & validation
- API key management
- Session handling
- Role & permission checks
- Audit logging
- Rate limiting
- Input validation
- Request signing
- CSRF protection

## Security Best Practices

### 1. Secret Management

- Never commit secrets to version control
- Use environment variables or secret management systems
- Rotate secrets regularly
- Use strong, randomly generated keys (≥32 bytes)

### 2. Database Security

- Use PostgreSQL row-level security (RLS)
- Enable SSL/TLS for database connections
- Implement prepared statements (prevent SQL injection)
- Regular backups with encryption

### 3. Authentication

- Enforce strong password policies
- Implement MFA for privileged accounts
- Use short-lived access tokens (30 min)
- Longer-lived refresh tokens (7 days)
- Rotate API keys regularly

### 4. Rate Limiting

- Apply different limits per tier
- Use distributed rate limiting (Redis)
- Implement exponential backoff
- Monitor for abuse patterns

### 5. Audit Logging

- Log all security-relevant events
- Include context (IP, user agent)
- Implement log integrity (hashing)
- Set retention policies (365 days)
- Regular compliance reviews

## API Reference

### Organization Manager

```python
class OrganizationManager:
    def create_organization(name, slug, tier, owner_user_id) -> Organization
    def get_organization(org_id) -> Optional[Organization]
    def update_organization(org_id, updates) -> Organization
    def delete_organization(org_id, hard_delete=False) -> bool
    def add_user_to_org(user_id, org_id, role) -> UserOrganizationMapping
    def remove_user_from_org(user_id, org_id) -> bool
```

### Auth Manager

```python
class TokenManager:
    def create_access_token(user_id, org_id) -> str
    def create_refresh_token(user_id, org_id) -> str
    def verify_token(token, expected_type) -> Dict[str, Any]
    def refresh_access_token(refresh_token) -> Tuple[str, str]

class APIKeyManager:
    def generate_api_key(user_id, org_id, name, scopes) -> Tuple[str, APIKey]
    def validate_api_key(plain_key) -> Optional[APIKey]
    def revoke_api_key(key_id) -> bool
    def rotate_api_key(key_id) -> Tuple[str, APIKey]
```

### RBAC Manager

```python
class RBACManager:
    def create_custom_role(org_id, name, permissions) -> Role
    def assign_role_to_user(user_id, role_id, org_id) -> UserRole
    def revoke_role_from_user(user_id, role_id, org_id) -> bool
    def check_permission(user_id, org_id, permission) -> bool
    def require_permission(user_id, org_id, permission) -> None
```

### Audit Logger

```python
class AuditLogger:
    def log(action, user_id, org_id, **kwargs) -> AuditEvent
    def log_access(user_id, action, resource_type, granted) -> AuditEvent
    def log_change(action, user_id, before, after) -> AuditEvent
    def search(org_id, user_id, action, start_date, end_date) -> List[AuditEvent]
    def export_logs(org_id, start_date, end_date, format) -> str
```

### Security Manager

```python
class SecurityManager:
    request_signer: RequestSigner
    csrf_protection: CSRFProtection
    rate_limiter: RateLimiter
    input_validator: InputValidator

    def get_security_headers() -> Dict[str, str]
    def create_rate_limit_config(tier) -> RateLimitConfig
```

## License

Copyright (c) 2025 LOKI Team. All rights reserved.

## Support

For issues, questions, or contributions, please contact the LOKI development team.
