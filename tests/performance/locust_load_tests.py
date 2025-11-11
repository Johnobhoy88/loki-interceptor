"""
Load testing suite using Locust for performance benchmarking.

Tests API endpoints under load with various concurrency levels,
request patterns, and failure scenarios.

Run with:
    locust -f tests/performance/locust_load_tests.py --host=http://localhost:5002
"""

from locust import HttpUser, task, between, events
import random
import json
import time
from typing import Dict, Any


class APIHeaders:
    """Common API headers."""
    @staticmethod
    def get_headers() -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "X-API-Key": "test-api-key-12345",
            "User-Agent": "Locust-Load-Test/1.0"
        }


class ValidationPayloads:
    """Sample payloads for validation endpoint."""

    COMPLIANT_DOCUMENT = {
        "document": """
        INVESTMENT PROSPECTUS

        Risk Disclosure
        This investment carries market risk. Past performance is not indicative
        of future results. The value of your investment may go down as well as up.

        Key Features
        - Diversified portfolio management
        - Professional fund managers
        - Regular performance reporting
        """,
        "modules": ["fca_uk", "gdpr_uk", "tax_uk"],
        "options": {
            "validate": True,
            "return_violations": True
        }
    }

    NON_COMPLIANT_DOCUMENT = {
        "document": """
        GUARANTEED 15% ANNUAL RETURNS!

        This is a risk-free investment. Zero loss guaranteed.
        Send your money today!
        """,
        "modules": ["fca_uk"],
        "options": {
            "validate": True,
            "return_violations": True
        }
    }

    PRIVACY_POLICY = {
        "document": """
        PRIVACY POLICY

        We collect your data and store it forever.
        We may share with anyone for any purpose.
        """,
        "modules": ["gdpr_uk"],
        "options": {
            "validate": True,
            "return_violations": True
        }
    }


