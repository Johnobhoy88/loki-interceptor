# Frontend Testing Suite

## Overview

Comprehensive testing infrastructure for LOKI Interceptor frontend with 80%+ coverage target.

## Test Structure

```
tests/
├── setup.js                    # Jest global setup
├── unit/                       # Unit tests (fast, isolated)
│   ├── core.test.js           # Core functions (toast, storage, state)
│   └── dom.test.js            # DOM manipulation & navigation
├── integration/                # Integration tests (API + workflows)
│   ├── api.test.js            # Backend API communication
│   └── workflow.test.js       # Complete user workflows
├── e2e/                        # E2E tests (real browsers)
│   ├── navigation.spec.ts     # Navigation & UI interactions
│   └── validation.spec.ts     # Validation workflows
├── accessibility/              # WCAG 2.1 AA compliance
│   └── a11y.test.js           # Comprehensive a11y tests
├── performance/                # Performance benchmarks
│   ├── metrics.test.js        # Performance tests
│   └── budgets.json           # Performance budgets
└── fixtures/                   # Test data and mocks
```

## Quick Start

```bash
# Install dependencies
npm install

# Run all tests
npm test

# Run specific test suite
npm run test:unit           # Unit tests only
npm run test:integration    # Integration tests
npm run test:e2e           # E2E with Playwright
npm run test:a11y          # Accessibility tests
npm run test:performance   # Lighthouse CI

# Watch mode
npm run test:watch

# Coverage report
npm run test:coverage
```

## Test Statistics

- **Total Test Files**: 10
- **Unit Tests**: 2 files (core, DOM)
- **Integration Tests**: 2 files (API, workflows)
- **E2E Tests**: 2 files (navigation, validation)
- **Accessibility Tests**: 1 file (comprehensive)
- **Performance Tests**: 1 file + budgets
- **Coverage Target**: 80%+ (all metrics)

## Test Coverage

### Unit Tests (`unit/`)

**core.test.js**:
- Toast notification system (8 tests)
- Storage helper (7 tests)
- State management (2 tests)
- API base detection (4 tests)
- Constants validation (3 tests)

**dom.test.js**:
- View switching (7 tests)
- Navigation binding (2 tests)
- Action binding (4 tests)
- Element rendering (3 tests)
- Backend status indicator (3 tests)

### Integration Tests (`integration/`)

**api.test.js**:
- Backend health checks (4 tests)
- Module catalog loading (3 tests)
- Prompt validation (4 tests)
- Document validation (2 tests)
- Analytics data (3 tests)
- API key management (2 tests)
- Error handling (4 tests)
- Request headers (2 tests)

**workflow.test.js**:
- Prompt validation workflow (3 tests)
- Document validation workflow (2 tests)
- Module management workflow (2 tests)
- Analytics workflow (3 tests)
- API key management workflow (2 tests)
- Error recovery workflow (2 tests)

### E2E Tests (`e2e/`)

**navigation.spec.ts**:
- Basic navigation (10 tests)
- Sidebar functionality (3 tests)
- Responsive design (3 tests)
- Accessibility (3 tests)

**validation.spec.ts**:
- Prompt validation (7 tests)
- Document validation (3 tests)
- Module selection (3 tests)
- Error handling (3 tests)
- Toast notifications (2 tests)

### Accessibility Tests (`accessibility/`)

**a11y.test.js**:
- Main structure (4 tests)
- Navigation accessibility (4 tests)
- Form accessibility (4 tests)
- Button accessibility (4 tests)
- Color contrast (1 test)
- ARIA roles and states (3 tests)
- Keyboard navigation (3 tests)
- Headings hierarchy (3 tests)
- Images and media (3 tests)
- Focus management (3 tests)
- Live regions (3 tests)

### Performance Tests (`performance/`)

**metrics.test.js**:
- Resource budgets (4 tests)
- Load time performance (4 tests)
- JavaScript execution (4 tests)
- Memory usage (3 tests)
- Network performance (2 tests)
- Rendering performance (3 tests)
- Core Web Vitals (4 tests)

## Configuration Files

| File | Purpose |
|------|---------|
| `jest.config.js` | Jest configuration |
| `playwright.config.ts` | Playwright E2E config |
| `.lighthouserc.json` | Lighthouse CI config |
| `webpack.config.js` | Bundle analysis |
| `tests/setup.js` | Global test setup |
| `tests/performance/budgets.json` | Performance budgets |

## CI/CD Integration

Tests run automatically on:
- Push to `main` or `develop`
- Pull requests
- Changes to `frontend/` directory

**GitHub Actions Workflow**: `.github/workflows/frontend-tests.yml`

**Jobs**:
1. Unit Tests (~30s)
2. Integration Tests (~45s)
3. Coverage Check (~1m)
4. E2E Tests (~3m)
5. Accessibility Tests (~30s)
6. Performance Tests (~2m)
7. Bundle Analysis (~30s)

**Total Pipeline Time**: < 10 minutes

## Coverage Requirements

All thresholds set to **80%**:
- Lines
- Branches
- Functions
- Statements

Enforced in:
- `jest.config.js`
- CI/CD pipeline
- Pre-commit hooks (optional)

## Performance Budgets

### Resource Budgets

| Resource | Budget |
|----------|--------|
| JavaScript | 250 KB |
| CSS | 100 KB |
| HTML | 50 KB |
| Total | 500 KB |

### Timing Budgets

| Metric | Budget |
|--------|--------|
| FCP | 2.0s |
| LCP | 2.5s |
| TTI | 3.5s |
| TBT | 300ms |
| CLS | 0.1 |

## Best Practices

1. **Follow AAA Pattern**: Arrange-Act-Assert
2. **One Assertion Per Test**: Keep tests focused
3. **Mock External Dependencies**: Isolate unit tests
4. **Clean Up After Tests**: Reset state, clear mocks
5. **Use Descriptive Names**: `should do X when Y`
6. **Test Error Cases**: Don't only test happy paths
7. **Keep Tests Fast**: Unit tests should be < 100ms

## Writing New Tests

### Unit Test Template

```javascript
describe('Feature Name', () => {
  beforeEach(() => {
    // Setup
  });

  afterEach(() => {
    // Cleanup
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

### E2E Test Template

```typescript
test.describe('Feature', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should perform action', async ({ page }) => {
    await page.click('.button');
    await expect(page.locator('.result')).toBeVisible();
  });
});
```

## Troubleshooting

### Tests Not Running

```bash
# Clear Jest cache
jest --clearCache

# List all tests
jest --listTests

# Run with verbose output
npm test -- --verbose
```

### E2E Tests Failing

```bash
# Reinstall browsers
npx playwright install --with-deps

# Run in headed mode
npm run test:e2e:headed

# Debug mode
npm run test:e2e:debug
```

### Coverage Not Updating

```bash
# Clear cache and rerun
jest --clearCache
npm run test:coverage
```

## Documentation

- **Testing Guide**: `/FRONTEND_TESTING.md`
- **Performance Guide**: `/FRONTEND_PERFORMANCE_OPTIMIZATION.md`
- **CI/CD Config**: `/.github/workflows/frontend-tests.yml`

## Support

For issues:
1. Check this README
2. Review test examples
3. Check CI/CD logs
4. Consult Jest/Playwright docs

---

**Last Updated**: November 2025
**Maintained by**: LOKI QA Team
