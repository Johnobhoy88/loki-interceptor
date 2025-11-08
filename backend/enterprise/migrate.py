"""
Database migration script for LOKI Enterprise.

Creates all required tables, indexes, and constraints for the enterprise system.
"""

import sys
from typing import Optional
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


# Complete schema combining all modules
COMPLETE_SCHEMA = """
-- =============================================================================
-- LOKI Enterprise Database Schema
-- =============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- ORGANIZATIONS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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

CREATE INDEX IF NOT EXISTS idx_orgs_slug ON organizations(slug);
CREATE INDEX IF NOT EXISTS idx_orgs_status ON organizations(status);
CREATE INDEX IF NOT EXISTS idx_orgs_tier ON organizations(tier);
CREATE INDEX IF NOT EXISTS idx_orgs_parent ON organizations(parent_org_id);

-- =============================================================================
-- USERS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_login TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(255)
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);

-- =============================================================================
-- USER-ORGANIZATION MAPPINGS
-- =============================================================================

CREATE TABLE IF NOT EXISTS user_organizations (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    joined_at TIMESTAMP NOT NULL DEFAULT NOW(),
    invited_by UUID REFERENCES users(id),
    metadata JSONB DEFAULT '{}',
    PRIMARY KEY (user_id, org_id)
);

CREATE INDEX IF NOT EXISTS idx_user_orgs_user ON user_organizations(user_id);
CREATE INDEX IF NOT EXISTS idx_user_orgs_org ON user_organizations(org_id);
CREATE INDEX IF NOT EXISTS idx_user_orgs_primary ON user_organizations(user_id, is_primary) WHERE is_primary = TRUE;

-- =============================================================================
-- API KEYS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    scopes JSONB DEFAULT '[]',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP,
    last_used TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX IF NOT EXISTS idx_api_keys_user ON api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_org ON api_keys(org_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_active ON api_keys(is_active) WHERE is_active = TRUE;

-- =============================================================================
-- ROLES TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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

CREATE INDEX IF NOT EXISTS idx_roles_name ON roles(name);
CREATE INDEX IF NOT EXISTS idx_roles_org ON roles(org_id);
CREATE INDEX IF NOT EXISTS idx_roles_system ON roles(is_system_role);

-- =============================================================================
-- USER-ROLE ASSIGNMENTS
-- =============================================================================

CREATE TABLE IF NOT EXISTS user_roles (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP NOT NULL DEFAULT NOW(),
    assigned_by UUID REFERENCES users(id),
    expires_at TIMESTAMP,
    PRIMARY KEY (user_id, role_id, org_id)
);

CREATE INDEX IF NOT EXISTS idx_user_roles_user ON user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_org ON user_roles(org_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_role ON user_roles(role_id);

-- =============================================================================
-- RESOURCE PERMISSIONS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS resource_permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    resource_type VARCHAR(100) NOT NULL,
    resource_id VARCHAR(255) NOT NULL,
    permissions JSONB DEFAULT '[]',
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    granted_at TIMESTAMP NOT NULL DEFAULT NOW(),
    granted_by UUID REFERENCES users(id),
    expires_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_resource_perms_user ON resource_permissions(user_id);
CREATE INDEX IF NOT EXISTS idx_resource_perms_resource ON resource_permissions(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_resource_perms_org ON resource_permissions(org_id);

-- =============================================================================
-- AUDIT EVENTS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS audit_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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

CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_org ON audit_events(org_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_events(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_events(action);
CREATE INDEX IF NOT EXISTS idx_audit_resource ON audit_events(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_level ON audit_events(level);
CREATE INDEX IF NOT EXISTS idx_audit_session ON audit_events(session_id);
CREATE INDEX IF NOT EXISTS idx_audit_request ON audit_events(request_id);

-- =============================================================================
-- TRIGGERS & FUNCTIONS
-- =============================================================================

-- Function: Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger: Update organizations.updated_at
CREATE TRIGGER update_organizations_updated_at
    BEFORE UPDATE ON organizations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function: Cleanup old audit events
CREATE OR REPLACE FUNCTION cleanup_old_audit_events()
RETURNS void AS $$
BEGIN
    DELETE FROM audit_events
    WHERE timestamp < NOW() - INTERVAL '365 days';
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- ROW-LEVEL SECURITY (RLS)
-- =============================================================================

-- Enable RLS on organizations
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see organizations they belong to
DROP POLICY IF EXISTS org_isolation ON organizations;
CREATE POLICY org_isolation ON organizations
    FOR ALL
    USING (
        id IN (
            SELECT org_id FROM user_organizations
            WHERE user_id = current_setting('app.current_user_id', TRUE)::UUID
        )
    );

-- Enable RLS on audit_events
ALTER TABLE audit_events ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see audit events for their organizations
DROP POLICY IF EXISTS audit_org_isolation ON audit_events;
CREATE POLICY audit_org_isolation ON audit_events
    FOR SELECT
    USING (
        org_id IN (
            SELECT org_id FROM user_organizations
            WHERE user_id = current_setting('app.current_user_id', TRUE)::UUID
        )
    );

-- =============================================================================
-- INITIAL DATA: System Roles
-- =============================================================================

-- Insert system roles
INSERT INTO roles (name, display_name, description, permissions, is_system_role)
VALUES
    ('super_admin', 'Super Administrator', 'Full system access', '["system:admin"]', TRUE),
    ('admin', 'Administrator', 'Full organizational access',
     '["org:view","org:update","org:manage_users","doc:view","doc:create","doc:update","doc:delete","doc:analyze","doc:export","compliance:view","compliance:run","compliance:configure","audit:view","audit:export","user:view","user:create","user:update","user:delete","user:invite","api_key:view","api_key:create","api_key:revoke","report:view","report:create","report:export","settings:view","settings:update"]',
     TRUE),
    ('compliance_officer', 'Compliance Officer', 'Compliance operations',
     '["org:view","doc:view","doc:create","doc:update","doc:analyze","doc:export","compliance:view","compliance:run","compliance:configure","audit:view","user:view","report:view","report:create","report:export","settings:view"]',
     TRUE),
    ('auditor', 'Auditor', 'Read-only access',
     '["org:view","doc:view","doc:export","compliance:view","audit:view","audit:export","user:view","report:view","report:export","settings:view"]',
     TRUE),
    ('viewer', 'Viewer', 'Basic read-only',
     '["org:view","doc:view","compliance:view","report:view"]',
     TRUE)
ON CONFLICT DO NOTHING;

-- =============================================================================
-- UTILITY VIEWS
-- =============================================================================

-- View: Organization user counts
CREATE OR REPLACE VIEW organization_user_counts AS
SELECT
    o.id AS org_id,
    o.name AS org_name,
    COUNT(uo.user_id) AS user_count,
    o.max_users
FROM organizations o
LEFT JOIN user_organizations uo ON o.id = uo.org_id
GROUP BY o.id, o.name, o.max_users;

-- View: Active sessions summary
CREATE OR REPLACE VIEW audit_login_summary AS
SELECT
    org_id,
    user_id,
    COUNT(*) FILTER (WHERE action = 'login' AND success = TRUE) AS successful_logins,
    COUNT(*) FILTER (WHERE action = 'login_failed') AS failed_logins,
    MAX(timestamp) AS last_login
FROM audit_events
WHERE action IN ('login', 'login_failed')
    AND timestamp > NOW() - INTERVAL '30 days'
GROUP BY org_id, user_id;

-- =============================================================================
-- GRANT PERMISSIONS (adjust as needed)
-- =============================================================================

-- Grant permissions to application user
-- GRANT ALL ON ALL TABLES IN SCHEMA public TO loki_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO loki_app;

-- =============================================================================
-- COMPLETE
-- =============================================================================

-- Vacuum and analyze
VACUUM ANALYZE;
"""


