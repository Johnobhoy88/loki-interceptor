"""
Zapier Integration

Send LOKI events to Zapier webhooks for workflow automation.
Enables integration with thousands of apps through Zapier.
"""

import aiohttp
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .base import BaseIntegration, IntegrationStatus


logger = logging.getLogger(__name__)


class ZapierIntegration(BaseIntegration):
    """
    Zapier integration for LOKI

    Features:
    - Send events to Zapier catch hooks
    - Support for workflow automation
    - Integration with thousands of apps
    - Custom transformation rules
    - Event batching and scheduling
    - Error tracking and retries
    """

    def __init__(
        self,
        name: str,
        webhook_url: str,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Zapier integration

        Args:
            name: Integration name
            webhook_url: Zapier catch hook URL
            config: Configuration options
        """
        credentials = {'webhook_url': webhook_url}
        config = config or {}
        config.setdefault('include_metadata', True)
        config.setdefault('batch_events', False)
        config.setdefault('batch_size', 10)
        config.setdefault('batch_timeout_seconds', 30)

        super().__init__(
            name=name,
            integration_type='zapier',
            credentials=credentials,
            config=config,
        )

        self.event_queue = []

    async def connect(self) -> bool:
        """Connect to Zapier and validate webhook"""
        try:
            is_valid = await self.validate_credentials()
            if is_valid:
                self.status = IntegrationStatus.CONNECTED
                logger.info(f"Zapier integration connected: {self.name}")
            return is_valid
        except Exception as e:
            logger.error(f"Failed to connect Zapier integration: {str(e)}")
            self.status = IntegrationStatus.ERROR
            return False

    async def disconnect(self) -> bool:
        """Disconnect from Zapier"""
        # Flush any pending events
        if self.event_queue:
            await self._flush_event_queue()

        self.status = IntegrationStatus.DISCONNECTED
        logger.info(f"Zapier integration disconnected: {self.name}")
        return True

    async def validate_credentials(self) -> bool:
        """Validate Zapier webhook URL"""
        try:
            webhook_url = self.credentials.get('webhook_url')
            if not webhook_url:
                return False

            payload = {
                'event_type': 'test',
                'timestamp': datetime.utcnow().isoformat(),
                'message': 'LOKI Zapier integration test',
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    return response.status in [200, 201]

        except Exception as e:
            logger.error(f"Zapier credential validation failed: {str(e)}")
            return False

    async def send_message(self, message: Dict[str, Any]) -> bool:
        """
        Send a message to Zapier

        Args:
            message: Message payload

        Returns:
            True if message sent successfully
        """
        try:
            webhook_url = self.credentials.get('webhook_url')
            if not webhook_url:
                logger.error("Zapier webhook URL not configured")
                return False

            # Check if batching is enabled
            if self.config.get('batch_events'):
                self.event_queue.append(message)
                if len(self.event_queue) >= self.config.get('batch_size'):
                    await self._flush_event_queue()
                return True

            payload = self._format_message(message)

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status not in [200, 201]:
                        logger.error(f"Zapier message failed: {response.status}")
                        return False

                    self.last_event_at = datetime.utcnow()
                    return True

        except Exception as e:
            logger.error(f"Failed to send Zapier message: {str(e)}")
            return False

    async def _flush_event_queue(self) -> bool:
        """
        Flush pending events to Zapier

        Returns:
            True if all events sent successfully
        """
        if not self.event_queue:
            return True

        try:
            webhook_url = self.credentials.get('webhook_url')
            payload = {
                'events': [self._format_message(msg) for msg in self.event_queue],
                'batch_count': len(self.event_queue),
                'batch_timestamp': datetime.utcnow().isoformat(),
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status in [200, 201]:
                        self.event_queue = []
                        self.last_event_at = datetime.utcnow()
                        logger.info(f"Flushed {len(self.event_queue)} events to Zapier")
                        return True
                    else:
                        logger.error(f"Zapier flush failed: {response.status}")
                        return False

        except Exception as e:
            logger.error(f"Failed to flush event queue: {str(e)}")
            return False

    async def on_validation_completed(self, validation_data: Dict[str, Any]) -> bool:
        """Handle validation completion event"""
        message = {
            'type': 'validation.completed',
            'data': validation_data,
        }
        return await self.send_message(message)

    async def on_compliance_alert(self, alert_data: Dict[str, Any]) -> bool:
        """Handle compliance alert event"""
        message = {
            'type': 'compliance.alert',
            'data': alert_data,
        }
        return await self.send_message(message)

    async def on_document_processed(self, document_data: Dict[str, Any]) -> bool:
        """Handle document processed event"""
        message = {
            'type': 'document.processed',
            'data': document_data,
        }
        return await self.send_message(message)

    async def on_correction_applied(self, correction_data: Dict[str, Any]) -> bool:
        """Handle correction applied event"""
        message = {
            'type': 'correction.applied',
            'data': correction_data,
        }
        return await self.send_message(message)

    async def on_batch_completed(self, batch_data: Dict[str, Any]) -> bool:
        """Handle batch completion event"""
        message = {
            'type': 'batch.completed',
            'data': batch_data,
        }
        return await self.send_message(message)

    async def on_error(self, error_data: Dict[str, Any]) -> bool:
        """Handle error event"""
        message = {
            'type': 'system.error',
            'data': error_data,
        }
        return await self.send_message(message)

    def _format_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format message for Zapier webhook

        Args:
            message: Message payload

        Returns:
            Zapier-formatted message
        """
        formatted = {
            'event_type': message.get('type', message.get('event_type', 'event')),
            'timestamp': datetime.utcnow().isoformat(),
        }

        # Add data
        if 'data' in message:
            formatted.update(message['data'])
        else:
            formatted.update(message)

        # Add metadata if enabled
        if self.config.get('include_metadata'):
            formatted['_metadata'] = {
                'source': 'loki_interceptor',
                'integration': self.name,
                'version': '1.0',
            }

        return formatted

    async def send_custom_action(
        self,
        action_type: str,
        action_data: Dict[str, Any],
    ) -> bool:
        """
        Send a custom action to Zapier

        Args:
            action_type: Type of action
            action_data: Action data payload

        Returns:
            True if action sent successfully
        """
        message = {
            'type': f'custom.{action_type}',
            'data': action_data,
        }
        return await self.send_message(message)

    async def trigger_workflow(
        self,
        workflow_id: str,
        parameters: Dict[str, Any],
    ) -> bool:
        """
        Trigger a Zapier workflow

        Args:
            workflow_id: Workflow identifier
            parameters: Workflow parameters

        Returns:
            True if workflow triggered successfully
        """
        message = {
            'type': 'workflow_trigger',
            'workflow_id': workflow_id,
            'data': parameters,
        }
        return await self.send_message(message)
