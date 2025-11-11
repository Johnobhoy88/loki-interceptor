"""
Unified Error Handling and Recovery System
Provides graceful error handling with self-healing capabilities
"""

import logging
import traceback
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import asyncio

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryStrategy(Enum):
    """Error recovery strategies"""
    RETRY = "retry"
    FALLBACK = "fallback"
    CIRCUIT_BREAK = "circuit_break"
    IGNORE = "ignore"
    ALERT = "alert"


@dataclass
class ErrorEvent:
    """Error event record"""
    error_type: str
    message: str
    severity: ErrorSeverity
    timestamp: datetime = field(default_factory=datetime.utcnow)
    context: Dict[str, Any] = field(default_factory=dict)
    traceback: Optional[str] = None
    recovery_attempted: bool = False
    recovery_successful: bool = False
    recovery_strategy: Optional[RecoveryStrategy] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'error_type': self.error_type,
            'message': self.message,
            'severity': self.severity.value,
            'timestamp': self.timestamp.isoformat(),
            'context': self.context,
            'traceback': self.traceback,
            'recovery_attempted': self.recovery_attempted,
            'recovery_successful': self.recovery_successful,
            'recovery_strategy': self.recovery_strategy.value if self.recovery_strategy else None,
        }


@dataclass
class CircuitBreaker:
    """Circuit breaker for a service"""
    name: str
    failure_threshold: int = 5
    timeout: int = 60  # seconds
    failures: int = 0
    last_failure_time: Optional[datetime] = None
    state: str = "closed"  # closed, open, half_open

    def record_failure(self):
        """Record a failure"""
        self.failures += 1
        self.last_failure_time = datetime.utcnow()

        if self.failures >= self.failure_threshold:
            self.state = "open"
            logger.warning(f"Circuit breaker {self.name} opened after {self.failures} failures")

    def record_success(self):
        """Record a success"""
        self.failures = 0
        self.state = "closed"

    def can_attempt(self) -> bool:
        """Check if attempt is allowed"""
        if self.state == "closed":
            return True

        if self.state == "open":
            # Check if timeout has elapsed
            if self.last_failure_time and (datetime.utcnow() - self.last_failure_time).total_seconds() > self.timeout:
                self.state = "half_open"
                logger.info(f"Circuit breaker {self.name} entering half-open state")
                return True
            return False

        # half_open state
        return True


