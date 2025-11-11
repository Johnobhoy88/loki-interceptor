"""
API Dependencies and Middleware

Dependency injection for FastAPI endpoints
"""

import time
from typing import Optional
from functools import lru_cache

from fastapi import Request, HTTPException, status
from fastapi.security import APIKeyHeader

# Singleton instances
_engine = None
_corrector = None
_audit_logger = None
_cache = None
_rate_limiter = None
_security_manager = None


# API Key security (optional - for future use)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


@lru_cache()
def get_engine():
    """Get or create LOKI engine instance"""
    global _engine
    if _engine is None:
        try:
            from backend.core.async_engine import AsyncLOKIEngine
        except ImportError:
            # Fallback to sync engine
            from backend.core.engine import LOKIEngine
            _engine = LOKIEngine()
        else:
            _engine = AsyncLOKIEngine(max_workers=4)
    return _engine


@lru_cache()
def get_corrector():
    """Get or create document corrector instance"""
    global _corrector
    if _corrector is None:
        try:
            from backend.core.corrector import DocumentCorrector
            _corrector = DocumentCorrector()
        except ImportError:
            raise RuntimeError("DocumentCorrector not available")
    return _corrector


@lru_cache()
def get_synthesis_engine():
    """Get or create synthesis engine instance"""
    try:
        from backend.core.synthesis import SynthesisEngine
        audit_logger = get_audit_logger()
        engine = get_engine()
        return SynthesisEngine(engine, audit_logger=audit_logger)
    except ImportError:
        raise RuntimeError("SynthesisEngine not available")


@lru_cache()
def get_audit_logger():
    """Get or create audit logger instance"""
    global _audit_logger
    if _audit_logger is None:
        try:
            from backend.core.audit_log import AuditLogger
            _audit_logger = AuditLogger()
        except ImportError:
            # Create a simple logger fallback
            class SimpleLogger:
                def log_validation(self, *args, **kwargs):
                    pass

                def get_stats(self, *args, **kwargs):
                    return {}

                def get_overview(self, *args, **kwargs):
                    return {}

                def get_risk_trends(self, *args, **kwargs):
                    return []

                def get_module_performance(self, *args, **kwargs):
                    return []

                def get_top_gate_failures(self, *args, **kwargs):
                    return []

            _audit_logger = SimpleLogger()
    return _audit_logger


@lru_cache()
def get_cache():
    """Get or create validation cache instance"""
    global _cache
    if _cache is None:
        try:
            from backend.core.cache import ValidationCache
            _cache = ValidationCache(max_size=500, ttl_seconds=1800)
        except ImportError:
            # Create a simple cache fallback
            class SimpleCache:
                def get(self, *args, **kwargs):
                    return None

                def set(self, *args, **kwargs):
                    pass

                def clear(self):
                    pass

                def get_stats(self):
                    return {
                        'total_entries': 0,
                        'cache_hits': 0,
                        'cache_misses': 0,
                        'hit_rate': 0.0,
                        'memory_usage_mb': 0.0,
                        'oldest_entry_age_seconds': 0.0
                    }

            _cache = SimpleCache()
    return _cache


@lru_cache()
def get_rate_limiter():
    """Get or create rate limiter instance"""
    global _rate_limiter
    if _rate_limiter is None:
        try:
            from backend.core.security import RateLimiter
            _rate_limiter = RateLimiter()
        except ImportError:
            # Create a simple rate limiter fallback
            class SimpleRateLimiter:
                def is_allowed(self, *args, **kwargs):
                    return True

                def get_client_id(self):
                    return "unknown"

            _rate_limiter = SimpleRateLimiter()
    return _rate_limiter


@lru_cache()
def get_security_manager():
    """Get or create security manager instance"""
    global _security_manager
    if _security_manager is None:
        try:
            from backend.core.security import SecurityManager
            _security_manager = SecurityManager()
        except ImportError:
            # Create a simple security manager fallback
            class SimpleSecurityManager:
                def validate_api_key_format(self, provider, api_key):
                    return True

                def sanitize_error(self, error):
                    return {"error": str(error)}

            _security_manager = SimpleSecurityManager()
    return _security_manager


# Rate limiting dependency
async def check_rate_limit(request: Request):
    """
    Check rate limit for incoming request

    Raises HTTPException if rate limit exceeded
    """
    rate_limiter = get_rate_limiter()

    # Get client identifier
    client_ip = request.client.host if request.client else "unknown"

    # Check rate limit
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": "60"}
        )

    return True


# API Key validation dependency (optional)
async def validate_api_key(
    request: Request,
    api_key: Optional[str] = None
):
    """
    Validate API key if provided

    For future authentication implementation
    """
    if api_key is None:
        # API key not required yet
        return None

    security_manager = get_security_manager()

    # Validate key format
    if not security_manager.validate_api_key_format("loki", api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format"
        )

    # Here you would validate against a database or key store
    # For now, just return the key
    return api_key


# Request size limit dependency
async def check_request_size(request: Request, max_size_mb: float = 10.0):
    """
    Check request size limit

    Args:
        request: FastAPI request
        max_size_mb: Maximum request size in megabytes

    Raises:
        HTTPException: If request size exceeds limit
    """
    content_length = request.headers.get("content-length")

    if content_length:
        content_length_bytes = int(content_length)
        max_bytes = max_size_mb * 1024 * 1024

        if content_length_bytes > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Request size exceeds maximum of {max_size_mb}MB"
            )

    return True


# Timing dependency
class RequestTimer:
    """Request timing context"""

    def __init__(self):
        self.start_time = time.time()

    def elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds"""
        return (time.time() - self.start_time) * 1000


def get_request_timer() -> RequestTimer:
    """Get request timer"""
    return RequestTimer()
