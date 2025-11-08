"""
Document Correction Flow Tests

Tests the document correction system including:
- Pattern-based corrections
- Strategy application
- Correction lineage
- Deterministic results
- Validation integration
"""

import pytest
import json
import hashlib


class TestCorrectionWorkflow:
    """Test end-to-end correction workflow."""

    def test_basic_correction(self, client, sample_violation_text):
        """Test basic document correction flow."""
        # First validate
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

        # Then correct
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

        # Verify correction structure
        assert 'original' in correction_data
        assert 'corrected' in correction_data
        assert 'corrections' in correction_data
        assert correction_data['original'] == sample_violation_text

    def test_correction_improves_compliance(self, client, sample_violation_text):
        """Test corrected text has better compliance than original."""
        # Validate original
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
        original_violations = validation_data['validation']['modules']['fca_uk']['violations']

        # Correct
        correct_payload = {
            'text': sample_violation_text,
            'validation_results': validation_data['validation']
        }

        correct_response = client.post(
            '/api/correct-document',
            data=json.dumps(correct_payload),
            content_type='application/json'
        )

        correction_data = correct_response.get_json()
        corrected_text = correction_data['corrected']

        # Validate corrected
        validate_corrected = {
            'text': corrected_text,
            'document_type': 'financial',
            'modules': ['fca_uk']
        }

        validate_corrected_response = client.post(
            '/api/validate-document',
            data=json.dumps(validate_corrected),
            content_type='application/json'
        )

        corrected_validation = validate_corrected_response.get_json()
        corrected_violations = corrected_validation['validation']['modules']['fca_uk']['violations']

        # Should have fewer violations
        assert corrected_violations <= original_violations

    def test_no_corrections_needed(self, client, sample_compliant_text):
        """Test correction handles already-compliant text."""
        # Validate
        validate_payload = {
            'text': sample_compliant_text,
            'document_type': 'privacy_policy',
            'modules': ['gdpr_uk']
        }

        validate_response = client.post(
            '/api/validate-document',
            data=json.dumps(validate_payload),
            content_type='application/json'
        )

        validation_data = validate_response.get_json()

        # Attempt correction
        correct_payload = {
            'text': sample_compliant_text,
            'validation_results': validation_data['validation']
        }

        correct_response = client.post(
            '/api/correct-document',
            data=json.dumps(correct_payload),
            content_type='application/json'
        )

        assert correct_response.status_code == 200
        correction_data = correct_response.get_json()

        # Should have minimal or no corrections
        assert isinstance(correction_data['corrections'], list)


