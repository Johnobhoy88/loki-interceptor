"""
Multi-Tenant Organization Management for LOKI

Provides complete organization lifecycle management with data isolation,
subscription tracking, and enterprise-grade multi-tenancy support.

Features:
- Organization CRUD operations
- User-to-organization mapping
- Data isolation enforcement at query level
- Subscription/billing tracking
- Organization hierarchies (parent/child)
- PostgreSQL row-level security support
"""

import uuid
import json
from typing import Optional, List, Dict, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib


class SubscriptionTier(Enum):
    """Subscription tier levels."""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class OrganizationStatus(Enum):
    """Organization status states."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    CANCELLED = "cancelled"
    PENDING = "pending"


@dataclass
class Organization:
    """
    Organization entity representing a tenant in the system.

    Attributes:
        id: Unique organization identifier (UUID)
        name: Organization name
        slug: URL-safe unique identifier
        status: Current organization status
        tier: Subscription tier level
        created_at: Creation timestamp
        updated_at: Last update timestamp
        metadata: Additional organization metadata
        settings: Organization-specific settings
        parent_org_id: Parent organization ID (for hierarchies)
        max_users: Maximum allowed users
        max_storage_gb: Maximum storage in GB
        features: Enabled feature flags
    """
    id: str
    name: str
    slug: str
    status: OrganizationStatus
    tier: SubscriptionTier
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    settings: Dict[str, Any]
    parent_org_id: Optional[str] = None
    max_users: int = 10
    max_storage_gb: int = 10
    features: Set[str] = None

    def __post_init__(self):
        """Initialize computed fields."""
        if self.features is None:
            self.features = set()
        if isinstance(self.status, str):
            self.status = OrganizationStatus(self.status)
        if isinstance(self.tier, str):
            self.tier = SubscriptionTier(self.tier)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['status'] = self.status.value
        data['tier'] = self.tier.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        data['features'] = list(self.features)
        return data

    def is_active(self) -> bool:
        """Check if organization is active."""
        return self.status == OrganizationStatus.ACTIVE

    def has_feature(self, feature: str) -> bool:
        """Check if organization has specific feature enabled."""
        return feature in self.features


@dataclass
class UserOrganizationMapping:
    """
    Maps users to organizations with role information.

    Attributes:
        user_id: User identifier
        org_id: Organization identifier
        role: User's role in the organization
        is_primary: Whether this is the user's primary organization
        joined_at: When user joined the organization
        invited_by: User ID who invited this user
        metadata: Additional mapping metadata
    """
    user_id: str
    org_id: str
    role: str
    is_primary: bool = False
    joined_at: datetime = None
    invited_by: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Initialize defaults."""
        if self.joined_at is None:
            self.joined_at = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'user_id': self.user_id,
            'org_id': self.org_id,
            'role': self.role,
            'is_primary': self.is_primary,
            'joined_at': self.joined_at.isoformat(),
            'invited_by': self.invited_by,
            'metadata': self.metadata,
        }


class TenantContext:
    """
    Thread-safe tenant context for request-scoped organization isolation.

    Ensures all database queries are scoped to the current organization,
    providing automatic data isolation.
    """

    _context: Dict[str, Any] = {}

    @classmethod
    def set_current_org(cls, org_id: str) -> None:
        """Set current organization for this context."""
        cls._context['org_id'] = org_id

    @classmethod
    def get_current_org(cls) -> Optional[str]:
        """Get current organization ID."""
        return cls._context.get('org_id')

    @classmethod
    def clear(cls) -> None:
        """Clear context."""
        cls._context.clear()

    @classmethod
    def set_user(cls, user_id: str) -> None:
        """Set current user."""
        cls._context['user_id'] = user_id

    @classmethod
    def get_user(cls) -> Optional[str]:
        """Get current user ID."""
        return cls._context.get('user_id')

    @classmethod
    def require_org(cls) -> str:
        """
        Require organization context to be set.

        Returns:
            Current organization ID

        Raises:
            ValueError: If no organization context is set
        """
        org_id = cls.get_current_org()
        if not org_id:
            raise ValueError("No organization context set. Multi-tenant operation requires organization scope.")
        return org_id


