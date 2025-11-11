"""
Webhook Retry Handler with Exponential Backoff

Implements sophisticated retry logic with multiple strategies,
exponential backoff, jitter, and dead-letter queue handling.
"""

import random
import time
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Callable, Dict, Any
from enum import Enum
from dataclasses import dataclass
import hashlib
import hmac


logger = logging.getLogger(__name__)


class RetryStrategy(str, Enum):
    """Retry strategy enumeration"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_INTERVAL = "fixed_interval"
    NO_RETRY = "no_retry"


@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    max_retries: int = 5
    initial_delay_seconds: int = 60
    max_delay_seconds: int = 3600  # 1 hour
    backoff_multiplier: float = 2.0
    jitter_enabled: bool = True
    jitter_percentage: float = 0.1  # 10% jitter


class RetryHandler:
    """
    Sophisticated retry handler for webhook delivery failures

    Features:
    - Multiple retry strategies (exponential, linear, fixed, none)
    - Exponential backoff with jitter
    - Configurable retry limits and delays
    - Dead-letter queue handling
    - Async/concurrent retry processing
    - Metrics tracking
    """

    def __init__(self, config: Optional[RetryConfig] = None):
        """
        Initialize retry handler

        Args:
            config: Retry configuration (uses defaults if not provided)
        """
        self.config = config or RetryConfig()
        self.failed_deliveries = {}  # Track failed deliveries
        self.metrics = {
            'total_retries': 0,
            'successful_retries': 0,
            'permanent_failures': 0,
        }

    def calculate_next_retry_delay(self, attempt_number: int) -> int:
        """
        Calculate delay for next retry based on strategy and attempt number

        Args:
            attempt_number: Current retry attempt number (1-based)

        Returns:
            Delay in seconds before next retry
        """
        if self.config.strategy == RetryStrategy.NO_RETRY:
            return 0

        if attempt_number > self.config.max_retries:
            return 0

        # Calculate base delay
        if self.config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            base_delay = self.config.initial_delay_seconds * (
                self.config.backoff_multiplier ** (attempt_number - 1)
            )
        elif self.config.strategy == RetryStrategy.LINEAR_BACKOFF:
            base_delay = self.config.initial_delay_seconds * attempt_number
        else:  # FIXED_INTERVAL
            base_delay = self.config.initial_delay_seconds

        # Cap at max delay
        delay = min(base_delay, self.config.max_delay_seconds)

        # Add jitter if enabled
        if self.config.jitter_enabled:
            jitter = delay * self.config.jitter_percentage * random.random()
            delay = delay + jitter

        return int(delay)

    def should_retry(
        self,
        attempt_number: int,
        status_code: Optional[int] = None,
        error: Optional[str] = None,
    ) -> bool:
        """
        Determine if a delivery should be retried

        Args:
            attempt_number: Current attempt number
            status_code: HTTP status code of failed delivery
            error: Error message or type

        Returns:
            True if delivery should be retried, False otherwise
        """
        # Don't retry if max retries exceeded
        if attempt_number > self.config.max_retries:
            return False

        # Don't retry if no retry strategy
        if self.config.strategy == RetryStrategy.NO_RETRY:
            return False

        # Retry on specific HTTP status codes
        if status_code:
            # Retry on server errors and some client errors
            if status_code in [429, 500, 502, 503, 504]:
                return True
            # Don't retry on permanent client errors
            if status_code in [400, 401, 403, 405]:
                return False

        # Retry on timeout and network errors
        if error:
            retryable_errors = [
                'timeout',
                'connection_error',
                'network_error',
                'dns_error',
                'ssl_error',
            ]
            if any(err in error.lower() for err in retryable_errors):
                return True

        # If status is 2xx or 3xx, don't retry
        if status_code and status_code < 400:
            return False

        # Default: retry on unknown errors
        return attempt_number <= self.config.max_retries

    def calculate_exponential_backoff(
        self,
        attempt: int,
        base_delay: int = 60,
        multiplier: float = 2.0,
        max_delay: int = 3600,
    ) -> int:
        """
        Calculate exponential backoff delay

        Args:
            attempt: Attempt number (1-based)
            base_delay: Base delay in seconds
            multiplier: Backoff multiplier
            max_delay: Maximum delay in seconds

        Returns:
            Delay in seconds
        """
        delay = base_delay * (multiplier ** (attempt - 1))
        return int(min(delay, max_delay))

    def create_retry_schedule(
        self,
        delivery_id: str,
        initial_attempt: int = 1,
    ) -> Dict[str, Any]:
        """
        Create a retry schedule for a failed delivery

        Args:
            delivery_id: ID of failed delivery
            initial_attempt: Initial attempt number

        Returns:
            Retry schedule metadata
        """
        schedule = {
            'delivery_id': delivery_id,
            'attempts': [],
            'total_retry_time_seconds': 0,
        }

        current_time = datetime.utcnow()
        cumulative_delay = 0

        for attempt in range(initial_attempt, self.config.max_retries + 1):
            delay = self.calculate_next_retry_delay(attempt)
            retry_time = current_time + timedelta(seconds=cumulative_delay + delay)

            schedule['attempts'].append({
                'attempt': attempt,
                'delay_seconds': delay,
                'retry_at': retry_time.isoformat(),
            })

            cumulative_delay += delay

        schedule['total_retry_time_seconds'] = cumulative_delay
        return schedule

    async def retry_delivery(
        self,
        delivery_func: Callable,
        delivery_id: str,
        current_attempt: int,
        *args,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Retry a delivery with proper error handling and metrics

        Args:
            delivery_func: Function to execute for retry
            delivery_id: Delivery identifier
            current_attempt: Current attempt number
            *args: Positional arguments for delivery function
            **kwargs: Keyword arguments for delivery function

        Returns:
            Result of delivery attempt
        """
        self.metrics['total_retries'] += 1

        try:
            result = await delivery_func(*args, **kwargs)
            self.metrics['successful_retries'] += 1
            return {
                'success': True,
                'attempt': current_attempt,
                'result': result,
            }
        except Exception as e:
            error_msg = str(e)
            should_retry = self.should_retry(
                current_attempt,
                error=error_msg,
            )

            if should_retry:
                delay = self.calculate_next_retry_delay(current_attempt + 1)
                retry_at = (datetime.utcnow() + timedelta(seconds=delay)).isoformat()

                return {
                    'success': False,
                    'attempt': current_attempt,
                    'error': error_msg,
                    'should_retry': True,
                    'next_retry_at': retry_at,
                    'retry_delay_seconds': delay,
                }
            else:
                self.metrics['permanent_failures'] += 1
                return {
                    'success': False,
                    'attempt': current_attempt,
                    'error': error_msg,
                    'should_retry': False,
                    'permanent_failure': True,
                }

    async def process_retry_queue(
        self,
        pending_retries: list,
        delivery_func: Callable,
        max_concurrent: int = 5,
    ):
        """
        Process a queue of pending retries concurrently

        Args:
            pending_retries: List of pending retry tasks
            delivery_func: Function to execute for each retry
            max_concurrent: Maximum concurrent retries
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def bounded_retry(task):
            async with semaphore:
                return await self.retry_delivery(delivery_func, **task)

        results = await asyncio.gather(
            *[bounded_retry(task) for task in pending_retries],
            return_exceptions=True,
        )
        return results

    def get_retry_metrics(self) -> Dict[str, Any]:
        """Get retry metrics and statistics"""
        total = self.metrics['total_retries']
        successful = self.metrics['successful_retries']
        permanent = self.metrics['permanent_failures']

        return {
            'total_retries': total,
            'successful_retries': successful,
            'permanent_failures': permanent,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'failure_rate': (permanent / total * 100) if total > 0 else 0,
        }

    def reset_metrics(self):
        """Reset retry metrics"""
        self.metrics = {
            'total_retries': 0,
            'successful_retries': 0,
            'permanent_failures': 0,
        }


class WebhookSignatureVerifier:
    """
    Verify webhook signatures using HMAC-SHA256

    Ensures that webhook payloads are authentic and haven't been tampered with.
    """

    ALGORITHM = 'sha256'
    HEADER_NAME = 'X-Webhook-Signature'

    @staticmethod
    def generate_signature(
        secret: str,
        payload: bytes,
        algorithm: str = 'sha256',
    ) -> str:
        """
        Generate HMAC signature for webhook payload

        Args:
            secret: Webhook secret key
            payload: Payload bytes to sign
            algorithm: HMAC algorithm (default: sha256)

        Returns:
            Hex-encoded signature
        """
        if isinstance(payload, str):
            payload = payload.encode('utf-8')
        if isinstance(secret, str):
            secret = secret.encode('utf-8')

        signature = hmac.new(
            secret,
            payload,
            getattr(hashlib, algorithm),
        )
        return signature.hexdigest()

    @staticmethod
    def verify_signature(
        secret: str,
        payload: bytes,
        signature: str,
        algorithm: str = 'sha256',
    ) -> bool:
        """
        Verify webhook signature

        Args:
            secret: Webhook secret key
            payload: Payload bytes that were signed
            signature: Signature to verify (hex-encoded)
            algorithm: HMAC algorithm (default: sha256)

        Returns:
            True if signature is valid, False otherwise
        """
        expected_signature = WebhookSignatureVerifier.generate_signature(
            secret,
            payload,
            algorithm,
        )
        # Use constant-time comparison to prevent timing attacks
        return hmac.compare_digest(expected_signature, signature)

    @staticmethod
    def create_signed_request(
        secret: str,
        payload: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """
        Create request headers with signature

        Args:
            secret: Webhook secret key
            payload: Payload string
            headers: Existing headers to merge with

        Returns:
            Headers dictionary with signature
        """
        result_headers = headers.copy() if headers else {}

        signature = WebhookSignatureVerifier.generate_signature(
            secret,
            payload,
        )
        result_headers[WebhookSignatureVerifier.HEADER_NAME] = f"sha256={signature}"

        return result_headers
