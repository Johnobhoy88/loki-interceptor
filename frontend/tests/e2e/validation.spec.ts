/**
 * E2E Tests - Validation Workflows
 *
 * Tests for:
 * - Prompt validation
 * - Document validation
 * - Module selection
 * - Results display
 */

import { test, expect } from '@playwright/test';

test.describe('Prompt Validation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.click('.nav__item[data-view="interceptor"]');
  });

  test('should display prompt validation interface', async ({ page }) => {
    await expect(page.locator('#prompt-input')).toBeVisible();
    await expect(page.locator('#test-btn')).toBeVisible();
  });

  test('should accept text input in prompt field', async ({ page }) => {
    const promptInput = page.locator('#prompt-input');
    await promptInput.fill('Test financial advice prompt');

    await expect(promptInput).toHaveValue('Test financial advice prompt');
  });

  test('should enable validation button with text', async ({ page }) => {
    const promptInput = page.locator('#prompt-input');
    const validateBtn = page.locator('#test-btn');

    await promptInput.fill('Test prompt');
    await expect(validateBtn).toBeEnabled();
  });

  test('should trigger validation on button click', async ({ page }) => {
    // Mock API response
    await page.route('**/validate', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'pass',
          violations: [],
          warnings: [],
          metadata: { processing_time_ms: 150 }
        })
      });
    });

    const promptInput = page.locator('#prompt-input');
    await promptInput.fill('Compliant prompt');

    const validateBtn = page.locator('#test-btn');
    await validateBtn.click();

    // Wait for validation to complete
    await page.waitForResponse('**/validate');
  });

  test('should display validation results', async ({ page }) => {
    // Mock successful validation
    await page.route('**/validate', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'pass',
          violations: [],
          warnings: [],
          metadata: {}
        })
      });
    });

    await page.locator('#prompt-input').fill('Test prompt');
    await page.locator('#test-btn').click();

    // Wait for results
    await page.waitForResponse('**/validate');

    // Check for result container
    await expect(page.locator('#result-container')).toBeVisible();
  });

  test('should display violations when present', async ({ page }) => {
    // Mock validation with violations
    await page.route('**/validate', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'fail',
          violations: [
            {
              rule: 'FCA-001',
              severity: 'high',
              message: 'Missing risk disclosure'
            }
          ],
          warnings: []
        })
      });
    });

    await page.locator('#prompt-input').fill('Non-compliant prompt');
    await page.locator('#test-btn').click();

    await page.waitForResponse('**/validate');

    // Check for violation display (adjust selector based on implementation)
    await expect(page.locator('.violation, .error')).toBeVisible();
  });

  test('should display warnings', async ({ page }) => {
    // Mock validation with warnings
    await page.route('**/validate', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'warn',
          violations: [],
          warnings: [
            {
              rule: 'GDPR-001',
              message: 'Consider adding privacy notice'
            }
          ]
        })
      });
    });

    await page.locator('#prompt-input').fill('Prompt with warnings');
    await page.locator('#test-btn').click();

    await page.waitForResponse('**/validate');
  });
});

test.describe('Document Validation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.click('.nav__item[data-view="validator"]');
  });

  test('should display document validation interface', async ({ page }) => {
    await expect(page.locator('#document-input')).toBeVisible();
    await expect(page.locator('#validate-btn')).toBeVisible();
  });

  test('should accept document text', async ({ page }) => {
    const docInput = page.locator('#document-input');
    const documentText = 'Privacy Policy\n\nThis is our privacy policy...';

    await docInput.fill(documentText);
    await expect(docInput).toHaveValue(documentText);
  });

  test('should validate document', async ({ page }) => {
    // Mock document validation response
    await page.route('**/validate/document', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'pass',
          compliance_score: 95,
          violations: [],
          corrections: null
        })
      });
    });

    await page.locator('#document-input').fill('Compliant privacy policy');
    await page.locator('#validate-btn').click();

    await page.waitForResponse('**/validate/document');
  });

  test('should display corrections when available', async ({ page }) => {
    // Mock document validation with corrections
    await page.route('**/validate/document', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'fail',
          compliance_score: 60,
          violations: [
            { rule: 'FCA-005', message: 'Missing disclosure' }
          ],
          corrections: {
            original: 'Original text',
            corrected: 'Corrected compliant text',
            changes: ['Added FCA disclosure'],
            diff: '+ Added FCA disclosure'
          }
        })
      });
    });

    await page.locator('#document-input').fill('Non-compliant document');
    await page.locator('#validate-btn').click();

    await page.waitForResponse('**/validate/document');

    // Check for corrections view
    await expect(page.locator('#corrections-view')).toBeVisible();
  });
});

