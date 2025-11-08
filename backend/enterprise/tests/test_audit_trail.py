"""
Unit tests for audit trail system.
"""

import unittest
from datetime import datetime, timedelta
from backend.enterprise.audit_trail import (
    AuditLogger,
    AuditEvent,
    ComplianceReporter,
    AuditAction,
    AuditLevel,
)


class TestAuditEvent(unittest.TestCase):
    """Test AuditEvent entity."""

    def test_event_creation(self):
        """Test creating audit event."""
        event = AuditEvent(
            id="event-123",
            timestamp=datetime.utcnow(),
            action=AuditAction.USER_CREATED,
            level=AuditLevel.INFO,
            user_id="user-123",
            org_id="org-456",
            success=True,
        )

        self.assertEqual(event.action, AuditAction.USER_CREATED)
        self.assertEqual(event.level, AuditLevel.INFO)
        self.assertTrue(event.success)

    def test_event_to_dict(self):
        """Test event serialization."""
        event = AuditEvent(
            id="event-123",
            timestamp=datetime.utcnow(),
            action=AuditAction.USER_CREATED,
            level=AuditLevel.INFO,
            user_id="user-123",
            org_id="org-456",
        )

        event_dict = event.to_dict()

        self.assertIn('id', event_dict)
        self.assertIn('action', event_dict)
        self.assertEqual(event_dict['action'], 'user_created')

    def test_get_changes(self):
        """Test change tracking."""
        before = {'name': 'Old Name', 'status': 'active'}
        after = {'name': 'New Name', 'status': 'active'}

        event = AuditEvent(
            id="event-123",
            timestamp=datetime.utcnow(),
            action=AuditAction.ORG_UPDATED,
            level=AuditLevel.INFO,
            user_id="user-123",
            org_id="org-456",
            before_state=before,
            after_state=after,
        )

        changes = event.get_changes()

        self.assertIn('name', changes)
        self.assertEqual(changes['name'], ('Old Name', 'New Name'))
        self.assertNotIn('status', changes)

    def test_calculate_hash(self):
        """Test event hash calculation."""
        event = AuditEvent(
            id="event-123",
            timestamp=datetime.utcnow(),
            action=AuditAction.USER_CREATED,
            level=AuditLevel.INFO,
            user_id="user-123",
            org_id="org-456",
        )

        hash1 = event.calculate_hash()
        self.assertIsInstance(hash1, str)
        self.assertEqual(len(hash1), 64)  # SHA-256 hex

        # Same event should produce same hash
        hash2 = event.calculate_hash()
        self.assertEqual(hash1, hash2)


