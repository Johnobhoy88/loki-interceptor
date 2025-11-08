# LOKI Testing Framework - Quick Reference

## Common Commands

### Run Tests

```bash
# All tests
pytest

# Fast tests only
pytest -m "not slow"

# Specific category
pytest tests/api/                  # API tests
pytest tests/security/             # Security tests
pytest tests/gates/                # Gate accuracy tests
pytest tests/integration/          # Integration tests
pytest tests/load/                 # Load tests

# By marker
pytest -m api                      # API tests
pytest -m security                 # Security tests
pytest -m gates                    # Gate tests
pytest -m performance              # Performance tests

# With coverage
pytest --cov=backend --cov-report=html

# Parallel (fast)
pytest -n auto

# Verbose
pytest -v

# Stop on first failure
pytest -x
```

### Coverage

```bash
# Generate HTML report
pytest --cov=backend --cov-report=html
# Open: htmlcov/index.html

# Terminal report
pytest --cov=backend --cov-report=term-missing

# Check threshold
pytest --cov=backend --cov-fail-under=80
```

## Test Structure

```
tests/
├── api/              # API endpoint tests
├── security/         # Security tests
├── gates/            # Gate accuracy tests
├── integration/      # End-to-end tests
├── load/             # Performance tests
├── conftest.py       # Fixtures
├── helpers.py        # Utilities
└── factories.py      # Data generators
```

## Common Fixtures

```python
def test_example(client, sample_compliant_text, engine):
    # client - Flask test client
    # sample_compliant_text - Compliant document
    # engine - LOKI validation engine
    pass
```

**Available Fixtures:**
- `client` - Test client
- `authenticated_client` - Auth client
- `engine` - LOKI engine
- `corrector` - Document corrector
- `sample_compliant_text` - Compliant doc
- `sample_violation_text` - Violation doc
- `mock_validation_pass` - Pass result
- `mock_validation_fail` - Fail result

## Test Factories

```python
from tests.factories import (
    ValidationResultFactory,
    DocumentFactory,
    APIPayloadFactory
)

# Create test data
result = ValidationResultFactory.create_fail_result('fca_uk', violations=3)
doc = DocumentFactory.create_financial_document(compliant=False)
payload = APIPayloadFactory.create_validation_payload()
```

## Helper Functions

```python
from tests.helpers import AssertionHelpers

# Common assertions
AssertionHelpers.assert_valid_validation_response(data)
AssertionHelpers.assert_has_violations(data, 'fca_uk')
AssertionHelpers.assert_module_present(data, 'gdpr_uk')
```

## Writing Tests

### Basic Test

```python
def test_feature(client):
    """Test description."""
    # Arrange
    payload = {'text': 'test'}

    # Act
    response = client.post('/api/validate-document',
                          data=json.dumps(payload),
                          content_type='application/json')

    # Assert
    assert response.status_code == 200
```

### Parametrized Test

```python
@pytest.mark.parametrize('input,expected', [
    ('compliant', 'PASS'),
    ('violation', 'FAIL'),
])
def test_with_params(client, input, expected):
    # Test implementation
    pass
```

### Marked Test

```python
@pytest.mark.slow
def test_expensive_operation(client):
    # Long-running test
    pass
```

## Test Markers

- `@pytest.mark.slow` - Slow test
- `@pytest.mark.integration` - Integration test
- `@pytest.mark.security` - Security test
- `@pytest.mark.performance` - Performance test
- `@pytest.mark.api` - API test
- `@pytest.mark.gates` - Gate test

## CI/CD

### GitHub Actions
- Runs on: Push, PR, Daily
- Platforms: Ubuntu, Windows, macOS
- Python: 3.8, 3.9, 3.10, 3.11
- Jobs: Tests, Security, Lint, Coverage

### View Results
- GitHub Actions tab
- Download artifacts
- Check PR status

## Coverage Targets

| Component | Target |
|-----------|--------|
| Overall | 80%+ |
| API | 90%+ |
| Security | 95%+ |
| Gates | 90%+ |

## Performance Benchmarks

| Operation | Threshold |
|-----------|-----------|
| API Response | 2s |
| Validation | 5s |
| Correction | 10s |
| Gate Check | 0.5s |
| Synthesis | 15s |

## Troubleshooting

### Import Errors
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Slow Tests
```bash
pytest -m "not slow"
pytest -n auto  # Parallel
```

### Coverage Issues
```bash
pip install pytest-cov
pytest --cov=backend
```

### Rate Limiting
```bash
pytest --maxfail=1
```

## Quick Start

```bash
# 1. Install
pip install pytest pytest-cov pytest-xdist

# 2. Run all tests
pytest

# 3. Generate coverage
pytest --cov=backend --cov-report=html

# 4. View report
open htmlcov/index.html
```

## Resources

- Full docs: `tests/README.md`
- Summary: `TESTING_FRAMEWORK_SUMMARY.md`
- Pytest: https://docs.pytest.org/
- Coverage: https://coverage.readthedocs.io/
