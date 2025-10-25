---
name: loki-document-corrector
description: Expert in LOKI's advanced document correction system, including correction strategies, patterns, synthesizer, multi-level corrections, and context-aware logic
---

# LOKI Document Corrector Skill

You are an expert in LOKI's enterprise-grade document correction system. This skill provides comprehensive knowledge of correction workflows, patterns, strategies, and the deterministic synthesis engine.

## System Overview

The LOKI Document Corrector is a **NO-AI** rule-based correction system that automatically fixes compliance issues in documents based on validation results. It uses:

- **Gate-specific patterns** for 5 regulatory modules
- **Multi-level correction strategies** (regex, template, structural, suggestion)
- **Deterministic synthesis** for repeatable corrections
- **Context-aware logic** for intelligent correction filtering
- **Validation layer** for correction integrity

## Architecture

```
DocumentCorrector
├── Pattern Registry (46 patterns)
│   ├── FCA UK patterns (11)
│   ├── GDPR UK patterns (17)
│   ├── Tax UK patterns (6)
│   ├── NDA UK patterns (8)
│   └── HR Scottish patterns (4)
├── Correction Strategies (4)
│   ├── SuggestionExtractionStrategy (priority 20)
│   ├── RegexReplacementStrategy (priority 30)
│   ├── TemplateInsertionStrategy (priority 40)
│   └── StructuralReorganizationStrategy (priority 60)
├── Synthesis Engine
│   ├── Standard synthesis
│   ├── Multi-level synthesis
│   └── Context-aware synthesis
└── Validation Layer
    ├── Integrity checks
    ├── Structure validation
    └── Safety verification
```

## Core Files

### Primary Files

1. **corrector.py** (`backend/core/corrector.py`)
   - Main interface for document correction
   - Supports advanced and legacy modes
   - Entry point for all corrections

2. **correction_strategies.py** (`backend/core/correction_strategies.py`)
   - 4 correction strategy implementations
   - Strategy base class
   - Priority-based execution

3. **correction_patterns.py** (`backend/core/correction_patterns.py`)
   - Gate-specific correction patterns
   - Organized by regulatory module
   - 46 total patterns (19 regex, 26 templates, 1 structural)

4. **correction_synthesizer.py** (`backend/core/correction_synthesizer.py`)
   - Deterministic synthesis engine
   - Multi-level correction orchestration
   - Context-aware filtering
   - Validation logic

5. **test_advanced_corrector.py** (`backend/core/test_advanced_corrector.py`)
   - Comprehensive test suite
   - 8 tests covering all features
   - Determinism verification

6. **CORRECTOR_README.md** (`backend/core/CORRECTOR_README.md`)
   - Complete documentation
   - Usage examples
   - Extension guide

## Correction Strategies

### 1. SuggestionExtractionStrategy (Priority: 20)

**Purpose:** Extract and apply suggestions from gate validation results

**When Applied:** When gate provides actionable suggestion text

**Pattern Matching:**
```python
# Extracts from suggestions like:
"Add: 'You have the right to be accompanied...'"
"Include: 'RISK WARNING: ...'"
```

**Location:** `backend/core/correction_strategies.py:286-325`

**Example:**
```python
# Gate suggestion:
"Add: 'Nothing in this Agreement prevents whistleblowing.'"

# Result:
# Appends suggestion text to end of document
```

### 2. RegexReplacementStrategy (Priority: 30)

**Purpose:** Pattern-based find and replace operations

**When Applied:** When regex patterns match problematic text

**Registration:**
```python
strategy.register_pattern(
    gate_pattern='vat_threshold',
    regex_pattern=r'£85,000',
    replacement='£90,000',
    reason='Updated VAT threshold (April 2024)',
    flags=0
)
```

**Location:** `backend/core/correction_strategies.py:31-117`

**Common Patterns:**
- VAT threshold updates: `£85,000` → `£90,000`
- Risk warnings: `investments can go down as well as up` → FCA-compliant text
- Forced consent: `by using this website, you automatically agree` → `We request your explicit consent`

