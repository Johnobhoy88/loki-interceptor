"""
Example usage of LOKI Interceptor performance optimization utilities

This file demonstrates how to use the various performance optimization
features in a production environment.
"""

import time
from typing import Dict, Any


def example_cache_usage():
    """Demonstrate cache manager usage"""
    print("\n" + "="*80)
    print("CACHE MANAGER EXAMPLE")
    print("="*80)

    from core.utils.cache_manager import CacheManager, cache_result

    # Initialize cache (auto-detects fakeredis or falls back to memory)
    cache = CacheManager(default_ttl=300)

    # Basic operations
    cache.set('user:123', {'name': 'John', 'role': 'admin'}, ttl=600)
    user = cache.get('user:123')
    print(f"Retrieved user: {user}")

    # Using decorator for automatic caching
    @cache_result(ttl=300, namespace="validation")
    def expensive_validation(text: str) -> dict:
        print("  → Performing expensive validation...")
        time.sleep(0.1)  # Simulate expensive operation
        return {'status': 'PASS', 'text_length': len(text)}

    # First call - cache miss
    print("\nFirst call (cache miss):")
    start = time.time()
    result1 = expensive_validation("Sample document text")
    print(f"  Time: {(time.time() - start)*1000:.2f}ms")
    print(f"  Result: {result1}")

    # Second call - cache hit
    print("\nSecond call (cache hit):")
    start = time.time()
    result2 = expensive_validation("Sample document text")
    print(f"  Time: {(time.time() - start)*1000:.2f}ms")
    print(f"  Result: {result2}")

    # Statistics
    stats = cache.get_stats()
    print(f"\nCache statistics:")
    print(f"  Hit rate: {stats['hit_rate']}%")
    print(f"  Total requests: {stats['total_requests']}")
    print(f"  Backend: {stats['backend']}")


def example_profiler_usage():
    """Demonstrate profiler usage"""
    print("\n" + "="*80)
    print("PERFORMANCE PROFILER EXAMPLE")
    print("="*80)

    from core.utils.profiler import get_profiler, profile_function, ProfileContext

    profiler = get_profiler()

    # Method 1: Decorator
    @profile_function("validate_document")
    def validate_document(text: str) -> dict:
        time.sleep(0.05)  # Simulate processing
        return {'status': 'PASS', 'checks': 10}

    # Method 2: Context manager
    def process_with_context():
        with ProfileContext("data_processing") as ctx:
            time.sleep(0.03)
            return "processed"

    # Run operations
    print("\nRunning profiled operations...")
    for i in range(5):
        validate_document(f"Document {i}")
        process_with_context()

    # Get statistics
    print("\nOperation statistics:")
    stats = profiler.get_all_stats()
    for op_name, op_stats in stats['operations'].items():
        print(f"\n  {op_name}:")
        print(f"    Count: {op_stats['count']}")
        print(f"    Avg: {op_stats['avg_ms']:.2f}ms")
        print(f"    Min: {op_stats['min_ms']:.2f}ms")
        print(f"    Max: {op_stats['max_ms']:.2f}ms")

    # Identify bottlenecks
    bottlenecks = profiler.identify_bottlenecks(threshold_ms=40)
    if bottlenecks:
        print("\nIdentified bottlenecks:")
        for bn in bottlenecks:
            print(f"  {bn['operation']}: {bn['avg_slow_ms']:.2f}ms avg")


def example_async_processor():
    """Demonstrate async document processor"""
    print("\n" + "="*80)
    print("ASYNC DOCUMENT PROCESSOR EXAMPLE")
    print("="*80)

    from core.utils.async_processor import AsyncDocumentProcessor

    processor = AsyncDocumentProcessor(
        chunk_size=1000,  # Small chunks for demo
        max_workers=2,
        overlap_size=50
    )

    # Create a large document
    large_doc = "This is a test sentence. " * 500  # ~12KB

    print(f"\nProcessing document: {len(large_doc)} characters")

    # Simple validation function
    def validate_chunk(text: str) -> dict:
        time.sleep(0.05)  # Simulate processing
        return {
            'status': 'PASS',
            'word_count': len(text.split()),
            'char_count': len(text)
        }

    # Progress callback
    def progress(current, total):
        print(f"  Progress: {current}/{total} chunks")

    # Process document
    start = time.time()
    result = processor.process_large_document(
        text=large_doc,
        processor_func=validate_chunk,
        auto_chunk=True,
        aggregation_strategy='merge',
        progress_callback=progress
    )

    print(f"\nProcessing completed:")
    print(f"  Time: {result['processing_time_ms']:.2f}ms")
    print(f"  Chunked: {result['chunked']}")
    if result['chunked']:
        print(f"  Chunks: {result['chunk_count']}")
    print(f"  Status: {result.get('overall_status', 'N/A')}")


