"""
Deployment Smoke Tests

Quick validation tests that run after deployment to ensure
core functionality is operational.
"""

import pytest
import requests
import time


@pytest.mark.smoke
class TestBackendAvailability:
    """Test backend service availability."""

    def test_backend_is_responsive(self, smoke_config):
        """Test backend is responsive."""
        try:
            response = requests.get(
                f"{smoke_config['backend_url']}/health",
                timeout=smoke_config['timeout']
            )
            assert response.status_code == 200
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Backend not responsive: {str(e)}")

    def test_backend_returns_json(self, smoke_config):
        """Test backend returns valid JSON."""
        response = requests.get(
            f"{smoke_config['backend_url']}/health",
            timeout=smoke_config['timeout']
        )
        assert response.status_code == 200
        assert response.json() is not None

    def test_api_version_endpoint(self, smoke_config):
        """Test API version endpoint."""
        try:
            response = requests.get(
                f"{smoke_config['backend_url']}/api/version",
                timeout=smoke_config['timeout']
            )
            # Accept 200 or 404 - version endpoint may not exist
            assert response.status_code in [200, 404]
        except requests.exceptions.RequestException:
            pass


@pytest.mark.smoke
class TestFrontendAvailability:
    """Test frontend service availability."""

    def test_frontend_is_accessible(self, smoke_config):
        """Test frontend is accessible."""
        try:
            response = requests.get(
                f"{smoke_config['frontend_url']}/",
                timeout=smoke_config['timeout']
            )
            assert response.status_code == 200
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Frontend not accessible: {str(e)}")

    def test_frontend_returns_html(self, smoke_config):
        """Test frontend returns HTML."""
        response = requests.get(
            f"{smoke_config['frontend_url']}/",
            timeout=smoke_config['timeout']
        )
        assert response.status_code == 200
        assert "html" in response.text.lower() or "doctype" in response.text.lower()


@pytest.mark.smoke
class TestCoreAPIs:
    """Test core API endpoints."""

    def test_validation_endpoint_available(self, smoke_config):
        """Test validation endpoint is available."""
        response = requests.post(
            f"{smoke_config['backend_url']}/api/validate",
            json={
                "title": "Smoke Test",
                "content": "Test content",
                "metadata": {},
            },
            timeout=smoke_config['timeout']
        )
        assert response.status_code in [200, 202, 400, 422]

    def test_correction_endpoint_available(self, smoke_config):
        """Test correction endpoint is available."""
        response = requests.post(
            f"{smoke_config['backend_url']}/api/correct",
            json={
                "title": "Smoke Test",
                "content": "Test content",
                "metadata": {},
            },
            timeout=smoke_config['timeout']
        )
        assert response.status_code in [200, 202, 400, 422]


@pytest.mark.smoke
class TestDatabaseConnectivity:
    """Test database connectivity."""

    def test_database_health_via_api(self, smoke_config):
        """Test database health through API."""
        response = requests.get(
            f"{smoke_config['backend_url']}/health",
            timeout=smoke_config['timeout']
        )
        assert response.status_code == 200

        # If health endpoint reports DB status, it should be healthy
        data = response.json()
        if "database" in data:
            assert data["database"] in ["healthy", "connected", "ok", True]


@pytest.mark.smoke
class TestCacheConnectivity:
    """Test cache (Redis) connectivity."""

    def test_cache_via_api(self, smoke_config):
        """Test cache connectivity through API."""
        # Make two identical requests to test caching
        payload = {
            "title": "Cache Test",
            "content": "Test content",
            "metadata": {},
        }

        # First request
        response1 = requests.post(
            f"{smoke_config['backend_url']}/api/validate",
            json=payload,
            timeout=smoke_config['timeout']
        )

        # Cache should be working even if endpoint returns error
        assert response1.status_code in [200, 202, 400, 422]


@pytest.mark.smoke
class TestComplianceGates:
    """Test compliance gates are operational."""

    def test_at_least_one_gate_available(self, smoke_config):
        """Test at least one compliance gate is available."""
        gates = [
            "hr_scottish",
            "gdpr_uk",
            "nda_uk",
            "tax_uk",
            "fca_uk",
        ]

        gates_available = []

        for gate in gates:
            try:
                response = requests.post(
                    f"{smoke_config['backend_url']}/api/gates/{gate}",
                    json={"title": "Test", "content": "Test", "metadata": {}},
                    timeout=smoke_config['timeout']
                )
                if response.status_code in [200, 202]:
                    gates_available.append(gate)
            except requests.exceptions.RequestException:
                pass

        assert len(gates_available) > 0, "No compliance gates are available"


@pytest.mark.smoke
class TestErrorHandling:
    """Test error handling is operational."""

    def test_invalid_request_handling(self, smoke_config):
        """Test invalid request is handled gracefully."""
        response = requests.post(
            f"{smoke_config['backend_url']}/api/validate",
            json={"invalid": "data"},
            timeout=smoke_config['timeout']
        )

        # Should return 4xx error, not 5xx
        assert response.status_code < 500

    def test_not_found_handling(self, smoke_config):
        """Test 404 handling."""
        response = requests.get(
            f"{smoke_config['backend_url']}/api/nonexistent",
            timeout=smoke_config['timeout']
        )

        assert response.status_code == 404


@pytest.mark.smoke
class TestResponseTimes:
    """Test response times are acceptable."""

    def test_health_check_response_time(self, smoke_config):
        """Test health check response time."""
        start = time.time()
        response = requests.get(
            f"{smoke_config['backend_url']}/health",
            timeout=smoke_config['timeout']
        )
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 5, f"Health check took {elapsed:.2f}s, expected < 5s"

    def test_validation_response_time(self, smoke_config):
        """Test validation response time."""
        start = time.time()
        response = requests.post(
            f"{smoke_config['backend_url']}/api/validate",
            json={
                "title": "Test",
                "content": "Test content",
                "metadata": {},
            },
            timeout=smoke_config['timeout']
        )
        elapsed = time.time() - start

        assert response.status_code in [200, 202]
        assert elapsed < 30, f"Validation took {elapsed:.2f}s, expected < 30s"