class ErrorHandler:
    """
    Unified Error Handling and Recovery System
    Provides graceful degradation and self-healing capabilities
    """

    def __init__(self, config):
        """
        Initialize error handler

        Args:
            config: PlatformConfig instance
        """
        self.config = config
        self.error_history: deque = deque(maxlen=1000)
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.recovery_handlers: Dict[str, Callable] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.fallback_handlers: Dict[str, Callable] = {}
        self.alert_handlers: List[Callable] = []

        # Error rate tracking
        self.error_rates: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.last_alert_times: Dict[str, datetime] = {}

    def register_recovery_handler(self, error_type: str, handler: Callable, strategy: RecoveryStrategy = RecoveryStrategy.RETRY):
        """
        Register a recovery handler for an error type

        Args:
            error_type: Error type to handle
            handler: Recovery handler function
            strategy: Recovery strategy
        """
        self.recovery_handlers[error_type] = (handler, strategy)
        logger.info(f"Registered recovery handler for {error_type} with strategy {strategy.value}")

    def register_fallback_handler(self, service: str, handler: Callable):
        """
        Register a fallback handler for a service

        Args:
            service: Service name
            handler: Fallback handler function
        """
        self.fallback_handlers[service] = handler
        logger.info(f"Registered fallback handler for {service}")

    def register_alert_handler(self, handler: Callable):
        """
        Register an alert handler

        Args:
            handler: Alert handler function (called for critical errors)
        """
        self.alert_handlers.append(handler)
        logger.info("Registered alert handler")

    def get_circuit_breaker(self, service: str, **kwargs) -> CircuitBreaker:
        """
        Get or create circuit breaker for a service

        Args:
            service: Service name
            **kwargs: Circuit breaker configuration

        Returns:
            CircuitBreaker instance
        """
        if service not in self.circuit_breakers:
            self.circuit_breakers[service] = CircuitBreaker(
                name=service,
                **kwargs
            )

        return self.circuit_breakers[service]

    async def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        attempt_recovery: bool = True
    ) -> Optional[Any]:
        """
        Handle an error with optional recovery

        Args:
            error: The exception
            context: Optional error context
            severity: Error severity
            attempt_recovery: Whether to attempt recovery

        Returns:
            Recovery result if successful, None otherwise
        """
        error_type = type(error).__name__
        context = context or {}

        # Create error event
        event = ErrorEvent(
            error_type=error_type,
            message=str(error),
            severity=severity,
            context=context,
            traceback=traceback.format_exc()
        )

        # Record error
        self.error_history.append(event)
        self.error_counts[error_type] += 1
        self.error_rates[error_type].append(datetime.utcnow())

        # Log error
        log_func = logger.error if severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL] else logger.warning
        log_func(f"Error occurred: {error_type} - {error}")

        # Check error rate and send alerts if needed
        await self._check_error_rate(error_type, severity)

        # Attempt recovery if enabled
        if attempt_recovery and error_type in self.recovery_handlers:
            handler, strategy = self.recovery_handlers[error_type]
            event.recovery_attempted = True
            event.recovery_strategy = strategy

            try:
                result = await self._execute_recovery(handler, strategy, error, context)
                event.recovery_successful = True
                logger.info(f"Recovery successful for {error_type}")
                return result
            except Exception as recovery_error:
                logger.error(f"Recovery failed for {error_type}: {recovery_error}")
                event.recovery_successful = False

        # Send alert for critical errors
        if severity == ErrorSeverity.CRITICAL:
            await self._send_alerts(event)

        return None

    async def _execute_recovery(
        self,
        handler: Callable,
        strategy: RecoveryStrategy,
        error: Exception,
        context: Dict[str, Any]
    ) -> Any:
        """Execute recovery handler with strategy"""
        if strategy == RecoveryStrategy.RETRY:
            return await self._retry_with_backoff(handler, context)
        elif strategy == RecoveryStrategy.FALLBACK:
            service = context.get('service', 'unknown')
            if service in self.fallback_handlers:
                return await self.fallback_handlers[service](context)
        elif strategy == RecoveryStrategy.IGNORE:
            logger.info("Error ignored per recovery strategy")
            return None
        else:
            # Default: call handler directly
            if asyncio.iscoroutinefunction(handler):
                return await handler(error, context)
            return handler(error, context)

    async def _retry_with_backoff(
        self,
        handler: Callable,
        context: Dict[str, Any],
        max_retries: int = 3,
        initial_delay: float = 1.0
    ) -> Any:
        """
        Retry with exponential backoff

        Args:
            handler: Handler function
            context: Context dict
            max_retries: Maximum retry attempts
            initial_delay: Initial delay in seconds

        Returns:
            Handler result

        Raises:
            Exception if all retries fail
        """
        delay = initial_delay

        for attempt in range(max_retries):
            try:
                if asyncio.iscoroutinefunction(handler):
                    return await handler(context)
                return handler(context)
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Retry {attempt + 1}/{max_retries} failed, retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    raise

    async def _check_error_rate(self, error_type: str, severity: ErrorSeverity):
        """Check error rate and send alerts if threshold exceeded"""
        if error_type not in self.error_rates:
            return

        # Count errors in last minute
        now = datetime.utcnow()
        one_minute_ago = now - timedelta(minutes=1)

        recent_errors = sum(
            1 for timestamp in self.error_rates[error_type]
            if timestamp > one_minute_ago
        )

        # Alert threshold: 10 errors per minute for non-critical, 5 for critical
        threshold = 5 if severity == ErrorSeverity.CRITICAL else 10

        if recent_errors >= threshold:
            # Avoid alert spam - only alert once per 5 minutes
            last_alert = self.last_alert_times.get(error_type)
            if not last_alert or (now - last_alert).total_seconds() > 300:
                logger.warning(f"High error rate detected for {error_type}: {recent_errors} errors in 1 minute")
                self.last_alert_times[error_type] = now

                # Send alert
                event = ErrorEvent(
                    error_type=error_type,
                    message=f"High error rate: {recent_errors} errors in 1 minute",
                    severity=ErrorSeverity.HIGH
                )
                await self._send_alerts(event)

    async def _send_alerts(self, event: ErrorEvent):
        """Send alerts to all registered handlers"""
        for handler in self.alert_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")

    async def with_circuit_breaker(
        self,
        service: str,
        func: Callable,
        *args,
        fallback: Optional[Callable] = None,
        **kwargs
    ) -> Any:
        """
        Execute function with circuit breaker protection

        Args:
            service: Service name
            func: Function to execute
            *args: Function arguments
            fallback: Optional fallback function
            **kwargs: Function keyword arguments

        Returns:
            Function result or fallback result

        Raises:
            Exception if circuit is open and no fallback
        """
        breaker = self.get_circuit_breaker(service)

        if not breaker.can_attempt():
            logger.warning(f"Circuit breaker {service} is open")

            if fallback:
                logger.info(f"Using fallback for {service}")
                if asyncio.iscoroutinefunction(fallback):
                    return await fallback(*args, **kwargs)
                return fallback(*args, **kwargs)

            raise Exception(f"Circuit breaker {service} is open")

        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            breaker.record_success()
            return result

        except Exception as e:
            breaker.record_failure()

            if fallback and breaker.state == "open":
                logger.info(f"Circuit opened, using fallback for {service}")
                if asyncio.iscoroutinefunction(fallback):
                    return await fallback(*args, **kwargs)
                return fallback(*args, **kwargs)

            raise

    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        total_errors = len(self.error_history)
        recent_errors = list(self.error_history)[-100:] if self.error_history else []

        severity_counts = defaultdict(int)
        for event in recent_errors:
            severity_counts[event.severity.value] += 1

        return {
            'total_errors': total_errors,
            'recent_errors': len(recent_errors),
            'error_counts': dict(self.error_counts),
            'severity_distribution': dict(severity_counts),
            'circuit_breakers': {
                name: {
                    'state': breaker.state,
                    'failures': breaker.failures,
                }
                for name, breaker in self.circuit_breakers.items()
            },
            'recovery_stats': {
                'total_attempted': sum(1 for e in recent_errors if e.recovery_attempted),
                'total_successful': sum(1 for e in recent_errors if e.recovery_successful),
            }
        }

    def get_recent_errors(self, n: int = 10, severity: Optional[ErrorSeverity] = None) -> List[ErrorEvent]:
        """
        Get recent errors

        Args:
            n: Number of errors to return
            severity: Optional severity filter

        Returns:
            List of error events
        """
        errors = list(self.error_history)

        if severity:
            errors = [e for e in errors if e.severity == severity]

        return errors[-n:]

    def reset_circuit_breaker(self, service: str):
        """Manually reset a circuit breaker"""
        if service in self.circuit_breakers:
            breaker = self.circuit_breakers[service]
            breaker.failures = 0
            breaker.state = "closed"
            logger.info(f"Circuit breaker {service} manually reset")

    def clear_errors(self):
        """Clear error history (mainly for testing)"""
        self.error_history.clear()
        self.error_counts.clear()
        self.error_rates.clear()
        logger.info("Error history cleared")
