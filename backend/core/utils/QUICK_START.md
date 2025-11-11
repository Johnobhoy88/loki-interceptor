# LOKI Performance Utilities - Quick Start Guide

## Installation

```bash
pip install fakeredis redis
```

## 5-Minute Quick Start

### 1. Use Optimized Engine (Easiest)

```python
from core.engine_optimized import LOKIEngineOptimized

# Drop-in replacement for standard engine
engine = LOKIEngineOptimized(
    enable_caching=True,      # 99% faster for repeated docs
    enable_profiling=True     # Track performance metrics
)

# Use exactly like standard engine
result = engine.check_document(
    text="Your document text...",
    document_type='privacy_notice',
    active_modules=['gdpr_compliance']
)

# Check performance
stats = engine.get_performance_stats()
print(f"Cache hit rate: {stats['cache']['hit_rate']}%")
```

### 2. Add Caching to Existing Functions

```python
from core.utils.cache_manager import cache_result

@cache_result(ttl=300, namespace="validation")
def expensive_validation(text: str) -> dict:
    # Your expensive logic here
    return result

# First call: slow (cache miss)
result1 = expensive_validation("document")

# Second call: fast (cache hit)
result2 = expensive_validation("document")
```

### 3. Profile Slow Operations

```python
from core.utils.profiler import profile_function

@profile_function("document_processing")
def process_document(text: str) -> dict:
    # Your processing logic
    return result

# After running, check stats
from core.utils.profiler import get_profiler
profiler = get_profiler()
stats = profiler.get_operation_stats("document_processing")
print(f"Average time: {stats['avg_ms']}ms")

# Find bottlenecks
bottlenecks = profiler.identify_bottlenecks(threshold_ms=100)
for bn in bottlenecks:
    print(f"{bn['operation']}: {bn['avg_slow_ms']}ms")
```

### 4. Process Large Documents

```python
from core.utils.async_processor import AsyncDocumentProcessor

processor = AsyncDocumentProcessor(
    chunk_size=50000,    # 50KB chunks
    max_workers=4        # 4 parallel workers
)

# Automatically chunks and processes in parallel
result = processor.process_large_document(
    text=large_document,
    processor_func=your_validation_function,
    auto_chunk=True
)

print(f"Processed {result['chunk_count']} chunks in {result['processing_time_ms']}ms")
```

### 5. Protect API Calls

```python
from core.utils.circuit_breaker import with_circuit_breaker

@with_circuit_breaker(
    name='claude_api',
    failure_threshold=3,      # Open after 3 failures
    timeout_seconds=30        # Wait 30s before retry
)
def call_claude(prompt: str) -> str:
    # Your API call here
    return response

# Automatically handles failures and prevents cascade
try:
    result = call_claude("prompt")
except CircuitBreakerError:
    # Circuit is open, use fallback
    result = fallback_response()
```

## Common Patterns

### Pattern 1: Cached Validation Pipeline

```python
from core.engine_optimized import LOKIEngineOptimized
from core.utils.profiler import ProfileContext

engine = LOKIEngineOptimized(enable_caching=True, enable_profiling=True)

with ProfileContext("full_pipeline") as ctx:
    result = engine.check_document(text, doc_type, modules)

if result.get('cached'):
    print(f"Cache hit! Took {ctx.metrics.duration_ms}ms")
else:
    print(f"Cache miss. Took {ctx.metrics.duration_ms}ms")
```

### Pattern 2: Large Document with Progress

```python
from core.utils.async_processor import AsyncDocumentProcessor

def progress_callback(current, total):
    print(f"Progress: {current}/{total} ({current/total*100:.1f}%)")

processor = AsyncDocumentProcessor(max_workers=4)
result = processor.process_large_document(
    text=large_doc,
    processor_func=validate_chunk,
    progress_callback=progress_callback
)
```

### Pattern 3: Resilient API Call

```python
from core.providers_optimized import ProviderRouterOptimized

router = ProviderRouterOptimized(enable_circuit_breakers=True)
router.configure_provider('anthropic', api_key='...')

# Automatic retry with exponential backoff
response = router.call_provider(
    provider_name='anthropic',
    prompt='Analyze this...',
    max_retries=2  # Will retry 2 times
)

# Check health
health = router.health_check()
if not health['healthy']:
    print("WARNING: Some providers unhealthy")
```

## Performance Tips

### Tip 1: Enable Caching for Repeated Documents
- Templates, standard policies, repeated validations
- Target hit rate: >70%
- TTL: 30-60 minutes for most use cases

### Tip 2: Use Chunking for Large Documents
- >100KB: Consider chunking
- >500KB: Always chunk
- >5MB: Chunk with 8+ workers

### Tip 3: Monitor Bottlenecks
```python
profiler = get_profiler()
report = profiler.generate_report()
print(report)  # Shows bottlenecks >100ms
```

### Tip 4: Configure Redis for Production
```bash
export REDIS_URL=redis://localhost:6379/0
```

### Tip 5: Disable Profiling in Production (if needed)
```python
engine = LOKIEngineOptimized(
    enable_caching=True,
    enable_profiling=False  # Saves ~1-2% CPU
)
```

## Troubleshooting

### Problem: Low cache hit rate (<50%)
**Solution**: Check if documents are truly similar, verify TTL isn't too short

### Problem: High memory usage
**Solution**: Reduce cache size, lower TTL, enable chunking for large docs

### Problem: Circuit breaker always open
**Solution**: Check network, verify credentials, review failure threshold

### Problem: Slow performance despite caching
**Solution**: Run profiler, check bottlenecks, verify cache backend

## Monitoring Dashboard (Quick)

```python
from core.engine_optimized import LOKIEngineOptimized

engine = LOKIEngineOptimized(enable_caching=True, enable_profiling=True)

# After running validations...
def print_dashboard():
    stats = engine.get_performance_stats()

    print("=" * 60)
    print("LOKI PERFORMANCE DASHBOARD")
    print("=" * 60)

    print(f"\nValidations: {stats['total_validations']}")
    print(f"Cache hits: {stats['cache_hits']}")
    print(f"Cache misses: {stats['cache_misses']}")
    print(f"Hit rate: {stats['cache']['hit_rate']}%")

    print("\nTop Operations:")
    for op_name, op_stats in list(stats['profiling']['operations'].items())[:5]:
        print(f"  {op_name}: {op_stats['avg_ms']:.2f}ms avg")

    print("=" * 60)

# Call periodically
print_dashboard()
```

## Examples

See `/backend/core/utils/example_usage.py` for complete working examples.

Run examples:
```bash
cd backend
python -m core.utils.example_usage
```

## Full Documentation

- **Complete Guide**: `/PERFORMANCE_OPTIMIZATION.md`
- **Implementation Summary**: `/PERFORMANCE_IMPLEMENTATION_SUMMARY.md`
- **Code Examples**: `/backend/core/utils/example_usage.py`

---

**Quick Reference:**
- `engine_optimized.py` → Drop-in optimized engine
- `cache_manager.py` → Caching utilities
- `profiler.py` → Performance monitoring
- `async_processor.py` → Large document handling
- `circuit_breaker.py` → API resilience
- `providers_optimized.py` → Resilient API router
