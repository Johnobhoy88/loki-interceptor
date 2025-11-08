"""
Security Hardening System for LOKI Enterprise

Production-grade security features including request signing, CSRF protection,
distributed rate limiting, and input validation middleware.

Features:
- HMAC-SHA256 request signing
- CSRF token generation & validation
- Distributed rate limiting (Redis-backed)
- Input validation & sanitization
- Security headers middleware
- IP whitelisting/blacklisting
"""

import hmac
import hashlib
import secrets
import time
import re
from typing import Optional, Dict, Any, List, Callable, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json


class RateLimitStrategy(Enum):
    """Rate limiting strategies."""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"


@dataclass
class RateLimitConfig:
    """
    Rate limit configuration.

    Attributes:
        requests: Maximum requests allowed
        window_seconds: Time window in seconds
        strategy: Rate limiting strategy
        burst_size: Burst allowance for token bucket
    """
    requests: int
    window_seconds: int
    strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW
    burst_size: Optional[int] = None

    def __post_init__(self):
        """Set defaults."""
        if self.burst_size is None:
            self.burst_size = self.requests * 2


@dataclass
class SecurityHeaders:
    """Security headers configuration."""
    x_content_type_options: str = "nosniff"
    x_frame_options: str = "DENY"
    x_xss_protection: str = "1; mode=block"
    strict_transport_security: str = "max-age=31536000; includeSubDomains"
    content_security_policy: str = "default-src 'self'"
    referrer_policy: str = "strict-origin-when-cross-origin"
    permissions_policy: str = "geolocation=(), microphone=(), camera=()"

    def to_dict(self) -> Dict[str, str]:
        """Convert to header dictionary."""
        return {
            'X-Content-Type-Options': self.x_content_type_options,
            'X-Frame-Options': self.x_frame_options,
            'X-XSS-Protection': self.x_xss_protection,
            'Strict-Transport-Security': self.strict_transport_security,
            'Content-Security-Policy': self.content_security_policy,
            'Referrer-Policy': self.referrer_policy,
            'Permissions-Policy': self.permissions_policy,
        }


