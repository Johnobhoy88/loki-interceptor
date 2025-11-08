"""
LOKI Enterprise Integration Example

Demonstrates how to integrate all enterprise modules into a Flask application.
This is a complete working example showing authentication, RBAC, audit logging,
and security middleware.
"""

from flask import Flask, request, jsonify, g, abort
from functools import wraps
import redis
import psycopg2
from datetime import datetime

from backend.enterprise import (
    OrganizationManager,
    AuthManager,
    RBACManager,
    AuditLogger,
    SecurityManager,
    Permission,
    AuditAction,
    SubscriptionTier,
    TenantContext,
)
from backend.enterprise.config import load_config


# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

# Load configuration
config = load_config()

# Initialize database connections
db_conn = psycopg2.connect(config.database.url)
redis_client = redis.from_url(config.redis.url)

# Initialize enterprise managers
org_manager = OrganizationManager(db_connection=db_conn, cache_backend=redis_client)
auth_manager = AuthManager(db_connection=db_conn, cache_backend=redis_client)
rbac_manager = RBACManager(db_connection=db_conn, audit_logger=None)  # Set later
audit_logger = AuditLogger(db_connection=db_conn, cache_backend=redis_client)
security_manager = SecurityManager(cache_backend=redis_client)

# Link audit logger to RBAC
rbac_manager.audit_logger = audit_logger


# ============================================================================
# MIDDLEWARE
# ============================================================================

@app.before_request
def security_middleware():
    """Security checks before each request."""

    # Add security headers
    g.security_headers = security_manager.get_security_headers()

    # Skip security for health check
    if request.path == '/health':
        return None

    # Extract authentication token
    auth_header = request.headers.get('Authorization', '')
    api_key_header = request.headers.get('X-API-Key', '')

    if auth_header.startswith('Bearer '):
        # JWT authentication
        token = auth_header[7:]
        try:
            payload = auth_manager.token_manager.verify_token(token)
            g.user_id = payload['sub']
            g.org_id = payload['org_id']
        except Exception as e:
            abort(401, f"Invalid token: {str(e)}")

    elif api_key_header:
        # API key authentication
        api_key = auth_manager.api_key_manager.validate_api_key(api_key_header)
        if not api_key:
            abort(401, "Invalid API key")

        g.user_id = api_key.user_id
        g.org_id = api_key.org_id

    else:
        # No authentication provided
        abort(401, "Authentication required")

    # Set tenant context
    TenantContext.set_current_org(g.org_id)
    TenantContext.set_user(g.user_id)

    # Rate limiting
    org = org_manager.get_organization(g.org_id)
    if org:
        rate_config = security_manager.create_rate_limit_config(tier=org.tier.value)
        rate_result = security_manager.rate_limiter.check_rate_limit(
            identifier=f"user:{g.user_id}",
            config=rate_config,
        )

        if not rate_result['allowed']:
            abort(429, {
                'error': 'Rate limit exceeded',
                'retry_after': rate_result['retry_after'],
            })

    # CSRF validation for state-changing methods
    if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
        session_id = request.headers.get('X-Session-ID')
        csrf_token = request.headers.get('X-CSRF-Token')

        if session_id and csrf_token:
            if not security_manager.csrf_protection.validate_token(session_id, csrf_token):
                abort(403, "Invalid CSRF token")


@app.after_request
def add_security_headers(response):
    """Add security headers to response."""
    for header, value in g.get('security_headers', {}).items():
        response.headers[header] = value
    return response


@app.teardown_request
def cleanup_tenant_context(error=None):
    """Clean up tenant context after request."""
    TenantContext.clear()


# ============================================================================
# DECORATORS
# ============================================================================

def require_permission(permission: Permission):
    """Decorator to require specific permission."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            rbac_manager.require_permission(
                user_id=g.user_id,
                org_id=g.org_id,
                permission=permission,
            )
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def audit_log(action: AuditAction, resource_type: str = None):
    """Decorator to automatically log action."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            result = f(*args, **kwargs)

            # Log successful action
            audit_logger.log(
                action=action,
                user_id=g.user_id,
                org_id=g.org_id,
                resource_type=resource_type,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                success=True,
            )

            return result
        return decorated_function
    return decorator


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})


# --- Authentication Endpoints ---

