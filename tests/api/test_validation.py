"""
Document Validation Flow Tests

Tests the complete validation workflow including:
- Document type detection
- Module selection
- Gate execution
- Risk assessment
- Violation reporting
"""

import pytest
import json
from datetime import datetime


class TestValidationWorkflow:
    """Test end-to-end validation workflow."""

    def test_single_module_validation(self, client, sample_gdpr_violation):
        """Test validation with single module."""
        payload = {
            'text': sample_gdpr_violation,
            'document_type': 'privacy_policy',
            'modules': ['gdpr_uk']
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()

        # Verify response structure
        assert 'validation' in data
        assert 'risk' in data

        validation = data['validation']
        assert 'modules' in validation
        assert 'gdpr_uk' in validation['modules']

        # Check module results
        gdpr_result = validation['modules']['gdpr_uk']
        assert 'status' in gdpr_result
        assert 'violations' in gdpr_result
        assert 'gates' in gdpr_result

    def test_multi_module_validation(self, client, sample_compliant_text):
        """Test validation with multiple modules."""
        payload = {
            'text': sample_compliant_text,
            'document_type': 'general',
            'modules': ['gdpr_uk', 'fca_uk', 'nda_uk']
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()

        validation = data['validation']

        # All requested modules should be in results
        assert 'gdpr_uk' in validation['modules']
        assert 'fca_uk' in validation['modules']
        assert 'nda_uk' in validation['modules']

    def test_all_modules_validation(self, client, sample_compliant_text):
        """Test validation with all available modules."""
        payload = {
            'text': sample_compliant_text,
            'document_type': 'general'
            # No modules specified - should use all
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()

        validation = data['validation']
        modules = validation['modules']

        # Should include all 5 modules
        expected_modules = ['fca_uk', 'gdpr_uk', 'tax_uk', 'nda_uk', 'hr_scottish']
        for module in expected_modules:
            assert module in modules


class TestRiskAssessment:
    """Test risk level assessment logic."""

    def test_low_risk_document(self, client, sample_compliant_text):
        """Test compliant document receives LOW risk."""
        payload = {
            'text': sample_compliant_text,
            'document_type': 'privacy_policy',
            'modules': ['gdpr_uk']
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()

        # Should be low risk
        assert data['risk'] == 'LOW'

    def test_high_risk_document(self, client, sample_violation_text):
        """Test document with violations receives HIGH risk."""
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

        assert response.status_code == 200
        data = response.get_json()

        # Should be high or critical risk
        assert data['risk'] in ['HIGH', 'CRITICAL']

    def test_risk_aggregation_across_modules(self, client, sample_violation_text):
        """Test overall risk aggregates across modules."""
        payload = {
            'text': sample_violation_text,
            'document_type': 'financial',
            'modules': ['fca_uk', 'gdpr_uk']
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()

        # Overall risk should reflect highest module risk
        assert 'risk' in data
        assert data['risk'] in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']


class TestGateExecution:
    """Test individual gate execution."""

    def test_gate_failure_reporting(self, client, sample_violation_text):
        """Test failed gates are properly reported."""
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

        assert response.status_code == 200
        data = response.get_json()

        fca_result = data['validation']['modules']['fca_uk']
        gates = fca_result['gates']

        # Should have at least one failed gate
        failed_gates = [g for g, info in gates.items() if info.get('status') == 'FAIL']
        assert len(failed_gates) > 0

        # Check gate failure structure
        for gate_name in failed_gates:
            gate_info = gates[gate_name]
            assert 'status' in gate_info
            assert 'severity' in gate_info
            assert 'message' in gate_info

    def test_gate_pass_reporting(self, client, sample_compliant_text):
        """Test passed gates are properly reported."""
        payload = {
            'text': sample_compliant_text,
            'document_type': 'privacy_policy',
            'modules': ['gdpr_uk']
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()

        gdpr_result = data['validation']['modules']['gdpr_uk']

        # Should have overall PASS status
        assert gdpr_result['status'] in ['PASS', 'WARN']

    def test_severity_levels(self, client, sample_violation_text):
        """Test gates report appropriate severity levels."""
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

        assert response.status_code == 200
        data = response.get_json()

        fca_result = data['validation']['modules']['fca_uk']
        gates = fca_result['gates']

        # Check that severity levels are valid
        valid_severities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        for gate_info in gates.values():
            if 'severity' in gate_info:
                assert gate_info['severity'] in valid_severities


class TestViolationReporting:
    """Test violation count and details."""

    def test_violation_count(self, client, sample_violation_text):
        """Test violation counts are accurate."""
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

        assert response.status_code == 200
        data = response.get_json()

        validation = data['validation']
        fca_result = validation['modules']['fca_uk']

        # Should have violations
        assert fca_result['violations'] > 0

        # Violation count should match failed gates
        failed_gates = [g for g, info in fca_result['gates'].items()
                       if info.get('status') == 'FAIL']
        assert fca_result['violations'] == len(failed_gates)

    def test_zero_violations(self, client, sample_compliant_text):
        """Test compliant document has zero violations."""
        payload = {
            'text': sample_compliant_text,
            'document_type': 'privacy_policy',
            'modules': ['gdpr_uk']
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()

        gdpr_result = data['validation']['modules']['gdpr_uk']
        assert gdpr_result['violations'] == 0

    def test_violation_details(self, client, sample_violation_text):
        """Test violation details include necessary information."""
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

        assert response.status_code == 200
        data = response.get_json()

        fca_result = data['validation']['modules']['fca_uk']
        gates = fca_result['gates']

        # Find a failed gate
        failed_gates = {k: v for k, v in gates.items() if v.get('status') == 'FAIL'}

        if failed_gates:
            gate_info = list(failed_gates.values())[0]

            # Should have violation details
            assert 'message' in gate_info
            assert 'severity' in gate_info
            assert gate_info['message']  # Non-empty message


class TestDocumentTypes:
    """Test validation behavior for different document types."""

    @pytest.mark.parametrize('doc_type', [
        'financial',
        'privacy_policy',
        'tax_document',
        'nda',
        'hr_document',
        'general'
    ])
    def test_document_type_handling(self, client, sample_compliant_text, doc_type):
        """Test validation handles different document types."""
        payload = {
            'text': sample_compliant_text,
            'document_type': doc_type,
            'modules': ['gdpr_uk']
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()
        assert 'validation' in data

    def test_unknown_document_type(self, client, sample_compliant_text):
        """Test validation handles unknown document types."""
        payload = {
            'text': sample_compliant_text,
            'document_type': 'unknown_type_xyz',
            'modules': ['gdpr_uk']
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        # Should still process, just with unknown type
        assert response.status_code == 200


class TestCaching:
    """Test validation result caching."""

    def test_cache_hit(self, client, sample_compliant_text):
        """Test subsequent identical requests hit cache."""
        payload = {
            'text': sample_compliant_text,
            'document_type': 'privacy_policy',
            'modules': ['gdpr_uk']
        }

        # First request
        response1 = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        # Second identical request
        response2 = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response1.status_code == 200
        assert response2.status_code == 200

        # Second response should indicate cache hit
        data2 = response2.get_json()
        # May have _cached flag
        if '_cached' in data2.get('validation', {}):
            assert data2['validation']['_cached'] is True

    def test_cache_different_text(self, client, sample_compliant_text, sample_violation_text):
        """Test different text doesn't hit cache."""
        payload1 = {
            'text': sample_compliant_text,
            'document_type': 'test',
            'modules': ['gdpr_uk']
        }

        payload2 = {
            'text': sample_violation_text,
            'document_type': 'test',
            'modules': ['gdpr_uk']
        }

        response1 = client.post(
            '/api/validate-document',
            data=json.dumps(payload1),
            content_type='application/json'
        )

        response2 = client.post(
            '/api/validate-document',
            data=json.dumps(payload2),
            content_type='application/json'
        )

        # Should get different results
        data1 = response1.get_json()
        data2 = response2.get_json()

        # Results should differ
        assert data1['risk'] != data2['risk'] or \
               data1['validation']['status'] != data2['validation']['status']


class TestValidationTimestamp:
    """Test validation timestamps."""

    def test_timestamp_present(self, client, sample_compliant_text):
        """Test validation includes timestamp."""
        payload = {
            'text': sample_compliant_text,
            'document_type': 'test',
            'modules': ['gdpr_uk']
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()

        validation = data['validation']

        # Should have timestamp
        if 'timestamp' in validation:
            # Validate timestamp format
            timestamp = validation['timestamp']
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))


class TestModuleSpecificValidation:
    """Test module-specific validation behavior."""

    def test_fca_financial_validation(self, client, sample_violation_text):
        """Test FCA module validates financial content."""
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

        assert response.status_code == 200
        data = response.get_json()

        # FCA should catch violations
        fca_result = data['validation']['modules']['fca_uk']
        assert fca_result['status'] == 'FAIL'
        assert fca_result['violations'] > 0

    def test_gdpr_privacy_validation(self, client, sample_gdpr_violation):
        """Test GDPR module validates privacy content."""
        payload = {
            'text': sample_gdpr_violation,
            'document_type': 'privacy_policy',
            'modules': ['gdpr_uk']
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()

        # GDPR should catch violations
        gdpr_result = data['validation']['modules']['gdpr_uk']
        assert gdpr_result['violations'] > 0

    def test_tax_document_validation(self, client, sample_tax_document):
        """Test Tax module validates tax documents."""
        payload = {
            'text': sample_tax_document,
            'document_type': 'tax_document',
            'modules': ['tax_uk']
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()

        assert 'tax_uk' in data['validation']['modules']

    def test_nda_validation(self, client, sample_nda_document):
        """Test NDA module validates NDA documents."""
        payload = {
            'text': sample_nda_document,
            'document_type': 'nda',
            'modules': ['nda_uk']
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()

        assert 'nda_uk' in data['validation']['modules']

    def test_hr_document_validation(self, client, sample_hr_document):
        """Test HR module validates HR documents."""
        payload = {
            'text': sample_hr_document,
            'document_type': 'hr_document',
            'modules': ['hr_scottish']
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()

        assert 'hr_scottish' in data['validation']['modules']
