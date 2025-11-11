"""
Advanced query builder for complex searches and analytics
Provides a fluent interface for building complex database queries
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from enum import Enum

from sqlalchemy import and_, or_, not_, desc, asc, func, case
from sqlalchemy.orm import Session, Query
from sqlalchemy.sql.expression import ColumnElement

from backend.db.models import (
    Document, Validation, ValidationResult,
    Correction, AuditTrail, DocumentType, RiskLevel,
    ValidationStatus, GateStatus, CorrectionStatus
)


class SortOrder(str, Enum):
    """Sort order enumeration"""
    ASC = "asc"
    DESC = "desc"


class QueryBuilder:
    """
    Advanced query builder for complex searches
    Provides a fluent interface for building queries
    """

    def __init__(self, session: Session, model_class: type):
        """
        Initialize query builder

        Args:
            session: Database session
            model_class: SQLAlchemy model class to query
        """
        self.session = session
        self.model_class = model_class
        self.query = session.query(model_class)
        self.filters: List[ColumnElement] = []
        self._limit: Optional[int] = None
        self._offset: Optional[int] = None
        self._order_by: List[ColumnElement] = []

    def filter(self, *conditions) -> QueryBuilder:
        """
        Add filter conditions

        Args:
            *conditions: SQLAlchemy filter conditions

        Returns:
            Self for chaining
        """
        self.filters.extend(conditions)
        return self

    def filter_by(self, **kwargs) -> QueryBuilder:
        """
        Filter by attribute values

        Args:
            **kwargs: Attribute key-value pairs

        Returns:
            Self for chaining
        """
        for attr, value in kwargs.items():
            if hasattr(self.model_class, attr):
                self.filters.append(getattr(self.model_class, attr) == value)
        return self

    def equals(self, attribute: str, value: Any) -> QueryBuilder:
        """
        Add equality filter

        Args:
            attribute: Attribute name
            value: Value to match

        Returns:
            Self for chaining
        """
        if hasattr(self.model_class, attribute):
            self.filters.append(getattr(self.model_class, attribute) == value)
        return self

    def not_equals(self, attribute: str, value: Any) -> QueryBuilder:
        """
        Add inequality filter

        Args:
            attribute: Attribute name
            value: Value to exclude

        Returns:
            Self for chaining
        """
        if hasattr(self.model_class, attribute):
            self.filters.append(getattr(self.model_class, attribute) != value)
        return self

    def greater_than(self, attribute: str, value: Any) -> QueryBuilder:
        """
        Add greater than filter

        Args:
            attribute: Attribute name
            value: Comparison value

        Returns:
            Self for chaining
        """
        if hasattr(self.model_class, attribute):
            self.filters.append(getattr(self.model_class, attribute) > value)
        return self

    def less_than(self, attribute: str, value: Any) -> QueryBuilder:
        """
        Add less than filter

        Args:
            attribute: Attribute name
            value: Comparison value

        Returns:
            Self for chaining
        """
        if hasattr(self.model_class, attribute):
            self.filters.append(getattr(self.model_class, attribute) < value)
        return self

    def between(self, attribute: str, min_value: Any, max_value: Any) -> QueryBuilder:
        """
        Add between filter

        Args:
            attribute: Attribute name
            min_value: Minimum value (inclusive)
            max_value: Maximum value (inclusive)

        Returns:
            Self for chaining
        """
        if hasattr(self.model_class, attribute):
            col = getattr(self.model_class, attribute)
            self.filters.append(and_(col >= min_value, col <= max_value))
        return self

    def in_list(self, attribute: str, values: List[Any]) -> QueryBuilder:
        """
        Add IN filter

        Args:
            attribute: Attribute name
            values: List of values

        Returns:
            Self for chaining
        """
        if hasattr(self.model_class, attribute) and values:
            self.filters.append(getattr(self.model_class, attribute).in_(values))
        return self

    def not_in_list(self, attribute: str, values: List[Any]) -> QueryBuilder:
        """
        Add NOT IN filter

        Args:
            attribute: Attribute name
            values: List of values to exclude

        Returns:
            Self for chaining
        """
        if hasattr(self.model_class, attribute) and values:
            self.filters.append(~getattr(self.model_class, attribute).in_(values))
        return self

    def contains(self, attribute: str, value: str, case_sensitive: bool = True) -> QueryBuilder:
        """
        Add text contains filter

        Args:
            attribute: Attribute name
            value: Text to search for
            case_sensitive: Whether search is case-sensitive

        Returns:
            Self for chaining
        """
        if hasattr(self.model_class, attribute):
            col = getattr(self.model_class, attribute)
            if case_sensitive:
                self.filters.append(col.contains(value))
            else:
                self.filters.append(col.ilike(f'%{value}%'))
        return self

    def starts_with(self, attribute: str, value: str) -> QueryBuilder:
        """
        Add starts with filter

        Args:
            attribute: Attribute name
            value: Prefix to match

        Returns:
            Self for chaining
        """
        if hasattr(self.model_class, attribute):
            self.filters.append(getattr(self.model_class, attribute).startswith(value))
        return self

    def ends_with(self, attribute: str, value: str) -> QueryBuilder:
        """
        Add ends with filter

        Args:
            attribute: Attribute name
            value: Suffix to match

        Returns:
            Self for chaining
        """
        if hasattr(self.model_class, attribute):
            self.filters.append(getattr(self.model_class, attribute).endswith(value))
        return self

    def is_null(self, attribute: str) -> QueryBuilder:
        """
        Add IS NULL filter

        Args:
            attribute: Attribute name

        Returns:
            Self for chaining
        """
        if hasattr(self.model_class, attribute):
            self.filters.append(getattr(self.model_class, attribute).is_(None))
        return self

    def is_not_null(self, attribute: str) -> QueryBuilder:
        """
        Add IS NOT NULL filter

        Args:
            attribute: Attribute name

        Returns:
            Self for chaining
        """
        if hasattr(self.model_class, attribute):
            self.filters.append(getattr(self.model_class, attribute).isnot(None))
        return self

    def date_range(
        self,
        attribute: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None
    ) -> QueryBuilder:
        """
        Add date range filter

        Args:
            attribute: Attribute name
            start: Start date (inclusive)
            end: End date (inclusive)

        Returns:
            Self for chaining
        """
        if hasattr(self.model_class, attribute):
            col = getattr(self.model_class, attribute)
            if start:
                self.filters.append(col >= start)
            if end:
                self.filters.append(col <= end)
        return self

    def last_n_days(self, attribute: str, days: int) -> QueryBuilder:
        """
        Filter by last N days

        Args:
            attribute: Date attribute name
            days: Number of days

        Returns:
            Self for chaining
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        return self.greater_than(attribute, cutoff)

    def or_filter(self, *conditions) -> QueryBuilder:
        """
        Add OR filter group

        Args:
            *conditions: Conditions to OR together

        Returns:
            Self for chaining
        """
        if conditions:
            self.filters.append(or_(*conditions))
        return self

    def and_filter(self, *conditions) -> QueryBuilder:
        """
        Add AND filter group

        Args:
            *conditions: Conditions to AND together

        Returns:
            Self for chaining
        """
        if conditions:
            self.filters.append(and_(*conditions))
        return self

    def order_by(self, attribute: str, order: SortOrder = SortOrder.DESC) -> QueryBuilder:
        """
        Add ordering

        Args:
            attribute: Attribute to order by
            order: Sort order (asc or desc)

        Returns:
            Self for chaining
        """
        if hasattr(self.model_class, attribute):
            col = getattr(self.model_class, attribute)
            if order == SortOrder.ASC:
                self._order_by.append(asc(col))
            else:
                self._order_by.append(desc(col))
        return self

    def limit(self, limit: int) -> QueryBuilder:
        """
        Set result limit

        Args:
            limit: Maximum number of results

        Returns:
            Self for chaining
        """
        self._limit = limit
        return self

    def offset(self, offset: int) -> QueryBuilder:
        """
        Set result offset

        Args:
            offset: Number of results to skip

        Returns:
            Self for chaining
        """
        self._offset = offset
        return self

    def paginate(self, page: int, per_page: int) -> QueryBuilder:
        """
        Paginate results

        Args:
            page: Page number (1-indexed)
            per_page: Results per page

        Returns:
            Self for chaining
        """
        self._limit = per_page
        self._offset = (page - 1) * per_page
        return self

    def build(self) -> Query:
        """
        Build and return the SQLAlchemy query

        Returns:
            SQLAlchemy Query object
        """
        if self.filters:
            self.query = self.query.filter(and_(*self.filters))

        if self._order_by:
            self.query = self.query.order_by(*self._order_by)

        if self._offset:
            self.query = self.query.offset(self._offset)

        if self._limit:
            self.query = self.query.limit(self._limit)

        return self.query

    def all(self) -> List:
        """
        Execute query and return all results

        Returns:
            List of results
        """
        return self.build().all()

    def first(self):
        """
        Execute query and return first result

        Returns:
            First result or None
        """
        return self.build().first()

    def count(self) -> int:
        """
        Count matching results

        Returns:
            Number of matching results
        """
        if self.filters:
            query = self.session.query(self.model_class).filter(and_(*self.filters))
        else:
            query = self.session.query(self.model_class)
        return query.count()

    def exists(self) -> bool:
        """
        Check if any results exist

        Returns:
            True if results exist, False otherwise
        """
        return self.count() > 0


