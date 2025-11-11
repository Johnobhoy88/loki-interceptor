"""
SQLAlchemy ORM Models for LOKI Interceptor
Enterprise-grade data models with versioning, audit trails, and relationships
"""
from __future__ import annotations

import json
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from enum import Enum

from sqlalchemy import (
    Boolean, Column, DateTime, Enum as SQLEnum, Float, ForeignKey,
    Index, Integer, JSON, String, Text, Table, UniqueConstraint,
    CheckConstraint, event
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func

Base = declarative_base()


# Enumerations
class DocumentType(str, Enum):
    """Document type classification"""
    EMAIL = "email"
    CONTRACT = "contract"
    MARKETING = "marketing"
    FINANCIAL = "financial"
    LEGAL = "legal"
    MEDICAL = "medical"
    INSURANCE = "insurance"
    CUSTOMER_COMMS = "customer_comms"
    INTERNAL = "internal"
    OTHER = "other"


class RiskLevel(str, Enum):
    """Risk assessment levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class ValidationStatus(str, Enum):
    """Validation execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class GateStatus(str, Enum):
    """Gate validation result status"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIP = "skip"
    ERROR = "error"


class CorrectionStatus(str, Enum):
    """Correction application status"""
    PENDING = "pending"
    APPLIED = "applied"
    REJECTED = "rejected"
    REVERTED = "reverted"


class RetentionAction(str, Enum):
    """Data retention policy actions"""
    ARCHIVE = "archive"
    DELETE = "delete"
    ANONYMIZE = "anonymize"
    COMPRESS = "compress"


# Association tables for many-to-many relationships
document_tags = Table(
    'document_tags',
    Base.metadata,
    Column('document_id', Integer, ForeignKey('documents.id', ondelete='CASCADE')),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE')),
    Index('idx_doc_tags_document', 'document_id'),
    Index('idx_doc_tags_tag', 'tag_id')
)


class Document(Base):
    """
    Core document entity with versioning and metadata
    Stores all documents processed through LOKI
    """
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Document identification
    content_hash = Column(String(64), nullable=False, index=True, unique=True,
                         comment="SHA-256 hash of document content")
    document_type = Column(SQLEnum(DocumentType), nullable=False, index=True,
                          default=DocumentType.OTHER)

    # Content storage
    content = Column(Text, nullable=False, comment="Original document content")
    content_length = Column(Integer, nullable=False, default=0)

    # Metadata
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    source = Column(String(500), nullable=True, comment="Source system or file path")
    language = Column(String(10), nullable=True, default='en')
    metadata_json = Column(JSON, nullable=True, comment="Additional metadata")

    # Client/tenant information
    client_id = Column(String(100), nullable=False, index=True, default='default')
    tenant_id = Column(String(100), nullable=True, index=True)
    user_id = Column(String(100), nullable=True, index=True)

    # Version control
    version = Column(Integer, nullable=False, default=1)
    parent_id = Column(Integer, ForeignKey('documents.id', ondelete='SET NULL'),
                      nullable=True, index=True)
    is_latest = Column(Boolean, nullable=False, default=True, index=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow,
                       onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True, index=True)

    # Soft delete flag
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)

    # Relationships
    validations = relationship('Validation', back_populates='document',
                              cascade='all, delete-orphan')
    corrections = relationship('Correction', back_populates='document',
                              cascade='all, delete-orphan')
    audit_trails = relationship('AuditTrail', back_populates='document',
                               cascade='all, delete-orphan')
    parent = relationship('Document', remote_side=[id], backref='versions')
    tags = relationship('Tag', secondary=document_tags, back_populates='documents')

    # Indexes
    __table_args__ = (
        Index('idx_documents_client_created', 'client_id', 'created_at'),
        Index('idx_documents_type_risk', 'document_type', 'created_at'),
        Index('idx_documents_tenant_type', 'tenant_id', 'document_type'),
        Index('idx_documents_latest', 'is_latest', 'is_deleted'),
        {'comment': 'Documents processed through LOKI Interceptor'}
    )

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, type={self.document_type}, version={self.version})>"

    def to_dict(self, include_content: bool = False) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        data = {
            'id': self.id,
            'content_hash': self.content_hash,
            'document_type': self.document_type.value,
            'content_length': self.content_length,
            'title': self.title,
            'description': self.description,
            'source': self.source,
            'language': self.language,
            'client_id': self.client_id,
            'tenant_id': self.tenant_id,
            'user_id': self.user_id,
            'version': self.version,
            'is_latest': self.is_latest,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'metadata': self.metadata_json
        }
        if include_content:
            data['content'] = self.content
        return data


class Validation(Base):
    """
    Validation execution record
    Tracks each validation run with its configuration and status
    """
    __tablename__ = 'validations'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Document reference
    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'),
                        nullable=False, index=True)

    # Validation configuration
    modules_used = Column(JSON, nullable=False, comment="List of validation modules")
    config = Column(JSON, nullable=True, comment="Validation configuration")

    # Status and timing
    status = Column(SQLEnum(ValidationStatus), nullable=False,
                   default=ValidationStatus.PENDING, index=True)
    started_at = Column(DateTime, nullable=True, index=True)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True, comment="Execution time in milliseconds")

    # Results summary
    overall_risk = Column(SQLEnum(RiskLevel), nullable=True, index=True)
    critical_count = Column(Integer, nullable=False, default=0)
    high_count = Column(Integer, nullable=False, default=0)
    medium_count = Column(Integer, nullable=False, default=0)
    low_count = Column(Integer, nullable=False, default=0)
    pass_count = Column(Integer, nullable=False, default=0)
    fail_count = Column(Integer, nullable=False, default=0)
    warning_count = Column(Integer, nullable=False, default=0)

    # Request tracking
    request_hash = Column(String(64), nullable=False, index=True,
                         comment="Unique hash for this validation request")
    client_id = Column(String(100), nullable=False, index=True)
    user_id = Column(String(100), nullable=True, index=True)

    # Error tracking
    error_message = Column(Text, nullable=True)
    error_traceback = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    document = relationship('Document', back_populates='validations')
    results = relationship('ValidationResult', back_populates='validation',
                          cascade='all, delete-orphan')
    corrections = relationship('Correction', back_populates='validation',
                              cascade='all, delete-orphan')
    audit_trails = relationship('AuditTrail', back_populates='validation',
                               cascade='all, delete-orphan')

    # Indexes
    __table_args__ = (
        Index('idx_validations_doc_created', 'document_id', 'created_at'),
        Index('idx_validations_status_risk', 'status', 'overall_risk'),
        Index('idx_validations_client_date', 'client_id', 'created_at'),
        Index('idx_validations_risk_counts', 'overall_risk', 'critical_count', 'high_count'),
        {'comment': 'Validation execution records'}
    )

    def __repr__(self) -> str:
        return f"<Validation(id={self.id}, doc_id={self.document_id}, status={self.status})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'id': self.id,
            'document_id': self.document_id,
            'modules_used': self.modules_used,
            'status': self.status.value,
            'overall_risk': self.overall_risk.value if self.overall_risk else None,
            'critical_count': self.critical_count,
            'high_count': self.high_count,
            'medium_count': self.medium_count,
            'low_count': self.low_count,
            'pass_count': self.pass_count,
            'fail_count': self.fail_count,
            'warning_count': self.warning_count,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_ms': self.duration_ms,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ValidationResult(Base):
    """
    Individual gate/check result within a validation
    Stores detailed findings from each validation gate
    """
    __tablename__ = 'validation_results'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Validation reference
    validation_id = Column(Integer, ForeignKey('validations.id', ondelete='CASCADE'),
                          nullable=False, index=True)

    # Gate identification
    scope = Column(String(50), nullable=False, index=True,
                  comment="Scope: module, universal, analyzer, cross")
    module_id = Column(String(100), nullable=True, index=True)
    gate_id = Column(String(100), nullable=False, index=True)
    gate_key = Column(String(255), nullable=False, index=True,
                     comment="Full gate identifier (e.g., gdpr_uk.data_minimization)")

    # Result details
    status = Column(SQLEnum(GateStatus), nullable=False, index=True)
    severity = Column(SQLEnum(RiskLevel), nullable=True, index=True)
    message = Column(Text, nullable=True)
    suggestion = Column(Text, nullable=True)
    legal_source = Column(Text, nullable=True)

    # Additional metadata
    confidence_score = Column(Float, nullable=True,
                             comment="Confidence in result (0.0-1.0)")
    evidence = Column(JSON, nullable=True, comment="Supporting evidence")
    metadata_json = Column(JSON, nullable=True)

    # Version tracking
    gate_version = Column(String(20), nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    validation = relationship('Validation', back_populates='results')

    # Indexes
    __table_args__ = (
        Index('idx_results_validation_scope', 'validation_id', 'scope'),
        Index('idx_results_gate_status', 'gate_key', 'status'),
        Index('idx_results_severity_status', 'severity', 'status'),
        Index('idx_results_module_gate', 'module_id', 'gate_id'),
        {'comment': 'Individual validation gate results'}
    )

    def __repr__(self) -> str:
        return f"<ValidationResult(id={self.id}, gate={self.gate_key}, status={self.status})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'id': self.id,
            'validation_id': self.validation_id,
            'scope': self.scope,
            'module_id': self.module_id,
            'gate_id': self.gate_id,
            'gate_key': self.gate_key,
            'status': self.status.value,
            'severity': self.severity.value if self.severity else None,
            'message': self.message,
            'suggestion': self.suggestion,
            'legal_source': self.legal_source,
            'confidence_score': self.confidence_score,
            'evidence': self.evidence,
            'gate_version': self.gate_version,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Correction(Base):
    """
    Document correction record
    Tracks corrections applied or suggested for documents
    """
    __tablename__ = 'corrections'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # References
    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'),
                        nullable=False, index=True)
    validation_id = Column(Integer, ForeignKey('validations.id', ondelete='SET NULL'),
                          nullable=True, index=True)

    # Correction details
    correction_type = Column(String(50), nullable=False, index=True,
                            comment="Type: rewrite, suggestion, auto_fix")
    target_gate = Column(String(255), nullable=True, index=True,
                        comment="Gate that triggered correction")

    # Content changes
    original_content = Column(Text, nullable=True)
    corrected_content = Column(Text, nullable=True)
    diff = Column(JSON, nullable=True, comment="Structured diff of changes")

    # Correction metadata
    strategy = Column(String(100), nullable=True,
                     comment="Correction strategy used")
    confidence = Column(Float, nullable=True, comment="Confidence in correction (0.0-1.0)")
    reasoning = Column(Text, nullable=True, comment="Explanation of correction")

    # Status
    status = Column(SQLEnum(CorrectionStatus), nullable=False,
                   default=CorrectionStatus.PENDING, index=True)
    applied_at = Column(DateTime, nullable=True)
    applied_by = Column(String(100), nullable=True)

    # Review tracking
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(String(100), nullable=True)
    review_notes = Column(Text, nullable=True)

    # Metadata
    client_id = Column(String(100), nullable=False, index=True)
    metadata_json = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow,
                       onupdate=datetime.utcnow)

    # Relationships
    document = relationship('Document', back_populates='corrections')
    validation = relationship('Validation', back_populates='corrections')
    history = relationship('CorrectionHistory', back_populates='correction',
                          cascade='all, delete-orphan')

    # Indexes
    __table_args__ = (
        Index('idx_corrections_doc_status', 'document_id', 'status'),
        Index('idx_corrections_validation', 'validation_id', 'status'),
        Index('idx_corrections_type_status', 'correction_type', 'status'),
        Index('idx_corrections_gate', 'target_gate', 'status'),
        {'comment': 'Document correction records'}
    )

    def __repr__(self) -> str:
        return f"<Correction(id={self.id}, doc_id={self.document_id}, status={self.status})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'id': self.id,
            'document_id': self.document_id,
            'validation_id': self.validation_id,
            'correction_type': self.correction_type,
            'target_gate': self.target_gate,
            'strategy': self.strategy,
            'confidence': self.confidence,
            'reasoning': self.reasoning,
            'status': self.status.value,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
            'applied_by': self.applied_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class CorrectionHistory(Base):
    """
    Version history for corrections
    Tracks all changes to correction records
    """
    __tablename__ = 'correction_history'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Correction reference
    correction_id = Column(Integer, ForeignKey('corrections.id', ondelete='CASCADE'),
                          nullable=False, index=True)

    # Change tracking
    change_type = Column(String(50), nullable=False,
                        comment="Type: created, updated, applied, rejected, reverted")
    previous_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=False)

    # Change details
    changes = Column(JSON, nullable=True, comment="Changed fields and values")
    reason = Column(Text, nullable=True)

    # Actor information
    changed_by = Column(String(100), nullable=True)
    changed_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    correction = relationship('Correction', back_populates='history')

    # Indexes
    __table_args__ = (
        Index('idx_history_correction_date', 'correction_id', 'changed_at'),
        Index('idx_history_type', 'change_type', 'changed_at'),
        {'comment': 'Correction version history'}
    )

    def __repr__(self) -> str:
        return f"<CorrectionHistory(id={self.id}, correction_id={self.correction_id})>"


class AuditTrail(Base):
    """
    Comprehensive audit trail for all operations
    Tracks who did what, when, and why
    """
    __tablename__ = 'audit_trail'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Entity references (nullable to support various entity types)
    document_id = Column(Integer, ForeignKey('documents.id', ondelete='SET NULL'),
                        nullable=True, index=True)
    validation_id = Column(Integer, ForeignKey('validations.id', ondelete='SET NULL'),
                          nullable=True, index=True)

    # Audit details
    action = Column(String(100), nullable=False, index=True,
                   comment="Action: create, read, update, delete, validate, correct")
    entity_type = Column(String(50), nullable=False, index=True,
                        comment="Entity type: document, validation, correction")
    entity_id = Column(Integer, nullable=True, index=True)

    # Actor information
    actor_id = Column(String(100), nullable=False, index=True,
                     comment="User or system that performed action")
    actor_type = Column(String(50), nullable=False, default='user',
                       comment="Type: user, system, api")

    # Change details
    changes = Column(JSON, nullable=True, comment="Before/after values")
    metadata_json = Column(JSON, nullable=True)

    # Request context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    request_id = Column(String(100), nullable=True, index=True)

    # Timestamps
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Client/tenant
    client_id = Column(String(100), nullable=False, index=True)
    tenant_id = Column(String(100), nullable=True, index=True)

    # Relationships
    document = relationship('Document', back_populates='audit_trails')
    validation = relationship('Validation', back_populates='audit_trails')

    # Indexes
    __table_args__ = (
        Index('idx_audit_action_time', 'action', 'timestamp'),
        Index('idx_audit_entity', 'entity_type', 'entity_id', 'timestamp'),
        Index('idx_audit_actor', 'actor_id', 'timestamp'),
        Index('idx_audit_client', 'client_id', 'timestamp'),
        Index('idx_audit_request', 'request_id', 'timestamp'),
        {'comment': 'Comprehensive audit trail'}
    )

    def __repr__(self) -> str:
        return f"<AuditTrail(id={self.id}, action={self.action}, actor={self.actor_id})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'id': self.id,
            'document_id': self.document_id,
            'validation_id': self.validation_id,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'actor_id': self.actor_id,
            'actor_type': self.actor_type,
            'changes': self.changes,
            'ip_address': self.ip_address,
            'request_id': self.request_id,
            'client_id': self.client_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class Tag(Base):
    """
    Tags for categorizing documents
    """
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True, index=True)
    color = Column(String(7), nullable=True, comment="Hex color code")

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    documents = relationship('Document', secondary=document_tags, back_populates='tags')

    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name={self.name})>"


class DataRetentionPolicy(Base):
    """
    Data retention policies for automated data lifecycle management
    """
    __tablename__ = 'data_retention_policies'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Policy details
    name = Column(String(200), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    entity_type = Column(String(50), nullable=False, index=True,
                        comment="Entity type: document, validation, audit_trail")

    # Retention rules
    retention_days = Column(Integer, nullable=False,
                           comment="Days to retain before action")
    action = Column(SQLEnum(RetentionAction), nullable=False)

    # Filtering criteria
    criteria = Column(JSON, nullable=True,
                     comment="Additional criteria (e.g., risk_level, client_id)")

    # Status
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    priority = Column(Integer, nullable=False, default=100,
                     comment="Priority for conflict resolution (lower = higher priority)")

    # Execution tracking
    last_run = Column(DateTime, nullable=True)
    next_run = Column(DateTime, nullable=True, index=True)

    # Statistics
    total_processed = Column(Integer, nullable=False, default=0)
    total_affected = Column(Integer, nullable=False, default=0)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow,
                       onupdate=datetime.utcnow)
    created_by = Column(String(100), nullable=True)

    # Constraints
    __table_args__ = (
        CheckConstraint('retention_days > 0', name='chk_retention_days_positive'),
        Index('idx_retention_active_next', 'is_active', 'next_run'),
        Index('idx_retention_entity', 'entity_type', 'is_active'),
        {'comment': 'Data retention policies'}
    )

    def __repr__(self) -> str:
        return f"<DataRetentionPolicy(id={self.id}, name={self.name})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'entity_type': self.entity_type,
            'retention_days': self.retention_days,
            'action': self.action.value,
            'criteria': self.criteria,
            'is_active': self.is_active,
            'priority': self.priority,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': self.next_run.isoformat() if self.next_run else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ExportLog(Base):
    """
    Log of data exports for compliance and tracking
    """
    __tablename__ = 'export_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Export details
    export_type = Column(String(50), nullable=False, index=True,
                        comment="Type: csv, json, excel, pdf")
    entity_type = Column(String(50), nullable=False,
                        comment="Entity type: document, validation, audit")

    # Export configuration
    filters = Column(JSON, nullable=True, comment="Filters applied")
    fields = Column(JSON, nullable=True, comment="Fields included")

    # Results
    record_count = Column(Integer, nullable=False, default=0)
    file_size_bytes = Column(Integer, nullable=True)
    file_path = Column(String(500), nullable=True)
    file_hash = Column(String(64), nullable=True, comment="SHA-256 hash of export file")

    # Status
    status = Column(String(50), nullable=False, default='pending', index=True,
                   comment="Status: pending, completed, failed")
    error_message = Column(Text, nullable=True)

    # Actor information
    requested_by = Column(String(100), nullable=False, index=True)
    client_id = Column(String(100), nullable=False, index=True)

    # Timestamps
    requested_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True, index=True,
                       comment="Export file expiration")

    # Indexes
    __table_args__ = (
        Index('idx_exports_type_status', 'export_type', 'status'),
        Index('idx_exports_requester', 'requested_by', 'requested_at'),
        Index('idx_exports_client', 'client_id', 'requested_at'),
        {'comment': 'Data export log'}
    )

    def __repr__(self) -> str:
        return f"<ExportLog(id={self.id}, type={self.export_type}, status={self.status})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'id': self.id,
            'export_type': self.export_type,
            'entity_type': self.entity_type,
            'record_count': self.record_count,
            'file_size_bytes': self.file_size_bytes,
            'status': self.status,
            'requested_by': self.requested_by,
            'requested_at': self.requested_at.isoformat() if self.requested_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }


# SQLAlchemy event listeners for automatic behavior
@event.listens_for(Document, 'before_insert')
def document_before_insert(mapper, connection, target):
    """Generate content hash and length before insert"""
    if target.content:
        target.content_hash = hashlib.sha256(target.content.encode('utf-8')).hexdigest()
        target.content_length = len(target.content)


@event.listens_for(Document, 'before_update')
def document_before_update(mapper, connection, target):
    """Update hash and length on content change"""
    if target.content:
        new_hash = hashlib.sha256(target.content.encode('utf-8')).hexdigest()
        if new_hash != target.content_hash:
            target.content_hash = new_hash
            target.content_length = len(target.content)


@event.listens_for(Validation, 'before_insert')
def validation_before_insert(mapper, connection, target):
    """Generate request hash before insert"""
    hash_input = f"{target.document_id}{datetime.utcnow().isoformat()}{target.client_id}"
    target.request_hash = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
    target.started_at = datetime.utcnow()
