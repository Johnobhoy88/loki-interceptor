"""
Redis-based caching abstraction for LOKI Interceptor
Provides high-performance distributed caching with fallback to in-memory for development
"""

import hashlib
import json
import pickle
import time
from typing import Any, Optional, Callable, Dict
from collections import OrderedDict
from functools import wraps
import os


class CacheManager:
    """
    Enterprise-grade caching with Redis backend and fakeredis fallback

    Features:
    - Distributed caching with Redis
    - Automatic serialization/deserialization
    - TTL support
    - Cache statistics and monitoring
    - Connection pooling
    - Graceful fallback to in-memory cache
    """

    def __init__(
        self,
        redis_url: Optional[str] = None,
        default_ttl: int = 3600,
        max_memory_size: int = 1000,
        use_compression: bool = False
    ):
        """
        Initialize cache manager with Redis or in-memory fallback

        Args:
            redis_url: Redis connection URL (e.g., redis://localhost:6379/0)
                      If None, uses fakeredis for local development
            default_ttl: Default time-to-live in seconds (default: 1 hour)
            max_memory_size: Maximum items for in-memory fallback
            use_compression: Enable compression for large values
        """
        self.default_ttl = default_ttl
        self.max_memory_size = max_memory_size
        self.use_compression = use_compression

        # Statistics tracking
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0
        }

        # Try to initialize Redis
        self.redis_client = None
        self.use_redis = False
        self._memory_cache: OrderedDict = OrderedDict()

        try:
            # Try real Redis first
            if redis_url:
                import redis
                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses=False,
                    socket_connect_timeout=2,
                    socket_timeout=2
                )
                # Test connection
                self.redis_client.ping()
                self.use_redis = True
                print(f"[CacheManager] Connected to Redis: {redis_url}")
            else:
                # Use fakeredis for local development
                try:
                    import fakeredis
                    self.redis_client = fakeredis.FakeStrictRedis(decode_responses=False)
                    self.use_redis = True
                    print("[CacheManager] Using fakeredis for local development")
                except ImportError:
                    print("[CacheManager] fakeredis not available, using in-memory cache")
                    self.use_redis = False
        except Exception as e:
            print(f"[CacheManager] Redis connection failed: {e}, falling back to memory")
            self.redis_client = None
            self.use_redis = False

    def _make_key(self, key: str, namespace: str = "loki") -> str:
        """
        Generate namespaced cache key

        Args:
            key: Base key
            namespace: Cache namespace for isolation

        Returns:
            Namespaced key
        """
        return f"{namespace}:{key}"

    def _serialize(self, value: Any) -> bytes:
        """
        Serialize value for storage

        Args:
            value: Value to serialize

        Returns:
            Serialized bytes
        """
        try:
            # Try JSON first (faster, more readable)
            return json.dumps(value).encode('utf-8')
        except (TypeError, ValueError):
            # Fall back to pickle for complex objects
            return pickle.dumps(value)

    def _deserialize(self, data: bytes) -> Any:
        """
        Deserialize stored value

        Args:
            data: Serialized bytes

        Returns:
            Deserialized value
        """
        try:
            # Try JSON first
            return json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Fall back to pickle
            return pickle.loads(data)

    def get(self, key: str, namespace: str = "loki") -> Optional[Any]:
        """
        Retrieve value from cache

        Args:
            key: Cache key
            namespace: Cache namespace

        Returns:
            Cached value or None if not found
        """
        cache_key = self._make_key(key, namespace)

        try:
            if self.use_redis and self.redis_client:
                # Redis backend
                data = self.redis_client.get(cache_key)
                if data:
                    self.stats['hits'] += 1
                    return self._deserialize(data)
                else:
                    self.stats['misses'] += 1
                    return None
            else:
                # In-memory fallback
                if cache_key in self._memory_cache:
                    value, expiry = self._memory_cache[cache_key]
                    if expiry is None or time.time() < expiry:
                        # Move to end (LRU)
                        self._memory_cache.move_to_end(cache_key)
                        self.stats['hits'] += 1
                        return value
                    else:
                        # Expired
                        del self._memory_cache[cache_key]
                        self.stats['misses'] += 1
                        return None
                else:
                    self.stats['misses'] += 1
                    return None
        except Exception as e:
            print(f"[CacheManager] Get error for key {key}: {e}")
            self.stats['errors'] += 1
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        namespace: str = "loki"
    ) -> bool:
        """
        Store value in cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None = default_ttl)
            namespace: Cache namespace

        Returns:
            True if successful, False otherwise
        """
        cache_key = self._make_key(key, namespace)
        ttl = ttl if ttl is not None else self.default_ttl

        try:
            if self.use_redis and self.redis_client:
                # Redis backend
                data = self._serialize(value)
                self.redis_client.setex(cache_key, ttl, data)
                self.stats['sets'] += 1
                return True
            else:
                # In-memory fallback with LRU eviction
                if len(self._memory_cache) >= self.max_memory_size and cache_key not in self._memory_cache:
                    # Remove oldest item
                    self._memory_cache.popitem(last=False)

                expiry = time.time() + ttl if ttl > 0 else None
                self._memory_cache[cache_key] = (value, expiry)
                self.stats['sets'] += 1
                return True
        except Exception as e:
            print(f"[CacheManager] Set error for key {key}: {e}")
            self.stats['errors'] += 1
            return False

    def delete(self, key: str, namespace: str = "loki") -> bool:
        """
        Delete value from cache

        Args:
            key: Cache key
            namespace: Cache namespace

        Returns:
            True if deleted, False otherwise
        """
        cache_key = self._make_key(key, namespace)

        try:
            if self.use_redis and self.redis_client:
                result = self.redis_client.delete(cache_key)
                if result:
                    self.stats['deletes'] += 1
                return bool(result)
            else:
                if cache_key in self._memory_cache:
                    del self._memory_cache[cache_key]
                    self.stats['deletes'] += 1
                    return True
                return False
        except Exception as e:
            print(f"[CacheManager] Delete error for key {key}: {e}")
            self.stats['errors'] += 1
            return False

    def clear(self, namespace: str = "loki") -> bool:
        """
        Clear all keys in namespace

        Args:
            namespace: Cache namespace to clear

        Returns:
            True if successful
        """
        try:
            if self.use_redis and self.redis_client:
                # Delete all keys with namespace prefix
                pattern = self._make_key("*", namespace)
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
                return True
            else:
                # Clear memory cache for namespace
                keys_to_delete = [k for k in self._memory_cache.keys() if k.startswith(f"{namespace}:")]
                for key in keys_to_delete:
                    del self._memory_cache[key]
                return True
        except Exception as e:
            print(f"[CacheManager] Clear error for namespace {namespace}: {e}")
            self.stats['errors'] += 1
            return False

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Dictionary with cache statistics
        """
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0

        stats = {
            **self.stats,
            'hit_rate': round(hit_rate, 2),
            'backend': 'redis' if self.use_redis else 'memory',
            'total_requests': total_requests
        }

        if not self.use_redis:
            stats['memory_size'] = len(self._memory_cache)
            stats['memory_max'] = self.max_memory_size

        return stats

    def reset_stats(self) -> None:
        """Reset cache statistics"""
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0
        }

    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on cache backend

        Returns:
            Health status dictionary
        """
        health = {
            'healthy': False,
            'backend': 'redis' if self.use_redis else 'memory',
            'latency_ms': None
        }

        try:
            start = time.time()

            if self.use_redis and self.redis_client:
                # Test Redis connection
                self.redis_client.ping()
            else:
                # Memory cache is always healthy if we got here
                pass

            latency = (time.time() - start) * 1000
            health['healthy'] = True
            health['latency_ms'] = round(latency, 2)
        except Exception as e:
            health['error'] = str(e)

        return health


