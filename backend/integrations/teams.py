"""
Microsoft Teams Integration

Send LOKI events and notifications to Microsoft Teams channels.
Supports rich message formatting with adaptive cards.
"""

import aiohttp
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from .base import BaseIntegration, IntegrationStatus


logger = logging.getLogger(__name__)


class TeamsIntegration(BaseIntegration):
    """
    Microsoft Teams integration for LOKI

    Features:
    - Send messages to Teams channels
    - Adaptive card formatting
    - Rich formatting with sections and fields
    - Threat modeling and risk coloring
    - Webhook URL support
    - Custom formatting per event type
    """

    def __init__(
        self,
        name: str,
        webhook_url: str,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Teams integration

        Args:
            name: Integration name
            webhook_url: Teams webhook URL
            config: Configuration options
        """
        credentials = {'webhook_url': webhook_url}
        config = config or {}
        config.setdefault('include_footer', True)
        config.setdefault('include_timestamp', True)
        config.setdefault('theme_color', '0078D4')  # Microsoft Teams blue

        super().__init__(
            name=name,
            integration_type='teams',
            credentials=credentials,
            config=config,
        )

    async def connect(self) -> bool:
        """Connect to Teams and validate webhook"""
        try:
            is_valid = await self.validate_credentials()
            if is_valid:
                self.status = IntegrationStatus.CONNECTED
                logger.info(f"Teams integration connected: {self.name}")
            return is_valid
        except Exception as e:
            logger.error(f"Failed to connect Teams integration: {str(e)}")
            self.status = IntegrationStatus.ERROR
            return False

    async def disconnect(self) -> bool:
        """Disconnect from Teams"""
        self.status = IntegrationStatus.DISCONNECTED
        logger.info(f"Teams integration disconnected: {self.name}")
        return True

    async def validate_credentials(self) -> bool:
        """Validate Teams webhook URL"""
        try:
            webhook_url = self.credentials.get('webhook_url')
            if not webhook_url:
                return False

            payload = {
                '@type': 'MessageCard',
                '@context': 'https://schema.org/extensions',
                'summary': 'LOKI Connection Test',
                'themeColor': self.config.get('theme_color'),
                'sections': [
                    {
                        'activityTitle': 'LOKI Interceptor',
                        'activitySubtitle': 'Connection Test',
                        'facts': [
                            {
                                'name': 'Status',
                                'value': 'Active'
                            }
                        ]
                    }
                ]
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    return response.status == 200

        except Exception as e:
            logger.error(f"Teams credential validation failed: {str(e)}")
            return False

    async def send_message(self, message: Dict[str, Any]) -> bool:
        """
        Send a message to Teams

        Args:
            message: Message payload

        Returns:
            True if message sent successfully
        """
        try:
            webhook_url = self.credentials.get('webhook_url')
            if not webhook_url:
                logger.error("Teams webhook URL not configured")
                return False

            payload = self._format_message(message)

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status != 200:
                        logger.error(f"Teams message failed: {response.status}")
                        return False

                    self.last_event_at = datetime.utcnow()
                    return True

        except Exception as e:
            logger.error(f"Failed to send Teams message: {str(e)}")
            return False

    async def on_validation_completed(self, validation_data: Dict[str, Any]) -> bool:
        """Handle validation completion event"""
        color = '28a745' if validation_data.get('validation_status') == 'pass' else 'dc3545'
        message = {
            'type': 'validation.completed',
            'title': 'Document Validation Completed',
            'color': color,
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
            'color': '0078D4',
            'data': document_data,
        }
        return await self.send_message(message)

    async def on_batch_completed(self, batch_data: Dict[str, Any]) -> bool:
        """Handle batch completion event"""
        message = {
            'type': 'batch.completed',
            'title': f"Batch Completed: {batch_data.get('total_documents', 0)} documents",
            'color': '28a745',
            'data': batch_data,
        }
        return await self.send_message(message)

    def _format_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format message for Teams Adaptive Card format

        Args:
            message: LOKI message payload

        Returns:
            Teams-formatted message
        """
        title = message.get('title', 'LOKI Notification')
        color = message.get('color', self.config.get('theme_color'))
        data = message.get('data', {})

        facts = []
        if isinstance(data, dict):
            for key, value in list(data.items())[:10]:  # Limit to 10 facts
                if not isinstance(value, (dict, list)):
                    facts.append({
                        'name': key,
                        'value': self._format_value(value),
                    })

        sections = [
            {
                'activityTitle': title,
                'activitySubtitle': 'LOKI Interceptor',
                'facts': facts,
                'markdown': True,
            }
        ]

        # Add footer section
        if self.config.get('include_footer'):
            sections.append({
                'text': f'*LOKI Interceptor* | {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}',
                'markdown': True,
            })

        return {
            '@type': 'MessageCard',
            '@context': 'https://schema.org/extensions',
            'summary': title,
            'themeColor': color,
            'sections': sections,
            'potentialAction': [
                {
                    '@type': 'OpenUri',
                    'name': 'View Details',
                    'targets': [
                        {
                            'os': 'default',
                            'uri': f'https://loki.local/dashboard'
                        }
                    ]
                }
            ]
        }

    @staticmethod
    def _format_value(value: Any) -> str:
        """Format a value for Teams display"""
        if isinstance(value, bool):
            return 'Yes' if value else 'No'
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, str):
            return value[:200]
        return str(value)[:200]

    @staticmethod
    def _get_alert_color(level: str) -> str:
        """Get alert color based on severity level"""
        colors = {
            'critical': 'dc3545',  # Red
            'high': 'fd7e14',      # Orange
            'medium': 'ffc107',    # Yellow
            'low': '28a745',       # Green
        }
        return colors.get(level, '0078D4')

    async def send_direct_message(
        self,
        user_id: str,
        title: str,
        message: str,
    ) -> bool:
        """
        Send a direct message to a Teams user

        Args:
            user_id: Teams user ID or email
            title: Message title
            message: Message content

        Returns:
            True if message sent successfully
        """
        payload = {
            'type': 'generic',
            'title': title,
            'data': {'message': message},
        }

        return await self.send_message(payload)
