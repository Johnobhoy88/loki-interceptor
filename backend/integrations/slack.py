"""
Slack Integration

Send LOKI events and notifications to Slack channels.
Supports rich message formatting with blocks and interactive elements.
"""

import aiohttp
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from .base import BaseIntegration, IntegrationStatus


logger = logging.getLogger(__name__)


class SlackIntegration(BaseIntegration):
    """
    Slack integration for LOKI

    Features:
    - Send messages to Slack channels
    - Rich message formatting with blocks
    - Attachments and file uploads
    - Interactive message actions
    - Webhook URL support
    - Custom formatting per event type
    """

    API_BASE_URL = "https://slack.com/api"
    WEBHOOK_API_ENDPOINT = "/services/"

    def __init__(
        self,
        name: str,
        webhook_url: Optional[str] = None,
        bot_token: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Slack integration

        Args:
            name: Integration name
            webhook_url: Slack webhook URL (for simple webhooks)
            bot_token: Slack bot token (for more advanced features)
            config: Configuration options
        """
        credentials = {}
        if webhook_url:
            credentials['webhook_url'] = webhook_url
        if bot_token:
            credentials['bot_token'] = bot_token

        config = config or {}
        config.setdefault('default_channel', '#general')
        config.setdefault('include_footer', True)
        config.setdefault('include_timestamp', True)

        super().__init__(
            name=name,
            integration_type='slack',
            credentials=credentials,
            config=config,
        )

    async def connect(self) -> bool:
        """Connect to Slack and validate credentials"""
        try:
            is_valid = await self.validate_credentials()
            if is_valid:
                self.status = IntegrationStatus.CONNECTED
                logger.info(f"Slack integration connected: {self.name}")
            return is_valid
        except Exception as e:
            logger.error(f"Failed to connect Slack integration: {str(e)}")
            self.status = IntegrationStatus.ERROR
            return False

    async def disconnect(self) -> bool:
        """Disconnect from Slack"""
        self.status = IntegrationStatus.DISCONNECTED
        logger.info(f"Slack integration disconnected: {self.name}")
        return True

    async def validate_credentials(self) -> bool:
        """Validate Slack credentials"""
        try:
            if 'webhook_url' in self.credentials:
                # Test webhook URL
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.credentials['webhook_url'],
                        json={'text': 'LOKI Slack integration test'},
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as response:
                        return response.status == 200

            if 'bot_token' in self.credentials:
                # Test bot token with auth.test endpoint
                async with aiohttp.ClientSession() as session:
                    headers = {
                        'Authorization': f"Bearer {self.credentials['bot_token']}",
                    }
                    async with session.get(
                        f"{self.API_BASE_URL}/auth.test",
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as response:
                        result = await response.json()
                        return result.get('ok', False)

            return False
        except Exception as e:
            logger.error(f"Slack credential validation failed: {str(e)}")
            return False

    async def send_message(self, message: Dict[str, Any]) -> bool:
        """
        Send a message to Slack

        Args:
            message: Message payload

        Returns:
            True if message sent successfully
        """
        try:
            webhook_url = self.credentials.get('webhook_url')
            if not webhook_url:
                logger.error("Slack webhook URL not configured")
                return False

            payload = self._format_message(message)

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status != 200:
                        logger.error(f"Slack message failed: {response.status}")
                        return False

                    self.last_event_at = datetime.utcnow()
                    return True

        except Exception as e:
            logger.error(f"Failed to send Slack message: {str(e)}")
            return False

    async def on_validation_completed(self, validation_data: Dict[str, Any]) -> bool:
        """Handle validation completion event"""
        message = {
            'type': 'validation.completed',
            'title': 'Document Validation Completed',
            'color': '#36a64f' if validation_data.get('validation_status') == 'pass' else '#ff0000',
            'data': validation_data,
        }
        return await self.send_message(message)

    async def on_compliance_alert(self, alert_data: Dict[str, Any]) -> bool:
        """Handle compliance alert event"""
        message = {
            'type': 'compliance.alert',
            'title': f"Compliance Alert: {alert_data.get('alert_type', 'Unknown')}",
            'color': self._get_alert_color(alert_data.get('alert_level')),
            'data': alert_data,
        }
        return await self.send_message(message)

    async def on_document_processed(self, document_data: Dict[str, Any]) -> bool:
        """Handle document processed event"""
        message = {
            'type': 'document.processed',
            'title': f"Document Processed: {document_data.get('document_type', 'Unknown')}",
            'color': '#0099ff',
            'data': document_data,
        }
        return await self.send_message(message)

    async def on_batch_completed(self, batch_data: Dict[str, Any]) -> bool:
        """Handle batch completion event"""
        message = {
            'type': 'batch.completed',
            'title': f"Batch Completed: {batch_data.get('total_documents', 0)} documents",
            'color': '#36a64f',
            'data': batch_data,
        }
        return await self.send_message(message)

    def _format_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format message for Slack API

        Converts LOKI message format to Slack Block Kit format.

        Args:
            message: LOKI message payload

        Returns:
            Slack-formatted message
        """
        title = message.get('title', 'LOKI Notification')
        color = message.get('color', '#0099ff')
        data = message.get('data', {})

        blocks = [
            {
                'type': 'header',
                'text': {
                    'type': 'plain_text',
                    'text': title,
                    'emoji': True,
                }
            },
            {'type': 'divider'},
        ]

        # Add fields from data
        if isinstance(data, dict):
            fields = []
            for key, value in data.items():
                if not isinstance(value, (dict, list)):
                    fields.append({
                        'type': 'mrkdwn',
                        'text': f"*{key}:*\n{self._format_value(value)}",
                    })

            if fields:
                blocks.append({
                    'type': 'section',
                    'fields': fields[:10],  # Limit to 10 fields
                })

        # Add footer
        if self.config.get('include_footer'):
            footer_text = f"LOKI Interceptor | {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
            blocks.append({
                'type': 'context',
                'elements': [
                    {
                        'type': 'mrkdwn',
                        'text': footer_text,
                    }
                ]
            })

        return {
            'blocks': blocks,
            'attachments': [
                {
                    'color': color,
                    'blocks': blocks,
                }
            ]
        }

    @staticmethod
    def _format_value(value: Any) -> str:
        """Format a value for Slack display"""
        if isinstance(value, bool):
            return '✓ Yes' if value else '✗ No'
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, str):
            return value[:100]
        return str(value)[:100]

    @staticmethod
    def _get_alert_color(level: str) -> str:
        """Get alert color based on severity level"""
        colors = {
            'critical': '#ff0000',
            'high': '#ff6600',
            'medium': '#ffaa00',
            'low': '#00ff00',
        }
        return colors.get(level, '#0099ff')

    async def send_to_channel(
        self,
        channel: str,
        text: str,
        blocks: Optional[List[Dict[str, Any]]] = None,
        thread_ts: Optional[str] = None,
    ) -> bool:
        """
        Send a message to a specific Slack channel

        Args:
            channel: Channel name or ID
            text: Message text
            blocks: Optional Block Kit blocks
            thread_ts: Optional thread timestamp for replies

        Returns:
            True if message sent successfully
        """
        payload = {
            'channel': channel,
            'text': text,
        }

        if blocks:
            payload['blocks'] = blocks

        if thread_ts:
            payload['thread_ts'] = thread_ts

        message = {
            'type': 'generic',
            'data': payload,
        }

        return await self.send_message(message)