class DocumentQueryBuilder(QueryBuilder):
    """Specialized query builder for documents"""

    def __init__(self, session: Session):
        super().__init__(session, Document)

    def by_type(self, doc_type: DocumentType) -> DocumentQueryBuilder:
        """Filter by document type"""
        return self.equals('document_type', doc_type)

    def by_client(self, client_id: str) -> DocumentQueryBuilder:
        """Filter by client"""
        return self.equals('client_id', client_id)

    def by_tenant(self, tenant_id: str) -> DocumentQueryBuilder:
        """Filter by tenant"""
        return self.equals('tenant_id', tenant_id)

    def latest_versions(self) -> DocumentQueryBuilder:
        """Only return latest versions"""
        return self.equals('is_latest', True)

    def not_deleted(self) -> DocumentQueryBuilder:
        """Exclude soft-deleted documents"""
        return self.equals('is_deleted', False)

    def search_content(self, query: str) -> DocumentQueryBuilder:
        """Search in content, title, and description"""
        if query:
            search_filters = []
            if hasattr(Document, 'content'):
                search_filters.append(Document.content.contains(query))
            if hasattr(Document, 'title'):
                search_filters.append(Document.title.contains(query))
            if hasattr(Document, 'description'):
                search_filters.append(Document.description.contains(query))

            if search_filters:
                self.or_filter(*search_filters)
        return self


