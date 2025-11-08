# Compliance Gate Developer

Expert in creating, testing, and maintaining compliance gates for the LOKI document validation system.

## Overview

This skill enables you to design, implement, and optimize compliance gates that validate documents against UK regulatory frameworks including FCA, GDPR, Tax, NDA, and Employment Law.

## Core Responsibilities

### 1. Gate Design
- Create regulatory compliance checks following LOKI gate patterns
- Design regex patterns for detection
- Determine severity levels (critical, high, medium, low)
- Map legal sources to technical requirements

### 2. Implementation Standards
- Follow LOKI gate class structure
- Implement relevance checking
- Provide actionable failure messages
- Include legal source citations

### 3. Testing & Validation
- Write comprehensive test cases
- Create positive and negative test fixtures
- Validate false positive/negative rates
- Performance test regex patterns

## LOKI Gate Architecture

### Standard Gate Structure

```python
import re

class ExampleGate:
    def __init__(self):
        self.name = "gate_name"
        self.severity = "high"  # critical, high, medium, low
        self.legal_source = "Regulation Name (Article/Section)"
        self.relevance_keywords = ['keyword1', 'keyword2']

    def _is_relevant(self, text):
        """Determine if gate applies to this document"""
        t = (text or '').lower()
        return any(keyword in t for keyword in self.relevance_keywords)

    def check(self, text, document_type):
        """
        Validate document against compliance rule

        Returns:
            dict: {
                'status': 'PASS' | 'FAIL' | 'N/A',
                'severity': str,
                'message': str,
                'legal_source': str,
                'suggestion': str (optional)
            }
        """
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable to this document type',
                'legal_source': self.legal_source
            }

        # Validation logic here
        violation_pattern = r"pattern_to_detect"
        matches = re.findall(violation_pattern, text, re.IGNORECASE)

        if matches:
            return {
                'status': 'FAIL',
                'severity': self.severity,
                'message': 'Clear description of violation',
                'legal_source': self.legal_source,
                'suggestion': 'Actionable correction advice'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Compliance requirement met',
            'legal_source': self.legal_source
        }
```

### Real Example from LOKI

```python
# From: backend/modules/hr_scottish/gates/notice.py

import re

class NoticePeriodGate:
    def __init__(self):
        self.name = "notice_period"
        self.severity = "high"
        self.legal_source = "ACAS Code of Practice (Disciplinary and Grievance)"
        self.relevance_keywords = ['disciplinary', 'hearing', 'meeting', 'invite', 'invited']

    def _is_relevant(self, text):
        t = (text or '').lower()
        return 'disciplinary' in t and any(k in t for k in ['hearing', 'meeting', 'invite', 'invited'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a disciplinary notice or warning',
                'legal_source': self.legal_source
            }

        # Look for date/time indicators suggesting notice was provided
        has_date = bool(re.search(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b", text, re.IGNORECASE))
        has_time = bool(re.search(r"\b(?:\d{1,2}:[0-5]\d|\d{1,2}\s?(?:am|pm))\b", text, re.IGNORECASE))

        if has_date or has_time:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Meeting date/time provided',
                'legal_source': self.legal_source
            }

        return {
            'status': 'FAIL',
            'severity': 'high',
            'message': 'No clear meeting date/time provided',
            'legal_source': self.legal_source,
            'suggestion': 'State the date, time and location to provide reasonable notice.'
        }
```

## Key Principles

### 1. Precision Over Recall
- Minimize false positives
- Make detections specific and actionable
- Use context-aware patterns

### 2. Legal Accuracy
- Cite exact regulations (e.g., "GDPR Article 13", "FCA COBS 4.2.1")
- Include section numbers and regulation names
- Reference official guidance documents

### 3. Actionable Feedback
- Provide clear failure messages
- Include specific correction suggestions
- Explain why the violation matters

### 4. Performance
- Test regex efficiency
- Avoid catastrophic backtracking
- Use compiled patterns for repeated checks

## Severity Classification

