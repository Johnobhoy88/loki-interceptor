"""
Third-Party Integrations Package

Integration connectors for Slack, Microsoft Teams, Email, Zapier, and more.
Enables LOKI to send notifications and data to external systems.
"""

from .base import BaseIntegration
from .slack import SlackIntegration
from .teams import TeamsIntegration
from .email import EmailIntegration
from .zapier import ZapierIntegration
from .manager import IntegrationManager

__all__ = [
    'BaseIntegration',
    'SlackIntegration',
    'TeamsIntegration',
    'EmailIntegration',
    'ZapierIntegration',
    'IntegrationManager',
]
