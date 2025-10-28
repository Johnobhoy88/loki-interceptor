---
name: loki-testing-expert
description: Expert in testing LOKI compliance system, including validation testing, correction testing, gate testing, integration testing, and test automation
---

# LOKI Testing Expert Skill

You are an expert in testing the LOKI compliance checking system. This skill provides comprehensive knowledge of testing procedures, test suites, validation testing, and quality assurance.

## Testing Philosophy

LOKI uses **deterministic, repeatable testing** with:
- No AI/ML components (fully rule-based)
- Predictable outputs for given inputs
- Regression testing for all modules
- Integration testing across components
- Unit testing for individual gates

## Test Structure

### Test Locations

```
loki-interceptor/
├── backend/
│   ├── core/
│   │   └── test_advanced_corrector.py   # Correction system tests
│   └── modules/
│       ├── fca_uk/
│       │   └── tests/                    # FCA gate tests
│       ├── gdpr_uk/
│       │   └── tests/                    # GDPR gate tests
│       ├── tax_uk/
│       │   └── tests/                    # Tax gate tests
│       ├── nda_uk/
│       │   └── tests/                    # NDA gate tests
│       └── hr_scottish/
│           └── tests/                    # HR gate tests
└── frontend/
    └── __tests__/                        # Frontend component tests
```

## Test Types

### 1. Unit Tests (Gate Level)

**Purpose:** Test individual compliance gates

**Pattern:**
```python
def test_gate_name():
    # 1. Setup
    gate = GateClass()
    text = "Test document text"

    # 2. Execute
    result = gate.check(text, document_type="financial")

    # 3. Assert
    assert result['status'] == 'FAIL'
    assert result['severity'] == 'critical'
    assert 'expected message' in result['message']
```

**Example: FCA Risk Warning Test**
```python
def test_risk_benefit_balance_fail():
    from backend.modules.fca_uk.gates.risk_benefit_balance import RiskBenefitBalanceGate

    gate = RiskBenefitBalanceGate()

    # Document with benefits but no risk warnings
    text = """
    Investment Opportunity
    High returns! Significant profit potential!
    Excellent performance guaranteed!
    """

    result = gate.check(text, "financial")

    assert result['status'] == 'FAIL'
    assert result['severity'] == 'high'
    assert 'without any risk warnings' in result['message'].lower()
    assert len(result['spans']) > 0  # Should mark benefit mentions
```

**Example: GDPR Consent Test**
```python
def test_forced_consent_detection():
    from backend.modules.gdpr_uk.gates.consent import ConsentGate

    gate = ConsentGate()

    text = """
    Privacy Policy
    By using this website, you automatically agree to our data collection.
    """

    result = gate.check(text, "privacy")

    assert result['status'] == 'FAIL'
    assert result['severity'] == 'critical'
    assert 'forced consent' in result['message'].lower()
    assert len(result['spans']) > 0
```

**Example: N/A (Not Applicable) Test**
```python
def test_gate_not_applicable():
    from backend.modules.fca_uk.gates.risk_benefit_balance import RiskBenefitBalanceGate

    gate = RiskBenefitBalanceGate()

    # Tax document - no investment mentions
    text = """
    VAT Registration Guide
    Complete this form to register for VAT.
    """

    result = gate.check(text, "tax")

    assert result['status'] == 'N/A'
    assert 'not applicable' in result['message'].lower()
```

### 2. Integration Tests (Module Level)

**Purpose:** Test complete module validation

**Pattern:**
```python
def test_module_validation():
    from backend.modules.fca_uk.module import get_gates

    gates = get_gates()
    text = "Test document"

    results = {}
    for gate in gates:
        result = gate.check(text, "financial")
        results[gate.name] = result

    # Verify all gates executed
    assert len(results) > 0

    # Check specific gates
    assert 'risk_benefit_balance' in results
```

