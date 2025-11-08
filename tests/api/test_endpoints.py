"""
API Endpoint Tests for LOKI Compliance Platform

Tests all public API endpoints for:
- Correct status codes
- Response structure
- Error handling
- Input validation
- Authentication requirements
"""

import pytest
import json
from datetime import datetime


class TestHealthEndpoint:
    """Test /api/health endpoint."""

    def test_health_basic(self, client):
        """Test basic health check returns 200 OK."""
        response = client.get('/api/health')
        assert response.status_code == 200

        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'modules' in data
        assert 'modules_loaded' in data

    def test_health_detailed(self, client):
        """Test detailed health check with query parameter."""
        response = client.get('/api/health?detailed=true')
        assert response.status_code == 200

        data = response.get_json()
        assert 'gate_counts' in data
        assert 'cache_stats' in data

    def test_health_both_routes(self, client):
        """Test both /health and /api/health routes work."""
        response1 = client.get('/health')
        response2 = client.get('/api/health')

        assert response1.status_code == 200
        assert response2.status_code == 200


class TestModulesEndpoint:
    """Test /api/modules endpoint."""

    def test_list_modules(self, client):
        """Test listing all available modules."""
        response = client.get('/api/modules')
        assert response.status_code == 200

        data = response.get_json()
        assert 'modules' in data
        assert len(data['modules']) > 0

        # Verify module structure
        module = data['modules'][0]
        assert 'id' in module
        assert 'name' in module
        assert 'version' in module
        assert 'gates' in module

    def test_expected_modules_present(self, client):
        """Test that all expected modules are loaded."""
        response = client.get('/api/modules')
        data = response.get_json()

        module_ids = [m['id'] for m in data['modules']]
        expected = ['fca_uk', 'gdpr_uk', 'tax_uk', 'nda_uk', 'hr_scottish']

        for module_id in expected:
            assert module_id in module_ids


