"""
Audit repository for comprehensive audit trail management
"""
from __future__ import annotations

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session

from backend.db.models import AuditTrail
from backend.db.repositories.base import BaseRepository


class AuditRepository(BaseRepository[AuditTrail]):
    """Repository for AuditTrail operations"""

    def __init__(self, session: Session):
        super().__init__(AuditTrail, session)

    def log(
        self,
        action: str,
        entity_type: str,
        entity_id: int,
        actor_id: str,
        client_id: str,
        actor_type: str = 'user',
        document_id: Optional[int] = None,
        validation_id: Optional[int] = None,
        changes: Optional[dict] = None,
        metadata: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> AuditTrail:
        """
        Create an audit log entry

        Args:
            action: Action performed (create, read, update, delete, etc.)
            entity_type: Type of entity (document, validation, correction)
            entity_id: Entity ID
            actor_id: User or system that performed action
            client_id: Client identifier
            actor_type: Type of actor (user, system, api)
            document_id: Optional document reference
            validation_id: Optional validation reference
            changes: Optional before/after values
            metadata: Optional metadata
            ip_address: Optional IP address
            user_agent: Optional user agent
            request_id: Optional request ID
            tenant_id: Optional tenant ID

        Returns:
            Created audit trail entry
        """
        return self.create(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            actor_id=actor_id,
            actor_type=actor_type,
            client_id=client_id,
            document_id=document_id,
            validation_id=validation_id,
            changes=changes,
            metadata_json=metadata,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            tenant_id=tenant_id
        )

    def get_by_entity(
        self,
        entity_type: str,
        entity_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditTrail]:
        """
        Get audit trail for a specific entity

        Args:
            entity_type: Entity type
            entity_id: Entity ID
            limit: Maximum results
            offset: Results to skip

        Returns:
            List of audit entries
        """
        return self.session.query(AuditTrail).filter(
            AuditTrail.entity_type == entity_type,
            AuditTrail.entity_id == entity_id
        ).order_by(desc(AuditTrail.timestamp)).offset(offset).limit(limit).all()

    def get_by_actor(
        self,
        actor_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditTrail]:
        """
        Get audit trail for a specific actor

        Args:
            actor_id: Actor identifier
            limit: Maximum results
            offset: Results to skip

        Returns:
            List of audit entries
        """
        return self.session.query(AuditTrail).filter(
            AuditTrail.actor_id == actor_id
        ).order_by(desc(AuditTrail.timestamp)).offset(offset).limit(limit).all()

    def get_by_action(
        self,
        action: str,
        client_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditTrail]:
        """
        Get audit trail by action type

        Args:
            action: Action type
            client_id: Optional client filter
            start_date: Optional start date
            end_date: Optional end date
            limit: Maximum results

        Returns:
            List of audit entries
        """
        filters = [AuditTrail.action == action]

        if client_id:
            filters.append(AuditTrail.client_id == client_id)

        if start_date:
            filters.append(AuditTrail.timestamp >= start_date)

        if end_date:
            filters.append(AuditTrail.timestamp <= end_date)

        return self.session.query(AuditTrail).filter(
            and_(*filters)
        ).order_by(desc(AuditTrail.timestamp)).limit(limit).all()

    def get_by_document(
        self,
        document_id: int,
        limit: int = 100
    ) -> List[AuditTrail]:
        """
        Get audit trail for a document

        Args:
            document_id: Document ID
            limit: Maximum results

        Returns:
            List of audit entries
        """
        return self.session.query(AuditTrail).filter(
            AuditTrail.document_id == document_id
        ).order_by(desc(AuditTrail.timestamp)).limit(limit).all()

    def get_by_validation(
        self,
        validation_id: int,
        limit: int = 100
    ) -> List[AuditTrail]:
        """
        Get audit trail for a validation

        Args:
            validation_id: Validation ID
            limit: Maximum results

        Returns:
            List of audit entries
        """
        return self.session.query(AuditTrail).filter(
            AuditTrail.validation_id == validation_id
        ).order_by(desc(AuditTrail.timestamp)).limit(limit).all()

    def get_by_request(
        self,
        request_id: str,
        limit: int = 100
    ) -> List[AuditTrail]:
        """
        Get audit trail for a request

        Args:
            request_id: Request ID
            limit: Maximum results

        Returns:
            List of audit entries
        """
        return self.session.query(AuditTrail).filter(
            AuditTrail.request_id == request_id
        ).order_by(AuditTrail.timestamp.asc()).limit(limit).all()

    def get_recent(
        self,
        client_id: Optional[str] = None,
        hours: int = 24,
        limit: int = 100
    ) -> List[AuditTrail]:
        """
        Get recent audit entries

        Args:
            client_id: Optional client filter
            hours: Number of hours to look back
            limit: Maximum results

        Returns:
            List of recent audit entries
        """
        since = datetime.utcnow() - timedelta(hours=hours)

        query = self.session.query(AuditTrail).filter(
            AuditTrail.timestamp >= since
        )

        if client_id:
            query = query.filter(AuditTrail.client_id == client_id)

        return query.order_by(desc(AuditTrail.timestamp)).limit(limit).all()

    def search(
        self,
        action: Optional[str] = None,
        entity_type: Optional[str] = None,
        actor_id: Optional[str] = None,
        client_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditTrail]:
        """
        Search audit trail with multiple filters

        Args:
            action: Filter by action
            entity_type: Filter by entity type
            actor_id: Filter by actor
            client_id: Filter by client
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum results
            offset: Results to skip

        Returns:
            List of matching audit entries
        """
        filters = []

        if action:
            filters.append(AuditTrail.action == action)

        if entity_type:
            filters.append(AuditTrail.entity_type == entity_type)

        if actor_id:
            filters.append(AuditTrail.actor_id == actor_id)

        if client_id:
            filters.append(AuditTrail.client_id == client_id)

        if start_date:
            filters.append(AuditTrail.timestamp >= start_date)

        if end_date:
            filters.append(AuditTrail.timestamp <= end_date)

        query = self.session.query(AuditTrail)

        if filters:
            query = query.filter(and_(*filters))

        return query.order_by(desc(AuditTrail.timestamp)).offset(offset).limit(limit).all()

    def get_statistics(
        self,
        client_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get audit trail statistics

        Args:
            client_id: Optional client filter
            days: Number of days to analyze

        Returns:
            Statistics dictionary
        """
        since = datetime.utcnow() - timedelta(days=days)

        query = self.session.query(AuditTrail).filter(
            AuditTrail.timestamp >= since
        )

        if client_id:
            query = query.filter(AuditTrail.client_id == client_id)

        total = query.count()

        # Count by action
        action_stats = self.session.query(
            AuditTrail.action,
            func.count(AuditTrail.id).label('count')
        ).filter(AuditTrail.timestamp >= since)

        if client_id:
            action_stats = action_stats.filter(AuditTrail.client_id == client_id)

        action_counts = {
            action: count
            for action, count in action_stats.group_by(AuditTrail.action).all()
        }

        # Count by entity type
        entity_stats = self.session.query(
            AuditTrail.entity_type,
            func.count(AuditTrail.id).label('count')
        ).filter(AuditTrail.timestamp >= since)

        if client_id:
            entity_stats = entity_stats.filter(AuditTrail.client_id == client_id)

        entity_counts = {
            entity_type: count
            for entity_type, count in entity_stats.group_by(AuditTrail.entity_type).all()
        }

        # Top actors
        top_actors = self.session.query(
            AuditTrail.actor_id,
            func.count(AuditTrail.id).label('count')
        ).filter(AuditTrail.timestamp >= since)

        if client_id:
            top_actors = top_actors.filter(AuditTrail.client_id == client_id)

        top_actors_list = [
            {'actor_id': actor, 'action_count': count}
            for actor, count in top_actors.group_by(
                AuditTrail.actor_id
            ).order_by(desc('count')).limit(10).all()
        ]

        return {
            'period_days': days,
            'total_actions': total,
            'by_action': action_counts,
            'by_entity_type': entity_counts,
            'top_actors': top_actors_list
        }

    def get_activity_timeline(
        self,
        client_id: Optional[str] = None,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get activity timeline grouped by day

        Args:
            client_id: Optional client filter
            days: Number of days

        Returns:
            List of daily activity counts
        """
        since = datetime.utcnow() - timedelta(days=days)

        query = self.session.query(
            func.date(AuditTrail.timestamp).label('day'),
            AuditTrail.action,
            func.count(AuditTrail.id).label('count')
        ).filter(AuditTrail.timestamp >= since)

        if client_id:
            query = query.filter(AuditTrail.client_id == client_id)

        results = query.group_by('day', AuditTrail.action).all()

        # Organize by day
        timeline = {}
        for day, action, count in results:
            day_str = str(day)
            if day_str not in timeline:
                timeline[day_str] = {}
            timeline[day_str][action] = count

        return [
            {'date': day, 'actions': actions}
            for day, actions in sorted(timeline.items())
        ]

    def cleanup_old_entries(
        self,
        retention_days: int = 365,
        batch_size: int = 1000
    ) -> int:
        """
        Delete old audit entries (for data retention policies)

        Args:
            retention_days: Days to retain
            batch_size: Number of records to delete per batch

        Returns:
            Number of deleted entries
        """
        cutoff = datetime.utcnow() - timedelta(days=retention_days)

        deleted_count = 0
        while True:
            # Delete in batches to avoid locking issues
            batch = self.session.query(AuditTrail).filter(
                AuditTrail.timestamp < cutoff
            ).limit(batch_size).all()

            if not batch:
                break

            for entry in batch:
                self.session.delete(entry)

            self.flush()
            deleted_count += len(batch)

        return deleted_count