**Example: Complete FCA Module Test**
```python
def test_fca_module_complete():
    from backend.modules.fca_uk.module import get_gates

    gates = get_gates()

    text = """
    Investment Product Notice

    This investment offers guaranteed returns of 10% annually!
    Risk-free opportunity with high profit potential!
    Past performance shows excellent results.
    """

    results = {}
    for gate in gates:
        result = gate.check(text, "financial")
        results[gate.name] = result

    # Should have multiple failures
    assert results['fair_clear_not_misleading']['status'] == 'FAIL'  # "guaranteed"
    assert results['risk_benefit_balance']['status'] == 'FAIL'  # No risk warnings

    # Count critical failures
    critical_failures = [r for r in results.values() if r.get('severity') == 'critical']
    assert len(critical_failures) > 0
```

### 3. Correction Tests

**Purpose:** Test document correction system

**Test Suites:**

#### A. Initial Test Suite
**Location:** `backend/core/test_advanced_corrector.py`
**Tests:** 8 tests covering basic features
**Status:** Baseline tests (deprecated by comprehensive suite)

#### B. Enhanced Module Tests
**Location:** `backend/core/test_enhanced_corrections.py`
**Tests:** 6 comprehensive tests
**Coverage:**
1. FCA corrections (fair_clear, risk_benefit)
2. GDPR corrections (consent violations)
3. Tax UK corrections (VAT threshold)
4. NDA UK corrections (whistleblowing)
5. HR Scottish corrections (accompaniment rights)
6. Multi-module corrections

**Running Enhanced Tests:**
```bash
cd backend/core
python3 test_enhanced_corrections.py
```

**Expected Output:**
```
✓ Test 1: FCA corrections - PASS
✓ Test 2: GDPR corrections - PASS
✓ Test 3: Tax UK corrections - PASS
✓ Test 4: NDA UK corrections - PASS
✓ Test 5: HR Scottish corrections - PASS
✓ Test 6: Multi-module corrections - PASS

All 6 tests passed!
```

#### C. Comprehensive Production Test Suite
**Location:** `backend/core/comprehensive_test_runner.py`
**Tests:** 11 total tests
**Status:** ✅ PRODUCTION READY (11/11 PASSED)

**Test Breakdown:**
1. **Primary Test Suite** (6 tests)
   - FCA corrections
   - GDPR corrections
   - Tax UK corrections
   - NDA UK corrections
   - HR Scottish corrections
   - Multi-module corrections

2. **Pattern Coverage Test** (1 test)
   - Verifies all 107 patterns are registered
   - Module breakdown: FCA (23), GDPR (31), Tax (18), NDA (15), HR (20)

3. **Determinism Test** (1 test)
   - Runs same input 3 times
   - Verifies byte-identical outputs
   - SHA256 hash verification

4. **Performance Benchmark** (1 test)
   - Tests small (<1KB), medium (1-10KB), large (10-100KB) documents
   - Average: 5.15M chars/sec
   - Target: 10K chars/sec (515x above threshold)

5. **Specific Pattern Tests** (7 tests)
   - FCA risk warnings
   - GDPR forced consent
   - Tax VAT threshold
   - NDA whistleblowing
   - HR accompaniment rights
   - Multi-correction scenarios
   - Context-aware filtering

6. **Integration Test** (1 test)
   - End-to-end validation → correction workflow

**Running Comprehensive Tests:**
```bash
cd backend/core
python3 comprehensive_test_runner.py
```

**Production Test Results:**
```
✅ Primary Test Suite: 6/6 PASS
✅ Pattern Coverage: 107/107 verified
✅ Determinism: Perfect (3 identical runs)
✅ Performance: 5.15M chars/sec average
✅ Specific Patterns: 7/7 PASS
✅ Integration: PASS

Overall: 11/11 Tests PASSED (100%)
Status: PRODUCTION READY
```

**Example Test:**
```python
def test_vat_threshold_correction():
    from backend.core.corrector import DocumentCorrector

    text = "VAT registration threshold is £85,000."

    validation_results = {
        'validation': {
            'modules': {
                'tax_uk': {
                    'gates': {
                        'vat_threshold': {
                            'status': 'FAIL',
                            'severity': 'medium'
                        }
                    }
                }
            }
        }
    }

    corrector = DocumentCorrector()
    result = corrector.correct_document(text, validation_results)

    # Verify correction applied
    assert '£90,000' in result['corrected']
    assert '£85,000' not in result['corrected']
    assert result['correction_count'] > 0
    assert result['unchanged'] == False
```

