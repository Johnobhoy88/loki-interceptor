# Advanced Document Corrector - Enterprise-Grade Compliance System

## Overview

The Advanced Document Corrector is an enterprise-grade multi-level correction system for the LOKI compliance checker. It automatically applies rule-based corrections to documents based on validation results **without using AI**.

### Key Features

✅ **Gate-Specific Correction Patterns** - Pre-configured patterns for FCA UK, GDPR UK, Tax UK, NDA UK, and HR Scottish regulations
✅ **Context-Aware Correction Logic** - Understands document types and applies relevant corrections
✅ **Deterministic Synthesis** - Guarantees repeatable corrections across multiple runs
✅ **Multi-Level Strategies** - Regex replacements, template insertions, structural reorganization
✅ **Validation Layer** - Ensures correction integrity and document structure maintenance

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    DocumentCorrector                         │
│  Main interface for document correction                      │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────────┐    ┌────────────────────┐
│ Pattern Registry │    │ Synthesis Engine   │
│ - FCA UK         │    │ - Deterministic    │
│ - GDPR UK        │    │ - Multi-level      │
│ - Tax UK         │    │ - Context-aware    │
│ - NDA UK         │    │ - Validation       │
│ - HR Scottish    │    └────────────────────┘
└──────────────────┘              │
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
        ┌──────────────────────┐   ┌─────────────────────┐
        │ Correction Strategies │   │   Validator         │
        │ - Regex Replacement   │   │ - Integrity checks  │
        │ - Template Insertion  │   │ - Structure tests   │
        │ - Structural Reorg    │   │ - Safety validation │
        │ - Suggestion Extract  │   └─────────────────────┘
        └──────────────────────┘
```

## Modules

### 1. `corrector.py` - Main Interface

The primary interface for document correction.

**Usage:**

```python
from backend.core.corrector import DocumentCorrector

# Initialize (advanced mode enabled by default)
corrector = DocumentCorrector(advanced_mode=True)

# Basic correction
result = corrector.correct_document(text, validation_results)

# Multi-level correction
result = corrector.correct_document(
    text,
    validation_results,
    advanced_options={'multi_level': True}
)

