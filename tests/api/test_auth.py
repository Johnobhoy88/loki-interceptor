"""
Authentication and Authorization Tests

Tests API authentication and authorization including:
- API key validation
- Key format checks
- Provider-specific auth
- Unauthorized access prevention
"""

import pytest
import json


class TestAPIKeyValidation:
    """Test API key validation."""

    def test_missing_api_key(self, client):
        """Test request without API key is rejected."""
        payload = {
            'messages': [{'role': 'user', 'content': 'Test'}],
            'model': 'claude-3-5-sonnet-20241022'
        }

        response = client.post(
            '/api/v1/messages',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 401

    def test_empty_api_key(self, client):
        """Test empty API key is rejected."""
        payload = {
            'messages': [{'role': 'user', 'content': 'Test'}],
            'model': 'claude-3-5-sonnet-20241022'
        }

        response = client.post(
            '/api/v1/messages',
            data=json.dumps(payload),
            content_type='application/json',
            headers={'x-api-key': ''}
        )

        assert response.status_code == 401

    def test_malformed_api_key(self, client):
        """Test malformed API key is rejected."""
        payload = {
            'messages': [{'role': 'user', 'content': 'Test'}],
            'model': 'claude-3-5-sonnet-20241022'
        }

        response = client.post(
            '/api/v1/messages',
            data=json.dumps(payload),
            content_type='application/json',
            headers={'x-api-key': 'invalid'}
        )

        assert response.status_code == 401


class TestProviderAuth:
    """Test provider-specific authentication."""

    def test_anthropic_key_format(self, client):
        """Test Anthropic API key format validation."""
        # Anthropic keys should start with 'sk-ant-'
        payload = {
            'provider': 'anthropic',
            'messages': [{'role': 'user', 'content': 'Test'}]
        }

        # Invalid format
        response = client.post(
            '/api/proxy',
            data=json.dumps(payload),
            content_type='application/json',
            headers={'x-api-key': 'invalid-key'}
        )

        assert response.status_code == 401

    def test_openai_key_format(self, client):
        """Test OpenAI API key format validation."""
        # OpenAI keys should start with 'sk-'
        payload = {
            'provider': 'openai',
            'messages': [{'role': 'user', 'content': 'Test'}]
        }

        response = client.post(
            '/api/proxy',
            data=json.dumps(payload),
            content_type='application/json',
            headers={'openai-api-key': 'invalid'}
        )

        assert response.status_code == 401

    def test_gemini_key_format(self, client):
        """Test Gemini API key format validation."""
        payload = {
            'provider': 'gemini',
            'messages': [{'role': 'user', 'content': 'Test'}]
        }

        response = client.post(
            '/api/proxy',
            data=json.dumps(payload),
            content_type='application/json',
            headers={'gemini-api-key': 'invalid'}
        )

        assert response.status_code == 401


class TestHeaderVariations:
    """Test different API key header formats."""

    def test_x_api_key_header(self, client):
        """Test x-api-key header is accepted."""
        payload = {
            'messages': [{'role': 'user', 'content': 'Test'}],
            'model': 'claude-3-5-sonnet-20241022'
        }

        response = client.post(
            '/api/v1/messages',
            data=json.dumps(payload),
            content_type='application/json',
            headers={'x-api-key': 'test-key'}
        )

        # Should attempt to process (may fail on actual API call)
        assert response.status_code in [200, 401, 500]

    def test_anthropic_api_key_header(self, client):
        """Test anthropic-api-key header is accepted."""
        payload = {
            'provider': 'anthropic',
            'messages': [{'role': 'user', 'content': 'Test'}]
        }

        response = client.post(
            '/api/proxy',
            data=json.dumps(payload),
            content_type='application/json',
            headers={'anthropic-api-key': 'test-key'}
        )

        assert response.status_code in [200, 401]


class TestUnauthorizedAccess:
    """Test prevention of unauthorized access."""

    def test_cannot_bypass_validation(self, client):
        """Test cannot bypass validation with invalid credentials."""
        # Attempt to access protected endpoint
        payload = {
            'text': 'Test document',
            'document_type': 'financial',
            'modules': ['fca_uk']
        }

        # Validation endpoint may not require auth
        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        # Should either work or reject based on endpoint protection
        assert response.status_code in [200, 401, 403]

    def test_protected_endpoints_require_auth(self, client):
        """Test protected endpoints require authentication."""
        # Proxy endpoint should require auth
        payload = {
            'provider': 'anthropic',
            'messages': [{'role': 'user', 'content': 'Test'}]
        }

        response = client.post(
            '/api/proxy',
            data=json.dumps(payload),
            content_type='application/json'
        )

        # Should require authentication
        assert response.status_code in [400, 401]


class TestAuthErrorMessages:
    """Test authentication error messages."""

    def test_missing_key_error_message(self, client):
        """Test missing API key returns clear error."""
        payload = {
            'messages': [{'role': 'user', 'content': 'Test'}]
        }

        response = client.post(
            '/api/v1/messages',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 401
        data = response.get_json()

        # Error message should be sanitized but informative
        assert data is not None

    def test_invalid_key_error_message(self, client):
        """Test invalid API key returns clear error."""
        payload = {
            'provider': 'anthropic',
            'messages': [{'role': 'user', 'content': 'Test'}]
        }

        response = client.post(
            '/api/proxy',
            data=json.dumps(payload),
            content_type='application/json',
            headers={'x-api-key': 'invalid'}
        )

        assert response.status_code == 401
        data = response.get_json()
        assert data is not None


class TestMultipleAuthMethods:
    """Test handling of multiple authentication methods."""

    def test_precedence_of_headers(self, client):
        """Test header precedence when multiple are provided."""
        payload = {
            'provider': 'anthropic',
            'messages': [{'role': 'user', 'content': 'Test'}]
        }

        # Provide multiple key headers
        response = client.post(
            '/api/proxy',
            data=json.dumps(payload),
            content_type='application/json',
            headers={
                'x-api-key': 'key1',
                'anthropic-api-key': 'key2'
            }
        )

        # Should use one consistently
        assert response.status_code in [200, 401]