**Determinism Test:**
```python
def test_correction_determinism():
    from backend.core.corrector import DocumentCorrector

    text = "By using this site, you agree to our terms."

    validation_results = {
        'validation': {
            'modules': {
                'gdpr_uk': {
                    'gates': {
                        'consent': {
                            'status': 'FAIL',
                            'severity': 'critical'
                        }
                    }
                }
            }
        }
    }

    corrector = DocumentCorrector()

    # Run correction 3 times
    result1 = corrector.correct_document(text, validation_results)
    result2 = corrector.correct_document(text, validation_results)
    result3 = corrector.correct_document(text, validation_results)

    # Verify determinism
    assert result1['corrected'] == result2['corrected'] == result3['corrected']
    assert result1['determinism']['output_hash'] == result2['determinism']['output_hash']
    assert result1['determinism']['output_hash'] == result3['determinism']['output_hash']
```

### 4. API Tests

**Purpose:** Test API endpoints

**Validation Endpoint Test:**
```bash
# POST /api/validate
curl -X POST http://localhost:3001/api/validate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Investment with high returns and no risk!",
    "document_type": "financial"
  }' | jq

# Expected response:
# {
#   "validation": {
#     "overall_status": "FAIL",
#     "modules": {
#       "fca_uk": {
#         "status": "FAIL",
#         "gates": {
#           "fair_clear_not_misleading": {
#             "status": "FAIL",
#             "severity": "critical"
#           }
#         }
#       }
#     }
#   }
# }
```

**Correction Endpoint Test:**
```bash
# POST /api/correct
curl -X POST http://localhost:3001/api/correct \
  -H "Content-Type: application/json" \
  -d '{
    "text": "VAT threshold is £85,000",
    "validation_results": {...}
  }' | jq

# Expected: corrected text with £90,000
```

**Health Check Test:**
```bash
# GET /api/health
curl http://localhost:3001/api/health

# Expected: {"status": "ok"}
```

### 5. End-to-End Tests

**Purpose:** Test complete user workflows

**Example: Complete Validation and Correction Flow**
```python
def test_complete_validation_correction_flow():
    # 1. Validate document
    text = "By using this website, you agree to everything. VAT is £85,000."

    validation_response = validate_document(text, "privacy")

    # 2. Verify validation detected issues
    assert validation_response['validation']['overall_status'] == 'FAIL'

    # 3. Apply corrections
    correction_response = correct_document(text, validation_response)

    # 4. Verify corrections applied
    corrected_text = correction_response['corrected']
    assert 'automatically agree' not in corrected_text
    assert '£90,000' in corrected_text

    # 5. Re-validate corrected document
    revalidation_response = validate_document(corrected_text, "privacy")

    # 6. Verify fewer failures
    original_failures = count_failures(validation_response)
    corrected_failures = count_failures(revalidation_response)
    assert corrected_failures < original_failures
```

## Test Data

### Sample Documents

**FCA Financial Document (Should Fail):**
```python
FCA_FAIL_SAMPLE = """
Investment Opportunity - Guaranteed Returns!

Our fund offers risk-free investment with guaranteed returns of 15% annually.
Past performance has been exceptional with no losses ever recorded.
This is a can't-miss opportunity for high returns!

Invest now for guaranteed profit!
"""
```

**FCA Financial Document (Should Pass):**
```python
FCA_PASS_SAMPLE = """
Investment Product Information

⚠️ RISK WARNING: The value of investments can fall as well as rise
and you may get back less than you invest. Past performance is not
a reliable indicator of future results.

This product offers the potential for returns based on market performance.
Capital is at risk and returns are not guaranteed.

TARGET MARKET: This product is designed for experienced investors with
high risk tolerance and long-term investment objectives.

COMPLAINTS: If you have a complaint, you may refer it to the
Financial Ombudsman Service (www.financial-ombudsman.org.uk).
"""
```

