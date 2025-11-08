"""
Comprehensive Audit Trail System for LOKI Enterprise

Complete audit logging with change tracking, compliance reporting,
and searchable audit logs for regulatory requirements.

Features:
- Action logging (who, what, when, where)
- Before/after change tracking
- Compliance report generation
- Searchable and filterable audit logs
- Data retention policies
- Export capabilities (JSON, CSV)
"""

import uuid
import json
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import hashlib


class AuditAction(Enum):
    """Audit action types."""
    # Authentication
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_RESET = "password_reset"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"

    # User management
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_INVITED = "user_invited"
    USER_ACTIVATED = "user_activated"
    USER_DEACTIVATED = "user_deactivated"

    # Organization
    ORG_CREATED = "org_created"
    ORG_UPDATED = "org_updated"
    ORG_DELETED = "org_deleted"
    ORG_USER_ADDED = "org_user_added"
    ORG_USER_REMOVED = "org_user_removed"

    # Documents
    DOC_CREATED = "doc_created"
    DOC_VIEWED = "doc_viewed"
    DOC_UPDATED = "doc_updated"
    DOC_DELETED = "doc_deleted"
    DOC_ANALYZED = "doc_analyzed"
    DOC_EXPORTED = "doc_exported"
    DOC_SHARED = "doc_shared"

    # Compliance
    COMPLIANCE_CHECK_RUN = "compliance_check_run"
    COMPLIANCE_RULE_ADDED = "compliance_rule_added"
    COMPLIANCE_RULE_UPDATED = "compliance_rule_updated"
    COMPLIANCE_RULE_DELETED = "compliance_rule_deleted"

    # Roles & Permissions
    ROLE_CREATED = "role_created"
    ROLE_UPDATED = "role_updated"
    ROLE_DELETED = "role_deleted"
    ROLE_ASSIGNED = "role_assigned"
    ROLE_REVOKED = "role_revoked"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_REVOKED = "permission_revoked"

    # API Keys
    API_KEY_CREATED = "api_key_created"
    API_KEY_REVOKED = "api_key_revoked"
    API_KEY_USED = "api_key_used"

    # Settings
    SETTINGS_UPDATED = "settings_updated"

    # Data export
    DATA_EXPORTED = "data_exported"

    # Access control
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"


