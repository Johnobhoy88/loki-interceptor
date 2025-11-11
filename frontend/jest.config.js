/**
 * Jest Configuration for LOKI Interceptor Frontend Testing
 *
 * Configured for vanilla JavaScript with DOM testing
 * Targets: 80%+ code coverage across all metrics
 */

export default {
  // Use jsdom to simulate browser environment
  testEnvironment: 'jsdom',

  // Setup files to run before tests
  setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],

  // Test match patterns
  testMatch: [
    '**/tests/**/*.test.js',
    '**/tests/**/*.spec.js'
  ],

  // Coverage configuration
  collectCoverage: false, // Enable with --coverage flag
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html', 'json-summary'],

  // Coverage thresholds - enforce 80%+ coverage
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },

  // Files to collect coverage from
  collectCoverageFrom: [
    'app.js',
    'app-web.js',
    '!**/*.config.js',
    '!**/node_modules/**',
    '!**/tests/**',
    '!**/coverage/**',
    '!**/dist/**'
  ],

  // Transform files (for ES modules if needed)
  transform: {},

  // Module paths
  moduleDirectories: ['node_modules', '<rootDir>'],

  // Test timeout
  testTimeout: 10000,

  // Verbose output
  verbose: true,

  // Clear mocks between tests
  clearMocks: true,
  resetMocks: true,
  restoreMocks: true,

  // Global setup/teardown
  globalSetup: undefined,
  globalTeardown: undefined,

  // Error on deprecated APIs
  errorOnDeprecated: true,

  // Detect open handles
  detectOpenHandles: true,

  // Force exit after tests complete
  forceExit: false,

  // Maximum worker configuration for CI
  maxWorkers: '50%',

  // Coverage path ignore patterns
  coveragePathIgnorePatterns: [
    '/node_modules/',
    '/tests/',
    '/coverage/',
    '/.github/',
    '/dist/'
  ],

  // Module file extensions
  moduleFileExtensions: ['js', 'json', 'html'],

  // Notify on completion (useful for watch mode)
  notify: false,
  notifyMode: 'failure-change',

  // Bail after first test failure (useful for CI)
  bail: false,

  // Display individual test results
  displayName: {
    name: 'LOKI Frontend',
    color: 'blue'
  }
};
