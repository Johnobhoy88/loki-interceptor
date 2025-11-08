# Gate Testing Framework

Comprehensive testing strategies for LOKI compliance gates.

## Testing Philosophy

LOKI gates must achieve:
- **High Precision**: Minimize false positives (incorrect failures)
- **High Recall**: Catch all genuine violations
- **Performance**: Execute quickly on large documents
- **Maintainability**: Tests document expected behavior

## Test Structure

### 1. Unit Tests

Test individual gates in isolation.

```python
# tests/unit/test_notice_period_gate.py

import pytest
from backend.modules.hr_scottish.gates.notice import NoticePeriodGate

class TestNoticePeriodGate:
    @pytest.fixture
    def gate(self):
        return NoticePeriodGate()

    def test_pass_with_date(self, gate):
        """Gate should pass when date is provided"""
        text = """
        Disciplinary Hearing Invitation

        You are invited to a disciplinary meeting on 15/03/2024
        at 10:00 AM in Conference Room B.
        """
        result = gate.check(text, 'disciplinary_notice')

        assert result['status'] == 'PASS'
        assert result['severity'] == 'none'

    def test_pass_with_time(self, gate):
        """Gate should pass when time is provided"""
        text = """
        Disciplinary Meeting

        Meeting scheduled for 2:30 PM today.
        """
        result = gate.check(text, 'disciplinary_notice')

        assert result['status'] == 'PASS'

    def test_fail_without_datetime(self, gate):
        """Gate should fail when no date or time provided"""
        text = """
        Disciplinary Hearing

        You are required to attend a meeting regarding
        your conduct. Please prepare your response.
        """
        result = gate.check(text, 'disciplinary_notice')

        assert result['status'] == 'FAIL'
        assert result['severity'] == 'high'
        assert 'suggestion' in result

    def test_not_applicable_irrelevant_doc(self, gate):
        """Gate should return N/A for non-disciplinary documents"""
        text = """
        Performance Review

        Your annual review is scheduled for next week.
        """
        result = gate.check(text, 'performance_review')

        assert result['status'] == 'N/A'

    def test_edge_case_empty_text(self, gate):
        """Gate should handle empty text gracefully"""
        result = gate.check('', 'disciplinary_notice')
        assert result['status'] in ['FAIL', 'N/A']

    def test_edge_case_none_text(self, gate):
        """Gate should handle None text gracefully"""
        result = gate.check(None, 'disciplinary_notice')
        assert result['status'] in ['FAIL', 'N/A']

    def test_legal_source_present(self, gate):
        """Gate result must include legal source"""
        text = "Disciplinary meeting scheduled"
        result = gate.check(text, 'disciplinary_notice')

        assert 'legal_source' in result
        assert len(result['legal_source']) > 0
        assert 'ACAS' in result['legal_source']

    def test_various_date_formats(self, gate):
        """Gate should recognize multiple date formats"""
        date_formats = [
            "15/03/2024",
            "15-03-2024",
            "15 March 2024",
            "15 Mar 2024",
            "15th March",
        ]

        for date_str in date_formats:
            text = f"Disciplinary meeting on {date_str}"
            result = gate.check(text, 'disciplinary_notice')
            assert result['status'] == 'PASS', f"Failed for date format: {date_str}"
```

### 2. Integration Tests

Test gates within module context.