| Severity | Use Case | Example |
|----------|----------|---------|
| **critical** | Legal requirement, financial penalty risk | VAT invoice missing required fields |
| **high** | Regulatory violation, tribunal risk | Disciplinary notice missing appeal rights |
| **medium** | Best practice, potential dispute | Vague allegations in HR documents |
| **low** | Style/clarity improvement | Inconsistent terminology |

## Module Integration

### Register Gates in Module

```python
# backend/modules/module_name/__init__.py

from .gates.gate1 import Gate1
from .gates.gate2 import Gate2

def register_gates():
    return {
        'gate1': Gate1(),
        'gate2': Gate2(),
    }

MODULE_INFO = {
    'id': 'module_name',
    'name': 'Module Display Name',
    'description': 'Module description',
    'version': '1.0.0',
    'gates': register_gates()
}
```

### Gate Registry Integration

```python
from backend.core.gate_registry import gate_registry

# Register gate with version control
gate_registry.register_gate(
    module_id='fca_uk',
    gate_id='fair_clear_not_misleading',
    gate_obj=FairClearNotMisleadingGate(),
    version='1.0.0'
)
```

## Common Patterns

### Financial Promotions (FCA)

```python
# Detect guaranteed return claims
guarantee_pattern = r'\b(?:guarantee[d]?|certain|assured|promised?)\s+(?:return|profit|gain|income)\b'

# Detect missing risk warnings
risk_required_context = r'\b(?:invest|return|profit|performance)\b'
risk_warning_present = r'\b(?:risk|may (?:fall|lose)|not guaranteed|past performance)\b'
```

### Data Protection (GDPR)

```python
# Detect vague purposes
vague_purposes = r'\b(?:various|legitimate|necessary|business|operational)\s+purpose[s]?\b'

# Detect missing lawful basis
lawful_basis_terms = r'\b(?:consent|contract|legal obligation|vital interest|public task|legitimate interest)\b'
```

### Tax Compliance (HMRC)

```python
# VAT number validation
vat_pattern = r'\bGB\d{9}(?:\d{3})?\b'

# VAT rate validation
valid_vat_rates = ['0%', '5%', '20%']
invalid_rate_pattern = r'\b(?:VAT|tax).*?(\d+(?:\.\d+)?%)'
```

## Testing Strategy

### Unit Tests

```python
def test_gate_pass_scenario():
    gate = MyGate()
    text = "Compliant document text"
    result = gate.check(text, 'document_type')
    assert result['status'] == 'PASS'

def test_gate_fail_scenario():
    gate = MyGate()
    text = "Non-compliant document text"
    result = gate.check(text, 'document_type')
    assert result['status'] == 'FAIL'
    assert 'suggestion' in result

def test_gate_not_applicable():
    gate = MyGate()
    text = "Unrelated document"
    result = gate.check(text, 'other_type')
    assert result['status'] == 'N/A'
```

### Integration Tests

```python
from backend.server import validate_document

def test_module_integration():
    results = validate_document(
        text="Test document",
        document_type="financial",
        modules=['fca_uk']
    )
    assert 'fca_uk' in results['validation']['modules']
    assert 'gates' in results['validation']['modules']['fca_uk']
```

## Best Practices

1. **Always provide legal sources** - Every gate must cite specific regulations
2. **Make patterns specific** - Avoid overly broad regex that triggers false positives
3. **Test edge cases** - Check boundary conditions, empty strings, special characters
4. **Document patterns** - Comment complex regex with explanation
5. **Version gates** - Use gate registry for deprecation and version control
6. **Measure performance** - Profile regex patterns on large documents
7. **Provide examples** - Include sample compliant and non-compliant text

## Resources

- See `gate-design-patterns.md` for regex pattern library
- See `testing-framework.md` for comprehensive testing guide
- See `regulatory-research.md` for researching regulations
- See `accuracy-optimization.md` for reducing false positives

## File Locations

- Gate implementations: `backend/modules/{module_name}/gates/`
- Gate tests: `backend/tests/semantic/`
- Gate registry: `backend/core/gate_registry.py`
- Module definitions: `backend/modules/{module_name}/__init__.py`