def cache_result(
    ttl: int = 3600,
    namespace: str = "loki",
    key_prefix: str = "",
    cache_manager: Optional[CacheManager] = None
) -> Callable:
    """
    Decorator for caching function results

    Args:
        ttl: Time-to-live in seconds
        namespace: Cache namespace
        key_prefix: Optional key prefix
        cache_manager: CacheManager instance (creates new if None)

    Returns:
        Decorated function

    Example:
        @cache_result(ttl=300, namespace="validation")
        def expensive_operation(text: str) -> dict:
            # ... expensive processing
            return result
    """
    def decorator(func: Callable) -> Callable:
        # Use global cache manager or create one
        cm = cache_manager or CacheManager()

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_parts = [key_prefix or func.__name__]

            # Hash arguments for key
            args_str = json.dumps([str(arg) for arg in args], sort_keys=True)
            kwargs_str = json.dumps(kwargs, sort_keys=True, default=str)
            combined = f"{args_str}:{kwargs_str}"
            arg_hash = hashlib.md5(combined.encode()).hexdigest()
            key_parts.append(arg_hash)

            cache_key = ":".join(key_parts)

            # Try to get from cache
            cached = cm.get(cache_key, namespace)
            if cached is not None:
                return cached

            # Execute function
            result = func(*args, **kwargs)

            # Store in cache
            cm.set(cache_key, result, ttl, namespace)

            return result

        return wrapper
    return decorator


# Global cache manager instance
_global_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """
    Get or create global cache manager instance

    Returns:
        Global CacheManager instance
    """
    global _global_cache_manager

    if _global_cache_manager is None:
        redis_url = os.getenv('REDIS_URL')
        _global_cache_manager = CacheManager(redis_url=redis_url)

    return _global_cache_manager
