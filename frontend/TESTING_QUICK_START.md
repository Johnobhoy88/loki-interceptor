# Frontend Testing - Quick Start Guide

## Installation

```bash
cd /home/user/loki-interceptor/frontend
npm install
```

## Run Tests (Quick Commands)

```bash
# All tests
npm test

# With coverage (80% threshold)
npm run test:coverage

# Watch mode (auto-rerun)
npm run test:watch

# Specific suites
npm run test:unit           # Unit tests (~30s)
npm run test:integration    # Integration tests (~45s)
npm run test:e2e           # E2E browser tests (~3m)
npm run test:a11y          # Accessibility tests (~30s)
npm run test:performance   # Lighthouse CI (~2m)

# All tests with full coverage
npm run test:all
```

## E2E Testing Options

```bash
# Interactive UI mode (recommended for debugging)
npm run test:e2e:ui

# See the browser while testing
npm run test:e2e:headed

# Step-by-step debugging
npm run test:e2e:debug
```

## Performance & Analysis

```bash
# Bundle size analysis
npm run analyze:bundle

# Lighthouse performance audit
npm run analyze:lighthouse

# View coverage report (after running tests)
npm run serve:coverage
# Open http://localhost:8081
```

## Test Locations

```
frontend/tests/
├── unit/              # 43 tests - Core functions & DOM
├── integration/       # 38 tests - API & workflows
├── e2e/              # 37 tests - Full user journeys
├── accessibility/     # 35 tests - WCAG compliance
└── performance/       # 24 tests - Core Web Vitals
```

## Coverage Requirements

All set to **80%** minimum:
- Lines: 80%
- Branches: 80%
- Functions: 80%
- Statements: 80%

## Performance Budgets

| Resource | Limit | Current |
|----------|-------|---------|
| JavaScript | 250 KB | ~90 KB ✓ |
| CSS | 100 KB | ~24 KB ✓ |
| Total | 500 KB | ~123 KB ✓ |

## Key Files

| File | Purpose |
|------|---------|
| `package.json` | Dependencies & scripts |
| `jest.config.js` | Jest configuration |
| `playwright.config.ts` | E2E test config |
| `.lighthouserc.json` | Performance config |
| `tests/setup.js` | Global test setup |

## CI/CD

Pipeline runs automatically on:
- Push to main/develop
- Pull requests
- Changes to frontend/

**Pipeline time**: < 10 minutes total

## Documentation

- **Full Testing Guide**: `/FRONTEND_TESTING.md`
- **Performance Guide**: `/FRONTEND_PERFORMANCE_OPTIMIZATION.md`
- **Test README**: `frontend/tests/README.md`

## Quick Troubleshooting

```bash
# Clear cache
jest --clearCache

# Reinstall browsers
npx playwright install --with-deps

# List all tests
jest --listTests

# Run single test file
npm test -- tests/unit/core.test.js

# Verbose output
npm test -- --verbose
```

## Common Issues

**Tests not found?**
```bash
jest --clearCache
npm test
```

**E2E failing?**
```bash
npx playwright install --with-deps
npm run test:e2e:headed
```

**Coverage not updating?**
```bash
jest --clearCache
npm run test:coverage
```

## Writing Your First Test

```javascript
// tests/unit/mytest.test.js
describe('My Feature', () => {
  test('should work correctly', () => {
    // Arrange
    const input = 'test';

    // Act
    const result = myFunction(input);

    // Assert
    expect(result).toBe('expected');
  });
});
```

Run it:
```bash
npm test -- tests/unit/mytest.test.js
```

## Getting Help

1. Check `/FRONTEND_TESTING.md` for detailed guide
2. Review example tests in `tests/` directories
3. Check CI/CD logs in GitHub Actions
4. Consult Jest docs: https://jestjs.io
5. Consult Playwright docs: https://playwright.dev

---

**Quick Start Version**: 1.0
**Last Updated**: November 2025
