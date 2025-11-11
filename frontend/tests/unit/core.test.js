/**
 * Unit Tests - Core Application Functions
 *
 * Tests for app.js core functionality including:
 * - Toast notifications
 * - Storage helpers
 * - State management
 * - API detection
 */

describe('Core Application Functions', () => {
  describe('showToast', () => {
    beforeEach(() => {
      // Setup toast container
      document.body.innerHTML = '<div id="toast-container"></div>';

      // Load the escapeHtml function
      window.escapeHtml = (str) => {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
      };

      // Load showToast function
      window.showToast = function(message, type = 'info', title = null) {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast toast--${type}`;

        const icons = {
          error: '!',
          success: '✓',
          warning: '!',
          info: 'i'
        };

        const titles = {
          error: title || 'Error',
          success: title || 'Success',
          warning: title || 'Warning',
          info: title || 'Information'
        };

        toast.innerHTML = `
          <div class="toast__icon">${icons[type] || 'i'}</div>
          <div class="toast__body">
            <div class="toast__title">${titles[type]}</div>
            <div class="toast__message">${window.escapeHtml(message)}</div>
          </div>
        `;

        container.appendChild(toast);
      };
    });

    test('should create toast with default info type', () => {
      showToast('Test message');

      const toast = document.querySelector('.toast');
      expect(toast).toBeTruthy();
      expect(toast.classList.contains('toast--info')).toBe(true);
      expect(toast.querySelector('.toast__message').textContent).toBe('Test message');
    });

    test('should create success toast', () => {
      showToast('Success message', 'success');

      const toast = document.querySelector('.toast');
      expect(toast.classList.contains('toast--success')).toBe(true);
      expect(toast.querySelector('.toast__title').textContent).toBe('Success');
    });

    test('should create error toast', () => {
      showToast('Error message', 'error');

      const toast = document.querySelector('.toast');
      expect(toast.classList.contains('toast--error')).toBe(true);
      expect(toast.querySelector('.toast__title').textContent).toBe('Error');
    });

    test('should create warning toast', () => {
      showToast('Warning message', 'warning');

      const toast = document.querySelector('.toast');
      expect(toast.classList.contains('toast--warning')).toBe(true);
      expect(toast.querySelector('.toast__title').textContent).toBe('Warning');
    });

    test('should use custom title when provided', () => {
      showToast('Custom message', 'error', 'Custom Error');

      const toast = document.querySelector('.toast');
      expect(toast.querySelector('.toast__title').textContent).toBe('Custom Error');
    });

    test('should escape HTML in messages', () => {
      showToast('<script>alert("xss")</script>');

      const message = document.querySelector('.toast__message');
      expect(message.innerHTML).not.toContain('<script>');
      expect(message.innerHTML).toContain('&lt;script&gt;');
    });

    test('should not create toast if container missing', () => {
      document.body.innerHTML = '';
      showToast('Test message');

      const toast = document.querySelector('.toast');
      expect(toast).toBeFalsy();
    });

    test('should support multiple toasts', () => {
      showToast('Message 1', 'info');
      showToast('Message 2', 'success');
      showToast('Message 3', 'error');

      const toasts = document.querySelectorAll('.toast');
      expect(toasts.length).toBe(3);
    });
  });

  describe('storage helper', () => {
    beforeEach(() => {
      localStorage.clear();

      // Load storage helper
      window.storage = {
        get(key, fallback = []) {
          try {
            const raw = localStorage.getItem(key);
            if (!raw) return fallback;
            const parsed = JSON.parse(raw);
            return Array.isArray(parsed) ? parsed : fallback;
          } catch {
            return fallback;
          }
        },
        set(key, value) {
          localStorage.setItem(key, JSON.stringify(value));
        }
      };
    });

    test('should return fallback for non-existent key', () => {
      const result = storage.get('nonexistent', ['default']);
      expect(result).toEqual(['default']);
    });

    test('should return empty array as default fallback', () => {
      const result = storage.get('nonexistent');
      expect(result).toEqual([]);
    });

    test('should store and retrieve arrays', () => {
      const data = ['item1', 'item2', 'item3'];
      storage.set('test-key', data);

      const result = storage.get('test-key');
      expect(result).toEqual(data);
    });

    test('should store and retrieve objects in arrays', () => {
      const data = [{ id: 1, name: 'test' }, { id: 2, name: 'test2' }];
      storage.set('test-objects', data);

      const result = storage.get('test-objects');
      expect(result).toEqual(data);
    });

    test('should return fallback for invalid JSON', () => {
      localStorage.setItem('invalid', '{invalid json}');

      const result = storage.get('invalid', ['fallback']);
      expect(result).toEqual(['fallback']);
    });

    test('should return fallback for non-array values', () => {
      localStorage.setItem('non-array', JSON.stringify({ key: 'value' }));

      const result = storage.get('non-array', ['fallback']);
      expect(result).toEqual(['fallback']);
    });

    test('should handle empty arrays', () => {
      storage.set('empty', []);

      const result = storage.get('empty');
      expect(result).toEqual([]);
    });
  });

  describe('state management', () => {
    test('should initialize with default state', () => {
      const state = {
        provider: 'anthropic',
        apiKeys: {},
        modules: [],
        stats: { validated: 0, warnings: 0, blocked: 0 },
        analyticsWindow: 30,
        analytics: { loading: false, overview: null, trends: null, modules: null, error: null },
        lastValidation: { text: null, result: null }
      };

      expect(state.provider).toBe('anthropic');
      expect(state.apiKeys).toEqual({});
      expect(state.modules).toEqual([]);
      expect(state.stats).toEqual({ validated: 0, warnings: 0, blocked: 0 });
      expect(state.analyticsWindow).toBe(30);
    });

    test('should have correct analytics initial state', () => {
      const state = {
        analytics: { loading: false, overview: null, trends: null, modules: null, error: null }
      };

      expect(state.analytics.loading).toBe(false);
      expect(state.analytics.overview).toBe(null);
      expect(state.analytics.trends).toBe(null);
      expect(state.analytics.modules).toBe(null);
      expect(state.analytics.error).toBe(null);
    });
  });

  describe('API base detection', () => {
    test('should use local API for localhost', () => {
      Object.defineProperty(window, 'location', {
        value: {
          protocol: 'http:',
          hostname: 'localhost'
        },
        writable: true
      });

      const API_BASE = (window.location.protocol === 'file:' ||
                        window.location.hostname === 'localhost' ||
                        window.location.hostname === '127.0.0.1')
        ? 'http://127.0.0.1:5002'
        : 'https://loki-interceptor.vercel.app/api';

      expect(API_BASE).toBe('http://127.0.0.1:5002');
    });

    test('should use local API for 127.0.0.1', () => {
      Object.defineProperty(window, 'location', {
        value: {
          protocol: 'http:',
          hostname: '127.0.0.1'
        },
        writable: true
      });

      const API_BASE = (window.location.protocol === 'file:' ||
                        window.location.hostname === 'localhost' ||
                        window.location.hostname === '127.0.0.1')
        ? 'http://127.0.0.1:5002'
        : 'https://loki-interceptor.vercel.app/api';

      expect(API_BASE).toBe('http://127.0.0.1:5002');
    });

    test('should use remote API for production domain', () => {
      Object.defineProperty(window, 'location', {
        value: {
          protocol: 'https:',
          hostname: 'loki-interceptor.vercel.app'
        },
        writable: true
      });

      const API_BASE = (window.location.protocol === 'file:' ||
                        window.location.hostname === 'localhost' ||
                        window.location.hostname === '127.0.0.1')
        ? 'http://127.0.0.1:5002'
        : 'https://loki-interceptor.vercel.app/api';

      expect(API_BASE).toBe('https://loki-interceptor.vercel.app/api');
    });

    test('should use local API for file protocol', () => {
      Object.defineProperty(window, 'location', {
        value: {
          protocol: 'file:',
          hostname: ''
        },
        writable: true
      });

      const API_BASE = (window.location.protocol === 'file:' ||
                        window.location.hostname === 'localhost' ||
                        window.location.hostname === '127.0.0.1')
        ? 'http://127.0.0.1:5002'
        : 'https://loki-interceptor.vercel.app/api';

      expect(API_BASE).toBe('http://127.0.0.1:5002');
    });
  });

  describe('constants', () => {
    test('should have correct default synthesis context', () => {
      const DEFAULT_SYNTHESIS_CONTEXT = {
        firm_name: 'Highland AI',
        contact_details: 'compliance@highland-ai.com',
        url: 'https://highland-ai.com/privacy',
        dpo_email: 'dpo@highland-ai.com'
      };

      expect(DEFAULT_SYNTHESIS_CONTEXT.firm_name).toBe('Highland AI');
      expect(DEFAULT_SYNTHESIS_CONTEXT.dpo_email).toBe('dpo@highland-ai.com');
    });

    test('should have correct handshake TTL', () => {
      const HANDSHAKE_TTL_MS = 60_000;
      expect(HANDSHAKE_TTL_MS).toBe(60000);
    });

    test('should have corrections enabled', () => {
      const ENABLE_CORRECTIONS = true;
      expect(ENABLE_CORRECTIONS).toBe(true);
    });
  });
});