**GDPR Privacy Policy (Should Fail):**
```python
GDPR_FAIL_SAMPLE = """
Privacy Policy

By using this website, you automatically agree to our data collection
and processing practices. We collect your personal information for
marketing purposes and share it with our partners.

Continued use of our service means you consent to these terms.
"""
```

**GDPR Privacy Policy (Should Pass):**
```python
GDPR_PASS_SAMPLE = """
Privacy Policy

LAWFUL BASIS: We process your personal data based on your explicit consent.

We request your explicit consent to collect and process your personal data
for the following purposes: [specify purposes].

WITHDRAWAL OF CONSENT: You may withdraw your consent at any time by
contacting us at privacy@example.com.

YOUR RIGHTS: Under GDPR, you have the right to:
• Access your personal data
• Rectify inaccurate data
• Erase your data
• Restrict processing
• Data portability
• Object to processing

To exercise these rights, contact us at privacy@example.com.

RETENTION: We will retain your personal data for [specify period] or
as required by law.
"""
```

**Tax Document (Should Fail):**
```python
TAX_FAIL_SAMPLE = """
VAT Registration Information

The VAT registration threshold is £85,000.
If your turnover exceeds £83,000, you must register.

URGENT: Pay your tax debt via iTunes gift cards immediately or
face immediate arrest!
"""
```

**NDA Document (Should Fail):**
```python
NDA_FAIL_SAMPLE = """
NON-DISCLOSURE AGREEMENT

The Recipient shall not disclose any Confidential Information to
any third party under any circumstances whatsoever, in perpetuity.

This prohibition shall apply indefinitely and without exception.
"""
```

**Employment Document (Should Fail):**
```python
HR_FAIL_SAMPLE = """
Disciplinary Hearing Notice

You are required to attend a disciplinary meeting on [date].

You may not bring a lawyer or legal representative to this meeting.
You must attend alone.
"""
```

## Test Execution

### Running All Tests

**Backend Tests:**
```bash
# Run correction tests
cd backend/core
python3 test_advanced_corrector.py

# Expected output:
# ✓ All tests passed
# ✓ Advanced correction system is operational
# ✓ Determinism verified
```

**Frontend Tests (if using Jest):**
```bash
cd frontend
npm test

# Run specific test file
npm test -- ValidationForm.test.js

# Run with coverage
npm test -- --coverage
```

### Manual Testing Workflow

**1. Test Gate Individually:**
```python
from backend.modules.fca_uk.gates.risk_benefit_balance import RiskBenefitBalanceGate

gate = RiskBenefitBalanceGate()
result = gate.check("Test document text", "financial")

print(f"Status: {result['status']}")
print(f"Message: {result['message']}")
```

**2. Test Module:**
```python
from backend.modules.fca_uk.module import get_gates

gates = get_gates()
print(f"FCA UK has {len(gates)} gates")

for gate in gates:
    print(f"- {gate.name} (severity: {gate.severity})")
```

**3. Test Validation Engine:**
```python
from backend.core.engine import ValidationEngine

engine = ValidationEngine()
result = engine.validate("Test document", "financial")

print(f"Overall status: {result['validation']['overall_status']}")
```

**4. Test Corrector:**
```python
from backend.core.corrector import DocumentCorrector

corrector = DocumentCorrector()

# Get statistics
stats = corrector.get_correction_statistics()
print(f"Total patterns: {stats['total_patterns']}")

# Test pattern match
match = corrector.test_pattern_match("£85,000", "vat_threshold")
print(f"Would correct: {match['would_correct']}")
```

## Test Coverage

### Gate Coverage Checklist

For each gate, verify:

- [ ] **PASS** case - Compliant document returns PASS
- [ ] **FAIL** case - Non-compliant document returns FAIL
- [ ] **WARNING** case - Potential issue returns WARNING (if applicable)
- [ ] **N/A** case - Irrelevant document returns N/A
- [ ] **Spans** - Violations are marked with spans
- [ ] **Suggestions** - Actionable suggestions provided
- [ ] **Legal source** - Legal reference included

