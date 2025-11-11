"""
LOKI Interceptor - Utilities Package
Performance optimization and monitoring tools for enterprise-scale operations
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .cache_manager import CacheManager, get_cache_manager
    from .profiler import PerformanceProfiler, profile_function, ProfileContext, get_profiler
    from .async_processor import AsyncDocumentProcessor, ConnectionPool
    from .circuit_breaker import CircuitBreaker, get_circuit_breaker, with_circuit_breaker

__all__ = [
    'CacheManager',
    'get_cache_manager',
    'PerformanceProfiler',
    'profile_function',
    'ProfileContext',
    'get_profiler',
    'AsyncDocumentProcessor',
    'ConnectionPool',
    'CircuitBreaker',
    'get_circuit_breaker',
    'with_circuit_breaker',
]
