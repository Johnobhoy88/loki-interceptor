"""
Performance profiling and monitoring utilities for LOKI Interceptor
Provides detailed metrics on execution time, memory usage, and bottleneck identification
"""

import time
import functools
import tracemalloc
from typing import Dict, List, Any, Callable, Optional
from collections import defaultdict
from datetime import datetime
import json
import threading


class PerformanceMetrics:
    """Container for performance measurement data"""

    def __init__(self, name: str):
        self.name = name
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.duration_ms: Optional[float] = None
        self.memory_start: Optional[int] = None
        self.memory_end: Optional[int] = None
        self.memory_peak: Optional[int] = None
        self.memory_delta: Optional[int] = None
        self.metadata: Dict[str, Any] = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            'name': self.name,
            'duration_ms': self.duration_ms,
            'memory_delta_kb': self.memory_delta / 1024 if self.memory_delta else None,
            'memory_peak_mb': self.memory_peak / (1024 * 1024) if self.memory_peak else None,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'metadata': self.metadata
        }


class PerformanceProfiler:
    """
    Enterprise-grade performance profiler with detailed metrics collection

    Features:
    - Execution time tracking
    - Memory usage monitoring
    - Per-operation metrics
    - Aggregated statistics
    - Bottleneck identification
    - Thread-safe operations
    """

    def __init__(self, enable_memory_tracking: bool = True):
        """
        Initialize performance profiler

        Args:
            enable_memory_tracking: Enable memory profiling (adds overhead)
        """
        self.enable_memory_tracking = enable_memory_tracking
        self.metrics_history: List[PerformanceMetrics] = []
        self.operation_stats: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.Lock()

        if self.enable_memory_tracking:
            tracemalloc.start()

    def start_operation(self, name: str) -> PerformanceMetrics:
        """
        Start tracking an operation

        Args:
            name: Operation name/identifier

        Returns:
            PerformanceMetrics instance
        """
        metrics = PerformanceMetrics(name)
        metrics.start_time = time.time()

        if self.enable_memory_tracking:
            try:
                current, peak = tracemalloc.get_traced_memory()
                metrics.memory_start = current
            except Exception:
                pass

        return metrics

    def end_operation(self, metrics: PerformanceMetrics) -> PerformanceMetrics:
        """
        Complete operation tracking

        Args:
            metrics: PerformanceMetrics from start_operation

        Returns:
            Completed PerformanceMetrics with all data
        """
        metrics.end_time = time.time()
        metrics.duration_ms = (metrics.end_time - metrics.start_time) * 1000

        if self.enable_memory_tracking:
            try:
                current, peak = tracemalloc.get_traced_memory()
                metrics.memory_end = current
                metrics.memory_peak = peak
                if metrics.memory_start is not None:
                    metrics.memory_delta = current - metrics.memory_start
            except Exception:
                pass

        # Store metrics
        with self._lock:
            self.metrics_history.append(metrics)
            self.operation_stats[metrics.name].append(metrics.duration_ms)

        return metrics

    def get_operation_stats(self, operation_name: str) -> Dict[str, Any]:
        """
        Get aggregated statistics for an operation

        Args:
            operation_name: Name of operation to analyze

        Returns:
            Dictionary with min, max, avg, count statistics
        """
        with self._lock:
            durations = self.operation_stats.get(operation_name, [])

        if not durations:
            return {
                'operation': operation_name,
                'count': 0,
                'min_ms': None,
                'max_ms': None,
                'avg_ms': None,
                'total_ms': None
            }

        return {
            'operation': operation_name,
            'count': len(durations),
            'min_ms': round(min(durations), 2),
            'max_ms': round(max(durations), 2),
            'avg_ms': round(sum(durations) / len(durations), 2),
            'total_ms': round(sum(durations), 2)
        }

    def get_all_stats(self) -> Dict[str, Any]:
        """
        Get statistics for all tracked operations

        Returns:
            Dictionary mapping operation names to their statistics
        """
        with self._lock:
            operation_names = list(self.operation_stats.keys())

        return {
            'operations': {name: self.get_operation_stats(name) for name in operation_names},
            'total_operations': sum(len(durations) for durations in self.operation_stats.values()),
            'tracked_operation_types': len(operation_names)
        }

    def identify_bottlenecks(self, threshold_ms: float = 100.0) -> List[Dict[str, Any]]:
        """
        Identify slow operations exceeding threshold

        Args:
            threshold_ms: Threshold in milliseconds to flag operations

        Returns:
            List of slow operations with details
        """
        bottlenecks = []

        with self._lock:
            for operation, durations in self.operation_stats.items():
                slow_calls = [d for d in durations if d > threshold_ms]
                if slow_calls:
                    bottlenecks.append({
                        'operation': operation,
                        'slow_calls': len(slow_calls),
                        'total_calls': len(durations),
                        'percentage': round(len(slow_calls) / len(durations) * 100, 2),
                        'avg_slow_ms': round(sum(slow_calls) / len(slow_calls), 2),
                        'max_ms': round(max(slow_calls), 2)
                    })

        # Sort by impact (slow calls * avg duration)
        bottlenecks.sort(
            key=lambda x: x['slow_calls'] * x['avg_slow_ms'],
            reverse=True
        )

        return bottlenecks

    def get_recent_metrics(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most recent performance metrics

        Args:
            limit: Maximum number of metrics to return

        Returns:
            List of recent metrics dictionaries
        """
        with self._lock:
            recent = self.metrics_history[-limit:] if self.metrics_history else []

        return [m.to_dict() for m in recent]

    def clear_history(self) -> None:
        """Clear all stored metrics history"""
        with self._lock:
            self.metrics_history.clear()
            self.operation_stats.clear()

    def generate_report(self) -> str:
        """
        Generate comprehensive performance report

        Returns:
            Formatted performance report string
        """
        stats = self.get_all_stats()
        bottlenecks = self.identify_bottlenecks()

        report = ["=" * 80]
        report.append("LOKI INTERCEPTOR - PERFORMANCE REPORT")
        report.append(f"Generated: {datetime.utcnow().isoformat()}")
        report.append("=" * 80)
        report.append("")

        # Overall statistics
        report.append("OVERALL STATISTICS:")
        report.append(f"  Total operations tracked: {stats['total_operations']}")
        report.append(f"  Operation types: {stats['tracked_operation_types']}")
        report.append("")

        # Per-operation breakdown
        report.append("OPERATION BREAKDOWN:")
        for op_name, op_stats in stats['operations'].items():
            if op_stats['count'] > 0:
                report.append(f"  {op_name}:")
                report.append(f"    Count: {op_stats['count']}")
                report.append(f"    Avg: {op_stats['avg_ms']}ms")
                report.append(f"    Min: {op_stats['min_ms']}ms")
                report.append(f"    Max: {op_stats['max_ms']}ms")
                report.append(f"    Total: {op_stats['total_ms']}ms")
                report.append("")

        # Bottlenecks
        if bottlenecks:
            report.append("IDENTIFIED BOTTLENECKS (>100ms):")
            for idx, bottleneck in enumerate(bottlenecks[:5], 1):
                report.append(f"  {idx}. {bottleneck['operation']}:")
                report.append(f"     Slow calls: {bottleneck['slow_calls']}/{bottleneck['total_calls']} ({bottleneck['percentage']}%)")
                report.append(f"     Avg slow: {bottleneck['avg_slow_ms']}ms")
                report.append(f"     Max: {bottleneck['max_ms']}ms")
                report.append("")
        else:
            report.append("BOTTLENECKS: None identified")
            report.append("")

        report.append("=" * 80)

        return "\n".join(report)

    def export_metrics(self, filepath: str) -> None:
        """
        Export metrics to JSON file

        Args:
            filepath: Path to output file
        """
        data = {
            'generated_at': datetime.utcnow().isoformat(),
            'statistics': self.get_all_stats(),
            'bottlenecks': self.identify_bottlenecks(),
            'recent_metrics': self.get_recent_metrics(limit=100)
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


# Global profiler instance
_global_profiler: Optional[PerformanceProfiler] = None


def get_profiler() -> PerformanceProfiler:
    """
    Get or create global profiler instance

    Returns:
        Global PerformanceProfiler instance
    """
    global _global_profiler

    if _global_profiler is None:
        _global_profiler = PerformanceProfiler()

    return _global_profiler


def profile_function(operation_name: Optional[str] = None):
    """
    Decorator for profiling function execution

    Args:
        operation_name: Custom operation name (defaults to function name)

    Returns:
        Decorated function

    Example:
        @profile_function("document_validation")
        def validate_document(text: str) -> dict:
            # ... processing
            return result
    """
    def decorator(func: Callable) -> Callable:
        op_name = operation_name or func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            profiler = get_profiler()
            metrics = profiler.start_operation(op_name)

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                profiler.end_operation(metrics)

        return wrapper
    return decorator


class ProfileContext:
    """
    Context manager for profiling code blocks

    Example:
        with ProfileContext("expensive_operation") as ctx:
            # ... expensive code
            pass
        print(f"Took {ctx.metrics.duration_ms}ms")
    """

    def __init__(self, operation_name: str, profiler: Optional[PerformanceProfiler] = None):
        """
        Initialize profile context

        Args:
            operation_name: Name for this operation
            profiler: PerformanceProfiler instance (uses global if None)
        """
        self.operation_name = operation_name
        self.profiler = profiler or get_profiler()
        self.metrics: Optional[PerformanceMetrics] = None

    def __enter__(self) -> 'ProfileContext':
        """Start profiling"""
        self.metrics = self.profiler.start_operation(self.operation_name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop profiling"""
        if self.metrics:
            self.profiler.end_operation(self.metrics)
        return False


def benchmark_comparison(func: Callable, inputs: List[tuple], iterations: int = 10) -> Dict[str, Any]:
    """
    Benchmark a function with multiple input sets

    Args:
        func: Function to benchmark
        inputs: List of input tuples (args)
        iterations: Number of iterations per input

    Returns:
        Benchmark results dictionary

    Example:
        results = benchmark_comparison(
            my_function,
            [('input1',), ('input2',)],
            iterations=100
        )
    """
    results = {
        'function': func.__name__,
        'iterations': iterations,
        'inputs': []
    }

    for idx, args in enumerate(inputs):
        timings = []

        for _ in range(iterations):
            start = time.time()
            func(*args)
            duration = (time.time() - start) * 1000
            timings.append(duration)

        results['inputs'].append({
            'input_index': idx,
            'args': str(args)[:100],  # Truncate for readability
            'avg_ms': round(sum(timings) / len(timings), 3),
            'min_ms': round(min(timings), 3),
            'max_ms': round(max(timings), 3),
            'total_ms': round(sum(timings), 3)
        })

    return results
