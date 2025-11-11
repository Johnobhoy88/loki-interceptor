# E2E Testing Guide for LOKI Compliance Platform

## Overview

This guide provides comprehensive instructions for running end-to-end (E2E), integration, smoke, and chaos engineering tests for the LOKI Compliance Platform.

## Test Structure

```
tests/
├── e2e/                          # End-to-end tests
│   ├── __init__.py
│   └── test_api_validation_workflow.py
├── integration/                  # Integration tests
│   ├── __init__.py
│   ├── test_api_contract.py
│   ├── test_database_integration.py
│   └── test_database_migration.py
├── smoke/                        # Smoke tests for deployments
│   ├── __init__.py
│   └── test_deployment_smoke.py
├── chaos/                        # Chaos engineering tests
│   ├── __init__.py
│   └── test_resilience.py
├── conftest.py                   # Shared fixtures and configuration
└── fixtures/                     # Test fixtures and data
```

## Test Categories

### 1. Smoke Tests (Quick Validation)
Quick tests to verify basic system functionality after deployment.

**Run smoke tests:**
```bash
pytest tests/smoke/ -v
```

**What they test:**
- Backend availability and health
- Frontend accessibility
- Core API endpoints
- Database connectivity
- Cache functionality
- Error handling
- Response times

### 2. E2E Tests (User Workflows)
Tests that simulate complete user workflows through the system.

**Run E2E tests:**
```bash
pytest tests/e2e/ -v
```

**Test scenarios:**
- Document validation workflow
- Document correction workflow
- Gate execution workflow
- Batch document processing
- Multi-gate compliance checking

### 3. Integration Tests (Component Interaction)
Tests that validate interaction between multiple components.

**Run integration tests:**
```bash
pytest tests/integration/ -v
```

**What they test:**
- Database operations and transactions
- Cache operations and expiration
- API contracts and response schemas
- Cross-service integration
- Database migrations
- Query builder functionality

### 4. Chaos Engineering Tests (Resilience)
Tests that validate system behavior under failure conditions.

**Run chaos tests:**
```bash
pytest tests/chaos/ -v
```

**What they test:**
- Database failure resilience
- Cache failure fallback
- Network failure handling
- High load scenarios
- Concurrent request handling
- Memory leak detection
- Error propagation

## Setup Instructions

### 1. Install Test Dependencies

```bash
pip install -r requirements-test.txt
```

Required packages:
- pytest >= 7.4.0
- pytest-cov >= 4.1.0
- requests >= 0.23.0
- redis >= 4.0.0
- sqlalchemy >= 2.0.0

### 2. Set Up Test Environment

#### Option A: Using Docker Compose (Recommended)

```bash
docker-compose -f docker-compose.test.yml up -d
```

This creates:
- PostgreSQL test database (port 5433)
- Redis test cache (port 6380)
- Backend test server (port 5003)
- Frontend test app (port 8081)

#### Option B: Using Local Services

Make sure you have:
- PostgreSQL running on port 5433
- Redis running on port 6380
- Backend running on port 5002
- Frontend running on port 80

### 3. Configure Environment Variables

Create a `.env.test` file or export variables:

```bash
# Database
export TEST_DATABASE_URL="postgresql://loki:testpass@localhost:5433/loki_test"
export TEST_POSTGRES_DB="loki_test"
export TEST_POSTGRES_USER="loki"
export TEST_POSTGRES_PASSWORD="testpass"
export TEST_POSTGRES_PORT="5433"

# Redis
export TEST_REDIS_URL="redis://:testpass@localhost:6380/0"
export TEST_REDIS_PASSWORD="testpass"
export TEST_REDIS_PORT="6380"

# API
export BACKEND_URL="http://localhost:5002"
export FRONTEND_URL="http://localhost:80"
export API_TIMEOUT="30"

# Smoke Tests
export SMOKE_TEST_TIMEOUT="10"

# Chaos Engineering
export CHAOS_ENABLED="true"
export CHAOS_FAILURE_RATE="0.1"
export CHAOS_DELAY_MS="100"
export CHAOS_TIMEOUT="30"
```

## Running Tests

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test Categories

```bash
# Smoke tests only
pytest tests/smoke/ -v

# E2E tests only
pytest tests/e2e/ -v

# Integration tests only
pytest tests/integration/ -v

# Chaos tests only
pytest tests/chaos/ -v
```

### Run Tests with Markers

```bash
# Run only fast tests (skip slow)
pytest tests/ -v -m "not slow"

# Run only integration tests
pytest tests/ -v -m "integration"

# Run only smoke tests
pytest tests/ -v -m "smoke"

# Run only E2E tests
pytest tests/ -v -m "e2e"
```

### Run Tests with Coverage

```bash
pytest tests/ -v --cov=backend --cov-report=html --cov-report=term-missing
```

This generates:
- `htmlcov/index.html` - HTML coverage report
- Console coverage summary

### Run Tests in Parallel

```bash
# Install pytest-xdist first
pip install pytest-xdist

# Run with parallel execution (auto-detect CPU cores)
pytest tests/ -v -n auto

# Run with specific number of workers
pytest tests/ -v -n 4
```

### Run Tests with Specific Configuration

```bash
# Use custom pytest configuration
pytest tests/ -c pytest.ini -v

# Run with custom timeout
pytest tests/ -v --timeout=60

# Run with specific log level
pytest tests/ -v --log-cli-level=DEBUG

# Generate JUnit XML for CI/CD
pytest tests/ -v --junit-xml=test-results.xml

# Generate JSON report for parsing
pytest tests/ -v --json-report --json-report-file=report.json
```

## Test Execution Examples

### Pre-Deployment Smoke Test Suite

```bash
# Run quick validation suite (< 5 minutes)
pytest tests/smoke/ -v --timeout=30 -m "not slow"

# Expected output: 20+ tests, all passing
```