class ValidationQueryBuilder(QueryBuilder):
    """Specialized query builder for validations"""

    def __init__(self, session: Session):
        super().__init__(session, Validation)

    def by_status(self, status: ValidationStatus) -> ValidationQueryBuilder:
        """Filter by validation status"""
        return self.equals('status', status)

    def by_risk(self, risk: RiskLevel) -> ValidationQueryBuilder:
        """Filter by risk level"""
        return self.equals('overall_risk', risk)

    def by_document(self, document_id: int) -> ValidationQueryBuilder:
        """Filter by document"""
        return self.equals('document_id', document_id)

    def by_client(self, client_id: str) -> ValidationQueryBuilder:
        """Filter by client"""
        return self.equals('client_id', client_id)

    def completed_only(self) -> ValidationQueryBuilder:
        """Only return completed validations"""
        return self.equals('status', ValidationStatus.COMPLETED)

    def high_risk(self) -> ValidationQueryBuilder:
        """Only return high or critical risk"""
        return self.in_list('overall_risk', [RiskLevel.HIGH, RiskLevel.CRITICAL])

    def with_failures(self) -> ValidationQueryBuilder:
        """Only return validations with failures"""
        return self.greater_than('fail_count', 0)


class CorrectionQueryBuilder(QueryBuilder):
    """Specialized query builder for corrections"""

    def __init__(self, session: Session):
        super().__init__(session, Correction)

    def by_status(self, status: CorrectionStatus) -> CorrectionQueryBuilder:
        """Filter by correction status"""
        return self.equals('status', status)

    def by_document(self, document_id: int) -> CorrectionQueryBuilder:
        """Filter by document"""
        return self.equals('document_id', document_id)

    def by_validation(self, validation_id: int) -> CorrectionQueryBuilder:
        """Filter by validation"""
        return self.equals('validation_id', validation_id)

    def pending_only(self) -> CorrectionQueryBuilder:
        """Only return pending corrections"""
        return self.equals('status', CorrectionStatus.PENDING)

    def high_confidence(self, threshold: float = 0.8) -> CorrectionQueryBuilder:
        """Only return high confidence corrections"""
        return self.greater_than('confidence', threshold)


class AuditQueryBuilder(QueryBuilder):
    """Specialized query builder for audit trails"""

    def __init__(self, session: Session):
        super().__init__(session, AuditTrail)

    def by_action(self, action: str) -> AuditQueryBuilder:
        """Filter by action"""
        return self.equals('action', action)

    def by_entity(self, entity_type: str, entity_id: int) -> AuditQueryBuilder:
        """Filter by entity"""
        return self.equals('entity_type', entity_type).equals('entity_id', entity_id)

    def by_actor(self, actor_id: str) -> AuditQueryBuilder:
        """Filter by actor"""
        return self.equals('actor_id', actor_id)

    def by_client(self, client_id: str) -> AuditQueryBuilder:
        """Filter by client"""
        return self.equals('client_id', client_id)

    def by_request(self, request_id: str) -> AuditQueryBuilder:
        """Filter by request ID"""
        return self.equals('request_id', request_id)
