"""
Unit tests for security hardening.
"""

import unittest
import time
from backend.enterprise.security import (
    RequestSigner,
    CSRFProtection,
    RateLimiter,
    RateLimitConfig,
    RateLimitStrategy,
    InputValidator,
    IPFilter,
    SecurityManager,
    SecurityHeaders,
)


class TestRequestSigner(unittest.TestCase):
    """Test RequestSigner."""

    def setUp(self):
        """Set up test fixtures."""
        self.signer = RequestSigner(secret_key="test-secret-key")

    def test_sign_request(self):
        """Test signing request."""
        signature = self.signer.sign_request(
            method="POST",
            path="/api/users",
            body='{"name":"test"}',
            timestamp=1234567890,
        )

        self.assertIsInstance(signature, str)
        self.assertEqual(len(signature), 64)  # SHA-256 hex

    def test_verify_request(self):
        """Test verifying signed request."""
        timestamp = int(time.time())

        signature = self.signer.sign_request(
            method="POST",
            path="/api/users",
            body='{"name":"test"}',
            timestamp=timestamp,
        )

        is_valid = self.signer.verify_request(
            signature=signature,
            method="POST",
            path="/api/users",
            body='{"name":"test"}',
            timestamp=timestamp,
        )

        self.assertTrue(is_valid)

    def test_verify_invalid_signature(self):
        """Test rejecting invalid signature."""
        timestamp = int(time.time())

        is_valid = self.signer.verify_request(
            signature="invalid-signature",
            method="POST",
            path="/api/users",
            timestamp=timestamp,
        )

        self.assertFalse(is_valid)

    def test_verify_expired_request(self):
        """Test rejecting expired request."""
        old_timestamp = int(time.time()) - 400  # More than 300s ago

        signature = self.signer.sign_request(
            method="GET",
            path="/api/data",
            timestamp=old_timestamp,
        )

        is_valid = self.signer.verify_request(
            signature=signature,
            method="GET",
            path="/api/data",
            timestamp=old_timestamp,
            max_age_seconds=300,
        )

        self.assertFalse(is_valid)

    def test_generate_signed_url(self):
        """Test generating signed URL."""
        url = self.signer.generate_signed_url(
            path="/api/download",
            expires_in_seconds=3600,
            params={'file': 'document.pdf'},
        )

        self.assertIn('expires=', url)
        self.assertIn('signature=', url)
        self.assertIn('file=document.pdf', url)


class TestCSRFProtection(unittest.TestCase):
    """Test CSRFProtection."""

    def setUp(self):
        """Set up test fixtures."""
        self.csrf = CSRFProtection()

    def test_generate_token(self):
        """Test generating CSRF token."""
        token = self.csrf.generate_token(session_id="session-123")

        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 20)

    def test_validate_token(self):
        """Test validating CSRF token."""
        session_id = "session-123"
        token = self.csrf.generate_token(session_id)

        is_valid = self.csrf.validate_token(
            session_id=session_id,
            token=token,
            consume=False,
        )

        self.assertTrue(is_valid)

    def test_validate_invalid_token(self):
        """Test rejecting invalid CSRF token."""
        is_valid = self.csrf.validate_token(
            session_id="session-123",
            token="invalid-token",
        )

        self.assertFalse(is_valid)

    def test_token_consumption(self):
        """Test token is consumed after validation."""
        session_id = "session-123"
        token = self.csrf.generate_token(session_id)

        # First validation should succeed and consume
        is_valid = self.csrf.validate_token(session_id, token, consume=True)
        self.assertTrue(is_valid)

        # Second validation should fail (token consumed)
        is_valid = self.csrf.validate_token(session_id, token, consume=False)
        self.assertFalse(is_valid)


