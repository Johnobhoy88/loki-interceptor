"""
Unit tests for multi-tenant organization management.
"""

import unittest
from datetime import datetime
from backend.enterprise.multi_tenant import (
    Organization,
    OrganizationManager,
    UserOrganizationMapping,
    TenantContext,
    SubscriptionTier,
    OrganizationStatus,
)


class TestOrganization(unittest.TestCase):
    """Test Organization entity."""

    def test_organization_creation(self):
        """Test creating organization instance."""
        org = Organization(
            id="test-id",
            name="Test Org",
            slug="test-org",
            status=OrganizationStatus.ACTIVE,
            tier=SubscriptionTier.FREE,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata={},
            settings={},
        )

        self.assertEqual(org.name, "Test Org")
        self.assertEqual(org.slug, "test-org")
        self.assertTrue(org.is_active())

    def test_organization_features(self):
        """Test feature checking."""
        org = Organization(
            id="test-id",
            name="Test Org",
            slug="test-org",
            status=OrganizationStatus.ACTIVE,
            tier=SubscriptionTier.FREE,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata={},
            settings={},
            features={'feature1', 'feature2'},
        )

        self.assertTrue(org.has_feature('feature1'))
        self.assertFalse(org.has_feature('feature3'))

    def test_organization_to_dict(self):
        """Test dictionary serialization."""
        org = Organization(
            id="test-id",
            name="Test Org",
            slug="test-org",
            status=OrganizationStatus.ACTIVE,
            tier=SubscriptionTier.FREE,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata={},
            settings={},
        )

        org_dict = org.to_dict()

        self.assertIn('id', org_dict)
        self.assertIn('name', org_dict)
        self.assertEqual(org_dict['status'], 'active')


class TestOrganizationManager(unittest.TestCase):
    """Test OrganizationManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = OrganizationManager()

    def test_create_organization(self):
        """Test organization creation."""
        org = self.manager.create_organization(
            name="Test Organization",
            tier=SubscriptionTier.STARTER,
        )

        self.assertIsNotNone(org.id)
        self.assertEqual(org.name, "Test Organization")
        self.assertIsNotNone(org.slug)

    def test_create_organization_with_owner(self):
        """Test creating organization with owner."""
        org = self.manager.create_organization(
            name="Test Org",
            owner_user_id="user-123",
        )

        mappings = self.manager.get_org_users(org.id)
        self.assertEqual(len(mappings), 1)
        self.assertEqual(mappings[0].role, "owner")

    def test_get_organization(self):
        """Test retrieving organization."""
        org = self.manager.create_organization(name="Test Org")
        retrieved = self.manager.get_organization(org.id)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, org.id)

    def test_update_organization(self):
        """Test updating organization."""
        org = self.manager.create_organization(name="Test Org")
        updated = self.manager.update_organization(
            org.id,
            {'name': 'Updated Org'},
        )

        self.assertEqual(updated.name, 'Updated Org')

    def test_add_user_to_org(self):
        """Test adding user to organization."""
        org = self.manager.create_organization(name="Test Org")
        mapping = self.manager.add_user_to_org(
            user_id="user-123",
            org_id=org.id,
            role="member",
        )

        self.assertEqual(mapping.user_id, "user-123")
        self.assertEqual(mapping.org_id, org.id)

    def test_user_limit_enforcement(self):
        """Test user limit enforcement."""
        org = self.manager.create_organization(name="Test Org")
        org.max_users = 2

        # Add first user
        self.manager.add_user_to_org("user-1", org.id)

        # Add second user
        self.manager.add_user_to_org("user-2", org.id)

        # Third user should fail
        with self.assertRaises(ValueError):
            self.manager.add_user_to_org("user-3", org.id)


class TestTenantContext(unittest.TestCase):
    """Test TenantContext."""

    def setUp(self):
        """Clear context before each test."""
        TenantContext.clear()

    def test_set_get_org(self):
        """Test setting and getting organization context."""
        TenantContext.set_current_org("org-123")
        self.assertEqual(TenantContext.get_current_org(), "org-123")

    def test_require_org(self):
        """Test requiring organization context."""
        with self.assertRaises(ValueError):
            TenantContext.require_org()

        TenantContext.set_current_org("org-123")
        org_id = TenantContext.require_org()
        self.assertEqual(org_id, "org-123")

    def test_clear_context(self):
        """Test clearing context."""
        TenantContext.set_current_org("org-123")
        TenantContext.clear()
        self.assertIsNone(TenantContext.get_current_org())


if __name__ == '__main__':
    unittest.main()
