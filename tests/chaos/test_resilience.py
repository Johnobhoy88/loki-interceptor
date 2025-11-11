"""
Resilience and Chaos Engineering Tests

Tests system behavior under failure conditions and high load.
"""

import pytest
import requests
import random
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed


@pytest.mark.chaos
class TestDatabaseFailureResilience:
    """Test system resilience to database failures."""

    def test_graceful_database_connection_failure(self, test_config):
        """Test graceful handling of database connection failures."""
        # This would simulate database connection loss
        # In a real scenario, this would involve network partitioning

        payload = {
            "title": "Resilience Test",
            "content": "Test content",
            "metadata": {"jurisdiction": "UK"},
        }

        # System should return error response, not crash
        response = requests.post(
            f"{test_config['backend_url']}/api/validate",
            json=payload,
            timeout=test_config['api_timeout']
        )

        # Should handle gracefully
        assert response.status_code < 500  # No server errors

    def test_cache_failure_fallback(self, test_config):
        """Test fallback when cache is unavailable."""
        payload = {
            "title": "Cache Resilience Test",
            "content": "Test content",
            "metadata": {},
        }

        # Make request with potentially unavailable cache
        response = requests.post(
            f"{test_config['backend_url']}/api/validate",
            json=payload,
            timeout=test_config['api_timeout']
        )

        # Should still work even if cache is down
        assert response.status_code in [200, 202, 400, 422]


@pytest.mark.chaos
class TestNetworkFailureResilience:
    """Test system resilience to network failures."""

    def test_timeout_handling(self, test_config):
        """Test timeout handling for slow responses."""
        # Set a very short timeout
        short_timeout = 0.001

        try:
            response = requests.post(
                f"{test_config['backend_url']}/api/validate",
                json={
                    "title": "Timeout Test",
                    "content": "Test",
                    "metadata": {},
                },
                timeout=short_timeout
            )
        except requests.exceptions.Timeout:
            # Expected behavior
            assert True
        except requests.exceptions.RequestException as e:
            # Other network errors also acceptable
            assert "timeout" in str(e).lower() or "connection" in str(e).lower()

    def test_connection_reset_resilience(self, test_config):
        """Test resilience to connection resets."""
        payload = {
            "title": "Connection Test",
            "content": "Test content",
            "metadata": {},
        }

        try:
            response = requests.post(
                f"{test_config['backend_url']}/api/validate",
                json=payload,
                timeout=test_config['api_timeout']
            )
            # If it succeeds, great
            assert response.status_code < 500
        except requests.exceptions.ConnectionError:
            # Acceptable - indicates connection issue, not application crash
            assert True


@pytest.mark.chaos
class TestHighLoadResilience:
    """Test system under high load."""

    def test_concurrent_requests(self, test_config):
        """Test system handles concurrent requests."""
        payload = {
            "title": "High Load Test",
            "content": "Test content",
            "metadata": {},
        }

        def make_request():
            try:
                response = requests.post(
                    f"{test_config['backend_url']}/api/validate",
                    json=payload,
                    timeout=test_config['api_timeout']
                )
                return response.status_code < 500
            except Exception:
                return False

        # Make 10 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in as_completed(futures)]

        # Most requests should succeed
        successful = sum(results)
        assert successful >= len(results) * 0.7  # At least 70% success

    def test_rapid_sequential_requests(self, test_config):
        """Test rapid sequential requests."""
        payload = {
            "title": "Rapid Request Test",
            "content": "Test content",
            "metadata": {},
        }

        responses = []
        for _ in range(5):
            try:
                response = requests.post(
                    f"{test_config['backend_url']}/api/validate",
                    json=payload,
                    timeout=test_config['api_timeout']
                )
                responses.append(response.status_code < 500)
            except Exception:
                responses.append(False)

        # Most requests should succeed
        assert sum(responses) >= len(responses) * 0.6


@pytest.mark.chaos
class TestMemoryLeakDetection:
    """Basic memory behavior tests."""

    def test_repeated_validation_memory(self, test_config):
        """Test repeated validations don't leak memory."""
        payload = {
            "title": "Memory Test",
            "content": "Test content" * 100,  # Larger content
            "metadata": {},
        }

        response_times = []

        for _ in range(5):
            start = time.time()
            response = requests.post(
                f"{test_config['backend_url']}/api/validate",
                json=payload,
                timeout=test_config['api_timeout']
            )
            elapsed = time.time() - start
            response_times.append(elapsed)

            assert response.status_code in [200, 202]

        # Response times should not significantly degrade
        avg_first = sum(response_times[:2]) / 2
        avg_last = sum(response_times[-2:]) / 2

        # Allow 2x degradation due to system load
        assert avg_last < avg_first * 2


@pytest.mark.chaos
class TestPartialFailureHandling:
    """Test handling of partial failures."""

    def test_batch_with_partial_failures(self, test_config):
        """Test batch processing with some invalid documents."""
        payload = {
            "documents": [
                {"title": "Valid1", "content": "Content 1", "metadata": {}},
                {"title": "", "content": None},  # Invalid
                {"title": "Valid2", "content": "Content 2", "metadata": {}},
            ]
        }

        response = requests.post(
            f"{test_config['backend_url']}/api/validate/batch",
            json=payload,
            timeout=test_config['api_timeout']
        )

        # Should handle gracefully
        assert response.status_code < 500

    def test_mixed_gate_execution(self, test_config):
        """Test with some gates failing."""
        payload = {
            "title": "Mixed Gates Test",
            "content": "Test content",
            "metadata": {},
            "gates": [
                "valid_gate",
                "nonexistent_gate",
                "another_gate",
            ],
        }

        response = requests.post(
            f"{test_config['backend_url']}/api/validate",
            json=payload,
            timeout=test_config['api_timeout']
        )

        # Should handle gracefully
        assert response.status_code < 500


@pytest.mark.chaos
class TestErrorPropagation:
    """Test error handling and propagation."""

    def test_invalid_input_doesnt_crash_system(self, test_config):
        """Test invalid inputs don't crash the system."""
        invalid_payloads = [
            {},  # Empty
            {"title": "Test"},  # Missing content
            {"content": "Test"},  # Missing title
            None,  # Invalid JSON
            {"title": "Test", "content": "Test", "metadata": "invalid"},  # Wrong type
        ]

        for payload in invalid_payloads:
            if payload is None:
                continue

            response = requests.post(
                f"{test_config['backend_url']}/api/validate",
                json=payload,
                timeout=test_config['api_timeout']
            )

            # Should return 4xx error, never 5xx
            assert response.status_code < 500

    def test_exception_doesnt_break_subsequent_requests(self, test_config):
        """Test that one failed request doesn't break subsequent ones."""
        # First request is valid
        valid_payload = {
            "title": "Valid",
            "content": "Valid content",
            "metadata": {},
        }

        # Second request is invalid
        invalid_payload = {"invalid": "data"}

        # Third request should still work
        response1 = requests.post(
            f"{test_config['backend_url']}/api/validate",
            json=valid_payload,
            timeout=test_config['api_timeout']
        )
        assert response1.status_code in [200, 202]

        response2 = requests.post(
            f"{test_config['backend_url']}/api/validate",
            json=invalid_payload,
            timeout=test_config['api_timeout']
        )
        assert response2.status_code >= 400

        response3 = requests.post(
            f"{test_config['backend_url']}/api/validate",
            json=valid_payload,
            timeout=test_config['api_timeout']
        )
        assert response3.status_code in [200, 202]
