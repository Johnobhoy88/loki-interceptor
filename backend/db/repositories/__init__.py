"""
Repository pattern implementation for LOKI Interceptor
Provides clean data access layer abstractions
"""
from backend.db.repositories.base import BaseRepository
from backend.db.repositories.document_repository import DocumentRepository
from backend.db.repositories.validation_repository import ValidationRepository
from backend.db.repositories.correction_repository import CorrectionRepository
from backend.db.repositories.audit_repository import AuditRepository

__all__ = [
    'BaseRepository',
    'DocumentRepository',
    'ValidationRepository',
    'CorrectionRepository',
    'AuditRepository'
]
