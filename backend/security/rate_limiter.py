"""
Distributed Rate Limiting System

Enterprise-grade rate limiting with:
- Multiple strategies (sliding window, token bucket, fixed window)
- Redis-backed distributed limiting
- Per-user, per-IP, per-API-key limits
- Burst protection
- DDoS mitigation
- Adaptive rate limiting
"""

import time
import hashlib
import json
from typing import Optional, Dict, Any, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from functools import wraps
from flask import request, jsonify, g


class RateLimitStrategy(Enum):
    """Rate limiting strategies."""
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    FIXED_WINDOW = "fixed_window"
    ADAPTIVE = "adaptive"


class RateLimitScope(Enum):
    """Scope for rate limiting."""
    GLOBAL = "global"
    PER_IP = "per_ip"
    PER_USER = "per_user"
    PER_API_KEY = "per_api_key"
    PER_ENDPOINT = "per_endpoint"


@dataclass
class RateLimitConfig:
    """
    Rate limit configuration.

    Attributes:
        requests: Maximum requests allowed
        window_seconds: Time window in seconds
        strategy: Rate limiting strategy
        scope: Limiting scope
        burst_multiplier: Burst allowance multiplier
        block_duration: How long to block after limit exceeded (seconds)
    """
    requests: int
    window_seconds: int
    strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW
    scope: RateLimitScope = RateLimitScope.PER_IP
    burst_multiplier: float = 1.5
    block_duration: int = 60

    @property
    def burst_size(self) -> int:
        """Calculate burst size."""
        return int(self.requests * self.burst_multiplier)


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, message: str, retry_after: int):
        """
        Initialize exception.

        Args:
            message: Error message
            retry_after: Seconds until retry is allowed
        """
        super().__init__(message)
        self.retry_after = retry_after


@dataclass
class RateLimitResult:
    """Result of rate limit check."""
    allowed: bool
    remaining: int
    reset_at: int
    retry_after: int
    limit: int


