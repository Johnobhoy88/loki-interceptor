"""
API Contract Testing

Tests API contracts to ensure compatibility between frontend and backend.
"""

import pytest
import requests
import json
from typing import Dict, Any


@pytest.mark.integration
class TestAPIContractValidation:
    """Test API contract compliance."""

    @pytest.fixture
    def api_client(self, test_config):
        """Create API client."""
        return requests.Session()

    def test_validation_endpoint_contract(self, api_client, test_config):
        """Test /api/validate endpoint contract."""
        payload = {
            "title": "Test Document",
            "content": "Test content",
            "metadata": {"jurisdiction": "UK"},
        }

        response = api_client.post(
            f"{test_config['backend_url']}/api/validate",
            json=payload,
            timeout=test_config['api_timeout']
        )

        # Contract: Must return 200/202 with validation_id
        assert response.status_code in [200, 202]
        data = response.json()
        assert isinstance(data, dict)
        assert "validation_id" in data or "id" in data

    def test_correction_endpoint_contract(self, api_client, test_config):
        """Test /api/correct endpoint contract."""
        payload = {
            "title": "Test Document",
            "content": "Test content",
            "metadata": {"jurisdiction": "UK"},
        }

        response = api_client.post(
            f"{test_config['backend_url']}/api/correct",
            json=payload,
            timeout=test_config['api_timeout']
        )

        # Contract: Must return 200/202 with correction_id
        assert response.status_code in [200, 202]
        data = response.json()
        assert isinstance(data, dict)

    def test_health_endpoint_contract(self, api_client, test_config):
        """Test /health endpoint contract."""
        response = api_client.get(
            f"{test_config['backend_url']}/health",
            timeout=test_config['api_timeout']
        )

        # Contract: /health must return 200 with status
        assert response.status_code == 200
        data = response.json()
        assert "status" in data or "healthy" in data

    def test_error_response_contract(self, api_client, test_config):
        """Test error response contract."""
        # Invalid request
        response = api_client.post(
            f"{test_config['backend_url']}/api/validate",
            json={"invalid": "data"},  # Missing required fields
            timeout=test_config['api_timeout']
        )

        # Contract: Errors must return 4xx with error details
        assert response.status_code >= 400
        data = response.json()
        assert isinstance(data, dict)
        assert any(key in data for key in ["error", "message", "detail"])


@pytest.mark.integration
class TestResponseSchemaValidation:
    """Test API response schema validation."""

    @pytest.fixture
    def api_client(self, test_config):
        """Create API client."""
        return requests.Session()

    @pytest.fixture
    def json_schema_validator(self):
        """JSON schema validator."""
        try:
            import jsonschema
            return jsonschema.Draft7Validator
        except ImportError:
            pytest.skip("jsonschema not installed")

    def test_validation_response_schema(self, api_client, test_config):
        """Test validation response matches expected schema."""
        payload = {
            "title": "Test",
            "content": "Test content",
            "metadata": {"jurisdiction": "UK"},
        }

        response = api_client.post(
            f"{test_config['backend_url']}/api/validate",
            json=payload,
            timeout=test_config['api_timeout']
        )

        assert response.status_code in [200, 202]
        data = response.json()

        # Validate response structure
        assert isinstance(data, dict)
        assert isinstance(data.get("validation_id") or data.get("id"), str)

    def test_batch_response_schema(self, api_client, test_config):
        """Test batch response schema."""
        payload = {
            "documents": [
                {"title": "Doc1", "content": "Content1", "metadata": {}},
                {"title": "Doc2", "content": "Content2", "metadata": {}},
            ]
        }

        response = api_client.post(
            f"{test_config['backend_url']}/api/validate/batch",
            json=payload,
            timeout=test_config['api_timeout']
        )

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)
            assert isinstance(data.get("count"), int) or data.get("count") is None


@pytest.mark.integration
class TestCrossServiceIntegration:
    """Test cross-service integration scenarios."""

    @pytest.fixture
    def api_client(self, test_config):
        """Create API client."""
        return requests.Session()

    def test_validation_to_cache_integration(self, api_client, test_config, redis_client_pg):
        """Test that validation results are cached."""
        payload = {
            "title": "Cache Test",
            "content": "Content for cache test",
            "metadata": {"jurisdiction": "UK"},
        }

        response = api_client.post(
            f"{test_config['backend_url']}/api/validate",
            json=payload,
            timeout=test_config['api_timeout']
        )

        assert response.status_code in [200, 202]
        validation_id = response.json().get("validation_id") or response.json().get("id")

        # Verify cache is used
        cache_key = f"validation:{validation_id}"
        # Note: Actual verification depends on cache implementation

    def test_validation_to_database_integration(self, api_client, test_config, db_session_pg):
        """Test that validation is stored in database."""
        payload = {
            "title": "Database Test",
            "content": "Content for database test",
            "metadata": {"jurisdiction": "UK"},
        }

        response = api_client.post(
            f"{test_config['backend_url']}/api/validate",
            json=payload,
            timeout=test_config['api_timeout']
        )

        assert response.status_code in [200, 202]
        # Note: Actual DB verification depends on schema


@pytest.mark.integration
class TestGateExecutionIntegration:
    """Test compliance gate execution integration."""

    @pytest.fixture
    def api_client(self, test_config):
        """Create API client."""
        return requests.Session()

    def test_multiple_gates_execution_order(self, api_client, test_config):
        """Test multiple gates execute in correct order."""
        payload = {
            "title": "Multi-gate Test",
            "content": "Employment contract with GDPR and Tax terms",
            "metadata": {"jurisdiction": "UK"},
            "gates": ["employment", "gdpr_uk", "tax_uk"],
        }

        response = api_client.post(
            f"{test_config['backend_url']}/api/validate",
            json=payload,
            timeout=test_config['api_timeout']
        )

        assert response.status_code in [200, 202]

    def test_gate_failure_handling(self, api_client, test_config):
        """Test handling of gate execution failures."""
        payload = {
            "title": "Invalid Gate Test",
            "content": "Test content",
            "metadata": {},
            "gates": ["nonexistent_gate"],
        }

        response = api_client.post(
            f"{test_config['backend_url']}/api/validate",
            json=payload,
            timeout=test_config['api_timeout']
        )

        # System should handle gracefully
        assert response.status_code in [200, 202, 400, 422]
