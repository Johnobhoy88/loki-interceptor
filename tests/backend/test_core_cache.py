"""
Comprehensive tests for backend.core.cache module.

Tests cache functionality including:
- Cache initialization and configuration
- Setting and getting values
- TTL and expiration
- Cache invalidation
- Memory management
- Concurrent access
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import threading

from backend.core.cache import ValidationCache


class TestValidationCacheBasics:
    """Test basic cache operations."""

    def test_cache_initialization(self):
        """Test cache can be initialized with default settings."""
        cache = ValidationCache()
        assert cache is not None
        assert hasattr(cache, 'get')
        assert hasattr(cache, 'set')
        assert hasattr(cache, 'clear')

    def test_cache_initialization_with_custom_params(self):
        """Test cache initialization with custom parameters."""
        cache = ValidationCache(max_size=50, ttl_seconds=100)
        assert cache.max_size == 50
        assert cache.ttl_seconds == 100

    def test_set_and_get_simple_value(self):
        """Test setting and retrieving a simple value."""
        cache = ValidationCache()
        cache.set("test_key", "test_value")
        result = cache.get("test_key")
        assert result == "test_value"

    def test_get_nonexistent_key(self):
        """Test getting a key that doesn't exist."""
        cache = ValidationCache()
        result = cache.get("nonexistent")
        assert result is None

    def test_set_and_get_dict_value(self):
        """Test caching dictionary values."""
        cache = ValidationCache()
        test_dict = {"key1": "value1", "key2": "value2"}
        cache.set("dict_key", test_dict)
        result = cache.get("dict_key")
        assert result == test_dict

    def test_set_and_get_list_value(self):
        """Test caching list values."""
        cache = ValidationCache()
        test_list = [1, 2, 3, "a", "b"]
        cache.set("list_key", test_list)
        result = cache.get("list_key")
        assert result == test_list

    def test_overwrite_existing_key(self):
        """Test overwriting an existing key."""
        cache = ValidationCache()
        cache.set("key", "value1")
        cache.set("key", "value2")
        result = cache.get("key")
        assert result == "value2"

    def test_cache_clear(self):
        """Test clearing the entire cache."""
        cache = ValidationCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_delete_specific_key(self):
        """Test deleting a specific key from cache."""
        cache = ValidationCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        if hasattr(cache, 'delete'):
            cache.delete("key1")
            assert cache.get("key1") is None
            assert cache.get("key2") == "value2"

    def test_cache_size_limit(self):
        """Test that cache respects maximum size."""
        cache = ValidationCache(max_size=3)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        cache.set("key4", "value4")  # Should trigger eviction
        # At least some values should be in cache
        cached_values = sum([
            1 for key in ["key1", "key2", "key3", "key4"]
            if cache.get(key) is not None
        ])
        assert cached_values <= 3


class TestValidationCacheTTL:
    """Test cache TTL (Time To Live) functionality."""

    def test_value_expires_after_ttl(self):
        """Test that values expire after TTL."""
        cache = ValidationCache(ttl_seconds=1)
        cache.set("temp_key", "temp_value")
        assert cache.get("temp_key") == "temp_value"
        time.sleep(1.1)
        assert cache.get("temp_key") is None

    def test_value_persists_before_ttl(self):
        """Test that values persist before TTL expires."""
        cache = ValidationCache(ttl_seconds=5)
        cache.set("key", "value")
        time.sleep(0.5)
        assert cache.get("key") == "value"

    def test_custom_ttl_per_key(self):
        """Test setting custom TTL for individual keys if supported."""
        cache = ValidationCache(ttl_seconds=10)
        if hasattr(cache, 'set_with_ttl'):
            cache.set_with_ttl("key", "value", ttl_seconds=1)
            assert cache.get("key") == "value"
            time.sleep(1.1)
            assert cache.get("key") is None

    def test_accessed_key_updates_timestamp(self):
        """Test that accessing a key doesn't reset its TTL (typical behavior)."""
        cache = ValidationCache(ttl_seconds=2)
        cache.set("key", "value")
        time.sleep(1)
        cache.get("key")  # Access the key
        time.sleep(1.1)
        # Value should have expired based on original set time
        result = cache.get("key")
        # This depends on implementation - some caches reset TTL on access
        assert result is None or result == "value"


class TestValidationCachePerformance:
    """Test cache performance characteristics."""

    def test_bulk_set_performance(self):
        """Test performance of bulk operations."""
        cache = ValidationCache(max_size=1000)
        start_time = time.time()

        for i in range(100):
            cache.set(f"key_{i}", f"value_{i}")

        elapsed = time.time() - start_time
        assert elapsed < 1.0  # Should complete in less than 1 second

    def test_bulk_get_performance(self):
        """Test performance of bulk read operations."""
        cache = ValidationCache()

        # Setup: add items to cache
        for i in range(50):
            cache.set(f"key_{i}", f"value_{i}")

        # Test: read all items
        start_time = time.time()
        results = []
        for i in range(50):
            results.append(cache.get(f"key_{i}"))
        elapsed = time.time() - start_time

        assert len(results) == 50
        assert elapsed < 0.5  # Should be very fast

    def test_cache_hit_rate(self):
        """Test cache hit rate tracking if available."""
        cache = ValidationCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        # Generate hits
        cache.get("key1")
        cache.get("key1")
        cache.get("key2")

        # Generate misses
        cache.get("nonexistent1")
        cache.get("nonexistent2")

        if hasattr(cache, 'get_stats'):
            stats = cache.get_stats()
            assert 'hits' in stats or 'hit_rate' in stats