### Development Testing

```bash
# Run E2E and integration tests with coverage
pytest tests/e2e/ tests/integration/ -v --cov=backend --cov-report=html

# Watch for failures
pytest tests/ -v -x  # Stop at first failure
```

### CI/CD Pipeline

```bash
# Full test suite with reporting
pytest tests/ \
  -v \
  --cov=backend \
  --cov-report=xml \
  --junit-xml=test-results.xml \
  --json-report \
  --timeout=300 \
  -m "not slow"
```

### Load Testing

```bash
# Run chaos engineering tests for resilience
pytest tests/chaos/ -v --timeout=120

# Run with specific failure rate
CHAOS_FAILURE_RATE=0.2 pytest tests/chaos/ -v
```

## Test Fixtures

### Common Fixtures

All fixtures are defined in `tests/conftest.py` and are automatically available.

#### Configuration Fixtures
```python
def test_example(test_config):
    """Access test configuration."""
    backend_url = test_config['backend_url']
    api_timeout = test_config['api_timeout']
```

#### Database Fixtures
```python
def test_database(db_session_pg):
    """Access PostgreSQL database session."""
    result = db_session_pg.execute("SELECT 1")
    assert result.scalar() == 1
```

#### Cache Fixtures
```python
def test_cache(redis_client_pg):
    """Access Redis cache client."""
    redis_client_pg.set("key", "value")
    assert redis_client_pg.get("key") == "value"
```

#### API Fixtures
```python
def test_api(api_client_session, test_config):
    """Make HTTP requests."""
    response = api_client_session.post(
        f"{test_config['backend_url']}/api/validate",
        json={"title": "Test"}
    )
```

## Test Reporting

### HTML Coverage Report

```bash
pytest tests/ --cov=backend --cov-report=html
open htmlcov/index.html  # Open in browser
```

### Console Summary

```bash
pytest tests/ -v --tb=short
```

### Detailed Test Report

```bash
pytest tests/ -v --tb=long --capture=no
```

### Performance Report

```bash
pytest tests/ -v --durations=10  # Show slowest 10 tests
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: E2E Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: loki_test
      redis:
        image: redis:7-alpine

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt

      - name: Run smoke tests
        run: pytest tests/smoke/ -v

      - name: Run integration tests
        run: pytest tests/integration/ -v

      - name: Run E2E tests
        run: pytest tests/e2e/ -v

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

## Troubleshooting

### Common Issues

#### Database Connection Error
```
ERROR: Database connection failed
```

**Solution:**
1. Verify PostgreSQL is running: `psql -h localhost -p 5433 -U loki`
2. Check database exists: `createdb -h localhost -p 5433 -U loki loki_test`
3. Verify DATABASE_URL environment variable

#### Redis Connection Error
```
ERROR: Redis connection failed
```

**Solution:**
1. Verify Redis is running: `redis-cli -p 6380 ping`
2. Check Redis password is correct
3. Verify REDIS_URL environment variable

#### API Not Responding
```
ERROR: Backend not responsive
```

**Solution:**
1. Check backend is running: `curl http://localhost:5002/health`
2. Check logs: `docker logs loki-backend-test`
3. Verify BACKEND_URL environment variable

#### Tests Timing Out
```
TimeoutError: Test timed out
```

**Solution:**
1. Increase timeout: `pytest tests/ --timeout=300`
2. Skip slow tests: `pytest tests/ -m "not slow"`
3. Check system resources

### Debug Mode

```bash
# Run with verbose output
pytest tests/e2e/test_api_validation_workflow.py -vv -s

# Show all local variables on failure
pytest tests/ -l

# Drop into debugger on failure
pytest tests/ --pdb

# Log debug output
pytest tests/ -v --log-cli-level=DEBUG
```

## Best Practices

### 1. Test Isolation
- Each test should be independent
- Use fixtures for setup and teardown
- Don't rely on test execution order

### 2. Meaningful Assertions
```python
# Good
assert response.status_code == 200
assert "validation_id" in response.json()

# Bad
assert response  # Too vague
```

### 3. Test Documentation
```python
def test_validation_with_gates(api_client, test_config):
    """Test document validation with multiple compliance gates.

    This test verifies that:
    - Multiple gates execute in the correct order
    - Results are returned for each gate
    - Validation completes successfully
    """
```

### 4. Error Handling
```python
def test_error_handling(api_client, test_config):
    """Test graceful error handling."""
    response = api_client.post(
        f"{test_config['backend_url']}/api/validate",
        json={"invalid": "data"},
        timeout=test_config['api_timeout']
    )
    # Verify error response, not crash
    assert response.status_code < 500
```

## Performance Benchmarks

Expected test execution times:

| Suite | Count | Time | Average |
|-------|-------|------|---------|
| Smoke | 20 | 2-3m | 6-9s |
| E2E | 15 | 5-7m | 20-28s |
| Integration | 25 | 3-5m | 7-12s |
| Chaos | 20 | 8-10m | 24-30s |

**Total: ~80 tests in 20-25 minutes**

## Success Metrics

### Coverage Targets
- Line coverage: > 80%
- Branch coverage: > 75%
- Integration coverage: > 90%

### Performance Targets
- Smoke tests: < 5 minutes
- All tests: < 30 minutes
- Individual test: < 60 seconds

### Reliability Targets
- Test pass rate: 100%
- No flaky tests: 0
- Chaos test success rate: > 95%

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [Chaos Engineering Guide](https://principlesofchaos.org/)

## Support

For issues or questions:
1. Check test logs: `pytest tests/ -v --log-cli-level=DEBUG`
2. Review test output: `pytest tests/ -v -s`
3. Consult LOKI documentation
4. Submit issue with test output
