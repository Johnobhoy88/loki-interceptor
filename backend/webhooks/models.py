"""
Webhook Database Models using SQLAlchemy ORM

Defines schema for webhooks, events, deliveries, and configurations.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum
import json
import hashlib

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Enum as SQLEnum,
    Float, JSON, ForeignKey, Table, Index, CheckConstraint, UniqueConstraint,
    event, func
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class EventType(str, Enum):
    """Webhook event types"""
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


class WebhookStatus(str, Enum):
    """Webhook operational status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"
    DELETED = "deleted"


class DeliveryStatus(str, Enum):
    """Delivery attempt status"""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    PERMANENT_FAILURE = "permanent_failure"


class RetryStrategy(str, Enum):
    """Retry strategy for failed deliveries"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_INTERVAL = "fixed_interval"
    NO_RETRY = "no_retry"


# Association table for webhook subscriptions
webhook_events = Table(
    'webhook_events',
    Base.metadata,
    Column('webhook_id', Integer, ForeignKey('webhooks.id', ondelete='CASCADE')),
    Column('event_type', String(255), index=True),
    Index('idx_webhook_events_webhook', 'webhook_id'),
    Index('idx_webhook_events_type', 'event_type'),
)


class Webhook(Base):
    """
    Webhook configuration entity
    Stores webhook URLs, event subscriptions, and metadata
    """
    __tablename__ = 'webhooks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Webhook URL and security
    url = Column(String(2048), nullable=False, unique=True, index=True)
    secret = Column(String(255), nullable=False)  # For signature verification

    # Status and control
    status = Column(SQLEnum(WebhookStatus), default=WebhookStatus.ACTIVE, index=True)

    # Event subscriptions (JSON array of event types)
    event_types = Column(JSON, default=list, nullable=False)

    # Retry configuration
    retry_strategy = Column(SQLEnum(RetryStrategy), default=RetryStrategy.EXPONENTIAL_BACKOFF)
    max_retries = Column(Integer, default=5, nullable=False)
    retry_delay_seconds = Column(Integer, default=60, nullable=False)

    # Rate limiting
    rate_limit_per_minute = Column(Integer, default=60, nullable=False)
    rate_limit_per_hour = Column(Integer, default=1000, nullable=False)

    # Metadata
    custom_headers = Column(JSON, default=dict, nullable=True)
    metadata = Column(JSON, default=dict, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_triggered_at = Column(DateTime, nullable=True)

    # Relationships
    deliveries = relationship("WebhookDelivery", back_populates="webhook", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        CheckConstraint('max_retries >= 0', name='check_max_retries_positive'),
        CheckConstraint('retry_delay_seconds >= 0', name='check_retry_delay_positive'),
        CheckConstraint('rate_limit_per_minute > 0', name='check_rate_limit_minute_positive'),
        CheckConstraint('rate_limit_per_hour > 0', name='check_rate_limit_hour_positive'),
        Index('idx_webhook_status_created', 'status', 'created_at'),
        Index('idx_webhook_url_status', 'url', 'status'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'url': self.url,
            'status': self.status.value if self.status else None,
            'event_types': self.event_types,
            'retry_strategy': self.retry_strategy.value if self.retry_strategy else None,
            'max_retries': self.max_retries,
            'retry_delay_seconds': self.retry_delay_seconds,
            'rate_limit_per_minute': self.rate_limit_per_minute,
            'rate_limit_per_hour': self.rate_limit_per_hour,
            'custom_headers': self.custom_headers,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_triggered_at': self.last_triggered_at.isoformat() if self.last_triggered_at else None,
        }


class WebhookDelivery(Base):
    """
    Webhook delivery attempt record
    Tracks each delivery attempt with request/response details
    """
    __tablename__ = 'webhook_deliveries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    webhook_id = Column(Integer, ForeignKey('webhooks.id', ondelete='CASCADE'), nullable=False, index=True)

    # Event information
    event_type = Column(String(255), nullable=False, index=True)
    event_data = Column(JSON, nullable=False)
    event_id = Column(String(255), nullable=False, unique=True, index=True)  # UUID for idempotency

    # Delivery attempt
    attempt_number = Column(Integer, default=1, nullable=False)
    status = Column(SQLEnum(DeliveryStatus), default=DeliveryStatus.PENDING, nullable=False, index=True)

    # Request details
    request_headers = Column(JSON, nullable=True)
    request_body = Column(JSON, nullable=True)
    signature = Column(String(512), nullable=True)  # HMAC-SHA256 signature

    # Response details
    response_status_code = Column(Integer, nullable=True)
    response_headers = Column(JSON, nullable=True)
    response_body = Column(Text, nullable=True)

    # Timing
    sent_at = Column(DateTime, nullable=True)
    responded_at = Column(DateTime, nullable=True)
    duration_ms = Column(Float, nullable=True)

    # Retry tracking
    next_retry_at = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    webhook = relationship("Webhook", back_populates="deliveries")

    # Constraints
    __table_args__ = (
        CheckConstraint('attempt_number >= 1', name='check_attempt_number_positive'),
        CheckConstraint('duration_ms >= 0', name='check_duration_positive'),
        Index('idx_delivery_webhook_status', 'webhook_id', 'status'),
        Index('idx_delivery_event_type_created', 'event_type', 'created_at'),
        Index('idx_delivery_next_retry', 'next_retry_at', 'status'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'webhook_id': self.webhook_id,
            'event_type': self.event_type,
            'event_id': self.event_id,
            'attempt_number': self.attempt_number,
            'status': self.status.value if self.status else None,
            'response_status_code': self.response_status_code,
            'duration_ms': self.duration_ms,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'responded_at': self.responded_at.isoformat() if self.responded_at else None,
            'last_error': self.last_error,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class WebhookEvent(Base):
    """
    Webhook event record
    Represents an event that triggered webhook deliveries
    """
    __tablename__ = 'webhook_events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(255), nullable=False, unique=True, index=True)  # UUID
    event_type = Column(String(255), nullable=False, index=True)

    # Event context
    source = Column(String(255), nullable=True)  # e.g., 'validation', 'correction', 'system'
    source_id = Column(String(255), nullable=True, index=True)  # Related document/validation ID

    # Payload
    payload = Column(JSON, nullable=False)

    # Delivery stats
    total_deliveries = Column(Integer, default=0, nullable=False)
    successful_deliveries = Column(Integer, default=0, nullable=False)
    failed_deliveries = Column(Integer, default=0, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    processed_at = Column(DateTime, nullable=True)

    # Constraints
    __table_args__ = (
        CheckConstraint('total_deliveries >= 0', name='check_total_deliveries_positive'),
        CheckConstraint('successful_deliveries >= 0', name='check_successful_deliveries_positive'),
        CheckConstraint('failed_deliveries >= 0', name='check_failed_deliveries_positive'),
        Index('idx_event_source_created', 'source', 'created_at'),
        Index('idx_event_source_id', 'source_id'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'event_id': self.event_id,
            'event_type': self.event_type,
            'source': self.source,
            'source_id': self.source_id,
            'total_deliveries': self.total_deliveries,
            'successful_deliveries': self.successful_deliveries,
            'failed_deliveries': self.failed_deliveries,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
        }


class WebhookAnalytics(Base):
    """
    Analytics record for webhook performance tracking
    Aggregated metrics for monitoring and optimization
    """
    __tablename__ = 'webhook_analytics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    webhook_id = Column(Integer, ForeignKey('webhooks.id', ondelete='CASCADE'), nullable=False, index=True)

    # Time period
    period_date = Column(DateTime, nullable=False, index=True)  # Date of metrics

    # Delivery metrics
    total_events = Column(Integer, default=0, nullable=False)
    successful_deliveries = Column(Integer, default=0, nullable=False)
    failed_deliveries = Column(Integer, default=0, nullable=False)
    retry_count = Column(Integer, default=0, nullable=False)

    # Performance metrics
    avg_response_time_ms = Column(Float, nullable=True)
    min_response_time_ms = Column(Float, nullable=True)
    max_response_time_ms = Column(Float, nullable=True)
    p95_response_time_ms = Column(Float, nullable=True)

    # Error metrics
    http_4xx_errors = Column(Integer, default=0, nullable=False)
    http_5xx_errors = Column(Integer, default=0, nullable=False)
    timeout_errors = Column(Integer, default=0, nullable=False)
    network_errors = Column(Integer, default=0, nullable=False)

    # Success rate
    success_rate = Column(Float, default=0.0, nullable=False)  # Percentage (0-100)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Constraints
    __table_args__ = (
        UniqueConstraint('webhook_id', 'period_date', name='uq_webhook_period'),
        CheckConstraint('total_events >= 0', name='check_analytics_total_events'),
        CheckConstraint('success_rate >= 0 AND success_rate <= 100', name='check_success_rate_range'),
        Index('idx_analytics_period', 'period_date'),
        Index('idx_analytics_webhook_period', 'webhook_id', 'period_date'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'webhook_id': self.webhook_id,
            'period_date': self.period_date.isoformat() if self.period_date else None,
            'total_events': self.total_events,
            'successful_deliveries': self.successful_deliveries,
            'failed_deliveries': self.failed_deliveries,
            'retry_count': self.retry_count,
            'avg_response_time_ms': self.avg_response_time_ms,
            'success_rate': self.success_rate,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