class DistributedRateLimiter:
    """
    Distributed rate limiter with Redis backend.

    Supports multiple strategies and scopes for flexible rate limiting.
    """

    def __init__(self, redis_client=None):
        """
        Initialize rate limiter.

        Args:
            redis_client: Redis client for distributed limiting
        """
        self.redis = redis_client
        self._local_store: Dict[str, Any] = {}
        self._blocked_ips: Dict[str, int] = {}  # IP -> unblock_timestamp

    def check_rate_limit(
        self,
        identifier: str,
        config: RateLimitConfig,
    ) -> RateLimitResult:
        """
        Check if request should be rate limited.

        Args:
            identifier: Unique identifier (IP, user ID, API key, etc.)
            config: Rate limit configuration

        Returns:
            RateLimitResult with limit status

        Raises:
            RateLimitExceeded: If rate limit is exceeded
        """
        # Check if identifier is blocked
        if self._is_blocked(identifier):
            unblock_time = self._blocked_ips.get(identifier, 0)
            retry_after = max(0, int(unblock_time - time.time()))
            raise RateLimitExceeded(
                f"Rate limit exceeded. Temporarily blocked.",
                retry_after=retry_after
            )

        # Execute strategy
        if config.strategy == RateLimitStrategy.SLIDING_WINDOW:
            result = self._sliding_window(identifier, config)
        elif config.strategy == RateLimitStrategy.TOKEN_BUCKET:
            result = self._token_bucket(identifier, config)
        elif config.strategy == RateLimitStrategy.FIXED_WINDOW:
            result = self._fixed_window(identifier, config)
        elif config.strategy == RateLimitStrategy.ADAPTIVE:
            result = self._adaptive(identifier, config)
        else:
            raise ValueError(f"Unknown strategy: {config.strategy}")

        # Block if limit exceeded
        if not result.allowed and config.block_duration > 0:
            self._block_identifier(identifier, config.block_duration)

        return result

    def _sliding_window(
        self,
        identifier: str,
        config: RateLimitConfig,
    ) -> RateLimitResult:
        """
        Sliding window rate limiting.

        Most accurate, prevents burst at window boundaries.
        """
        now = time.time()
        window_start = now - config.window_seconds
        key = f"ratelimit:sw:{identifier}"

        if self.redis:
            # Redis implementation
            pipe = self.redis.pipeline()

            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)

            # Count requests in window
            pipe.zcard(key)

            # Execute
            _, count = pipe.execute()

            if count < config.requests:
                # Add current request
                self.redis.zadd(key, {str(now): now})
                self.redis.expire(key, config.window_seconds)

                remaining = config.requests - count - 1
                return RateLimitResult(
                    allowed=True,
                    remaining=remaining,
                    reset_at=int(now + config.window_seconds),
                    retry_after=0,
                    limit=config.requests
                )
            else:
                # Rate limited
                oldest_entries = self.redis.zrange(key, 0, 0, withscores=True)
                if oldest_entries:
                    oldest_score = oldest_entries[0][1]
                    reset_at = oldest_score + config.window_seconds
                    retry_after = max(0, int(reset_at - now))
                else:
                    reset_at = int(now + config.window_seconds)
                    retry_after = config.window_seconds

                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_at=int(reset_at),
                    retry_after=retry_after,
                    limit=config.requests
                )
        else:
            # Local memory implementation
            if key not in self._local_store:
                self._local_store[key] = []

            # Remove old timestamps
            self._local_store[key] = [
                ts for ts in self._local_store[key]
                if ts > window_start
            ]

            count = len(self._local_store[key])

            if count < config.requests:
                self._local_store[key].append(now)

                return RateLimitResult(
                    allowed=True,
                    remaining=config.requests - count - 1,
                    reset_at=int(now + config.window_seconds),
                    retry_after=0,
                    limit=config.requests
                )
            else:
                oldest = min(self._local_store[key])
                reset_at = oldest + config.window_seconds
                retry_after = max(0, int(reset_at - now))

                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_at=int(reset_at),
                    retry_after=retry_after,
                    limit=config.requests
                )

    def _token_bucket(
        self,
        identifier: str,
        config: RateLimitConfig,
    ) -> RateLimitResult:
        """
        Token bucket rate limiting.

        Allows controlled bursts while maintaining average rate.
        """
        now = time.time()
        key = f"ratelimit:tb:{identifier}"

        if self.redis:
            # Get current bucket state
            data = self.redis.get(key)

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

                self.redis.setex(key, config.window_seconds * 2, json.dumps(new_state))

                return RateLimitResult(
                    allowed=True,
                    remaining=int(tokens),
                    reset_at=int(now + config.window_seconds),
                    retry_after=0,
                    limit=config.requests
                )
            else:
                # Not enough tokens
                retry_after = int((1 - tokens) / (config.requests / config.window_seconds))

                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_at=int(now + retry_after),
                    retry_after=retry_after,
                    limit=config.requests
                )
        else:
            # Local implementation
            if key not in self._local_store:
                self._local_store[key] = {
                    'tokens': config.burst_size,
                    'last_update': now
                }

            state = self._local_store[key]
            elapsed = now - state['last_update']
            tokens_to_add = elapsed * (config.requests / config.window_seconds)
            tokens = min(config.burst_size, state['tokens'] + tokens_to_add)

            if tokens >= 1:
                tokens -= 1
                self._local_store[key] = {
                    'tokens': tokens,
                    'last_update': now
                }

                return RateLimitResult(
                    allowed=True,
                    remaining=int(tokens),
                    reset_at=int(now + config.window_seconds),
                    retry_after=0,
                    limit=config.requests
                )
            else:
                retry_after = int((1 - tokens) / (config.requests / config.window_seconds))

                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_at=int(now + retry_after),
                    retry_after=retry_after,
                    limit=config.requests
                )

    def _fixed_window(
        self,
        identifier: str,
        config: RateLimitConfig,
    ) -> RateLimitResult:
        """
        Fixed window rate limiting.

        Simpler but allows bursts at window boundaries.
        """
        now = time.time()
        window_key = int(now / config.window_seconds)
        key = f"ratelimit:fw:{identifier}:{window_key}"

        if self.redis:
            count = self.redis.get(key)
            count = int(count) if count else 0

            if count < config.requests:
                pipe = self.redis.pipeline()
                pipe.incr(key)
                pipe.expire(key, config.window_seconds)
                pipe.execute()

                return RateLimitResult(
                    allowed=True,
                    remaining=config.requests - count - 1,
                    reset_at=(window_key + 1) * config.window_seconds,
                    retry_after=0,
                    limit=config.requests
                )
            else:
                reset_at = (window_key + 1) * config.window_seconds
                retry_after = max(0, int(reset_at - now))

                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_at=int(reset_at),
                    retry_after=retry_after,
                    limit=config.requests
                )
        else:
            if key not in self._local_store:
                self._local_store[key] = 0

            count = self._local_store[key]

            if count < config.requests:
                self._local_store[key] = count + 1

                return RateLimitResult(
                    allowed=True,
                    remaining=config.requests - count - 1,
                    reset_at=(window_key + 1) * config.window_seconds,
                    retry_after=0,
                    limit=config.requests
                )
            else:
                reset_at = (window_key + 1) * config.window_seconds
                retry_after = max(0, int(reset_at - now))

                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_at=int(reset_at),
                    retry_after=retry_after,
                    limit=config.requests
                )

    def _adaptive(
        self,
        identifier: str,
        config: RateLimitConfig,
    ) -> RateLimitResult:
        """
        Adaptive rate limiting.

        Adjusts limits based on system load and user behavior.
        """
        # Get user's recent behavior
        violation_key = f"violations:{identifier}"

        if self.redis:
            violations = int(self.redis.get(violation_key) or 0)
        else:
            violations = self._local_store.get(violation_key, 0)

        # Adjust config based on violations
        adjusted_requests = config.requests
        if violations > 5:
            # Reduce limit for repeat violators
            adjusted_requests = max(1, config.requests // 2)
        elif violations > 10:
            # Severe violators get minimal access
            adjusted_requests = max(1, config.requests // 4)

        # Use sliding window with adjusted limit
        adjusted_config = RateLimitConfig(
            requests=adjusted_requests,
            window_seconds=config.window_seconds,
            strategy=RateLimitStrategy.SLIDING_WINDOW,
            scope=config.scope
        )

        result = self._sliding_window(identifier, adjusted_config)

        # Track violations
        if not result.allowed:
            if self.redis:
                pipe = self.redis.pipeline()
                pipe.incr(violation_key)
                pipe.expire(violation_key, 3600)  # Track for 1 hour
                pipe.execute()
            else:
                self._local_store[violation_key] = violations + 1

        return result

    def _is_blocked(self, identifier: str) -> bool:
        """Check if identifier is currently blocked."""
        if identifier in self._blocked_ips:
            if time.time() < self._blocked_ips[identifier]:
                return True
            else:
                # Unblock expired blocks
                del self._blocked_ips[identifier]
        return False

    def _block_identifier(self, identifier: str, duration: int):
        """Temporarily block an identifier."""
        self._blocked_ips[identifier] = time.time() + duration

    def get_identifier(self, scope: RateLimitScope) -> str:
        """
        Get identifier based on scope.

        Args:
            scope: Rate limit scope

        Returns:
            Unique identifier string
        """
        if scope == RateLimitScope.PER_IP:
            return self._get_client_ip()
        elif scope == RateLimitScope.PER_USER:
            return getattr(g, 'user_id', 'anonymous')
        elif scope == RateLimitScope.PER_API_KEY:
            api_key = request.headers.get('x-api-key') or request.headers.get('Authorization', '')
            return hashlib.sha256(api_key.encode()).hexdigest()[:16]
        elif scope == RateLimitScope.PER_ENDPOINT:
            return f"{self._get_client_ip()}:{request.endpoint}"
        else:  # GLOBAL
            return "global"

    def _get_client_ip(self) -> str:
        """Get client IP address."""
        # Check for proxy headers
        if request.headers.get('X-Forwarded-For'):
            # Get first IP in chain (original client)
            ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            ip = request.headers.get('X-Real-IP')
        else:
            ip = request.remote_addr

        return ip or 'unknown'


def rate_limit_decorator(
    config: RateLimitConfig,
    limiter: Optional[DistributedRateLimiter] = None,
):
    """
    Decorator to apply rate limiting to Flask routes.

    Usage:
        @app.route('/api/endpoint')
        @rate_limit_decorator(RateLimitConfig(requests=100, window_seconds=60))
        def my_endpoint():
            return jsonify({'status': 'ok'})

    Args:
        config: Rate limit configuration
        limiter: Rate limiter instance (creates new if not provided)
    """
    if limiter is None:
        limiter = DistributedRateLimiter()

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get identifier based on scope
            identifier = limiter.get_identifier(config.scope)

            try:
                # Check rate limit
                result = limiter.check_rate_limit(identifier, config)

                # Add rate limit headers to response
                @wraps(f)
                def add_headers(response):
                    response.headers['X-RateLimit-Limit'] = str(result.limit)
                    response.headers['X-RateLimit-Remaining'] = str(result.remaining)
                    response.headers['X-RateLimit-Reset'] = str(result.reset_at)
                    return response

                # Store function to add headers after request
                g.rate_limit_headers = add_headers

                # Call original function
                return f(*args, **kwargs)

            except RateLimitExceeded as e:
                # Return 429 Too Many Requests
                response = jsonify({
                    'error': 'rate_limit_exceeded',
                    'message': str(e),
                    'retry_after': e.retry_after
                })
                response.status_code = 429
                response.headers['Retry-After'] = str(e.retry_after)
                return response

        return decorated_function

    return decorator


# Predefined rate limit configs
RATE_LIMITS = {
    'free_tier': RateLimitConfig(
        requests=100,
        window_seconds=3600,
        strategy=RateLimitStrategy.SLIDING_WINDOW,
        scope=RateLimitScope.PER_IP
    ),
    'starter': RateLimitConfig(
        requests=1000,
        window_seconds=3600,
        strategy=RateLimitStrategy.TOKEN_BUCKET,
        scope=RateLimitScope.PER_API_KEY
    ),
    'professional': RateLimitConfig(
        requests=10000,
        window_seconds=3600,
        strategy=RateLimitStrategy.SLIDING_WINDOW,
        scope=RateLimitScope.PER_API_KEY
    ),
    'enterprise': RateLimitConfig(
        requests=100000,
        window_seconds=3600,
        strategy=RateLimitStrategy.ADAPTIVE,
        scope=RateLimitScope.PER_API_KEY
    ),
    'strict': RateLimitConfig(
        requests=10,
        window_seconds=60,
        strategy=RateLimitStrategy.SLIDING_WINDOW,
        scope=RateLimitScope.PER_IP,
        block_duration=300  # 5 minute block
    ),
}