def example_circuit_breaker():
    """Demonstrate circuit breaker"""
    print("\n" + "="*80)
    print("CIRCUIT BREAKER EXAMPLE")
    print("="*80)

    from core.utils.circuit_breaker import (
        get_circuit_breaker,
        with_circuit_breaker,
        CircuitBreakerError
    )

    # Simulate an unreliable API
    call_count = [0]

    @with_circuit_breaker(
        name='demo_api',
        failure_threshold=3,
        timeout_seconds=5,
        success_threshold=2
    )
    def unreliable_api_call():
        call_count[0] += 1
        # Fail first 3 calls, then succeed
        if call_count[0] <= 3:
            raise Exception("API Error")
        return "Success"

    print("\nSimulating API calls...")

    # Try calling the API
    for i in range(10):
        try:
            result = unreliable_api_call()
            print(f"  Call {i+1}: {result}")
        except CircuitBreakerError as e:
            print(f"  Call {i+1}: Circuit breaker OPEN - {e}")
        except Exception as e:
            print(f"  Call {i+1}: Failed - {e}")

        time.sleep(0.5)

    # Check circuit state
    breaker = get_circuit_breaker('demo_api')
    state = breaker.get_state()
    print(f"\nCircuit breaker state:")
    print(f"  State: {state['state']}")
    print(f"  Failures: {state['failure_count']}/{state['failure_threshold']}")
    print(f"  Success: {state['success_count']}/{state['success_threshold']}")


def example_optimized_engine():
    """Demonstrate optimized engine usage"""
    print("\n" + "="*80)
    print("OPTIMIZED ENGINE EXAMPLE")
    print("="*80)

    from core.engine_optimized import LOKIEngineOptimized

    # Initialize with all optimizations
    engine = LOKIEngineOptimized(
        enable_caching=True,
        enable_profiling=True
    )

    print("\nEngine initialized with optimizations enabled")

    # Simulate document validation
    test_doc = """
    This is a test privacy notice document.
    We collect your personal information including name and email.
    Your data will be processed in accordance with GDPR.
    """

    print("\nFirst validation (cache miss):")
    start = time.time()
    result1 = engine.check_document(
        text=test_doc,
        document_type='privacy_notice',
        active_modules=[]
    )
    time1 = (time.time() - start) * 1000
    print(f"  Time: {time1:.2f}ms")
    print(f"  Status: {result1.get('overall_risk', 'N/A')}")
    print(f"  Cached: {result1.get('cached', False)}")

    print("\nSecond validation (cache hit):")
    start = time.time()
    result2 = engine.check_document(
        text=test_doc,
        document_type='privacy_notice',
        active_modules=[]
    )
    time2 = (time.time() - start) * 1000
    print(f"  Time: {time2:.2f}ms")
    print(f"  Status: {result2.get('overall_risk', 'N/A')}")
    print(f"  Cached: {result2.get('cached', False)}")

    print(f"\nPerformance improvement: {((time1 - time2) / time1 * 100):.1f}% faster")

    # Get performance stats
    stats = engine.get_performance_stats()
    print(f"\nEngine statistics:")
    print(f"  Total validations: {stats['total_validations']}")
    print(f"  Cache hits: {stats['cache_hits']}")
    print(f"  Cache misses: {stats['cache_misses']}")
    if 'cache' in stats:
        print(f"  Cache hit rate: {stats['cache']['hit_rate']:.1f}%")


def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("LOKI INTERCEPTOR - PERFORMANCE OPTIMIZATION EXAMPLES")
    print("="*80)

    try:
        example_cache_usage()
    except Exception as e:
        print(f"Cache example error: {e}")

    try:
        example_profiler_usage()
    except Exception as e:
        print(f"Profiler example error: {e}")

    try:
        example_async_processor()
    except Exception as e:
        print(f"Async processor example error: {e}")

    try:
        example_circuit_breaker()
    except Exception as e:
        print(f"Circuit breaker example error: {e}")

    try:
        example_optimized_engine()
    except Exception as e:
        print(f"Optimized engine example error: {e}")

    print("\n" + "="*80)
    print("Examples completed!")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
