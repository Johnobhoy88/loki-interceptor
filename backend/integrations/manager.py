"""
Integration Manager

Manages multiple third-party integrations and routes events to them.
Handles integration lifecycle, event routing, and error handling.
"""

import logging
from typing import Dict, Any, Optional, List, Type
from datetime import datetime

from .base import BaseIntegration
from .slack import SlackIntegration
from .teams import TeamsIntegration
from .email import EmailIntegration
from .zapier import ZapierIntegration


logger = logging.getLogger(__name__)


class IntegrationManager:
    """
    Manages all third-party integrations

    Features:
    - Integration lifecycle management
    - Event routing to subscribed integrations
    - Error handling and fallback
    - Metrics tracking
    - Configuration management
    """

    INTEGRATION_TYPES = {
        'slack': SlackIntegration,
        'teams': TeamsIntegration,
        'email': EmailIntegration,
        'zapier': ZapierIntegration,
    }

    def __init__(self):
        """Initialize integration manager"""
        self.integrations: Dict[str, BaseIntegration] = {}
        self.subscriptions: Dict[str, List[str]] = {}  # event_type -> [integration_names]
        self.metrics = {
            'total_events_routed': 0,
            'successful_deliveries': 0,
            'failed_deliveries': 0,
        }

    async def register_integration(
        self,
        name: str,
        integration_type: str,
        credentials: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
        event_subscriptions: Optional[List[str]] = None,
    ) -> bool:
        """
        Register a new integration

        Args:
            name: Integration name
            integration_type: Type of integration (slack, teams, email, zapier)
            credentials: Integration credentials
            config: Configuration options
            event_subscriptions: List of event types to subscribe to

        Returns:
            True if integration registered successfully
        """
        try:
            if integration_type not in self.INTEGRATION_TYPES:
                logger.error(f"Unknown integration type: {integration_type}")
                return False

            integration_class = self.INTEGRATION_TYPES[integration_type]

            # Create integration instance based on type
            if integration_type == 'slack':
                integration = SlackIntegration(
                    name=name,
                    webhook_url=credentials.get('webhook_url'),
                    bot_token=credentials.get('bot_token'),
                    config=config,
                )
            elif integration_type == 'teams':
                integration = TeamsIntegration(
                    name=name,
                    webhook_url=credentials.get('webhook_url'),
                    config=config,
                )
            elif integration_type == 'email':
                integration = EmailIntegration(
                    name=name,
                    smtp_host=credentials.get('smtp_host'),
                    smtp_port=credentials.get('smtp_port', 587),
                    smtp_username=credentials.get('smtp_username'),
                    smtp_password=credentials.get('smtp_password'),
                    from_address=credentials.get('from_address', 'noreply@loki.local'),
                    config=config,
                )
            elif integration_type == 'zapier':
                integration = ZapierIntegration(
                    name=name,
                    webhook_url=credentials.get('webhook_url'),
                    config=config,
                )
            else:
                return False

            # Connect to integration
            connected = await integration.connect()
            if not connected:
                logger.warning(f"Could not connect to integration: {name}")

            self.integrations[name] = integration

            # Subscribe to events
            if event_subscriptions:
                for event_type in event_subscriptions:
                    if event_type not in self.subscriptions:
                        self.subscriptions[event_type] = []
                    self.subscriptions[event_type].append(name)

            logger.info(f"Registered integration: {name} ({integration_type})")
            return True

        except Exception as e:
            logger.error(f"Failed to register integration {name}: {str(e)}")
            return False

    async def unregister_integration(self, name: str) -> bool:
        """
        Unregister an integration

        Args:
            name: Integration name

        Returns:
            True if integration unregistered successfully
        """
        try:
            if name not in self.integrations:
                return False

            integration = self.integrations[name]
            await integration.disconnect()

            del self.integrations[name]

            # Remove from subscriptions
            for event_type in list(self.subscriptions.keys()):
                if name in self.subscriptions[event_type]:
                    self.subscriptions[event_type].remove(name)
                if not self.subscriptions[event_type]:
                    del self.subscriptions[event_type]

            logger.info(f"Unregistered integration: {name}")
            return True

        except Exception as e:
            logger.error(f"Failed to unregister integration {name}: {str(e)}")
            return False

    async def route_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Route an event to all subscribed integrations

        Args:
            event_type: Type of event
            event_data: Event data payload

        Returns:
            Routing results
        """
        self.metrics['total_events_routed'] += 1

        subscribed_integrations = self.subscriptions.get(event_type, [])
        if not subscribed_integrations:
            logger.debug(f"No integrations subscribed to event: {event_type}")
            return {'event_type': event_type, 'routed_to': 0, 'results': {}}

        results = {}
        for integration_name in subscribed_integrations:
            if integration_name not in self.integrations:
                logger.warning(f"Integration not found: {integration_name}")
                results[integration_name] = {'success': False, 'error': 'Integration not found'}
                continue

            integration = self.integrations[integration_name]

            try:
                success = await integration.process_event(event_type, event_data)
                results[integration_name] = {'success': success}

                if success:
                    self.metrics['successful_deliveries'] += 1
                else:
                    self.metrics['failed_deliveries'] += 1

            except Exception as e:
                logger.error(f"Error routing event to {integration_name}: {str(e)}")
                results[integration_name] = {'success': False, 'error': str(e)}
                self.metrics['failed_deliveries'] += 1

        return {
            'event_type': event_type,
            'routed_to': len(subscribed_integrations),
            'results': results,
        }

    async def subscribe_integration_to_event(
        self,
        integration_name: str,
        event_type: str,
    ) -> bool:
        """
        Subscribe an integration to an event type

        Args:
            integration_name: Integration name
            event_type: Event type to subscribe to

        Returns:
            True if subscription successful
        """
        try:
            if integration_name not in self.integrations:
                logger.error(f"Integration not found: {integration_name}")
                return False

            if event_type not in self.subscriptions:
                self.subscriptions[event_type] = []

            if integration_name not in self.subscriptions[event_type]:
                self.subscriptions[event_type].append(integration_name)

            logger.info(f"Subscribed {integration_name} to {event_type}")
            return True

        except Exception as e:
            logger.error(f"Failed to subscribe integration: {str(e)}")
            return False

    async def unsubscribe_integration_from_event(
        self,
        integration_name: str,
        event_type: str,
    ) -> bool:
        """
        Unsubscribe an integration from an event type

        Args:
            integration_name: Integration name
            event_type: Event type to unsubscribe from

        Returns:
            True if unsubscription successful
        """
        try:
            if event_type not in self.subscriptions:
                return False

            if integration_name in self.subscriptions[event_type]:
                self.subscriptions[event_type].remove(integration_name)

            if not self.subscriptions[event_type]:
                del self.subscriptions[event_type]

            logger.info(f"Unsubscribed {integration_name} from {event_type}")
            return True

        except Exception as e:
            logger.error(f"Failed to unsubscribe integration: {str(e)}")
            return False

    def get_integration(self, name: str) -> Optional[BaseIntegration]:
        """
        Get an integration by name

        Args:
            name: Integration name

        Returns:
            Integration instance or None
        """
        return self.integrations.get(name)

    def list_integrations(
        self,
        integration_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List all integrations

        Args:
            integration_type: Filter by type (optional)

        Returns:
            List of integration information
        """
        integrations = []
        for name, integration in self.integrations.items():
            if integration_type and integration.integration_type != integration_type:
                continue

            integrations.append({
                'name': integration.name,
                'type': integration.integration_type,
                'status': integration.status.value,
                'created_at': integration.created_at.isoformat(),
                'last_event_at': integration.last_event_at.isoformat() if integration.last_event_at else None,
            })

        return integrations

    def get_subscriptions(self, integration_name: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Get subscriptions

        Args:
            integration_name: Filter by integration name (optional)

        Returns:
            Dictionary of subscriptions
        """
        if not integration_name:
            return self.subscriptions.copy()

        result = {}
        for event_type, integrations in self.subscriptions.items():
            if integration_name in integrations:
                result[event_type] = integrations

        return result

    def get_metrics(self) -> Dict[str, Any]:
        """Get manager metrics"""
        return {
            'total_integrations': len(self.integrations),
            'total_subscriptions': sum(len(subs) for subs in self.subscriptions.values()),
            'total_events_routed': self.metrics['total_events_routed'],
            'successful_deliveries': self.metrics['successful_deliveries'],
            'failed_deliveries': self.metrics['failed_deliveries'],
            'success_rate': (
                self.metrics['successful_deliveries'] /
                max(self.metrics['total_events_routed'], 1) * 100
            ) if self.metrics['total_events_routed'] > 0 else 0,
        }

    async def test_integration(
        self,
        integration_name: str,
        event_type: str = 'integration.event',
    ) -> Dict[str, Any]:
        """
        Test an integration with a sample event

        Args:
            integration_name: Integration name
            event_type: Event type to test with

        Returns:
            Test result
        """
        integration = self.get_integration(integration_name)
        if not integration:
            return {'success': False, 'error': 'Integration not found'}

        test_data = {
            'event_type': event_type,
            'source': 'test',
            'timestamp': datetime.utcnow().isoformat(),
            'payload': {
                'test': True,
                'message': f'Test event for {integration_name}',
            },
        }

        try:
            success = await integration.process_event(event_type, test_data)
            return {
                'success': success,
                'integration': integration_name,
                'event_type': event_type,
            }
        except Exception as e:
            return {
                'success': False,
                'integration': integration_name,
                'error': str(e),
            }