### 3. TemplateInsertionStrategy (Priority: 40)

**Purpose:** Insert pre-formatted compliance text at strategic positions

**When Applied:** When compliance text is missing

**Insertion Positions:**
- `start` - Beginning of document
- `end` - End of document
- `after_header` - After document header/title
- `before_signature` - Before signature block

**Registration:**
```python
strategy.register_template(
    gate_pattern='whistleblowing',
    template='PROTECTED DISCLOSURES: Nothing in this Agreement...',
    position='end',
    condition=r'(?:nda|confidential)'  # Optional regex condition
)
```

**Location:** `backend/core/correction_strategies.py:120-196`

**Example Templates:**

1. **FCA Risk Warning:**
```
⚠️ RISK WARNING: The value of investments can fall as well as rise
and you may get back less than you invest. Past performance is not
a reliable indicator of future results.
```

2. **GDPR Withdrawal Rights:**
```
WITHDRAWAL OF CONSENT: You may withdraw your consent at any time
by contacting us at [contact details]. Withdrawal will not affect
the lawfulness of processing based on consent before withdrawal.
```

3. **NDA Whistleblowing Protection:**
```
PROTECTED DISCLOSURES: Nothing in this Agreement prevents the
disclosure of information protected under the Public Interest
Disclosure Act 1998 (whistleblowing) or required by law.
```

### 4. StructuralReorganizationStrategy (Priority: 60)

**Purpose:** Reorganize document structure for compliance

**When Applied:** When structure needs reorganization (e.g., risk warnings after benefits)

**Operations:**
- **move_section** - Move sections to different positions
- **add_section_header** - Add section headers
- **reorder_risk_warnings** - Move risk warnings before benefit statements

**Location:** `backend/core/correction_strategies.py:199-283`

**Example:**
```python
# Before:
"High returns and profit potential! [benefits]
Risk: investments may fall [warnings]"

# After:
"Risk: investments may fall [warnings]
High returns and profit potential! [benefits]"
```

## Correction Patterns Registry

### Pattern Structure

**Location:** `backend/core/correction_patterns.py`

**Types:**
1. **regex_patterns** - Pattern-based replacements
2. **templates** - Compliance text to insert
3. **structural_rules** - Document reorganization rules

### FCA UK Patterns

**Regex Patterns:**
```python
# Risk/benefit balance
'risk_benefit': [
    {
        'pattern': r'(?:high|significant|attractive)\s+(?:return|yield)',
        'replacement': r'potential returns (capital at risk)',
        'reason': 'FCA COBS 4.2.3 - Balance benefits with risk warnings'
    }
]

# Fair, clear, not misleading
'fair_clear': [
    {
        'pattern': r'guaranteed\s+(?:returns|profit)',
        'replacement': 'potential returns (not guaranteed)',
        'reason': 'FCA COBS 4.2.1 - Remove misleading guarantees'
    }
]

# Generic risk warnings
'risk_warning': [
    {
        'pattern': r'investments can go down as well as up',
        'replacement': 'The value of investments can fall as well as rise and you may get back less than you invest',
        'reason': 'FCA-compliant risk warning language'
    }
]
```

**Templates:**
```python
'risk_benefit': [
    {
        'template': '⚠️ RISK WARNING: The value of investments...',
        'position': 'after_header',
        'condition': r'(?:investment|return|profit|yield)'
    }
]

'target_market': [
    {
        'template': 'TARGET MARKET: This product is designed for...',
        'position': 'after_header',
        'condition': r'(?:product|service|investment)'
    }
]

'fos_signposting': [
    {
        'template': 'COMPLAINTS: If you have a complaint, please contact us. If we cannot resolve your complaint, you may refer it to the Financial Ombudsman Service...',
        'position': 'before_signature'
    }
]
```

**Location:** `backend/core/correction_patterns.py:35-125`

### GDPR UK Patterns