@app.route('/auth/login', methods=['POST'])
def login():
    """User login endpoint."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Authenticate user
    user = auth_manager.authenticate_user(email, password)

    if not user:
        audit_logger.log(
            action=AuditAction.LOGIN_FAILED,
            user_id=None,
            org_id=None,
            ip_address=request.remote_addr,
            metadata={'email': email},
            success=False,
        )
        abort(401, "Invalid credentials")

    # Get user's primary organization
    orgs = org_manager.get_user_organizations(user.id)
    if not orgs:
        abort(403, "User not assigned to any organization")

    primary_org = orgs[0]

    # Create session and tokens
    tokens = auth_manager.login(
        user=user,
        org_id=primary_org.id,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
    )

    # Log successful login
    audit_logger.log(
        action=AuditAction.LOGIN,
        user_id=user.id,
        org_id=primary_org.id,
        ip_address=request.remote_addr,
        success=True,
    )

    return jsonify(tokens)


@app.route('/auth/refresh', methods=['POST'])
def refresh_token():
    """Refresh access token."""
    data = request.get_json()
    refresh_token = data.get('refresh_token')

    try:
        new_access, new_refresh = auth_manager.token_manager.refresh_access_token(refresh_token)

        return jsonify({
            'access_token': new_access,
            'refresh_token': new_refresh,
            'token_type': 'Bearer',
        })

    except Exception as e:
        abort(401, f"Invalid refresh token: {str(e)}")


# --- Organization Endpoints ---

@app.route('/organizations', methods=['POST'])
@require_permission(Permission.ORG_CREATE)
@audit_log(AuditAction.ORG_CREATED, 'organization')
def create_organization():
    """Create new organization."""
    data = request.get_json()

    org = org_manager.create_organization(
        name=data['name'],
        tier=SubscriptionTier(data.get('tier', 'free')),
        owner_user_id=g.user_id,
    )

    return jsonify(org.to_dict()), 201


@app.route('/organizations/<org_id>', methods=['GET'])
@require_permission(Permission.ORG_VIEW)
def get_organization(org_id):
    """Get organization details."""
    org = org_manager.get_organization(org_id)

    if not org:
        abort(404, "Organization not found")

    return jsonify(org.to_dict())


@app.route('/organizations/<org_id>', methods=['PUT'])
@require_permission(Permission.ORG_UPDATE)
def update_organization(org_id):
    """Update organization."""
    data = request.get_json()

    # Get current state for audit
    org = org_manager.get_organization(org_id)
    before_state = org.to_dict() if org else {}

    # Update organization
    updated_org = org_manager.update_organization(org_id, data)

    # Log change
    audit_logger.log_change(
        action=AuditAction.ORG_UPDATED,
        user_id=g.user_id,
        org_id=org_id,
        resource_type='organization',
        resource_id=org_id,
        before=before_state,
        after=updated_org.to_dict(),
    )

    return jsonify(updated_org.to_dict())


# --- User Endpoints ---

@app.route('/organizations/<org_id>/users', methods=['GET'])
@require_permission(Permission.USER_VIEW)
def list_org_users(org_id):
    """List users in organization."""
    users = org_manager.get_org_users(org_id)
    return jsonify([u.to_dict() for u in users])


@app.route('/organizations/<org_id>/users', methods=['POST'])
@require_permission(Permission.USER_INVITE)
@audit_log(AuditAction.ORG_USER_ADDED, 'user_organization')
def add_user_to_org(org_id):
    """Add user to organization."""
    data = request.get_json()

    mapping = org_manager.add_user_to_org(
        user_id=data['user_id'],
        org_id=org_id,
        role=data.get('role', 'member'),
        invited_by=g.user_id,
    )

    return jsonify(mapping.to_dict()), 201


# --- Document Endpoints (Example) ---

@app.route('/documents', methods=['POST'])
@require_permission(Permission.DOC_CREATE)
@audit_log(AuditAction.DOC_CREATED, 'document')
def create_document():
    """Create document."""
    data = request.get_json()

    # Your document creation logic here
    document = {
        'id': 'doc-123',
        'title': data['title'],
        'org_id': g.org_id,
        'created_by': g.user_id,
    }

    return jsonify(document), 201


@app.route('/documents/<doc_id>', methods=['GET'])
@require_permission(Permission.DOC_VIEW)
def get_document(doc_id):
    """Get document."""

    # Log view access
    audit_logger.log(
        action=AuditAction.DOC_VIEWED,
        user_id=g.user_id,
        org_id=g.org_id,
        resource_type='document',
        resource_id=doc_id,
    )

    # Your document retrieval logic here
    document = {'id': doc_id, 'title': 'Example Document'}

    return jsonify(document)


@app.route('/documents/<doc_id>', methods=['DELETE'])
@require_permission(Permission.DOC_DELETE)
@audit_log(AuditAction.DOC_DELETED, 'document')
def delete_document(doc_id):
    """Delete document."""

    # Your document deletion logic here

    return '', 204


# --- Audit Endpoints ---

@app.route('/audit/events', methods=['GET'])
@require_permission(Permission.AUDIT_VIEW)
def search_audit_events():
    """Search audit events."""

    # Parse query parameters
    user_id = request.args.get('user_id')
    action = request.args.get('action')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    limit = int(request.args.get('limit', 100))

    # Parse dates
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None

    # Search events
    events = audit_logger.search(
        org_id=g.org_id,
        user_id=user_id,
        action=AuditAction(action) if action else None,
        start_date=start,
        end_date=end,
        limit=limit,
    )

    return jsonify([e.to_dict() for e in events])


@app.route('/audit/export', methods=['POST'])
@require_permission(Permission.AUDIT_EXPORT)
def export_audit_logs():
    """Export audit logs."""
    data = request.get_json()

    start_date = datetime.fromisoformat(data['start_date'])
    end_date = datetime.fromisoformat(data['end_date'])
    format = data.get('format', 'json')

    export_data = audit_logger.export_logs(
        org_id=g.org_id,
        start_date=start_date,
        end_date=end_date,
        format=format,
    )

    # Log export action
    audit_logger.log(
        action=AuditAction.DATA_EXPORTED,
        user_id=g.user_id,
        org_id=g.org_id,
        metadata={'format': format, 'start': start_date.isoformat(), 'end': end_date.isoformat()},
    )

    return export_data, 200, {'Content-Type': f'text/{format}'}


# --- API Key Endpoints ---

@app.route('/api-keys', methods=['POST'])
@require_permission(Permission.API_KEY_CREATE)
@audit_log(AuditAction.API_KEY_CREATED, 'api_key')
def create_api_key():
    """Create API key."""
    data = request.get_json()

    plain_key, api_key = auth_manager.api_key_manager.generate_api_key(
        user_id=g.user_id,
        org_id=g.org_id,
        name=data['name'],
        scopes=data.get('scopes', []),
        expires_days=data.get('expires_days'),
    )

    return jsonify({
        'key': plain_key,  # Only returned once!
        'api_key': api_key.to_dict(),
    }), 201


@app.route('/api-keys', methods=['GET'])
@require_permission(Permission.API_KEY_VIEW)
def list_api_keys():
    """List user's API keys."""
    keys = auth_manager.api_key_manager.list_user_keys(g.user_id)
    return jsonify([k.to_dict() for k in keys])


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(400)
def bad_request(error):
    """Handle bad request."""
    return jsonify({'error': 'Bad request', 'message': str(error)}), 400


@app.errorhandler(401)
def unauthorized(error):
    """Handle unauthorized."""
    return jsonify({'error': 'Unauthorized', 'message': str(error)}), 401


@app.errorhandler(403)
def forbidden(error):
    """Handle forbidden."""
    return jsonify({'error': 'Forbidden', 'message': str(error)}), 403


@app.errorhandler(404)
def not_found(error):
    """Handle not found."""
    return jsonify({'error': 'Not found', 'message': str(error)}), 404


@app.errorhandler(429)
def rate_limited(error):
    """Handle rate limit."""
    return jsonify({'error': 'Rate limit exceeded', 'message': str(error)}), 429


@app.errorhandler(500)
def internal_error(error):
    """Handle internal error."""
    # Log error
    audit_logger.log(
        action=AuditAction.USER_UPDATED,  # Use generic action
        user_id=g.get('user_id'),
        org_id=g.get('org_id'),
        level='error',
        success=False,
        metadata={'error': str(error)},
    )

    return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("LOKI Enterprise API Server")
    print("=" * 50)
    print(f"Environment: {config.environment}")
    print(f"Database: {config.database.url}")
    print(f"Redis: {config.redis.url}")
    print("=" * 50)

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=config.debug,
    )
