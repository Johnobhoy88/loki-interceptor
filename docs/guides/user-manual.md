# LOKI Interceptor User Manual

Complete guide for using LOKI Interceptor to validate and correct compliance documents.

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Document Validation](#document-validation)
5. [Document Correction](#document-correction)
6. [Compliance Modules](#compliance-modules)
7. [Best Practices](#best-practices)
8. [FAQ](#faq)

---

## Introduction

LOKI Interceptor is an AI-powered compliance system that:
- **Validates** documents against UK regulatory frameworks
- **Corrects** compliance issues automatically
- **Explains** findings with legal references
- **Generates** audit trails for compliance evidence

### Key Capabilities

| Feature | Description |
|---------|-------------|
| **141 Detection Rules** | Comprehensive coverage across 5 frameworks |
| **5 Compliance Modules** | FCA, GDPR, Tax, NDA, HR |
| **Automatic Correction** | Rule-based fixes with confidence scoring |
| **Deterministic Results** | Consistent outputs via SHA256 hashing |
| **Audit Trail** | Complete change tracking |
| **REST API** | Production-ready HTTP interface |

---

## Installation

### System Requirements
- Python 3.8 or higher
- 4GB RAM (minimum)
- 200MB disk space

### Quick Setup

```bash
# 1. Clone repository
git clone https://github.com/Johnobhoy88/loki-interceptor.git
cd loki-interceptor

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API key
cp .env.example .env
# Edit .env and add ANTHROPIC_API_KEY

# 5. Run API server
python -m backend.api.main

# API will be available at http://localhost:8000
```

---

## Quick Start

### Option 1: Command Line

```bash
# Validate a document
python -m backend.cli validate \
  --file document.txt \
  --type financial \
  --modules fca_uk gdpr_uk

# Validate and correct
python -m backend.cli correct \
  --file document.txt \
  --type financial \
  --output corrected.txt
```

### Option 2: Python API

```python
from backend.core.document_validator import DocumentValidator
from backend.core.document_corrector import DocumentCorrector

# Initialize
validator = DocumentValidator()
corrector = DocumentCorrector(advanced_mode=True)

# Validate
text = "Your document..."
results = validator.validate_document(
    text=text,
    document_type="financial",
    modules=["fca_uk", "gdpr_uk"]
)

# Check results
if results['validation']['status'] == 'FAIL':
    print(f"Risk: {results['validation']['overall_risk']}")

    # Correct
    corrections = corrector.correct_document(
        text=text,
        validation_results=results,
        document_type="financial"
    )

    print(f"Original: {corrections['original'][:100]}...")
    print(f"Corrected: {corrections['corrected'][:100]}...")
    print(f"Applied: {corrections['correction_count']} corrections")
```

### Option 3: REST API

```bash
curl -X POST http://localhost:8000/api/v1/validate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your document text...",
    "document_type": "financial",
    "modules": ["fca_uk"]
  }'
```

---

## Document Validation

### Step 1: Prepare Document

1. **Extract text** from your document
2. **Specify document type** (e.g., "financial_promotion", "privacy_policy")
3. **Choose modules** to validate against

### Step 2: Run Validation

```python
from backend.core.document_validator import DocumentValidator

validator = DocumentValidator()

results = validator.validate_document(
    text="Your document...",
    document_type="financial",
    modules=["fca_uk", "gdpr_uk"],
    context={"industry": "financial_services"}
)
```

### Step 3: Review Results

```python
# Overall status
status = results['validation']['status']  # PASS or FAIL
overall_risk = results['validation']['overall_risk']  # LOW, MEDIUM, HIGH, CRITICAL

# Module results
for module_name, module_data in results['validation']['modules'].items():
    print(f"\n{module_name}:")
    print(f"  Gates Checked: {module_data['gates_checked']}")
    print(f"  Gates Failed: {module_data['gates_failed']}")

    # Failed gates
    for gate in module_data['gates']:
        if gate['passed'] == False:
            print(f"  ❌ {gate['gate_name']}")
            print(f"     {gate['message']}")
            if gate.get('legal_source'):
                print(f"     Legal: {gate['legal_source']}")
            if gate.get('suggestions'):
                print(f"     Suggestions: {', '.join(gate['suggestions'])}")
```

### Understanding Risk Levels

| Level | Description | Action |
|-------|-------------|--------|
| **LOW** | No issues | Publish as-is |
| **MEDIUM** | Minor issues | Review suggestions |
| **HIGH** | Multiple issues | Mandatory correction |
| **CRITICAL** | Severe violations | Must correct |

---

## Document Correction

### Correction Workflow

```python
from backend.core.document_corrector import DocumentCorrector

# 1. Validate first
validator = DocumentValidator()
validation_results = validator.validate_document(text, "financial", ["fca_uk"])

# 2. Initialize corrector
corrector = DocumentCorrector(
    advanced_mode=True,
    max_iterations=3,
    confidence_threshold=0.8
)

# 3. Apply corrections
corrections = corrector.correct_document(
    text=text,
    validation_results=validation_results,
    document_type="financial",
    preserve_formatting=True
)
```

### Analyzing Corrections

```python
# Summary
print(f"Issues Found: {corrections['issues_found']}")
print(f"Issues Corrected: {corrections['issues_corrected']}")
print(f"Correction Rate: {corrections['issues_corrected'] / corrections['issues_found']:.0%}")

# Detailed corrections
for i, correction in enumerate(corrections['corrections'], 1):
    print(f"\n{i}. {correction['reason']}")
    print(f"   Strategy: {correction['strategy']}")
    print(f"   Confidence: {correction['confidence']:.0%}")
    print(f"   Before: {correction['before'][:50]}...")
    print(f"   After: {correction['after'][:50]}...")

# Suggestions for manual review
print(f"\nManual Review Needed:")
for suggestion in corrections['suggestions']:
    print(f"  • {suggestion}")
```

### Correction Strategies

LOKI uses a 4-tier strategy system, applied in priority order:

| Strategy | Priority | Example |
|----------|----------|---------|
| **Suggestion** | 20 | Recommend removing vague language |
| **Regex** | 30 | Replace "guaranteed" with "projected" |
| **Template** | 40 | Insert standard risk disclaimer |
| **Structural** | 60 | Reorganize document sections |

Higher priority strategies are applied first and prevent lower priority strategies from running.

---

## Compliance Modules

### FCA UK - Financial Conduct Authority

**51 Detection Rules | Best for**: Financial promotions, investment documents

```python
modules = ["fca_uk"]

# Checks:
# - Fair, Clear, Not Misleading (COBS 4.2.1)
# - Risk/Benefit Balance (COBS 4.2.3)
# - Past Performance Rules
# - Pressure Tactics
# - Implicit Advice Detection
```

**Common Issues**:
- Unsubstantiated performance claims
- Missing risk warnings
- Misleading language
- Unsuitable targeting

### GDPR UK - Data Protection

**29 Detection Rules | Best for**: Privacy policies, consent forms, data documents

```python
modules = ["gdpr_uk"]

# Checks:
# - Lawful Basis (Article 6)
# - Consent Requirements (Article 7)
# - Information to be Provided (Article 13)
# - Children's Data (Article 8)
# - Automated Decision-Making (Article 22)
# - International Transfers (Articles 44-46)
```

**Common Issues**:
- Vague consent language
- Missing privacy information
- Weak security statements
- Unauthorized sharing

### Tax UK - HMRC Compliance

**25 Detection Rules | Best for**: Invoices, tax documents, financial records

```python
modules = ["tax_uk"]

# Checks:
# - VAT Compliance (VAT Act 1994)
# - Income Tax (ITTOIA 2005)
# - Making Tax Digital (MTD)
# - Invoice Requirements
# - Scottish Income Tax
```

**Common Issues**:
- Invalid VAT numbers
- Incomplete invoices
- Wrong tax rates
- Missing required fields

### NDA UK - Non-Disclosure Agreements

**12 Detection Rules | Best for**: NDAs, confidentiality agreements

```python
modules = ["nda_uk"]

# Checks:
# - Whistleblowing Protection (PIDA 1998)
# - Reasonableness
# - GDPR Compliance
# - Legal Rights Protection
# - Contract Enforceability
```

**Common Issues**:
- Overly broad restrictions
- Unlawful provisions
- Unreasonable durations
- Unprotected legal rights

### HR Scottish - Employment Law

**24 Detection Rules | Best for**: Employment contracts, disciplinary letters

```python
modules = ["hr_scottish"]

# Checks:
# - ACAS Code of Practice
# - Accompaniment Rights (ERA 1999 s10)
# - Natural Justice Principles
# - Scottish Employment Law
# - Procedural Fairness
```

**Common Issues**:
- Missing rights information
- Vague allegations
- Insufficient notice
- Procedural unfairness

---

## Best Practices

### 1. Validation Strategy

```python
# For new documents: Check all modules
modules = ["fca_uk", "gdpr_uk", "tax_uk", "nda_uk", "hr_scottish"]

# For financial documents: Focus on FCA + GDPR
modules = ["fca_uk", "gdpr_uk"]

# For employment: Focus on HR + GDPR
modules = ["hr_scottish", "gdpr_uk"]
```

### 2. Correction Workflow

1. **Validate** with all relevant modules
2. **Review** high-confidence corrections
3. **Apply** corrections with confidence > 0.85
4. **Manually review** medium-confidence items (0.60-0.85)
5. **Reject** low-confidence suggestions (< 0.60)

### 3. Quality Assurance

```python
# Validate corrected document
corrected_text = corrections['corrected']

# Run validation again
qa_results = validator.validate_document(
    corrected_text,
    "financial",
    ["fca_uk"]
)

# Check improvement
improvement = (
    (validation_results['gates_failed'] - qa_results['gates_failed']) /
    validation_results['gates_failed']
)

print(f"Improvement: {improvement:.0%}")
```

### 4. Batch Processing

```python
import glob

for filepath in glob.glob("documents/*.txt"):
    with open(filepath, 'r') as f:
        text = f.read()

    # Validate
    results = validator.validate_document(text, "financial", ["fca_uk"])

    if results['validation']['status'] == 'FAIL':
        # Correct
        corrections = corrector.correct_document(
            text, results, "financial"
        )

        # Save
        output_path = filepath.replace('.txt', '_corrected.txt')
        with open(output_path, 'w') as f:
            f.write(corrections['corrected'])

        print(f"✓ {filepath} ({corrections['correction_count']} fixes)")
```

### 5. Audit Trail

```python
# Every correction includes:
# - Original text
# - Corrected text
# - Each correction with:
#   - Pattern matched
#   - Reason (legal basis)
#   - Confidence score
#   - Strategy used

# Use this for compliance evidence:
audit_report = {
    "document_hash": hash_original_document,
    "validations": validation_results,
    "corrections": corrections['corrections'],
    "timestamp": datetime.now().isoformat(),
    "user": current_user
}

# Save for records
import json
with open(f"audit/{doc_id}.json", 'w') as f:
    json.dump(audit_report, f, indent=2)
```

---

## FAQ

### Q: Can LOKI correct AI-generated content?
**A**: Yes. LOKI focuses on compliance issues, not the origin of content. It applies rule-based corrections to any text.

### Q: How long does validation take?
**A**: Typically 1-5 seconds depending on document length and modules. Caching can reduce this to <100ms for repeated validations.

### Q: Are corrections always safe to apply?
**A**: Corrections with high confidence (>0.85) are generally safe. Always review medium-confidence corrections (0.60-0.85) before auto-applying.

### Q: Can I add custom rules?
**A**: Yes, through the CorrectionPatternRegistry API:

```python
from backend.core.correction_patterns import CorrectionPatternRegistry

registry = CorrectionPatternRegistry()
registry.add_custom_pattern(
    module='fca_uk',
    category='custom',
    pattern={
        'pattern': r'your_regex',
        'replacement': 'corrected_text',
        'reason': 'Your compliance reason'
    }
)
```

### Q: How is data processed?
**A**: Document text is processed locally. Only error telemetry is sent to Anthropic. No text is stored permanently.

### Q: Can I use LOKI offline?
**A**: The validator runs locally. The AI analyzer requires API connectivity for enhanced semantic analysis.

### Q: What's the difference between modules?
**A**: Each module validates against different UK regulatory frameworks. See [Compliance Modules](#compliance-modules) for details.

### Q: How do I handle batch errors?
**A**: Implement retry logic with exponential backoff:

```python
import time

for attempt in range(3):
    try:
        result = validate_document(text, doc_type, modules)
        break
    except Exception as e:
        wait_time = 2 ** attempt
        print(f"Attempt {attempt + 1} failed. Retrying in {wait_time}s...")
        time.sleep(wait_time)
```

---

## Support & Resources

- **Documentation**: https://github.com/Johnobhoy88/loki-interceptor/wiki
- **API Reference**: [docs/api/README.md](../api/README.md)
- **Examples**: [docs/api/examples.md](../api/examples.md)
- **Issues**: https://github.com/Johnobhoy88/loki-interceptor/issues
- **Email**: support@highlandai.com

---

**Version**: 1.0.0
**Last Updated**: 2025-11-11
