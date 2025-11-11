# Backend Testing Guide - LOKI Interceptor

## Overview

This guide provides comprehensive information on testing the LOKI Interceptor backend, including test structure, execution, coverage targets, and best practices.

**Target**: 90%+ code coverage across all backend Python modules
**Status**: In progress
**Last Updated**: November 2024

---

## Table of Contents

1. [Test Structure](#test-structure)
2. [Running Tests](#running-tests)
3. [Coverage Requirements](#coverage-requirements)
4. [Test Categories](#test-categories)
5. [Writing Tests](#writing-tests)
6. [Best Practices](#best-practices)
7. [Performance Testing](#performance-testing)
8. [Troubleshooting](#troubleshooting)

---

## Test Structure

### Directory Organization

```
tests/
├── backend/                          # Backend-specific tests
│   ├── __init__.py
│   ├── test_core_cache.py           # Cache module tests
│   ├── test_core_security.py        # Security module tests
│   ├── test_core_audit_log.py       # Audit logging tests
│   ├── test_core_corrector.py       # Document correction tests
│   ├── test_data_generators.py      # Test data generators
│   ├── test_enterprise_modules.py   # Enterprise feature tests
│   ├── test_api_endpoints.py        # API endpoint tests
│   └── test_compliance_modules.py   # Compliance module tests
├── performance/                      # Load and performance tests
│   ├── __init__.py
│   ├── locust_load_tests.py         # Load testing with Locust
│   └── test_performance_benchmarks.py # Performance benchmarks
├── integration/                      # Integration tests
├── conftest.py                       # Shared fixtures
├── factories.py                      # Test data factories
└── helpers.py                        # Test utilities
```

### Module Test Coverage

#### Core Modules (`backend/core/`)

| Module | Tests | Coverage Target | Status |
|--------|-------|-----------------|--------|
| cache.py | test_core_cache.py | 95%+ | In Progress |
| security.py | test_core_security.py | 95%+ | In Progress |
| audit_log.py | test_core_audit_log.py | 90%+ | In Progress |
| corrector.py | test_core_corrector.py | 90%+ | In Progress |
| engine.py | test_core_engine.py | 85%+ | Planned |
| interceptor.py | test_core_interceptor.py | 85%+ | Planned |

#### Enterprise Modules (`backend/enterprise/`)

| Module | Tests | Coverage Target | Status |
|--------|-------|-----------------|--------|
| auth.py | test_enterprise_auth.py | 90%+ | Planned |
| rbac.py | test_enterprise_rbac.py | 90%+ | Planned |
| multi_tenant.py | test_enterprise_multi_tenant.py | 85%+ | Planned |
| audit_trail.py | test_enterprise_audit_trail.py | 85%+ | Planned |

#### Compliance Modules (`backend/modules/`)

| Module | Tests | Coverage Target | Status |
|--------|-------|-----------------|--------|
| fca_uk/ | test_fca_modules.py | 80%+ | Exists |
| gdpr_uk/ | test_gdpr_modules.py | 80%+ | Exists |
| tax_uk/ | test_tax_modules.py | 80%+ | Exists |

---

## Running Tests

### Quick Start

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest tests/backend/test_core_cache.py

# Run specific test class
pytest tests/backend/test_core_cache.py::TestValidationCacheBasics

# Run specific test
pytest tests/backend/test_core_cache.py::TestValidationCacheBasics::test_cache_initialization
```

### Test Markers

```bash
# Run unit tests only
pytest -m "unit"

# Run integration tests only
pytest -m "integration"

# Run all except slow tests
pytest -m "not slow"

# Run security tests
pytest -m "security"

# Run performance tests
pytest -m "performance"

# Run API tests
pytest -m "api"
```

### Test Execution Modes

#### Full Test Suite
```bash
pytest --cov=backend --cov-report=term-missing --cov-report=html
```

#### Fast Tests (Exclude Slow Tests)
```bash
pytest -m "not slow" --tb=short
```

#### Parallel Execution
```bash
pytest -n auto  # Uses all available CPU cores
```

#### With Profiling
```bash
pytest --profile
```

#### Generate Report
```bash
pytest --html=report.html --self-contained-html
```

---

## Coverage Requirements

### Target Coverage

- **Overall Backend Coverage**: 90%+
- **Core Modules**: 95%+
- **Enterprise Modules**: 90%+
- **Compliance Modules**: 85%+
- **Performance Modules**: 80%+

### Coverage Thresholds

```ini
# pytest.ini coverage settings
[coverage:report]
precision = 2
show_missing = True
skip_covered = False

exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    @abstractmethod
```

### Generate Coverage Report

```bash
# Terminal report with missing lines
pytest --cov=backend --cov-report=term-missing:skip-covered

# HTML report
pytest --cov=backend --cov-report=html
# Open htmlcov/index.html in browser

# JSON report for CI/CD integration
pytest --cov=backend --cov-report=json
```

---

## Test Categories

### 1. Unit Tests

Tests for individual functions and classes in isolation.

**Characteristics**:
- Fast execution (<100ms)
- No external dependencies
- Use mocks for external services
- Test single responsibility

**Example**:
```python
def test_cache_initialization():
    """Test cache can be initialized with default settings."""
    cache = ValidationCache()
    assert cache is not None
    assert hasattr(cache, 'get')
```

### 2. Integration Tests

Tests that verify multiple components work together correctly.

**Characteristics**:
- May use real database (in-memory or test database)
- Test API endpoints with test client
- Verify data flows between modules
- Medium execution speed (100ms - 1s)

**Example**:
```python
def test_full_correction_workflow(corrector):
    """Test complete correction workflow."""
    document = "GUARANTEED returns!"
    violations = [{"module": "fca_uk", "gate": "misleading_claims"}]

    result = corrector.correct(document, violations)
    assert result is not None
```

### 3. Performance Tests

Tests that verify performance and load characteristics.

**Characteristics**:
- Use locust for load testing
- Benchmark common operations
- Verify response times
- Test under stress conditions

**Example**:
```python
def test_single_violation_correction_speed(corrector):
    """Test speed of correcting single violation."""
    text = "GUARANTEED returns!"
    violations = [{"module": "fca_uk", "gate": "misleading_claims"}]

    start_time = time.time()
    result = corrector.correct(text, violations)
    elapsed = time.time() - start_time

    assert elapsed < 5.0  # Must complete in less than 5 seconds
```

### 4. Security Tests

Tests that verify security features and protections.

**Characteristics**:
- Test authentication and authorization
- Verify input validation and sanitization
- Test rate limiting
- Test against common attacks

**Example**:
```python
def test_rate_limit_blocks_excessive_requests():
    """Test that excessive requests are blocked."""
    limiter = RateLimiter(requests_per_minute=5)

    for i in range(5):
        limiter.check_rate_limit("client")

    result = limiter.check_rate_limit("client")
    assert result is False
```

---

## Writing Tests

### Test File Template

```python
"""
Comprehensive tests for backend.core.<module> module.

Tests <functionality> including:
- <Feature 1>
- <Feature 2>
- <Feature 3>
"""

import pytest
from unittest.mock import Mock, patch
from backend.core.<module> import <Class>


class Test<Class>Basics:
    """Test basic <class> functionality."""

    def test_<class>_initialization(self):
        """Test <class> can be initialized."""
        obj = <Class>()
        assert obj is not None

    def test_<method>_success(self):
        """Test <method> succeeds with valid input."""
        obj = <Class>()
        result = obj.<method>(valid_input)
        assert result == expected_output

    def test_<method>_with_invalid_input(self):
        """Test <method> handles invalid input."""
        obj = <Class>()
        try:
            result = obj.<method>(invalid_input)
        except Exception:
            pass  # Expected behavior


class Test<Class>ErrorHandling:
    """Test error handling in <class>."""

    def test_<method>_with_none_input(self):
        """Test <method> handles None input."""
        obj = <Class>()
        try:
            result = obj.<method>(None)
        except Exception:
            pass
```

### Test Data Generators

Use the provided test data generators for realistic test data:

```python
from tests.backend.test_data_generators import (
    DocumentGenerator,
    ViolationGenerator,
    ValidationResultGenerator,
)

def test_correction_with_generated_data():
    """Test with generated test data."""
    # Generate test document
    doc = DocumentGenerator.generate_non_compliant_investment_document()

    # Generate violations
    violations = ViolationGenerator.generate_violation_set(count=3)

    # Generate expected result
    result = ValidationResultGenerator.generate_fail_result()

    # Test with generated data
    assert len(violations) == 3
```

### Using Fixtures

```python
@pytest.fixture
def compliant_document(document_generator):
    """Provide a compliant test document."""
    return document_generator.generate_compliant_investment_document()

@pytest.fixture
def violation_set():
    """Provide a set of test violations."""
    return ViolationGenerator.generate_violation_set()

def test_correction_workflow(compliant_document, violation_set, corrector):
    """Test correction with fixtures."""
    result = corrector.correct(compliant_document, violation_set)
    assert result is not None
```

---

## Best Practices

### 1. Test Isolation

- Each test should be independent
- Use fresh fixtures for each test
- Clean up after tests
- Don't share state between tests

```python
@pytest.fixture
def fresh_cache():
    """Provide fresh cache for each test."""
    cache = ValidationCache()
    yield cache
    cache.clear()  # Cleanup
```

### 2. Meaningful Names

- Use descriptive test names
- Follow pattern: `test_<function>_<scenario>_<result>`
- Make expected behavior clear

```python
# Good
def test_rate_limiter_blocks_requests_after_limit_exceeded():
    pass

# Bad
def test_rate_limit():
    pass
```

### 3. Arrange-Act-Assert Pattern

```python
def test_document_correction():
    """Test document correction."""
    # ARRANGE: Set up test data
    document = "GUARANTEED returns!"
    violations = [{"module": "fca_uk", "gate": "misleading_claims"}]
    corrector = DocumentCorrector()

    # ACT: Execute the function
    result = corrector.correct(document, violations)

    # ASSERT: Verify the result
    assert result is not None
    assert "GUARANTEED" not in result or "may" in result.lower()
```

### 4. Avoid Test Anti-Patterns

```python
# Don't: Test multiple things in one test
def test_validation_and_correction():  # BAD
    result = validate(doc)
    corrected = correct(doc)
    assert result and corrected

# Do: Separate tests for separate concerns
def test_validation_passes():  # GOOD
    result = validate(compliant_doc)
    assert result.status == "PASS"

def test_correction_fixes_violations():  # GOOD
    result = correct(non_compliant_doc)
    assert violations_fixed > 0
```

### 5. Mock External Dependencies

```python
# Don't: Make real API calls in tests
def test_validation():
    response = requests.post("http://api.example.com/validate", ...)

# Do: Mock external dependencies
@patch('requests.post')
def test_validation(mock_post):
    mock_post.return_value.json.return_value = {"status": "PASS"}
    response = validate_document("test")
    assert response["status"] == "PASS"
```

### 6. Use Parametrization for Multiple Test Cases

```python
# Don't: Multiple nearly identical tests
def test_severity_low():
    assert process_violation("LOW")

def test_severity_medium():
    assert process_violation("MEDIUM")

# Do: Parametrize
@pytest.mark.parametrize("severity", ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
def test_process_violations(severity):
    assert process_violation(severity)
```

---

## Performance Testing

### Load Testing with Locust

```bash
# Run load test
locust -f tests/performance/locust_load_tests.py --host=http://localhost:5002

# Run with specific user count
locust -f tests/performance/locust_load_tests.py \
    --host=http://localhost:5002 \
    --users=100 \
    --spawn-rate=10 \
    --run-time=5m

# Headless mode for CI/CD
locust -f tests/performance/locust_load_tests.py \
    --host=http://localhost:5002 \
    --users=100 \
    --spawn-rate=10 \
    --run-time=5m \
    --headless
```

### Performance Benchmarks

```bash
# Run benchmark tests
pytest tests/performance/test_performance_benchmarks.py -v

# With timing output
pytest tests/performance/test_performance_benchmarks.py -v --benchmark-only
```

### Performance Targets

| Operation | Target | Critical |
|-----------|--------|----------|
| API response | <2s | <5s |
| Document validation | <5s | <15s |
| Document correction | <10s | <30s |
| Single gate check | <0.5s | <2s |
| Cache hit | <10ms | <50ms |

---

## Troubleshooting

### Common Issues

#### Issue: Tests fail with import errors

**Solution**:
```bash
# Ensure backend is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd):$(pwd)/backend"
pytest
```

#### Issue: Tests hang or timeout

**Solution**:
```bash
# Run with timeout
pytest --timeout=300  # 300 second timeout

# Skip slow tests
pytest -m "not slow"
```

#### Issue: Database-related test failures

**Solution**:
```bash
# Check database fixture setup in conftest.py
# Ensure temporary databases are created and cleaned up
pytest -v --tb=short
```

#### Issue: Rate limiting or API key errors

**Solution**:
```python
# Ensure correct API key in headers
headers = {
    "X-API-Key": "test-api-key-12345",
    "Content-Type": "application/json"
}
```

### Debug Mode

```bash
# Run with verbose output
pytest -v

# Show local variables on failure
pytest -l

# Drop into debugger on failure
pytest --pdb

# Show print statements
pytest -s

# Show warnings
pytest -W default
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Backend Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        pip install -r requirements-test.txt
        pip install -r requirements.txt

    - name: Run tests with coverage
      run: |
        pytest --cov=backend --cov-report=xml

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v2
      with:
        files: ./coverage.xml
```

---

## Contributing Tests

When adding new features to the backend:

1. **Write tests first** (TDD approach)
2. **Aim for 90%+ coverage** on new code
3. **Include unit, integration, and performance tests**
4. **Follow naming conventions** and best practices
5. **Update this guide** with new test categories

---

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [coverage.py Documentation](https://coverage.readthedocs.io/)
- [Locust Documentation](https://locust.io/)
- [Mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [Test Best Practices](https://12factor.net/dev-prod-parity)

---

## Conclusion

Comprehensive backend testing is essential for maintaining code quality and ensuring compliance functionality. By following this guide and best practices, we can achieve and maintain 90%+ coverage across all backend modules.

For questions or suggestions, please refer to the main project documentation or contact the development team.