```python
# tests/integration/test_hr_module.py

import pytest
from backend.modules.hr_scottish import MODULE_INFO

class TestHRScottishModule:
    def test_module_structure(self):
        """Verify module has required structure"""
        assert 'id' in MODULE_INFO
        assert 'gates' in MODULE_INFO
        assert len(MODULE_INFO['gates']) > 0

    def test_all_gates_registered(self):
        """Verify all gates are properly registered"""
        gates = MODULE_INFO['gates']

        for gate_id, gate_obj in gates.items():
            assert hasattr(gate_obj, 'name')
            assert hasattr(gate_obj, 'severity')
            assert hasattr(gate_obj, 'check')
            assert callable(gate_obj.check)

    def test_gate_severity_levels(self):
        """Verify all gates have valid severity levels"""
        valid_severities = ['critical', 'high', 'medium', 'low']
        gates = MODULE_INFO['gates']

        for gate_id, gate_obj in gates.items():
            assert gate_obj.severity in valid_severities, \
                f"Gate {gate_id} has invalid severity: {gate_obj.severity}"

    def test_module_validation_workflow(self):
        """Test complete module validation workflow"""
        from backend.server import validate_document

        text = """
        Disciplinary Hearing Notice

        You are invited to attend a disciplinary hearing.
        Date: 15 March 2024
        Time: 2:00 PM
        Location: Room 101

        You have the right to be accompanied by a trade union
        representative or work colleague.

        You have the right to appeal any decision made.
        """

        results = validate_document(
            text=text,
            document_type='disciplinary_notice',
            modules=['hr_scottish']
        )

        assert 'validation' in results
        assert 'hr_scottish' in results['validation']['modules']

        hr_results = results['validation']['modules']['hr_scottish']
        assert 'gates' in hr_results

        # Check specific gates passed
        assert hr_results['gates']['notice_period']['status'] == 'PASS'
        assert hr_results['gates']['accompaniment']['status'] == 'PASS'
        assert hr_results['gates']['appeal']['status'] == 'PASS'
```

### 3. Gold Standard Tests

Test against real-world violation fixtures.

```python
# tests/semantic/test_fca_gold_standard.py

import pytest
import json
from pathlib import Path
from backend.server import validate_document

FIXTURES_DIR = Path(__file__).parent / 'gold_fixtures' / 'fca_uk'

class TestFCAGoldStandard:
    @pytest.fixture
    def fixtures(self):
        """Load all FCA gold standard fixtures"""
        fixtures = []
        for fixture_file in FIXTURES_DIR.glob('*.json'):
            with open(fixture_file) as f:
                fixtures.append(json.load(f))
        return fixtures

    def test_guaranteed_returns_detection(self, fixtures):
        """Test guaranteed returns violations are detected"""
        fixture = next(f for f in fixtures if f['violation_type'] == 'guaranteed_returns')

        results = validate_document(
            text=fixture['text'],
            document_type='financial',
            modules=['fca_uk']
        )

        gates = results['validation']['modules']['fca_uk']['gates']

        # Should fail on fair_clear_not_misleading gate
        assert gates['fair_clear_not_misleading']['status'] == 'FAIL'
        assert 'guarantee' in gates['fair_clear_not_misleading']['message'].lower()

    def test_missing_risk_warnings(self, fixtures):
        """Test missing risk warning detection"""
        fixture = next(f for f in fixtures if f['violation_type'] == 'missing_risk_warning')

        results = validate_document(
            text=fixture['text'],
            document_type='financial',
            modules=['fca_uk']
        )

        gates = results['validation']['modules']['fca_uk']['gates']
        assert gates['risk_warnings']['status'] == 'FAIL'

    def test_compliant_documents_pass(self, fixtures):
        """Test that compliant documents pass all gates"""
        compliant_fixtures = [f for f in fixtures if f.get('should_pass', False)]

        for fixture in compliant_fixtures:
            results = validate_document(
                text=fixture['text'],
                document_type=fixture.get('document_type', 'financial'),
                modules=['fca_uk']
            )

            module_status = results['validation']['modules']['fca_uk']['status']
            assert module_status == 'PASS', \
                f"Compliant fixture failed: {fixture.get('name')}"

    def test_all_fixtures_have_metadata(self, fixtures):
        """Verify all fixtures have required metadata"""
        required_fields = ['text', 'violation_type', 'expected_gate_failures']

        for fixture in fixtures:
            for field in required_fields:
                assert field in fixture, \
                    f"Fixture missing required field: {field}"

    @pytest.mark.parametrize("fixture_name", [
        'guaranteed_returns_01.json',
        'pressure_tactics_01.json',
        'past_performance_01.json',
    ])
    def test_specific_violations(self, fixture_name):
        """Test specific violation scenarios"""
        with open(FIXTURES_DIR / fixture_name) as f:
            fixture = json.load(f)

        results = validate_document(
            text=fixture['text'],
            document_type='financial',
            modules=['fca_uk']
        )

        gates = results['validation']['modules']['fca_uk']['gates']

        # Check expected gate failures
        for expected_fail_gate in fixture['expected_gate_failures']:
            assert gates[expected_fail_gate]['status'] == 'FAIL', \
                f"Expected {expected_fail_gate} to fail for {fixture_name}"
```

