"""
Role-Based Access Control (RBAC) for LOKI Enterprise

Comprehensive permission system with predefined roles, custom permissions,
and resource-level access control with audit trails.

Features:
- Predefined roles: Admin, Compliance Officer, Auditor, Viewer
- Fine-grained permission system
- Resource-level access control
- Permission inheritance
- Audit trail for all access decisions
"""

import uuid
from typing import Optional, List, Dict, Any, Set
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json


class Permission(Enum):
    """
    Granular permissions in the system.

    Format: RESOURCE_ACTION
    """
    # Organization management
    ORG_VIEW = "org:view"
    ORG_CREATE = "org:create"
    ORG_UPDATE = "org:update"
    ORG_DELETE = "org:delete"
    ORG_MANAGE_USERS = "org:manage_users"
    ORG_MANAGE_BILLING = "org:manage_billing"

    # Document operations
    DOC_VIEW = "doc:view"
    DOC_CREATE = "doc:create"
    DOC_UPDATE = "doc:update"
    DOC_DELETE = "doc:delete"
    DOC_ANALYZE = "doc:analyze"
    DOC_EXPORT = "doc:export"

    # Compliance operations
    COMPLIANCE_VIEW = "compliance:view"
    COMPLIANCE_RUN = "compliance:run"
    COMPLIANCE_CONFIGURE = "compliance:configure"

    # Audit logs
    AUDIT_VIEW = "audit:view"
    AUDIT_EXPORT = "audit:export"

    # User management
    USER_VIEW = "user:view"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_INVITE = "user:invite"

    # API keys
    API_KEY_VIEW = "api_key:view"
    API_KEY_CREATE = "api_key:create"
    API_KEY_REVOKE = "api_key:revoke"

    # Reports
    REPORT_VIEW = "report:view"
    REPORT_CREATE = "report:create"
    REPORT_EXPORT = "report:export"

    # Settings
    SETTINGS_VIEW = "settings:view"
    SETTINGS_UPDATE = "settings:update"

    # System admin
    SYSTEM_ADMIN = "system:admin"


class RoleName(Enum):
    """Predefined system roles."""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    COMPLIANCE_OFFICER = "compliance_officer"
    AUDITOR = "auditor"
    VIEWER = "viewer"
    CUSTOM = "custom"


@dataclass
class Role:
    """
    Role with associated permissions.

    Attributes:
        id: Role identifier
        name: Role name (from RoleName enum or custom)
        display_name: Human-readable name
        description: Role description
        permissions: Set of permissions
        is_system_role: Whether this is a predefined system role
        org_id: Organization ID (for org-specific custom roles)
        created_at: Creation timestamp
        metadata: Additional metadata
    """
    id: str
    name: str
    display_name: str
    description: str
    permissions: Set[Permission]
    is_system_role: bool = True
    org_id: Optional[str] = None
    created_at: datetime = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Initialize defaults."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}

    def has_permission(self, permission: Permission) -> bool:
        """
        Check if role has specific permission.

        Args:
            permission: Permission to check

        Returns:
            True if role has permission
        """
        # Super admin has all permissions
        if Permission.SYSTEM_ADMIN in self.permissions:
            return True

        return permission in self.permissions

    def add_permission(self, permission: Permission) -> None:
        """Add permission to role."""
        if not self.is_system_role:
            self.permissions.add(permission)
        else:
            raise ValueError("Cannot modify system role permissions")

    def remove_permission(self, permission: Permission) -> None:
        """Remove permission from role."""
        if not self.is_system_role:
            self.permissions.discard(permission)
        else:
            raise ValueError("Cannot modify system role permissions")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'permissions': [p.value for p in self.permissions],
            'is_system_role': self.is_system_role,
            'org_id': self.org_id,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata,
        }


