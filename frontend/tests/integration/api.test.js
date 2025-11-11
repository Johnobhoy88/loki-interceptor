/**
 * Integration Tests - API Communication
 *
 * Tests for API integration including:
 * - Backend health checks
 * - Module catalog loading
 * - Validation workflows
 * - Analytics data fetching
 */

describe('API Integration Tests', () => {
  const API_BASE = 'http://127.0.0.1:5002';

  beforeEach(() => {
    fetch.mockClear();
  });

  describe('Backend Health Check', () => {
    test('should successfully check backend health', async () => {
      mockApiResponse({ status: 'ok', version: '1.0.0' });

      const response = await fetch(`${API_BASE}/health`);
      const data = await response.json();

      expect(response.ok).toBe(true);
      expect(data.status).toBe('ok');
      expect(fetch).toHaveBeenCalledWith(`${API_BASE}/health`);
    });

    test('should handle health check timeout', async () => {
      const timeoutError = new Error('Timeout');
      fetch.mockRejectedValueOnce(timeoutError);

      await expect(
        fetch(`${API_BASE}/health`)
      ).rejects.toThrow('Timeout');
    });

    test('should handle backend offline', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 503,
        statusText: 'Service Unavailable',
        json: () => Promise.resolve({ error: 'Backend offline' })
      });

      const response = await fetch(`${API_BASE}/health`);
      expect(response.ok).toBe(false);
      expect(response.status).toBe(503);
    });

    test('should include health check headers', async () => {
      mockApiResponse({ status: 'ok' });

      const timestamp = Date.now().toString();
      await fetch(`${API_BASE}/health`, {
        headers: {
          'x-loki-health-check': timestamp
        }
      });

      expect(fetch).toHaveBeenCalledWith(
        `${API_BASE}/health`,
        expect.objectContaining({
          headers: expect.objectContaining({
            'x-loki-health-check': timestamp
          })
        })
      );
    });
  });

  describe('Module Catalog Loading', () => {
    test('should load module catalog successfully', async () => {
      const modules = [
        { id: 'fca', name: 'FCA Compliance', enabled: true },
        { id: 'gdpr', name: 'GDPR', enabled: true },
        { id: 'smcr', name: 'SMCR', enabled: false }
      ];

      mockApiResponse(modules);

      const response = await fetch(`${API_BASE}/modules`);
      const data = await response.json();

      expect(data).toEqual(modules);
      expect(data.length).toBe(3);
      expect(data[0].id).toBe('fca');
    });

    test('should handle empty module catalog', async () => {
      mockApiResponse([]);

      const response = await fetch(`${API_BASE}/modules`);
      const data = await response.json();

      expect(data).toEqual([]);
      expect(Array.isArray(data)).toBe(true);
    });

    test('should handle module catalog error', async () => {
      mockApiError('Failed to load modules', 500);

      await expect(
        fetch(`${API_BASE}/modules`)
      ).rejects.toThrow('Failed to load modules');
    });
  });

  describe('Prompt Validation', () => {
    test('should validate prompt successfully', async () => {
      const validationResult = {
        status: 'pass',
        violations: [],
        warnings: [],
        metadata: { provider: 'anthropic', model: 'claude-3' }
      };

      mockApiResponse(validationResult);

      const response = await fetch(`${API_BASE}/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: 'Test prompt',
          provider: 'anthropic',
          modules: ['fca']
        })
      });

      const data = await response.json();

      expect(data.status).toBe('pass');
      expect(data.violations).toEqual([]);
      expect(fetch).toHaveBeenCalledWith(
        `${API_BASE}/validate`,
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          })
        })
      );
    });

    test('should detect violations in prompt', async () => {
      const validationResult = {
        status: 'fail',
        violations: [
          {
            rule: 'FCA-001',
            severity: 'high',
            message: 'Missing risk disclosure'
          }
        ],
        warnings: [],
        metadata: {}
      };

      mockApiResponse(validationResult);

      const response = await fetch(`${API_BASE}/validate`, {
        method: 'POST',
        body: JSON.stringify({ prompt: 'Risky prompt' })
      });

      const data = await response.json();

      expect(data.status).toBe('fail');
      expect(data.violations.length).toBe(1);
      expect(data.violations[0].rule).toBe('FCA-001');
      expect(data.violations[0].severity).toBe('high');
    });

    test('should handle validation with warnings', async () => {
      const validationResult = {
        status: 'warn',
        violations: [],
        warnings: [
          {
            rule: 'GDPR-002',
            message: 'Consider privacy notice'
          }
        ]
      };

      mockApiResponse(validationResult);

      const response = await fetch(`${API_BASE}/validate`, {
        method: 'POST',
        body: JSON.stringify({ prompt: 'Privacy-related prompt' })
      });

      const data = await response.json();

      expect(data.status).toBe('warn');
      expect(data.warnings.length).toBe(1);
      expect(data.warnings[0].rule).toBe('GDPR-002');
    });

    test('should validate with multiple modules', async () => {
      mockApiResponse({ status: 'pass', violations: [], warnings: [] });

      await fetch(`${API_BASE}/validate`, {
        method: 'POST',
        body: JSON.stringify({
          prompt: 'Test',
          modules: ['fca', 'gdpr', 'smcr']
        })
      });

      expect(fetch).toHaveBeenCalledTimes(1);
    });
  });

  describe('Document Validation', () => {
    test('should validate document successfully', async () => {
      const documentResult = {
        status: 'pass',
        compliance_score: 95,
        violations: [],
        suggestions: []
      };

      mockApiResponse(documentResult);

      const response = await fetch(`${API_BASE}/validate/document`, {
        method: 'POST',
        body: JSON.stringify({
          text: 'Document text',
          type: 'privacy_policy'
        })
      });

      const data = await response.json();

      expect(data.status).toBe('pass');
      expect(data.compliance_score).toBe(95);
    });

    test('should generate corrections for non-compliant document', async () => {
      const documentResult = {
        status: 'fail',
        compliance_score: 45,
        violations: [
          { rule: 'FCA-005', message: 'Missing required disclosure' }
        ],
        corrections: {
          original: 'Old text',
          corrected: 'New compliant text',
          changes: ['Added disclosure']
        }
      };

      mockApiResponse(documentResult);

      const response = await fetch(`${API_BASE}/validate/document`, {
        method: 'POST',
        body: JSON.stringify({
          text: 'Non-compliant document',
          enable_corrections: true
        })
      });

      const data = await response.json();

      expect(data.status).toBe('fail');
      expect(data.corrections).toBeDefined();
      expect(data.corrections.corrected).toBe('New compliant text');
    });
  });

  describe('Analytics Data', () => {
    test('should fetch analytics overview', async () => {
      const analyticsData = {
        total_validations: 1250,
        pass_rate: 87.5,
        top_violations: ['FCA-001', 'GDPR-002'],
        trend: 'improving'
      };

      mockApiResponse(analyticsData);

      const response = await fetch(`${API_BASE}/analytics?window=30`);
      const data = await response.json();

      expect(data.total_validations).toBe(1250);
      expect(data.pass_rate).toBe(87.5);
      expect(data.trend).toBe('improving');
    });

    test('should fetch analytics with custom window', async () => {
      mockApiResponse({ validations: [] });

      await fetch(`${API_BASE}/analytics?window=7`);

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('window=7')
      );
    });

    test('should handle analytics loading error', async () => {
      mockApiError('Analytics service unavailable', 503);

      await expect(
        fetch(`${API_BASE}/analytics`)
      ).rejects.toThrow('Analytics service unavailable');
    });
  });

  describe('API Key Management', () => {
    test('should save API key', async () => {
      mockApiResponse({ success: true, message: 'API key saved' });

      const response = await fetch(`${API_BASE}/keys`, {
        method: 'POST',
        body: JSON.stringify({
          provider: 'anthropic',
          key: 'sk-ant-test-key'
        })
      });

      const data = await response.json();

      expect(data.success).toBe(true);
      expect(fetch).toHaveBeenCalledWith(
        `${API_BASE}/keys`,
        expect.objectContaining({ method: 'POST' })
      );
    });

    test('should validate API key format', async () => {
      mockApiResponse(
        { error: 'Invalid key format' },
        { status: 400, ok: false }
      );

      const response = await fetch(`${API_BASE}/keys`, {
        method: 'POST',
        body: JSON.stringify({
          provider: 'anthropic',
          key: 'invalid-key'
        })
      });

      expect(response.ok).toBe(false);
      expect(response.status).toBe(400);
    });
  });

  describe('Error Handling', () => {
    test('should handle network errors', async () => {
      fetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(
        fetch(`${API_BASE}/validate`)
      ).rejects.toThrow('Network error');
    });

    test('should handle 404 errors', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: () => Promise.resolve({ error: 'Endpoint not found' })
      });

      const response = await fetch(`${API_BASE}/unknown-endpoint`);
      expect(response.status).toBe(404);
      expect(response.ok).toBe(false);
    });

    test('should handle 500 errors', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: () => Promise.resolve({ error: 'Server error' })
      });

      const response = await fetch(`${API_BASE}/validate`);
      expect(response.status).toBe(500);
    });

    test('should handle malformed JSON responses', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.reject(new Error('Invalid JSON'))
      });

      const response = await fetch(`${API_BASE}/data`);
      await expect(response.json()).rejects.toThrow('Invalid JSON');
    });
  });

  describe('Request Headers', () => {
    test('should include correct content-type for JSON', async () => {
      mockApiResponse({});

      await fetch(`${API_BASE}/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ data: 'test' })
      });

      expect(fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          })
        })
      );
    });

    test('should include custom headers', async () => {
      mockApiResponse({});

      await fetch(`${API_BASE}/endpoint`, {
        headers: {
          'X-Custom-Header': 'test-value',
          'Authorization': 'Bearer token'
        }
      });

      expect(fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'X-Custom-Header': 'test-value',
            'Authorization': 'Bearer token'
          })
        })
      );
    });
  });
});
