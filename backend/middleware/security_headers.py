"""
Security Headers and CORS Middleware

Implements comprehensive security headers and CORS policies:
- Content Security Policy (CSP)
- X-Frame-Options (Clickjacking protection)
- X-Content-Type-Options (MIME sniffing protection)
- X-XSS-Protection
- Strict-Transport-Security (HSTS)
- Referrer-Policy
- Permissions-Policy
- CORS with whitelist
"""

from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from flask import Flask, request, Response, make_response
from functools import wraps
import re


class CORSMethod(Enum):
    """Allowed HTTP methods for CORS."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"


class CSPDirective(Enum):
    """Content Security Policy directives."""
    DEFAULT_SRC = "default-src"
    SCRIPT_SRC = "script-src"
    STYLE_SRC = "style-src"
    IMG_SRC = "img-src"
    FONT_SRC = "font-src"
    CONNECT_SRC = "connect-src"
    FRAME_SRC = "frame-src"
    OBJECT_SRC = "object-src"
    MEDIA_SRC = "media-src"
    WORKER_SRC = "worker-src"
    FORM_ACTION = "form-action"
    FRAME_ANCESTORS = "frame-ancestors"
    BASE_URI = "base-uri"


@dataclass
class CORSConfig:
    """
    CORS configuration.

    Attributes:
        enabled: Enable CORS
        allowed_origins: List of allowed origins (use ['*'] for all)
        allowed_methods: Allowed HTTP methods
        allowed_headers: Allowed request headers
        expose_headers: Headers to expose to client
        allow_credentials: Allow credentials (cookies, auth)
        max_age: Preflight cache duration in seconds
    """
    enabled: bool = True
    allowed_origins: List[str] = None
    allowed_methods: List[str] = None
    allowed_headers: List[str] = None
    expose_headers: List[str] = None
    allow_credentials: bool = False
    max_age: int = 3600

    def __post_init__(self):
        """Set defaults."""
        if self.allowed_origins is None:
            # Secure default: localhost only
            self.allowed_origins = [
                'http://localhost:3000',
                'http://localhost:5000',
                'http://127.0.0.1:3000',
                'http://127.0.0.1:5000',
            ]

        if self.allowed_methods is None:
            self.allowed_methods = [
                CORSMethod.GET.value,
                CORSMethod.POST.value,
                CORSMethod.OPTIONS.value,
            ]

        if self.allowed_headers is None:
            self.allowed_headers = [
                'Content-Type',
                'Authorization',
                'X-API-Key',
                'X-Requested-With',
            ]

        if self.expose_headers is None:
            self.expose_headers = [
                'X-RateLimit-Limit',
                'X-RateLimit-Remaining',
                'X-RateLimit-Reset',
            ]


@dataclass
class SecurityHeadersConfig:
    """
    Security headers configuration.

    Attributes:
        content_security_policy: CSP directives
        x_frame_options: Frame options (DENY, SAMEORIGIN)
        x_content_type_options: MIME type sniffing (nosniff)
        x_xss_protection: XSS filter (0, 1, 1; mode=block)
        strict_transport_security: HSTS configuration
        referrer_policy: Referrer policy
        permissions_policy: Permissions policy (formerly Feature-Policy)
        remove_server_header: Remove Server header
    """
    content_security_policy: Dict[str, List[str]] = None
    x_frame_options: str = "DENY"
    x_content_type_options: str = "nosniff"
    x_xss_protection: str = "1; mode=block"
    strict_transport_security: str = "max-age=31536000; includeSubDomains; preload"
    referrer_policy: str = "strict-origin-when-cross-origin"
    permissions_policy: str = "geolocation=(), microphone=(), camera=(), payment=()"
    remove_server_header: bool = True

    def __post_init__(self):
        """Set default CSP."""
        if self.content_security_policy is None:
            self.content_security_policy = {
                CSPDirective.DEFAULT_SRC.value: ["'self'"],
                CSPDirective.SCRIPT_SRC.value: ["'self'", "'unsafe-inline'"],  # For inline scripts
                CSPDirective.STYLE_SRC.value: ["'self'", "'unsafe-inline'"],  # For inline styles
                CSPDirective.IMG_SRC.value: ["'self'", "data:", "https:"],
                CSPDirective.FONT_SRC.value: ["'self'", "data:"],
                CSPDirective.CONNECT_SRC.value: ["'self'"],
                CSPDirective.FRAME_ANCESTORS.value: ["'none'"],
                CSPDirective.FORM_ACTION.value: ["'self'"],
                CSPDirective.BASE_URI.value: ["'self'"],
                CSPDirective.OBJECT_SRC.value: ["'none'"],
            }

    def get_csp_header(self) -> str:
        """
        Build CSP header string.

        Returns:
            CSP header value
        """
        directives = []
        for directive, values in self.content_security_policy.items():
            directive_str = f"{directive} {' '.join(values)}"
            directives.append(directive_str)

        return "; ".join(directives)


class SecurityHeadersMiddleware:
    """
    Flask middleware for security headers and CORS.

    Usage:
        app = Flask(__name__)
        security = SecurityHeadersMiddleware(app)

    Or:
        security = SecurityHeadersMiddleware()
        security.init_app(app)
    """

    def __init__(
        self,
        app: Optional[Flask] = None,
        cors_config: Optional[CORSConfig] = None,
        headers_config: Optional[SecurityHeadersConfig] = None,
    ):
        """
        Initialize security middleware.

        Args:
            app: Flask application
            cors_config: CORS configuration
            headers_config: Security headers configuration
        """
        self.cors_config = cors_config or CORSConfig()
        self.headers_config = headers_config or SecurityHeadersConfig()

        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        """
        Initialize middleware with Flask app.

        Args:
            app: Flask application
        """
        # Register before_request handler
        app.before_request(self._before_request)

        # Register after_request handler
        app.after_request(self._after_request)

    def _before_request(self):
        """Handle preflight requests."""
        if request.method == 'OPTIONS':
            return self._handle_preflight()

    def _after_request(self, response: Response) -> Response:
        """
        Add security headers to response.

        Args:
            response: Flask response object

        Returns:
            Modified response with security headers
        """
        # Add CORS headers
        if self.cors_config.enabled:
            response = self._add_cors_headers(response)

        # Add security headers
        response = self._add_security_headers(response)

        return response

    def _handle_preflight(self) -> Response:
        """
        Handle CORS preflight OPTIONS request.

        Returns:
            Preflight response
        """
        response = make_response('', 204)

        if self.cors_config.enabled:
            response = self._add_cors_headers(response)

        return response

    def _add_cors_headers(self, response: Response) -> Response:
        """
        Add CORS headers to response.

        Args:
            response: Flask response

        Returns:
            Response with CORS headers
        """
        origin = request.headers.get('Origin')

        # Check if origin is allowed
        if origin and self._is_origin_allowed(origin):
            response.headers['Access-Control-Allow-Origin'] = origin
        elif '*' in self.cors_config.allowed_origins:
            response.headers['Access-Control-Allow-Origin'] = '*'

        # Add other CORS headers
        if self.cors_config.allow_credentials:
            response.headers['Access-Control-Allow-Credentials'] = 'true'

        response.headers['Access-Control-Allow-Methods'] = ', '.join(
            self.cors_config.allowed_methods
        )

        response.headers['Access-Control-Allow-Headers'] = ', '.join(
            self.cors_config.allowed_headers
        )

        if self.cors_config.expose_headers:
            response.headers['Access-Control-Expose-Headers'] = ', '.join(
                self.cors_config.expose_headers
            )

        response.headers['Access-Control-Max-Age'] = str(self.cors_config.max_age)

        return response

    def _is_origin_allowed(self, origin: str) -> bool:
        """
        Check if origin is allowed.

        Args:
            origin: Request origin

        Returns:
            True if allowed
        """
        # Allow exact matches
        if origin in self.cors_config.allowed_origins:
            return True

        # Allow wildcard patterns
        for allowed in self.cors_config.allowed_origins:
            if '*' in allowed:
                # Convert to regex pattern
                pattern = allowed.replace('.', r'\\.').replace('*', '.*')
                if re.match(f'^{pattern}$', origin):
                    return True

        return False

    def _add_security_headers(self, response: Response) -> Response:
        """
        Add security headers to response.

        Args:
            response: Flask response

        Returns:
            Response with security headers
        """
        config = self.headers_config

        # Content Security Policy
        if config.content_security_policy:
            response.headers['Content-Security-Policy'] = config.get_csp_header()

        # X-Frame-Options (Clickjacking protection)
        response.headers['X-Frame-Options'] = config.x_frame_options

        # X-Content-Type-Options (MIME sniffing protection)
        response.headers['X-Content-Type-Options'] = config.x_content_type_options

        # X-XSS-Protection
        response.headers['X-XSS-Protection'] = config.x_xss_protection

        # Strict-Transport-Security (HSTS)
        # Only add if using HTTPS
        if request.is_secure or request.headers.get('X-Forwarded-Proto') == 'https':
            response.headers['Strict-Transport-Security'] = config.strict_transport_security

        # Referrer-Policy
        response.headers['Referrer-Policy'] = config.referrer_policy

        # Permissions-Policy
        if config.permissions_policy:
            response.headers['Permissions-Policy'] = config.permissions_policy

        # Remove Server header
        if config.remove_server_header and 'Server' in response.headers:
            del response.headers['Server']

        # Add X-Content-Type-Options
        response.headers['X-Content-Type-Options'] = 'nosniff'

        return response


def setup_security_middleware(
    app: Flask,
    allowed_origins: Optional[List[str]] = None,
    strict_mode: bool = True,
) -> SecurityHeadersMiddleware:
    """
    Setup security middleware with sensible defaults.

    Args:
        app: Flask application
        allowed_origins: Custom allowed origins
        strict_mode: Use strict security settings

    Returns:
        Configured SecurityHeadersMiddleware instance
    """
    # Configure CORS
    cors_config = CORSConfig(
        enabled=True,
        allowed_origins=allowed_origins,
        allow_credentials=False,
    )

    # Configure security headers
    if strict_mode:
        # Strict CSP
        headers_config = SecurityHeadersConfig(
            content_security_policy={
                CSPDirective.DEFAULT_SRC.value: ["'self'"],
                CSPDirective.SCRIPT_SRC.value: ["'self'"],
                CSPDirective.STYLE_SRC.value: ["'self'"],
                CSPDirective.IMG_SRC.value: ["'self'", "data:"],
                CSPDirective.FONT_SRC.value: ["'self'"],
                CSPDirective.CONNECT_SRC.value: ["'self'"],
                CSPDirective.FRAME_ANCESTORS.value: ["'none'"],
                CSPDirective.FORM_ACTION.value: ["'self'"],
                CSPDirective.BASE_URI.value: ["'self'"],
                CSPDirective.OBJECT_SRC.value: ["'none'"],
            },
            x_frame_options="DENY",
        )
    else:
        # Permissive CSP (for development)
        headers_config = SecurityHeadersConfig()

    # Create and initialize middleware
    middleware = SecurityHeadersMiddleware(
        app=app,
        cors_config=cors_config,
        headers_config=headers_config,
    )

    return middleware


def cors_decorator(
    allowed_origins: Optional[List[str]] = None,
    allowed_methods: Optional[List[str]] = None,
):
    """
    Decorator to add CORS headers to specific routes.

    Usage:
        @app.route('/api/endpoint')
        @cors_decorator(allowed_origins=['https://example.com'])
        def my_endpoint():
            return jsonify({'status': 'ok'})

    Args:
        allowed_origins: Allowed origins for this route
        allowed_methods: Allowed methods for this route
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Call original function
            response = make_response(f(*args, **kwargs))

            # Add CORS headers
            origin = request.headers.get('Origin')

            if allowed_origins and origin in allowed_origins:
                response.headers['Access-Control-Allow-Origin'] = origin
            elif not allowed_origins:
                response.headers['Access-Control-Allow-Origin'] = '*'

            if allowed_methods:
                response.headers['Access-Control-Allow-Methods'] = ', '.join(allowed_methods)

            return response

        return decorated_function

    return decorator