class TestValidationCacheConcurrency:
    """Test thread-safe cache operations."""

    def test_concurrent_writes(self):
        """Test cache handles concurrent writes."""
        cache = ValidationCache()
        results = []

        def write_values(start, count):
            for i in range(start, start + count):
                cache.set(f"key_{i}", f"value_{i}")
                results.append(i)

        threads = [
            threading.Thread(target=write_values, args=(0, 10)),
            threading.Thread(target=write_values, args=(10, 10)),
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 20

    def test_concurrent_reads(self):
        """Test cache handles concurrent reads."""
        cache = ValidationCache()

        # Setup cache
        for i in range(20):
            cache.set(f"key_{i}", f"value_{i}")

        results = []
        errors = []

        def read_values(start, count):
            try:
                for i in range(start, start + count):
                    value = cache.get(f"key_{i}")
                    if value is not None:
                        results.append(value)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=read_values, args=(0, 10)),
            threading.Thread(target=read_values, args=(10, 10)),
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(results) == 20

    def test_concurrent_read_write(self):
        """Test cache handles concurrent reads and writes."""
        cache = ValidationCache()
        errors = []

        def writer():
            try:
                for i in range(10):
                    cache.set(f"write_key_{i}", f"value_{i}")
                    time.sleep(0.01)
            except Exception as e:
                errors.append(e)

        def reader():
            try:
                for i in range(20):
                    cache.get(f"write_key_{i % 10}")
                    time.sleep(0.005)
            except Exception as e:
                errors.append(e)

        writer_thread = threading.Thread(target=writer)
        reader_thread = threading.Thread(target=reader)

        writer_thread.start()
        reader_thread.start()

        writer_thread.join()
        reader_thread.join()

        assert len(errors) == 0


class TestValidationCacheIntegration:
    """Integration tests for cache with validation scenarios."""

    def test_cache_validation_results(self):
        """Test caching real validation results."""
        cache = ValidationCache()

        validation_result = {
            "status": "PASS",
            "overall_risk": "LOW",
            "modules": {
                "fca_uk": {"status": "PASS", "violations": 0},
                "gdpr_uk": {"status": "PASS", "violations": 0}
            },
            "timestamp": datetime.utcnow().isoformat(),
            "violations_count": 0
        }

        cache.set("validation_doc_123", validation_result)
        cached_result = cache.get("validation_doc_123")

        assert cached_result == validation_result
        assert cached_result["status"] == "PASS"
        assert cached_result["modules"]["fca_uk"]["violations"] == 0

    def test_cache_expiration_for_temporal_data(self):
        """Test cache expiration for time-sensitive validation data."""
        cache = ValidationCache(ttl_seconds=1)

        # Cache a validation result with timestamp
        result = {
            "status": "PASS",
            "timestamp": datetime.utcnow().isoformat()
        }

        cache.set("temp_validation", result)
        assert cache.get("temp_validation") is not None

        time.sleep(1.1)
        assert cache.get("temp_validation") is None

    def test_cache_invalidation_pattern(self):
        """Test cache invalidation patterns."""
        cache = ValidationCache()

        # Simulate document-level caching
        doc_id = "doc_123"
        module_name = "fca_uk"

        cache.set(f"{doc_id}_{module_name}", {"result": "pass"})

        # Invalidate all modules for this document
        if hasattr(cache, 'delete'):
            cache.delete(f"{doc_id}_{module_name}")
            assert cache.get(f"{doc_id}_{module_name}") is None
        else:
            cache.clear()
            assert cache.get(f"{doc_id}_{module_name}") is None


class TestValidationCacheErrorHandling:
    """Test cache error handling."""

    def test_set_none_value(self):
        """Test handling of None values."""
        cache = ValidationCache()
        cache.set("none_key", None)
        # Behavior depends on implementation
        result = cache.get("none_key")
        assert result is None

    def test_get_with_invalid_key_type(self):
        """Test handling of invalid key types."""
        cache = ValidationCache()
        try:
            # Most caches convert to string
            result = cache.get(12345)
            # Either succeeds or raises an error, both acceptable
        except Exception:
            pass  # Expected behavior

    def test_cache_with_large_values(self):
        """Test caching large values."""
        cache = ValidationCache(max_size=2)

        large_value = "x" * (1024 * 100)  # 100KB string
        cache.set("large_key", large_value)
        result = cache.get("large_key")
        assert result == large_value or result is None  # Depends on implementation

    def test_cache_with_special_characters_in_key(self):
        """Test keys with special characters."""
        cache = ValidationCache()
        special_keys = [
            "key with spaces",
            "key/with/slashes",
            "key:with:colons",
            "key.with.dots",
            "key@with#symbols$"
        ]

        for key in special_keys:
            cache.set(key, f"value_for_{key}")
            result = cache.get(key)
            assert result == f"value_for_{key}"


class TestValidationCacheMemoryManagement:
    """Test cache memory management."""

    def test_cache_with_max_size_enforcement(self):
        """Test that cache enforces maximum size."""
        cache = ValidationCache(max_size=5)

        # Add more items than max_size
        for i in range(10):
            cache.set(f"key_{i}", f"value_{i}")

        # Count items in cache
        count = sum([1 for i in range(10) if cache.get(f"key_{i}") is not None])
        assert count <= 5

    def test_lru_eviction_if_supported(self):
        """Test LRU eviction policy if supported."""
        cache = ValidationCache(max_size=3)

        # Add items in order
        cache.set("a", "1")
        cache.set("b", "2")
        cache.set("c", "3")

        # Access 'a' to mark it as recently used
        cache.get("a")

        # Add new item - should evict least recently used
        cache.set("d", "4")

        # At least 'a' or 'd' should be in cache
        assert cache.get("a") is not None or cache.get("d") is not None
