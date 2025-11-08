"""
False Negative Tests

Tests that violations are correctly detected by gates.
Goal: <0.1% false negative rate for known violations
"""

import pytest
import json


@pytest.mark.gates
class TestFCAFalseNegatives:
    """Test FCA gates catch all violations."""

    @pytest.mark.parametrize('violation_text,expected_gate', [
        ("GUARANTEED 20% returns every year!", "misleading_claims"),
        ("Zero risk investment opportunity", "risk_warnings"),
        ("Act now! Limited time offer - invest today!", "pressure_tactics"),
        ("Past performance: 15% annually for 10 years straight", "past_performance"),
    ])
    def test_catches_fca_violations(self, client, violation_text, expected_gate):
        """Test FCA gates catch specific violations."""
        payload = {
            'text': violation_text,
            'document_type': 'financial',
            'modules': ['fca_uk']
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()

        fca_result = data['validation']['modules']['fca_uk']

        # Should detect violation
        assert fca_result['status'] == 'FAIL'
        assert fca_result['violations'] > 0


@pytest.mark.gates
class TestGDPRFalseNegatives:
    """Test GDPR gates catch all violations."""

    @pytest.mark.parametrize('violation_text', [
        "We collect your data. By using our site you agree to data sharing.",
        "Your data will be stored indefinitely for our purposes.",
        "We may share your information with third parties without notice.",
        "Cookies are automatically enabled. No opt-out available.",
    ])
    def test_catches_gdpr_violations(self, client, violation_text):
        """Test GDPR gates catch privacy violations."""
        payload = {
            'text': violation_text,
            'document_type': 'privacy_policy',
            'modules': ['gdpr_uk']
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        data = response.get_json()
        gdpr_result = data['validation']['modules']['gdpr_uk']

        # Should detect violation
        assert gdpr_result['violations'] > 0


@pytest.mark.gates
class TestComprehensiveDetection:
    """Test comprehensive violation detection."""

    def test_multiple_violations_detected(self, client, sample_violation_text):
        """Test multiple violations in one document are all caught."""
        payload = {
            'text': sample_violation_text,
            'document_type': 'financial',
            'modules': ['fca_uk']
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        data = response.get_json()
        fca_result = data['validation']['modules']['fca_uk']

        # Should catch multiple violations
        assert fca_result['violations'] >= 3

    def test_subtle_violations_detected(self, client):
        """Test subtle violations are detected."""
        subtle_violation = """
        Our investment strategy has consistently outperformed the market.
        Suitable for all investors seeking growth.
        Contact us to get started immediately.
        """

        payload = {
            'text': subtle_violation,
            'document_type': 'financial',
            'modules': ['fca_uk']
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        data = response.get_json()
        fca_result = data['validation']['modules']['fca_uk']

        # Should detect issues even if subtle
        assert fca_result['violations'] > 0 or fca_result['status'] == 'WARN'