@dataclass
class UserRole:
    """
    Maps user to role within an organization.

    Attributes:
        user_id: User identifier
        role_id: Role identifier
        org_id: Organization identifier
        assigned_at: When role was assigned
        assigned_by: User who assigned the role
        expires_at: Optional expiration timestamp
    """
    user_id: str
    role_id: str
    org_id: str
    assigned_at: datetime = None
    assigned_by: Optional[str] = None
    expires_at: Optional[datetime] = None

    def __post_init__(self):
        """Initialize defaults."""
        if self.assigned_at is None:
            self.assigned_at = datetime.utcnow()

    def is_expired(self) -> bool:
        """Check if role assignment has expired."""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False


@dataclass
class ResourcePermission:
    """
    Resource-level permission for fine-grained access control.

    Attributes:
        id: Permission identifier
        user_id: User identifier
        resource_type: Type of resource (document, report, etc.)
        resource_id: Specific resource identifier
        permissions: Set of allowed permissions on this resource
        org_id: Organization identifier
        granted_at: When permission was granted
        granted_by: User who granted permission
        expires_at: Optional expiration
    """
    id: str
    user_id: str
    resource_type: str
    resource_id: str
    permissions: Set[Permission]
    org_id: str
    granted_at: datetime = None
    granted_by: Optional[str] = None
    expires_at: Optional[datetime] = None

    def __post_init__(self):
        """Initialize defaults."""
        if self.granted_at is None:
            self.granted_at = datetime.utcnow()

    def has_permission(self, permission: Permission) -> bool:
        """Check if resource permission grants specific permission."""
        return permission in self.permissions

    def is_expired(self) -> bool:
        """Check if permission has expired."""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False