def check_security_headers(response: Response) -> Dict[str, Any]:
    """
    Check if response has proper security headers.

    Args:
        response: Flask response object

    Returns:
        Dictionary with header presence and recommendations
    """
    required_headers = [
        'Content-Security-Policy',
        'X-Frame-Options',
        'X-Content-Type-Options',
        'X-XSS-Protection',
        'Referrer-Policy',
    ]

    optional_headers = [
        'Strict-Transport-Security',
        'Permissions-Policy',
    ]

    result = {
        'has_all_required': True,
        'missing_headers': [],
        'present_headers': [],
        'recommendations': [],
    }

    for header in required_headers:
        if header in response.headers:
            result['present_headers'].append(header)
        else:
            result['has_all_required'] = False
            result['missing_headers'].append(header)

    for header in optional_headers:
        if header in response.headers:
            result['present_headers'].append(header)
        else:
            result['recommendations'].append(f"Consider adding {header}")

    # Check CSP quality
    if 'Content-Security-Policy' in response.headers:
        csp = response.headers['Content-Security-Policy']
        if "'unsafe-inline'" in csp or "'unsafe-eval'" in csp:
            result['recommendations'].append(
                "CSP contains unsafe-inline or unsafe-eval. Consider using nonces or hashes."
            )

    return result
