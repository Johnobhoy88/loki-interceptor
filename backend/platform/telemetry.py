"""
Telemetry and Monitoring Integration
Comprehensive observability with metrics, tracing, and logging
"""

import time
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict, deque
from contextlib import contextmanager
import json

logger = logging.getLogger(__name__)


@dataclass
class Metric:
    """Metric data point"""
    name: str
    value: float
    tags: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metric_type: str = "gauge"  # gauge, counter, histogram


@dataclass
class Span:
    """Distributed tracing span"""
    name: str
    trace_id: str
    span_id: str
    parent_id: Optional[str] = None
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    duration: Optional[float] = None
    tags: Dict[str, str] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "ok"  # ok, error

    def finish(self):
        """Finish the span"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time


class TelemetrySystem:
    """
    Comprehensive Telemetry and Monitoring System
    Provides metrics collection, distributed tracing, and structured logging
    """

    def __init__(self, config):
        """
        Initialize telemetry system

        Args:
            config: PlatformConfig instance
        """
        self.config = config
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.active_spans: Dict[str, Span] = {}
        self.completed_spans: deque = deque(maxlen=1000)
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = defaultdict(list)

        # Performance tracking
        self.request_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
        self.latencies: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))

    # Metrics Methods

    def record_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None, metric_type: str = "gauge"):
        """
        Record a metric

        Args:
            name: Metric name
            value: Metric value
            tags: Optional tags
            metric_type: Type of metric (gauge, counter, histogram)
        """
        metric = Metric(
            name=name,
            value=value,
            tags=tags or {},
            metric_type=metric_type
        )

        self.metrics[name].append(metric)

        # Update aggregated values
        if metric_type == "counter":
            self.counters[name] += value
        elif metric_type == "gauge":
            self.gauges[name] = value
        elif metric_type == "histogram":
            self.histograms[name].append(value)

    def increment(self, name: str, value: float = 1.0, tags: Optional[Dict[str, str]] = None):
        """Increment a counter"""
        self.record_metric(name, value, tags, metric_type="counter")

    def gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Set a gauge value"""
        self.record_metric(name, value, tags, metric_type="gauge")

    def histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a histogram value"""
        self.record_metric(name, value, tags, metric_type="histogram")

    def get_metric(self, name: str, last_n: Optional[int] = None) -> List[Metric]:
        """Get metric history"""
        if name not in self.metrics:
            return []

        metrics = list(self.metrics[name])
        if last_n:
            return metrics[-last_n:]
        return metrics

    def get_counter(self, name: str) -> float:
        """Get counter value"""
        return self.counters.get(name, 0.0)

    def get_gauge(self, name: str) -> Optional[float]:
        """Get gauge value"""
        return self.gauges.get(name)

    def get_histogram_stats(self, name: str) -> Dict[str, float]:
        """Get histogram statistics"""
        if name not in self.histograms or not self.histograms[name]:
            return {}

        values = sorted(self.histograms[name])
        count = len(values)

        return {
            'count': count,
            'min': values[0],
            'max': values[-1],
            'mean': sum(values) / count,
            'median': values[count // 2],
            'p95': values[int(count * 0.95)] if count > 0 else 0,
            'p99': values[int(count * 0.99)] if count > 0 else 0,
        }

    # Tracing Methods

    def start_span(self, name: str, trace_id: str, span_id: str, parent_id: Optional[str] = None, tags: Optional[Dict[str, str]] = None) -> Span:
        """
        Start a new trace span

        Args:
            name: Span name
            trace_id: Trace ID
            span_id: Span ID
            parent_id: Optional parent span ID
            tags: Optional tags

        Returns:
            Created Span
        """
        span = Span(
            name=name,
            trace_id=trace_id,
            span_id=span_id,
            parent_id=parent_id,
            tags=tags or {}
        )

        self.active_spans[span_id] = span
        return span

    def finish_span(self, span_id: str, status: str = "ok"):
        """
        Finish a trace span

        Args:
            span_id: Span ID
            status: Span status (ok or error)
        """
        if span_id not in self.active_spans:
            logger.warning(f"Span not found: {span_id}")
            return

        span = self.active_spans[span_id]
        span.status = status
        span.finish()

        # Move to completed spans
        self.completed_spans.append(span)
        del self.active_spans[span_id]

        # Record latency metric
        self.histogram(f"span.{span.name}.duration", span.duration * 1000, {"status": status})

    def add_span_log(self, span_id: str, event: str, **kwargs):
        """
        Add a log entry to a span

        Args:
            span_id: Span ID
            event: Event name
            **kwargs: Additional data
        """
        if span_id not in self.active_spans:
            return

        span = self.active_spans[span_id]
        span.logs.append({
            'timestamp': time.time(),
            'event': event,
            **kwargs
        })

    @contextmanager
    def trace(self, name: str, trace_id: Optional[str] = None, parent_id: Optional[str] = None, tags: Optional[Dict[str, str]] = None):
        """
        Context manager for tracing

        Args:
            name: Span name
            trace_id: Optional trace ID (generated if not provided)
            parent_id: Optional parent span ID
            tags: Optional tags

        Yields:
            Span object
        """
        import uuid

        trace_id = trace_id or str(uuid.uuid4())
        span_id = str(uuid.uuid4())

        span = self.start_span(name, trace_id, span_id, parent_id, tags)

        try:
            yield span
            self.finish_span(span_id, status="ok")
        except Exception as e:
            self.finish_span(span_id, status="error")
            self.add_span_log(span_id, "error", error=str(e))
            raise

    # Request Tracking

    def record_request(self, endpoint: str, method: str, status_code: int, duration: float):
        """
        Record API request metrics

        Args:
            endpoint: API endpoint
            method: HTTP method
            status_code: Response status code
            duration: Request duration in seconds
        """
        tags = {
            'endpoint': endpoint,
            'method': method,
            'status': str(status_code)
        }

        # Increment request counter
        self.increment('http.requests.total', tags=tags)

        # Record duration
        self.histogram('http.request.duration', duration * 1000, tags=tags)

        # Track by endpoint
        self.request_counts[endpoint] += 1
        self.latencies[endpoint].append(duration)

        # Track errors
        if status_code >= 400:
            self.increment('http.requests.errors', tags=tags)
            self.error_counts[endpoint] += 1

    def record_compliance_check(self, module: str, gate: str, duration: float, passed: bool):
        """
        Record compliance check metrics

        Args:
            module: Compliance module name
            gate: Gate name
            duration: Check duration in seconds
            passed: Whether check passed
        """
        tags = {
            'module': module,
            'gate': gate,
            'result': 'pass' if passed else 'fail'
        }

        self.increment('compliance.checks.total', tags=tags)
        self.histogram('compliance.check.duration', duration * 1000, tags=tags)

    def record_cache_operation(self, operation: str, hit: bool, duration: float):
        """
        Record cache operation metrics

        Args:
            operation: Operation type (get, set, delete)
            hit: Whether operation was a cache hit
            duration: Operation duration in seconds
        """
        tags = {
            'operation': operation,
            'result': 'hit' if hit else 'miss'
        }

        self.increment('cache.operations.total', tags=tags)
        self.histogram('cache.operation.duration', duration * 1000, tags=tags)

    def record_database_query(self, query_type: str, duration: float, success: bool):
        """
        Record database query metrics

        Args:
            query_type: Type of query (select, insert, update, delete)
            duration: Query duration in seconds
            success: Whether query succeeded
        """
        tags = {
            'query_type': query_type,
            'result': 'success' if success else 'error'
        }

        self.increment('db.queries.total', tags=tags)
        self.histogram('db.query.duration', duration * 1000, tags=tags)

    # System Metrics

    def record_system_metrics(self):
        """Record system resource metrics"""
        try:
            import psutil

            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.gauge('system.cpu.percent', cpu_percent)

            # Memory
            memory = psutil.virtual_memory()
            self.gauge('system.memory.percent', memory.percent)
            self.gauge('system.memory.used', memory.used)
            self.gauge('system.memory.available', memory.available)

            # Disk
            disk = psutil.disk_usage('/')
            self.gauge('system.disk.percent', disk.percent)
            self.gauge('system.disk.used', disk.used)
            self.gauge('system.disk.free', disk.free)

            # Network (if available)
            network = psutil.net_io_counters()
            self.increment('system.network.bytes_sent', network.bytes_sent)
            self.increment('system.network.bytes_recv', network.bytes_recv)

        except Exception as e:
            logger.error(f"Error recording system metrics: {e}")

    # Analytics and Reporting

    def get_endpoint_stats(self, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """
        Get endpoint statistics

        Args:
            endpoint: Optional specific endpoint (None for all)

        Returns:
            Statistics dictionary
        """
        if endpoint:
            count = self.request_counts.get(endpoint, 0)
            errors = self.error_counts.get(endpoint, 0)
            latencies = list(self.latencies.get(endpoint, []))

            if not latencies:
                return {
                    'endpoint': endpoint,
                    'requests': count,
                    'errors': errors,
                }

            sorted_latencies = sorted(latencies)
            n = len(sorted_latencies)

            return {
                'endpoint': endpoint,
                'requests': count,
                'errors': errors,
                'error_rate': errors / count if count > 0 else 0,
                'latency': {
                    'min': sorted_latencies[0],
                    'max': sorted_latencies[-1],
                    'mean': sum(sorted_latencies) / n,
                    'median': sorted_latencies[n // 2],
                    'p95': sorted_latencies[int(n * 0.95)] if n > 0 else 0,
                    'p99': sorted_latencies[int(n * 0.99)] if n > 0 else 0,
                }
            }

        # Return stats for all endpoints
        return {
            endpoint: self.get_endpoint_stats(endpoint)
            for endpoint in self.request_counts.keys()
        }

    def get_summary(self) -> Dict[str, Any]:
        """Get telemetry summary"""
        return {
            'metrics': {
                'total': sum(len(m) for m in self.metrics.values()),
                'counters': len(self.counters),
                'gauges': len(self.gauges),
                'histograms': len(self.histograms),
            },
            'traces': {
                'active': len(self.active_spans),
                'completed': len(self.completed_spans),
            },
            'requests': {
                'total': sum(self.request_counts.values()),
                'errors': sum(self.error_counts.values()),
                'endpoints': len(self.request_counts),
            },
            'top_endpoints': self._get_top_endpoints(5),
        }

    def _get_top_endpoints(self, n: int) -> List[Dict[str, Any]]:
        """Get top N endpoints by request count"""
        sorted_endpoints = sorted(
            self.request_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:n]

        return [
            {
                'endpoint': endpoint,
                'requests': count,
                'errors': self.error_counts.get(endpoint, 0),
            }
            for endpoint, count in sorted_endpoints
        ]

    def export_metrics(self) -> Dict[str, Any]:
        """Export all metrics"""
        return {
            'counters': dict(self.counters),
            'gauges': dict(self.gauges),
            'histograms': {
                name: self.get_histogram_stats(name)
                for name in self.histograms.keys()
            },
            'timestamp': datetime.utcnow().isoformat(),
        }

    def reset_metrics(self):
        """Reset all metrics (useful for testing)"""
        self.metrics.clear()
        self.counters.clear()
        self.gauges.clear()
        self.histograms.clear()
        self.request_counts.clear()
        self.error_counts.clear()
        self.latencies.clear()
        logger.info("Metrics reset")
