# LOKI Compliance Platform - Testing Framework

Comprehensive testing suite for the LOKI compliance validation platform with 80%+ coverage targets.

## Overview

This testing framework validates all aspects of the LOKI platform including:
- API endpoints and workflows
- Document validation logic
- Correction algorithms
- Security measures
- Gate accuracy (false positives/negatives)
- Integration scenarios
- Load handling and performance

## Test Structure

```
tests/
├── conftest.py                  # Pytest configuration and shared fixtures
├── helpers.py                   # Test utility functions
├── factories.py                 # Test data factories
├── pytest.ini                   # Pytest settings
├── README.md                    # This file
│
├── api/                         # API Endpoint Tests
│   ├── test_endpoints.py        # All API endpoints
│   ├── test_validation.py       # Validation flow
│   ├── test_correction.py       # Correction flow
│   ├── test_interceptor.py      # AI interceptor
│   └── test_auth.py             # Authentication
│
├── security/                    # Security Tests
│   ├── test_rate_limiting.py    # Rate limit enforcement
│   ├── test_injection.py        # SQL/command injection
│   └── [Additional security tests]
│
├── gates/                       # Gate Accuracy Tests
│   ├── test_false_positives.py  # Compliant text detection
│   ├── test_false_negatives.py  # Violation detection
│   └── [Module-specific tests]
│
├── integration/                 # Integration Tests
│   ├── test_full_workflow.py    # End-to-end scenarios
│   └── [Additional integration tests]
│
└── load/                        # Load & Performance Tests
    ├── test_concurrent.py        # Concurrent requests
    └── [Additional load tests]
```

## Running Tests

### Quick Start

```bash
# Run all tests
pytest

# Run specific test category
pytest tests/api/
pytest tests/security/
pytest tests/gates/

# Run with coverage
pytest --cov=backend --cov-report=html
```

### By Marker

```bash
# Run only fast tests (exclude slow tests)
pytest -m "not slow"

# Run only security tests
pytest -m security

# Run only API tests
pytest -m api

# Run only gate accuracy tests
pytest -m gates

# Run only performance tests
pytest -m performance

# Run integration tests
pytest -m integration
```

### Specific Test Files

```bash
# Single test file
pytest tests/api/test_endpoints.py

# Single test class
pytest tests/api/test_endpoints.py::TestHealthEndpoint

# Single test function
pytest tests/api/test_endpoints.py::TestHealthEndpoint::test_health_basic

# Pattern matching
pytest -k "test_validation"
```

### With Options

```bash
# Verbose output
pytest -v

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Stop after N failures
pytest --maxfail=3

# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Generate HTML report
pytest --html=report.html --self-contained-html

# With coverage threshold
pytest --cov=backend --cov-fail-under=80
```

## Coverage Targets

| Component | Target Coverage | Current |
|-----------|----------------|---------|
| Overall | 80%+ | TBD |
| API Endpoints | 90%+ | TBD |
| Core Logic | 85%+ | TBD |
| Security | 95%+ | TBD |
| Gates | 90%+ | TBD |

### Generating Coverage Reports

```bash
# Terminal report
pytest --cov=backend --cov-report=term-missing

# HTML report (browse to htmlcov/index.html)
pytest --cov=backend --cov-report=html

# XML report (for CI/CD)
pytest --cov=backend --cov-report=xml

# Combined
pytest --cov=backend --cov-report=html --cov-report=xml --cov-report=term
```

## Test Categories

### 1. API Tests (`tests/api/`)

**Purpose:** Validate all API endpoints

**Coverage:**
- All REST endpoints
- Request/response validation
- Error handling
- Authentication
- CORS

**Run:** `pytest tests/api/ -v`

### 2. Security Tests (`tests/security/`)

**Purpose:** Validate security measures

**Coverage:**
- Rate limiting
- API key validation
- SQL injection protection
- Command injection protection
- XSS protection
- Input sanitization

**Run:** `pytest tests/security/ -m security -v`

### 3. Gate Accuracy Tests (`tests/gates/`)

**Purpose:** Validate gate detection accuracy

**Coverage:**
- False positive rate (<1%)
- False negative rate (<0.1%)
- Edge cases
- Performance benchmarks

**Run:** `pytest tests/gates/ -m gates -v`

**Key Metrics:**
- False Positives: Compliant text incorrectly flagged
- False Negatives: Violations not detected
- Accuracy: (TP + TN) / Total

### 4. Integration Tests (`tests/integration/`)

**Purpose:** Test complete workflows

**Coverage:**
- End-to-end document processing
- Multi-module validation
- Provider integration
- Real document scenarios

**Run:** `pytest tests/integration/ -m integration -v`

### 5. Load Tests (`tests/load/`)

**Purpose:** Validate performance under load

**Coverage:**
- Concurrent request handling
- Stress testing
- Spike traffic handling
- Resource limits

**Run:** `pytest tests/load/ -m performance -v`

**Note:** These tests are marked as `slow`

## Fixtures

### Available Fixtures (from conftest.py)

**Application Fixtures:**
- `app` - Flask application instance
- `client` - Test client for API calls
- `authenticated_client` - Pre-authenticated client

**Engine Fixtures:**
- `engine` - LOKI validation engine
- `corrector` - Document corrector
- `cache` - Validation cache

**Security Fixtures:**
- `security_manager` - Security manager instance
- `rate_limiter` - Rate limiter instance
- `audit_logger` - Audit logger instance

