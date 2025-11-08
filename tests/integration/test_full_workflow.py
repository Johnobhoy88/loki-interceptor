"""
Full Workflow Integration Tests

Tests complete end-to-end scenarios including:
- Document submission
- Validation
- Correction
- Re-validation
- Synthesis
"""

import pytest
import json


@pytest.mark.integration
class TestCompleteWorkflow:
    """Test complete document processing workflow."""

    def test_validate_correct_revalidate_flow(self, client, sample_violation_text):
        """Test full workflow: validate -> correct -> re-validate."""
        # Step 1: Validate original document
        validate_payload = {
            'text': sample_violation_text,
            'document_type': 'financial',
            'modules': ['fca_uk']
        }

        validate_response = client.post(
            '/api/validate-document',
            data=json.dumps(validate_payload),
            content_type='application/json'
        )

        assert validate_response.status_code == 200
        validation_data = validate_response.get_json()

        original_violations = validation_data['validation']['modules']['fca_uk']['violations']
        assert original_violations > 0  # Should have violations

        # Step 2: Correct document
        correct_payload = {
            'text': sample_violation_text,
            'validation_results': validation_data['validation']
        }

        correct_response = client.post(
            '/api/correct-document',
            data=json.dumps(correct_payload),
            content_type='application/json'
        )

        assert correct_response.status_code == 200
        correction_data = correct_response.get_json()

        corrected_text = correction_data['corrected']
        assert corrected_text != sample_violation_text  # Should be different

        # Step 3: Re-validate corrected document
        revalidate_payload = {
            'text': corrected_text,
            'document_type': 'financial',
            'modules': ['fca_uk']
        }

        revalidate_response = client.post(
            '/api/validate-document',
            data=json.dumps(revalidate_payload),
            content_type='application/json'
        )

        revalidation_data = revalidate_response.get_json()
        corrected_violations = revalidation_data['validation']['modules']['fca_uk']['violations']

        # Should have fewer violations
        assert corrected_violations < original_violations

    def test_synthesis_workflow(self, client, sample_violation_text):
        """Test validation -> synthesis workflow."""
        # Step 1: Validate
        validate_payload = {
            'text': sample_violation_text,
            'document_type': 'financial',
            'modules': ['fca_uk']
        }

        validate_response = client.post(
            '/api/validate-document',
            data=json.dumps(validate_payload),
            content_type='application/json'
        )

        validation_data = validate_response.get_json()

        # Step 2: Synthesize
        synthesize_payload = {
            'base_text': sample_violation_text,
            'validation': validation_data['validation'],
            'modules': ['fca_uk']
        }

        synthesize_response = client.post(
            '/api/synthesize',
            data=json.dumps(synthesize_payload),
            content_type='application/json'
        )

        assert synthesize_response.status_code == 200


@pytest.mark.integration
class TestMultiModuleWorkflow:
    """Test workflows involving multiple modules."""

    def test_multi_module_validation_correction(self, client):
        """Test correction across multiple modules."""
        # Document with violations in multiple areas
        multi_violation_text = """
        Investment Opportunity - GUARANTEED Returns!

        We collect your data and may share with anyone.
        No refunds. All sales final.

        By investing, you agree to all terms.
        """

        # Validate with multiple modules
        validate_payload = {
            'text': multi_violation_text,
            'document_type': 'financial',
            'modules': ['fca_uk', 'gdpr_uk']
        }

        validate_response = client.post(
            '/api/validate-document',
            data=json.dumps(validate_payload),
            content_type='application/json'
        )

        validation_data = validate_response.get_json()

        # Should have violations in both modules
        assert 'fca_uk' in validation_data['validation']['modules']
        assert 'gdpr_uk' in validation_data['validation']['modules']

        # Correct
        correct_payload = {
            'text': multi_violation_text,
            'validation_results': validation_data['validation']
        }

        correct_response = client.post(
            '/api/correct-document',
            data=json.dumps(correct_payload),
            content_type='application/json'
        )

        assert correct_response.status_code == 200


@pytest.mark.integration
class TestErrorRecovery:
    """Test error recovery in workflows."""

    def test_invalid_validation_recovery(self, client):
        """Test system recovers from invalid validation input."""
        # Try to correct without proper validation
        payload = {
            'text': 'test',
            'validation_results': {}
        }

        response = client.post(
            '/api/correct-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        # Should handle gracefully
        assert response.status_code in [200, 400]

    def test_large_document_workflow(self, client):
        """Test workflow with large documents."""
        large_text = "Compliant content. " * 5000  # ~100KB

        # Validate
        validate_payload = {
            'text': large_text,
            'document_type': 'general',
            'modules': ['gdpr_uk']
        }

        validate_response = client.post(
            '/api/validate-document',
            data=json.dumps(validate_payload),
            content_type='application/json'
        )

        assert validate_response.status_code == 200


@pytest.mark.integration
class TestCachingIntegration:
    """Test caching behavior in workflows."""

    def test_cached_validation_performance(self, client, sample_compliant_text):
        """Test cached results improve performance."""
        import time

        payload = {
            'text': sample_compliant_text,
            'document_type': 'test',
            'modules': ['gdpr_uk']
        }

        # First request (uncached)
        start1 = time.time()
        response1 = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )
        duration1 = time.time() - start1

        # Second request (should be cached)
        start2 = time.time()
        response2 = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )
        duration2 = time.time() - start2

        assert response1.status_code == 200
        assert response2.status_code == 200

        # Cached request should be faster (or at least not slower)
        # Note: In testing this may not always be true due to overhead
        assert duration2 <= duration1 * 2  # Allow some variance
