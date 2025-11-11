"""
Fallback and Resilience Handler Module

Manages fallback strategies for API failures and degraded service:
- Provider failover
- Cached response fallback
- Graceful degradation
- Retry strategies
"""

from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from dataclasses import dataclass
import time


class FallbackStrategy(str, Enum):
    """Fallback strategy types"""
    FAILOVER = "failover"  # Switch to alternative provider
    CACHED = "cached"  # Return cached response
    DEGRADED = "degraded"  # Return simplified response
    RETRY = "retry"  # Retry with backoff
    CIRCUIT_BREAKER = "circuit_breaker"  # Prevent cascading failures


@dataclass
class FallbackAction:
    """Action to take on failure"""
    strategy: FallbackStrategy
    target: Optional[str] = None  # e.g., alternative provider
    config: Dict = None  # Strategy-specific configuration

    def __post_init__(self):
        if self.config is None:
            self.config = {}


@dataclass
class FailureContext:
    """Context of a failure"""
    error_type: str
    error_message: str
    timestamp: str
    provider: str
    attempt_number: int = 1


class FallbackHandler:
    """
    Manages fallback strategies for resilience

    Features:
    - Multiple fallback strategies
    - Intelligent failover
    - Circuit breaker pattern
    - Retry strategies with backoff
    """

    def __init__(self):
        self.fallback_chain: List[FallbackAction] = []
        self.provider_health: Dict[str, bool] = {}
        self.failure_log: List[FailureContext] = []
        self.circuit_breaker_state: Dict[str, str] = {}  # CLOSED, OPEN, HALF_OPEN
        self.failure_thresholds = {
            "circuit_breaker_failures": 5,
            "circuit_breaker_timeout": 60  # seconds
        }

    def add_fallback(self, action: FallbackAction, position: Optional[int] = None):
        """Add fallback action to chain"""
        if position is None:
            self.fallback_chain.append(action)
        else:
            self.fallback_chain.insert(position, action)

    def set_provider_health(self, provider: str, healthy: bool):
        """Update provider health status"""
        self.provider_health[provider] = healthy

        if not healthy and provider in self.circuit_breaker_state:
            self.circuit_breaker_state[provider] = "OPEN"

    def get_next_fallback(
        self,
        current_provider: str,
        failure_context: FailureContext
    ) -> Optional[FallbackAction]:
        """
        Determine next fallback action

        Args:
            current_provider: Provider that failed
            failure_context: Context of failure

        Returns:
            Next fallback action or None
        """
        self._log_failure(failure_context)

        # Check circuit breaker state
        if self._should_circuit_break(current_provider):
            self._open_circuit(current_provider)
            failure_context.error_message += " (Circuit breaker opened)"

        # Find best fallback
        for action in self.fallback_chain:
            if self._can_execute_fallback(action, current_provider):
                return action

        return None

    def execute_retry(
        self,
        fn: Callable,
        max_attempts: int = 3,
        base_wait: float = 1.0,
        max_wait: float = 30.0
    ) -> Any:
        """
        Execute function with exponential backoff retry

        Args:
            fn: Function to execute
            max_attempts: Maximum retry attempts
            base_wait: Initial wait time in seconds
            max_wait: Maximum wait time between retries

        Returns:
            Result of function or raises exception
        """
        last_exception = None
        wait_time = base_wait

        for attempt in range(max_attempts):
            try:
                return fn()
            except Exception as e:
                last_exception = e

                if attempt < max_attempts - 1:
                    # Exponential backoff with jitter
                    import random
                    jitter = random.uniform(0, wait_time * 0.1)
                    sleep_time = min(wait_time + jitter, max_wait)

                    time.sleep(sleep_time)
                    wait_time *= 2

        if last_exception:
            raise last_exception

    def handle_degraded_service(self, original_request: str) -> str:
        """
        Provide degraded response when service is degraded

        Args:
            original_request: Original request that failed

        Returns:
            Simplified response
        """
        return f"""Service experiencing issues. Providing simplified response:

Original request: {original_request[:100]}...

This is a degraded response due to system unavailability.
Please try again in a few moments.

Note: Full analysis features are temporarily unavailable."""

    def reset_circuit_breaker(self, provider: str):
        """Reset circuit breaker for provider"""
        if provider in self.circuit_breaker_state:
            self.circuit_breaker_state[provider] = "CLOSED"
            self.provider_health[provider] = True

    def _should_circuit_break(self, provider: str) -> bool:
        """Check if circuit should break for provider"""
        provider_failures = [
            f for f in self.failure_log
            if f.provider == provider
        ]

        if len(provider_failures) >= self.failure_thresholds["circuit_breaker_failures"]:
            return True

        return False

    def _open_circuit(self, provider: str):
        """Open circuit for provider"""
        self.circuit_breaker_state[provider] = "OPEN"
        self.provider_health[provider] = False

    def _can_execute_fallback(self, action: FallbackAction, failed_provider: str) -> bool:
        """Check if fallback can be executed"""
        if action.strategy == FallbackStrategy.FAILOVER:
            # Check if target provider is healthy
            target = action.config.get("provider")
            return self.provider_health.get(target, True)

        elif action.strategy == FallbackStrategy.CACHED:
            # Can always try cached
            return True

        elif action.strategy == FallbackStrategy.DEGRADED:
            # Can always degrade
            return True

        elif action.strategy == FallbackStrategy.RETRY:
            # Check if should retry
            return action.config.get("max_attempts", 3) > 0

        elif action.strategy == FallbackStrategy.CIRCUIT_BREAKER:
            # Don't execute if circuit is open
            return self.circuit_breaker_state.get(failed_provider, "CLOSED") != "OPEN"

        return False

    def _log_failure(self, context: FailureContext):
        """Log failure event"""
        self.failure_log.append(context)

        # Keep log bounded
        if len(self.failure_log) > 10000:
            self.failure_log = self.failure_log[-5000:]

    def get_health_report(self) -> Dict:
        """Get health status report"""
        return {
            "provider_health": self.provider_health.copy(),
            "circuit_breaker_states": self.circuit_breaker_state.copy(),
            "recent_failures": len(self.failure_log),
            "fallback_chain_length": len(self.fallback_chain)
        }

    def get_failure_statistics(self) -> Dict:
        """Get failure statistics"""
        if not self.failure_log:
            return {}

        failures_by_provider = {}
        for failure in self.failure_log:
            provider = failure.provider
            failures_by_provider[provider] = failures_by_provider.get(provider, 0) + 1

        failures_by_type = {}
        for failure in self.failure_log:
            error_type = failure.error_type
            failures_by_type[error_type] = failures_by_type.get(error_type, 0) + 1

        return {
            "total_failures": len(self.failure_log),
            "failures_by_provider": failures_by_provider,
            "failures_by_type": failures_by_type,
            "failure_rate": len(self.failure_log) / max(1, len(self.failure_log) * 10)
        }


class ResilienceConfig:
    """Configuration for resilience settings"""

    def __init__(self):
        self.max_retries = 3
        self.base_retry_delay = 1.0
        self.max_retry_delay = 30.0
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_timeout = 60
        self.fallback_providers = []
        self.enable_caching = True
        self.cache_fallback_ttl = 3600  # 1 hour

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "max_retries": self.max_retries,
            "base_retry_delay": self.base_retry_delay,
            "max_retry_delay": self.max_retry_delay,
            "circuit_breaker_threshold": self.circuit_breaker_threshold,
            "circuit_breaker_timeout": self.circuit_breaker_timeout,
            "fallback_providers": self.fallback_providers,
            "enable_caching": self.enable_caching,
            "cache_fallback_ttl": self.cache_fallback_ttl
        }