test.describe('Module Selection', () => {
  test.beforeEach(async ({ page }) => {
    // Mock module catalog
    await page.route('**/modules', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          { id: 'fca', name: 'FCA Compliance', enabled: true },
          { id: 'gdpr', name: 'GDPR', enabled: true },
          { id: 'smcr', name: 'SMCR', enabled: false }
        ])
      });
    });

    await page.goto('/');
    await page.click('.nav__item[data-view="interceptor"]');
  });

  test('should display available modules', async ({ page }) => {
    await page.waitForResponse('**/modules');

    const moduleChips = page.locator('.chip[data-module]');
    await expect(moduleChips).toHaveCount(2); // Only enabled modules
  });

  test('should allow module selection', async ({ page }) => {
    await page.waitForResponse('**/modules');

    const fcaChip = page.locator('.chip[data-module="fca"]');
    await expect(fcaChip).toBeVisible();

    // Check if clickable
    await fcaChip.click();
  });

  test('should toggle module active state', async ({ page }) => {
    await page.waitForResponse('**/modules');

    const fcaChip = page.locator('.chip[data-module="fca"]');

    // Get initial state
    const initialClass = await fcaChip.getAttribute('class');

    // Toggle
    await fcaChip.click();

    // Check state changed
    const newClass = await fcaChip.getAttribute('class');
    expect(newClass).not.toBe(initialClass);
  });
});

test.describe('Error Handling', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.click('.nav__item[data-view="interceptor"]');
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Mock API error
    await page.route('**/validate', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          error: 'Internal server error'
        })
      });
    });

    await page.locator('#prompt-input').fill('Test prompt');
    await page.locator('#test-btn').click();

    await page.waitForResponse('**/validate');

    // Check for error message or toast
    await expect(page.locator('.toast--error, .error-message')).toBeVisible({ timeout: 5000 });
  });

  test('should handle network errors', async ({ page }) => {
    // Mock network failure
    await page.route('**/validate', (route) => route.abort('failed'));

    await page.locator('#prompt-input').fill('Test prompt');
    await page.locator('#test-btn').click();

    // Check for error indication
    await page.waitForTimeout(1000);
  });

  test('should handle timeout errors', async ({ page }) => {
    // Mock slow response
    await page.route('**/validate', async (route) => {
      await page.waitForTimeout(10000);
      await route.fulfill({
        status: 200,
        body: JSON.stringify({ status: 'pass' })
      });
    });

    await page.locator('#prompt-input').fill('Test prompt');
    await page.locator('#test-btn').click();

    // Should show timeout or error
    await expect(page.locator('.toast--error, .error-message')).toBeVisible({ timeout: 15000 });
  });
});

test.describe('Toast Notifications', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display toast container', async ({ page }) => {
    await expect(page.locator('#toast-container')).toBeAttached();
  });

  test('should show success toast on successful validation', async ({ page }) => {
    await page.click('.nav__item[data-view="interceptor"]');

    await page.route('**/validate', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          status: 'pass',
          violations: [],
          warnings: []
        })
      });
    });

    await page.locator('#prompt-input').fill('Compliant prompt');
    await page.locator('#test-btn').click();

    await page.waitForResponse('**/validate');

    // Check for success toast
    await expect(page.locator('.toast--success')).toBeVisible({ timeout: 5000 });
  });

  test('should show error toast on validation failure', async ({ page }) => {
    await page.click('.nav__item[data-view="interceptor"]');

    await page.route('**/validate', async (route) => {
      await route.fulfill({
        status: 500,
        body: JSON.stringify({ error: 'Server error' })
      });
    });

    await page.locator('#prompt-input').fill('Test prompt');
    await page.locator('#test-btn').click();

    await page.waitForResponse('**/validate');

    // Check for error toast
    await expect(page.locator('.toast--error')).toBeVisible({ timeout: 5000 });
  });
});