**Regex Patterns:**
```python
'consent': [
    {
        'pattern': r'by\s+using\s+(?:this|our)\s+(?:website|service|app),?\s+you\s+(?:automatically\s+)?(?:agree|consent)\s+to',
        'replacement': 'We request your explicit consent to',
        'reason': 'GDPR Article 7 - Remove forced consent'
    },
    {
        'pattern': r'continued\s+use.*constitutes.*(?:agreement|consent)',
        'replacement': 'You may provide your explicit consent by clicking "I agree"',
        'reason': 'GDPR Article 4(11) - Consent must be unambiguous affirmative action'
    }
]

'cookies': [
    {
        'pattern': r'this\s+(?:site|website)\s+uses\s+cookies',
        'replacement': 'This website uses cookies. We require your consent for non-essential cookies',
        'reason': 'PECR - Explicit consent required for non-essential cookies'
    }
]
```

**Templates:**
```python
'withdrawal_consent': [
    {
        'template': 'WITHDRAWAL OF CONSENT: You may withdraw your consent at any time...',
        'position': 'end',
        'condition': r'(?:consent|agree to)'
    }
]

'rights': [
    {
        'template': '''YOUR RIGHTS: Under GDPR, you have the right to:
• Access your personal data
• Rectify inaccurate data
• Erase your data ("right to be forgotten")
• Restrict processing
• Data portability
• Object to processing
• Not be subject to automated decision-making

To exercise these rights, contact us at [contact details].''',
        'position': 'before_signature',
        'condition': r'(?:personal data|privacy|data protection)'
    }
]

'lawful_basis': [
    {
        'template': 'LAWFUL BASIS: We process your personal data based on [specify: consent / contract / legal obligation / vital interests / public task / legitimate interests].',
        'position': 'after_header'
    }
]
```

**Location:** `backend/core/correction_patterns.py:131-239`

### Tax UK Patterns

**Regex Patterns:**
```python
'vat_threshold': [
    {
        'pattern': r'£85,?000',
        'replacement': '£90,000',
        'reason': 'Updated VAT threshold (April 2024)'
    },
    {
        'pattern': r'£83,?000',
        'replacement': '£90,000',
        'reason': 'Updated VAT threshold (April 2024)'
    }
]

'hmrc_scam': [
    {
        'pattern': r'(?:pay|payment).*(?:via|using).*(?:gift\s+card|itunes)',
        'replacement': '[REMOVED - SCAM INDICATOR: HMRC never requests payment via gift cards]',
        'reason': 'HMRC scam prevention'
    }
]
```

**Templates:**
```python
'mtd': [
    {
        'template': 'MAKING TAX DIGITAL: VAT-registered businesses must use MTD-compatible software...',
        'position': 'end',
        'condition': r'(?:VAT|value added tax)'
    }
]

'hmrc_scam_notice': [
    {
        'template': '⚠️ HMRC WARNING: HMRC will never request payment via gift cards, Bitcoin, or threaten immediate arrest...',
        'position': 'start',
        'condition': r'(?:hmrc|tax|payment|refund)'
    }
]
```

**Location:** `backend/core/correction_patterns.py:245-296`

### NDA UK Patterns

**Templates:**
```python
'whistleblowing': [
    {
        'template': 'PROTECTED DISCLOSURES: Nothing in this Agreement prevents the disclosure of information protected under the Public Interest Disclosure Act 1998 (whistleblowing) or required by law.',
        'position': 'end',
        'condition': r'(?:disclose|confidential|nda)'
    }
]

'crime_reporting': [
    {
        'template': 'RIGHT TO REPORT CRIME: Nothing in this Agreement prevents you from reporting suspected criminal activity to law enforcement or regulatory authorities.',
        'position': 'end'
    }
]

'harassment': [
    {
        'template': 'HARASSMENT AND DISCRIMINATION: Nothing in this Agreement prevents you from making a complaint of harassment, discrimination, or victimisation under the Equality Act 2010.',
        'position': 'end'
    }
]

'public_domain': [
    {
        'template': 'EXCLUSIONS: Confidential Information does not include information that: (a) is or becomes publicly available through no breach of this Agreement; (b) was lawfully known prior to disclosure...',
        'position': 'after_header'
    }
]
```