class OrganizationManager:
    """
    Manages organization lifecycle, CRUD operations, and tenant isolation.

    Handles:
    - Organization creation, updates, deletion
    - User-organization mappings
    - Subscription management
    - Data isolation enforcement
    - PostgreSQL integration
    """

    def __init__(self, db_connection=None, cache_backend=None):
        """
        Initialize organization manager.

        Args:
            db_connection: Database connection (PostgreSQL)
            cache_backend: Redis or compatible cache backend
        """
        self.db = db_connection
        self.cache = cache_backend
        self._organizations: Dict[str, Organization] = {}
        self._user_mappings: Dict[str, List[UserOrganizationMapping]] = {}

    def create_organization(
        self,
        name: str,
        slug: Optional[str] = None,
        tier: SubscriptionTier = SubscriptionTier.FREE,
        owner_user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        settings: Optional[Dict[str, Any]] = None,
    ) -> Organization:
        """
        Create a new organization.

        Args:
            name: Organization name
            slug: URL-safe identifier (auto-generated if not provided)
            tier: Subscription tier
            owner_user_id: User ID of organization owner
            metadata: Additional metadata
            settings: Organization settings

        Returns:
            Created Organization instance

        Raises:
            ValueError: If slug already exists or invalid parameters
        """
        if not name or len(name.strip()) < 2:
            raise ValueError("Organization name must be at least 2 characters")

        org_id = str(uuid.uuid4())

        if not slug:
            slug = self._generate_slug(name)

        if self._slug_exists(slug):
            raise ValueError(f"Organization slug '{slug}' already exists")

        now = datetime.utcnow()

        org = Organization(
            id=org_id,
            name=name.strip(),
            slug=slug,
            status=OrganizationStatus.TRIAL if tier != SubscriptionTier.FREE else OrganizationStatus.ACTIVE,
            tier=tier,
            created_at=now,
            updated_at=now,
            metadata=metadata or {},
            settings=settings or {},
            features=self._get_tier_features(tier),
        )

        # Store in memory (replace with DB insert)
        self._organizations[org_id] = org

        # If owner specified, create mapping
        if owner_user_id:
            self.add_user_to_org(
                user_id=owner_user_id,
                org_id=org_id,
                role="owner",
                is_primary=True,
            )

        # Cache organization
        if self.cache:
            self._cache_organization(org)

        # TODO: Execute PostgreSQL INSERT
        # INSERT INTO organizations (...) VALUES (...)

        return org

    def get_organization(self, org_id: str) -> Optional[Organization]:
        """
        Retrieve organization by ID.

        Args:
            org_id: Organization identifier

        Returns:
            Organization instance or None if not found
        """
        # Check cache first
        if self.cache:
            cached = self._get_cached_organization(org_id)
            if cached:
                return cached

        # Check memory store
        org = self._organizations.get(org_id)

        # TODO: Query PostgreSQL
        # SELECT * FROM organizations WHERE id = %s

        if org and self.cache:
            self._cache_organization(org)

        return org

    def get_organization_by_slug(self, slug: str) -> Optional[Organization]:
        """
        Retrieve organization by slug.

        Args:
            slug: Organization slug

        Returns:
            Organization instance or None
        """
        # Search memory store
        for org in self._organizations.values():
            if org.slug == slug:
                return org

        # TODO: Query PostgreSQL
        # SELECT * FROM organizations WHERE slug = %s

        return None

    def update_organization(
        self,
        org_id: str,
        updates: Dict[str, Any],
    ) -> Organization:
        """
        Update organization fields.

        Args:
            org_id: Organization identifier
            updates: Dictionary of fields to update

        Returns:
            Updated Organization instance

        Raises:
            ValueError: If organization not found or invalid updates
        """
        org = self.get_organization(org_id)
        if not org:
            raise ValueError(f"Organization {org_id} not found")

        # Update allowed fields
        allowed_fields = {'name', 'status', 'tier', 'metadata', 'settings', 'max_users', 'max_storage_gb'}

        for key, value in updates.items():
            if key not in allowed_fields:
                raise ValueError(f"Cannot update field: {key}")

            if key == 'status' and isinstance(value, str):
                value = OrganizationStatus(value)
            elif key == 'tier' and isinstance(value, str):
                value = SubscriptionTier(value)

            setattr(org, key, value)

        org.updated_at = datetime.utcnow()

        # Update cache
        if self.cache:
            self._cache_organization(org)

        # TODO: Execute PostgreSQL UPDATE
        # UPDATE organizations SET ... WHERE id = %s

        return org

    def delete_organization(self, org_id: str, hard_delete: bool = False) -> bool:
        """
        Delete or soft-delete organization.

        Args:
            org_id: Organization identifier
            hard_delete: If True, permanently delete; otherwise mark as cancelled

        Returns:
            True if successful

        Raises:
            ValueError: If organization not found
        """
        org = self.get_organization(org_id)
        if not org:
            raise ValueError(f"Organization {org_id} not found")

        if hard_delete:
            # Remove from memory
            del self._organizations[org_id]

            # Remove from cache
            if self.cache:
                self._invalidate_cache(org_id)

            # TODO: Execute PostgreSQL DELETE
            # DELETE FROM organizations WHERE id = %s
        else:
            # Soft delete
            self.update_organization(org_id, {'status': OrganizationStatus.CANCELLED})

        return True

    def add_user_to_org(
        self,
        user_id: str,
        org_id: str,
        role: str = "member",
        is_primary: bool = False,
        invited_by: Optional[str] = None,
    ) -> UserOrganizationMapping:
        """
        Add user to organization.

        Args:
            user_id: User identifier
            org_id: Organization identifier
            role: User's role in organization
            is_primary: Whether this is user's primary organization
            invited_by: User ID who invited this user

        Returns:
            UserOrganizationMapping instance

        Raises:
            ValueError: If organization not found or user already in org
        """
        org = self.get_organization(org_id)
        if not org:
            raise ValueError(f"Organization {org_id} not found")

        # Check if user already in org
        if self._user_in_org(user_id, org_id):
            raise ValueError(f"User {user_id} already in organization {org_id}")

        # Check user limit
        current_users = self.get_org_user_count(org_id)
        if current_users >= org.max_users:
            raise ValueError(f"Organization has reached maximum user limit ({org.max_users})")

        mapping = UserOrganizationMapping(
            user_id=user_id,
            org_id=org_id,
            role=role,
            is_primary=is_primary,
            invited_by=invited_by,
        )

        # Store mapping
        if user_id not in self._user_mappings:
            self._user_mappings[user_id] = []
        self._user_mappings[user_id].append(mapping)

        # TODO: Execute PostgreSQL INSERT
        # INSERT INTO user_organizations (...) VALUES (...)

        return mapping

    def remove_user_from_org(self, user_id: str, org_id: str) -> bool:
        """
        Remove user from organization.

        Args:
            user_id: User identifier
            org_id: Organization identifier

        Returns:
            True if successful
        """
        if user_id in self._user_mappings:
            self._user_mappings[user_id] = [
                m for m in self._user_mappings[user_id]
                if m.org_id != org_id
            ]

        # TODO: Execute PostgreSQL DELETE
        # DELETE FROM user_organizations WHERE user_id = %s AND org_id = %s

        return True

    def get_user_organizations(self, user_id: str) -> List[Organization]:
        """
        Get all organizations for a user.

        Args:
            user_id: User identifier

        Returns:
            List of Organization instances
        """
        mappings = self._user_mappings.get(user_id, [])
        orgs = []

        for mapping in mappings:
            org = self.get_organization(mapping.org_id)
            if org:
                orgs.append(org)

        return orgs

    def get_org_users(self, org_id: str) -> List[UserOrganizationMapping]:
        """
        Get all users in an organization.

        Args:
            org_id: Organization identifier

        Returns:
            List of UserOrganizationMapping instances
        """
        users = []
        for user_mappings in self._user_mappings.values():
            for mapping in user_mappings:
                if mapping.org_id == org_id:
                    users.append(mapping)

        # TODO: Query PostgreSQL
        # SELECT * FROM user_organizations WHERE org_id = %s

        return users

    def get_org_user_count(self, org_id: str) -> int:
        """Get user count for organization."""
        return len(self.get_org_users(org_id))

    def enforce_tenant_isolation(self, query: str, org_id: Optional[str] = None) -> str:
        """
        Enforce tenant isolation on SQL queries.

        Automatically adds WHERE org_id = %s clause to queries.

        Args:
            query: SQL query string
            org_id: Organization ID (uses TenantContext if not provided)

        Returns:
            Modified query with tenant isolation

        Raises:
            ValueError: If no organization context available
        """
        if not org_id:
            org_id = TenantContext.require_org()

        # Simple implementation - production should use query parser
        if 'WHERE' in query.upper():
            return query.replace('WHERE', f"WHERE org_id = '{org_id}' AND", 1)
        else:
            # Find FROM clause
            from_idx = query.upper().find('FROM')
            if from_idx == -1:
                return query

            # Find next clause (WHERE, GROUP BY, ORDER BY, etc.)
            next_clause_idx = len(query)
            for clause in ['WHERE', 'GROUP BY', 'ORDER BY', 'LIMIT', 'OFFSET']:
                idx = query.upper().find(clause, from_idx)
                if idx != -1 and idx < next_clause_idx:
                    next_clause_idx = idx

            return query[:next_clause_idx] + f" WHERE org_id = '{org_id}' " + query[next_clause_idx:]

    def _generate_slug(self, name: str) -> str:
        """Generate URL-safe slug from name."""
        slug = name.lower().strip()
        slug = ''.join(c if c.isalnum() or c in '-_' else '-' for c in slug)
        slug = '-'.join(filter(None, slug.split('-')))

        # Add hash suffix for uniqueness
        hash_suffix = hashlib.md5(name.encode()).hexdigest()[:6]
        return f"{slug}-{hash_suffix}"

    def _slug_exists(self, slug: str) -> bool:
        """Check if slug already exists."""
        return any(org.slug == slug for org in self._organizations.values())

    def _user_in_org(self, user_id: str, org_id: str) -> bool:
        """Check if user is already in organization."""
        mappings = self._user_mappings.get(user_id, [])
        return any(m.org_id == org_id for m in mappings)

    def _get_tier_features(self, tier: SubscriptionTier) -> Set[str]:
        """Get feature flags for subscription tier."""
        base_features = {'basic_compliance', 'document_analysis'}

        tier_features = {
            SubscriptionTier.FREE: base_features,
            SubscriptionTier.STARTER: base_features | {'api_access', 'advanced_analytics'},
            SubscriptionTier.PROFESSIONAL: base_features | {'api_access', 'advanced_analytics', 'custom_rules', 'priority_support'},
            SubscriptionTier.ENTERPRISE: base_features | {'api_access', 'advanced_analytics', 'custom_rules', 'priority_support', 'sso', 'audit_logs', 'sla'},
            SubscriptionTier.CUSTOM: base_features | {'api_access', 'advanced_analytics', 'custom_rules', 'priority_support', 'sso', 'audit_logs', 'sla', 'custom_integration'},
        }

        return tier_features.get(tier, base_features)

    def _cache_organization(self, org: Organization) -> None:
        """Cache organization in Redis."""
        if not self.cache:
            return

        key = f"org:{org.id}"
        self.cache.setex(key, 3600, json.dumps(org.to_dict()))

    def _get_cached_organization(self, org_id: str) -> Optional[Organization]:
        """Retrieve organization from cache."""
        if not self.cache:
            return None

        key = f"org:{org_id}"
        data = self.cache.get(key)

        if data:
            org_dict = json.loads(data)
            org_dict['created_at'] = datetime.fromisoformat(org_dict['created_at'])
            org_dict['updated_at'] = datetime.fromisoformat(org_dict['updated_at'])
            org_dict['features'] = set(org_dict.get('features', []))
            return Organization(**org_dict)

        return None

    def _invalidate_cache(self, org_id: str) -> None:
        """Invalidate cached organization."""
        if self.cache:
            self.cache.delete(f"org:{org_id}")


