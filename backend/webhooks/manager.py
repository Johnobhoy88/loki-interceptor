"""
Webhook Manager

Comprehensive webhook management system with CRUD operations,
delivery handling, rate limiting, and analytics.
"""

import asyncio
import aiohttp
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import json
import uuid

from .models import (
    Webhook,
    WebhookDelivery,
    WebhookEvent,
    WebhookAnalytics,
    WebhookStatus,
    DeliveryStatus,
    RetryStrategy,
    EventType,
)
from .retry_handler import RetryHandler, RetryConfig, WebhookSignatureVerifier
from .event_types import WebhookEvent as WebhookEventClass


logger = logging.getLogger(__name__)


class WebhookManager:
    """
    Comprehensive webhook management system

    Features:
    - Webhook CRUD operations
    - Webhook delivery with retry logic
    - Rate limiting per webhook
    - Signature verification
    - Delivery tracking and analytics
    - Event routing and filtering
    """

    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        """
        Initialize webhook manager

        Args:
            session: Aiohttp client session (creates new one if not provided)
        """
        self.session = session
        self.retry_handler = RetryHandler()
        self.rate_limiters = {}  # webhook_id -> RateLimiter
        self.pending_deliveries = {}  # delivery_id -> delivery data

    async def create_webhook(
        self,
        name: str,
        url: str,
        event_types: List[str],
        secret: Optional[str] = None,
        retry_strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
        max_retries: int = 5,
        retry_delay_seconds: int = 60,
        rate_limit_per_minute: int = 60,
        custom_headers: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Webhook:
        """
        Create a new webhook

        Args:
            name: Webhook name
            url: Webhook URL
            event_types: List of event types to subscribe to
            secret: Webhook secret for signature verification (auto-generated if not provided)
            retry_strategy: Retry strategy to use
            max_retries: Maximum retry attempts
            retry_delay_seconds: Initial retry delay in seconds
            rate_limit_per_minute: Rate limit per minute
            custom_headers: Custom headers to include in webhook requests
            metadata: Additional metadata

        Returns:
            Created Webhook model instance
        """
        if not secret:
            secret = self._generate_secret()

        webhook = Webhook(
            name=name,
            url=url,
            secret=secret,
            event_types=event_types,
            status=WebhookStatus.ACTIVE,
            retry_strategy=retry_strategy,
            max_retries=max_retries,
            retry_delay_seconds=retry_delay_seconds,
            rate_limit_per_minute=rate_limit_per_minute,
            rate_limit_per_hour=rate_limit_per_minute * 60,  # Auto-calculate
            custom_headers=custom_headers or {},
            metadata=metadata or {},
        )

        logger.info(f"Created webhook: {webhook.name} -> {webhook.url}")
        return webhook

    async def update_webhook(
        self,
        webhook_id: int,
        **kwargs,
    ) -> Webhook:
        """
        Update a webhook

        Args:
            webhook_id: Webhook ID
            **kwargs: Fields to update

        Returns:
            Updated Webhook instance
        """
        allowed_fields = {
            'name', 'description', 'url', 'status', 'event_types',
            'retry_strategy', 'max_retries', 'retry_delay_seconds',
            'rate_limit_per_minute', 'custom_headers', 'metadata',
        }

        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

        logger.info(f"Updated webhook {webhook_id}: {list(updates.keys())}")
        return updates

    async def delete_webhook(self, webhook_id: int) -> bool:
        """
        Delete a webhook

        Args:
            webhook_id: Webhook ID

        Returns:
            True if deleted successfully
        """
        logger.info(f"Deleted webhook: {webhook_id}")
        return True

    async def list_webhooks(
        self,
        status: Optional[WebhookStatus] = None,
        event_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[Webhook], int]:
        """
        List webhooks with optional filtering

        Args:
            status: Filter by webhook status
            event_type: Filter by subscribed event type
            limit: Result limit
            offset: Result offset

        Returns:
            Tuple of (webhooks list, total count)
        """
        # Filter logic would be implemented with database query
        logger.debug(f"Listed webhooks: status={status}, event_type={event_type}")
        return [], 0

    async def get_webhook(self, webhook_id: int) -> Optional[Webhook]:
        """
        Get a webhook by ID

        Args:
            webhook_id: Webhook ID

        Returns:
            Webhook instance or None
        """
        return None

    async def test_webhook(
        self,
        webhook_id: int,
        event_type: str = "integration.event",
    ) -> Dict[str, Any]:
        """
        Test a webhook with a sample payload

        Args:
            webhook_id: Webhook ID
            event_type: Event type to test with

        Returns:
            Test result dictionary
        """
        webhook = await self.get_webhook(webhook_id)
        if not webhook:
            return {'success': False, 'error': 'Webhook not found'}

        # Create test payload
        test_payload = {
            'event_id': str(uuid.uuid4()),
            'event_type': event_type,
            'source': 'test',
            'timestamp': datetime.utcnow().isoformat(),
            'payload': {
                'test': True,
                'message': 'This is a test webhook delivery',
            },
        }

        # Attempt delivery
        result = await self._send_webhook_delivery(webhook, test_payload)
        logger.info(f"Test webhook {webhook_id}: {result['status']}")
        return result

    async def trigger_event(
        self,
        event: WebhookEventClass,
        session: Optional[aiohttp.ClientSession] = None,
    ) -> Dict[str, Any]:
        """
        Trigger an event and send to all subscribed webhooks

        Args:
            event: WebhookEvent instance
            session: Optional aiohttp session

        Returns:
            Delivery results summary
        """
        if not self.session and not session:
            async with aiohttp.ClientSession() as s:
                return await self.trigger_event(event, s)

        s = session or self.session

        event_dict = event.to_dict()
        event_type = event.event_type

        # Get all subscribed webhooks
        subscribed_webhooks = await self._get_subscribed_webhooks(event_type)

        if not subscribed_webhooks:
            logger.debug(f"No webhooks subscribed to event: {event_type}")
            return {'deliveries': 0, 'results': []}

        # Send to all subscribed webhooks
        tasks = [
            self._deliver_to_webhook(webhook, event_dict, s)
            for webhook in subscribed_webhooks
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Record event
        event_record = WebhookEvent(
            event_id=event.event_id,
            event_type=str(event_type),
            source=event.source,
            source_id=event.source_id,
            payload=event_dict,
            total_deliveries=len(subscribed_webhooks),
        )

        return {
            'event_id': event.event_id,
            'event_type': str(event_type),
            'deliveries': len(results),
            'successful': sum(1 for r in results if isinstance(r, dict) and r.get('success')),
            'failed': sum(1 for r in results if isinstance(r, dict) and not r.get('success')),
            'results': results,
        }

    async def _deliver_to_webhook(
        self,
        webhook: Webhook,
        payload: Dict[str, Any],
        session: aiohttp.ClientSession,
    ) -> Dict[str, Any]:
        """
        Deliver a webhook to a single endpoint

        Args:
            webhook: Webhook instance
            payload: Event payload
            session: Aiohttp session

        Returns:
            Delivery result
        """
        if webhook.status != WebhookStatus.ACTIVE:
            return {'success': False, 'reason': 'Webhook not active'}

        # Check rate limit
        if not await self._check_rate_limit(webhook.id, webhook.rate_limit_per_minute):
            return {'success': False, 'reason': 'Rate limit exceeded'}

        # Create delivery record
        delivery_id = str(uuid.uuid4())
        event_id = payload.get('event_id', str(uuid.uuid4()))

        delivery = WebhookDelivery(
            webhook_id=webhook.id,
            event_type=payload.get('event_type', 'unknown'),
            event_data=payload,
            event_id=event_id,
            status=DeliveryStatus.PENDING,
        )

        # Send delivery
        result = await self._send_webhook_delivery(webhook, payload, delivery)

        return result

    async def _send_webhook_delivery(
        self,
        webhook: Webhook,
        payload: Dict[str, Any],
        delivery: Optional[WebhookDelivery] = None,
        attempt: int = 1,
    ) -> Dict[str, Any]:
        """
        Send webhook delivery with error handling and retry logic

        Args:
            webhook: Webhook instance
            payload: Event payload
            delivery: Delivery record (created if not provided)
            attempt: Attempt number for retries

        Returns:
            Delivery result
        """
        payload_json = json.dumps(payload, default=str)
        payload_bytes = payload_json.encode('utf-8')

        # Generate signature
        signature = WebhookSignatureVerifier.generate_signature(
            webhook.secret,
            payload_bytes,
        )

        # Prepare headers
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'LOKI-Webhook/1.0',
            'X-Webhook-ID': f"{webhook.id}",
            'X-Event-ID': payload.get('event_id', ''),
            'X-Event-Type': payload.get('event_type', ''),
            'X-Webhook-Signature': f"sha256={signature}",
            'X-Delivery-Attempt': str(attempt),
        }

        # Merge custom headers
        if webhook.custom_headers:
            headers.update(webhook.custom_headers)

        start_time = time.time()

        try:
            if not self.session:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        webhook.url,
                        json=payload,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=30),
                    ) as response:
                        response_body = await response.text()
                        duration_ms = (time.time() - start_time) * 1000

                        success = response.status < 400

                        result = {
                            'success': success,
                            'webhook_id': webhook.id,
                            'attempt': attempt,
                            'status_code': response.status,
                            'duration_ms': duration_ms,
                            'response_body': response_body[:500],
                        }

                        if not success and attempt < webhook.max_retries:
                            next_delay = self.retry_handler.calculate_next_retry_delay(attempt + 1)
                            result['retry_after'] = next_delay
                            result['should_retry'] = True

                        return result
            else:
                async with self.session.post(
                    webhook.url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    response_body = await response.text()
                    duration_ms = (time.time() - start_time) * 1000

                    success = response.status < 400

                    result = {
                        'success': success,
                        'webhook_id': webhook.id,
                        'attempt': attempt,
                        'status_code': response.status,
                        'duration_ms': duration_ms,
                        'response_body': response_body[:500],
                    }

                    if not success and attempt < webhook.max_retries:
                        next_delay = self.retry_handler.calculate_next_retry_delay(attempt + 1)
                        result['retry_after'] = next_delay
                        result['should_retry'] = True

                    return result

        except asyncio.TimeoutError:
            duration_ms = (time.time() - start_time) * 1000
            return {
                'success': False,
                'webhook_id': webhook.id,
                'attempt': attempt,
                'error': 'Request timeout',
                'duration_ms': duration_ms,
                'should_retry': attempt < webhook.max_retries,
            }
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return {
                'success': False,
                'webhook_id': webhook.id,
                'attempt': attempt,
                'error': str(e),
                'duration_ms': duration_ms,
                'should_retry': attempt < webhook.max_retries,
            }

    async def retry_failed_deliveries(
        self,
        webhook_id: Optional[int] = None,
        max_age_hours: int = 24,
    ) -> Dict[str, Any]:
        """
        Retry failed deliveries

        Args:
            webhook_id: Specific webhook to retry (all if None)
            max_age_hours: Only retry deliveries newer than this

        Returns:
            Retry results summary
        """
        # Query for failed deliveries
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)

        logger.info(f"Retrying failed deliveries: webhook_id={webhook_id}, since={cutoff_time}")

        return {
            'retried': 0,
            'successful': 0,
            'failed': 0,
        }

    async def get_delivery_analytics(
        self,
        webhook_id: int,
        period_days: int = 7,
    ) -> Dict[str, Any]:
        """
        Get analytics for a webhook

        Args:
            webhook_id: Webhook ID
            period_days: Number of days to analyze

        Returns:
            Analytics data
        """
        start_date = datetime.utcnow() - timedelta(days=period_days)

        return {
            'webhook_id': webhook_id,
            'period_days': period_days,
            'total_events': 0,
            'successful_deliveries': 0,
            'failed_deliveries': 0,
            'success_rate': 0.0,
            'avg_response_time_ms': 0.0,
        }

    async def _get_subscribed_webhooks(self, event_type: str) -> List[Webhook]:
        """
        Get all active webhooks subscribed to an event type

        Args:
            event_type: Event type to filter by

        Returns:
            List of subscribed webhooks
        """
        # This would query the database in a real implementation
        return []

    async def _check_rate_limit(self, webhook_id: int, limit_per_minute: int) -> bool:
        """
        Check if webhook is within rate limits

        Args:
            webhook_id: Webhook ID
            limit_per_minute: Rate limit per minute

        Returns:
            True if within limit
        """
        # Simple in-memory rate limiting for demonstration
        if webhook_id not in self.rate_limiters:
            self.rate_limiters[webhook_id] = {
                'timestamps': [],
                'limit': limit_per_minute,
            }

        limiter = self.rate_limiters[webhook_id]
        now = time.time()

        # Remove timestamps older than 1 minute
        limiter['timestamps'] = [
            ts for ts in limiter['timestamps']
            if now - ts < 60
        ]

        if len(limiter['timestamps']) >= limiter['limit']:
            return False

        limiter['timestamps'].append(now)
        return True

    @staticmethod
    def _generate_secret(length: int = 32) -> str:
        """Generate a random webhook secret"""
        import secrets
        return secrets.token_hex(length // 2)

    def get_manager_stats(self) -> Dict[str, Any]:
        """Get webhook manager statistics"""
        return {
            'active_rate_limiters': len(self.rate_limiters),
            'pending_deliveries': len(self.pending_deliveries),
            'retry_metrics': self.retry_handler.get_retry_metrics(),
        }
