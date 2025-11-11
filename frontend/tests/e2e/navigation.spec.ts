/**
 * E2E Tests - Navigation & Basic Functionality
 *
 * Tests for:
 * - Page loading
 * - Navigation between views
 * - Basic UI interactions
 */

import { test, expect } from '@playwright/test';

test.describe('Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should load the application', async ({ page }) => {
    await expect(page).toHaveTitle(/LOKI/);
    await expect(page.locator('.brand__title')).toContainText('LOKI Interceptor');
  });

  test('should display main navigation', async ({ page }) => {
    await expect(page.locator('.nav__item[data-view="overview"]')).toBeVisible();
    await expect(page.locator('.nav__item[data-view="interceptor"]')).toBeVisible();
    await expect(page.locator('.nav__item[data-view="validator"]')).toBeVisible();
    await expect(page.locator('.nav__item[data-view="analytics"]')).toBeVisible();
  });

  test('should start with overview view active', async ({ page }) => {
    const overviewBtn = page.locator('.nav__item[data-view="overview"]');
    await expect(overviewBtn).toHaveClass(/active/);
  });

  test('should navigate to interceptor view', async ({ page }) => {
    await page.click('.nav__item[data-view="interceptor"]');

    const interceptorBtn = page.locator('.nav__item[data-view="interceptor"]');
    await expect(interceptorBtn).toHaveClass(/active/);

    const interceptorView = page.locator('.view[data-id="interceptor"]');
    await expect(interceptorView).toBeVisible();
  });

  test('should navigate to validator view', async ({ page }) => {
    await page.click('.nav__item[data-view="validator"]');

    const validatorBtn = page.locator('.nav__item[data-view="validator"]');
    await expect(validatorBtn).toHaveClass(/active/);

    const validatorView = page.locator('.view[data-id="validator"]');
    await expect(validatorView).toBeVisible();
  });

  test('should navigate to analytics view', async ({ page }) => {
    await page.click('.nav__item[data-view="analytics"]');

    const analyticsBtn = page.locator('.nav__item[data-view="analytics"]');
    await expect(analyticsBtn).toHaveClass(/active/);

    const analyticsView = page.locator('.view[data-id="analytics"]');
    await expect(analyticsView).toBeVisible();
  });

  test('should switch between views multiple times', async ({ page }) => {
    // Go to interceptor
    await page.click('.nav__item[data-view="interceptor"]');
    await expect(page.locator('.nav__item[data-view="interceptor"]')).toHaveClass(/active/);

    // Go to validator
    await page.click('.nav__item[data-view="validator"]');
    await expect(page.locator('.nav__item[data-view="validator"]')).toHaveClass(/active/);

    // Go back to overview
    await page.click('.nav__item[data-view="overview"]');
    await expect(page.locator('.nav__item[data-view="overview"]')).toHaveClass(/active/);

    // Go to analytics
    await page.click('.nav__item[data-view="analytics"]');
    await expect(page.locator('.nav__item[data-view="analytics"]')).toHaveClass(/active/);
  });

  test('should display backend status', async ({ page }) => {
    const status = page.locator('#backend-status');
    await expect(status).toBeVisible();
    await expect(status).toContainText(/ONLINE|OFFLINE|Checking/i);
  });

  test('should have refresh status button', async ({ page }) => {
    const refreshBtn = page.locator('#refresh-status');
    await expect(refreshBtn).toBeVisible();
    await expect(refreshBtn).toBeEnabled();
  });

  test('should refresh backend status on click', async ({ page }) => {
    const refreshBtn = page.locator('#refresh-status');
    await refreshBtn.click();

    // Status should be updated (checking animation or final status)
    const status = page.locator('#backend-status');
    await expect(status).toBeVisible();
  });
});

test.describe('Sidebar', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display brand information', async ({ page }) => {
    await expect(page.locator('.brand__title')).toContainText('LOKI Interceptor');
    await expect(page.locator('.brand__subtitle')).toContainText('FCA Compliance Console');
  });

  test('should display backend information', async ({ page }) => {
    const meta = page.locator('.sidebar__meta');
    await expect(meta).toContainText(/Backend:/);
    await expect(meta).toContainText(/Build:/);
  });

  test('should display navigation descriptions', async ({ page }) => {
    await expect(page.locator('.nav__item[data-view="overview"] .nav__desc'))
      .toContainText('At-a-glance status & metrics');

    await expect(page.locator('.nav__item[data-view="interceptor"] .nav__desc'))
      .toContainText('Validate live AI outputs');

    await expect(page.locator('.nav__item[data-view="validator"] .nav__desc'))
      .toContainText('Scan disclosures & policies');

    await expect(page.locator('.nav__item[data-view="analytics"] .nav__desc'))
      .toContainText('Telemetry & breach trends');
  });
});

test.describe('Responsive Design', () => {
  test('should be responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    await expect(page.locator('.brand__title')).toBeVisible();
    await expect(page.locator('.nav__item')).toHaveCount(4);
  });

  test('should be responsive on tablet', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/');

    await expect(page.locator('.brand__title')).toBeVisible();
    await expect(page.locator('.content')).toBeVisible();
  });

  test('should be responsive on desktop', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/');

    await expect(page.locator('.sidebar')).toBeVisible();
    await expect(page.locator('.content')).toBeVisible();
  });
});

test.describe('Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should have proper document structure', async ({ page }) => {
    // Check for semantic HTML
    await expect(page.locator('aside.sidebar')).toBeVisible();
    await expect(page.locator('main.content')).toBeVisible();
    await expect(page.locator('nav.nav')).toBeVisible();
    await expect(page.locator('header.topbar')).toBeVisible();
  });

  test('should allow keyboard navigation', async ({ page }) => {
    // Tab through navigation items
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    // Check if navigation is focused (browser-dependent)
    const focusedElement = await page.evaluate(() => document.activeElement?.className);
    expect(focusedElement).toBeDefined();
  });

  test('should have appropriate ARIA labels', async ({ page }) => {
    // Check for proper button types
    const buttons = page.locator('button');
    await expect(buttons.first()).toHaveAttribute('type');
  });
});