### 4. Performance Tests

Test gate performance at scale.

```python
# tests/performance/test_gate_performance.py

import pytest
import time
from backend.modules.fca_uk.gates.fair_clear_not_misleading import FairClearNotMisleadingGate

class TestGatePerformance:
    @pytest.fixture
    def large_document(self):
        """Generate large test document"""
        base_text = """
        Investment opportunity with potential returns.
        This document contains important information about risks.
        """ * 1000  # 2000 lines
        return base_text

    def test_single_gate_performance(self, large_document):
        """Gate should process large document quickly"""
        gate = FairClearNotMisleadingGate()

        start = time.time()
        result = gate.check(large_document, 'financial')
        elapsed = time.time() - start

        # Should complete in under 100ms
        assert elapsed < 0.1, f"Gate took {elapsed:.3f}s (expected < 0.1s)"
        assert result['status'] in ['PASS', 'FAIL', 'N/A']

    def test_module_performance(self, large_document):
        """Full module validation should be performant"""
        from backend.server import validate_document

        start = time.time()
        results = validate_document(
            text=large_document,
            document_type='financial',
            modules=['fca_uk']
        )
        elapsed = time.time() - start

        # Full module should complete in under 500ms
        assert elapsed < 0.5, f"Module validation took {elapsed:.3f}s"

    def test_repeated_validations(self):
        """Test caching and repeated validation performance"""
        from backend.server import validate_document

        text = "Sample investment document with potential returns."

        times = []
        for _ in range(100):
            start = time.time()
            validate_document(text, 'financial', ['fca_uk'])
            elapsed = time.time() - start
            times.append(elapsed)

        avg_time = sum(times) / len(times)

        # Average should be very fast (< 10ms with caching)
        assert avg_time < 0.01, f"Average time: {avg_time:.4f}s"
```

### 5. Regression Tests

Prevent reintroduction of fixed bugs.

```python
# tests/regression/test_fixed_bugs.py

import pytest
from backend.modules.gdpr_uk.gates.lawful_basis import LawfulBasisGate

class TestRegressionSuite:
    def test_bug_123_false_positive_on_contract(self):
        """
        Bug #123: Lawful basis gate failed on valid contract basis
        Fixed: 2024-03-15
        """
        gate = LawfulBasisGate()

        text = """
        We process your data to fulfill our contract with you
        and provide the services you requested.
        """

        result = gate.check(text, 'privacy_policy')

        # Should pass - contract is valid lawful basis
        assert result['status'] == 'PASS', \
            "Regression: Bug #123 - false positive on contract basis"

    def test_bug_145_unicode_handling(self):
        """
        Bug #145: Gate crashed on unicode characters
        Fixed: 2024-03-20
        """
        gate = LawfulBasisGate()

        text = """
        We process your data based on your consent.
        Contact us at: hello@company.co.uk
        © 2024 Company Ltd
        """

        # Should not crash
        result = gate.check(text, 'privacy_policy')
        assert 'status' in result

    def test_bug_167_case_sensitivity(self):
        """
        Bug #167: Gate missed violations due to case sensitivity
        Fixed: 2024-04-01
        """
        from backend.modules.fca_uk.gates.fair_clear_not_misleading import FairClearNotMisleadingGate

        gate = FairClearNotMisleadingGate()

        # Should detect regardless of case
        texts = [
            "GUARANTEED RETURNS OF 10%",
            "guaranteed returns of 10%",
            "Guaranteed Returns Of 10%",
        ]

        for text in texts:
            result = gate.check(text, 'financial')
            assert result['status'] == 'FAIL', \
                f"Regression: Bug #167 - case sensitivity issue with: {text}"
```