def create_database(database_url: str, database_name: str) -> bool:
    """
    Create database if it doesn't exist.

    Args:
        database_url: PostgreSQL connection URL (to default db)
        database_name: Name of database to create

    Returns:
        True if created or already exists
    """
    try:
        # Connect to default postgres database
        conn = psycopg2.connect(database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (database_name,)
        )

        if cursor.fetchone():
            print(f"Database '{database_name}' already exists")
        else:
            cursor.execute(f"CREATE DATABASE {database_name}")
            print(f"Created database '{database_name}'")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"Error creating database: {e}")
        return False


def run_migration(database_url: str) -> bool:
    """
    Run database migration.

    Args:
        database_url: PostgreSQL connection URL

    Returns:
        True if successful
    """
    try:
        print(f"Connecting to database...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        print("Running migration...")

        # Execute complete schema
        cursor.execute(COMPLETE_SCHEMA)

        conn.commit()

        print("Migration completed successfully!")

        # Print summary
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)

        tables = cursor.fetchall()
        print(f"\nCreated {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def rollback_migration(database_url: str) -> bool:
    """
    Rollback migration (drop all tables).

    WARNING: This will delete all data!

    Args:
        database_url: PostgreSQL connection URL

    Returns:
        True if successful
    """
    try:
        print("WARNING: This will delete all enterprise tables and data!")
        confirmation = input("Type 'DELETE ALL DATA' to confirm: ")

        if confirmation != "DELETE ALL DATA":
            print("Rollback cancelled")
            return False

        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        print("Rolling back migration...")

        # Drop all tables in reverse order
        tables = [
            'audit_events',
            'resource_permissions',
            'user_roles',
            'roles',
            'api_keys',
            'user_organizations',
            'users',
            'organizations',
        ]

        for table in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
            print(f"Dropped table: {table}")

        # Drop views
        cursor.execute("DROP VIEW IF EXISTS organization_user_counts CASCADE")
        cursor.execute("DROP VIEW IF EXISTS audit_login_summary CASCADE")

        # Drop functions
        cursor.execute("DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE")
        cursor.execute("DROP FUNCTION IF EXISTS cleanup_old_audit_events() CASCADE")

        conn.commit()

        print("Rollback completed")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"Rollback failed: {e}")
        return False


def main():
    """Main migration CLI."""
    import argparse

    parser = argparse.ArgumentParser(description='LOKI Enterprise Database Migration')
    parser.add_argument(
        'command',
        choices=['migrate', 'rollback', 'create-db'],
        help='Migration command',
    )
    parser.add_argument(
        '--database-url',
        default='postgresql://localhost:5432/loki_db',
        help='PostgreSQL connection URL',
    )
    parser.add_argument(
        '--database-name',
        default='loki_db',
        help='Database name (for create-db)',
    )

    args = parser.parse_args()

    if args.command == 'create-db':
        # Extract base URL for postgres database
        base_url = args.database_url.rsplit('/', 1)[0] + '/postgres'
        success = create_database(base_url, args.database_name)

    elif args.command == 'migrate':
        success = run_migration(args.database_url)

    elif args.command == 'rollback':
        success = rollback_migration(args.database_url)

    else:
        print(f"Unknown command: {args.command}")
        success = False

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