**Regex Patterns:**
```python
'duration': [
    {
        'pattern': r'(?:in\s+)?perpetuity',
        'replacement': 'for a period of [specify reasonable duration, typically 2-5 years]',
        'reason': 'Unreasonable duration - must be proportionate'
    }
]
```

**Location:** `backend/core/correction_patterns.py:302-374`

### HR Scottish Patterns

**Templates:**
```python
'accompaniment': [
    {
        'template': 'RIGHT TO BE ACCOMPANIED: You have the statutory right to be accompanied at this meeting by a work colleague or trade union representative. Please inform us in advance if you wish to be accompanied and provide the name of your companion.',
        'position': 'after_header',
        'condition': r'(?:disciplinary|grievance|hearing|meeting)'
    }
]

'appeal': [
    {
        'template': 'APPEAL RIGHTS: If you are dissatisfied with the outcome, you have the right to appeal. You must submit your appeal in writing within [5-10] working days to [name/position].',
        'position': 'before_signature'
    }
]

'right_to_be_heard': [
    {
        'template': 'RIGHT TO RESPOND: You will have the opportunity to state your case, present evidence, and call witnesses before any decision is made.',
        'position': 'after_header'
    }
]
```

**Regex Patterns:**
```python
'accompaniment_restrictions': [
    {
        'pattern': r'(?:may\s+not|cannot).*(?:bring|accompanied\s+by).*(?:solicitor|lawyer)',
        'replacement': 'You have the right to be accompanied by a work colleague or trade union representative',
        'reason': 'ERA 1999 s10 - Statutory right to accompaniment'
    }
]

'suspension': [
    {
        'pattern': r'suspended.*(?:pending|during).*investigation',
        'replacement': 'suspended on full pay (not a disciplinary sanction) pending investigation',
        'reason': 'Clarify suspension is neutral act, not punishment'
    }
]
```

**Location:** `backend/core/correction_patterns.py:380-483`

## Synthesis Engine

### Standard Synthesis

**Method:** `synthesizer.synthesize_corrections(text, gate_results, context)`

**Process:**
1. Sort gates alphabetically (determinism)
2. Filter to FAIL/WARNING status
3. Apply strategies in priority order (60→40→30→20)
4. Stop after first successful strategy per gate
5. Calculate determinism hashes

**Location:** `backend/core/correction_synthesizer.py:38-102`

**Usage:**
```python
from backend.core.correction_synthesizer import CorrectionSynthesizer
from backend.core.correction_strategies import *

strategies = [
    SuggestionExtractionStrategy(),
    RegexReplacementStrategy(),
    TemplateInsertionStrategy(),
    StructuralReorganizationStrategy()
]

synthesizer = CorrectionSynthesizer(strategies, document_type='financial')
result = synthesizer.synthesize_corrections(text, gate_results)

print(result['correction_count'])
print(result['determinism']['output_hash'])
```

### Multi-Level Synthesis

**Method:** `synthesizer.synthesize_multi_level(text, gate_results, levels)`

**Process:**
1. Apply corrections in multiple passes
2. Each level uses specific strategy types
3. Default order: suggestion → regex → template → structural

**Location:** `backend/core/correction_synthesizer.py:139-192`

**Usage:**
```python
result = synthesizer.synthesize_multi_level(
    text,
    gate_results,
    levels=['suggestion_extraction', 'regex_replacement',
            'template_insertion', 'structural_reorganization']
)

print(result['multi_level'])  # True
print(result['levels'])  # Level-by-level results
```

### Context-Aware Synthesis

**Method:** `synthesizer.synthesize_with_context_awareness(text, gate_results, document_metadata)`

**Process:**
1. Filter gates by document context
2. Prioritize module-specific gates
3. Filter warnings by relevance

**Location:** `backend/core/correction_synthesizer.py:104-137`

**Filtering Rules:**
- Critical failures always included
- High severity failures always included
- Warnings filtered by document type relevance
- Module-specific gates prioritized