class RequestSigner:
    """
    HMAC-SHA256 request signing for API security.

    Provides request signature generation and verification to ensure
    request integrity and authenticity.
    """

    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize request signer.

        Args:
            secret_key: Secret key for signing (generated if not provided)
        """
        self.secret_key = secret_key or self._generate_secret()

    def sign_request(
        self,
        method: str,
        path: str,
        body: Optional[str] = None,
        timestamp: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Generate HMAC signature for request.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            body: Request body (JSON string)
            timestamp: Unix timestamp (current time if not provided)
            headers: Additional headers to include in signature

        Returns:
            HMAC-SHA256 signature (hex)
        """
        if timestamp is None:
            timestamp = int(time.time())

        # Build canonical string
        parts = [
            method.upper(),
            path,
            str(timestamp),
        ]

        if body:
            body_hash = hashlib.sha256(body.encode()).hexdigest()
            parts.append(body_hash)

        if headers:
            # Sort headers for consistent signature
            sorted_headers = sorted(headers.items())
            for key, value in sorted_headers:
                parts.append(f"{key}:{value}")

        canonical_string = "\n".join(parts)

        # Generate HMAC signature
        signature = hmac.new(
            self.secret_key.encode(),
            canonical_string.encode(),
            hashlib.sha256,
        ).hexdigest()

        return signature

    def verify_request(
        self,
        signature: str,
        method: str,
        path: str,
        body: Optional[str] = None,
        timestamp: int = None,
        headers: Optional[Dict[str, str]] = None,
        max_age_seconds: int = 300,
    ) -> bool:
        """
        Verify request signature.

        Args:
            signature: Provided signature
            method: HTTP method
            path: Request path
            body: Request body
            timestamp: Request timestamp
            headers: Request headers
            max_age_seconds: Maximum age of request (prevents replay attacks)

        Returns:
            True if signature is valid and not expired
        """
        # Check timestamp age
        if timestamp:
            current_time = int(time.time())
            age = current_time - timestamp

            if age > max_age_seconds or age < 0:
                return False

        # Generate expected signature
        expected = self.sign_request(method, path, body, timestamp, headers)

        # Constant-time comparison
        return hmac.compare_digest(signature, expected)

    def generate_signed_url(
        self,
        path: str,
        expires_in_seconds: int = 3600,
        params: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Generate signed URL with expiration.

        Args:
            path: URL path
            expires_in_seconds: URL validity period
            params: Query parameters

        Returns:
            Signed URL with signature and expiration
        """
        expires = int(time.time()) + expires_in_seconds

        # Build query string
        query_parts = [f"expires={expires}"]

        if params:
            for key, value in sorted(params.items()):
                query_parts.append(f"{key}={value}")

        query_string = "&".join(query_parts)

        # Sign URL
        signature = self.sign_request("GET", path, timestamp=expires)

        return f"{path}?{query_string}&signature={signature}"

    @staticmethod
    def _generate_secret() -> str:
        """Generate cryptographically secure secret key."""
        return secrets.token_hex(32)


class CSRFProtection:
    """
    Cross-Site Request Forgery (CSRF) protection.

    Generates and validates CSRF tokens for state-changing operations.
    """

    TOKEN_LENGTH = 32

    def __init__(self, cache_backend=None, token_expiry_seconds: int = 3600):
        """
        Initialize CSRF protection.

        Args:
            cache_backend: Redis cache for token storage
            token_expiry_seconds: Token validity period
        """
        self.cache = cache_backend
        self.token_expiry = token_expiry_seconds
        self._tokens: Dict[str, datetime] = {}

    def generate_token(self, session_id: str) -> str:
        """
        Generate CSRF token for session.

        Args:
            session_id: User session identifier

        Returns:
            CSRF token
        """
        token = secrets.token_urlsafe(self.TOKEN_LENGTH)

        # Store token with expiration
        expires_at = datetime.utcnow() + timedelta(seconds=self.token_expiry)

        if self.cache:
            # Store in Redis
            key = f"csrf:{session_id}:{token}"
            self.cache.setex(key, self.token_expiry, "1")
        else:
            # Store in memory
            self._tokens[f"{session_id}:{token}"] = expires_at

        return token

    def validate_token(
        self,
        session_id: str,
        token: str,
        consume: bool = True,
    ) -> bool:
        """
        Validate CSRF token.

        Args:
            session_id: User session identifier
            token: CSRF token to validate
            consume: Whether to consume (delete) token after validation

        Returns:
            True if token is valid
        """
        key = f"{session_id}:{token}"

        if self.cache:
            # Check Redis
            redis_key = f"csrf:{key}"
            valid = self.cache.get(redis_key) is not None

            if valid and consume:
                self.cache.delete(redis_key)

            return valid
        else:
            # Check memory
            if key in self._tokens:
                expires_at = self._tokens[key]

                if datetime.utcnow() <= expires_at:
                    if consume:
                        del self._tokens[key]
                    return True
                else:
                    # Token expired
                    del self._tokens[key]

        return False

    def cleanup_expired_tokens(self) -> int:
        """
        Remove expired tokens from memory storage.

        Returns:
            Number of tokens removed
        """
        if self.cache:
            # Redis handles expiration automatically
            return 0

        now = datetime.utcnow()
        expired_keys = [
            key for key, expires_at in self._tokens.items()
            if now > expires_at
        ]

        for key in expired_keys:
            del self._tokens[key]

        return len(expired_keys)


class RateLimiter:
    """
    Distributed rate limiter with Redis backend.

    Supports multiple strategies: fixed window, sliding window, token bucket.
    """

    def __init__(self, cache_backend=None):
        """
        Initialize rate limiter.

        Args:
            cache_backend: Redis cache backend (required for distributed limiting)
        """
        self.cache = cache_backend
        self._local_store: Dict[str, List[float]] = {}

    def check_rate_limit(
        self,
        identifier: str,
        config: RateLimitConfig,
    ) -> Dict[str, Any]:
        """
        Check if request should be rate limited.

        Args:
            identifier: Unique identifier (user ID, IP, API key, etc.)
            config: Rate limit configuration

        Returns:
            Dictionary with:
                - allowed: Whether request is allowed
                - remaining: Remaining requests in window
                - reset_at: When limit resets (timestamp)
                - retry_after: Seconds until next allowed request
        """
        if config.strategy == RateLimitStrategy.SLIDING_WINDOW:
            return self._sliding_window(identifier, config)
        elif config.strategy == RateLimitStrategy.FIXED_WINDOW:
            return self._fixed_window(identifier, config)
        elif config.strategy == RateLimitStrategy.TOKEN_BUCKET:
            return self._token_bucket(identifier, config)
        else:
            raise ValueError(f"Unknown rate limit strategy: {config.strategy}")

    def _sliding_window(
        self,
        identifier: str,
        config: RateLimitConfig,
    ) -> Dict[str, Any]:
        """
        Sliding window rate limiting.

        More accurate than fixed window, prevents burst at window boundaries.
        """
        now = time.time()
        window_start = now - config.window_seconds

        if self.cache:
            # Redis-backed implementation
            key = f"ratelimit:sw:{identifier}"

            # Remove old entries
            self.cache.zremrangebyscore(key, 0, window_start)

            # Count requests in window
            count = self.cache.zcard(key)

            if count < config.requests:
                # Add current request
                self.cache.zadd(key, {str(now): now})
                self.cache.expire(key, config.window_seconds)

                remaining = config.requests - count - 1
                return {
                    'allowed': True,
                    'remaining': remaining,
                    'reset_at': int(now + config.window_seconds),
                    'retry_after': 0,
                }
            else:
                # Rate limited
                oldest = self.cache.zrange(key, 0, 0, withscores=True)
                if oldest:
                    reset_at = oldest[0][1] + config.window_seconds
                    retry_after = max(0, int(reset_at - now))
                else:
                    reset_at = int(now + config.window_seconds)
                    retry_after = config.window_seconds

                return {
                    'allowed': False,
                    'remaining': 0,
                    'reset_at': int(reset_at),
                    'retry_after': retry_after,
                }
        else:
            # Local memory implementation
            if identifier not in self._local_store:
                self._local_store[identifier] = []

            # Remove old timestamps
            self._local_store[identifier] = [
                ts for ts in self._local_store[identifier]
                if ts > window_start
            ]

            count = len(self._local_store[identifier])

            if count < config.requests:
                self._local_store[identifier].append(now)

                return {
                    'allowed': True,
                    'remaining': config.requests - count - 1,
                    'reset_at': int(now + config.window_seconds),
                    'retry_after': 0,
                }
            else:
                oldest = min(self._local_store[identifier])
                reset_at = oldest + config.window_seconds
                retry_after = max(0, int(reset_at - now))

                return {
                    'allowed': False,
                    'remaining': 0,
                    'reset_at': int(reset_at),
                    'retry_after': retry_after,
                }

    def _fixed_window(
        self,
        identifier: str,
        config: RateLimitConfig,
    ) -> Dict[str, Any]:
        """
        Fixed window rate limiting.

        Simpler but allows bursts at window boundaries.
        """
        now = time.time()
        window_key = int(now / config.window_seconds)

        if self.cache:
            key = f"ratelimit:fw:{identifier}:{window_key}"

            count = self.cache.get(key)
            count = int(count) if count else 0

            if count < config.requests:
                # Increment counter
                pipe = self.cache.pipeline()
                pipe.incr(key)
                pipe.expire(key, config.window_seconds)
                pipe.execute()

                return {
                    'allowed': True,
                    'remaining': config.requests - count - 1,
                    'reset_at': (window_key + 1) * config.window_seconds,
                    'retry_after': 0,
                }
            else:
                reset_at = (window_key + 1) * config.window_seconds
                retry_after = max(0, int(reset_at - now))

                return {
                    'allowed': False,
                    'remaining': 0,
                    'reset_at': int(reset_at),
                    'retry_after': retry_after,
                }
        else:
            # Local implementation
            key = f"{identifier}:{window_key}"

            if key not in self._local_store:
                self._local_store[key] = []

            count = len(self._local_store[key])

            if count < config.requests:
                self._local_store[key].append(now)

                return {
                    'allowed': True,
                    'remaining': config.requests - count - 1,
                    'reset_at': (window_key + 1) * config.window_seconds,
                    'retry_after': 0,
                }
            else:
                reset_at = (window_key + 1) * config.window_seconds
                retry_after = max(0, int(reset_at - now))

                return {
                    'allowed': False,
                    'remaining': 0,
                    'reset_at': int(reset_at),
                    'retry_after': retry_after,
                }

    def _token_bucket(
        self,
        identifier: str,
        config: RateLimitConfig,
    ) -> Dict[str, Any]:
        """
        Token bucket rate limiting.

        Allows controlled bursts while maintaining average rate.
        """
        now = time.time()

        if self.cache:
            key = f"ratelimit:tb:{identifier}"

            # Get current bucket state
            data = self.cache.get(key)

            if data:
                state = json.loads(data)
                tokens = state['tokens']
                last_update = state['last_update']
            else:
                tokens = config.burst_size
                last_update = now

            # Add tokens based on time elapsed
            elapsed = now - last_update
            tokens_to_add = elapsed * (config.requests / config.window_seconds)
            tokens = min(config.burst_size, tokens + tokens_to_add)

            if tokens >= 1:
                # Consume token
                tokens -= 1

                new_state = {
                    'tokens': tokens,
                    'last_update': now,
                }

                self.cache.setex(key, config.window_seconds * 2, json.dumps(new_state))

                return {
                    'allowed': True,
                    'remaining': int(tokens),
                    'reset_at': int(now + config.window_seconds),
                    'retry_after': 0,
                }
            else:
                # Not enough tokens
                retry_after = int((1 - tokens) / (config.requests / config.window_seconds))

                return {
                    'allowed': False,
                    'remaining': 0,
                    'reset_at': int(now + retry_after),
                    'retry_after': retry_after,
                }
        else:
            # Local implementation
            if identifier not in self._local_store:
                self._local_store[identifier] = [config.burst_size, now]

            tokens, last_update = self._local_store[identifier]

            elapsed = now - last_update
            tokens_to_add = elapsed * (config.requests / config.window_seconds)
            tokens = min(config.burst_size, tokens + tokens_to_add)

            if tokens >= 1:
                tokens -= 1
                self._local_store[identifier] = [tokens, now]

                return {
                    'allowed': True,
                    'remaining': int(tokens),
                    'reset_at': int(now + config.window_seconds),
                    'retry_after': 0,
                }
            else:
                retry_after = int((1 - tokens) / (config.requests / config.window_seconds))

                return {
                    'allowed': False,
                    'remaining': 0,
                    'reset_at': int(now + retry_after),
                    'retry_after': retry_after,
                }


class InputValidator:
    """
    Input validation and sanitization.

    Protects against injection attacks, XSS, and malformed input.
    """

    # Common regex patterns
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
    SLUG_PATTERN = re.compile(r'^[a-z0-9-]+$')
    ALPHANUMERIC_PATTERN = re.compile(r'^[a-zA-Z0-9]+$')

    # Dangerous characters for SQL/NoSQL injection
    SQL_DANGEROUS_CHARS = {"'", '"', ';', '--', '/*', '*/', 'xp_', 'sp_', 'EXEC', 'EXECUTE'}

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        if not email or len(email) > 255:
            return False
        return bool(InputValidator.EMAIL_PATTERN.match(email))

    @staticmethod
    def validate_uuid(uuid_str: str) -> bool:
        """Validate UUID format."""
        if not uuid_str:
            return False
        return bool(InputValidator.UUID_PATTERN.match(uuid_str))

    @staticmethod
    def validate_slug(slug: str) -> bool:
        """Validate slug format."""
        if not slug or len(slug) > 100:
            return False
        return bool(InputValidator.SLUG_PATTERN.match(slug))

    @staticmethod
    def sanitize_string(
        text: str,
        max_length: int = 1000,
        allow_html: bool = False,
    ) -> str:
        """
        Sanitize string input.

        Args:
            text: Input text
            max_length: Maximum allowed length
            allow_html: Whether to allow HTML tags

        Returns:
            Sanitized string
        """
        if not text:
            return ""

        # Truncate
        text = text[:max_length]

        # Strip dangerous SQL patterns
        for pattern in InputValidator.SQL_DANGEROUS_CHARS:
            if pattern.upper() in text.upper():
                text = text.replace(pattern, '')

        # Remove HTML if not allowed
        if not allow_html:
            text = re.sub(r'<[^>]+>', '', text)

        return text.strip()

    @staticmethod
    def validate_json(data: Any, schema: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate JSON against schema.

        Args:
            data: JSON data to validate
            schema: Schema definition

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Basic type checking
        if 'type' in schema:
            expected_type = schema['type']

            type_map = {
                'string': str,
                'number': (int, float),
                'integer': int,
                'boolean': bool,
                'array': list,
                'object': dict,
            }

            if expected_type in type_map:
                if not isinstance(data, type_map[expected_type]):
                    return False, f"Expected type {expected_type}"

        # Required fields
        if isinstance(data, dict) and 'required' in schema:
            for field in schema['required']:
                if field not in data:
                    return False, f"Missing required field: {field}"

        return True, None


class IPFilter:
    """
    IP address whitelist/blacklist filtering.
    """

    def __init__(self):
        """Initialize IP filter."""
        self.whitelist: Set[str] = set()
        self.blacklist: Set[str] = set()

    def add_to_whitelist(self, ip: str) -> None:
        """Add IP to whitelist."""
        self.whitelist.add(ip)

    def add_to_blacklist(self, ip: str) -> None:
        """Add IP to blacklist."""
        self.blacklist.add(ip)

    def is_allowed(self, ip: str) -> bool:
        """
        Check if IP is allowed.

        Args:
            ip: IP address

        Returns:
            True if allowed
        """
        # Blacklist takes precedence
        if ip in self.blacklist:
            return False

        # If whitelist is empty, allow all (except blacklisted)
        if not self.whitelist:
            return True

        # Check whitelist
        return ip in self.whitelist


class SecurityManager:
    """
    Central security manager coordinating all security features.
    """

    def __init__(
        self,
        cache_backend=None,
        secret_key: Optional[str] = None,
    ):
        """
        Initialize security manager.

        Args:
            cache_backend: Redis cache backend
            secret_key: Secret key for signing
        """
        self.cache = cache_backend

        self.request_signer = RequestSigner(secret_key)
        self.csrf_protection = CSRFProtection(cache_backend)
        self.rate_limiter = RateLimiter(cache_backend)
        self.input_validator = InputValidator()
        self.ip_filter = IPFilter()
        self.security_headers = SecurityHeaders()

    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers for HTTP responses."""
        return self.security_headers.to_dict()

    def create_rate_limit_config(
        self,
        tier: str = "free",
    ) -> RateLimitConfig:
        """
        Create rate limit config based on subscription tier.

        Args:
            tier: Subscription tier

        Returns:
            RateLimitConfig instance
        """
        configs = {
            'free': RateLimitConfig(requests=100, window_seconds=3600),
            'starter': RateLimitConfig(requests=1000, window_seconds=3600),
            'professional': RateLimitConfig(requests=10000, window_seconds=3600),
            'enterprise': RateLimitConfig(requests=100000, window_seconds=3600),
        }

        return configs.get(tier, configs['free'])


# Example middleware usage
def example_flask_middleware():
    """
    Example Flask middleware integration.

    This is a reference implementation showing how to integrate
    the security components into a Flask application.
    """
    return """
    from flask import Flask, request, abort, g
    from backend.enterprise.security import SecurityManager

    app = Flask(__name__)
    security_manager = SecurityManager(cache_backend=redis_client)

    @app.before_request
    def security_middleware():
        # Add security headers
        g.security_headers = security_manager.get_security_headers()

        # Check IP filter
        if not security_manager.ip_filter.is_allowed(request.remote_addr):
            abort(403, "IP address blocked")

        # Rate limiting
        rate_config = security_manager.create_rate_limit_config(tier=g.user.tier)
        rate_result = security_manager.rate_limiter.check_rate_limit(
            identifier=g.user.id,
            config=rate_config,
        )

        if not rate_result['allowed']:
            abort(429, "Rate limit exceeded")

        # CSRF validation for state-changing methods
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            csrf_token = request.headers.get('X-CSRF-Token')
            if not security_manager.csrf_protection.validate_token(
                session_id=g.session.id,
                token=csrf_token,
            ):
                abort(403, "Invalid CSRF token")

    @app.after_request
    def add_security_headers(response):
        for header, value in g.get('security_headers', {}).items():
            response.headers[header] = value
        return response
    """