class TestRateLimiter(unittest.TestCase):
    """Test RateLimiter."""

    def setUp(self):
        """Set up test fixtures."""
        self.limiter = RateLimiter()

    def test_sliding_window_allow(self):
        """Test sliding window allows requests within limit."""
        config = RateLimitConfig(
            requests=5,
            window_seconds=60,
            strategy=RateLimitStrategy.SLIDING_WINDOW,
        )

        result = self.limiter.check_rate_limit("user-123", config)

        self.assertTrue(result['allowed'])
        self.assertEqual(result['remaining'], 4)

    def test_sliding_window_block(self):
        """Test sliding window blocks requests over limit."""
        config = RateLimitConfig(
            requests=2,
            window_seconds=60,
            strategy=RateLimitStrategy.SLIDING_WINDOW,
        )

        # Use up limit
        self.limiter.check_rate_limit("user-123", config)
        self.limiter.check_rate_limit("user-123", config)

        # Third request should be blocked
        result = self.limiter.check_rate_limit("user-123", config)

        self.assertFalse(result['allowed'])
        self.assertEqual(result['remaining'], 0)
        self.assertGreater(result['retry_after'], 0)

    def test_fixed_window(self):
        """Test fixed window rate limiting."""
        config = RateLimitConfig(
            requests=3,
            window_seconds=60,
            strategy=RateLimitStrategy.FIXED_WINDOW,
        )

        result = self.limiter.check_rate_limit("user-456", config)

        self.assertTrue(result['allowed'])

    def test_token_bucket(self):
        """Test token bucket rate limiting."""
        config = RateLimitConfig(
            requests=5,
            window_seconds=60,
            strategy=RateLimitStrategy.TOKEN_BUCKET,
            burst_size=10,
        )

        result = self.limiter.check_rate_limit("user-789", config)

        self.assertTrue(result['allowed'])

    def test_different_users_isolated(self):
        """Test that different users have separate rate limits."""
        config = RateLimitConfig(
            requests=1,
            window_seconds=60,
            strategy=RateLimitStrategy.SLIDING_WINDOW,
        )

        # User 1 uses their limit
        result1 = self.limiter.check_rate_limit("user-1", config)
        self.assertTrue(result1['allowed'])

        # User 2 should still be allowed
        result2 = self.limiter.check_rate_limit("user-2", config)
        self.assertTrue(result2['allowed'])


class TestInputValidator(unittest.TestCase):
    """Test InputValidator."""

    def test_validate_email_valid(self):
        """Test validating valid email."""
        self.assertTrue(InputValidator.validate_email("test@example.com"))
        self.assertTrue(InputValidator.validate_email("user+tag@domain.co.uk"))

    def test_validate_email_invalid(self):
        """Test rejecting invalid email."""
        self.assertFalse(InputValidator.validate_email("invalid"))
        self.assertFalse(InputValidator.validate_email("@example.com"))
        self.assertFalse(InputValidator.validate_email("test@"))

    def test_validate_uuid_valid(self):
        """Test validating valid UUID."""
        self.assertTrue(InputValidator.validate_uuid("550e8400-e29b-41d4-a716-446655440000"))
        self.assertTrue(InputValidator.validate_uuid("550E8400-E29B-41D4-A716-446655440000"))

    def test_validate_uuid_invalid(self):
        """Test rejecting invalid UUID."""
        self.assertFalse(InputValidator.validate_uuid("invalid-uuid"))
        self.assertFalse(InputValidator.validate_uuid("123"))

    def test_validate_slug_valid(self):
        """Test validating valid slug."""
        self.assertTrue(InputValidator.validate_slug("my-slug"))
        self.assertTrue(InputValidator.validate_slug("slug123"))

    def test_validate_slug_invalid(self):
        """Test rejecting invalid slug."""
        self.assertFalse(InputValidator.validate_slug("My Slug"))
        self.assertFalse(InputValidator.validate_slug("slug_with_underscore"))

    def test_sanitize_string(self):
        """Test string sanitization."""
        result = InputValidator.sanitize_string(
            "Hello <script>alert('xss')</script>",
            max_length=100,
        )

        self.assertNotIn("<script>", result)
        self.assertNotIn("</script>", result)

    def test_sanitize_sql_injection(self):
        """Test SQL injection prevention."""
        result = InputValidator.sanitize_string(
            "test'; DROP TABLE users;--",
            max_length=100,
        )

        self.assertNotIn("';", result)
        self.assertNotIn("--", result)

    def test_validate_json_valid(self):
        """Test JSON validation."""
        schema = {
            'type': 'object',
            'required': ['name', 'email'],
        }

        data = {'name': 'Test', 'email': 'test@example.com'}

        is_valid, error = InputValidator.validate_json(data, schema)

        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_json_missing_field(self):
        """Test JSON validation with missing required field."""
        schema = {
            'type': 'object',
            'required': ['name', 'email'],
        }

        data = {'name': 'Test'}

        is_valid, error = InputValidator.validate_json(data, schema)

        self.assertFalse(is_valid)
        self.assertIn('email', error)