**Relevance Mapping:**
```python
relevance_map = {
    'financial': ['fca', 'risk', 'investment', 'promotion'],
    'privacy': ['gdpr', 'consent', 'data', 'retention', 'rights'],
    'tax': ['vat', 'hmrc', 'tax', 'mtd'],
    'nda': ['whistleblowing', 'crime', 'harassment', 'duration'],
    'employment': ['accompaniment', 'appeal', 'notice', 'suspension']
}
```

**Usage:**
```python
result = synthesizer.synthesize_with_context_awareness(
    text,
    gate_results,
    document_metadata={
        'document_type': 'privacy',
        'module_id': 'gdpr_uk',
        'confidence': 0.95,
        'industry': 'fintech',
        'jurisdiction': 'UK'
    }
)

print(result['context_aware'])  # True
print(result['context'])
```

## DocumentCorrector Interface

### Initialization

```python
from backend.core.corrector import DocumentCorrector

# Advanced mode (default)
corrector = DocumentCorrector(advanced_mode=True)

# Legacy mode
corrector = DocumentCorrector(advanced_mode=False)
```

**Location:** `backend/core/corrector.py`

### Basic Correction

```python
result = corrector.correct_document(
    text=document_text,
    validation_results=validation_response
)
```

**Response:**
```python
{
    'original': str,
    'corrected': str,
    'corrections_applied': [
        {
            'gate_id': 'consent',
            'gate_severity': 'critical',
            'strategy': 'regex_replacement',
            'metadata': {
                'strategy': 'regex_replacement',
                'changes': 2,
                'locations': [45, 123],
                'reason': 'GDPR Article 7 - Remove forced consent',
                'examples': ['by using this website...']
            },
            'text_length_delta': 15
        }
    ],
    'unchanged': False,
    'correction_count': 3,
    'strategies_applied': ['regex_replacement', 'template_insertion'],
    'determinism': {
        'input_hash': 'a1b2c3d4...',
        'output_hash': 'e5f6g7h8...',
        'repeatable': True
    },
    'validation': {
        'valid': True,
        'warnings': [],
        'errors': []
    },
    'mode': 'advanced'
}
```

### Multi-Level Correction

```python
result = corrector.correct_document(
    text=document_text,
    validation_results=validation_response,
    advanced_options={'multi_level': True}
)

print(result['multi_level'])  # True
print(result['levels'])  # Level breakdown
```

### Context-Aware Correction

```python
result = corrector.correct_document(
    text=document_text,
    validation_results=validation_response,
    document_type='privacy',
    advanced_options={
        'context_aware': True,
        'document_metadata': {
            'document_type': 'privacy',
            'module_id': 'gdpr_uk',
            'confidence': 0.95
        }
    }
)

print(result['context_aware'])  # True
```

## Utility Methods

### Get Available Corrections

Preview corrections without applying:

```python
preview = corrector.get_available_corrections(text, validation_results)

print(f"Failing gates: {preview['failing_gates']}")
print(f"Available corrections: {preview['available_corrections']}")
print(f"Estimated changes: {preview['estimated_changes']}")
```

**Location:** `backend/core/corrector.py:372-410`

### Get Correction Statistics

View system capabilities:

```python
stats = corrector.get_correction_statistics()

# Output:
{
    'regex_patterns': 19,
    'templates': 26,
    'structural_rules': 1,
    'total_patterns': 46,
    'modules': ['FCA UK', 'GDPR UK', 'HR Scottish', 'NDA UK', 'Tax UK'],
    'strategies': ['suggestion_extraction', 'regex_replacement',
                   'template_insertion', 'structural_reorganization']
}
```

**Location:** `backend/core/corrector.py:412-456`

### Test Pattern Match

Test if patterns match specific text:

```python
result = corrector.test_pattern_match(
    text="VAT threshold is £85,000",
    gate_pattern="vat_threshold"
)

print(f"Would correct: {result['would_correct']}")  # True
print(f"Matches: {result['matches']}")
# [{'type': 'regex', 'pattern_key': 'vat_threshold',
#   'matches': ['£85,000'], 'count': 1}]
```