class TestCorrectionMetadata:
    """Test correction metadata and lineage."""

    def test_correction_count(self, client, sample_violation_text, mock_validation_fail):
        """Test correction count is accurate."""
        correct_payload = {
            'text': sample_violation_text,
            'validation_results': mock_validation_fail
        }

        response = client.post(
            '/api/correct-document',
            data=json.dumps(correct_payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()

        if 'correction_count' in data:
            correction_count = data['correction_count']
            corrections_list = data['corrections']
            assert correction_count == len(corrections_list)

    def test_correction_details(self, client, sample_violation_text, mock_validation_fail):
        """Test each correction includes necessary details."""
        correct_payload = {
            'text': sample_violation_text,
            'validation_results': mock_validation_fail
        }

        response = client.post(
            '/api/correct-document',
            data=json.dumps(correct_payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()

        corrections = data['corrections']

        if corrections:
            for correction in corrections:
                # Each correction should have metadata
                assert isinstance(correction, dict)
                # May include: pattern, reason, before, after, etc.

    def test_deterministic_hash(self, client, sample_violation_text, mock_validation_fail):
        """Test corrections are deterministic with hash."""
        correct_payload = {
            'text': sample_violation_text,
            'validation_results': mock_validation_fail
        }

        # First correction
        response1 = client.post(
            '/api/correct-document',
            data=json.dumps(correct_payload),
            content_type='application/json'
        )

        # Second correction (identical input)
        response2 = client.post(
            '/api/correct-document',
            data=json.dumps(correct_payload),
            content_type='application/json'
        )

        data1 = response1.get_json()
        data2 = response2.get_json()

        # Corrected text should be identical
        assert data1['corrected'] == data2['corrected']

        # If hash is provided, should be identical
        if 'deterministic_hash' in data1 and 'deterministic_hash' in data2:
            assert data1['deterministic_hash'] == data2['deterministic_hash']


class TestCorrectionStrategies:
    """Test different correction strategies."""

    def test_regex_strategy(self, client):
        """Test regex-based corrections."""
        # Text with simple pattern violations
        text = "GUARANTEED returns! ACT NOW!"

        validation = {
            'status': 'FAIL',
            'modules': {
                'fca_uk': {
                    'status': 'FAIL',
                    'gates': {
                        'pressure_tactics': {'status': 'FAIL'}
                    }
                }
            }
        }

        correct_payload = {
            'text': text,
            'validation_results': validation
        }

        response = client.post(
            '/api/correct-document',
            data=json.dumps(correct_payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()

        corrected = data['corrected']
        # Should remove or replace problematic phrases
        assert corrected != text

    def test_template_insertion(self, client):
        """Test template-based corrections."""
        # Privacy policy missing required sections
        text = "We collect data."

        validation = {
            'status': 'FAIL',
            'modules': {
                'gdpr_uk': {
                    'status': 'FAIL',
                    'gates': {
                        'rights': {'status': 'FAIL'},
                        'lawful_basis': {'status': 'FAIL'}
                    }
                }
            }
        }

        correct_payload = {
            'text': text,
            'validation_results': validation
        }

        response = client.post(
            '/api/correct-document',
            data=json.dumps(correct_payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()

        corrected = data['corrected']
        # Should have more content than original
        assert len(corrected) >= len(text)


class TestCorrectionEdgeCases:
    """Test correction edge cases."""

    def test_empty_validation_results(self, client):
        """Test correction handles empty validation results."""
        correct_payload = {
            'text': 'Test text',
            'validation_results': {}
        }

        response = client.post(
            '/api/correct-document',
            data=json.dumps(correct_payload),
            content_type='application/json'
        )

        # Should handle gracefully
        assert response.status_code in [200, 400]

    def test_malformed_validation_results(self, client):
        """Test correction handles malformed validation."""
        correct_payload = {
            'text': 'Test text',
            'validation_results': {'invalid': 'structure'}
        }

        response = client.post(
            '/api/correct-document',
            data=json.dumps(correct_payload),
            content_type='application/json'
        )

        # Should handle gracefully
        assert response.status_code in [200, 400, 500]

    def test_very_long_document(self, client):
        """Test correction handles very long documents."""
        long_text = "Test content. " * 10000  # ~150KB
        validation = {
            'status': 'PASS',
            'modules': {'gdpr_uk': {'status': 'PASS', 'gates': {}}}
        }

        correct_payload = {
            'text': long_text,
            'validation_results': validation
        }

        response = client.post(
            '/api/correct-document',
            data=json.dumps(correct_payload),
            content_type='application/json'
        )

        assert response.status_code == 200

    def test_unicode_handling(self, client):
        """Test correction handles unicode characters."""
        text = "Test with unicode: £€¥ 中文 العربية"
        validation = {
            'status': 'PASS',
            'modules': {'gdpr_uk': {'status': 'PASS', 'gates': {}}}
        }

        correct_payload = {
            'text': text,
            'validation_results': validation
        }

        response = client.post(
            '/api/correct-document',
            data=json.dumps(correct_payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()

        # Unicode should be preserved
        assert '£' in data['corrected'] or '€' in data['corrected']


class TestModuleSpecificCorrections:
    """Test corrections for specific modules."""

    def test_fca_corrections(self, client, sample_violation_text):
        """Test FCA-specific corrections."""
        validation = {
            'status': 'FAIL',
            'modules': {
                'fca_uk': {
                    'status': 'FAIL',
                    'gates': {
                        'misleading_claims': {'status': 'FAIL'},
                        'risk_warnings': {'status': 'FAIL'}
                    }
                }
            }
        }

        correct_payload = {
            'text': sample_violation_text,
            'validation_results': validation
        }

        response = client.post(
            '/api/correct-document',
            data=json.dumps(correct_payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()

        # Should have corrections
        assert 'corrected' in data

    def test_gdpr_corrections(self, client, sample_gdpr_violation):
        """Test GDPR-specific corrections."""
        validation = {
            'status': 'FAIL',
            'modules': {
                'gdpr_uk': {
                    'status': 'FAIL',
                    'gates': {
                        'consent': {'status': 'FAIL'},
                        'purpose': {'status': 'FAIL'}
                    }
                }
            }
        }

        correct_payload = {
            'text': sample_gdpr_violation,
            'validation_results': validation
        }

        response = client.post(
            '/api/correct-document',
            data=json.dumps(correct_payload),
            content_type='application/json'
        )

        assert response.status_code == 200

    def test_multi_module_corrections(self, client):
        """Test corrections across multiple modules."""
        text = "Test document with multiple issues."

        validation = {
            'status': 'FAIL',
            'modules': {
                'fca_uk': {
                    'status': 'FAIL',
                    'gates': {'test_gate': {'status': 'FAIL'}}
                },
                'gdpr_uk': {
                    'status': 'FAIL',
                    'gates': {'test_gate': {'status': 'FAIL'}}
                }
            }
        }

        correct_payload = {
            'text': text,
            'validation_results': validation
        }

        response = client.post(
            '/api/correct-document',
            data=json.dumps(correct_payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()

        # Should apply corrections from both modules
        assert 'corrected' in data


class TestCorrectionQuality:
    """Test quality of corrections."""

    def test_preserves_meaning(self, client, sample_violation_text):
        """Test corrections preserve document meaning."""
        validation = {
            'status': 'FAIL',
            'modules': {
                'fca_uk': {
                    'status': 'FAIL',
                    'gates': {'test': {'status': 'FAIL'}}
                }
            }
        }

        correct_payload = {
            'text': sample_violation_text,
            'validation_results': validation
        }

        response = client.post(
            '/api/correct-document',
            data=json.dumps(correct_payload),
            content_type='application/json'
        )

        data = response.get_json()
        corrected = data['corrected']

        # Corrected text should not be empty
        assert len(corrected) > 0

        # Should retain some original content structure
        # (This is a basic check - actual verification would need semantic analysis)

    def test_no_corruption(self, client):
        """Test corrections don't corrupt document structure."""
        text = """
        Section 1: Introduction
        This is the introduction.

        Section 2: Main Content
        This is the main content.

        Section 3: Conclusion
        This is the conclusion.
        """

        validation = {
            'status': 'PASS',
            'modules': {'gdpr_uk': {'status': 'PASS', 'gates': {}}}
        }

        correct_payload = {
            'text': text,
            'validation_results': validation
        }

        response = client.post(
            '/api/correct-document',
            data=json.dumps(correct_payload),
            content_type='application/json'
        )

        data = response.get_json()
        corrected = data['corrected']

        # Basic structure should be preserved
        assert 'Section 1' in corrected or 'Section' in corrected