# Context-aware correction
result = corrector.correct_document(
    text,
    validation_results,
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
```

**Response Format:**

```python
{
    'original': str,              # Original document text
    'corrected': str,             # Corrected document text
    'corrections_applied': List,  # List of corrections with metadata
    'unchanged': bool,            # True if no corrections needed
    'correction_count': int,      # Number of corrections applied
    'strategies_applied': List,   # List of strategy types used
    'determinism': {              # Determinism information
        'input_hash': str,
        'output_hash': str,
        'repeatable': bool
    },
    'validation': {               # Validation results
        'valid': bool,
        'warnings': List,
        'errors': List
    },
    'mode': str,                  # 'advanced' or 'legacy'
    'multi_level': bool,          # Whether multi-level was used
    'context_aware': bool         # Whether context-aware was used
}
```

### 2. `correction_strategies.py` - Correction Strategies

Four correction strategies with different priorities:

#### RegexReplacementStrategy (Priority: 30)
Simple find-and-replace using regex patterns.

**Example:**
- Find: `£85,000` → Replace: `£90,000` (VAT threshold update)
- Find: `investments can go down as well as up` → Replace: FCA-compliant warning

#### TemplateInsertionStrategy (Priority: 40)
Inserts pre-formatted compliance text at appropriate positions.

**Positions:**
- `start` - Beginning of document
- `end` - End of document
- `after_header` - After document header
- `before_signature` - Before signature block

**Example:**
```
⚠️ RISK WARNING: The value of investments can fall as well as rise
and you may get back less than you invest. Past performance is not
a reliable indicator of future results.
```

#### StructuralReorganizationStrategy (Priority: 60)
Reorganizes document structure for compliance.

**Operations:**
- Move risk warnings before benefit statements
- Add section headers
- Reorder sections for prominence

#### SuggestionExtractionStrategy (Priority: 20)
Extracts and applies suggestions from gate validation results.

### 3. `correction_patterns.py` - Pattern Registry

Pre-configured correction patterns organized by regulatory module.

#### FCA UK Patterns

**Risk/Benefit Balance:**
- Replaces weak risk warnings with FCA-compliant language
- Moves risk warnings to prominent positions
- Adds capital-at-risk warnings

**Fair, Clear, Not Misleading:**
- Removes "guaranteed returns" → "potential returns (not guaranteed)"
- Removes "risk-free" → "lower-risk (capital at risk)"

**Templates:**
- Target market definitions
- FOS (Financial Ombudsman Service) signposting
- Promotions approval statements

#### GDPR UK Patterns

**Consent Violations:**
- "By using this website, you automatically agree" → "We request your explicit consent"
- Removes bundled consent requirements
- Removes pre-selected/opt-out consent

**Templates:**
- Withdrawal of consent instructions
- Subject rights (access, rectification, erasure, etc.)
- Lawful basis statements
- Data retention periods
- International transfer notices

#### Tax UK Patterns

**VAT Threshold:**
- £85,000 → £90,000 (April 2024 update)
- £83,000 → £90,000

**HMRC Scam Detection:**
- Removes gift card payment requests
- Removes arrest threats
- Adds HMRC scam warnings

**Templates:**
- Making Tax Digital (MTD) notices
- IR35 status statements

#### NDA UK Patterns

**Protected Disclosures:**
- Whistleblowing protections (PIDA 1998)
- Crime reporting protections
- Harassment complaint protections (Equality Act 2010)

**Duration:**
- "in perpetuity" → "[specify reasonable duration]"
- "indefinitely" → "[specify period] years"

**Templates:**
- GDPR compliance in NDAs
- Governing law clauses
- Public domain exclusions

#### HR Scottish Patterns

**Accompaniment Rights:**
- Removes unlawful restrictions on legal representation
- Adds statutory accompaniment rights (ERA 1999 s10)

**Due Process:**
- Right to be heard statements
- Appeal rights notices
- Evidence disclosure requirements
- Impartial decision-maker statements

**Templates:**
- Notice of disciplinary/grievance meetings
- Suspension clarifications
- Confidentiality notices

### 4. `correction_synthesizer.py` - Deterministic Engine

Orchestrates correction strategies in a repeatable, deterministic manner.

**Key Features:**

1. **Deterministic Ordering** - Strategies applied in consistent priority order
2. **Gate Sorting** - Gates processed in alphabetical order for consistency
3. **Hash Verification** - Input/output hashes to verify repeatability
4. **Context Filtering** - Intelligent gate filtering based on document context

**Synthesis Modes:**

```python
# Standard synthesis
result = synthesizer.synthesize_corrections(text, gate_results)

# Context-aware synthesis
result = synthesizer.synthesize_with_context_awareness(
    text, gate_results, document_metadata
)

# Multi-level synthesis
result = synthesizer.synthesize_multi_level(
    text, gate_results,
    levels=['suggestion_extraction', 'regex_replacement',
            'template_insertion', 'structural_reorganization']
)
```

**Context-Aware Filtering Rules:**

1. Critical failures always included
2. High severity failures always included
3. Warnings filtered by document type relevance
4. Module-specific gates prioritized when module matches

## Usage Examples

### Example 1: Basic FCA Risk Warning Correction

```python
from backend.core.corrector import DocumentCorrector

text = """
Investment Opportunity
This product offers high returns and significant profit potential.
"""

validation_results = {
    'validation': {
        'modules': {
            'fca_uk': {
                'gates': {
                    'risk_benefit_balance': {
                        'status': 'FAIL',
                        'severity': 'high',
                        'message': 'Benefits mentioned without risk warnings'
                    }
                }
            }
        }
    }
}

corrector = DocumentCorrector()
result = corrector.correct_document(text, validation_results)

print(f"Corrections: {result['correction_count']}")
print(f"Strategies: {result['strategies_applied']}")
# Output:
# Corrections: 1
# Strategies: ['template_insertion']
```

### Example 2: GDPR Consent Correction

```python
text = """
Privacy Policy
By using this website, you automatically agree to our data collection.
"""

validation_results = {
    'validation': {
        'modules': {
            'gdpr_uk': {
                'gates': {
                    'consent': {
                        'status': 'FAIL',
                        'severity': 'critical',
                        'message': 'Forced consent detected'
                    }
                }
            }
        }
    }
}

corrector = DocumentCorrector()
result = corrector.correct_document(text, validation_results)

# The forced consent language is replaced with GDPR-compliant text
assert 'automatically agree' not in result['corrected']
assert 'explicit consent' in result['corrected']
```

### Example 3: Multi-Module Correction

```python
text = """
Investment and Privacy Notice
By using this service you agree to everything.
VAT registration threshold is £85,000.
Guaranteed risk-free returns!
"""

validation_results = {
    'validation': {
        'modules': {
            'fca_uk': {
                'gates': {
                    'fair_clear': {'status': 'FAIL', 'severity': 'critical'}
                }
            },
            'gdpr_uk': {
                'gates': {
                    'consent': {'status': 'FAIL', 'severity': 'critical'}
                }
            },
            'tax_uk': {
                'gates': {
                    'vat_threshold': {'status': 'FAIL', 'severity': 'medium'}
                }
            }
        }
    }
}

corrector = DocumentCorrector()
result = corrector.correct_document(
    text,
    validation_results,
    advanced_options={'multi_level': True}
)

# Multiple corrections applied across different modules
print(f"Total corrections: {result['correction_count']}")
# Output: Total corrections: 3
```

### Example 4: Context-Aware Correction

```python
text = """Privacy Notice - We process your data."""

validation_results = {
    'validation': {
        'modules': {
            'gdpr_uk': {
                'gates': {
                    'lawful_basis': {'status': 'WARNING', 'severity': 'medium'},
                    'consent': {'status': 'FAIL', 'severity': 'critical'}
                }
            },
            'fca_uk': {
                'gates': {
                    'risk_warning': {'status': 'WARNING', 'severity': 'low'}
                }
            }
        }
    }
}

corrector = DocumentCorrector()
result = corrector.correct_document(
    text,
    validation_results,
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

# Only GDPR corrections applied (FCA warning filtered out due to low relevance)
print([c['gate_id'] for c in result['corrections_applied']])
# Output: ['consent', 'lawful_basis']
```

## Utility Methods

### Get Available Corrections

Preview corrections without applying them:

```python
corrector = DocumentCorrector()
preview = corrector.get_available_corrections(text, validation_results)

print(f"Failing gates: {preview['failing_gates']}")
print(f"Estimated changes: {preview['estimated_changes']}")
```

### Get Correction Statistics

View system capabilities:

```python
corrector = DocumentCorrector()
stats = corrector.get_correction_statistics()

print(f"Total patterns: {stats['total_patterns']}")
print(f"Modules: {stats['modules']}")
# Output:
# Total patterns: 46
# Modules: ['FCA UK', 'GDPR UK', 'HR Scottish', 'NDA UK', 'Tax UK']
```

### Test Pattern Matching

Test if patterns would match specific text:

```python
corrector = DocumentCorrector()
result = corrector.test_pattern_match(
    "VAT threshold is £85,000",
    "vat_threshold"
)

print(f"Would correct: {result['would_correct']}")
print(f"Matches: {result['matches']}")
```

## Determinism Guarantees

The system provides strong determinism guarantees:

1. **Consistent Ordering** - Strategies and gates processed in fixed order
2. **No Random Elements** - No random numbers or timing-dependent operations
3. **Hash Verification** - Input and output hashes verify repeatability
4. **Idempotent** - Running correction multiple times produces identical results

**Verification:**

```python
corrector = DocumentCorrector()

result1 = corrector.correct_document(text, validation_results)
result2 = corrector.correct_document(text, validation_results)
result3 = corrector.correct_document(text, validation_results)

# All results are identical
assert result1['corrected'] == result2['corrected'] == result3['corrected']
assert result1['determinism']['output_hash'] == result2['determinism']['output_hash']
```

## Performance Characteristics

- **Strategy Priority System** - Higher priority strategies execute first
- **Early Termination** - Stops after first successful strategy per gate
- **Pattern Caching** - Regex patterns compiled once and reused
- **Minimal Text Passes** - Multi-level mode processes document in fixed passes

**Typical Performance:**
- Small documents (<1KB): <10ms
- Medium documents (1-10KB): <50ms
- Large documents (>10KB): <200ms

## Testing

Run the comprehensive test suite:

```bash
cd backend/core
python3 test_advanced_corrector.py
```

**Tests include:**
- Basic regex replacement corrections
- GDPR consent corrections
- VAT threshold updates
- Multi-level correction strategy
- Context-aware filtering
- Correction statistics
- Pattern matching
- Determinism verification

## Migration from Legacy Mode

The system maintains backward compatibility with legacy mode:

```python
# New advanced mode (default)
corrector = DocumentCorrector(advanced_mode=True)

# Legacy mode for backward compatibility
corrector = DocumentCorrector(advanced_mode=False)
```

**Legacy mode:**
- Uses simple regex rules from original implementation
- No multi-level strategies
- No context-aware filtering
- No determinism hashing

## Extension Guide

### Adding New Correction Patterns

Edit `correction_patterns.py`:

```python
# Add to appropriate module initialization method
def _init_fca_uk_patterns(self):
    # Add regex pattern
    self.regex_patterns['new_pattern_id'] = [{
        'pattern': r'your_regex_here',
        'replacement': 'replacement_text',
        'reason': 'Explanation for correction',
        'flags': re.IGNORECASE
    }]

    # Add template
    self.templates['new_template_id'] = [{
        'template': 'Your compliance text here',
        'position': 'end',  # or 'start', 'after_header', 'before_signature'
        'condition': r'optional_condition_regex'
    }]
```

### Adding New Correction Strategies

Subclass `CorrectionStrategy` in `correction_strategies.py`:

```python
class CustomStrategy(CorrectionStrategy):
    def __init__(self):
        super().__init__("custom_strategy", priority=45)

    def can_apply(self, text: str, gate_id: str, gate_result: Dict) -> bool:
        # Return True if this strategy applies
        return 'custom' in gate_id

    def apply(self, text: str, gate_id: str, gate_result: Dict,
             context: Dict) -> Optional[Dict]:
        # Apply your correction logic
        corrected_text = text  # ... your logic here

        return {
            'text': corrected_text,
            'metadata': {
                'strategy': self.strategy_type,
                'changes': 1,
                'locations': [0],
                'reason': 'Custom correction applied',
                'examples': ['example']
            }
        }
```

Then register it in `corrector.py`:

```python
self.custom_strategy = CustomStrategy()
self.strategies.append(self.custom_strategy)
```

## Troubleshooting

### Corrections Not Applied

1. Check gate status is 'FAIL' or 'WARNING'
2. Verify pattern matches using `test_pattern_match()`
3. Check strategy priority ordering
4. Enable debug logging

### Incorrect Corrections

1. Test patterns individually with `test_pattern_match()`
2. Review correction examples in result
3. Check regex pattern syntax
4. Verify template conditions

### Performance Issues

1. Use multi-level mode with specific levels
2. Enable context-aware filtering
3. Review regex pattern complexity
4. Consider pattern caching

## License & Compliance

This correction system is designed for defensive security and compliance purposes only. It:

- ✅ Helps organizations comply with regulations
- ✅ Corrects non-compliant language
- ✅ Adds required disclosures
- ❌ Does not use AI or machine learning
- ❌ Does not send data externally
- ❌ Does not store personal information

## Support

For issues or questions:
- Review test suite: `test_advanced_corrector.py`
- Check pattern registry: `correction_patterns.py`
- Consult gate modules: `backend/modules/`

---

**Version:** 1.0.0
**Last Updated:** 2025-10-25
**Modules Supported:** FCA UK, GDPR UK, Tax UK, NDA UK, HR Scottish
