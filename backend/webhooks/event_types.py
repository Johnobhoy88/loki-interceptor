"""
Webhook Event Types and Payload Definitions

Defines event schemas and examples for all webhook event types.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
import uuid
import json


class EventType(str, Enum):
    """Webhook event type enumeration"""
    VALIDATION_COMPLETED = "validation.completed"
    VALIDATION_FAILED = "validation.failed"
    CORRECTION_APPLIED = "correction.applied"
    DOCUMENT_PROCESSED = "document.processed"
    COMPLIANCE_ALERT = "compliance.alert"
    SYSTEM_ERROR = "system.error"
    BATCH_COMPLETED = "batch.completed"
    REPORT_GENERATED = "report.generated"
    USER_ACTION = "user.action"
    INTEGRATION_EVENT = "integration.event"


class WebhookEvent:
    """
    Base webhook event class
    Encapsulates event data and metadata
    """

    def __init__(
        self,
        event_type: EventType,
        source: str,
        payload: Dict[str, Any],
        source_id: Optional[str] = None,
        event_id: Optional[str] = None,
    ):
        """
        Initialize a webhook event

        Args:
            event_type: Type of event
            source: Source system that generated the event
            payload: Event payload data
            source_id: ID of the resource that triggered the event
            event_id: Unique event identifier (auto-generated if not provided)
        """
        self.event_id = event_id or str(uuid.uuid4())
        self.event_type = event_type
        self.source = source
        self.source_id = source_id
        self.payload = payload
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value if isinstance(self.event_type, EventType) else self.event_type,
            'source': self.source,
            'source_id': self.source_id,
            'timestamp': self.timestamp,
            'payload': self.payload,
        }

    def to_json(self) -> str:
        """Convert event to JSON string"""
        return json.dumps(self.to_dict(), default=str)


class ValidationCompletedEvent(WebhookEvent):
    """Event fired when document validation completes successfully"""

    def __init__(
        self,
        source_id: str,
        document_id: str,
        validation_status: str,
        gates_passed: int,
        gates_failed: int,
        issues: List[Dict[str, Any]],
        processing_time_ms: float,
        event_id: Optional[str] = None,
    ):
        payload = {
            'document_id': document_id,
            'validation_status': validation_status,
            'gates_passed': gates_passed,
            'gates_failed': gates_failed,
            'total_gates': gates_passed + gates_failed,
            'issues': issues,
            'processing_time_ms': processing_time_ms,
            'success_rate': (gates_passed / (gates_passed + gates_failed) * 100) if (gates_passed + gates_failed) > 0 else 0,
        }
        super().__init__(
            event_type=EventType.VALIDATION_COMPLETED,
            source='validation',
            payload=payload,
            source_id=source_id,
            event_id=event_id,
        )


class ValidationFailedEvent(WebhookEvent):
    """Event fired when document validation fails"""

    def __init__(
        self,
        source_id: str,
        document_id: str,
        error_message: str,
        error_code: Optional[str] = None,
        stack_trace: Optional[str] = None,
        event_id: Optional[str] = None,
    ):
        payload = {
            'document_id': document_id,
            'error_message': error_message,
            'error_code': error_code,
            'stack_trace': stack_trace,
        }
        super().__init__(
            event_type=EventType.VALIDATION_FAILED,
            source='validation',
            payload=payload,
            source_id=source_id,
            event_id=event_id,
        )


class CorrectionAppliedEvent(WebhookEvent):
    """Event fired when corrections are applied to a document"""

    def __init__(
        self,
        source_id: str,
        document_id: str,
        corrections_count: int,
        changes: List[Dict[str, Any]],
        before_text: str,
        after_text: str,
        confidence_score: float,
        event_id: Optional[str] = None,
    ):
        payload = {
            'document_id': document_id,
            'corrections_count': corrections_count,
            'changes': changes,
            'before_text': before_text[:500],  # First 500 chars
            'after_text': after_text[:500],
            'confidence_score': confidence_score,
            'total_change_percentage': (len(changes) / max(len(before_text.split()), 1)) * 100,
        }
        super().__init__(
            event_type=EventType.CORRECTION_APPLIED,
            source='correction',
            payload=payload,
            source_id=source_id,
            event_id=event_id,
        )


class DocumentProcessedEvent(WebhookEvent):
    """Event fired when a document is fully processed"""

    def __init__(
        self,
        source_id: str,
        document_id: str,
        document_type: str,
        file_size_bytes: int,
        processing_time_ms: float,
        validation_results: Dict[str, Any],
        corrections_applied: bool,
        event_id: Optional[str] = None,
    ):
        payload = {
            'document_id': document_id,
            'document_type': document_type,
            'file_size_bytes': file_size_bytes,
            'processing_time_ms': processing_time_ms,
            'validation_results': validation_results,
            'corrections_applied': corrections_applied,
        }
        super().__init__(
            event_type=EventType.DOCUMENT_PROCESSED,
            source='document',
            payload=payload,
            source_id=source_id,
            event_id=event_id,
        )


class ComplianceAlertEvent(WebhookEvent):
    """Event fired when compliance violations are detected"""

    def __init__(
        self,
        source_id: str,
        alert_level: str,  # 'critical', 'high', 'medium', 'low'
        alert_type: str,
        message: str,
        affected_documents: List[str],
        recommended_actions: List[str],
        event_id: Optional[str] = None,
    ):
        payload = {
            'alert_level': alert_level,
            'alert_type': alert_type,
            'message': message,
            'affected_documents': affected_documents,
            'recommended_actions': recommended_actions,
            'affected_document_count': len(affected_documents),
        }
        super().__init__(
            event_type=EventType.COMPLIANCE_ALERT,
            source='compliance',
            payload=payload,
            source_id=source_id,
            event_id=event_id,
        )


class BatchCompletedEvent(WebhookEvent):
    """Event fired when a batch processing job completes"""

    def __init__(
        self,
        source_id: str,
        batch_id: str,
        total_documents: int,
        processed_documents: int,
        failed_documents: int,
        processing_time_ms: float,
        results_summary: Dict[str, Any],
        event_id: Optional[str] = None,
    ):
        payload = {
            'batch_id': batch_id,
            'total_documents': total_documents,
            'processed_documents': processed_documents,
            'failed_documents': failed_documents,
            'success_rate': (processed_documents / total_documents * 100) if total_documents > 0 else 0,
            'processing_time_ms': processing_time_ms,
            'avg_time_per_document_ms': processing_time_ms / processed_documents if processed_documents > 0 else 0,
            'results_summary': results_summary,
        }
        super().__init__(
            event_type=EventType.BATCH_COMPLETED,
            source='batch',
            payload=payload,
            source_id=source_id,
            event_id=event_id,
        )


class ReportGeneratedEvent(WebhookEvent):
    """Event fired when a report is generated"""

    def __init__(
        self,
        source_id: str,
        report_id: str,
        report_type: str,
        report_url: str,
        file_size_bytes: int,
        document_count: int,
        event_id: Optional[str] = None,
    ):
        payload = {
            'report_id': report_id,
            'report_type': report_type,
            'report_url': report_url,
            'file_size_bytes': file_size_bytes,
            'document_count': document_count,
        }
        super().__init__(
            event_type=EventType.REPORT_GENERATED,
            source='reporting',
            payload=payload,
            source_id=source_id,
            event_id=event_id,
        )


class SystemErrorEvent(WebhookEvent):
    """Event fired when a system error occurs"""

    def __init__(
        self,
        source_id: str,
        error_code: str,
        error_message: str,
        component: str,
        severity: str,  # 'critical', 'high', 'medium', 'low'
        stack_trace: Optional[str] = None,
        event_id: Optional[str] = None,
    ):
        payload = {
            'error_code': error_code,
            'error_message': error_message,
            'component': component,
            'severity': severity,
            'stack_trace': stack_trace,
        }
        super().__init__(
            event_type=EventType.SYSTEM_ERROR,
            source='system',
            payload=payload,
            source_id=source_id,
            event_id=event_id,
        )


# Event factory
def create_event(
    event_type: str,
    source: str,
    payload: Dict[str, Any],
    source_id: Optional[str] = None,
    event_id: Optional[str] = None,
) -> WebhookEvent:
    """
    Factory function to create webhook events

    Args:
        event_type: Type of event (string or EventType enum)
        source: Source system
        payload: Event payload
        source_id: Source resource ID
        event_id: Event ID

    Returns:
        WebhookEvent instance
    """
    # Convert string to enum if needed
    if isinstance(event_type, str):
        try:
            event_type = EventType[event_type.upper().replace('.', '_')]
        except KeyError:
            event_type = EventType.INTEGRATION_EVENT

    return WebhookEvent(
        event_type=event_type,
        source=source,
        payload=payload,
        source_id=source_id,
        event_id=event_id,
    )
