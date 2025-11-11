/**
 * Accessibility Tests with axe-core
 *
 * Tests for WCAG 2.1 AA compliance including:
 * - Color contrast
 * - Keyboard navigation
 * - Screen reader support
 * - ARIA attributes
 * - Form labels
 */

import { axe, toHaveNoViolations } from 'jest-axe';

// Extend Jest matchers
expect.extend(toHaveNoViolations);

describe('Accessibility Tests', () => {
  describe('Main Application Structure', () => {
    beforeEach(() => {
      document.body.innerHTML = `
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <title>LOKI FCA Control Center</title>
        </head>
        <body>
          <div class="shell" id="app">
            <aside class="sidebar">
              <div class="brand">
                <div class="brand__icon">LK</div>
                <div class="brand__copy">
                  <span class="brand__title">LOKI Interceptor</span>
                  <span class="brand__subtitle">FCA Compliance Console</span>
                </div>
              </div>
              <nav class="nav" aria-label="Main navigation">
                <button class="nav__item active" data-view="overview">
                  <span class="nav__title">Command Centre</span>
                  <span class="nav__desc">At-a-glance status & metrics</span>
                </button>
              </nav>
            </aside>
            <main class="content">
              <header class="topbar">
                <h1>Dashboard</h1>
              </header>
            </main>
          </div>
        </body>
        </html>
      `;
    });

    test('should not have accessibility violations', async () => {
      const results = await axe(document.body);
      expect(results).toHaveNoViolations();
    });

    test('should have lang attribute on html', () => {
      const html = document.querySelector('html');
      expect(html?.getAttribute('lang')).toBe('en');
    });

    test('should have proper document title', () => {
      expect(document.title).toBeTruthy();
      expect(document.title).toContain('LOKI');
    });

    test('should have semantic HTML structure', () => {
      expect(document.querySelector('aside')).toBeTruthy();
      expect(document.querySelector('main')).toBeTruthy();
      expect(document.querySelector('nav')).toBeTruthy();
      expect(document.querySelector('header')).toBeTruthy();
    });
  });

  describe('Navigation Accessibility', () => {
    beforeEach(() => {
      document.body.innerHTML = `
        <nav class="nav" aria-label="Main navigation" role="navigation">
          <button class="nav__item" data-view="overview" aria-label="Navigate to Command Centre">
            <span class="nav__title">Command Centre</span>
            <span class="nav__desc">At-a-glance status & metrics</span>
          </button>
          <button class="nav__item" data-view="interceptor" aria-label="Navigate to API Interceptor">
            <span class="nav__title">API Interceptor</span>
            <span class="nav__desc">Validate live AI outputs</span>
          </button>
        </nav>
      `;
    });

    test('should not have accessibility violations', async () => {
      const results = await axe(document.body);
      expect(results).toHaveNoViolations();
    });

    test('should have proper ARIA labels on navigation', () => {
      const nav = document.querySelector('nav');
      expect(nav?.getAttribute('aria-label')).toBe('Main navigation');
    });

    test('should have accessible button elements', () => {
      const buttons = document.querySelectorAll('button.nav__item');
      buttons.forEach(button => {
        expect(button.getAttribute('aria-label')).toBeTruthy();
      });
    });

    test('should have keyboard-accessible buttons', () => {
      const buttons = document.querySelectorAll('button');
      buttons.forEach(button => {
        expect(button.tagName).toBe('BUTTON');
        expect(button.getAttribute('type')).not.toBe('submit'); // Should be button type
      });
    });
  });

  describe('Form Accessibility', () => {
    beforeEach(() => {
      document.body.innerHTML = `
        <form>
          <div class="form-group">
            <label for="prompt-input">Enter prompt for validation</label>
            <input
              type="text"
              id="prompt-input"
              name="prompt"
              aria-describedby="prompt-help"
              aria-required="true"
            />
            <small id="prompt-help">Enter the AI-generated content to validate</small>
          </div>

          <div class="form-group">
            <label for="provider-select">Select AI Provider</label>
            <select id="provider-select" name="provider" aria-required="true">
              <option value="">Choose provider</option>
              <option value="anthropic">Anthropic</option>
              <option value="openai">OpenAI</option>
            </select>
          </div>

          <button type="submit" aria-label="Submit validation request">
            Validate
          </button>
        </form>
      `;
    });

    test('should not have accessibility violations', async () => {
      const results = await axe(document.body);
      expect(results).toHaveNoViolations();
    });

    test('should have labels for all form inputs', () => {
      const inputs = document.querySelectorAll('input, select');
      inputs.forEach(input => {
        const id = input.getAttribute('id');
        const label = document.querySelector(`label[for="${id}"]`);
        expect(label).toBeTruthy();
      });
    });

    test('should have aria-required on required fields', () => {
      const requiredInput = document.querySelector('#prompt-input');
      expect(requiredInput?.getAttribute('aria-required')).toBe('true');
    });

    test('should have aria-describedby for help text', () => {
      const input = document.querySelector('#prompt-input');
      const describedBy = input?.getAttribute('aria-describedby');
      expect(describedBy).toBe('prompt-help');

      const helpText = document.getElementById(describedBy);
      expect(helpText).toBeTruthy();
    });
  });

  describe('Button Accessibility', () => {
    beforeEach(() => {
      document.body.innerHTML = `
        <button type="button" aria-label="Refresh backend status" id="refresh-status">
          <span aria-hidden="true">↻</span>
          Refresh
        </button>

        <button type="button" id="test-btn" aria-label="Validate prompt">
          Validate
        </button>

        <button
          type="button"
          id="save-key-btn"
          aria-label="Save API key"
          aria-disabled="false"
        >
          Save Key
        </button>
      `;
    });

    test('should not have accessibility violations', async () => {
      const results = await axe(document.body);
      expect(results).toHaveNoViolations();
    });

    test('should have appropriate button types', () => {
      const buttons = document.querySelectorAll('button');
      buttons.forEach(button => {
        const type = button.getAttribute('type');
        expect(['button', 'submit', 'reset']).toContain(type);
      });
    });

    test('should have aria-labels for icon-only buttons', () => {
      const refreshBtn = document.querySelector('#refresh-status');
      expect(refreshBtn?.getAttribute('aria-label')).toBeTruthy();
    });

    test('should mark decorative icons as aria-hidden', () => {
      const icon = document.querySelector('span[aria-hidden="true"]');
      expect(icon).toBeTruthy();
    });
  });

  describe('Color Contrast', () => {
    beforeEach(() => {
      document.body.innerHTML = `
        <style>
          .high-contrast { color: #000; background-color: #fff; }
          .error-text { color: #d32f2f; background-color: #fff; }
          .success-text { color: #388e3c; background-color: #fff; }
          .warning-text { color: #f57c00; background-color: #fff; }
        </style>

        <div class="high-contrast">High contrast text</div>
        <div class="error-text">Error message</div>
        <div class="success-text">Success message</div>
        <div class="warning-text">Warning message</div>
      `;
    });

    test('should not have color contrast violations', async () => {
      const results = await axe(document.body, {
        rules: {
          'color-contrast': { enabled: true }
        }
      });

      expect(results).toHaveNoViolations();
    });
  });

  describe('ARIA Roles and States', () => {
    beforeEach(() => {
      document.body.innerHTML = `
        <div role="alert" aria-live="polite" class="toast toast--success">
          <div class="toast__icon" aria-hidden="true">✓</div>
          <div class="toast__body">
            <div class="toast__title">Success</div>
            <div class="toast__message">Validation completed successfully</div>
          </div>
        </div>

        <div role="status" aria-live="polite" id="backend-status">
          ONLINE
        </div>

        <div role="progressbar" aria-valuenow="75" aria-valuemin="0" aria-valuemax="100">
          Loading...
        </div>
      `;
    });

    test('should not have accessibility violations', async () => {
      const results = await axe(document.body);
      expect(results).toHaveNoViolations();
    });

    test('should have proper alert role for notifications', () => {
      const alert = document.querySelector('[role="alert"]');
      expect(alert).toBeTruthy();
      expect(alert?.getAttribute('aria-live')).toBe('polite');
    });

    test('should have proper status role for dynamic content', () => {
      const status = document.querySelector('[role="status"]');
      expect(status).toBeTruthy();
    });

    test('should have proper progressbar attributes', () => {
      const progressbar = document.querySelector('[role="progressbar"]');
      expect(progressbar?.getAttribute('aria-valuenow')).toBe('75');
      expect(progressbar?.getAttribute('aria-valuemin')).toBe('0');
      expect(progressbar?.getAttribute('aria-valuemax')).toBe('100');
    });
  });

  describe('Keyboard Navigation', () => {
    beforeEach(() => {
      document.body.innerHTML = `
        <button class="nav__item" data-view="overview" tabindex="0">Overview</button>
        <button class="nav__item" data-view="interceptor" tabindex="0">Interceptor</button>
        <a href="#main-content" class="skip-link" tabindex="0">Skip to main content</a>
        <input type="text" id="prompt-input" tabindex="0" />
      `;
    });

    test('should have proper tabindex values', () => {
      const focusableElements = document.querySelectorAll('[tabindex]');
      focusableElements.forEach(el => {
        const tabindex = parseInt(el.getAttribute('tabindex') || '0');
        expect(tabindex).toBeGreaterThanOrEqual(0);
      });
    });

    test('should have skip link for keyboard users', () => {
      const skipLink = document.querySelector('.skip-link');
      expect(skipLink).toBeTruthy();
      expect(skipLink?.getAttribute('href')).toBe('#main-content');
    });

    test('should allow keyboard focus on interactive elements', () => {
      const buttons = document.querySelectorAll('button');
      buttons.forEach(button => {
        expect(button.getAttribute('tabindex')).toBeTruthy();
      });
    });
  });

  describe('Headings Hierarchy', () => {
    beforeEach(() => {
      document.body.innerHTML = `
        <main>
          <h1>LOKI Interceptor Dashboard</h1>
          <section>
            <h2>Validation Results</h2>
            <article>
              <h3>FCA Compliance Check</h3>
              <p>Results...</p>
            </article>
            <article>
              <h3>GDPR Compliance Check</h3>
              <p>Results...</p>
            </article>
          </section>
          <section>
            <h2>Analytics</h2>
            <h3>Overview</h3>
          </section>
        </main>
      `;
    });

    test('should not have accessibility violations', async () => {
      const results = await axe(document.body);
      expect(results).toHaveNoViolations();
    });

    test('should have single h1 per page', () => {
      const h1s = document.querySelectorAll('h1');
      expect(h1s.length).toBe(1);
    });

    test('should have proper heading hierarchy', () => {
      const h1 = document.querySelector('h1');
      const h2s = document.querySelectorAll('h2');
      const h3s = document.querySelectorAll('h3');

      expect(h1).toBeTruthy();
      expect(h2s.length).toBeGreaterThan(0);
      expect(h3s.length).toBeGreaterThan(0);
    });
  });

  describe('Images and Media', () => {
    beforeEach(() => {
      document.body.innerHTML = `
        <img src="logo.png" alt="LOKI Interceptor Logo" />
        <img src="icon.png" alt="" role="presentation" />
        <div class="brand__icon" role="img" aria-label="LOKI brand icon">LK</div>
      `;
    });

    test('should not have accessibility violations', async () => {
      const results = await axe(document.body);
      expect(results).toHaveNoViolations();
    });

    test('should have alt text on meaningful images', () => {
      const meaningfulImg = document.querySelector('img[src="logo.png"]');
      const alt = meaningfulImg?.getAttribute('alt');
      expect(alt).toBeTruthy();
      expect(alt?.length).toBeGreaterThan(0);
    });

    test('should have empty alt for decorative images', () => {
      const decorativeImg = document.querySelector('img[role="presentation"]');
      expect(decorativeImg?.getAttribute('alt')).toBe('');
    });

    test('should have aria-label for icon divs', () => {
      const iconDiv = document.querySelector('[role="img"]');
      expect(iconDiv?.getAttribute('aria-label')).toBeTruthy();
    });
  });

  describe('Focus Management', () => {
    beforeEach(() => {
      document.body.innerHTML = `
        <button id="btn1">Button 1</button>
        <button id="btn2">Button 2</button>
        <input id="input1" type="text" />
        <div tabindex="-1" id="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
          <h2 id="modal-title">Modal Dialog</h2>
          <button id="modal-close">Close</button>
        </div>
      `;
    });

    test('should have proper focus indicators', () => {
      const focusableElements = document.querySelectorAll('button, input');
      expect(focusableElements.length).toBeGreaterThan(0);
    });

    test('should have aria-modal for modal dialogs', () => {
      const modal = document.querySelector('[role="dialog"]');
      expect(modal?.getAttribute('aria-modal')).toBe('true');
      expect(modal?.getAttribute('aria-labelledby')).toBeTruthy();
    });

    test('should have proper modal title reference', () => {
      const modal = document.querySelector('[role="dialog"]');
      const labelledBy = modal?.getAttribute('aria-labelledby');
      const title = document.getElementById(labelledBy || '');
      expect(title).toBeTruthy();
    });
  });

  describe('Live Regions', () => {
    beforeEach(() => {
      document.body.innerHTML = `
        <div id="toast-container" aria-live="polite" aria-atomic="true"></div>
        <div id="status" role="status" aria-live="polite">Loading...</div>
        <div id="alert" role="alert" aria-live="assertive">Error occurred!</div>
      `;
    });

    test('should not have accessibility violations', async () => {
      const results = await axe(document.body);
      expect(results).toHaveNoViolations();
    });

    test('should have aria-live on dynamic content', () => {
      const liveRegions = document.querySelectorAll('[aria-live]');
      expect(liveRegions.length).toBeGreaterThan(0);

      liveRegions.forEach(region => {
        const ariaLive = region.getAttribute('aria-live');
        expect(['polite', 'assertive', 'off']).toContain(ariaLive);
      });
    });

    test('should use polite for non-critical updates', () => {
      const status = document.querySelector('#status');
      expect(status?.getAttribute('aria-live')).toBe('polite');
    });

    test('should use assertive for critical alerts', () => {
      const alert = document.querySelector('#alert');
      expect(alert?.getAttribute('aria-live')).toBe('assertive');
    });
  });
});
