/**
 * Playwright Configuration for LOKI Interceptor E2E Testing
 *
 * Comprehensive E2E testing configuration with:
 * - Multiple browser support
 * - Parallel execution
 * - Screenshots and videos on failure
 * - Trace on failure
 */

import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  // Test directory
  testDir: './tests/e2e',

  // Maximum time one test can run
  timeout: 30 * 1000,

  // Fail the build on CI if you accidentally left test.only in the source code
  forbidOnly: !!process.env.CI,

  // Retry on CI only
  retries: process.env.CI ? 2 : 0,

  // Opt out of parallel tests on CI
  workers: process.env.CI ? 1 : undefined,

  // Reporter to use
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'playwright-report/results.json' }],
    ['junit', { outputFile: 'playwright-report/results.xml' }],
    ['list']
  ],

  // Shared settings for all projects
  use: {
    // Base URL to use in actions like `await page.goto('/')`
    baseURL: process.env.BASE_URL || 'http://localhost:8080',

    // Collect trace on failure
    trace: 'on-first-retry',

    // Screenshot on failure
    screenshot: 'only-on-failure',

    // Video on failure
    video: 'retain-on-failure',

    // Maximum time each action can take
    actionTimeout: 10 * 1000,

    // Navigation timeout
    navigationTimeout: 30 * 1000,

    // Ignore HTTPS errors
    ignoreHTTPSErrors: true,

    // Viewport size
    viewport: { width: 1280, height: 720 },
  },

  // Configure projects for major browsers
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },

    // Mobile viewports
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },

    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 12'] },
    },

    // Tablet viewports
    {
      name: 'tablet',
      use: { ...devices['iPad Pro'] },
    },
  ],

  // Run local dev server before starting tests
  webServer: {
    command: 'npm run serve',
    url: 'http://localhost:8080',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },

  // Global setup/teardown
  globalSetup: undefined,
  globalTeardown: undefined,

  // Folder for test artifacts
  outputDir: 'test-results/',

  // Whether to preserve output between runs
  preserveOutput: 'always',

  // Fail fast on first failure (useful for quick feedback)
  fullyParallel: !process.env.CI,

  // Expect defaults
  expect: {
    // Maximum time expect() should wait for the condition to be met
    timeout: 5000,

    toHaveScreenshot: {
      // Maximum time to wait for screenshot comparison
      maxDiffPixels: 100,
      maxDiffPixelRatio: 0.1,
    },
  },
});