### Module Coverage Checklist

For each module, verify:

- [ ] All gates registered
- [ ] All gates executable
- [ ] No duplicate gate names
- [ ] Module-level status calculated correctly
- [ ] All gates have tests

### Correction Coverage Checklist

- [ ] Regex patterns match correctly
- [ ] Templates insert at correct positions
- [ ] Structural reorganization works
- [ ] Determinism verified (3+ runs)
- [ ] Context-aware filtering works
- [ ] Multi-level correction works
- [ ] Validation catches bad corrections

## Regression Testing

### When to Run Regression Tests

Run full regression suite when:
- Modifying gate logic
- Adding new gates
- Updating correction patterns
- Changing validation engine
- Before merging to main
- Before production deployment

### Regression Test Suite

**Create:** `backend/tests/regression_suite.py`

```python
def run_regression_tests():
    """Run all regression tests"""
    results = {
        'fca_uk': test_fca_module(),
        'gdpr_uk': test_gdpr_module(),
        'tax_uk': test_tax_module(),
        'nda_uk': test_nda_module(),
        'hr_scottish': test_hr_module(),
        'corrector': test_corrector_system()
    }

    # Report
    total = sum(len(r) for r in results.values())
    passed = sum(sum(1 for t in r if t['passed']) for r in results.values())

    print(f"\nRegression Tests: {passed}/{total} passed")

    return all(all(t['passed'] for t in r) for r in results.values())
```

## Performance Testing

### Response Time Tests

```python
import time

def test_validation_performance():
    """Validate large document performance"""
    # Generate large document (10KB)
    text = "Investment opportunity. " * 1000

    start = time.time()
    result = validate_document(text, "financial")
    duration = time.time() - start

    # Should complete in <1 second
    assert duration < 1.0
    print(f"Validation took {duration*1000:.2f}ms")
```

### Correction Performance Tests

```python
def test_correction_performance():
    """Test correction speed"""
    text = "By using this site you agree. VAT is £85,000. " * 100

    validation_results = validate_document(text, "privacy")

    start = time.time()
    result = correct_document(text, validation_results)
    duration = time.time() - start

    # Should complete in <2 seconds
    assert duration < 2.0
    print(f"Correction took {duration*1000:.2f}ms")
```

## Testing Best Practices

1. **Test edge cases** - Empty strings, very long documents, special characters
2. **Test N/A logic** - Verify gates return N/A for irrelevant documents
3. **Verify spans** - Check violation marking is accurate
4. **Test determinism** - Run multiple times, verify identical results
5. **Check suggestions** - Ensure actionable correction suggestions
6. **Test all severities** - Critical, high, medium, low
7. **Integration test** - Test complete workflows
8. **Performance test** - Check response times
9. **Regression test** - Verify old functionality still works
10. **Document tests** - Add comments explaining what's tested

## Debugging Failed Tests

### Common Test Failures

**1. Gate Returns Wrong Status**

Check:
- `_is_relevant()` logic
- Pattern matching regex
- Status determination logic
- Severity assignment

**2. Spans Not Generated**

Check:
- Regex patterns have match groups
- `re.finditer()` used instead of `re.search()`
- Span structure includes required fields

**3. Correction Not Applied**

Check:
- Pattern registered correctly
- Gate ID matches pattern
- Strategy `can_apply()` returns true
- Replacement text is different

**4. Determinism Fails**

Check:
- No random elements
- Gates sorted alphabetically
- Strategies sorted by priority
- No timing dependencies

### Debug Techniques

**Print Debug Info:**
```python
def test_gate_debug():
    gate = RiskBenefitBalanceGate()
    text = "Test document"

    # Check relevance
    print(f"Is relevant: {gate._is_relevant(text)}")

    # Check result
    result = gate.check(text, "financial")
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    print(f"Spans: {result.get('spans', [])}")

    # Detailed inspection
    import json
    print(json.dumps(result, indent=2))
```

