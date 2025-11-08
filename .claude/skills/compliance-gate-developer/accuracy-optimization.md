# Accuracy Optimization

Strategies for reducing false positives and improving gate precision.

## Precision vs Recall Tradeoff

```
Precision = True Positives / (True Positives + False Positives)
Recall = True Positives / (True Positives + False Negatives)

LOKI Priority: HIGH PRECISION (minimize false positives)
- Better to miss some violations than flag compliant text
- False positives erode user trust
- Gates should only fail on genuine violations
```

## False Positive Reduction Strategies

### 1. Context-Aware Pattern Matching

**Problem:** Pattern matches unrelated text

```python
# BAD: Matches any mention of "risk"
pattern = r'\brisk\b'

# Document: "There is a risk of rain tomorrow"
# Result: FALSE POSITIVE (not investment risk)
```

**Solution:** Require investment context

```python
# GOOD: Only match risk in investment context
def check_risk_warning(text):
    # First check if document discusses investments
    investment_context = r'\b(?:invest|portfolio|return|fund|stock)\b'

    if not re.search(investment_context, text, re.IGNORECASE):
        return {'status': 'N/A'}  # Not applicable

    # Now check for risk warnings
    risk_warning = r'\b(?:capital|investment).*?risk\b'
    has_warning = bool(re.search(risk_warning, text, re.IGNORECASE))

    # Only fail if investment context exists but warning doesn't
    if not has_warning:
        return {'status': 'FAIL'}

    return {'status': 'PASS'}
```

### 2. Negative Lookah ead/Lookbehind

**Problem:** Pattern matches legitimate uses

```python
# BAD: Flags "past performance" even with disclaimer
pattern = r'\bpast\s+performance\b'

# Document: "Past performance is not a reliable guide to future results"
# Result: FALSE POSITIVE (disclaimer present)
```

**Solution:** Use negative lookahead

```python
# GOOD: Only flag if disclaimer is missing
pattern = r'\bpast\s+performance\b(?!.*(?:not.*(?:guarantee|reliable|indication)))'

# Matches: "We delivered 15% past performance"
# Doesn't match: "Past performance is not a reliable guide"
```

### 3. Whitelist Exceptions

**Problem:** Pattern flags valid regulatory language

```python
# BAD: Flags all instances of "guaranteed"
pattern = r'\bguarantee[d]?\b'

# Document: "Your deposits are guaranteed by the FSCS up to £85,000"
# Result: FALSE POSITIVE (FSCS guarantee is legitimate)
```

**Solution:** Whitelist exceptions

```python
def check_guarantees(text):
    # Find all guarantee claims
    guarantee_pattern = r'\bguarantee[d]?\s+(?:return|profit|income|yield)\b'
    matches = re.finditer(guarantee_pattern, text, re.IGNORECASE)

    # Whitelist: FSCS guarantee, regulatory guarantees
    whitelist_patterns = [
        r'\bFSCS\b.*\bguarantee',
        r'\bdeposit\s+protection\b.*\bguarantee',
        r'\bguaranteed\s+by\s+(?:the\s+)?government\b',
    ]

    violations = []
    for match in matches:
        context = text[max(0, match.start()-100):match.end()+100]

        # Check if match is whitelisted
        is_whitelisted = any(
            re.search(pattern, context, re.IGNORECASE)
            for pattern in whitelist_patterns
        )

        if not is_whitelisted:
            violations.append(match.group())

    if violations:
        return {'status': 'FAIL', 'violations': violations}

    return {'status': 'PASS'}
```

### 4. Proximity Requirements

**Problem:** Pattern matches distant references

```python
# BAD: Matches "VAT" and "number" anywhere in document
vat_pattern = r'\bVAT\b'
number_pattern = r'\bnumber\b'

# Document: "VAT is 20%. Call our number: 555-1234"
# Result: FALSE POSITIVE (not a VAT number)
```

**Solution:** Require proximity

```python
# GOOD: Match only when terms are close together
vat_number_pattern = r'\bVAT\s*(?:No\.?|Number)?\s*:?\s*([A-Z]{2}\d{9,12})\b'

# Matches: "VAT Number: GB123456789"
# Matches: "VAT: GB123456789"
# Doesn't match: distant references
```

### 5. Relevance Checking

**Problem:** Gate runs on irrelevant documents

```python
# BAD: NDA gates run on all documents
class WhistleblowingGate:
    def check(self, text, document_type):
        # Runs on everything, causes false positives
        if 'disclose' in text.lower():
            return {'status': 'FAIL'}
```

**Solution:** Implement relevance checking

```python
# GOOD: Only run on NDA-related documents
class WhistleblowingGate:
    def __init__(self):
        self.relevance_keywords = [
            'confidential', 'nda', 'non-disclosure',
            'proprietary', 'trade secret'
        ]

    def _is_relevant(self, text):
        """Check if document is likely an NDA"""
        text_lower = (text or '').lower()
        keyword_count = sum(1 for kw in self.relevance_keywords if kw in text_lower)
        return keyword_count >= 2

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A'}  # Not applicable

        # Now check for whistleblowing restrictions
        restriction = r'\bprohibit.*?(?:disclosure|reporting).*?(?:to\s+authorities)\b'
        if re.search(restriction, text, re.IGNORECASE):
            return {'status': 'FAIL'}

        return {'status': 'PASS'}
```

### 6. Multi-Stage Validation

**Problem:** Single pattern too broad or too narrow

```python
# BAD: Single broad pattern with many false positives
pattern = r'\binvest\b'  # Matches "investment", "investigate", etc.
```

**Solution:** Multi-stage validation