## Test Coverage Goals

### Minimum Coverage Targets

| Component | Coverage Target |
|-----------|----------------|
| Gate logic | 95%+ |
| Pattern matching | 90%+ |
| Error handling | 100% |
| Integration paths | 85%+ |

### Coverage Measurement

```bash
# Run tests with coverage
pytest --cov=backend --cov-report=html --cov-report=term

# View coverage report
open htmlcov/index.html

# Check specific module
pytest --cov=backend.modules.fca_uk --cov-report=term
```

## Test Data Management

### Creating Test Fixtures

```python
# tests/semantic/gold_fixtures/fca_uk/guaranteed_returns_01.json

{
    "name": "guaranteed_returns_basic",
    "violation_type": "guaranteed_returns",
    "text": "Invest now for guaranteed 15% annual returns. Zero risk, secure your future today!",
    "document_type": "financial",
    "expected_gate_failures": [
        "fair_clear_not_misleading",
        "risk_warnings"
    ],
    "severity": "critical",
    "legal_source": "FCA COBS 4.2.1",
    "notes": "Basic guaranteed returns claim with pressure tactics"
}
```

### Fixture Organization

```
tests/semantic/gold_fixtures/
├── fca_uk/
│   ├── guaranteed_returns_01.json
│   ├── pressure_tactics_01.json
│   └── past_performance_01.json
├── gdpr_uk/
│   ├── vague_purposes_01.json
│   └── invalid_consent_01.json
├── tax_uk/
│   ├── invalid_vat_01.json
│   └── missing_invoice_fields_01.json
└── hr_scottish/
    ├── missing_notice_01.json
    └── no_appeal_rights_01.json
```

## Continuous Testing

### Pre-commit Hooks

```bash
# .pre-commit-config.yaml

repos:
  - repo: local
    hooks:
      - id: pytest-check
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
        args: ['tests/unit/', '-v']
```

### CI/CD Pipeline

```yaml
# .github/workflows/test.yml

name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run unit tests
        run: pytest tests/unit/ -v

      - name: Run integration tests
        run: pytest tests/integration/ -v

      - name: Run gold standard tests
        run: pytest tests/semantic/ -v

      - name: Check coverage
        run: pytest --cov=backend --cov-fail-under=85
```

## Best Practices

1. **Test pyramid**: Many unit tests, fewer integration tests, some E2E tests
2. **Independent tests**: Each test should run independently
3. **Deterministic**: Tests should always produce same results
4. **Fast**: Unit tests should complete in milliseconds
5. **Clear assertions**: Use descriptive assertion messages
6. **Test edge cases**: Empty strings, None, unicode, special characters
7. **Document regressions**: Every bug fix gets a regression test
8. **Maintain fixtures**: Keep gold standard fixtures up-to-date

## Debugging Failed Tests

```python
# Use pytest fixtures for debugging

@pytest.fixture
def debug_mode():
    import logging
    logging.basicConfig(level=logging.DEBUG)
    return True

def test_with_debug(debug_mode):
    # Test will show debug output
    gate = MyGate()
    result = gate.check("test text", "doc_type")
    print(f"Debug: {result}")  # Will be visible with -s flag
    assert result['status'] == 'PASS'
```

```bash
# Run with verbose output
pytest -v -s tests/unit/test_my_gate.py

# Run single test
pytest tests/unit/test_my_gate.py::TestMyGate::test_specific_case -v

# Run with debugging on failure
pytest --pdb tests/unit/
```

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [Python unittest](https://docs.python.org/3/library/unittest.html)
- [Coverage.py](https://coverage.readthedocs.io/)
- LOKI test fixtures: `backend/tests/semantic/gold_fixtures/`
