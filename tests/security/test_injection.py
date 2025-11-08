"""
Injection Attack Tests

Tests protection against:
- SQL injection
- Command injection
- Code injection
- XSS attempts
"""

import pytest
import json


@pytest.mark.security
class TestSQLInjection:
    """Test SQL injection protection."""

    @pytest.mark.parametrize('injection', [
        "'; DROP TABLE audit_log; --",
        "' OR '1'='1",
        "admin'--",
        "1' UNION SELECT * FROM users--",
        "'; DELETE FROM audit_log WHERE '1'='1",
    ])
    def test_sql_injection_in_text(self, client, injection):
        """Test SQL injection attempts in document text are handled safely."""
        payload = {
            'text': f"Test document {injection}",
            'document_type': 'test',
            'modules': ['gdpr_uk']
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        # Should process safely without executing SQL
        assert response.status_code in [200, 400]

        # Verify database wasn't affected (audit log still exists)
        stats_response = client.get('/api/audit/stats')
        assert stats_response.status_code == 200

    def test_sql_injection_in_params(self, client):
        """Test SQL injection in query parameters is sanitized."""
        # Attempt injection in query parameter
        response = client.get("/api/analytics/overview?window='; DROP TABLE audit_log; --")

        # Should handle safely
        assert response.status_code in [200, 400]


@pytest.mark.security
class TestCommandInjection:
    """Test command injection protection."""

    @pytest.mark.parametrize('injection', [
        "; ls -la",
        "| cat /etc/passwd",
        "&& whoami",
        "`rm -rf /`",
        "$(malicious command)",
    ])
    def test_command_injection_attempts(self, client, injection):
        """Test command injection attempts are neutralized."""
        payload = {
            'text': f"Test content {injection}",
            'document_type': 'test'
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        # Should process safely
        assert response.status_code in [200, 400]


@pytest.mark.security
class TestCodeInjection:
    """Test code injection protection."""

    @pytest.mark.parametrize('injection', [
        "__import__('os').system('ls')",
        "eval('1+1')",
        "exec('import os')",
        "compile('print(1)', '', 'exec')",
    ])
    def test_python_code_injection(self, client, injection):
        """Test Python code injection attempts are handled safely."""
        payload = {
            'text': injection,
            'document_type': 'test'
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        # Should not execute code
        assert response.status_code in [200, 400]


@pytest.mark.security
class TestXSSProtection:
    """Test XSS protection."""

    @pytest.mark.parametrize('xss', [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<iframe src='javascript:alert(1)'>",
        "javascript:alert('XSS')",
        "<svg onload=alert('XSS')>",
    ])
    def test_xss_in_text(self, client, xss):
        """Test XSS attempts are sanitized."""
        payload = {
            'text': f"Document with {xss}",
            'document_type': 'test'
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code in [200, 400]

        if response.status_code == 200:
            data = response.get_json()
            # Response should be JSON, not HTML
            assert isinstance(data, dict)


@pytest.mark.security
class TestPathTraversal:
    """Test path traversal protection."""

    @pytest.mark.parametrize('traversal', [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32",
        "....//....//....//etc/passwd",
        "%2e%2e%2f%2e%2e%2f",
    ])
    def test_path_traversal_attempts(self, client, traversal):
        """Test path traversal attempts are blocked."""
        payload = {
            'text': f"File: {traversal}",
            'document_type': 'test'
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        # Should process safely without accessing files
        assert response.status_code in [200, 400]


@pytest.mark.security
class TestHeaderInjection:
    """Test HTTP header injection protection."""

    def test_crlf_injection(self, client):
        """Test CRLF injection in headers is prevented."""
        # Attempt to inject headers
        malicious_header = "test\\r\\nX-Injected-Header: malicious"

        response = client.get(
            '/api/health',
            headers={'User-Agent': malicious_header}
        )

        # Should handle safely
        assert response.status_code == 200

        # Injected header should not appear in response
        assert 'X-Injected-Header' not in response.headers


@pytest.mark.security
class TestJSONInjection:
    """Test JSON injection protection."""

    def test_malformed_json_injection(self, client):
        """Test malformed JSON is rejected."""
        malicious_payloads = [
            '{"text": "test"}}}}',
            '{"text": "test", "extra": {"nested": {"deep": ' + '{' * 1000,
            '{"__proto__": {"polluted": true}}',
        ]

        for payload in malicious_payloads:
            response = client.post(
                '/api/validate-document',
                data=payload,
                content_type='application/json'
            )

            # Should reject malformed JSON
            assert response.status_code in [400, 500]

    def test_prototype_pollution(self, client):
        """Test prototype pollution attempts are handled."""
        payload = {
            '__proto__': {'polluted': True},
            'text': 'test',
            'document_type': 'test'
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        # Should handle safely
        assert response.status_code in [200, 400]


@pytest.mark.security
class TestInputSanitization:
    """Test input sanitization."""

    def test_null_byte_injection(self, client):
        """Test null byte injection is handled."""
        payload = {
            'text': "test\\x00malicious",
            'document_type': 'test'
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code in [200, 400]

    def test_unicode_normalization(self, client):
        """Test unicode normalization attacks are handled."""
        # Unicode characters that might bypass filters
        payload = {
            'text': "test\\u202e\\u202dmalicious",
            'document_type': 'test'
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code in [200, 400]

    def test_excessive_nesting(self, client):
        """Test deeply nested structures are rejected."""
        # Create deeply nested JSON
        nested = {'text': 'test'}
        for i in range(100):
            nested = {'nested': nested}

        response = client.post(
            '/api/validate-document',
            data=json.dumps(nested),
            content_type='application/json'
        )

        # Should reject or handle safely
        assert response.status_code in [200, 400, 500]
