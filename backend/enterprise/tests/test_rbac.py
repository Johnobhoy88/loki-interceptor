"""
Unit tests for RBAC (Role-Based Access Control).
"""

import unittest
from backend.enterprise.rbac import (
    RBACManager,
    ResourceAccessControl,
    Role,
    Permission,
    RoleName,
)


class TestRBACManager(unittest.TestCase):
    """Test RBACManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.rbac = RBACManager()

    def test_system_roles_initialized(self):
        """Test that system roles are created on initialization."""
        admin_role = self.rbac.get_role_by_name(RoleName.ADMIN.value)
        self.assertIsNotNone(admin_role)
        self.assertTrue(admin_role.is_system_role)

    def test_admin_role_permissions(self):
        """Test admin role has expected permissions."""
        admin_role = self.rbac.get_role_by_name(RoleName.ADMIN.value)

        self.assertTrue(admin_role.has_permission(Permission.ORG_VIEW))
        self.assertTrue(admin_role.has_permission(Permission.USER_CREATE))
        self.assertTrue(admin_role.has_permission(Permission.DOC_DELETE))

    def test_viewer_role_permissions(self):
        """Test viewer role has limited permissions."""
        viewer_role = self.rbac.get_role_by_name(RoleName.VIEWER.value)

        self.assertTrue(viewer_role.has_permission(Permission.DOC_VIEW))
        self.assertFalse(viewer_role.has_permission(Permission.DOC_DELETE))
        self.assertFalse(viewer_role.has_permission(Permission.USER_CREATE))

    def test_create_custom_role(self):
        """Test creating custom role."""
        custom_role = self.rbac.create_custom_role(
            org_id="org-123",
            name="custom_role",
            display_name="Custom Role",
            description="A custom role",
            permissions={Permission.DOC_VIEW, Permission.DOC_CREATE},
        )

        self.assertFalse(custom_role.is_system_role)
        self.assertEqual(custom_role.org_id, "org-123")
        self.assertTrue(custom_role.has_permission(Permission.DOC_VIEW))

    def test_assign_role_to_user(self):
        """Test assigning role to user."""
        admin_role = self.rbac.get_role_by_name(RoleName.ADMIN.value)

        user_role = self.rbac.assign_role_to_user(
            user_id="user-123",
            role_id=admin_role.id,
            org_id="org-456",
        )

        self.assertEqual(user_role.user_id, "user-123")
        self.assertEqual(user_role.role_id, admin_role.id)

    def test_get_user_roles(self):
        """Test retrieving user's roles."""
        admin_role = self.rbac.get_role_by_name(RoleName.ADMIN.value)
        viewer_role = self.rbac.get_role_by_name(RoleName.VIEWER.value)

        self.rbac.assign_role_to_user("user-123", admin_role.id, "org-456")
        self.rbac.assign_role_to_user("user-123", viewer_role.id, "org-456")

        roles = self.rbac.get_user_roles("user-123", "org-456")

        self.assertEqual(len(roles), 2)

    def test_check_permission(self):
        """Test permission checking."""
        admin_role = self.rbac.get_role_by_name(RoleName.ADMIN.value)
        self.rbac.assign_role_to_user("user-123", admin_role.id, "org-456")

        # Admin should have permission
        has_perm = self.rbac.check_permission(
            user_id="user-123",
            org_id="org-456",
            permission=Permission.USER_CREATE,
        )

        self.assertTrue(has_perm)

    def test_check_permission_denied(self):
        """Test permission denied."""
        viewer_role = self.rbac.get_role_by_name(RoleName.VIEWER.value)
        self.rbac.assign_role_to_user("user-123", viewer_role.id, "org-456")

        # Viewer should not have permission to delete
        has_perm = self.rbac.check_permission(
            user_id="user-123",
            org_id="org-456",
            permission=Permission.DOC_DELETE,
        )

        self.assertFalse(has_perm)

    def test_require_permission(self):
        """Test require_permission raises on denial."""
        viewer_role = self.rbac.get_role_by_name(RoleName.VIEWER.value)
        self.rbac.assign_role_to_user("user-123", viewer_role.id, "org-456")

        with self.assertRaises(PermissionError):
            self.rbac.require_permission(
                user_id="user-123",
                org_id="org-456",
                permission=Permission.USER_DELETE,
            )

    def test_revoke_role_from_user(self):
        """Test revoking role from user."""
        admin_role = self.rbac.get_role_by_name(RoleName.ADMIN.value)
        self.rbac.assign_role_to_user("user-123", admin_role.id, "org-456")

        success = self.rbac.revoke_role_from_user("user-123", admin_role.id, "org-456")
        self.assertTrue(success)

        roles = self.rbac.get_user_roles("user-123", "org-456")
        self.assertEqual(len(roles), 0)

    def test_super_admin_has_all_permissions(self):
        """Test super admin has all permissions."""
        super_admin_role = self.rbac.get_role_by_name(RoleName.SUPER_ADMIN.value)

        # Super admin should have permission to any action
        self.assertTrue(super_admin_role.has_permission(Permission.DOC_DELETE))
        self.assertTrue(super_admin_role.has_permission(Permission.USER_CREATE))
        self.assertTrue(super_admin_role.has_permission(Permission.SETTINGS_UPDATE))


