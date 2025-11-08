# Document Correction Expert

Specialist in auto-correction strategies and deterministic synthesis for LOKI compliance documents.

## Overview

The Document Correction Expert skill enables implementation of automated compliance corrections using deterministic, reproducible strategies.

## Correction Philosophy

**LOKI Correction Principles:**
1. **Deterministic** - Same input always produces same output
2. **Traceable** - Every correction has a reason and source
3. **Reversible** - Original text preserved, changes tracked
4. **Minimal** - Only fix compliance violations, preserve intent
5. **Lawful** - Corrections based on legal requirements

## Correction Strategies

### Strategy Priority System

```python
CORRECTION_STRATEGIES = {
    20: 'suggestion',        # Advice only, no changes
    30: 'regex',             # Pattern-based replacement
    40: 'template',          # Insert required clauses
    60: 'structural',        # Reorganize document sections
}
```

### Strategy 1: Suggestion (Priority 20)

**Use when:** Correction requires human judgment

```python
{
    'strategy': 'suggestion',
    'priority': 20,
    'pattern': None,  # No automatic fix
    'reason': 'Allegations are too vague - provide specific dates and incidents',
    'suggestion': 'Replace "recent behaviour" with "On 15 March 2024, you..."',
    'legal_source': 'ACAS Code Para 10',
}
```

**Example:**
- Violation: "Your recent behaviour has been unacceptable"
- Suggestion: "State specific incidents with dates per ACAS Code Para 10"
- No automatic correction (requires employer knowledge)

### Strategy 2: Regex Replacement (Priority 30)

**Use when:** Simple pattern-based fix available

```python
{
    'strategy': 'regex',
    'priority': 30,
    'pattern': r'\bguaranteed?\s+(\d+%)\s+returns?\b',
    'replacement': r'potential returns of up to \1 (not guaranteed, capital at risk)',
    'reason': 'Remove guaranteed returns claim (FCA COBS 4.2.1R)',
    'legal_source': 'FCA COBS 4.2.1R',
}
```

**Example:**
- Original: "Guaranteed 10% returns annually"
- Corrected: "Potential returns of up to 10% (not guaranteed, capital at risk)"

### Strategy 3: Template Insertion (Priority 40)

**Use when:** Required clause is missing

```python
{
    'strategy': 'template',
    'priority': 40,
    'insertion_point': 'end_of_document',  # or 'after_pattern', 'before_pattern'
    'template': '''
**Right to Appeal**

You have the right to appeal this decision. Appeals must be submitted in writing
within 5 working days to [Manager Name], [Title].
    ''',
    'reason': 'Appeal rights missing (ACAS Code Para 24)',
    'legal_source': 'ACAS Code Para 24',
}
```

**Example:**
- Missing: Appeal rights clause
- Inserted: Standard appeal rights template at end of letter

### Strategy 4: Structural Reform (Priority 60)

**Use when:** Document needs reorganization

```python
{
    'strategy': 'structural',
    'priority': 60,
    'sections_to_add': ['Investigation', 'Meeting Details', 'Evidence', 'Appeal Rights'],
    'template': 'disciplinary_letter_template.md',
    'reason': 'Document lacks required structure (ACAS Code)',
    'legal_source': 'ACAS Code Para 9-24',
}
```

## Real LOKI Correction Examples

### Example 1: FCA Risk Warning

```python
from backend.core.correction_patterns import CorrectionPatternRegistry

registry = CorrectionPatternRegistry()

# Pattern detected by FCA gate
pattern = {
    'module': 'fca_uk',
    'category': 'guaranteed_returns',
    'strategy': 'regex',
    'priority': 30,
    'pattern': r'\b(guaranteed?|certain|assured)\s+(returns?|profits?)\b',
    'replacement': r'potential \2 (not guaranteed, value may fall)',
    'reason': 'Removed guarantee claim per FCA COBS 4.2.1R',
    'legal_source': 'FCA COBS 4.2.1R',
    'severity': 'critical',
}

# Application
original = "Invest now for guaranteed returns of 15% annually!"
corrected = apply_correction(original, pattern)
# Result: "Invest now for potential returns of 15% annually (not guaranteed, value may fall)!"
```

### Example 2: GDPR Lawful Basis

```python
pattern = {
    'module': 'gdpr_uk',
    'category': 'vague_purpose',
    'strategy': 'template',
    'priority': 40,
    'insertion_point': 'after_pattern',
    'anchor_pattern': r'\bWe\s+collect\s+your\s+data\b',
    'template': '''
**Why We Collect Your Data**

We collect and process your personal data for the following specific purposes:
- To process your order and deliver products/services
- To comply with our legal obligations (e.g., tax, accounting)
- To respond to your queries and provide customer support

Our lawful basis: Contract (Article 6(1)(b) GDPR) and Legal Obligation (Article 6(1)(c) GDPR).
    ''',
    'reason': 'Vague purpose replaced with specific purposes and lawful basis',
    'legal_source': 'GDPR Article 13(1)(c)',
    'severity': 'critical',
}
```

### Example 3: ACAS Accompaniment Rights

