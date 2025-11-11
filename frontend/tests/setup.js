/**
 * Jest Test Setup
 *
 * Global configuration and setup for all test suites
 * Runs before each test file
 */

import '@testing-library/jest-dom';

// Mock fetch globally
global.fetch = jest.fn();

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
  length: 0,
  key: jest.fn()
};
global.localStorage = localStorageMock;

// Mock sessionStorage
global.sessionStorage = localStorageMock;

// Mock console methods to reduce noise in tests
global.console = {
  ...console,
  error: jest.fn(),
  warn: jest.fn(),
  log: jest.fn(),
  info: jest.fn(),
  debug: jest.fn()
};

// Setup DOM environment
beforeEach(() => {
  // Reset DOM
  document.body.innerHTML = '';

  // Reset mocks
  jest.clearAllMocks();
  fetch.mockClear();
  localStorage.getItem.mockClear();
  localStorage.setItem.mockClear();
  localStorage.removeItem.mockClear();
  localStorage.clear.mockClear();

  // Reset fetch default implementation
  fetch.mockImplementation(() =>
    Promise.resolve({
      ok: true,
      json: () => Promise.resolve({}),
      text: () => Promise.resolve(''),
      status: 200,
      statusText: 'OK'
    })
  );
});

// Cleanup after each test
afterEach(() => {
  // Clean up any remaining timers
  jest.clearAllTimers();

  // Clean up DOM
  document.body.innerHTML = '';
});

// Global test utilities
global.waitFor = (callback, options = {}) => {
  const { timeout = 3000, interval = 50 } = options;
  return new Promise((resolve, reject) => {
    const startTime = Date.now();

    const check = () => {
      try {
        const result = callback();
        if (result) {
          resolve(result);
        } else if (Date.now() - startTime > timeout) {
          reject(new Error('Timeout waiting for condition'));
        } else {
          setTimeout(check, interval);
        }
      } catch (error) {
        if (Date.now() - startTime > timeout) {
          reject(error);
        } else {
          setTimeout(check, interval);
        }
      }
    };

    check();
  });
};

// Mock API responses helper
global.mockApiResponse = (data, options = {}) => {
  const { status = 200, ok = true, statusText = 'OK' } = options;

  fetch.mockResolvedValueOnce({
    ok,
    status,
    statusText,
    json: () => Promise.resolve(data),
    text: () => Promise.resolve(JSON.stringify(data))
  });
};

// Mock API error helper
global.mockApiError = (error, status = 500) => {
  fetch.mockRejectedValueOnce(
    new Error(error)
  );
};

// Performance timing mock
if (!window.performance) {
  window.performance = {
    now: () => Date.now(),
    timing: {
      navigationStart: Date.now()
    }
  };
}

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
  takeRecords() {
    return [];
  }
};

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Suppress specific warnings in tests
const originalError = console.error;
beforeAll(() => {
  console.error = (...args) => {
    if (
      typeof args[0] === 'string' &&
      (args[0].includes('Warning: ReactDOM.render') ||
       args[0].includes('Not implemented: HTMLFormElement.prototype.submit'))
    ) {
      return;
    }
    originalError.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
});