**Trace Execution:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now all debug logs will appear
result = gate.check(text, "financial")
```

## CI/CD Integration

### GitHub Actions Test Workflow

**File:** `.github/workflows/test.yml`

```yaml
name: Run Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run comprehensive correction tests
        run: |
          cd backend/core
          python3 comprehensive_test_runner.py

      - name: Run enhanced module tests
        run: |
          cd backend/core
          python3 test_enhanced_corrections.py

      - name: Run gate tests
        run: |
          python3 -m pytest backend/modules/*/tests/

      - name: Verify test results
        run: |
          cd backend/core
          if [ -f test_results.json ]; then
            echo "Test results generated successfully"
            cat test_results.json
          fi
```

## Test Reporting

### Generate Test Report

```python
def generate_test_report():
    """Generate comprehensive test report"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'modules': {},
        'correction_system': {},
        'summary': {}
    }

    # Test each module
    for module_id in ['fca_uk', 'gdpr_uk', 'tax_uk', 'nda_uk', 'hr_scottish']:
        report['modules'][module_id] = test_module(module_id)

    # Test correction system
    report['correction_system'] = test_correction_system()

    # Calculate summary
    total_tests = sum(m['total'] for m in report['modules'].values())
    passed_tests = sum(m['passed'] for m in report['modules'].values())

    report['summary'] = {
        'total': total_tests,
        'passed': passed_tests,
        'failed': total_tests - passed_tests,
        'pass_rate': f"{(passed_tests/total_tests*100):.1f}%"
    }

    # Save report
    with open('test_report.json', 'w') as f:
        json.dump(report, f, indent=2)

    return report
```

## Production Test Results

### Current Test Status (As of Latest Build)

**Correction System: ✅ PRODUCTION READY**
- Total Tests: 11/11 PASSED (100%)
- Pattern Coverage: 107/107 patterns verified
- Determinism: Perfect (byte-identical across 3 runs)
- Performance: 5.15M chars/sec (515x above 10K threshold)
- Integration: End-to-end workflow verified

**Test Report:** `TEST_REPORT.md` (22KB, 697 lines)
**Test Results:** `backend/core/test_results.json`

### Performance Metrics

**Verified Benchmarks:**
- Small documents (<1KB): <5ms per correction
- Medium documents (1-10KB): <20ms per correction
- Large documents (10-100KB): <200ms per correction
- Average throughput: 5.15 million characters/second

**Determinism Verification:**
```
Run 1 Hash: [identical]
Run 2 Hash: [identical]
Run 3 Hash: [identical]
Status: PERFECT DETERMINISM ✅
```

### Bug Fixes Verified

**Fix 1: Bidirectional Pattern Matching**
- Test: Pattern "accompaniment" matches gate "accompaniment_restrictions"
- Result: ✅ PASS
- Location: `backend/core/correction_strategies.py:64-68`

**Fix 2: GDPR Consent Regex**
- Test: Pattern matches both "you agree" and "you agree to"
- Result: ✅ PASS
- Location: `backend/core/correction_patterns.py:322`

### Coverage Report

**Module Coverage (107 patterns):**
- FCA UK: 23 patterns (100% of critical gates)
- GDPR UK: 31 patterns (100% of critical gates)
- Tax UK: 18 patterns (100% of critical gates)
- NDA UK: 15 patterns (100% of critical gates)
- HR Scottish: 20 patterns (100% of critical gates)

**Strategy Coverage:**
- Suggestion Extraction: ✅ Verified
- Regex Replacement: ✅ Verified (61 patterns)
- Template Insertion: ✅ Verified (44 patterns)
- Structural Reorganization: ✅ Verified (2 patterns)

**Test Files:**
1. `backend/core/test_advanced_corrector.py` - 8 baseline tests
2. `backend/core/test_enhanced_corrections.py` - 6 module tests
3. `backend/core/comprehensive_test_runner.py` - 11 production tests
4. `TEST_REPORT.md` - Complete production readiness report

## When to Use This Skill

Activate this skill when:
- Writing tests for new gates
- Testing validation logic
- Verifying correction behavior
- Debugging test failures
- Setting up CI/CD testing
- Running regression tests
- Performance testing
- Integration testing
- Generating test reports
- Reviewing test coverage