class RBACManager:
    """
    Manages roles, permissions, and access control decisions.

    Provides:
    - Role management (CRUD)
    - Permission checks
    - User-role assignments
    - Resource-level permissions
    """

    def __init__(self, db_connection=None, cache_backend=None, audit_logger=None):
        """
        Initialize RBAC manager.

        Args:
            db_connection: Database connection
            cache_backend: Redis cache backend
            audit_logger: Audit logger for access decisions
        """
        self.db = db_connection
        self.cache = cache_backend
        self.audit_logger = audit_logger

        # In-memory stores (replace with DB queries)
        self._roles: Dict[str, Role] = {}
        self._user_roles: Dict[str, List[UserRole]] = {}
        self._resource_permissions: Dict[str, List[ResourcePermission]] = {}

        # Initialize system roles
        self._initialize_system_roles()

    def _initialize_system_roles(self) -> None:
        """Create predefined system roles."""

        # Super Admin - all permissions
        self._create_system_role(
            RoleName.SUPER_ADMIN,
            "Super Administrator",
            "Full system access with all permissions",
            {Permission.SYSTEM_ADMIN},
        )

        # Admin - organization management
        self._create_system_role(
            RoleName.ADMIN,
            "Administrator",
            "Full organizational access and user management",
            {
                Permission.ORG_VIEW, Permission.ORG_UPDATE, Permission.ORG_MANAGE_USERS,
                Permission.DOC_VIEW, Permission.DOC_CREATE, Permission.DOC_UPDATE, Permission.DOC_DELETE,
                Permission.DOC_ANALYZE, Permission.DOC_EXPORT,
                Permission.COMPLIANCE_VIEW, Permission.COMPLIANCE_RUN, Permission.COMPLIANCE_CONFIGURE,
                Permission.AUDIT_VIEW, Permission.AUDIT_EXPORT,
                Permission.USER_VIEW, Permission.USER_CREATE, Permission.USER_UPDATE,
                Permission.USER_DELETE, Permission.USER_INVITE,
                Permission.API_KEY_VIEW, Permission.API_KEY_CREATE, Permission.API_KEY_REVOKE,
                Permission.REPORT_VIEW, Permission.REPORT_CREATE, Permission.REPORT_EXPORT,
                Permission.SETTINGS_VIEW, Permission.SETTINGS_UPDATE,
            },
        )

        # Compliance Officer - compliance operations
        self._create_system_role(
            RoleName.COMPLIANCE_OFFICER,
            "Compliance Officer",
            "Run compliance checks, manage documents, create reports",
            {
                Permission.ORG_VIEW,
                Permission.DOC_VIEW, Permission.DOC_CREATE, Permission.DOC_UPDATE,
                Permission.DOC_ANALYZE, Permission.DOC_EXPORT,
                Permission.COMPLIANCE_VIEW, Permission.COMPLIANCE_RUN, Permission.COMPLIANCE_CONFIGURE,
                Permission.AUDIT_VIEW,
                Permission.USER_VIEW,
                Permission.REPORT_VIEW, Permission.REPORT_CREATE, Permission.REPORT_EXPORT,
                Permission.SETTINGS_VIEW,
            },
        )

        # Auditor - read-only access to everything
        self._create_system_role(
            RoleName.AUDITOR,
            "Auditor",
            "Read-only access to documents, compliance, and audit logs",
            {
                Permission.ORG_VIEW,
                Permission.DOC_VIEW, Permission.DOC_EXPORT,
                Permission.COMPLIANCE_VIEW,
                Permission.AUDIT_VIEW, Permission.AUDIT_EXPORT,
                Permission.USER_VIEW,
                Permission.REPORT_VIEW, Permission.REPORT_EXPORT,
                Permission.SETTINGS_VIEW,
            },
        )

        # Viewer - basic read-only
        self._create_system_role(
            RoleName.VIEWER,
            "Viewer",
            "Basic read-only access to documents and reports",
            {
                Permission.ORG_VIEW,
                Permission.DOC_VIEW,
                Permission.COMPLIANCE_VIEW,
                Permission.REPORT_VIEW,
            },
        )

    def _create_system_role(
        self,
        role_name: RoleName,
        display_name: str,
        description: str,
        permissions: Set[Permission],
    ) -> Role:
        """Create and register system role."""
        role = Role(
            id=str(uuid.uuid4()),
            name=role_name.value,
            display_name=display_name,
            description=description,
            permissions=permissions,
            is_system_role=True,
        )
        self._roles[role.id] = role
        return role

    def create_custom_role(
        self,
        org_id: str,
        name: str,
        display_name: str,
        description: str,
        permissions: Set[Permission],
    ) -> Role:
        """
        Create custom organization-specific role.

        Args:
            org_id: Organization identifier
            name: Role name (slug)
            display_name: Human-readable name
            description: Role description
            permissions: Set of permissions

        Returns:
            Created Role instance

        Raises:
            ValueError: If role name already exists for org
        """
        # Check for duplicate
        for role in self._roles.values():
            if role.org_id == org_id and role.name == name:
                raise ValueError(f"Role '{name}' already exists for organization")

        role_id = str(uuid.uuid4())

        role = Role(
            id=role_id,
            name=name,
            display_name=display_name,
            description=description,
            permissions=permissions,
            is_system_role=False,
            org_id=org_id,
        )

        self._roles[role_id] = role

        # TODO: Insert into PostgreSQL
        # INSERT INTO roles (...) VALUES (...)

        return role

    def get_role(self, role_id: str) -> Optional[Role]:
        """
        Get role by ID.

        Args:
            role_id: Role identifier

        Returns:
            Role instance or None
        """
        return self._roles.get(role_id)

    def get_role_by_name(self, role_name: str, org_id: Optional[str] = None) -> Optional[Role]:
        """
        Get role by name.

        Args:
            role_name: Role name
            org_id: Organization ID (for custom roles)

        Returns:
            Role instance or None
        """
        for role in self._roles.values():
            if role.name == role_name:
                if role.is_system_role or role.org_id == org_id:
                    return role
        return None

    def assign_role_to_user(
        self,
        user_id: str,
        role_id: str,
        org_id: str,
        assigned_by: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> UserRole:
        """
        Assign role to user.

        Args:
            user_id: User identifier
            role_id: Role identifier
            org_id: Organization identifier
            assigned_by: User who assigned the role
            expires_at: Optional expiration timestamp

        Returns:
            UserRole instance

        Raises:
            ValueError: If role not found
        """
        role = self.get_role(role_id)
        if not role:
            raise ValueError(f"Role {role_id} not found")

        user_role = UserRole(
            user_id=user_id,
            role_id=role_id,
            org_id=org_id,
            assigned_by=assigned_by,
            expires_at=expires_at,
        )

        if user_id not in self._user_roles:
            self._user_roles[user_id] = []

        self._user_roles[user_id].append(user_role)

        # Log assignment
        if self.audit_logger:
            self.audit_logger.log_access(
                user_id=user_id,
                action="role_assigned",
                resource_type="role",
                resource_id=role_id,
                granted=True,
                metadata={'org_id': org_id, 'assigned_by': assigned_by},
            )

        # TODO: Insert into PostgreSQL
        # INSERT INTO user_roles (...) VALUES (...)

        return user_role

    def revoke_role_from_user(
        self,
        user_id: str,
        role_id: str,
        org_id: str,
    ) -> bool:
        """
        Revoke role from user.

        Args:
            user_id: User identifier
            role_id: Role identifier
            org_id: Organization identifier

        Returns:
            True if successful
        """
        if user_id in self._user_roles:
            original_count = len(self._user_roles[user_id])

            self._user_roles[user_id] = [
                ur for ur in self._user_roles[user_id]
                if not (ur.role_id == role_id and ur.org_id == org_id)
            ]

            if len(self._user_roles[user_id]) < original_count:
                # Log revocation
                if self.audit_logger:
                    self.audit_logger.log_access(
                        user_id=user_id,
                        action="role_revoked",
                        resource_type="role",
                        resource_id=role_id,
                        granted=False,
                        metadata={'org_id': org_id},
                    )

                # TODO: Delete from PostgreSQL
                # DELETE FROM user_roles WHERE user_id = %s AND role_id = %s AND org_id = %s

                return True

        return False

    def get_user_roles(self, user_id: str, org_id: str) -> List[Role]:
        """
        Get all roles for user in organization.

        Args:
            user_id: User identifier
            org_id: Organization identifier

        Returns:
            List of Role instances
        """
        user_roles = self._user_roles.get(user_id, [])
        roles = []

        for user_role in user_roles:
            if user_role.org_id == org_id and not user_role.is_expired():
                role = self.get_role(user_role.role_id)
                if role:
                    roles.append(role)

        return roles

    def check_permission(
        self,
        user_id: str,
        org_id: str,
        permission: Permission,
    ) -> bool:
        """
        Check if user has permission in organization.

        Args:
            user_id: User identifier
            org_id: Organization identifier
            permission: Permission to check

        Returns:
            True if user has permission
        """
        # Get user's roles
        roles = self.get_user_roles(user_id, org_id)

        # Check if any role grants permission
        for role in roles:
            if role.has_permission(permission):
                # Log successful check
                if self.audit_logger:
                    self.audit_logger.log_access(
                        user_id=user_id,
                        action="permission_check",
                        resource_type="permission",
                        resource_id=permission.value,
                        granted=True,
                        metadata={'org_id': org_id, 'role_id': role.id},
                    )
                return True

        # Log denied check
        if self.audit_logger:
            self.audit_logger.log_access(
                user_id=user_id,
                action="permission_check",
                resource_type="permission",
                resource_id=permission.value,
                granted=False,
                metadata={'org_id': org_id},
            )

        return False

    def require_permission(
        self,
        user_id: str,
        org_id: str,
        permission: Permission,
    ) -> None:
        """
        Require user to have permission (raise exception if not).

        Args:
            user_id: User identifier
            org_id: Organization identifier
            permission: Required permission

        Raises:
            PermissionError: If user lacks permission
        """
        if not self.check_permission(user_id, org_id, permission):
            raise PermissionError(
                f"User {user_id} lacks required permission: {permission.value}"
            )


class ResourceAccessControl:
    """
    Resource-level access control for fine-grained permissions.

    Allows granting specific permissions on individual resources
    (documents, reports, etc.) independent of role-based permissions.
    """

    def __init__(self, db_connection=None, audit_logger=None):
        """
        Initialize resource access control.

        Args:
            db_connection: Database connection
            audit_logger: Audit logger
        """
        self.db = db_connection
        self.audit_logger = audit_logger
        self._resource_permissions: Dict[str, ResourcePermission] = {}

    def grant_resource_permission(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        permissions: Set[Permission],
        org_id: str,
        granted_by: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> ResourcePermission:
        """
        Grant resource-specific permissions to user.

        Args:
            user_id: User identifier
            resource_type: Type of resource
            resource_id: Resource identifier
            permissions: Set of permissions to grant
            org_id: Organization identifier
            granted_by: User who granted permission
            expires_at: Optional expiration

        Returns:
            ResourcePermission instance
        """
        perm_id = str(uuid.uuid4())

        resource_perm = ResourcePermission(
            id=perm_id,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            permissions=permissions,
            org_id=org_id,
            granted_by=granted_by,
            expires_at=expires_at,
        )

        self._resource_permissions[perm_id] = resource_perm

        # Log grant
        if self.audit_logger:
            self.audit_logger.log_access(
                user_id=user_id,
                action="resource_permission_granted",
                resource_type=resource_type,
                resource_id=resource_id,
                granted=True,
                metadata={
                    'permissions': [p.value for p in permissions],
                    'granted_by': granted_by,
                    'org_id': org_id,
                },
            )

        # TODO: Insert into PostgreSQL
        # INSERT INTO resource_permissions (...) VALUES (...)

        return resource_perm

    def revoke_resource_permission(self, permission_id: str) -> bool:
        """
        Revoke resource permission.

        Args:
            permission_id: Permission identifier

        Returns:
            True if successful
        """
        perm = self._resource_permissions.pop(permission_id, None)

        if perm:
            # Log revocation
            if self.audit_logger:
                self.audit_logger.log_access(
                    user_id=perm.user_id,
                    action="resource_permission_revoked",
                    resource_type=perm.resource_type,
                    resource_id=perm.resource_id,
                    granted=False,
                    metadata={'org_id': perm.org_id},
                )

            # TODO: Delete from PostgreSQL
            # DELETE FROM resource_permissions WHERE id = %s

            return True

        return False

    def check_resource_permission(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        permission: Permission,
        org_id: str,
    ) -> bool:
        """
        Check if user has specific permission on resource.

        Args:
            user_id: User identifier
            resource_type: Resource type
            resource_id: Resource identifier
            permission: Permission to check
            org_id: Organization identifier

        Returns:
            True if user has permission on resource
        """
        for perm in self._resource_permissions.values():
            if (
                perm.user_id == user_id
                and perm.resource_type == resource_type
                and perm.resource_id == resource_id
                and perm.org_id == org_id
                and not perm.is_expired()
                and perm.has_permission(permission)
            ):
                return True

        return False


# PostgreSQL Schema
POSTGRES_SCHEMA = """
-- Roles table
CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    permissions JSONB DEFAULT '[]',
    is_system_role BOOLEAN DEFAULT FALSE,
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    UNIQUE(name, org_id)
);

-- User-Role assignments
CREATE TABLE IF NOT EXISTS user_roles (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP NOT NULL DEFAULT NOW(),
    assigned_by UUID REFERENCES users(id),
    expires_at TIMESTAMP,
    PRIMARY KEY (user_id, role_id, org_id)
);

-- Resource-level permissions
CREATE TABLE IF NOT EXISTS resource_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    resource_type VARCHAR(100) NOT NULL,
    resource_id VARCHAR(255) NOT NULL,
    permissions JSONB DEFAULT '[]',
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    granted_at TIMESTAMP NOT NULL DEFAULT NOW(),
    granted_by UUID REFERENCES users(id),
    expires_at TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_roles_name ON roles(name);
CREATE INDEX IF NOT EXISTS idx_roles_org ON roles(org_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_user ON user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_org ON user_roles(org_id);
CREATE INDEX IF NOT EXISTS idx_resource_perms_user ON resource_permissions(user_id);
CREATE INDEX IF NOT EXISTS idx_resource_perms_resource ON resource_permissions(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_resource_perms_org ON resource_permissions(org_id);
"""
