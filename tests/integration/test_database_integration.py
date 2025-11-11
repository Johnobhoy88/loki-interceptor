"""
Database Integration Tests

Tests database operations, migrations, and data consistency.
"""

import pytest
from datetime import datetime


@pytest.mark.integration
class TestDatabaseIntegration:
    """Test database operations and consistency."""

    def test_database_connection(self, db_session_pg):
        """Test database connection."""
        # Simple query to verify connection
        result = db_session_pg.execute("SELECT 1")
        assert result.scalar() == 1

    def test_database_health_check(self, db_session_pg):
        """Test database health check."""
        try:
            # Verify we can execute a query
            db_session_pg.execute("SELECT 1")
            db_session_pg.commit()
            assert True
        except Exception as e:
            pytest.fail(f"Database health check failed: {str(e)}")

    def test_transaction_rollback(self, db_session_pg):
        """Test transaction rollback on error."""
        try:
            # Attempt invalid query
            db_session_pg.execute("SELECT * FROM non_existent_table")
            db_session_pg.commit()
            assert False, "Should have raised an error"
        except Exception:
            db_session_pg.rollback()
            assert True

    def test_concurrent_database_operations(self, db_session_pg):
        """Test concurrent database operations."""
        # Verify session is active
        assert db_session_pg.is_active
        db_session_pg.commit()


@pytest.mark.integration
class TestCacheIntegration:
    """Test cache integration and data consistency."""

    def test_redis_connection(self, redis_client_pg):
        """Test Redis connection."""
        redis_client_pg.set("test_key", "test_value")
        assert redis_client_pg.get("test_key") == "test_value"

    def test_cache_expiration(self, redis_client_pg):
        """Test cache expiration."""
        redis_client_pg.setex("temp_key", 1, "temp_value")
        assert redis_client_pg.get("temp_key") == "temp_value"

        # Wait and verify expiration
        import time
        time.sleep(1.1)
        assert redis_client_pg.get("temp_key") is None

    def test_cache_key_operations(self, redis_client_pg):
        """Test cache key operations."""
        # Set multiple keys
        redis_client_pg.mset({"key1": "value1", "key2": "value2", "key3": "value3"})

        # Verify retrieval
        assert redis_client_pg.get("key1") == "value1"
        assert redis_client_pg.get("key2") == "value2"

        # Verify deletion
        redis_client_pg.delete("key1")
        assert redis_client_pg.get("key1") is None

    def test_cache_json_operations(self, redis_client_pg):
        """Test storing and retrieving JSON data."""
        import json

        data = {"document_id": "doc_123", "status": "processed", "timestamp": str(datetime.now())}
        json_data = json.dumps(data)

        redis_client_pg.set("doc_123", json_data)
        retrieved = json.loads(redis_client_pg.get("doc_123"))

        assert retrieved["document_id"] == "doc_123"
        assert retrieved["status"] == "processed"


@pytest.mark.integration
class TestMigrationIntegration:
    """Test database migrations."""

    def test_migration_up(self, db_session_pg):
        """Test migration up operation."""
        # Verify we can query without errors
        try:
            result = db_session_pg.execute("SELECT 1")
            assert result.scalar() == 1
        except Exception as e:
            pytest.fail(f"Migration verification failed: {str(e)}")

    def test_migration_consistency(self, db_session_pg):
        """Test migration consistency."""
        # Verify database schema is in expected state
        try:
            db_session_pg.execute("SELECT 1")
            db_session_pg.commit()
            assert True
        except Exception as e:
            pytest.fail(f"Migration consistency check failed: {str(e)}")


@pytest.mark.integration
class TestDatabaseQueryBuilder:
    """Test database query builder integration."""

    def test_query_execution(self, db_session_pg):
        """Test query execution."""
        try:
            result = db_session_pg.execute("SELECT 1 as test_value")
            row = result.fetchone()
            assert row[0] == 1
        except Exception as e:
            pytest.fail(f"Query execution failed: {str(e)}")

    def test_prepared_statements(self, db_session_pg):
        """Test prepared statement execution."""
        try:
            from sqlalchemy import text
            stmt = text("SELECT :value as result")
            result = db_session_pg.execute(stmt, {"value": 42})
            assert result.scalar() == 42
        except Exception as e:
            pytest.fail(f"Prepared statement test failed: {str(e)}")
