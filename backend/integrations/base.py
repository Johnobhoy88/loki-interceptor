"""
Base Integration Class

Abstract base class for all third-party integrations.
Defines common interface and patterns for integration connectors.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


class IntegrationStatus(str, Enum):
    """Integration operational status"""
    CONFIGURED = "configured"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    PAUSED = "paused"


class IntegrationEvent(str, Enum):
    """Integration event types"""
    VALIDATION_RESULT = "validation_result"
    COMPLIANCE_ALERT = "compliance_alert"
    DOCUMENT_PROCESSED = "document_processed"
    CORRECTION_APPLIED = "correction_applied"
    BATCH_COMPLETED = "batch_completed"
    ERROR_OCCURRED = "error_occurred"
    REPORT_GENERATED = "report_generated"


class BaseIntegration(ABC):
    """
    Abstract base class for third-party integrations

    All integrations must inherit from this class and implement
    the required abstract methods.
    """

    def __init__(
        self,
        name: str,
        integration_type: str,
        credentials: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize base integration

        Args:
            name: Integration name
            integration_type: Type of integration (e.g., 'slack', 'email')
            credentials: Integration credentials/API keys
            config: Configuration options
        """
        self.name = name
        self.integration_type = integration_type
        self.credentials = credentials
        self.config = config or {}
        self.status = IntegrationStatus.CONFIGURED
        self.created_at = datetime.utcnow()
        self.last_event_at: Optional[datetime] = None

    @abstractmethod
    async def connect(self) -> bool:
        """
        Connect to the integration

        Must be implemented by subclasses.

        Returns:
            True if connection successful
        """
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Disconnect from the integration

        Must be implemented by subclasses.

        Returns:
            True if disconnection successful
        """
        pass

    @abstractmethod
    async def send_message(self, message: Dict[str, Any]) -> bool:
        """
        Send a message/notification to the integration

        Must be implemented by subclasses.

        Args:
            message: Message payload

        Returns:
            True if message sent successfully
        """
        pass

    @abstractmethod
    async def validate_credentials(self) -> bool:
        """
        Validate that credentials are correct

        Must be implemented by subclasses.

        Returns:
            True if credentials are valid
        """
        pass

    async def on_validation_completed(self, validation_data: Dict[str, Any]) -> bool:
        """
        Handle validation completion event

        Can be overridden by subclasses for custom behavior.

        Args:
            validation_data: Validation result data

        Returns:
            True if event handled successfully
        """
        logger.debug(f"{self.name}: Validation completed event received")
        return True

    async def on_compliance_alert(self, alert_data: Dict[str, Any]) -> bool:
        """
        Handle compliance alert event

        Can be overridden by subclasses for custom behavior.

        Args:
            alert_data: Alert data

        Returns:
            True if event handled successfully
        """
        logger.debug(f"{self.name}: Compliance alert event received")
        return True

    async def on_document_processed(self, document_data: Dict[str, Any]) -> bool:
        """
        Handle document processed event

        Can be overridden by subclasses for custom behavior.

        Args:
            document_data: Document data

        Returns:
            True if event handled successfully
        """
        logger.debug(f"{self.name}: Document processed event received")
        return True

    async def on_correction_applied(self, correction_data: Dict[str, Any]) -> bool:
        """
        Handle correction applied event

        Can be overridden by subclasses for custom behavior.

        Args:
            correction_data: Correction data

        Returns:
            True if event handled successfully
        """
        logger.debug(f"{self.name}: Correction applied event received")
        return True

    async def on_batch_completed(self, batch_data: Dict[str, Any]) -> bool:
        """
        Handle batch completion event

        Can be overridden by subclasses for custom behavior.

        Args:
            batch_data: Batch result data

        Returns:
            True if event handled successfully
        """
        logger.debug(f"{self.name}: Batch completed event received")
        return True

    async def on_error(self, error_data: Dict[str, Any]) -> bool:
        """
        Handle error event

        Can be overridden by subclasses for custom behavior.

        Args:
            error_data: Error information

        Returns:
            True if event handled successfully
        """
        logger.debug(f"{self.name}: Error event received")
        return True

    async def process_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
    ) -> bool:
        """
        Process an event from the webhook system

        Routes events to appropriate handlers.

        Args:
            event_type: Type of event
            event_data: Event data payload

        Returns:
            True if event processed successfully
        """
        self.last_event_at = datetime.utcnow()

        handlers = {
            'validation.completed': self.on_validation_completed,
            'compliance.alert': self.on_compliance_alert,
            'document.processed': self.on_document_processed,
            'correction.applied': self.on_correction_applied,
            'batch.completed': self.on_batch_completed,
            'system.error': self.on_error,
        }

        handler = handlers.get(event_type)
        if handler:
            try:
                return await handler(event_data)
            except Exception as e:
                logger.error(f"{self.name}: Error processing {event_type}: {str(e)}")
                return False

        logger.warning(f"{self.name}: Unknown event type: {event_type}")
        return False

    def get_status(self) -> Dict[str, Any]:
        """
        Get integration status information

        Returns:
            Status dictionary
        """
        return {
            'name': self.name,
            'type': self.integration_type,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'last_event_at': self.last_event_at.isoformat() if self.last_event_at else None,
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert integration to dictionary

        Returns:
            Dictionary representation
        """
        return {
            'name': self.name,
            'type': self.integration_type,
            'status': self.status.value,
            'config': self.config,
            'created_at': self.created_at.isoformat(),
            'last_event_at': self.last_event_at.isoformat() if self.last_event_at else None,
        }
