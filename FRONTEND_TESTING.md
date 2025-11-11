# Frontend Testing Guide

## LOKI Interceptor Frontend Testing Framework

Comprehensive testing infrastructure for ensuring quality, performance, and reliability.

---

## Table of Contents

1. [Overview](#overview)
2. [Testing Stack](#testing-stack)
3. [Setup](#setup)
4. [Running Tests](#running-tests)
5. [Test Types](#test-types)
6. [Writing Tests](#writing-tests)
7. [Coverage Requirements](#coverage-requirements)
8. [CI/CD Integration](#cicd-integration)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The LOKI Interceptor frontend testing framework provides comprehensive coverage across:

- **Unit Tests**: Test individual functions and components
- **Integration Tests**: Test API interactions and workflows
- **E2E Tests**: Test complete user journeys with Playwright
- **Accessibility Tests**: WCAG 2.1 AA compliance with axe-core
- **Performance Tests**: Lighthouse CI and performance budgets

**Coverage Target**: 80%+ across all metrics (lines, branches, functions, statements)

---

## Testing Stack

### Core Testing Tools

| Tool | Purpose | Version |
|------|---------|---------|
| **Jest** | Unit & integration testing | ^29.7.0 |
| **Playwright** | E2E browser testing | ^1.40.1 |
| **@testing-library/dom** | DOM testing utilities | ^9.3.4 |
| **axe-core** | Accessibility testing | ^4.8.3 |
| **Lighthouse CI** | Performance monitoring | ^0.13.0 |
| **webpack-bundle-analyzer** | Bundle size analysis | ^4.10.1 |

### Test Environment

- **Environment**: jsdom (simulated browser)
- **Node**: >=18.0.0
- **Browsers**: Chromium, Firefox, WebKit

---

## Setup

### Installation

```bash
cd frontend
npm install
```

### Verify Setup

```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage
```

---

## Running Tests

### Quick Commands

```bash
# Run all tests
npm test

# Watch mode (auto-rerun on changes)
npm run test:watch

# Run with coverage report
npm run test:coverage

# Run specific test types
npm run test:unit           # Unit tests only
npm run test:integration    # Integration tests only
npm run test:e2e           # E2E tests with Playwright
npm run test:a11y          # Accessibility tests
npm run test:performance   # Lighthouse CI

# Run all test suites
npm run test:all
```

### E2E Testing Options

```bash
# Interactive UI mode
npm run test:e2e:ui

# Headed mode (see browser)
npm run test:e2e:headed

# Debug mode
npm run test:e2e:debug
```

### Performance & Analysis

```bash
# Bundle analysis
npm run analyze:bundle

# Lighthouse report
npm run analyze:lighthouse

# Serve coverage report
npm run serve:coverage
```

---

## Test Types

### 1. Unit Tests (`tests/unit/`)

Test individual functions and utilities in isolation.

**Location**: `/frontend/tests/unit/`

**Files**:
- `core.test.js` - Core application functions (toast, storage, state)
- `dom.test.js` - DOM manipulation and navigation

**Example**:
```javascript
describe('showToast', () => {
  test('should create toast with default info type', () => {
    showToast('Test message');

    const toast = document.querySelector('.toast');
    expect(toast).toBeTruthy();
    expect(toast.classList.contains('toast--info')).toBe(true);
  });
});
```

### 2. Integration Tests (`tests/integration/`)

Test API interactions and multi-component workflows.

**Location**: `/frontend/tests/integration/`

**Files**:
- `api.test.js` - Backend API communication
- `workflow.test.js` - Complete user workflows

**Example**:
```javascript
test('should validate prompt successfully', async () => {
  mockApiResponse({
    status: 'pass',
    violations: []
  });

  const response = await fetch(`${API_BASE}/validate`, {
    method: 'POST',
    body: JSON.stringify({ prompt: 'Test' })
  });

  const data = await response.json();
  expect(data.status).toBe('pass');
});
```

### 3. E2E Tests (`tests/e2e/`)

Test complete user journeys in real browsers.

**Location**: `/frontend/tests/e2e/`

**Files**:
- `navigation.spec.ts` - Navigation and UI interactions
- `validation.spec.ts` - Validation workflows

**Example**:
```typescript
test('should navigate to interceptor view', async ({ page }) => {
  await page.goto('/');
  await page.click('.nav__item[data-view="interceptor"]');

  await expect(page.locator('.nav__item[data-view="interceptor"]'))
    .toHaveClass(/active/);
});
```

### 4. Accessibility Tests (`tests/accessibility/`)

Verify WCAG 2.1 AA compliance.

**Location**: `/frontend/tests/accessibility/`

**Files**:
- `a11y.test.js` - Comprehensive accessibility tests

**Example**:
```javascript
test('should not have accessibility violations', async () => {
  const results = await axe(document.body);
  expect(results).toHaveNoViolations();
});
```

### 5. Performance Tests (`tests/performance/`)

Monitor performance metrics and budgets.

**Location**: `/frontend/tests/performance/`

**Files**:
- `metrics.test.js` - Performance benchmarks
- `budgets.json` - Performance budgets

**Example**:
```javascript
test('JavaScript bundle should be under 250KB', () => {
  const totalSize = scripts.reduce((sum, s) => sum + s.size, 0);
  expect(totalSize).toBeLessThan(250 * 1024);
});
```

---

## Writing Tests

### Test Structure

```javascript
describe('Feature Name', () => {
  // Setup before each test
  beforeEach(() => {
    document.body.innerHTML = '<div id="app"></div>';
  });

  // Cleanup after each test
  afterEach(() => {
    document.body.innerHTML = '';
  });

  test('should do something specific', () => {
    // Arrange
    const input = 'test';

    // Act
    const result = myFunction(input);

    // Assert
    expect(result).toBe('expected');
  });
});
```

### Mocking

#### Mock fetch API:
```javascript
mockApiResponse({ status: 'ok' });
```

#### Mock localStorage:
```javascript
localStorage.setItem('key', 'value');
expect(localStorage.getItem('key')).toBe('value');
```

#### Mock timers:
```javascript
jest.useFakeTimers();
setTimeout(() => callback(), 1000);
jest.advanceTimersByTime(1000);
expect(callback).toHaveBeenCalled();
```

### Async Testing

```javascript
test('should handle async operations', async () => {
  const promise = fetchData();
  const data = await promise;
  expect(data).toBeDefined();
});
```

### DOM Testing

```javascript
test('should update DOM', () => {
  const button = document.querySelector('button');
  button.click();

  expect(document.querySelector('.active')).toBeTruthy();
});
```

---

## Coverage Requirements

### Minimum Thresholds (80%)

- **Branches**: 80%
- **Functions**: 80%
- **Lines**: 80%
- **Statements**: 80%

### View Coverage Report

```bash
# Generate and view coverage
npm run test:coverage
npm run serve:coverage

# Open http://localhost:8081 in browser
```

### Coverage Files

Covered:
- `app.js`
- `app-web.js`

Excluded:
- Config files
- Node modules
- Test files

---

## CI/CD Integration

### GitHub Actions Workflow

Located at: `.github/workflows/frontend-tests.yml`

**Triggered on**:
- Push to `main` or `develop`
- Pull requests
- Changes to `frontend/` directory

**Jobs**:

1. **Unit Tests** - Fast feedback on core functionality
2. **Integration Tests** - API and workflow validation
3. **Coverage Check** - Enforce 80% threshold
4. **E2E Tests** - Full browser testing (Chromium, Firefox, WebKit)
5. **Accessibility Tests** - WCAG compliance
6. **Performance Tests** - Lighthouse CI with budgets
7. **Bundle Analysis** - Size tracking and visualization

### Pipeline Duration

**Target**: < 10 minutes total

- Unit: ~30s
- Integration: ~45s
- Coverage: ~1m
- E2E: ~3m
- Accessibility: ~30s
- Performance: ~2m
- Bundle Analysis: ~30s

### Artifacts

Available after each run:
- Test results
- Coverage reports
- Playwright reports
- Lighthouse reports
- Bundle analysis

---

## Best Practices

### 1. Test Naming

```javascript
// Good
test('should validate email format correctly', () => {});

// Bad
test('email test', () => {});
```

### 2. Arrange-Act-Assert Pattern

```javascript
test('should calculate total', () => {
  // Arrange
  const items = [1, 2, 3];

  // Act
  const total = sum(items);

  // Assert
  expect(total).toBe(6);
});
```

### 3. One Assertion Per Test

```javascript
// Good
test('should return success status', () => {
  expect(result.status).toBe('success');
});

test('should return data', () => {
  expect(result.data).toBeDefined();
});

// Avoid
test('should return valid response', () => {
  expect(result.status).toBe('success');
  expect(result.data).toBeDefined();
  expect(result.message).toBe('OK');
});
```

### 4. Mock External Dependencies

```javascript
// Mock API calls
beforeEach(() => {
  global.fetch = jest.fn(() =>
    Promise.resolve({
      ok: true,
      json: () => Promise.resolve({ status: 'ok' })
    })
  );
});
```

### 5. Clean Up After Tests

```javascript
afterEach(() => {
  document.body.innerHTML = '';
  jest.clearAllMocks();
  localStorage.clear();
});
```

### 6. Use Page Objects for E2E

```typescript
class LoginPage {
  async goto() {
    await page.goto('/login');
  }

  async login(email, password) {
    await page.fill('#email', email);
    await page.fill('#password', password);
    await page.click('button[type="submit"]');
  }
}
```

### 7. Test Error Cases

```javascript
test('should handle API errors', async () => {
  mockApiError('Server error', 500);

  await expect(validatePrompt('test'))
    .rejects.toThrow('Server error');
});
```

---

## Troubleshooting

### Common Issues

#### Tests Not Found

```bash
# Ensure tests match pattern
jest --listTests
```

#### Coverage Not Updating

```bash
# Clear Jest cache
jest --clearCache
npm run test:coverage
```

#### E2E Tests Failing

```bash
# Reinstall browsers
npx playwright install --with-deps

# Run in headed mode to debug
npm run test:e2e:headed
```

#### Performance Tests Failing

```bash
# Ensure server is running
npm run serve

# Check Lighthouse config
cat .lighthouserc.json
```

#### Mock Not Working

```javascript
// Reset mocks before each test
beforeEach(() => {
  jest.clearAllMocks();
  fetch.mockClear();
});
```

### Debug Mode

```bash
# Run single test file
npm test -- tests/unit/core.test.js

# Run with verbose output
npm test -- --verbose

# Run in watch mode
npm run test:watch

# Debug in VS Code
# Add breakpoint and use "Debug Jest Tests" task
```

### Getting Help

- Check test logs: `npm test -- --verbose`
- View coverage gaps: `npm run serve:coverage`
- Review CI artifacts in GitHub Actions
- Check Playwright trace: `npx playwright show-trace trace.zip`

---

## Performance Budgets

### Resource Budgets

| Resource | Budget |
|----------|--------|
| JavaScript | 250 KB |
| CSS | 100 KB |
| HTML | 50 KB |
| Images | 200 KB |
| Total | 500 KB |

### Timing Budgets

| Metric | Budget |
|--------|--------|
| First Contentful Paint | 2.0s |
| Largest Contentful Paint | 2.5s |
| Time to Interactive | 3.5s |
| Total Blocking Time | 300ms |
| Cumulative Layout Shift | 0.1 |

---

## Quick Reference

### Test Commands

| Command | Purpose |
|---------|---------|
| `npm test` | Run all tests |
| `npm run test:watch` | Watch mode |
| `npm run test:coverage` | Coverage report |
| `npm run test:unit` | Unit tests only |
| `npm run test:integration` | Integration tests |
| `npm run test:e2e` | E2E tests |
| `npm run test:a11y` | Accessibility tests |
| `npm run test:performance` | Performance tests |

### File Locations

| Type | Path |
|------|------|
| Unit | `frontend/tests/unit/` |
| Integration | `frontend/tests/integration/` |
| E2E | `frontend/tests/e2e/` |
| Accessibility | `frontend/tests/accessibility/` |
| Performance | `frontend/tests/performance/` |
| Config | `frontend/jest.config.js` |
| Playwright | `frontend/playwright.config.ts` |
| Lighthouse | `frontend/.lighthouserc.json` |

---

## Support

For issues or questions:

1. Check this documentation
2. Review test examples in `tests/` directories
3. Check CI/CD logs in GitHub Actions
4. Consult Jest/Playwright documentation

---

**Last Updated**: November 2025
**Framework Version**: 1.0.0
**Maintained by**: LOKI QA Team