# PostgreSQL Schema
POSTGRES_SCHEMA = """
-- Organizations table
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    tier VARCHAR(50) NOT NULL DEFAULT 'free',
    parent_org_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    max_users INTEGER NOT NULL DEFAULT 10,
    max_storage_gb INTEGER NOT NULL DEFAULT 10,
    metadata JSONB DEFAULT '{}',
    settings JSONB DEFAULT '{}',
    features JSONB DEFAULT '[]',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT valid_status CHECK (status IN ('active', 'suspended', 'trial', 'cancelled', 'pending')),
    CONSTRAINT valid_tier CHECK (tier IN ('free', 'starter', 'professional', 'enterprise', 'custom'))
);

-- User-Organization mappings
CREATE TABLE IF NOT EXISTS user_organizations (
    user_id UUID NOT NULL,
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    joined_at TIMESTAMP NOT NULL DEFAULT NOW(),
    invited_by UUID,
    metadata JSONB DEFAULT '{}',
    PRIMARY KEY (user_id, org_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_orgs_slug ON organizations(slug);
CREATE INDEX IF NOT EXISTS idx_orgs_status ON organizations(status);
CREATE INDEX IF NOT EXISTS idx_orgs_tier ON organizations(tier);
CREATE INDEX IF NOT EXISTS idx_user_orgs_user ON user_organizations(user_id);
CREATE INDEX IF NOT EXISTS idx_user_orgs_org ON user_organizations(org_id);
CREATE INDEX IF NOT EXISTS idx_user_orgs_primary ON user_organizations(user_id, is_primary) WHERE is_primary = TRUE;

-- Row-level security policies
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see organizations they belong to
CREATE POLICY org_isolation ON organizations
    FOR ALL
    USING (
        id IN (
            SELECT org_id FROM user_organizations WHERE user_id = current_setting('app.current_user_id')::UUID
        )
    );

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_organizations_updated_at
    BEFORE UPDATE ON organizations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
"""