**Data Fixtures:**
- `sample_compliant_text` - Compliant document
- `sample_violation_text` - Document with violations
- `sample_gdpr_violation` - GDPR-specific violations
- `sample_tax_document` - Tax document sample
- `sample_nda_document` - NDA sample
- `sample_hr_document` - HR document sample

**Mock Fixtures:**
- `mock_anthropic_response` - Mock Anthropic API response
- `mock_openai_response` - Mock OpenAI response
- `mock_validation_pass` - Mock passing validation
- `mock_validation_fail` - Mock failing validation

**Utility Fixtures:**
- `performance_monitor` - Performance measurement
- `benchmark_threshold` - Performance thresholds
- `test_documents_path` - Test documents directory

## Factories

Use test factories for generating test data:

```python
from tests.factories import (
    ValidationResultFactory,
    DocumentFactory,
    CorrectionFactory,
    APIPayloadFactory
)

# Create validation results
pass_result = ValidationResultFactory.create_pass_result('gdpr_uk')
fail_result = ValidationResultFactory.create_fail_result('fca_uk', violations=5)

# Create documents
compliant_doc = DocumentFactory.create_financial_document(compliant=True)
violation_doc = DocumentFactory.create_privacy_policy(compliant=False)

# Create payloads
payload = APIPayloadFactory.create_validation_payload(
    text="Test document",
    modules=['fca_uk', 'gdpr_uk']
)
```

## Helpers

Use helper functions for common operations:

```python
from tests.helpers import (
    AssertionHelpers,
    DocumentGenerator,
    PerformanceHelpers
)

# Common assertions
AssertionHelpers.assert_valid_validation_response(response_data)
AssertionHelpers.assert_module_present(data, 'fca_uk')
AssertionHelpers.assert_has_violations(data, 'fca_uk')

# Generate test data
random_text = DocumentGenerator.generate_random_text(1000)

# Performance measurement
result, duration = PerformanceHelpers.measure_execution_time(some_function)
PerformanceHelpers.assert_within_threshold(duration, 5.0, "Validation")
```

## Writing Tests

### Test Structure

```python
import pytest
import json


class TestFeature:
    """Test a specific feature."""

    def test_basic_functionality(self, client):
        """Test basic functionality works."""
        # Arrange
        payload = {'text': 'test'}

        # Act
        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert 'validation' in data

    @pytest.mark.parametrize('input_value,expected', [
        ('compliant', 'PASS'),
        ('violation', 'FAIL'),
    ])
    def test_with_parameters(self, client, input_value, expected):
        """Test with multiple parameter sets."""
        # Test implementation
        pass

    @pytest.mark.slow
    def test_expensive_operation(self, client):
        """Test that takes a long time."""
        # Will be skipped when running: pytest -m "not slow"
        pass
```

### Best Practices

1. **Use descriptive names:** Test names should clearly describe what is being tested
2. **Follow AAA pattern:** Arrange, Act, Assert
3. **One assertion per test:** When possible, focus on one thing
4. **Use fixtures:** Reuse setup code via fixtures
5. **Use factories:** Generate test data with factories
6. **Mark tests appropriately:** Use markers for organization
7. **Test edge cases:** Include boundary conditions
8. **Mock external dependencies:** Don't rely on external services

## CI/CD Integration

### GitHub Actions

Tests run automatically on:
- Push to main/develop branches
- Pull requests
- Daily schedule (2 AM UTC)

### Workflow Jobs

1. **Test Matrix:** Runs on Ubuntu, Windows, macOS with Python 3.8-3.11
2. **Performance Tests:** Runs performance benchmarks
3. **Security Scan:** Runs Bandit and Safety
4. **Lint:** Runs Flake8, Black, isort, MyPy
5. **Coverage Report:** Generates coverage reports

### Viewing Results

- Check GitHub Actions tab for test results
- Download artifacts for coverage reports
- View test summary in PR checks

## Performance Benchmarks

### Thresholds

| Operation | Threshold |
|-----------|-----------|
| API Response | 2s |
| Document Validation | 5s |
| Document Correction | 10s |
| Single Gate Check | 0.5s |
| Document Synthesis | 15s |

### Running Benchmarks

```bash
# Run performance tests
pytest tests/load/ -m performance -v

# With benchmark plugin
pytest tests/ --benchmark-only
```

## Troubleshooting

### Common Issues

**Tests fail with import errors:**
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
# Or on Windows:
set PYTHONPATH=%PYTHONPATH%;%CD%
```

**Rate limiting in tests:**
```bash
# Increase rate limits or clear between test runs
pytest tests/api/test_endpoints.py --maxfail=1
```

**Slow test execution:**
```bash
# Skip slow tests
pytest -m "not slow"

# Run in parallel
pytest -n auto
```

**Coverage not generated:**
```bash
# Ensure pytest-cov is installed
pip install pytest-cov

# Run with explicit coverage
pytest --cov=backend
```

## Contributing

When adding new features:

1. Write tests first (TDD)
2. Ensure tests pass: `pytest`
3. Check coverage: `pytest --cov=backend --cov-report=term-missing`
4. Maintain 80%+ coverage
5. Add appropriate markers
6. Update this README if needed

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [Coverage.py](https://coverage.readthedocs.io/)
- [GitHub Actions](https://docs.github.com/en/actions)
