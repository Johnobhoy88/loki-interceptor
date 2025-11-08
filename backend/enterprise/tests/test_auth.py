"""
Unit tests for authentication system.
"""

import unittest
import jwt
from datetime import datetime, timedelta
from backend.enterprise.auth import (
    TokenManager,
    APIKeyManager,
    SessionManager,
    AuthManager,
    TokenType,
    User,
    APIKey,
)


class TestTokenManager(unittest.TestCase):
    """Test TokenManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.token_manager = TokenManager(secret_key="test-secret")

    def test_create_access_token(self):
        """Test access token creation."""
        token = self.token_manager.create_access_token(
            user_id="user-123",
            org_id="org-456",
        )

        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 0)

    def test_verify_access_token(self):
        """Test token verification."""
        token = self.token_manager.create_access_token(
            user_id="user-123",
            org_id="org-456",
        )

        payload = self.token_manager.verify_token(token, TokenType.ACCESS)

        self.assertEqual(payload['sub'], "user-123")
        self.assertEqual(payload['org_id'], "org-456")
        self.assertEqual(payload['type'], TokenType.ACCESS.value)

    def test_verify_expired_token(self):
        """Test expired token rejection."""
        # Create token manager with very short expiry
        short_manager = TokenManager(
            secret_key="test-secret",
            access_token_expire_minutes=-1,  # Already expired
        )

        token = short_manager.create_access_token(
            user_id="user-123",
            org_id="org-456",
        )

        with self.assertRaises(jwt.InvalidTokenError):
            short_manager.verify_token(token, TokenType.ACCESS)

    def test_create_refresh_token(self):
        """Test refresh token creation."""
        token = self.token_manager.create_refresh_token(
            user_id="user-123",
            org_id="org-456",
        )

        payload = self.token_manager.verify_token(token, TokenType.REFRESH)
        self.assertEqual(payload['type'], TokenType.REFRESH.value)

    def test_refresh_access_token(self):
        """Test token refresh."""
        refresh_token = self.token_manager.create_refresh_token(
            user_id="user-123",
            org_id="org-456",
        )

        new_access, new_refresh = self.token_manager.refresh_access_token(refresh_token)

        self.assertIsInstance(new_access, str)
        self.assertIsInstance(new_refresh, str)

        # Verify new tokens
        access_payload = self.token_manager.verify_token(new_access, TokenType.ACCESS)
        self.assertEqual(access_payload['sub'], "user-123")

    def test_invalid_token_type(self):
        """Test mismatched token type validation."""
        access_token = self.token_manager.create_access_token(
            user_id="user-123",
            org_id="org-456",
        )

        with self.assertRaises(ValueError):
            self.token_manager.verify_token(access_token, TokenType.REFRESH)


class TestAPIKeyManager(unittest.TestCase):
    """Test APIKeyManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = APIKeyManager()

    def test_generate_api_key(self):
        """Test API key generation."""
        plain_key, api_key = self.manager.generate_api_key(
            user_id="user-123",
            org_id="org-456",
            name="Test Key",
            scopes=["read", "write"],
        )

        self.assertIsInstance(plain_key, str)
        self.assertTrue(plain_key.startswith("loki_"))
        self.assertIsNotNone(api_key.id)

    def test_validate_api_key(self):
        """Test API key validation."""
        plain_key, api_key = self.manager.generate_api_key(
            user_id="user-123",
            org_id="org-456",
            name="Test Key",
            scopes=["read"],
        )

        validated = self.manager.validate_api_key(plain_key)

        self.assertIsNotNone(validated)
        self.assertEqual(validated.id, api_key.id)
        self.assertEqual(validated.user_id, "user-123")

    def test_validate_invalid_key(self):
        """Test invalid key rejection."""
        result = self.manager.validate_api_key("invalid-key")
        self.assertIsNone(result)

    def test_revoke_api_key(self):
        """Test API key revocation."""
        plain_key, api_key = self.manager.generate_api_key(
            user_id="user-123",
            org_id="org-456",
            name="Test Key",
            scopes=["read"],
        )

        # Revoke key
        success = self.manager.revoke_api_key(api_key.id)
        self.assertTrue(success)

        # Should no longer validate
        validated = self.manager.validate_api_key(plain_key)
        self.assertIsNone(validated)

    def test_rotate_api_key(self):
        """Test API key rotation."""
        old_plain_key, old_api_key = self.manager.generate_api_key(
            user_id="user-123",
            org_id="org-456",
            name="Test Key",
            scopes=["read"],
        )

        new_plain_key, new_api_key = self.manager.rotate_api_key(old_api_key.id)

        # New key should validate
        validated = self.manager.validate_api_key(new_plain_key)
        self.assertIsNotNone(validated)

        # Old key should not validate
        old_validated = self.manager.validate_api_key(old_plain_key)
        self.assertIsNone(old_validated)


class TestSessionManager(unittest.TestCase):
    """Test SessionManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = SessionManager()

    def test_create_session(self):
        """Test session creation."""
        session = self.manager.create_session(
            user_id="user-123",
            org_id="org-456",
            ip_address="192.168.1.1",
        )

        self.assertIsNotNone(session.id)
        self.assertIsNotNone(session.token)
        self.assertEqual(session.user_id, "user-123")

    def test_validate_session(self):
        """Test session validation."""
        session = self.manager.create_session(
            user_id="user-123",
            org_id="org-456",
        )

        validated = self.manager.validate_session(session.token)

        self.assertIsNotNone(validated)
        self.assertEqual(validated.id, session.id)

    def test_validate_invalid_session(self):
        """Test invalid session rejection."""
        result = self.manager.validate_session("invalid-token")
        self.assertIsNone(result)

    def test_refresh_session(self):
        """Test session refresh."""
        session = self.manager.create_session(
            user_id="user-123",
            org_id="org-456",
        )

        original_expiry = session.expires_at

        # Refresh session
        refreshed = self.manager.refresh_session(session.token)

        self.assertIsNotNone(refreshed)
        self.assertGreater(refreshed.expires_at, original_expiry)

    def test_revoke_session(self):
        """Test session revocation."""
        session = self.manager.create_session(
            user_id="user-123",
            org_id="org-456",
        )

        success = self.manager.revoke_session(session.token)
        self.assertTrue(success)

        # Should no longer validate
        validated = self.manager.validate_session(session.token)
        self.assertIsNone(validated)


class TestUser(unittest.TestCase):
    """Test User entity."""

    def test_user_creation(self):
        """Test user creation."""
        user = User(
            id="user-123",
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
        )

        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_verified)

    def test_user_to_dict(self):
        """Test user serialization."""
        user = User(
            id="user-123",
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
        )

        user_dict = user.to_dict()

        self.assertIn('email', user_dict)
        self.assertNotIn('password_hash', user_dict)


if __name__ == '__main__':
    unittest.main()
