"""
Circuit breaker pattern implementation for external API calls
Provides resilience and prevents cascade failures in LOKI Interceptor
"""

import time
import threading
from typing import Callable, Any, Optional, Dict
from enum import Enum
from functools import wraps
from datetime import datetime


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failures detected, rejecting calls
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreakerError(Exception):
    """Raised when circuit is open"""
    pass


class CircuitBreaker:
    """
    Circuit breaker for protecting external API calls

    States:
    - CLOSED: Normal operation, calls pass through
    - OPEN: Too many failures, calls rejected immediately
    - HALF_OPEN: Testing recovery, limited calls allowed

    Features:
    - Automatic state transitions
    - Failure threshold configuration
    - Timeout-based recovery
    - Success threshold for half-open state
    - Thread-safe operations
    - Metrics collection
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
        success_threshold: int = 2,
        expected_exception: type = Exception
    ):
        """
        Initialize circuit breaker

        Args:
            name: Circuit breaker identifier
            failure_threshold: Number of failures before opening circuit
            timeout_seconds: Time to wait before attempting recovery
            success_threshold: Successful calls needed in half-open to close circuit
            expected_exception: Exception type to catch (default: Exception)
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.success_threshold = success_threshold
        self.expected_exception = expected_exception

        # State management
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.opened_at: Optional[float] = None

        # Metrics
        self.metrics = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'rejected_calls': 0,
            'state_changes': 0
        }

        # Thread safety
        self._lock = threading.RLock()

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection

        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            CircuitBreakerError: If circuit is open
            Exception: If function raises and circuit allows it
        """
        with self._lock:
            self.metrics['total_calls'] += 1

            # Check if we should allow the call
            if self.state == CircuitState.OPEN:
                # Check if timeout has elapsed
                if self._should_attempt_reset():
                    self._transition_to_half_open()
                else:
                    self.metrics['rejected_calls'] += 1
                    raise CircuitBreakerError(
                        f"Circuit breaker '{self.name}' is OPEN. "
                        f"Wait {self._time_until_retry():.1f}s before retry."
                    )

            # In CLOSED or HALF_OPEN state, attempt the call
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise e

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.opened_at is None:
            return True
        return (time.time() - self.opened_at) >= self.timeout_seconds

    def _time_until_retry(self) -> float:
        """Calculate time until retry is allowed"""
        if self.opened_at is None:
            return 0.0
        elapsed = time.time() - self.opened_at
        remaining = self.timeout_seconds - elapsed
        return max(0.0, remaining)

    def _on_success(self):
        """Handle successful call"""
        with self._lock:
            self.metrics['successful_calls'] += 1

            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.success_threshold:
                    self._transition_to_closed()
            elif self.state == CircuitState.CLOSED:
                # Reset failure count on success
                self.failure_count = 0

    def _on_failure(self):
        """Handle failed call"""
        with self._lock:
            self.metrics['failed_calls'] += 1
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.state == CircuitState.HALF_OPEN:
                # Failure in half-open immediately opens circuit again
                self._transition_to_open()
            elif self.state == CircuitState.CLOSED:
                if self.failure_count >= self.failure_threshold:
                    self._transition_to_open()

    def _transition_to_open(self):
        """Transition to OPEN state"""
        with self._lock:
            if self.state != CircuitState.OPEN:
                print(f"[CircuitBreaker:{self.name}] Transitioning to OPEN state "
                      f"after {self.failure_count} failures")
                self.state = CircuitState.OPEN
                self.opened_at = time.time()
                self.success_count = 0
                self.metrics['state_changes'] += 1

    def _transition_to_half_open(self):
        """Transition to HALF_OPEN state"""
        with self._lock:
            if self.state != CircuitState.HALF_OPEN:
                print(f"[CircuitBreaker:{self.name}] Transitioning to HALF_OPEN state "
                      f"(testing recovery)")
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                self.failure_count = 0
                self.metrics['state_changes'] += 1

    def _transition_to_closed(self):
        """Transition to CLOSED state"""
        with self._lock:
            if self.state != CircuitState.CLOSED:
                print(f"[CircuitBreaker:{self.name}] Transitioning to CLOSED state "
                      f"(service recovered)")
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                self.opened_at = None
                self.metrics['state_changes'] += 1

    def get_state(self) -> Dict[str, Any]:
        """
        Get current circuit breaker state

        Returns:
            State dictionary with current status
        """
        with self._lock:
            return {
                'name': self.name,
                'state': self.state.value,
                'failure_count': self.failure_count,
                'success_count': self.success_count,
                'failure_threshold': self.failure_threshold,
                'success_threshold': self.success_threshold,
                'timeout_seconds': self.timeout_seconds,
                'time_until_retry': self._time_until_retry() if self.state == CircuitState.OPEN else 0,
                'metrics': dict(self.metrics)
            }

    def reset(self):
        """Manually reset circuit breaker to closed state"""
        with self._lock:
            print(f"[CircuitBreaker:{self.name}] Manual reset to CLOSED state")
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.opened_at = None
            self.last_failure_time = None

    def is_closed(self) -> bool:
        """Check if circuit is closed (accepting calls)"""
        with self._lock:
            return self.state == CircuitState.CLOSED

    def is_open(self) -> bool:
        """Check if circuit is open (rejecting calls)"""
        with self._lock:
            return self.state == CircuitState.OPEN


class CircuitBreakerRegistry:
    """
    Global registry for managing multiple circuit breakers
    """

    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
        self._lock = threading.RLock()

    def get_or_create(
        self,
        name: str,
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
        success_threshold: int = 2
    ) -> CircuitBreaker:
        """
        Get existing circuit breaker or create new one

        Args:
            name: Circuit breaker name
            failure_threshold: Failures before opening
            timeout_seconds: Recovery timeout
            success_threshold: Successes needed to close

        Returns:
            CircuitBreaker instance
        """
        with self._lock:
            if name not in self.breakers:
                self.breakers[name] = CircuitBreaker(
                    name=name,
                    failure_threshold=failure_threshold,
                    timeout_seconds=timeout_seconds,
                    success_threshold=success_threshold
                )
            return self.breakers[name]

    def get(self, name: str) -> Optional[CircuitBreaker]:
        """Get circuit breaker by name"""
        with self._lock:
            return self.breakers.get(name)

    def get_all_states(self) -> Dict[str, Dict[str, Any]]:
        """Get states of all registered circuit breakers"""
        with self._lock:
            return {
                name: breaker.get_state()
                for name, breaker in self.breakers.items()
            }

    def reset_all(self):
        """Reset all circuit breakers"""
        with self._lock:
            for breaker in self.breakers.values():
                breaker.reset()


# Global registry instance
_global_registry = CircuitBreakerRegistry()


def get_circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    timeout_seconds: int = 60,
    success_threshold: int = 2
) -> CircuitBreaker:
    """
    Get or create a circuit breaker from global registry

    Args:
        name: Circuit breaker name
        failure_threshold: Failures before opening
        timeout_seconds: Recovery timeout
        success_threshold: Successes needed to close

    Returns:
        CircuitBreaker instance
    """
    return _global_registry.get_or_create(
        name=name,
        failure_threshold=failure_threshold,
        timeout_seconds=timeout_seconds,
        success_threshold=success_threshold
    )


def with_circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    timeout_seconds: int = 60,
    success_threshold: int = 2,
    fallback: Optional[Callable] = None
):
    """
    Decorator for protecting functions with circuit breaker

    Args:
        name: Circuit breaker name
        failure_threshold: Failures before opening
        timeout_seconds: Recovery timeout
        success_threshold: Successes needed to close
        fallback: Optional fallback function if circuit is open

    Returns:
        Decorated function

    Example:
        @with_circuit_breaker('claude_api', failure_threshold=3, timeout_seconds=30)
        def call_claude_api(prompt: str) -> str:
            # ... API call
            return response
    """
    def decorator(func: Callable) -> Callable:
        breaker = get_circuit_breaker(
            name=name,
            failure_threshold=failure_threshold,
            timeout_seconds=timeout_seconds,
            success_threshold=success_threshold
        )

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return breaker.call(func, *args, **kwargs)
            except CircuitBreakerError as e:
                if fallback:
                    print(f"[CircuitBreaker:{name}] Using fallback due to: {e}")
                    return fallback(*args, **kwargs)
                raise

        return wrapper
    return decorator


class RateLimiter:
    """
    Simple token bucket rate limiter

    Prevents overwhelming external APIs with too many concurrent requests
    """

    def __init__(self, rate: int, per_seconds: float = 1.0):
        """
        Initialize rate limiter

        Args:
            rate: Number of allowed calls
            per_seconds: Time window in seconds
        """
        self.rate = rate
        self.per_seconds = per_seconds
        self.allowance = rate
        self.last_check = time.time()
        self._lock = threading.RLock()

    def allow_request(self) -> bool:
        """
        Check if request is allowed under rate limit

        Returns:
            True if request is allowed, False otherwise
        """
        with self._lock:
            current = time.time()
            time_passed = current - self.last_check
            self.last_check = current

            # Add tokens based on time passed
            self.allowance += time_passed * (self.rate / self.per_seconds)

            # Cap at maximum rate
            if self.allowance > self.rate:
                self.allowance = self.rate

            # Check if we have tokens available
            if self.allowance < 1.0:
                return False

            # Consume token
            self.allowance -= 1.0
            return True

    def wait_if_needed(self):
        """Block until request is allowed"""
        while not self.allow_request():
            sleep_time = self.per_seconds / self.rate
            time.sleep(sleep_time)