class TestIPFilter(unittest.TestCase):
    """Test IPFilter."""

    def setUp(self):
        """Set up test fixtures."""
        self.filter = IPFilter()

    def test_allow_all_by_default(self):
        """Test that all IPs are allowed by default."""
        self.assertTrue(self.filter.is_allowed("192.168.1.1"))
        self.assertTrue(self.filter.is_allowed("10.0.0.1"))

    def test_whitelist(self):
        """Test IP whitelisting."""
        self.filter.add_to_whitelist("192.168.1.1")

        self.assertTrue(self.filter.is_allowed("192.168.1.1"))
        self.assertFalse(self.filter.is_allowed("192.168.1.2"))

    def test_blacklist(self):
        """Test IP blacklisting."""
        self.filter.add_to_blacklist("192.168.1.100")

        self.assertFalse(self.filter.is_allowed("192.168.1.100"))
        self.assertTrue(self.filter.is_allowed("192.168.1.1"))

    def test_blacklist_overrides_whitelist(self):
        """Test that blacklist takes precedence over whitelist."""
        self.filter.add_to_whitelist("192.168.1.1")
        self.filter.add_to_blacklist("192.168.1.1")

        self.assertFalse(self.filter.is_allowed("192.168.1.1"))


class TestSecurityHeaders(unittest.TestCase):
    """Test SecurityHeaders."""

    def test_default_headers(self):
        """Test default security headers."""
        headers = SecurityHeaders()
        header_dict = headers.to_dict()

        self.assertIn('X-Content-Type-Options', header_dict)
        self.assertIn('X-Frame-Options', header_dict)
        self.assertIn('Strict-Transport-Security', header_dict)
        self.assertEqual(header_dict['X-Frame-Options'], 'DENY')

    def test_custom_headers(self):
        """Test custom security headers."""
        headers = SecurityHeaders(
            x_frame_options="SAMEORIGIN",
            content_security_policy="default-src 'self' https:",
        )

        header_dict = headers.to_dict()

        self.assertEqual(header_dict['X-Frame-Options'], 'SAMEORIGIN')
        self.assertIn("https:", header_dict['Content-Security-Policy'])


class TestSecurityManager(unittest.TestCase):
    """Test SecurityManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = SecurityManager(secret_key="test-secret")

    def test_initialization(self):
        """Test security manager initialization."""
        self.assertIsNotNone(self.manager.request_signer)
        self.assertIsNotNone(self.manager.csrf_protection)
        self.assertIsNotNone(self.manager.rate_limiter)

    def test_get_security_headers(self):
        """Test getting security headers."""
        headers = self.manager.get_security_headers()

        self.assertIsInstance(headers, dict)
        self.assertIn('X-Content-Type-Options', headers)

    def test_create_rate_limit_config(self):
        """Test creating rate limit config based on tier."""
        free_config = self.manager.create_rate_limit_config(tier="free")
        enterprise_config = self.manager.create_rate_limit_config(tier="enterprise")

        self.assertEqual(free_config.requests, 100)
        self.assertEqual(enterprise_config.requests, 100000)
        self.assertGreater(enterprise_config.requests, free_config.requests)


if __name__ == '__main__':
    unittest.main()
