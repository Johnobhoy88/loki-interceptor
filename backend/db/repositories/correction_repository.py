"""
Correction repository for managing document corrections
"""
from __future__ import annotations

from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

from backend.db.models import Correction, CorrectionHistory, CorrectionStatus
from backend.db.repositories.base import BaseRepository


class CorrectionRepository(BaseRepository[Correction]):
    """Repository for Correction operations"""

    def __init__(self, session: Session):
        super().__init__(Correction, session)

    def create_correction(
        self,
        document_id: int,
        correction_type: str,
        client_id: str,
        validation_id: Optional[int] = None,
        target_gate: Optional[str] = None,
        original_content: Optional[str] = None,
        corrected_content: Optional[str] = None,
        diff: Optional[dict] = None,
        strategy: Optional[str] = None,
        confidence: Optional[float] = None,
        reasoning: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> Correction:
        """
        Create a new correction record

        Args:
            document_id: Document ID
            correction_type: Type of correction
            client_id: Client identifier
            validation_id: Optional validation that triggered correction
            target_gate: Gate that triggered correction
            original_content: Original content
            corrected_content: Corrected content
            diff: Structured diff
            strategy: Correction strategy used
            confidence: Confidence score (0.0-1.0)
            reasoning: Explanation
            metadata: Additional metadata

        Returns:
            Created correction instance
        """
        correction = self.create(
            document_id=document_id,
            validation_id=validation_id,
            correction_type=correction_type,
            target_gate=target_gate,
            original_content=original_content,
            corrected_content=corrected_content,
            diff=diff,
            strategy=strategy,
            confidence=confidence,
            reasoning=reasoning,
            status=CorrectionStatus.PENDING,
            client_id=client_id,
            metadata_json=metadata
        )

        # Create history entry
        self._add_history(
            correction.id,
            change_type='created',
            new_status=CorrectionStatus.PENDING.value,
            reason='Correction created'
        )

        return correction

    def apply_correction(
        self,
        correction_id: int,
        applied_by: str,
        notes: Optional[str] = None
    ) -> Optional[Correction]:
        """
        Mark correction as applied

        Args:
            correction_id: Correction ID
            applied_by: User who applied correction
            notes: Optional application notes

        Returns:
            Updated correction or None
        """
        correction = self.get_by_id(correction_id)
        if not correction:
            return None

        old_status = correction.status.value
        correction = self.update(
            correction_id,
            status=CorrectionStatus.APPLIED,
            applied_at=datetime.utcnow(),
            applied_by=applied_by
        )

        if correction:
            self._add_history(
                correction_id,
                change_type='applied',
                previous_status=old_status,
                new_status=CorrectionStatus.APPLIED.value,
                reason=notes,
                changed_by=applied_by
            )

        return correction

    def reject_correction(
        self,
        correction_id: int,
        rejected_by: str,
        reason: Optional[str] = None
    ) -> Optional[Correction]:
        """
        Reject a correction

        Args:
            correction_id: Correction ID
            rejected_by: User who rejected
            reason: Rejection reason

        Returns:
            Updated correction or None
        """
        correction = self.get_by_id(correction_id)
        if not correction:
            return None

        old_status = correction.status.value
        correction = self.update(
            correction_id,
            status=CorrectionStatus.REJECTED,
            reviewed_at=datetime.utcnow(),
            reviewed_by=rejected_by,
            review_notes=reason
        )

        if correction:
            self._add_history(
                correction_id,
                change_type='rejected',
                previous_status=old_status,
                new_status=CorrectionStatus.REJECTED.value,
                reason=reason,
                changed_by=rejected_by
            )

        return correction

    def revert_correction(
        self,
        correction_id: int,
        reverted_by: str,
        reason: Optional[str] = None
    ) -> Optional[Correction]:
        """
        Revert an applied correction

        Args:
            correction_id: Correction ID
            reverted_by: User who reverted
            reason: Revert reason

        Returns:
            Updated correction or None
        """
        correction = self.get_by_id(correction_id)
        if not correction or correction.status != CorrectionStatus.APPLIED:
            return None

        old_status = correction.status.value
        correction = self.update(
            correction_id,
            status=CorrectionStatus.REVERTED
        )

        if correction:
            self._add_history(
                correction_id,
                change_type='reverted',
                previous_status=old_status,
                new_status=CorrectionStatus.REVERTED.value,
                reason=reason,
                changed_by=reverted_by
            )

        return correction

    def get_by_document(
        self,
        document_id: int,
        status: Optional[CorrectionStatus] = None,
        limit: int = 50
    ) -> List[Correction]:
        """
        Get corrections for a document

        Args:
            document_id: Document ID
            status: Optional status filter
            limit: Maximum results

        Returns:
            List of corrections
        """
        query = self.session.query(Correction).filter(
            Correction.document_id == document_id
        )

        if status:
            query = query.filter(Correction.status == status)

        return query.order_by(desc(Correction.created_at)).limit(limit).all()

    def get_by_validation(
        self,
        validation_id: int,
        limit: int = 50
    ) -> List[Correction]:
        """
        Get corrections for a validation

        Args:
            validation_id: Validation ID
            limit: Maximum results

        Returns:
            List of corrections
        """
        return self.session.query(Correction).filter(
            Correction.validation_id == validation_id
        ).order_by(desc(Correction.created_at)).limit(limit).all()

    def get_pending(
        self,
        client_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Correction]:
        """
        Get pending corrections

        Args:
            client_id: Optional client filter
            limit: Maximum results

        Returns:
            List of pending corrections
        """
        query = self.session.query(Correction).filter(
            Correction.status == CorrectionStatus.PENDING
        )

        if client_id:
            query = query.filter(Correction.client_id == client_id)

        return query.order_by(Correction.created_at.asc()).limit(limit).all()

    def get_history(self, correction_id: int) -> List[CorrectionHistory]:
        """
        Get history for a correction

        Args:
            correction_id: Correction ID

        Returns:
            List of history entries
        """
        return self.session.query(CorrectionHistory).filter(
            CorrectionHistory.correction_id == correction_id
        ).order_by(CorrectionHistory.changed_at.asc()).all()

    def get_statistics(
        self,
        client_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get correction statistics

        Args:
            client_id: Optional client filter

        Returns:
            Statistics dictionary
        """
        query = self.session.query(Correction)

        if client_id:
            query = query.filter(Correction.client_id == client_id)

        total = query.count()
        pending = query.filter(Correction.status == CorrectionStatus.PENDING).count()
        applied = query.filter(Correction.status == CorrectionStatus.APPLIED).count()
        rejected = query.filter(Correction.status == CorrectionStatus.REJECTED).count()
        reverted = query.filter(Correction.status == CorrectionStatus.REVERTED).count()

        # Get top correction types
        type_query = self.session.query(
            Correction.correction_type,
            func.count(Correction.id).label('count')
        )

        if client_id:
            type_query = type_query.filter(Correction.client_id == client_id)

        type_stats = type_query.group_by(
            Correction.correction_type
        ).order_by(desc('count')).limit(5).all()

        return {
            'total_corrections': total,
            'pending': pending,
            'applied': applied,
            'rejected': rejected,
            'reverted': reverted,
            'by_type': [
                {'type': t[0], 'count': t[1]}
                for t in type_stats
            ]
        }

    def _add_history(
        self,
        correction_id: int,
        change_type: str,
        new_status: str,
        previous_status: Optional[str] = None,
        reason: Optional[str] = None,
        changed_by: Optional[str] = None,
        changes: Optional[dict] = None
    ) -> CorrectionHistory:
        """
        Add a history entry for a correction

        Args:
            correction_id: Correction ID
            change_type: Type of change
            new_status: New status
            previous_status: Previous status
            reason: Change reason
            changed_by: User who made the change
            changes: Changed fields

        Returns:
            Created history entry
        """
        history = CorrectionHistory(
            correction_id=correction_id,
            change_type=change_type,
            previous_status=previous_status,
            new_status=new_status,
            changes=changes,
            reason=reason,
            changed_by=changed_by
        )

        self.session.add(history)
        self.flush()
        return history


# Import for type checking
from sqlalchemy import func
