# Correction Testing Guide

## 🎯 Overview

This guide provides comprehensive documentation for testing the LOKI Correction System. The testing framework ensures corrections are accurate, deterministic, performant, and maintain document quality.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Test Structure](#test-structure)
3. [Running Tests](#running-tests)
4. [Test Categories](#test-categories)
5. [Metrics and Reporting](#metrics-and-reporting)
6. [Writing New Tests](#writing-new-tests)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Installation

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Additional libraries for property-based testing
pip install hypothesis
```

### Run All Tests

```bash
# Run all correction tests
./scripts/run_correction_tests.sh --all

# Run with coverage
./scripts/run_correction_tests.sh --all --coverage --html

# Run specific test suite
./scripts/run_correction_tests.sh --accuracy
```

### Quick Test Commands

```bash
# Accuracy tests (100+ test cases)
pytest tests/correction/test_accuracy.py -v

# Regression tests
pytest tests/correction/test_regression.py -v

# Property-based tests
pytest tests/correction/test_property_based.py -v

# Performance benchmarks
pytest tests/correction/test_performance.py --benchmark-only

# Adversarial tests
pytest tests/correction/adversarial/ -v
```

---

## 📁 Test Structure

```
tests/correction/
├── __init__.py
├── test_accuracy.py          # 100+ accuracy test cases
├── test_regression.py         # Regression prevention tests
├── test_property_based.py     # Property-based tests (Hypothesis)
├── test_performance.py        # Performance benchmarks
└── adversarial/
    ├── __init__.py
    ├── test_edge_cases.py     # Edge case tests
    └── test_corner_cases.py   # Corner case tests

backend/testing/
├── __init__.py
├── correction_metrics.py      # Metrics collection
├── visual_diff.py             # Visual diff tools
└── quality_scorer.py          # Quality scoring

scripts/
└── run_correction_tests.sh    # Test runner script
```

---

## 🧪 Test Categories

### 1. Accuracy Tests (`test_accuracy.py`)

**Purpose**: Verify corrections are accurate across all regulatory modules.

**Coverage**:
- FCA UK corrections (30 tests)
- GDPR UK corrections (25 tests)
- Tax UK corrections (20 tests)
- NDA UK corrections (15 tests)
- HR Scottish corrections (15 tests)
- Cross-module corrections (10 tests)

**Example**:
```python
def test_risk_warning_correction(synthesizer):
    """Test risk warning is properly formatted."""
    text = "investments can go down as well as up"
    gates = [('risk_warning', {'status': 'FAIL', 'severity': 'high'})]

    result = synthesizer.synthesize_corrections(text, gates)

    assert result['corrected'] != text
    assert 'fall as well as rise' in result['corrected'].lower()
    assert len(result['corrections']) > 0
```

**Run**:
```bash
pytest tests/correction/test_accuracy.py -v
pytest tests/correction/test_accuracy.py::TestFCACorrections -v
```

### 2. Regression Tests (`test_regression.py`)

**Purpose**: Prevent previously fixed bugs from reoccurring.

**Coverage**:
- Historical bug prevention (10 tests)
- Snapshot testing (5 tests)
- Determinism tests (5 tests)
- Quality regression (5 tests)
- Performance regression (3 tests)
- Baseline comparisons (3 tests)

**Example**:
```python
def test_bug_001_double_correction_prevention(synthesizer_full):
    """
    BUG-001: Prevent same correction being applied twice
    """
    text = "GUARANTEED high returns!"
    gates = [
        ('fair_clear', {'status': 'FAIL', 'severity': 'critical'}),
        ('risk_benefit', {'status': 'FAIL', 'severity': 'high'})
    ]

    result = synthesizer_full.synthesize_corrections(text, gates)

    # Count occurrences - should appear once, not multiple times
    potential_count = result['corrected'].lower().count('potential')
    assert potential_count <= 2, "Correction applied multiple times (BUG-001)"
```

**Run**:
```bash
pytest tests/correction/test_regression.py -v
pytest tests/correction/test_regression.py::TestHistoricalBugPrevention -v
```

### 3. Property-Based Tests (`test_property_based.py`)

**Purpose**: Automatically generate test cases using Hypothesis library to verify invariants.

**Properties Tested**:
- Determinism (same input → same output)
- Idempotency (multiple applications converge)
- Structure preservation
- No data loss (emails, URLs, phones preserved)
- Length bounds (reasonable growth/shrinkage)
- Unicode safety
- Metadata consistency

**Example**:
```python
from hypothesis import given, strategies as st

@given(
    text=st.text(min_size=10, max_size=200),
    gates=gates_list_strategy
)
def test_determinism_property(synthesizer_full, text, gates):
    """Property: Same input always produces same output."""
    assume(len(text) > 0)

    result1 = synthesizer_full.synthesize_corrections(text, gates)
    result2 = synthesizer_full.synthesize_corrections(text, gates)

    assert result1['corrected'] == result2['corrected']
    assert result1['correction_count'] == result2['correction_count']
```

**Run**:
```bash
pytest tests/correction/test_property_based.py -v
pytest tests/correction/test_property_based.py::TestDeterminismProperty -v
```

### 4. Performance Tests (`test_performance.py`)

**Purpose**: Benchmark correction performance and establish baselines.

**Benchmarks**:
- Document size (short, medium, long, very long)
- Gate complexity (few gates, many gates)
- Strategy-specific performance
- Real-world scenarios
- Memory usage

**Example**:
```python
def test_benchmark_short_document(benchmark, synthesizer_full, short_document, failing_gates_few):
    """
    Benchmark: Short document correction (< 1KB)
    Target: < 100ms
    """
    result = benchmark(
        synthesizer_full.synthesize_corrections,
        short_document,
        failing_gates_few
    )

    assert result['correction_count'] >= 0
```

**Run**:
```bash
# Run benchmarks only
pytest tests/correction/test_performance.py --benchmark-only

# Compare with previous runs
pytest tests/correction/test_performance.py --benchmark-compare

# Save benchmark results
pytest tests/correction/test_performance.py --benchmark-autosave
```

### 5. Adversarial Tests (`adversarial/`)

**Purpose**: Test edge cases and unusual inputs that might break the system.

**Coverage**:
- Extreme lengths (very short, very long)
- Special characters (unicode, control chars)
- Malformed input (unbalanced brackets, unclosed tags)
- Repeating patterns
- Boundary values
- Encoding issues
- Regex edge cases

**Example**:
```python
def test_extremely_long_line(synthesizer):
    """Test document with one extremely long line (10KB)."""
    text = "GUARANTEED " * 1000  # 10KB single line
    gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

    result = synthesizer.synthesize_corrections(text, gates)

    assert 'GUARANTEED' not in result['corrected'] or len(result['corrected']) > len(text)
```

**Run**:
```bash
pytest tests/correction/adversarial/ -v
pytest tests/correction/adversarial/test_edge_cases.py -v
pytest tests/correction/adversarial/test_corner_cases.py -v
```

---

## 📊 Metrics and Reporting

### Metrics Collection

```python
from backend.testing.correction_metrics import CorrectionMetricsCollector

collector = CorrectionMetricsCollector()

# Start timing
collector.start_correction("doc_123", "financial")

# Apply corrections
result = synthesizer.synthesize_corrections(text, gates)

# Record metrics
metrics = collector.end_correction(
    original_text=text,
    correction_result=result,
    gate_results=gates,
    violations_before=5,
    violations_after=1
)

# Get summary
summary = collector.get_summary()
print(f"Average processing time: {summary['performance']['avg_processing_time_ms']:.2f}ms")
```

### Visual Diff

```python
from backend.testing.visual_diff import VisualDiffer, DiffFormat

differ = VisualDiffer()

# Text diff (terminal)
text_diff = differ.create_diff(original, corrected, DiffFormat.TEXT)
print(text_diff)

# HTML diff (browser)
html_diff = differ.create_diff(original, corrected, DiffFormat.HTML)
with open('diff.html', 'w') as f:
    f.write(html_diff)

# Get change statistics
stats = differ.get_change_statistics(original, corrected)
print(f"Similarity: {stats['similarity_ratio']:.2%}")
```

### Quality Scoring

```python
from backend.testing.quality_scorer import CorrectionQualityScorer

scorer = CorrectionQualityScorer()

score = scorer.score_correction(
    original_text=original,
    corrected_text=corrected,
    correction_result=result,
    gates_before=gates_before,
    gates_after=gates_after,
    processing_time_ms=150.5
)

print(f"Quality Score: {score.overall_score}/100 ({score.grade})")
print(f"Completeness: {score.completeness_score}")
print(f"Accuracy: {score.accuracy_score}")
print(f"Preservation: {score.preservation_score}")

if score.issues:
    print("Issues:", score.issues)
if score.recommendations:
    print("Recommendations:", score.recommendations)
```

---

## 📝 Running Tests

### Using Test Runner Script

```bash
# Run all tests
./scripts/run_correction_tests.sh --all

# Run specific suite
./scripts/run_correction_tests.sh --accuracy
./scripts/run_correction_tests.sh --regression
./scripts/run_correction_tests.sh --property
./scripts/run_correction_tests.sh --performance
./scripts/run_correction_tests.sh --adversarial

# With coverage
./scripts/run_correction_tests.sh --all --coverage --html

# With benchmarks
./scripts/run_correction_tests.sh --performance --benchmark

# Parallel execution (faster)
./scripts/run_correction_tests.sh --all --parallel

# Generate comprehensive report
./scripts/run_correction_tests.sh --all --coverage --report

# Verbose output
./scripts/run_correction_tests.sh --accuracy --verbose

# Quiet mode
./scripts/run_correction_tests.sh --accuracy --quiet
```

### Using Pytest Directly

```bash
# Run all correction tests
pytest tests/correction/ -v

# Run specific test file
pytest tests/correction/test_accuracy.py -v

# Run specific test class
pytest tests/correction/test_accuracy.py::TestFCACorrections -v

# Run specific test
pytest tests/correction/test_accuracy.py::TestFCACorrections::test_risk_warning_correction -v

# Run with markers
pytest tests/correction/ -m "not slow" -v

# Run with coverage
pytest tests/correction/ --cov=backend/core --cov-report=html

# Run benchmarks
pytest tests/correction/test_performance.py --benchmark-only

# Run with specific number of Hypothesis examples
pytest tests/correction/test_property_based.py --hypothesis-show-statistics
```

### Coverage Reporting

```bash
# Generate coverage report
pytest tests/correction/ --cov=backend/core --cov=backend/testing --cov-report=term-missing

# Generate HTML coverage report
pytest tests/correction/ --cov=backend/core --cov-report=html

# View HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

---

## ✍️ Writing New Tests

### Adding Accuracy Tests

```python
# tests/correction/test_accuracy.py

class TestNewModuleCorrections:
    """Test corrections for new module."""

    def test_new_pattern_correction(self, synthesizer):
        """Test new correction pattern."""
        text = "Text with new violation"
        gates = [('new_gate', {'status': 'FAIL', 'severity': 'high'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert result['correction_count'] > 0
        assert 'corrected text' in result['corrected'].lower()
```

### Adding Regression Tests

```python
# tests/correction/test_regression.py

def test_bug_NNN_description(synthesizer_full):
    """
    BUG-NNN: Brief description of bug

    Historical issue: Detailed explanation of what went wrong
    """
    # Setup that triggers the bug
    text = "problematic input"
    gates = [('gate', {'status': 'FAIL', 'severity': 'high'})]

    # Apply correction
    result = synthesizer_full.synthesize_corrections(text, gates)

    # Assert bug is fixed
    assert expected_behavior, "BUG-NNN regression detected"
```

### Adding Property Tests

```python
# tests/correction/test_property_based.py

from hypothesis import given, strategies as st

@given(
    text=st.text(min_size=10, max_size=100),
    gates=gates_list_strategy
)
def test_new_property(synthesizer_full, text, gates):
    """
    Property: Description of invariant being tested
    """
    assume(len(text) > 5)  # Add assumptions if needed

    result = synthesizer_full.synthesize_corrections(text, gates)

    # Assert property holds
    assert invariant_holds(result)
```

### Adding Performance Benchmarks

```python
# tests/correction/test_performance.py

def test_benchmark_new_scenario(benchmark, synthesizer_full):
    """
    Benchmark: Description
    Target: < XXXms
    """
    text = "test document"
    gates = [('gate', {'status': 'FAIL', 'severity': 'high'})]

    result = benchmark(
        synthesizer_full.synthesize_corrections,
        text,
        gates
    )

    assert result['correction_count'] >= 0
```

---

## ✅ Best Practices

### Test Design

1. **Deterministic Tests**: All tests must be deterministic (same input → same output)
2. **Isolated Tests**: Each test should be independent
3. **Clear Assertions**: Use descriptive assertion messages
4. **Test Names**: Use descriptive names that explain what is being tested
5. **Documentation**: Add docstrings explaining test purpose and rationale

### Test Organization

1. **Group Related Tests**: Use test classes to group related tests
2. **Use Fixtures**: Share common setup using pytest fixtures
3. **Mark Tests**: Use pytest markers for slow tests, integration tests, etc.

```python
@pytest.mark.slow
def test_very_large_document(synthesizer):
    """Test that takes a long time to run."""
    pass
```

### Performance Considerations

1. **Module-Scoped Fixtures**: Use module-scoped fixtures for expensive setup
2. **Parallel Execution**: Run tests in parallel when possible
3. **Skip Slow Tests**: Mark slow tests so they can be skipped in quick runs

```python
@pytest.fixture(scope="module")
def expensive_resource():
    """Create once per module."""
    return setup_expensive_resource()
```

### Coverage Goals

- **Target**: 95%+ coverage for correction code
- **Focus**: Core correction logic, strategies, patterns
- **Prioritize**: Critical paths and error handling

---

## 🔧 Troubleshooting

### Common Issues

#### Tests Failing Locally

```bash
# Update dependencies
pip install -r requirements-test.txt

# Clear pytest cache
pytest --cache-clear

# Run single test with verbose output
pytest tests/correction/test_accuracy.py::test_name -vv
```

#### Hypothesis Tests Failing

```bash
# Show more examples
pytest tests/correction/test_property_based.py --hypothesis-show-statistics

# Increase deadline
pytest tests/correction/test_property_based.py --hypothesis-deadline=5000
```

#### Benchmarks Not Running

```bash
# Install pytest-benchmark
pip install pytest-benchmark

# Run with benchmark flag
pytest tests/correction/test_performance.py --benchmark-only
```

#### Coverage Not Generated

```bash
# Install coverage tools
pip install pytest-cov coverage

# Run with coverage
pytest tests/correction/ --cov=backend/core --cov-report=term
```

### Getting Help

1. **Check Test Output**: Read failure messages carefully
2. **Run with -vv**: Get more detailed output
3. **Check Logs**: Review test logs for errors
4. **Review Code**: Check the correction code being tested
5. **Ask Team**: Reach out to team members for help

---

## 📈 Continuous Improvement

### Regular Tasks

1. **Run Full Suite**: Run all tests before committing
2. **Check Coverage**: Aim for 95%+ coverage
3. **Review Failures**: Investigate and fix failures promptly
4. **Update Tests**: Keep tests up-to-date with code changes
5. **Add Tests**: Add tests for new features and bug fixes

### Metrics to Monitor

- Test pass rate (target: 100%)
- Code coverage (target: 95%+)
- Performance benchmarks (detect regressions)
- Correction accuracy (via metrics)
- Quality scores (via quality scorer)

---

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [pytest-benchmark Documentation](https://pytest-benchmark.readthedocs.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)

---

## 🎓 Summary

This comprehensive testing framework ensures:

✅ **Accuracy**: 100+ test cases verify corrections are accurate
✅ **Regression Prevention**: Historical bugs don't reoccur
✅ **Property Invariants**: System properties hold across all inputs
✅ **Performance**: Corrections remain fast and efficient
✅ **Edge Cases**: Unusual inputs are handled correctly
✅ **Quality**: Corrections maintain document quality
✅ **Metrics**: Comprehensive metrics track system health

**Remember**: Tests are your safety net. Write them well, run them often, and trust them completely.
