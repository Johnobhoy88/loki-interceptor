"""
Validation repository for CRUD operations on validations and results
"""
from __future__ import annotations

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session, joinedload

from backend.db.models import (
    Validation, ValidationResult, ValidationStatus,
    RiskLevel, GateStatus
)
from backend.db.repositories.base import BaseRepository


class ValidationRepository(BaseRepository[Validation]):
    """Repository for Validation operations"""

    def __init__(self, session: Session):
        super().__init__(Validation, session)

    def create_validation(
        self,
        document_id: int,
        modules_used: List[str],
        client_id: str,
        user_id: Optional[str] = None,
        config: Optional[dict] = None
    ) -> Validation:
        """
        Create a new validation record

        Args:
            document_id: Document to validate
            modules_used: List of module IDs
            client_id: Client identifier
            user_id: Optional user ID
            config: Optional configuration

        Returns:
            Created validation instance
        """
        return self.create(
            document_id=document_id,
            modules_used=modules_used,
            config=config,
            status=ValidationStatus.PENDING,
            client_id=client_id,
            user_id=user_id,
            started_at=datetime.utcnow()
        )

    def start_validation(self, validation_id: int) -> Optional[Validation]:
        """
        Mark validation as in progress

        Args:
            validation_id: Validation ID

        Returns:
            Updated validation or None
        """
        return self.update(
            validation_id,
            status=ValidationStatus.IN_PROGRESS,
            started_at=datetime.utcnow()
        )

    def complete_validation(
        self,
        validation_id: int,
        overall_risk: RiskLevel,
        counts: Dict[str, int],
        error_message: Optional[str] = None
    ) -> Optional[Validation]:
        """
        Mark validation as completed with results

        Args:
            validation_id: Validation ID
            overall_risk: Overall risk assessment
            counts: Dictionary with severity/status counts
            error_message: Optional error message

        Returns:
            Updated validation or None
        """
        validation = self.get_by_id(validation_id)
        if not validation:
            return None

        # Calculate duration
        duration_ms = None
        if validation.started_at:
            duration = datetime.utcnow() - validation.started_at
            duration_ms = int(duration.total_seconds() * 1000)

        status = ValidationStatus.COMPLETED if not error_message else ValidationStatus.FAILED

        return self.update(
            validation_id,
            status=status,
            completed_at=datetime.utcnow(),
            duration_ms=duration_ms,
            overall_risk=overall_risk,
            critical_count=counts.get('critical', 0),
            high_count=counts.get('high', 0),
            medium_count=counts.get('medium', 0),
            low_count=counts.get('low', 0),
            pass_count=counts.get('pass', 0),
            fail_count=counts.get('fail', 0),
            warning_count=counts.get('warning', 0),
            error_message=error_message
        )

    def add_result(
        self,
        validation_id: int,
        scope: str,
        gate_key: str,
        status: GateStatus,
        severity: Optional[RiskLevel] = None,
        message: Optional[str] = None,
        suggestion: Optional[str] = None,
        legal_source: Optional[str] = None,
        module_id: Optional[str] = None,
        gate_id: Optional[str] = None,
        confidence_score: Optional[float] = None,
        evidence: Optional[dict] = None,
        metadata: Optional[dict] = None,
        gate_version: Optional[str] = None
    ) -> ValidationResult:
        """
        Add a validation result to a validation

        Args:
            validation_id: Validation ID
            scope: Result scope (module, universal, analyzer, cross)
            gate_key: Full gate identifier
            status: Gate status
            severity: Result severity
            message: Result message
            suggestion: Suggested fix
            legal_source: Legal reference
            module_id: Module identifier
            gate_id: Gate identifier
            confidence_score: Confidence (0.0-1.0)
            evidence: Supporting evidence
            metadata: Additional metadata
            gate_version: Gate version

        Returns:
            Created validation result
        """
        result = ValidationResult(
            validation_id=validation_id,
            scope=scope,
            gate_key=gate_key,
            status=status,
            severity=severity,
            message=message,
            suggestion=suggestion,
            legal_source=legal_source,
            module_id=module_id,
            gate_id=gate_id,
            confidence_score=confidence_score,
            evidence=evidence,
            metadata_json=metadata,
            gate_version=gate_version
        )

        self.session.add(result)
        self.flush()
        return result

    def get_with_results(self, validation_id: int) -> Optional[Validation]:
        """
        Get validation with eagerly loaded results

        Args:
            validation_id: Validation ID

        Returns:
            Validation with results or None
        """
        return self.session.query(Validation).options(
            joinedload(Validation.results)
        ).filter(Validation.id == validation_id).first()

    def get_by_document(
        self,
        document_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[Validation]:
        """
        Get validations for a document

        Args:
            document_id: Document ID
            limit: Maximum results
            offset: Results to skip

        Returns:
            List of validations
        """
        return self.session.query(Validation).filter(
            Validation.document_id == document_id
        ).order_by(desc(Validation.created_at)).offset(offset).limit(limit).all()

    def get_by_risk_level(
        self,
        risk_level: RiskLevel,
        client_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Validation]:
        """
        Get validations by risk level

        Args:
            risk_level: Risk level to filter
            client_id: Optional client filter
            start_date: Optional start date
            limit: Maximum results

        Returns:
            List of validations
        """
        filters = [
            Validation.overall_risk == risk_level,
            Validation.status == ValidationStatus.COMPLETED
        ]

        if client_id:
            filters.append(Validation.client_id == client_id)

        if start_date:
            filters.append(Validation.created_at >= start_date)

        return self.session.query(Validation).filter(
            and_(*filters)
        ).order_by(desc(Validation.created_at)).limit(limit).all()

    def get_recent(
        self,
        client_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Validation]:
        """
        Get recent validations

        Args:
            client_id: Optional client filter
            limit: Maximum results
            offset: Results to skip

        Returns:
            List of recent validations
        """
        query = self.session.query(Validation)

        if client_id:
            query = query.filter(Validation.client_id == client_id)

        return query.order_by(desc(Validation.created_at)).offset(offset).limit(limit).all()

    def get_statistics(
        self,
        client_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get validation statistics

        Args:
            client_id: Optional client filter
            days: Number of days to analyze

        Returns:
            Statistics dictionary
        """
        since = datetime.utcnow() - timedelta(days=days)

        query = self.session.query(Validation).filter(
            Validation.created_at >= since
        )

        if client_id:
            query = query.filter(Validation.client_id == client_id)

        total = query.count()
        completed = query.filter(Validation.status == ValidationStatus.COMPLETED).count()
        failed = query.filter(Validation.status == ValidationStatus.FAILED).count()

        # Risk breakdown
        risk_counts = {}
        for risk in RiskLevel:
            count = query.filter(Validation.overall_risk == risk).count()
            if count > 0:
                risk_counts[risk.value] = count

        # Average duration
        avg_duration = self.session.query(
            func.avg(Validation.duration_ms)
        ).filter(
            Validation.created_at >= since,
            Validation.duration_ms.isnot(None)
        )

        if client_id:
            avg_duration = avg_duration.filter(Validation.client_id == client_id)

        avg_duration_ms = avg_duration.scalar() or 0

        # Issue counts
        critical_total = self.session.query(
            func.sum(Validation.critical_count)
        ).filter(Validation.created_at >= since)

        high_total = self.session.query(
            func.sum(Validation.high_count)
        ).filter(Validation.created_at >= since)

        if client_id:
            critical_total = critical_total.filter(Validation.client_id == client_id)
            high_total = high_total.filter(Validation.client_id == client_id)

        return {
            'period_days': days,
            'total_validations': total,
            'completed': completed,
            'failed': failed,
            'risk_breakdown': risk_counts,
            'avg_duration_ms': int(avg_duration_ms),
            'total_critical_issues': critical_total.scalar() or 0,
            'total_high_issues': high_total.scalar() or 0
        }

    def get_gate_failure_stats(
        self,
        client_id: Optional[str] = None,
        days: int = 30,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get top failing gates

        Args:
            client_id: Optional client filter
            days: Number of days to analyze
            limit: Maximum results

        Returns:
            List of gate failure statistics
        """
        since = datetime.utcnow() - timedelta(days=days)

        query = self.session.query(
            ValidationResult.gate_key,
            ValidationResult.module_id,
            ValidationResult.gate_id,
            func.count(ValidationResult.id).label('failure_count'),
            func.max(ValidationResult.severity).label('max_severity')
        ).join(Validation).filter(
            Validation.created_at >= since,
            ValidationResult.status == GateStatus.FAIL
        )

        if client_id:
            query = query.filter(Validation.client_id == client_id)

        results = query.group_by(
            ValidationResult.gate_key,
            ValidationResult.module_id,
            ValidationResult.gate_id
        ).order_by(desc('failure_count')).limit(limit).all()

        return [
            {
                'gate_key': r.gate_key,
                'module_id': r.module_id,
                'gate_id': r.gate_id,
                'failure_count': r.failure_count,
                'max_severity': r.max_severity
            }
            for r in results
        ]

    def search_results(
        self,
        query: str,
        scope: Optional[str] = None,
        status: Optional[GateStatus] = None,
        severity: Optional[RiskLevel] = None,
        limit: int = 100
    ) -> List[ValidationResult]:
        """
        Search validation results

        Args:
            query: Search query (in message, suggestion)
            scope: Filter by scope
            status: Filter by status
            severity: Filter by severity
            limit: Maximum results

        Returns:
            List of matching results
        """
        filters = []

        # Text search
        if query:
            filters.append(
                or_(
                    ValidationResult.message.contains(query),
                    ValidationResult.suggestion.contains(query)
                )
            )

        # Scope filter
        if scope:
            filters.append(ValidationResult.scope == scope)

        # Status filter
        if status:
            filters.append(ValidationResult.status == status)

        # Severity filter
        if severity:
            filters.append(ValidationResult.severity == severity)

        if filters:
            return self.session.query(ValidationResult).filter(
                and_(*filters)
            ).limit(limit).all()
        else:
            return self.session.query(ValidationResult).limit(limit).all()
