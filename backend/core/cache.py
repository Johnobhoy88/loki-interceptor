"""
Content-hash based caching for validation results
Reduces redundant gate execution
"""
import hashlib
import time
import json
from collections import OrderedDict


class ValidationCache:
    """LRU cache for validation results with TTL"""

    def __init__(self, max_size=1000, ttl_seconds=3600):
        """
        Args:
            max_size: Maximum number of cached entries
            ttl_seconds: Time-to-live for cache entries (default 1 hour)
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache = OrderedDict()  # {cache_key: (result, timestamp)}
        self.hits = 0
        self.misses = 0

    def _make_cache_key(self, text, document_type, active_modules):
        """
        Generate cache key from validation inputs

        Args:
            text: Document text
            document_type: Type of document
            active_modules: List of module IDs

        Returns:
            str: SHA-256 hash cache key
        """
        # Sort modules for consistency
        modules_str = ','.join(sorted(active_modules or []))
        key_input = f"{text}|{document_type}|{modules_str}"
        return hashlib.sha256(key_input.encode()).hexdigest()

    def get(self, text, document_type, active_modules):
        """
        Retrieve cached validation result

        Returns:
            dict or None: Cached result if valid, None otherwise
        """
        cache_key = self._make_cache_key(text, document_type, active_modules)

        if cache_key in self.cache:
            result, timestamp = self.cache[cache_key]

            # Check if expired
            if time.time() - timestamp > self.ttl_seconds:
                del self.cache[cache_key]
                self.misses += 1
                return None

            # Move to end (most recently used)
            self.cache.move_to_end(cache_key)
            self.hits += 1
            return result

        self.misses += 1
        return None

    def set(self, text, document_type, active_modules, result):
        """
        Store validation result in cache

        Args:
            text: Document text
            document_type: Type of document
            active_modules: List of module IDs
            result: Validation result to cache
        """
        cache_key = self._make_cache_key(text, document_type, active_modules)

        # Remove oldest entry if at capacity
        if len(self.cache) >= self.max_size and cache_key not in self.cache:
            self.cache.popitem(last=False)

        # Store with timestamp
        self.cache[cache_key] = (result, time.time())

    def clear(self):
        """Clear all cached entries"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def get_stats(self):
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': round(hit_rate, 2),
            'ttl_seconds': self.ttl_seconds
        }

    def cleanup_expired(self):
        """Remove expired entries from cache"""
        now = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if now - timestamp > self.ttl_seconds
        ]

        for key in expired_keys:
            del self.cache[key]

        return len(expired_keys)