class TestResourceAccessControl(unittest.TestCase):
    """Test ResourceAccessControl."""

    def setUp(self):
        """Set up test fixtures."""
        self.rac = ResourceAccessControl()

    def test_grant_resource_permission(self):
        """Test granting resource-specific permission."""
        perm = self.rac.grant_resource_permission(
            user_id="user-123",
            resource_type="document",
            resource_id="doc-456",
            permissions={Permission.DOC_VIEW, Permission.DOC_UPDATE},
            org_id="org-789",
        )

        self.assertEqual(perm.user_id, "user-123")
        self.assertEqual(perm.resource_id, "doc-456")

    def test_check_resource_permission(self):
        """Test checking resource permission."""
        self.rac.grant_resource_permission(
            user_id="user-123",
            resource_type="document",
            resource_id="doc-456",
            permissions={Permission.DOC_VIEW},
            org_id="org-789",
        )

        has_perm = self.rac.check_resource_permission(
            user_id="user-123",
            resource_type="document",
            resource_id="doc-456",
            permission=Permission.DOC_VIEW,
            org_id="org-789",
        )

        self.assertTrue(has_perm)

    def test_check_resource_permission_denied(self):
        """Test resource permission denied."""
        self.rac.grant_resource_permission(
            user_id="user-123",
            resource_type="document",
            resource_id="doc-456",
            permissions={Permission.DOC_VIEW},
            org_id="org-789",
        )

        has_perm = self.rac.check_resource_permission(
            user_id="user-123",
            resource_type="document",
            resource_id="doc-456",
            permission=Permission.DOC_DELETE,  # Not granted
            org_id="org-789",
        )

        self.assertFalse(has_perm)

    def test_revoke_resource_permission(self):
        """Test revoking resource permission."""
        perm = self.rac.grant_resource_permission(
            user_id="user-123",
            resource_type="document",
            resource_id="doc-456",
            permissions={Permission.DOC_VIEW},
            org_id="org-789",
        )

        success = self.rac.revoke_resource_permission(perm.id)
        self.assertTrue(success)

        # Should no longer have permission
        has_perm = self.rac.check_resource_permission(
            user_id="user-123",
            resource_type="document",
            resource_id="doc-456",
            permission=Permission.DOC_VIEW,
            org_id="org-789",
        )

        self.assertFalse(has_perm)


class TestRole(unittest.TestCase):
    """Test Role entity."""

    def test_role_creation(self):
        """Test creating role."""
        role = Role(
            id="role-123",
            name="test_role",
            display_name="Test Role",
            description="A test role",
            permissions={Permission.DOC_VIEW},
            is_system_role=False,
        )

        self.assertEqual(role.name, "test_role")
        self.assertTrue(role.has_permission(Permission.DOC_VIEW))

    def test_add_permission_to_custom_role(self):
        """Test adding permission to custom role."""
        role = Role(
            id="role-123",
            name="test_role",
            display_name="Test Role",
            description="A test role",
            permissions={Permission.DOC_VIEW},
            is_system_role=False,
        )

        role.add_permission(Permission.DOC_CREATE)

        self.assertTrue(role.has_permission(Permission.DOC_CREATE))

    def test_cannot_modify_system_role(self):
        """Test that system roles cannot be modified."""
        role = Role(
            id="role-123",
            name="admin",
            display_name="Admin",
            description="System admin",
            permissions={Permission.DOC_VIEW},
            is_system_role=True,
        )

        with self.assertRaises(ValueError):
            role.add_permission(Permission.DOC_DELETE)


if __name__ == '__main__':
    unittest.main()