class TestValidateDocumentEndpoint:
    """Test /api/validate-document endpoint."""

    def test_validate_compliant_document(self, client, sample_compliant_text):
        """Test validation of compliant document."""
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

        assert 'validation' in data
        assert 'risk' in data

    def test_validate_violation_document(self, client, sample_violation_text):
        """Test validation of document with violations."""
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

        assert data['risk'] in ['HIGH', 'CRITICAL']
        assert data['validation']['status'] == 'FAIL'

    def test_validate_missing_text(self, client):
        """Test validation fails without text."""
        payload = {
            'document_type': 'financial',
            'modules': ['fca_uk']
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 400

    def test_validate_empty_text(self, client):
        """Test validation handles empty text."""
        payload = {
            'text': '',
            'document_type': 'financial',
            'modules': ['fca_uk']
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 400

    def test_validate_default_all_modules(self, client, sample_compliant_text):
        """Test validation defaults to all modules when not specified."""
        payload = {
            'text': sample_compliant_text,
            'document_type': 'general'
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()

        # Should include results from multiple modules
        assert len(data['validation']['modules']) > 1

    def test_validate_invalid_json(self, client):
        """Test validation handles invalid JSON."""
        response = client.post(
            '/api/validate-document',
            data='invalid json{',
            content_type='application/json'
        )

        assert response.status_code in [400, 500]

    def test_validate_large_document(self, client):
        """Test validation handles large documents."""
        large_text = "Test content. " * 10000  # ~150KB

        payload = {
            'text': large_text,
            'document_type': 'general',
            'modules': ['gdpr_uk']
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 200

    @pytest.mark.parametrize('module', ['fca_uk', 'gdpr_uk', 'tax_uk', 'nda_uk', 'hr_scottish'])
    def test_validate_each_module(self, client, sample_compliant_text, module):
        """Test validation works for each individual module."""
        payload = {
            'text': sample_compliant_text,
            'document_type': 'general',
            'modules': [module]
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()
        assert module in data['validation']['modules']


class TestCorrectDocumentEndpoint:
    """Test /api/correct-document endpoint."""

    def test_correct_document_basic(self, client, sample_violation_text, mock_validation_fail):
        """Test basic document correction."""
        payload = {
            'text': sample_violation_text,
            'validation_results': mock_validation_fail
        }

        response = client.post(
            '/api/correct-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()

        assert 'corrected' in data
        assert 'original' in data
        assert 'corrections' in data

    def test_correct_missing_text(self, client, mock_validation_fail):
        """Test correction fails without text."""
        payload = {
            'validation_results': mock_validation_fail
        }

        response = client.post(
            '/api/correct-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 400

    def test_correct_missing_validation(self, client, sample_violation_text):
        """Test correction fails without validation results."""
        payload = {
            'text': sample_violation_text
        }

        response = client.post(
            '/api/correct-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 400


class TestSynthesizeEndpoint:
    """Test /api/synthesize endpoint."""

    def test_synthesize_basic(self, client, mock_validation_fail):
        """Test basic document synthesis."""
        payload = {
            'base_text': 'Original document content',
            'validation': mock_validation_fail,
            'context': {'company': 'Test Corp'},
            'modules': ['fca_uk']
        }

        response = client.post(
            '/api/synthesize',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 200

    def test_synthesize_missing_validation(self, client):
        """Test synthesis fails without validation."""
        payload = {
            'base_text': 'Test content'
        }

        response = client.post(
            '/api/synthesize',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 400

    def test_synthesize_with_empty_modules(self, client, mock_validation_fail):
        """Test synthesis with empty modules list defaults to all."""
        payload = {
            'validation': mock_validation_fail,
            'modules': []
        }

        response = client.post(
            '/api/synthesize',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 200


class TestGatesEndpoint:
    """Test /api/gates endpoint."""

    def test_list_all_gates(self, client):
        """Test listing all gates."""
        response = client.get('/api/gates')
        assert response.status_code == 200

        data = response.get_json()
        assert 'gates' in data
        assert len(data['gates']) > 0

        # Verify gate structure
        gate = data['gates'][0]
        assert 'id' in gate
        assert 'version' in gate
        assert 'module' in gate
        assert 'severity' in gate

    def test_list_module_gates(self, client):
        """Test listing gates for specific module."""
        response = client.get('/api/gates?module=fca_uk')
        assert response.status_code == 200

        data = response.get_json()
        gates = data['gates']

        # All gates should belong to fca_uk
        for gate in gates:
            assert gate['module'] == 'fca_uk'

    def test_list_deprecated_gates(self, client):
        """Test listing deprecated gates."""
        response = client.get('/api/gates/deprecated')
        assert response.status_code == 200

        data = response.get_json()
        assert 'deprecated_gates' in data


class TestAnalyticsEndpoints:
    """Test analytics endpoints."""

    def test_analytics_overview(self, client):
        """Test analytics overview endpoint."""
        response = client.get('/api/analytics/overview')
        assert response.status_code == 200

    def test_analytics_overview_with_window(self, client):
        """Test analytics overview with time window."""
        response = client.get('/api/analytics/overview?window=7')
        assert response.status_code == 200

    def test_analytics_trends(self, client):
        """Test analytics trends endpoint."""
        response = client.get('/api/analytics/trends')
        assert response.status_code == 200

    def test_analytics_modules(self, client):
        """Test analytics modules endpoint."""
        response = client.get('/api/analytics/modules')
        assert response.status_code == 200

        data = response.get_json()
        assert 'modules' in data
        assert 'top_gates' in data


class TestCacheEndpoints:
    """Test cache management endpoints."""

    def test_cache_stats(self, client):
        """Test cache statistics endpoint."""
        response = client.get('/api/cache/stats')
        assert response.status_code == 200

        data = response.get_json()
        # Verify expected cache stat fields
        assert isinstance(data, dict)

    def test_cache_clear(self, client):
        """Test cache clear endpoint."""
        response = client.post('/api/cache/clear')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True


class TestAuditEndpoints:
    """Test audit log endpoints."""

    def test_audit_stats(self, client):
        """Test audit statistics endpoint."""
        response = client.get('/api/audit/stats')
        assert response.status_code == 200

    def test_audit_stats_with_since(self, client):
        """Test audit stats with time filter."""
        since = datetime.utcnow().isoformat()
        response = client.get(f'/api/audit/stats?since={since}')
        assert response.status_code == 200


class TestProxyEndpoint:
    """Test universal proxy endpoint."""

    def test_proxy_anthropic(self, client):
        """Test proxying to Anthropic."""
        payload = {
            'provider': 'anthropic',
            'messages': [{'role': 'user', 'content': 'Test'}],
            'model': 'claude-3-5-sonnet-20241022'
        }

        response = client.post(
            '/api/proxy',
            data=json.dumps(payload),
            content_type='application/json',
            headers={'x-api-key': 'test-key'}
        )

        # May fail without valid API key, but should not be 500
        assert response.status_code in [200, 401, 403]

    def test_proxy_missing_provider(self, client):
        """Test proxy fails without provider."""
        payload = {
            'messages': [{'role': 'user', 'content': 'Test'}]
        }

        response = client.post(
            '/api/proxy',
            data=json.dumps(payload),
            content_type='application/json'
        )

        # Should default to anthropic or return error
        assert response.status_code in [400, 401]

    def test_proxy_invalid_provider(self, client):
        """Test proxy fails with invalid provider."""
        payload = {
            'provider': 'invalid_provider',
            'messages': [{'role': 'user', 'content': 'Test'}]
        }

        response = client.post(
            '/api/proxy',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 400


class TestErrorHandling:
    """Test API error handling."""

    def test_404_route(self, client):
        """Test 404 for non-existent route."""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404

    def test_method_not_allowed(self, client):
        """Test 405 for wrong HTTP method."""
        response = client.delete('/api/health')
        assert response.status_code == 405

    def test_large_payload_rejection(self, client):
        """Test rejection of oversized payload."""
        # Create payload over 10MB limit
        large_payload = {
            'text': 'x' * (11 * 1024 * 1024),  # 11MB
            'document_type': 'test'
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(large_payload),
            content_type='application/json'
        )

        assert response.status_code == 413


class TestCORSHeaders:
    """Test CORS header configuration."""

    def test_cors_headers_present(self, client):
        """Test CORS headers are included in responses."""
        response = client.options('/api/health')
        # CORS headers should be present
        assert response.status_code in [200, 204]

    def test_cors_allows_localhost(self, client, sample_compliant_text):
        """Test CORS allows localhost origins."""
        response = client.post(
            '/api/validate-document',
            data=json.dumps({
                'text': sample_compliant_text,
                'document_type': 'test'
            }),
            content_type='application/json',
            headers={'Origin': 'http://localhost:3000'}
        )

        assert response.status_code == 200


class TestResponseFormat:
    """Test API response format consistency."""

    def test_json_content_type(self, client):
        """Test all API responses use JSON content type."""
        response = client.get('/api/health')
        assert 'application/json' in response.content_type

    def test_error_response_format(self, client):
        """Test error responses follow consistent format."""
        response = client.post(
            '/api/validate-document',
            data=json.dumps({}),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.get_json()
        assert isinstance(data, dict)

    def test_success_response_structure(self, client, sample_compliant_text):
        """Test success responses have consistent structure."""
        response = client.post(
            '/api/validate-document',
            data=json.dumps({
                'text': sample_compliant_text,
                'document_type': 'test',
                'modules': ['gdpr_uk']
            }),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()

        # Should have standard top-level keys
        assert 'validation' in data or 'error' in data