**Location:** `backend/core/corrector.py:458-516`

## Validation Layer

### CorrectionValidator

Validates corrections maintain document integrity.

**Location:** `backend/core/correction_synthesizer.py:290-337`

**Checks:**
1. Document not empty (>10 chars)
2. No excessive deletions (>50% removal)
3. No excessive additions (>200% growth)
4. All corrections have metadata
5. No infinite loops (same correction repeated)

**Usage:**
```python
from backend.core.correction_synthesizer import CorrectionValidator

validator = CorrectionValidator()
validation = validator.validate_correction(original, corrected, corrections)

print(validation['valid'])  # True/False
print(validation['warnings'])  # List of warnings
print(validation['errors'])  # List of errors
```

## Determinism Guarantees

### Hash Calculation

**Input Hash:**
```python
input_hash = hashlib.sha256(json.dumps({
    'text_hash': hashlib.sha256(text.encode()).hexdigest(),
    'gates': sorted([(gate_id, status, severity) for gate_id, result in gate_results])
}, sort_keys=True).encode()).hexdigest()[:16]
```

**Output Hash:**
```python
output_hash = hashlib.sha256(json.dumps({
    'text_hash': hashlib.sha256(corrected_text.encode()).hexdigest(),
    'correction_count': len(corrections),
    'strategies': sorted(list(set(c['strategy'] for c in corrections)))
}, sort_keys=True).encode()).hexdigest()[:16]
```

### Determinism Features

1. **Consistent Ordering** - Gates sorted alphabetically
2. **Priority-Based** - Strategies execute in fixed priority order
3. **No Random Elements** - No `random`, no timing dependencies
4. **Idempotent** - Same input always produces same output
5. **Hash Verification** - Input/output hashes prove repeatability

## Testing

### Test Suite

**Location:** `backend/core/test_advanced_corrector.py`

**Tests:**
1. Basic correction (FCA risk warning)
2. GDPR consent corrections
3. VAT threshold updates
4. Multi-level correction
5. Context-aware correction
6. Correction statistics
7. Pattern matching
8. Determinism verification (3 runs)

**Run Tests:**
```bash
cd backend/core
python3 test_advanced_corrector.py
```

**Expected Output:**
```
✓ All tests passed
✓ Advanced correction system is operational
✓ Determinism verified
✓ Multiple correction strategies working
✓ Context-aware filtering operational
```

## Common Workflows

### Workflow 1: Simple Correction

```python
# 1. Validate document
validation_results = validate_document(text)

# 2. Apply corrections
corrector = DocumentCorrector()
result = corrector.correct_document(text, validation_results)

# 3. Return corrected document
return result['corrected']
```

### Workflow 2: Preview Before Correction

```python
# 1. Preview available corrections
corrector = DocumentCorrector()
preview = corrector.get_available_corrections(text, validation_results)

# 2. Show user what will be corrected
print(f"{preview['estimated_changes']} corrections available")

# 3. Apply if user confirms
if user_confirms:
    result = corrector.correct_document(text, validation_results)
```

### Workflow 3: Context-Aware Correction

```python
# 1. Detect document type
document_type = detect_document_type(text)

# 2. Apply context-aware correction
result = corrector.correct_document(
    text,
    validation_results,
    document_type=document_type,
    advanced_options={
        'context_aware': True,
        'document_metadata': {
            'document_type': document_type,
            'confidence': 0.95
        }
    }
)

# 3. Only relevant corrections applied
```

### Workflow 4: Multi-Level Correction

```python
# 1. Apply corrections in stages
result = corrector.correct_document(
    text,
    validation_results,
    advanced_options={'multi_level': True}
)

# 2. Review level-by-level
for level, info in result['levels'].items():
    print(f"{level}: {info['corrections']} corrections")

# 3. Return final result
return result['corrected']
```

## Extension Guide

### Adding New Patterns

**Step 1:** Edit `backend/core/correction_patterns.py`