class TestAuditLogger(unittest.TestCase):
    """Test AuditLogger."""

    def setUp(self):
        """Set up test fixtures."""
        self.logger = AuditLogger()

    def test_log_event(self):
        """Test logging audit event."""
        event = self.logger.log(
            action=AuditAction.USER_CREATED,
            user_id="user-123",
            org_id="org-456",
            success=True,
        )

        self.assertIsNotNone(event.id)
        self.assertEqual(event.action, AuditAction.USER_CREATED)

    def test_log_access(self):
        """Test logging access control decision."""
        event = self.logger.log_access(
            user_id="user-123",
            action="view_document",
            resource_type="document",
            resource_id="doc-456",
            granted=True,
        )

        self.assertEqual(event.action, AuditAction.ACCESS_GRANTED)
        self.assertTrue(event.success)

    def test_log_access_denied(self):
        """Test logging denied access."""
        event = self.logger.log_access(
            user_id="user-123",
            action="delete_document",
            resource_type="document",
            resource_id="doc-456",
            granted=False,
        )

        self.assertEqual(event.action, AuditAction.ACCESS_DENIED)
        self.assertEqual(event.level, AuditLevel.SECURITY)

    def test_log_change(self):
        """Test logging state change."""
        before = {'status': 'active'}
        after = {'status': 'suspended'}

        event = self.logger.log_change(
            action=AuditAction.ORG_UPDATED,
            user_id="user-123",
            org_id="org-456",
            resource_type="organization",
            resource_id="org-456",
            before=before,
            after=after,
        )

        self.assertEqual(event.before_state, before)
        self.assertEqual(event.after_state, after)

    def test_search_by_org(self):
        """Test searching events by organization."""
        # Log events for different orgs
        self.logger.log(
            action=AuditAction.USER_CREATED,
            user_id="user-123",
            org_id="org-1",
        )
        self.logger.log(
            action=AuditAction.USER_CREATED,
            user_id="user-456",
            org_id="org-2",
        )

        results = self.logger.search(org_id="org-1")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].org_id, "org-1")

    def test_search_by_user(self):
        """Test searching events by user."""
        self.logger.log(
            action=AuditAction.LOGIN,
            user_id="user-123",
            org_id="org-456",
        )
        self.logger.log(
            action=AuditAction.LOGOUT,
            user_id="user-123",
            org_id="org-456",
        )

        results = self.logger.search(user_id="user-123")

        self.assertEqual(len(results), 2)

    def test_search_by_action(self):
        """Test searching events by action type."""
        self.logger.log(action=AuditAction.LOGIN, user_id="user-123", org_id="org-456")
        self.logger.log(action=AuditAction.LOGOUT, user_id="user-123", org_id="org-456")
        self.logger.log(action=AuditAction.LOGIN, user_id="user-456", org_id="org-456")

        results = self.logger.search(action=AuditAction.LOGIN)

        self.assertEqual(len(results), 2)
        for event in results:
            self.assertEqual(event.action, AuditAction.LOGIN)

    def test_search_with_date_range(self):
        """Test searching events within date range."""
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)

        self.logger.log(action=AuditAction.USER_CREATED, user_id="user-123", org_id="org-456")

        # Search with date range including today
        results = self.logger.search(
            org_id="org-456",
            start_date=yesterday,
            end_date=tomorrow,
        )

        self.assertGreater(len(results), 0)

    def test_get_user_activity(self):
        """Test retrieving user activity."""
        self.logger.log(action=AuditAction.LOGIN, user_id="user-123", org_id="org-456")
        self.logger.log(action=AuditAction.DOC_VIEWED, user_id="user-123", org_id="org-456")

        activity = self.logger.get_user_activity("user-123", days=30)

        self.assertGreaterEqual(len(activity), 2)

    def test_get_resource_history(self):
        """Test retrieving resource history."""
        self.logger.log(
            action=AuditAction.DOC_CREATED,
            user_id="user-123",
            org_id="org-456",
            resource_type="document",
            resource_id="doc-123",
        )
        self.logger.log(
            action=AuditAction.DOC_UPDATED,
            user_id="user-123",
            org_id="org-456",
            resource_type="document",
            resource_id="doc-123",
        )

        history = self.logger.get_resource_history(
            resource_type="document",
            resource_id="doc-123",
            org_id="org-456",
        )

        self.assertEqual(len(history), 2)

    def test_export_logs_json(self):
        """Test exporting logs as JSON."""
        start = datetime.utcnow() - timedelta(days=1)
        end = datetime.utcnow() + timedelta(days=1)

        self.logger.log(action=AuditAction.USER_CREATED, user_id="user-123", org_id="org-456")

        export = self.logger.export_logs(
            org_id="org-456",
            start_date=start,
            end_date=end,
            format="json",
        )

        self.assertIsInstance(export, str)
        self.assertIn("user_created", export)

    def test_export_logs_csv(self):
        """Test exporting logs as CSV."""
        start = datetime.utcnow() - timedelta(days=1)
        end = datetime.utcnow() + timedelta(days=1)

        self.logger.log(action=AuditAction.USER_CREATED, user_id="user-123", org_id="org-456")

        export = self.logger.export_logs(
            org_id="org-456",
            start_date=start,
            end_date=end,
            format="csv",
        )

        self.assertIsInstance(export, str)
        self.assertIn("ID,Timestamp,Action", export)


class TestComplianceReporter(unittest.TestCase):
    """Test ComplianceReporter."""

    def setUp(self):
        """Set up test fixtures."""
        self.logger = AuditLogger()
        self.reporter = ComplianceReporter(self.logger)

    def test_generate_access_report(self):
        """Test generating access control report."""
        start = datetime.utcnow() - timedelta(days=1)
        end = datetime.utcnow() + timedelta(days=1)

        self.logger.log_access("user-123", "view", "doc", "doc-1", granted=True)
        self.logger.log_access("user-123", "delete", "doc", "doc-1", granted=False)

        report = self.reporter.generate_access_report("org-456", start, end)

        self.assertIn('total_access_attempts', report)
        self.assertIn('access_granted', report)
        self.assertIn('access_denied', report)

    def test_generate_change_report(self):
        """Test generating change tracking report."""
        start = datetime.utcnow() - timedelta(days=1)
        end = datetime.utcnow() + timedelta(days=1)

        self.logger.log_change(
            action=AuditAction.ORG_UPDATED,
            user_id="user-123",
            org_id="org-456",
            resource_type="organization",
            resource_id="org-456",
            before={'name': 'Old'},
            after={'name': 'New'},
        )

        report = self.reporter.generate_change_report("org-456", start, end)

        self.assertIn('total_changes', report)
        self.assertIn('by_action', report)

    def test_generate_security_report(self):
        """Test generating security events report."""
        start = datetime.utcnow() - timedelta(days=1)
        end = datetime.utcnow() + timedelta(days=1)

        self.logger.log(
            action=AuditAction.LOGIN_FAILED,
            level=AuditLevel.SECURITY,
            user_id="user-123",
            org_id="org-456",
            ip_address="192.168.1.1",
        )

        report = self.reporter.generate_security_report("org-456", start, end)

        self.assertIn('total_security_events', report)
        self.assertIn('failed_login_attempts', report)
        self.assertIn('suspicious_ips', report)

    def test_generate_compliance_package(self):
        """Test generating complete compliance package."""
        start = datetime.utcnow() - timedelta(days=1)
        end = datetime.utcnow() + timedelta(days=1)

        package = self.reporter.generate_compliance_package("org-456", start, end)

        self.assertIn('access_report', package)
        self.assertIn('change_report', package)
        self.assertIn('security_report', package)
        self.assertIn('audit_log_export', package)


if __name__ == '__main__':
    unittest.main()
