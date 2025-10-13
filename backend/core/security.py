"""
Security utilities for LOKI Interceptor
- API key validation
- Request authentication
- Token management
"""
import hashlib
import secrets
import time
from functools import wraps
from flask import request, jsonify


class SecurityManager:
    """Manages authentication and API key validation"""

    def __init__(self):
        # In production, use environment variable or secure key management
        self.master_token = None  # Optional: Set for backend auth
        self.valid_tokens = set()  # Session tokens for authenticated clients

    def generate_session_token(self):
        """Generate a secure session token"""
        token = secrets.token_urlsafe(32)
        self.valid_tokens.add(token)
        return token

    def validate_session_token(self, token):
        """Validate a session token"""
        return token in self.valid_tokens

    def revoke_session_token(self, token):
        """Revoke a session token"""
        self.valid_tokens.discard(token)

    def validate_api_key_format(self, provider, api_key):
        """
        Basic API key format validation
        Does NOT verify with provider - just checks format
        """
        if not api_key or not isinstance(api_key, str):
            return False

        # Provider-specific format checks
        api_key = api_key.strip()

        if provider == 'anthropic':
            return api_key.startswith('sk-ant-') and len(api_key) >= 40
        elif provider == 'openai':
            return api_key.startswith('sk-') and len(api_key) >= 32 and '_' not in api_key
        elif provider == 'gemini':
            return api_key.startswith('AIza') and len(api_key) >= 39

        return False


class RateLimiter:
    """Simple in-memory rate limiter"""

    def __init__(self):
        self.requests = {}  # {client_id: [(timestamp, count)]}
        self.limits = {
            'default': (10000, 60),  # (requests, seconds) - 10k/min for automated testing
            '/validate-document': (10000, 60),  # 10k/min for validation endpoint
            '/proxy': (10000, 60),
            '/v1/messages': (10000, 60),
        }

    def is_allowed(self, client_id, endpoint='/default'):
        """Check if request is allowed under rate limit"""
        now = time.time()
        limit_key = endpoint if endpoint in self.limits else 'default'
        max_requests, window = self.limits[limit_key]

        if client_id not in self.requests:
            self.requests[client_id] = []

        # Clean old requests outside window
        self.requests[client_id] = [
            (ts, count) for ts, count in self.requests[client_id]
            if now - ts < window
        ]

        # Count requests in current window
        total = sum(count for _, count in self.requests[client_id])

        if total >= max_requests:
            return False

        # Add current request
        self.requests[client_id].append((now, 1))
        return True

    def get_client_id(self):
        """Extract client identifier from request"""
        # Use IP address as basic identifier
        return request.remote_addr or 'unknown'


def require_auth(security_manager):
    """Decorator to require authentication for endpoints"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check for session token or master token
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'error': 'Authentication required'}), 401

            # Strip 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]

            # Validate token
            if security_manager.master_token:
                if token != security_manager.master_token and not security_manager.validate_session_token(token):
                    return jsonify({'error': 'Invalid authentication token'}), 403
            elif not security_manager.validate_session_token(token):
                return jsonify({'error': 'Invalid session token'}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def rate_limit(rate_limiter):
    """Decorator to apply rate limiting to endpoints"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_id = rate_limiter.get_client_id()
            endpoint = request.path

            if not rate_limiter.is_allowed(client_id, endpoint):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': 'Too many requests. Please try again later.'
                }), 429

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def sanitize_error(error, include_detail=False):
    """
    Sanitize error messages to prevent information leakage

    Args:
        error: Exception or error message
        include_detail: If True, include sanitized detail (for development)

    Returns:
        dict: Safe error response
    """
    error_str = str(error)

    # Generic error categories
    if 'permission' in error_str.lower() or 'forbidden' in error_str.lower():
        category = 'permission_denied'
        message = 'Access forbidden'
    elif 'not found' in error_str.lower():
        category = 'not_found'
        message = 'Resource not found'
    elif 'timeout' in error_str.lower():
        category = 'timeout'
        message = 'Request timeout'
    elif 'validation' in error_str.lower() or 'invalid' in error_str.lower():
        category = 'validation_error'
        message = 'Invalid request'
    else:
        category = 'internal_error'
        message = 'An internal error occurred'

    response = {
        'error': category,
        'message': message
    }

    # Only include sanitized detail if explicitly requested (dev mode)
    if include_detail:
        # Strip sensitive paths and system info
        detail = error_str.replace('\\', '/').split('/')[-1] if '/' in error_str else error_str
        response['detail'] = detail[:100]  # Limit length

    return response
