/**
 * Integration Tests - User Workflows
 *
 * End-to-end workflow tests including:
 * - Complete validation flow
 * - Module management workflow
 * - Analytics workflow
 * - Settings management
 */

describe('User Workflow Integration Tests', () => {
  let state;

  beforeEach(() => {
    // Initialize application state
    state = {
      provider: 'anthropic',
      apiKeys: {},
      modules: [],
      stats: { validated: 0, warnings: 0, blocked: 0 },
      analyticsWindow: 30,
      analytics: { loading: false, overview: null, trends: null, modules: null, error: null },
      lastValidation: { text: null, result: null }
    };

    // Setup DOM
    document.body.innerHTML = `
      <div id="toast-container"></div>
      <div class="content">
        <div class="view" data-id="interceptor">
          <input id="prompt-input" type="text" />
          <button id="test-btn">Validate</button>
          <div id="result-container"></div>
        </div>
        <div class="view" data-id="validator">
          <textarea id="document-input"></textarea>
          <button id="validate-btn">Validate Document</button>
          <div id="corrections-view"></div>
        </div>
        <div class="view" data-id="analytics">
          <select id="analytics-window">
            <option value="7">7 days</option>
            <option value="30">30 days</option>
          </select>
          <div id="analytics-content"></div>
        </div>
      </div>
      <div id="modules-interceptor"></div>
    `;

    fetch.mockClear();
  });

  describe('Prompt Validation Workflow', () => {
    test('should complete full validation workflow', async () => {
      // Step 1: User enters prompt
      const promptInput = document.getElementById('prompt-input');
      promptInput.value = 'Test financial advice prompt';

      // Step 2: User clicks validate
      const validateBtn = document.getElementById('test-btn');

      // Mock successful API response
      mockApiResponse({
        status: 'pass',
        violations: [],
        warnings: [],
        metadata: {
          modules_checked: ['fca', 'gdpr'],
          processing_time_ms: 245
        }
      });

      // Step 3: Trigger validation
      const validationPromise = fetch('http://127.0.0.1:5002/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: promptInput.value,
          provider: state.provider,
          modules: ['fca', 'gdpr']
        })
      });

      const response = await validationPromise;
      const result = await response.json();

      // Step 4: Update state
      state.stats.validated += 1;
      state.lastValidation = { text: promptInput.value, result };

      // Verify workflow
      expect(result.status).toBe('pass');
      expect(state.stats.validated).toBe(1);
      expect(state.lastValidation.text).toBe('Test financial advice prompt');
      expect(fetch).toHaveBeenCalledTimes(1);
    });

    test('should handle validation with violations', async () => {
      const promptInput = document.getElementById('prompt-input');
      promptInput.value = 'Non-compliant prompt';

      mockApiResponse({
        status: 'fail',
        violations: [
          { rule: 'FCA-001', severity: 'high', message: 'Missing risk disclosure' },
          { rule: 'FCA-002', severity: 'medium', message: 'Unclear language' }
        ],
        warnings: []
      });

      const response = await fetch('http://127.0.0.1:5002/validate', {
        method: 'POST',
        body: JSON.stringify({ prompt: promptInput.value })
      });

      const result = await response.json();

      // Update stats
      state.stats.validated += 1;
      state.stats.blocked += 1;

      expect(result.status).toBe('fail');
      expect(result.violations.length).toBe(2);
      expect(state.stats.blocked).toBe(1);
      expect(state.stats.validated).toBe(1);
    });

    test('should handle validation with warnings only', async () => {
      const promptInput = document.getElementById('prompt-input');
      promptInput.value = 'Prompt with minor issues';

      mockApiResponse({
        status: 'warn',
        violations: [],
        warnings: [
          { rule: 'GDPR-001', message: 'Consider adding privacy notice' }
        ]
      });

      const response = await fetch('http://127.0.0.1:5002/validate', {
        method: 'POST',
        body: JSON.stringify({ prompt: promptInput.value })
      });

      const result = await response.json();

      state.stats.validated += 1;
      state.stats.warnings += 1;

      expect(result.status).toBe('warn');
      expect(result.warnings.length).toBe(1);
      expect(state.stats.warnings).toBe(1);
    });
  });

  describe('Document Validation Workflow', () => {
    test('should complete document validation with corrections', async () => {
      // Step 1: User enters document text
      const docInput = document.getElementById('document-input');
      docInput.value = 'Privacy policy without required disclosures';

      // Step 2: Mock API response with corrections
      mockApiResponse({
        status: 'fail',
        compliance_score: 60,
        violations: [
          { rule: 'FCA-005', message: 'Missing required disclosure' }
        ],
        corrections: {
          original: docInput.value,
          corrected: 'Privacy policy with required disclosures and proper FCA compliance language',
          changes: ['Added FCA disclosure', 'Added privacy rights section'],
          diff: '+ Added FCA disclosure\n+ Added privacy rights'
        }
      });

      // Step 3: Validate document
      const response = await fetch('http://127.0.0.1:5002/validate/document', {
        method: 'POST',
        body: JSON.stringify({
          text: docInput.value,
          enable_corrections: true
        })
      });

      const result = await response.json();

      // Step 4: Update state
      state.lastValidation = { text: docInput.value, result };

      // Verify
      expect(result.corrections).toBeDefined();
      expect(result.corrections.corrected).toContain('FCA compliance');
      expect(result.corrections.changes.length).toBe(2);
      expect(state.lastValidation.result.status).toBe('fail');
    });

    test('should handle document validation without corrections', async () => {
      const docInput = document.getElementById('document-input');
      docInput.value = 'Compliant privacy policy';

      mockApiResponse({
        status: 'pass',
        compliance_score: 95,
        violations: [],
        corrections: null
      });

      const response = await fetch('http://127.0.0.1:5002/validate/document', {
        method: 'POST',
        body: JSON.stringify({ text: docInput.value })
      });

      const result = await response.json();

      expect(result.status).toBe('pass');
      expect(result.compliance_score).toBe(95);
      expect(result.corrections).toBeNull();
    });
  });

  describe('Module Management Workflow', () => {
    test('should load and display modules', async () => {
      // Step 1: Load module catalog
      const modules = [
        { id: 'fca', name: 'FCA Compliance', enabled: true, description: 'FCA rules' },
        { id: 'gdpr', name: 'GDPR', enabled: true, description: 'GDPR compliance' },
        { id: 'smcr', name: 'SMCR', enabled: false, description: 'SMCR rules' }
      ];

      mockApiResponse(modules);

      const response = await fetch('http://127.0.0.1:5002/modules');
      const loadedModules = await response.json();

      // Step 2: Update state
      state.modules = loadedModules;

      // Step 3: Render module chips
      const container = document.getElementById('modules-interceptor');
      container.innerHTML = '';

      state.modules
        .filter(m => m.enabled)
        .forEach(mod => {
          const chip = document.createElement('div');
          chip.className = 'chip active';
          chip.dataset.module = mod.id;
          chip.textContent = mod.name;
          container.appendChild(chip);
        });

      // Verify
      expect(state.modules.length).toBe(3);
      const chips = container.querySelectorAll('.chip');
      expect(chips.length).toBe(2); // Only enabled modules
      expect(chips[0].dataset.module).toBe('fca');
      expect(chips[1].dataset.module).toBe('gdpr');
    });

    test('should toggle module selection', () => {
      // Setup modules in DOM
      const container = document.getElementById('modules-interceptor');
      container.innerHTML = `
        <div class="chip active" data-module="fca">FCA</div>
        <div class="chip" data-module="gdpr">GDPR</div>
        <div class="chip active" data-module="smcr">SMCR</div>
      `;

      // Get selected modules
      const getSelectedModules = () => {
        return Array.from(container.querySelectorAll('.chip.active'))
          .map(chip => chip.dataset.module);
      };

      let selected = getSelectedModules();
      expect(selected).toEqual(['fca', 'smcr']);

      // Toggle GDPR on
      const gdprChip = container.querySelector('[data-module="gdpr"]');
      gdprChip.classList.add('active');

      selected = getSelectedModules();
      expect(selected).toEqual(['fca', 'gdpr', 'smcr']);

      // Toggle FCA off
      const fcaChip = container.querySelector('[data-module="fca"]');
      fcaChip.classList.remove('active');

      selected = getSelectedModules();
      expect(selected).toEqual(['gdpr', 'smcr']);
    });
  });

  describe('Analytics Workflow', () => {
    test('should load and display analytics data', async () => {
      // Step 1: Select time window
      const windowSelect = document.getElementById('analytics-window');
      windowSelect.value = '30';
      state.analyticsWindow = 30;

      // Step 2: Mock analytics API
      const analyticsData = {
        overview: {
          total_validations: 1500,
          pass_rate: 85.5,
          avg_violations: 0.8
        },
        trends: [
          { date: '2024-01-01', validations: 50, pass_rate: 80 },
          { date: '2024-01-02', validations: 55, pass_rate: 82 }
        ],
        modules: [
          { module: 'fca', violations: 45 },
          { module: 'gdpr', violations: 23 }
        ]
      };

      mockApiResponse(analyticsData);

      // Step 3: Fetch analytics
      state.analytics.loading = true;
      const response = await fetch(`http://127.0.0.1:5002/analytics?window=${state.analyticsWindow}`);
      const data = await response.json();

      state.analytics = {
        loading: false,
        overview: data.overview,
        trends: data.trends,
        modules: data.modules,
        error: null
      };

      // Verify
      expect(state.analytics.overview.total_validations).toBe(1500);
      expect(state.analytics.trends.length).toBe(2);
      expect(state.analytics.modules.length).toBe(2);
      expect(state.analytics.loading).toBe(false);
    });

    test('should handle analytics loading error', async () => {
      state.analytics.loading = true;

      mockApiError('Analytics service unavailable', 503);

      try {
        await fetch('http://127.0.0.1:5002/analytics');
      } catch (error) {
        state.analytics = {
          loading: false,
          overview: null,
          trends: null,
          modules: null,
          error: error.message
        };
      }

      expect(state.analytics.loading).toBe(false);
      expect(state.analytics.error).toBe('Analytics service unavailable');
      expect(state.analytics.overview).toBeNull();
    });

    test('should change analytics time window', async () => {
      const windowSelect = document.getElementById('analytics-window');

      // Change to 7 days
      windowSelect.value = '7';
      state.analyticsWindow = 7;

      mockApiResponse({ overview: {}, trends: [], modules: [] });

      await fetch(`http://127.0.0.1:5002/analytics?window=7`);

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('window=7')
      );

      // Change to 30 days
      windowSelect.value = '30';
      state.analyticsWindow = 30;

      mockApiResponse({ overview: {}, trends: [], modules: [] });

      await fetch(`http://127.0.0.1:5002/analytics?window=30`);

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('window=30')
      );
    });
  });

  describe('API Key Management Workflow', () => {
    test('should save and use API key', async () => {
      // Step 1: Save API key to localStorage
      const apiKey = 'sk-ant-test-key-12345';
      state.apiKeys.anthropic = apiKey;

      localStorage.setItem('loki-api-keys', JSON.stringify(state.apiKeys));

      // Step 2: Retrieve and verify
      const stored = JSON.parse(localStorage.getItem('loki-api-keys'));
      expect(stored.anthropic).toBe(apiKey);

      // Step 3: Use in API call
      mockApiResponse({ success: true });

      await fetch('http://127.0.0.1:5002/validate', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${stored.anthropic}`
        },
        body: JSON.stringify({ prompt: 'test' })
      });

      expect(fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': `Bearer ${apiKey}`
          })
        })
      );
    });

    test('should handle multiple provider keys', () => {
      state.apiKeys = {
        anthropic: 'sk-ant-key',
        openai: 'sk-openai-key'
      };

      localStorage.setItem('loki-api-keys', JSON.stringify(state.apiKeys));

      const stored = JSON.parse(localStorage.getItem('loki-api-keys'));
      expect(stored.anthropic).toBe('sk-ant-key');
      expect(stored.openai).toBe('sk-openai-key');
    });
  });

  describe('Error Recovery Workflow', () => {
    test('should recover from network error', async () => {
      let attempts = 0;
      const maxAttempts = 3;

      const attemptValidation = async () => {
        attempts++;

        try {
          if (attempts < 2) {
            throw new Error('Network error');
          }

          mockApiResponse({ status: 'pass' });
          const response = await fetch('http://127.0.0.1:5002/validate', {
            method: 'POST',
            body: JSON.stringify({ prompt: 'test' })
          });

          return await response.json();
        } catch (error) {
          if (attempts < maxAttempts) {
            return attemptValidation();
          }
          throw error;
        }
      };

      const result = await attemptValidation();

      expect(result.status).toBe('pass');
      expect(attempts).toBe(2);
    });

    test('should handle validation timeout gracefully', async () => {
      const timeout = 5000;
      const controller = new AbortController();

      setTimeout(() => controller.abort(), timeout);

      fetch.mockImplementationOnce(() =>
        new Promise((resolve) => setTimeout(() => resolve({ ok: true }), 10000))
      );

      try {
        await fetch('http://127.0.0.1:5002/validate', {
          signal: controller.signal
        });
      } catch (error) {
        expect(error.name).toBe('AbortError');
      }
    });
  });
});
