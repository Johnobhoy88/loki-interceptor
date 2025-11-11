"""
Database package for LOKI Interceptor
Enterprise-grade persistence layer with SQLAlchemy ORM
"""
from backend.db.models import (
    Base,
    Document,
    Validation,
    ValidationResult,
    Correction,
    CorrectionHistory,
    AuditTrail,
    DataRetentionPolicy,
    ExportLog
)
from backend.db.session import (
    get_session,
    get_engine,
    init_db,
    dispose_engine
)

__all__ = [
    'Base',
    'Document',
    'Validation',
    'ValidationResult',
    'Correction',
    'CorrectionHistory',
    'AuditTrail',
    'DataRetentionPolicy',
    'ExportLog',
    'get_session',
    'get_engine',
    'init_db',
    'dispose_engine'
]
