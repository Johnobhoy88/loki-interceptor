"""
Prometheus metrics for monitoring LOKI in production
"""
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from flask import Response
import time
import os


# Application info
app_info = Info('loki_app', 'LOKI Application Information')
app_info.info({
    'version': os.getenv('APP_VERSION', '1.0.0'),
    'environment': os.getenv('FLASK_ENV', 'production')
})

# Request metrics
request_count = Counter(
    'loki_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'loki_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

request_in_progress = Gauge(
    'loki_requests_in_progress',
    'Number of requests in progress',
    ['method', 'endpoint']
)

# Validation metrics
validation_count = Counter(
    'loki_validations_total',
    'Total number of validations',
    ['module', 'result']
)

validation_duration = Histogram(
    'loki_validation_duration_seconds',
    'Validation duration in seconds',
    ['module'],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0)
)

# Gate metrics
gate_trigger_count = Counter(
    'loki_gate_triggers_total',
    'Total number of gate triggers',
    ['module', 'gate_type', 'severity']
)

# Cache metrics
cache_hit_count = Counter(
    'loki_cache_hits_total',
    'Total number of cache hits'
)

cache_miss_count = Counter(
    'loki_cache_misses_total',
    'Total number of cache misses'
)

cache_size = Gauge(
    'loki_cache_size',
    'Current cache size'
)

# Model metrics
model_request_count = Counter(
    'loki_model_requests_total',
    'Total number of model requests',
    ['provider', 'model']
)

model_error_count = Counter(
    'loki_model_errors_total',
    'Total number of model errors',
    ['provider', 'error_type']
)

model_token_usage = Counter(
    'loki_model_tokens_total',
    'Total number of tokens used',
    ['provider', 'model', 'type']  # type: input/output
)

# Rate limiting metrics
rate_limit_exceeded = Counter(
    'loki_rate_limit_exceeded_total',
    'Total number of rate limit exceeded events',
    ['endpoint']
)

# System metrics
active_modules = Gauge(
    'loki_active_modules',
    'Number of active compliance modules'
)

# Error metrics
error_count = Counter(
    'loki_errors_total',
    'Total number of errors',
    ['type', 'endpoint']
)


class MetricsMiddleware:
    """Flask middleware to track request metrics"""

    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize middleware with Flask app"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_request(self.teardown_request)

        # Store request start time
        self._request_start_time = {}

    def before_request(self):
        """Track request start"""
        from flask import request, g
        g.start_time = time.time()

        # Track in-progress requests
        endpoint = request.endpoint or 'unknown'
        method = request.method
        request_in_progress.labels(method=method, endpoint=endpoint).inc()

    def after_request(self, response):
        """Track request completion"""
        from flask import request, g

        # Calculate duration
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time

            endpoint = request.endpoint or 'unknown'
            method = request.method
            status = response.status_code

            # Record metrics
            request_count.labels(
                method=method,
                endpoint=endpoint,
                status=status
            ).inc()

            request_duration.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

            # Decrement in-progress
            request_in_progress.labels(method=method, endpoint=endpoint).dec()

        return response

    def teardown_request(self, exception=None):
        """Handle request errors"""
        if exception:
            from flask import request
            endpoint = request.endpoint or 'unknown'
            error_type = type(exception).__name__
            error_count.labels(type=error_type, endpoint=endpoint).inc()


def track_validation(module_name: str, result: str, duration: float):
    """Track validation metrics"""
    validation_count.labels(module=module_name, result=result).inc()
    validation_duration.labels(module=module_name).observe(duration)


def track_gate_trigger(module_name: str, gate_type: str, severity: str):
    """Track gate trigger"""
    gate_trigger_count.labels(
        module=module_name,
        gate_type=gate_type,
        severity=severity
    ).inc()


def track_cache_hit():
    """Track cache hit"""
    cache_hit_count.inc()


def track_cache_miss():
    """Track cache miss"""
    cache_miss_count.inc()


def update_cache_size(size: int):
    """Update cache size gauge"""
    cache_size.set(size)


def track_model_request(provider: str, model: str):
    """Track model API request"""
    model_request_count.labels(provider=provider, model=model).inc()


def track_model_error(provider: str, error_type: str):
    """Track model API error"""
    model_error_count.labels(provider=provider, error_type=error_type).inc()


def track_token_usage(provider: str, model: str, input_tokens: int, output_tokens: int):
    """Track token usage"""
    model_token_usage.labels(provider=provider, model=model, type='input').inc(input_tokens)
    model_token_usage.labels(provider=provider, model=model, type='output').inc(output_tokens)


def track_rate_limit_exceeded(endpoint: str):
    """Track rate limit exceeded"""
    rate_limit_exceeded.labels(endpoint=endpoint).inc()


def update_active_modules(count: int):
    """Update active modules count"""
    active_modules.set(count)


def metrics_endpoint():
    """Endpoint to expose Prometheus metrics"""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