```python
def check_investment_suitability(text):
    # Stage 1: Check if suitability context exists
    suitability_context = r'\b(?:suitable|appropriate|ideal)\s+for\b'
    if not re.search(suitability_context, text, re.IGNORECASE):
        return {'status': 'N/A'}

    # Stage 2: Check if it's about investments
    investment_context = r'\b(?:invest|portfolio|fund|product)\b'
    if not re.search(investment_context, text, re.IGNORECASE):
        return {'status': 'N/A'}

    # Stage 3: Check for problematic universal suitability claims
    universal_suitability = r'\b(?:suitable|perfect)\s+for\s+(?:everyone|anyone|all)\b'
    if re.search(universal_suitability, text, re.IGNORECASE):
        return {
            'status': 'FAIL',
            'severity': 'high',
            'message': 'Universal suitability claim detected'
        }

    return {'status': 'PASS'}
```

## Testing for False Positives

### Create Adversarial Test Cases

```python
def test_false_positive_scenarios():
    gate = FairClearNotMisleadingGate()

    # Adversarial cases that should PASS
    false_positive_tests = [
        # Legitimate FSCS guarantee
        "Your deposits are guaranteed by the FSCS up to £85,000",

        # Past performance with disclaimer
        "Past performance: 10% (2023). Past performance is not a reliable guide.",

        # Non-investment risk mention
        "There is a risk of delays in delivery.",

        # Regulatory guarantee
        "Protected by the Financial Services Compensation Scheme guarantee",

        # Conditional language
        "Potential returns may vary depending on market conditions",
    ]

    for text in false_positive_tests:
        result = gate.check(text, 'financial')
        assert result['status'] != 'FAIL', \
            f"FALSE POSITIVE: {text}"
```

### Measure False Positive Rate

```python
def calculate_precision_recall(gate, test_cases):
    """
    Calculate precision and recall for a gate

    Args:
        test_cases: List of (text, ground_truth) tuples
                   ground_truth: True = should fail, False = should pass
    """
    true_positives = 0
    false_positives = 0
    true_negatives = 0
    false_negatives = 0

    for text, should_fail in test_cases:
        result = gate.check(text, 'document_type')
        did_fail = result['status'] == 'FAIL'

        if should_fail and did_fail:
            true_positives += 1
        elif should_fail and not did_fail:
            false_negatives += 1
        elif not should_fail and did_fail:
            false_positives += 1
        elif not should_fail and not did_fail:
            true_negatives += 1

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return {
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'false_positive_rate': false_positives / (false_positives + true_negatives) if (false_positives + true_negatives) > 0 else 0
    }

# Target metrics for LOKI gates
PRECISION_TARGET = 0.95  # 95% precision (5% false positive rate)
RECALL_TARGET = 0.85     # 85% recall (15% false negative rate)
```

## Pattern Refinement Process

### 1. Initial Pattern

```python
# V1: Too broad
pattern_v1 = r'\bguarantee\b'
# Problem: Matches "guarantee", "guaranteed", "guarantees", "guarantor", etc.
```

### 2. Add Boundaries

```python
# V2: More specific
pattern_v2 = r'\bguarantee[d]?\s+(?:return|profit)\b'
# Improvement: Only matches investment guarantees
# Problem: Still catches "not guaranteed" statements
```

### 3. Add Negative Lookahead

```python
# V3: Exclude disclaimers
pattern_v3 = r'\bguarantee[d]?\s+(?:return|profit)\b(?!.*\bnot\s+guaranteed\b)'
# Improvement: Excludes "not guaranteed" disclaimers
# Problem: Doesn't catch "returns are guaranteed"
```

### 4. Bidirectional Patterns

```python
# V4: Catch both word orders
patterns_v4 = [
    r'\bguarantee[d]?\s+(?:return|profit)\b',
    r'\b(?:return|profit)s?\s+(?:are|is)\s+guaranteed\b',
]
# Improvement: Catches multiple phrasings
```

### 5. Add Context Requirements

```python
# V5: Require investment context
def check_guarantees(text):
    # Only run if investment context present
    if not re.search(r'\b(?:invest|portfolio|fund)\b', text, re.IGNORECASE):
        return {'status': 'N/A'}

    # Check for guarantee claims
    patterns = [
        r'\bguarantee[d]?\s+(?:return|profit)\b',
        r'\b(?:return|profit)s?\s+(?:are|is)\s+guaranteed\b',
    ]

    # Exclude whitelisted terms
    whitelist = r'\b(?:FSCS|deposit\s+protection|government)\b'

    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            context = text[max(0, match.start()-100):match.end()+100]
            if not re.search(whitelist, context, re.IGNORECASE):
                return {'status': 'FAIL'}

    return {'status': 'PASS'}
```

## Optimization Checklist

- [ ] Implement relevance checking for all gates
- [ ] Use negative lookahead for disclaimers
- [ ] Whitelist legitimate regulatory language
- [ ] Require proximity for multi-term patterns
- [ ] Add context requirements
- [ ] Test against adversarial cases
- [ ] Measure precision/recall
- [ ] Target >95% precision, >85% recall
- [ ] Document all whitelisted exceptions
- [ ] Provide clear failure messages

## Monitoring False Positives in Production

```python
# Log potential false positives for review
def check_with_monitoring(gate, text, document_type):
    result = gate.check(text, document_type)

    if result['status'] == 'FAIL':
        # Log for manual review
        log_for_review({
            'gate': gate.name,
            'text_snippet': text[:200],
            'result': result,
            'timestamp': datetime.utcnow()
        })

    return result

# Periodically review logs to identify false positive patterns
# Update gates and whitelist as needed
```

## Resources

- Pattern testing: `tests/unit/test_pattern_accuracy.py`
- Gold standard fixtures: `tests/semantic/gold_fixtures/`
- Metrics tracking: `backend/core/metrics.py`