class AuditLevel(Enum):
    """Audit log severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SECURITY = "security"


@dataclass
class AuditEvent:
    """
    Complete audit event record.

    Attributes:
        id: Event identifier
        timestamp: When event occurred
        action: Action performed
        level: Severity level
        user_id: User who performed action
        org_id: Organization context
        resource_type: Type of resource affected
        resource_id: Specific resource identifier
        ip_address: Client IP address
        user_agent: Client user agent
        success: Whether action succeeded
        before_state: State before change (JSON)
        after_state: State after change (JSON)
        metadata: Additional event metadata
        session_id: Associated session
        request_id: Associated request ID for tracing
    """
    id: str
    timestamp: datetime
    action: AuditAction
    level: AuditLevel
    user_id: Optional[str]
    org_id: Optional[str]
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool = True
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    session_id: Optional[str] = None
    request_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'action': self.action.value,
            'level': self.level.value,
            'user_id': self.user_id,
            'org_id': self.org_id,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'success': self.success,
            'before_state': self.before_state,
            'after_state': self.after_state,
            'metadata': self.metadata,
            'session_id': self.session_id,
            'request_id': self.request_id,
        }

    def get_changes(self) -> Dict[str, Tuple[Any, Any]]:
        """
        Get field-level changes between before and after states.

        Returns:
            Dictionary mapping field names to (before, after) tuples
        """
        if not self.before_state or not self.after_state:
            return {}

        changes = {}
        all_keys = set(self.before_state.keys()) | set(self.after_state.keys())

        for key in all_keys:
            before = self.before_state.get(key)
            after = self.after_state.get(key)

            if before != after:
                changes[key] = (before, after)

        return changes

    def calculate_hash(self) -> str:
        """
        Calculate hash of event for integrity verification.

        Returns:
            SHA-256 hash of event data
        """
        data = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()


class AuditLogger:
    """
    Central audit logging system.

    Handles logging of all system events with comprehensive metadata,
    change tracking, and integrity verification.
    """

    def __init__(
        self,
        db_connection=None,
        cache_backend=None,
        retention_days: int = 365,
    ):
        """
        Initialize audit logger.

        Args:
            db_connection: Database connection
            cache_backend: Redis cache
            retention_days: Audit log retention period
        """
        self.db = db_connection
        self.cache = cache_backend
        self.retention_days = retention_days
        self._events: List[AuditEvent] = []

    def log(
        self,
        action: AuditAction,
        user_id: Optional[str] = None,
        org_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        level: AuditLevel = AuditLevel.INFO,
        success: bool = True,
        before_state: Optional[Dict[str, Any]] = None,
        after_state: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> AuditEvent:
        """
        Log audit event.

        Args:
            action: Action performed
            user_id: User who performed action
            org_id: Organization context
            resource_type: Resource type affected
            resource_id: Resource identifier
            level: Severity level
            success: Whether action succeeded
            before_state: State before change
            after_state: State after change
            metadata: Additional metadata
            ip_address: Client IP
            user_agent: Client user agent
            session_id: Session ID
            request_id: Request ID

        Returns:
            Created AuditEvent
        """
        event_id = str(uuid.uuid4())

        event = AuditEvent(
            id=event_id,
            timestamp=datetime.utcnow(),
            action=action,
            level=level,
            user_id=user_id,
            org_id=org_id,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            before_state=before_state,
            after_state=after_state,
            metadata=metadata or {},
            session_id=session_id,
            request_id=request_id,
        )

        # Store in memory
        self._events.append(event)

        # Store in database
        self._persist_event(event)

        # Cache recent events
        if self.cache:
            self._cache_event(event)

        return event

    def log_access(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        granted: bool,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        """
        Log access control decision.

        Args:
            user_id: User requesting access
            action: Action attempted
            resource_type: Resource type
            resource_id: Resource ID
            granted: Whether access was granted
            metadata: Additional metadata

        Returns:
            Created AuditEvent
        """
        audit_action = AuditAction.ACCESS_GRANTED if granted else AuditAction.ACCESS_DENIED
        level = AuditLevel.INFO if granted else AuditLevel.SECURITY

        return self.log(
            action=audit_action,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            level=level,
            success=granted,
            metadata=metadata or {},
        )

    def log_change(
        self,
        action: AuditAction,
        user_id: str,
        org_id: str,
        resource_type: str,
        resource_id: str,
        before: Dict[str, Any],
        after: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        """
        Log state change with before/after tracking.

        Args:
            action: Action type
            user_id: User who made change
            org_id: Organization context
            resource_type: Resource type
            resource_id: Resource ID
            before: State before change
            after: State after change
            metadata: Additional metadata

        Returns:
            Created AuditEvent
        """
        return self.log(
            action=action,
            user_id=user_id,
            org_id=org_id,
            resource_type=resource_type,
            resource_id=resource_id,
            level=AuditLevel.INFO,
            before_state=before,
            after_state=after,
            metadata=metadata,
        )

    def search(
        self,
        org_id: Optional[str] = None,
        user_id: Optional[str] = None,
        action: Optional[AuditAction] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        level: Optional[AuditLevel] = None,
        success: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AuditEvent]:
        """
        Search audit logs with filters.

        Args:
            org_id: Filter by organization
            user_id: Filter by user
            action: Filter by action type
            resource_type: Filter by resource type
            resource_id: Filter by specific resource
            start_date: Start of time range
            end_date: End of time range
            level: Filter by severity level
            success: Filter by success status
            limit: Maximum results
            offset: Pagination offset

        Returns:
            List of matching AuditEvent instances
        """
        results = self._events.copy()

        # Apply filters
        if org_id:
            results = [e for e in results if e.org_id == org_id]

        if user_id:
            results = [e for e in results if e.user_id == user_id]

        if action:
            results = [e for e in results if e.action == action]

        if resource_type:
            results = [e for e in results if e.resource_type == resource_type]

        if resource_id:
            results = [e for e in results if e.resource_id == resource_id]

        if start_date:
            results = [e for e in results if e.timestamp >= start_date]

        if end_date:
            results = [e for e in results if e.timestamp <= end_date]

        if level:
            results = [e for e in results if e.level == level]

        if success is not None:
            results = [e for e in results if e.success == success]

        # Sort by timestamp (newest first)
        results.sort(key=lambda e: e.timestamp, reverse=True)

        # Pagination
        return results[offset:offset + limit]

    def get_user_activity(
        self,
        user_id: str,
        days: int = 30,
    ) -> List[AuditEvent]:
        """
        Get user activity for specified period.

        Args:
            user_id: User identifier
            days: Number of days to look back

        Returns:
            List of user's audit events
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        return self.search(
            user_id=user_id,
            start_date=start_date,
            limit=1000,
        )

    def get_resource_history(
        self,
        resource_type: str,
        resource_id: str,
        org_id: Optional[str] = None,
    ) -> List[AuditEvent]:
        """
        Get complete history for a resource.

        Args:
            resource_type: Resource type
            resource_id: Resource identifier
            org_id: Organization context

        Returns:
            List of events for this resource
        """
        return self.search(
            org_id=org_id,
            resource_type=resource_type,
            resource_id=resource_id,
            limit=1000,
        )

    def export_logs(
        self,
        org_id: str,
        start_date: datetime,
        end_date: datetime,
        format: str = "json",
    ) -> str:
        """
        Export audit logs for compliance.

        Args:
            org_id: Organization identifier
            start_date: Export start date
            end_date: Export end date
            format: Export format (json or csv)

        Returns:
            Formatted export data

        Raises:
            ValueError: If format is invalid
        """
        events = self.search(
            org_id=org_id,
            start_date=start_date,
            end_date=end_date,
            limit=10000,
        )

        if format == "json":
            return json.dumps(
                [e.to_dict() for e in events],
                indent=2,
                default=str,
            )
        elif format == "csv":
            return self._export_csv(events)
        else:
            raise ValueError(f"Invalid export format: {format}")

    def cleanup_old_logs(self) -> int:
        """
        Remove logs older than retention period.

        Returns:
            Number of logs deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)

        original_count = len(self._events)
        self._events = [e for e in self._events if e.timestamp >= cutoff_date]
        deleted_count = original_count - len(self._events)

        # TODO: Delete from PostgreSQL
        # DELETE FROM audit_events WHERE timestamp < %s

        return deleted_count

    def _persist_event(self, event: AuditEvent) -> None:
        """Persist event to database."""
        # TODO: Insert into PostgreSQL
        # INSERT INTO audit_events (...) VALUES (...)
        pass

    def _cache_event(self, event: AuditEvent) -> None:
        """Cache recent event in Redis."""
        if not self.cache:
            return

        # Cache under multiple keys for different access patterns
        keys = [
            f"audit:event:{event.id}",
            f"audit:user:{event.user_id}:latest",
            f"audit:org:{event.org_id}:latest",
        ]

        for key in keys:
            self.cache.setex(key, 3600, json.dumps(event.to_dict()))

    def _export_csv(self, events: List[AuditEvent]) -> str:
        """Export events as CSV."""
        if not events:
            return ""

        lines = []

        # Header
        lines.append(
            "ID,Timestamp,Action,Level,User ID,Org ID,Resource Type,"
            "Resource ID,Success,IP Address,Metadata"
        )

        # Rows
        for event in events:
            lines.append(
                f"{event.id},"
                f"{event.timestamp.isoformat()},"
                f"{event.action.value},"
                f"{event.level.value},"
                f"{event.user_id or ''},"
                f"{event.org_id or ''},"
                f"{event.resource_type or ''},"
                f"{event.resource_id or ''},"
                f"{event.success},"
                f"{event.ip_address or ''},"
                f"\"{json.dumps(event.metadata)}\""
            )

        return "\n".join(lines)


class ComplianceReporter:
    """
    Generate compliance reports from audit logs.

    Supports various compliance frameworks (SOC2, ISO27001, GDPR, etc.)
    """

    def __init__(self, audit_logger: AuditLogger):
        """
        Initialize compliance reporter.

        Args:
            audit_logger: Audit logger instance
        """
        self.audit_logger = audit_logger

    def generate_access_report(
        self,
        org_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        """
        Generate access control report.

        Args:
            org_id: Organization identifier
            start_date: Report start date
            end_date: Report end date

        Returns:
            Access report data
        """
        # Get all access events
        access_events = self.audit_logger.search(
            org_id=org_id,
            start_date=start_date,
            end_date=end_date,
            limit=10000,
        )

        # Filter access-related events
        access_events = [
            e for e in access_events
            if e.action in [AuditAction.ACCESS_GRANTED, AuditAction.ACCESS_DENIED]
        ]

        total_attempts = len(access_events)
        granted = len([e for e in access_events if e.success])
        denied = total_attempts - granted

        # Group by user
        by_user = {}
        for event in access_events:
            user_id = event.user_id or "unknown"
            if user_id not in by_user:
                by_user[user_id] = {'granted': 0, 'denied': 0}

            if event.success:
                by_user[user_id]['granted'] += 1
            else:
                by_user[user_id]['denied'] += 1

        return {
            'org_id': org_id,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_access_attempts': total_attempts,
            'access_granted': granted,
            'access_denied': denied,
            'by_user': by_user,
            'generated_at': datetime.utcnow().isoformat(),
        }

    def generate_change_report(
        self,
        org_id: str,
        start_date: datetime,
        end_date: datetime,
        resource_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate change tracking report.

        Args:
            org_id: Organization identifier
            start_date: Report start date
            end_date: Report end date
            resource_type: Optional resource type filter

        Returns:
            Change report data
        """
        events = self.audit_logger.search(
            org_id=org_id,
            start_date=start_date,
            end_date=end_date,
            resource_type=resource_type,
            limit=10000,
        )

        # Filter events with state changes
        change_events = [
            e for e in events
            if e.before_state or e.after_state
        ]

        # Categorize by action
        by_action = {}
        for event in change_events:
            action = event.action.value
            if action not in by_action:
                by_action[action] = 0
            by_action[action] += 1

        # Get top changers
        by_user = {}
        for event in change_events:
            user_id = event.user_id or "unknown"
            if user_id not in by_user:
                by_user[user_id] = 0
            by_user[user_id] += 1

        top_changers = sorted(
            by_user.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:10]

        return {
            'org_id': org_id,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'resource_type': resource_type,
            'total_changes': len(change_events),
            'by_action': by_action,
            'top_changers': [
                {'user_id': user_id, 'changes': count}
                for user_id, count in top_changers
            ],
            'generated_at': datetime.utcnow().isoformat(),
        }

    def generate_security_report(
        self,
        org_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        """
        Generate security events report.

        Args:
            org_id: Organization identifier
            start_date: Report start date
            end_date: Report end date

        Returns:
            Security report data
        """
        security_events = self.audit_logger.search(
            org_id=org_id,
            start_date=start_date,
            end_date=end_date,
            level=AuditLevel.SECURITY,
            limit=10000,
        )

        failed_logins = [
            e for e in security_events
            if e.action == AuditAction.LOGIN_FAILED
        ]

        access_denied = [
            e for e in security_events
            if e.action == AuditAction.ACCESS_DENIED
        ]

        # Get unique IPs with failed attempts
        suspicious_ips = {}
        for event in failed_logins:
            ip = event.ip_address or "unknown"
            if ip not in suspicious_ips:
                suspicious_ips[ip] = 0
            suspicious_ips[ip] += 1

        return {
            'org_id': org_id,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_security_events': len(security_events),
            'failed_login_attempts': len(failed_logins),
            'access_denied_events': len(access_denied),
            'suspicious_ips': [
                {'ip': ip, 'failed_attempts': count}
                for ip, count in sorted(
                    suspicious_ips.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )[:20]
            ],
            'generated_at': datetime.utcnow().isoformat(),
        }

    def generate_compliance_package(
        self,
        org_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        """
        Generate comprehensive compliance package.

        Args:
            org_id: Organization identifier
            start_date: Report start date
            end_date: Report end date

        Returns:
            Complete compliance package
        """
        return {
            'access_report': self.generate_access_report(org_id, start_date, end_date),
            'change_report': self.generate_change_report(org_id, start_date, end_date),
            'security_report': self.generate_security_report(org_id, start_date, end_date),
            'audit_log_export': self.audit_logger.export_logs(
                org_id,
                start_date,
                end_date,
                format="json",
            ),
        }


# PostgreSQL Schema
POSTGRES_SCHEMA = """
-- Audit events table
CREATE TABLE IF NOT EXISTS audit_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    action VARCHAR(100) NOT NULL,
    level VARCHAR(50) NOT NULL DEFAULT 'info',
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    org_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),
    ip_address VARCHAR(45),
    user_agent TEXT,
    success BOOLEAN DEFAULT TRUE,
    before_state JSONB,
    after_state JSONB,
    metadata JSONB DEFAULT '{}',
    session_id VARCHAR(255),
    request_id VARCHAR(255),
    event_hash VARCHAR(64)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_org ON audit_events(org_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_events(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_events(action);
CREATE INDEX IF NOT EXISTS idx_audit_resource ON audit_events(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_level ON audit_events(level);
CREATE INDEX IF NOT EXISTS idx_audit_session ON audit_events(session_id);
CREATE INDEX IF NOT EXISTS idx_audit_request ON audit_events(request_id);

-- Partitioning by month for large scale (PostgreSQL 10+)
-- CREATE TABLE audit_events_y2025m01 PARTITION OF audit_events
--     FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

-- Retention policy trigger
CREATE OR REPLACE FUNCTION cleanup_old_audit_events()
RETURNS void AS $$
BEGIN
    DELETE FROM audit_events
    WHERE timestamp < NOW() - INTERVAL '365 days';
END;
$$ LANGUAGE plpgsql;
"""