```python
pattern = {
    'module': 'hr_scottish',
    'category': 'accompaniment',
    'strategy': 'template',
    'priority': 40,
    'insertion_point': 'before_pattern',
    'anchor_pattern': r'\b(?:Date|Meeting)\s*:',
    'template': '''
**Right to be Accompanied**

You have the statutory right to be accompanied at this meeting by:
- A trade union representative, OR
- A work colleague

Please inform [Contact Name] if you wish to be accompanied and who will accompany you.

    ''',
    'reason': 'Added accompaniment rights per ERA 1999 s10',
    'legal_source': 'ERA 1999 s10 + ACAS Code Para 15',
    'severity': 'high',
}
```

## Deterministic Synthesis

### SHA256 Hashing

```python
import hashlib
import json

def generate_deterministic_hash(correction_data):
    """
    Generate SHA256 hash for correction reproducibility

    Args:
        correction_data: Dict containing original, corrected, patterns applied

    Returns:
        str: SHA256 hash
    """
    # Normalize data
    normalized = {
        'original': correction_data['original'],
        'patterns': sorted(correction_data['patterns'], key=lambda x: x['priority']),
        'timestamp': None,  # Exclude timestamp for determinism
    }

    # Create canonical JSON
    canonical_json = json.dumps(normalized, sort_keys=True, separators=(',', ':'))

    # Generate hash
    return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()

# Verify reproducibility
hash1 = generate_deterministic_hash(correction_data)
hash2 = generate_deterministic_hash(correction_data)
assert hash1 == hash2  # Always identical for same input
```

### Correction Lineage

```python
correction_result = {
    'original': original_text,
    'corrected': corrected_text,
    'deterministic_hash': 'a3f5b2...',
    'corrections': [
        {
            'pattern': 'guaranteed_returns',
            'before': 'guaranteed returns',
            'after': 'potential returns (not guaranteed)',
            'reason': 'FCA COBS 4.2.1R violation',
            'legal_source': 'FCA COBS 4.2.1R',
            'strategy': 'regex',
            'priority': 30,
        },
        # ... more corrections
    ],
    'correction_count': 3,
    'modules_applied': ['fca_uk', 'gdpr_uk'],
}
```

## Template Design

### Template Categories

```python
TEMPLATE_CATEGORIES = {
    'risk_warnings': [
        'investment_risk',
        'past_performance',
        'capital_at_risk',
    ],
    'gdpr_clauses': [
        'lawful_basis',
        'data_subject_rights',
        'retention_periods',
        'dpo_contact',
    ],
    'hr_procedures': [
        'accompaniment_rights',
        'appeal_rights',
        'investigation_notice',
    ],
}
```

### Template Structure

```markdown
## Template: Investment Risk Warning

**Category:** FCA / Risk Warnings
**Legal Source:** FCA COBS 4.2.1R
**Use When:** Investment product mentioned without risk disclosure

**Template:**
```
**Investment Risk Warning**

- The value of investments can go down as well as up
- You may get back less than you invested
- Past performance is not a reliable guide to future results
- Capital is at risk
```

**Insertion Point:** Before call-to-action or at document end

**Variables:**
- None (standardized text)

**Variations:**
- High-risk products: Add "This is a high-risk investment" at top
- Derivatives: Add specific derivative risk warnings
```

## Quality Assurance

### Correction Validation

```python
def validate_correction(original, corrected, patterns_applied):
    """
    QA checks for corrections

    Returns:
        dict: Validation results
    """
    issues = []

    # 1. Check no essential content lost
    important_terms = extract_key_terms(original)
    for term in important_terms:
        if term not in corrected:
            issues.append(f"Lost important term: {term}")

    # 2. Check corrections are minimal
    diff_ratio = compute_diff_ratio(original, corrected)
    if diff_ratio > 0.5:  # More than 50% changed
        issues.append(f"Excessive changes: {diff_ratio*100:.0f}%")

    # 3. Check legal sources cited
    for pattern in patterns_applied:
        if not pattern.get('legal_source'):
            issues.append(f"Missing legal source for: {pattern['pattern']}")

    # 4. Check determinism
    hash1 = generate_hash(corrected, patterns_applied)
    hash2 = generate_hash(corrected, patterns_applied)
    if hash1 != hash2:
        issues.append("Non-deterministic correction detected")

    return {
        'valid': len(issues) == 0,
        'issues': issues,
    }
```

## Best Practices

1. **Preserve Intent** - Don't change meaning, only fix compliance
2. **Cite Sources** - Every correction must reference legal basis
3. **Test Determinism** - Same input must always produce same output
4. **Minimal Changes** - Only fix violations, leave rest untouched
5. **Track Lineage** - Record all corrections applied
6. **Provide Fallbacks** - If auto-correction fails, provide suggestion
7. **Version Templates** - Keep templates up-to-date with regulation changes

## File Locations

- Correction patterns: `backend/core/correction_patterns.py`
- Templates: `backend/templates/`
- Corrector: `backend/core/corrector.py`
- Tests: `backend/tests/unit/test_corrections.py`

## See Also

- `template-design.md` - Building compliance templates
- `context-analysis.md` - Document type detection
- `quality-assurance.md` - QA processes
- `deterministic-synthesis.md` - Reproducible corrections