```python
def _init_fca_uk_patterns(self):
    # Add regex pattern
    self.regex_patterns['new_pattern_id'] = [{
        'pattern': r'your_regex_here',
        'replacement': 'replacement_text',
        'reason': 'Legal reference and explanation',
        'flags': re.IGNORECASE
    }]

    # Add template
    self.templates['new_template_id'] = [{
        'template': 'Your compliance text here',
        'position': 'end',
        'condition': r'optional_condition'
    }]
```

**Step 2:** Patterns are auto-registered on initialization

**Step 3:** Test with `test_pattern_match()`

### Adding New Strategies

**Step 1:** Create strategy class in `backend/core/correction_strategies.py`

```python
class CustomStrategy(CorrectionStrategy):
    def __init__(self):
        super().__init__("custom_strategy", priority=45)

    def can_apply(self, text: str, gate_id: str, gate_result: Dict) -> bool:
        return 'custom' in gate_id

    def apply(self, text: str, gate_id: str, gate_result: Dict,
             context: Dict) -> Optional[Dict]:
        # Your correction logic
        return {
            'text': corrected_text,
            'metadata': {
                'strategy': self.strategy_type,
                'changes': 1,
                'locations': [0],
                'reason': 'Custom correction',
                'examples': ['example']
            }
        }
```

**Step 2:** Register in `backend/core/corrector.py`

```python
def _init_advanced_system(self):
    # ... existing code ...
    self.custom_strategy = CustomStrategy()
    self.strategies.append(self.custom_strategy)
```

## API Integration

### Correction Endpoint

**POST** `/api/correct`

```javascript
// Request
{
  "text": "Document text",
  "validation_results": { /* from /api/validate */ },
  "document_type": "privacy",  // optional
  "advanced_options": {
    "multi_level": true,
    "context_aware": true,
    "document_metadata": {
      "document_type": "privacy",
      "module_id": "gdpr_uk",
      "confidence": 0.95
    }
  }
}

// Response
{
  "original": "...",
  "corrected": "...",
  "corrections_applied": [...],
  "correction_count": 5,
  "unchanged": false,
  "strategies_applied": ["regex_replacement", "template_insertion"],
  "determinism": {
    "input_hash": "...",
    "output_hash": "...",
    "repeatable": true
  },
  "validation": {
    "valid": true,
    "warnings": [],
    "errors": []
  }
}
```

## Best Practices

1. **Always validate first** - Run validation before correction
2. **Use context-aware mode** - Better results for specific document types
3. **Preview corrections** - Use `get_available_corrections()` before applying
4. **Verify determinism** - Check output hashes match on re-run
5. **Review validation** - Check `validation.valid` in response
6. **Handle warnings** - Address correction validation warnings
7. **Test new patterns** - Use `test_pattern_match()` for testing
8. **Document changes** - Update legal references when regulations change

## Troubleshooting

### No Corrections Applied

**Check:**
1. Gate status is 'FAIL' or 'WARNING'
2. Pattern matches using `test_pattern_match()`
3. Strategy `can_apply()` returns true
4. Condition regex matches (for templates)

### Wrong Corrections Applied

**Debug:**
1. Check pattern priority (lower number = first)
2. Review regex pattern syntax
3. Test individual strategies
4. Check context filtering

### Validation Errors

**Common Issues:**
- Document reduced by >50% - check deletion patterns
- Document grew by >200% - check template insertions
- Same correction repeated - check for loops

## Performance

**Typical Performance:**
- Small docs (<1KB): <10ms
- Medium docs (1-10KB): <50ms
- Large docs (>10KB): <200ms

**Optimization:**
- Use context-aware filtering to reduce corrections
- Patterns are compiled once and cached
- Multi-level processes in fixed passes

## When to Use This Skill

Activate this skill when:
- Working with document correction logic
- Adding or modifying correction patterns
- Debugging correction failures
- Implementing new correction strategies
- Reviewing correction results
- Optimizing correction performance
- Testing correction determinism
- Extending the correction system