class BasicValidationUser(HttpUser):
    """Basic user making validation requests."""

    wait_time = between(1, 3)

    @task(3)
    def validate_compliant_document(self):
        """Validate a compliant document."""
        with self.client.post(
            "/api/validate",
            json=ValidationPayloads.COMPLIANT_DOCUMENT,
            headers=APIHeaders.get_headers(),
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got {response.status_code} status code")

    @task(2)
    def validate_non_compliant_document(self):
        """Validate a non-compliant document."""
        with self.client.post(
            "/api/validate",
            json=ValidationPayloads.NON_COMPLIANT_DOCUMENT,
            headers=APIHeaders.get_headers(),
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got {response.status_code} status code")

    @task(1)
    def validate_privacy_policy(self):
        """Validate privacy policy."""
        with self.client.post(
            "/api/validate",
            json=ValidationPayloads.PRIVACY_POLICY,
            headers=APIHeaders.get_headers(),
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got {response.status_code} status code")


class CorrectionUser(HttpUser):
    """User making correction requests."""

    wait_time = between(2, 5)

    @task(2)
    def correct_document(self):
        """Correct a document."""
        payload = {
            "document": ValidationPayloads.NON_COMPLIANT_DOCUMENT["document"],
            "modules": ["fca_uk"],
            "violations": [
                {
                    "module": "fca_uk",
                    "gate": "misleading_claims",
                    "severity": "CRITICAL"
                }
            ]
        }

        with self.client.post(
            "/api/correct",
            json=payload,
            headers=APIHeaders.get_headers(),
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got {response.status_code} status code")

    @task(1)
    def get_correction_preview(self):
        """Get a preview of corrections."""
        payload = {
            "document": ValidationPayloads.NON_COMPLIANT_DOCUMENT["document"],
            "module": "fca_uk"
        }

        with self.client.post(
            "/api/preview",
            json=payload,
            headers=APIHeaders.get_headers(),
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got {response.status_code} status code")


class HealthCheckUser(HttpUser):
    """User making health check requests."""

    wait_time = between(0.5, 2)

    @task(10)
    def health_check(self):
        """Check API health."""
        with self.client.get(
            "/api/health",
            headers=APIHeaders.get_headers(),
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got {response.status_code} status code")

    @task(5)
    def get_status(self):
        """Get API status."""
        with self.client.get(
            "/api/status",
            headers=APIHeaders.get_headers(),
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got {response.status_code} status code")


class MixedWorkloadUser(HttpUser):
    """User simulating mixed workload with validation, correction, and health checks."""

    wait_time = between(1, 4)

    def on_start(self):
        """Initialize user."""
        self.test_count = 0
        self.start_time = time.time()

    @task(5)
    def validate_random_document(self):
        """Validate a random document."""
        payloads = [
            ValidationPayloads.COMPLIANT_DOCUMENT,
            ValidationPayloads.NON_COMPLIANT_DOCUMENT,
            ValidationPayloads.PRIVACY_POLICY,
        ]

        payload = random.choice(payloads)

        with self.client.post(
            "/api/validate",
            json=payload,
            headers=APIHeaders.get_headers(),
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
                self.test_count += 1
            else:
                response.failure(f"Got {response.status_code} status code")

    @task(2)
    def correct_random_document(self):
        """Correct a random document."""
        payload = {
            "document": random.choice([
                ValidationPayloads.COMPLIANT_DOCUMENT["document"],
                ValidationPayloads.NON_COMPLIANT_DOCUMENT["document"],
            ]),
            "modules": random.sample(
                ["fca_uk", "gdpr_uk", "tax_uk"],
                k=random.randint(1, 2)
            ),
            "violations": []
        }

        with self.client.post(
            "/api/correct",
            json=payload,
            headers=APIHeaders.get_headers(),
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
                self.test_count += 1
            else:
                response.failure(f"Got {response.status_code} status code")

    @task(1)
    def health_check(self):
        """Periodic health check."""
        with self.client.get(
            "/api/health",
            headers=APIHeaders.get_headers(),
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got {response.status_code} status code")


class StressTestUser(HttpUser):
    """User for stress testing with rapid requests."""

    wait_time = between(0.1, 0.5)

    @task(10)
    def rapid_validation(self):
        """Rapid validation requests."""
        payload = ValidationPayloads.COMPLIANT_DOCUMENT

        with self.client.post(
            "/api/validate",
            json=payload,
            headers=APIHeaders.get_headers(),
            timeout=5,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 429:
                # Rate limiting is expected
                response.success()
            else:
                response.failure(f"Got {response.status_code} status code")


class EdgeCaseUser(HttpUser):
    """User testing edge cases and error scenarios."""

    wait_time = between(2, 5)

    @task(1)
    def test_empty_document(self):
        """Test with empty document."""
        payload = {
            "document": "",
            "modules": ["fca_uk"],
            "options": {"validate": True}
        }

        with self.client.post(
            "/api/validate",
            json=payload,
            headers=APIHeaders.get_headers(),
            catch_response=True
        ) as response:
            # Empty documents might be handled gracefully
            if response.status_code in [200, 400]:
                response.success()
            else:
                response.failure(f"Got {response.status_code} status code")

    @task(1)
    def test_large_document(self):
        """Test with large document."""
        large_text = "x" * (1024 * 100)  # 100KB
        payload = {
            "document": large_text,
            "modules": ["fca_uk"],
            "options": {"validate": True}
        }

        with self.client.post(
            "/api/validate",
            json=payload,
            headers=APIHeaders.get_headers(),
            timeout=30,
            catch_response=True
        ) as response:
            if response.status_code in [200, 413]:  # 413 = Payload Too Large
                response.success()
            else:
                response.failure(f"Got {response.status_code} status code")

    @task(1)
    def test_invalid_module(self):
        """Test with invalid module."""
        payload = {
            "document": "Test document",
            "modules": ["invalid_module_xyz"],
            "options": {"validate": True}
        }

        with self.client.post(
            "/api/validate",
            json=payload,
            headers=APIHeaders.get_headers(),
            catch_response=True
        ) as response:
            if response.status_code in [400, 422]:  # Bad request expected
                response.success()
            else:
                response.failure(f"Got {response.status_code} status code")

    @task(1)
    def test_missing_api_key(self):
        """Test without API key."""
        headers = {
            "Content-Type": "application/json",
            # Missing X-API-Key
        }

        with self.client.post(
            "/api/validate",
            json=ValidationPayloads.COMPLIANT_DOCUMENT,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code in [401, 403]:  # Unauthorized expected
                response.success()
            else:
                # Some endpoints might be public
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Got {response.status_code} status code")


# Event handlers for logging and metrics

@events.request.add_listener
def on_request_success(request_type, name, response_time, response_length, **kwargs):
    """Log successful requests."""
    pass  # Logging handled by Locust


@events.request.add_listener
def on_request_failure(request_type, name, response_time, response_length, exception, **kwargs):
    """Log failed requests."""
    pass  # Logging handled by Locust


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts."""
    print("Load test starting...")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops."""
    print("Load test completed!")
    print(f"Total requests: {environment.stats.total.num_requests}")
    print(f"Total failures: {environment.stats.total.num_failures}")
