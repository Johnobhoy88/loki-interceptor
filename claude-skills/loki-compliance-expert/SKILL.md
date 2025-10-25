---
name: loki-compliance-expert
description: Expert in LOKI compliance checking system, regulatory modules (FCA, GDPR, Tax UK, NDA UK, HR Scottish), gate structure, validation logic, and compliance rules
---

# LOKI Compliance Expert Skill

You are an expert in the LOKI compliance checking system. This skill provides comprehensive knowledge of LOKI's regulatory modules, gate structure, validation logic, and compliance rules.

## System Overview

LOKI is a multi-gate compliance validation system that checks documents against regulatory requirements for:
- **FCA UK** - Financial Conduct Authority regulations
- **GDPR UK** - Data protection and privacy regulations
- **Tax UK** - HMRC and tax compliance
- **NDA UK** - Non-disclosure agreement legal requirements
- **HR Scottish** - Scottish employment law compliance

## Core Architecture

### Module Structure

All compliance modules follow a consistent structure:

```
backend/modules/{module_id}/
├── __init__.py
├── module.py          # Module definition and gate registry
└── gates/
    ├── __init__.py
    └── {gate_name}.py # Individual gate implementations
```

### Gate Implementation Pattern

Each gate follows this standard pattern:

```python
class GateName:
    def __init__(self):
        self.name = "gate_identifier"
        self.severity = "critical" | "high" | "medium" | "low"
        self.legal_source = "Legal reference (e.g., GDPR Article 6)"

    def _is_relevant(self, text):
        """Check if gate applies to this document"""
        # Check for relevance keywords

    def check(self, text, document_type):
        """
        Perform compliance check

        Returns:
            {
                'status': 'PASS' | 'FAIL' | 'WARNING' | 'N/A',
                'severity': str,
                'message': str,
                'legal_source': str,
                'suggestion': str (optional),
                'spans': List[dict] (optional),
                'details': List[str] (optional),
                'penalty': str (optional)
            }
        """
```

## Regulatory Modules

### 1. FCA UK (Financial Conduct Authority)

**Location:** `backend/modules/fca_uk/`

**Key Gates:**

1. **risk_benefit_balance** (`gates/risk_benefit_balance.py`)
   - Legal: FCA COBS 4.2.3
   - Checks: Benefits vs risk warnings ratio, missing required warnings
   - Required warnings: capital_at_risk, not_guaranteed, can_go_down, past_performance
   - Severity: High
   - Example: "Benefits mentioned without risk warnings" → FAIL

2. **fair_clear_not_misleading** (`gates/fair_clear_not_misleading.py`)
   - Legal: FCA COBS 4.2.1
   - Checks: Misleading claims, exaggerations, unclear language
   - Severity: Critical
   - Example: "Guaranteed returns" → FAIL

3. **target_market_definition** (`gates/target_market_definition.py`)
   - Legal: FCA PROD 3.2
   - Checks: Target market specification, characteristics, objectives
   - Severity: High
   - Example: Missing target market definition → FAIL

4. **fos_signposting** (`gates/fos_signposting.py`)
   - Legal: FCA DISP 1.2
   - Checks: Financial Ombudsman Service information
   - Severity: Medium
   - Example: No FOS contact information → WARNING

5. **promotions_approval** (`gates/promotions_approval.py`)
   - Legal: FCA COBS 4.10
   - Checks: Approval by authorized firm
   - Severity: Critical
   - Example: No approval statement → FAIL

6. **target_audience** (`gates/target_audience.py`)
   - Checks: Appropriate audience targeting
   - Severity: Medium

7. **client_money_segregation** (`gates/client_money_segregation.py`)
   - Legal: FCA CASS 7
   - Checks: Client money protection disclosure
   - Severity: High

8. **vulnerability_identification** (`gates/vulnerability_identification.py`)
   - Legal: FCA Consumer Duty
   - Checks: Vulnerable customer considerations
   - Severity: Medium

**Common FCA Violations:**
- Presenting benefits without equally prominent risk warnings
- "Guaranteed returns" or "risk-free" claims
- Missing past performance disclaimers
- No target market definition
- Unapproved financial promotions

### 2. GDPR UK (Data Protection)

**Location:** `backend/modules/gdpr_uk/`

**Key Gates:**

1. **consent** (`gates/consent.py`)
   - Legal: GDPR Article 6 & 7
   - Checks: Forced consent, bundled consent, pre-selected consent
   - Severity: Critical
   - Violations:
     - "By using this website, you automatically agree" → FAIL
     - Bundled consent (multiple purposes in one checkbox)
     - Opt-out instead of opt-in
     - Conditional service tied to non-essential consent

2. **withdrawal_consent** (`gates/withdrawal_consent.py`)
   - Legal: GDPR Article 7(3)
   - Checks: Right to withdraw consent
   - Severity: High
   - Example: No withdrawal mechanism → FAIL

3. **rights** (`gates/rights.py`)
   - Legal: GDPR Articles 15-22
   - Checks: Subject rights information (access, rectification, erasure, etc.)
   - Severity: High
   - Required rights: Access, Rectification, Erasure, Restriction, Portability, Object

4. **lawful_basis** (`gates/lawful_basis.py`)
   - Legal: GDPR Article 6
   - Checks: Lawful basis for processing stated
   - Severity: Critical
   - Bases: Consent, Contract, Legal obligation, Vital interests, Public task, Legitimate interests

5. **purpose** (`gates/purpose.py`)
   - Legal: GDPR Article 5(1)(b)
   - Checks: Purpose specification
   - Severity: High

6. **retention** (`gates/retention.py`)
   - Legal: GDPR Article 5(1)(e)
   - Checks: Retention period specification
   - Severity: Medium

7. **security** (`gates/security.py`)
   - Legal: GDPR Article 32
   - Checks: Security measures disclosure
   - Severity: High

8. **international_transfer** (`gates/international_transfer.py`)
   - Legal: GDPR Chapter V
   - Checks: International data transfer safeguards
   - Severity: Critical

9. **dpo_contact** (`gates/dpo_contact.py`)
   - Legal: GDPR Article 37
   - Checks: DPO contact information (when required)
   - Severity: Medium

10. **cookies_tracking** (`gates/cookies_tracking.py`)
    - Legal: PECR Regulation 6
    - Checks: Cookie consent
    - Severity: High

11. **children_data** (`gates/children_data.py`)
    - Legal: GDPR Article 8
    - Checks: Parental consent for children under 13
    - Severity: Critical

**GDPR Penalties:** Up to €20M or 4% of global annual revenue

### 3. Tax UK (HMRC Compliance)

**Location:** `backend/modules/tax_uk/`

**Key Gates:**

1. **vat_threshold** (inferred from corrector patterns)
   - Current threshold: £90,000 (April 2024)
   - Old thresholds: £85,000, £83,000
   - Checks: Outdated VAT registration thresholds

2. **hmrc_scam_detection** (`gates/hmrc_scam_detection.py`)
   - Legal: Fraud Act 2006
   - Severity: Critical
   - Scam indicators:
     - Gift card payments (iTunes, Amazon, Google Play)
     - Arrest threats
     - Cryptocurrency payment requests
     - Non-government email addresses (@hmrc.gov.uk required)
     - Urgent payment demands
   - Example: "Pay via iTunes gift card" → FAIL (SCAM DETECTED)

3. **allowable_expenses** (`gates/allowable_expenses.py`)
   - Checks: Proper expense categorization
   - Severity: Medium

**Tax Compliance Notes:**
- HMRC NEVER requests payment via gift cards or cryptocurrency
- HMRC NEVER threatens immediate arrest
- Always verify through gov.uk
- Making Tax Digital (MTD) compliance required for VAT-registered businesses

### 4. NDA UK (Non-Disclosure Agreements)

**Location:** `backend/modules/nda_uk/`

**Key Gates:**

1. **protected_whistleblowing** (`gates/protected_whistleblowing.py`)
   - Legal: Public Interest Disclosure Act 1998, ERA 1996 Section 43J
   - Severity: Critical
   - Checks: Blanket prohibition without whistleblowing exception
   - Required: Carve-out for PIDA 1998 protected disclosures
   - Example: "Shall not disclose to any third party under any circumstances" without exception → FAIL

2. **protected_crime_reporting** (`gates/protected_crime_reporting.py`)
   - Legal: Common law right to report crime
   - Severity: Critical
   - Checks: Right to report criminal activity preserved

3. **protected_harassment** (`gates/protected_harassment.py`)
   - Legal: Equality Act 2010 Section 111
   - Severity: Critical
   - Checks: Right to report harassment/discrimination preserved

4. **duration_reasonableness** (`gates/duration_reasonableness.py`)
   - Severity: Medium
   - Checks: "in perpetuity" or "indefinitely" → unreasonable
   - Reasonable: 2-5 years for commercial information

5. **governing_law** (`gates/governing_law.py`)
   - Checks: Governing law clause (England/Wales, Scotland, NI)
   - Severity: Low

6. **public_domain_exclusion** (`gates/public_domain_exclusion.py`)
   - Checks: Exclusions for publicly available information
   - Severity: Medium

7. **gdpr_compliance** (`gates/gdpr_compliance.py`)
   - Checks: GDPR compliance in NDA
   - Severity: High

8. **parties_identified** (`gates/parties_identified.py`)
   - Checks: Parties clearly identified
   - Severity: High

**NDA Legal Requirements:**
- Must allow whistleblowing (PIDA 1998)
- Must allow crime reporting
- Must allow harassment complaints (Equality Act 2010)
- Duration must be reasonable
- Cannot override statutory rights

### 5. HR Scottish (Employment Law - Scotland)

**Location:** `backend/modules/hr_scottish/`

**Key Gates:**

1. **accompaniment** (`gates/accompaniment.py`)
   - Legal: Employment Relations Act 1999, Section 10
   - Severity: Critical
   - Checks: Statutory right to be accompanied at disciplinary/grievance meetings
   - Required: "Right to be accompanied by work colleague or trade union representative"
   - Violations: Restrictions on legal representation
   - Example: "You may not bring a lawyer" → FAIL

2. **appeal** (`gates/appeal.py`)
   - Legal: ACAS Code of Practice
   - Severity: High
   - Checks: Right to appeal disciplinary decisions
   - Timeframe: Typically 5-10 working days

3. **notice** (`gates/notice.py`)
   - Checks: Proper notice of meetings
   - Severity: High

4. **right_to_be_heard** (`gates/right_to_be_heard.py`)
   - Checks: Opportunity to respond to allegations
   - Severity: Critical

5. **evidence** (`gates/evidence.py`)
   - Checks: Evidence disclosure (typically 48 hours advance)
   - Severity: High

6. **impartial_chair** (`gates/impartial_chair.py`)
   - Checks: Impartial decision-maker
   - Severity: High

7. **suspension** (`gates/suspension.py`)
   - Checks: Suspension clarification (neutral act, full pay)
   - Severity: Medium

8. **allegations** (`gates/allegations.py`)
   - Checks: Clear allegations statement
   - Severity: High

9. **investigation** (`gates/investigation.py`)
   - Checks: Proper investigation process
   - Severity: High

10. **meeting_details** (`gates/meeting_details.py`)
    - Checks: Meeting date, time, location specified
    - Severity: Medium

**ACAS Code Compliance:**
- Breach can add up to 25% to tribunal awards
- Must provide accompaniment rights
- Must allow appeals
- Must conduct fair investigations
- Suspension is neutral (not disciplinary sanction)

## Gate Status Values

- **PASS**: Fully compliant
- **FAIL**: Non-compliant, requires correction
- **WARNING**: Potential issue, review recommended
- **N/A**: Not applicable to this document

## Severity Levels

- **critical**: Legal violation, high penalty risk
- **high**: Significant compliance issue
- **medium**: Moderate compliance concern
- **low**: Minor issue or best practice
- **none**: Informational only

## Common Patterns

### Relevance Checking

Gates use `_is_relevant()` to determine if they apply:

```python
def _is_relevant(self, text):
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in [
        'investment', 'return', 'profit'  # Example keywords
    ])
```

### Span Marking

Non-compliant text is marked with spans:

```python
spans.append({
    'type': 'violation_type',
    'start': match.start(),
    'end': match.end(),
    'text': match.group(),
    'severity': 'critical'
})
```

### Suggestions

Gates provide actionable suggestions:

```python
'suggestion': 'Add: "You have the right to be accompanied by a work colleague or trade union representative."'
```

## API Endpoints

### Validation Endpoint

**POST** `http://localhost:3001/api/validate`

Request:
```json
{
  "text": "Document text to validate",
  "document_type": "financial" | "privacy" | "tax" | "nda" | "employment"
}
```

Response:
```json
{
  "validation": {
    "overall_status": "FAIL",
    "overall_severity": "critical",
    "timestamp": "2025-10-25T...",
    "modules": {
      "fca_uk": {
        "status": "FAIL",
        "gates": {
          "risk_benefit_balance": {
            "status": "FAIL",
            "severity": "high",
            "message": "Benefits mentioned without risk warnings",
            "legal_source": "FCA COBS 4.2.3",
            "suggestion": "Include risk warnings...",
            "spans": [...],
            "details": [...]
          }
        }
      }
    }
  }
}
```

### Correction Endpoint

**POST** `http://localhost:3001/api/correct`

Request:
```json
{
  "text": "Document text",
  "validation_results": { /* validation response */ },
  "advanced_options": {
    "multi_level": true,
    "context_aware": true
  }
}
```

## File Paths Reference

### Module Files

- FCA UK module: `backend/modules/fca_uk/module.py`
- GDPR UK module: `backend/modules/gdpr_uk/module.py`
- Tax UK module: `backend/modules/tax_uk/module.py`
- NDA UK module: `backend/modules/nda_uk/module.py`
- HR Scottish module: `backend/modules/hr_scottish/module.py`

### Gate Implementations

All gates follow pattern: `backend/modules/{module_id}/gates/{gate_name}.py`

### Engine

- Validation engine: `backend/core/engine.py`
- Gate loader: `backend/core/gate_loader.py`

## Working with Gates

### Adding a New Gate

1. Create gate file in `backend/modules/{module_id}/gates/{gate_name}.py`
2. Implement gate class with `check()` method
3. Register in module's `module.py`
4. Add correction patterns in `backend/core/correction_patterns.py`

### Testing Gates

```python
from backend.modules.fca_uk.gates.risk_benefit_balance import RiskBenefitBalanceGate

gate = RiskBenefitBalanceGate()
result = gate.check(text, document_type="financial")
print(result['status'])  # PASS, FAIL, WARNING, or N/A
```

### Module Registration

In `module.py`:

```python
def get_gates():
    return [
        RiskBenefitBalanceGate(),
        FairClearGate(),
        # ... other gates
    ]
```

## Best Practices

1. **Always check relevance** - Use `_is_relevant()` to avoid false positives
2. **Provide legal sources** - Reference specific regulations
3. **Give actionable suggestions** - Help users fix issues
4. **Use appropriate severity** - Match to legal/business impact
5. **Mark violations with spans** - Enable precise highlighting
6. **Consider document type** - Context matters for applicability

## Regulatory Updates

When regulations change:

1. Update gate logic in `backend/modules/{module}/gates/`
2. Update correction patterns in `backend/core/correction_patterns.py`
3. Update legal_source references
4. Add tests for new requirements
5. Document changes in commit messages

## Common Debugging Queries

```python
# Check if gate is registered
from backend.modules.fca_uk.module import get_gates
gates = get_gates()
print([g.name for g in gates])

# Test single gate
gate = RiskBenefitBalanceGate()
result = gate.check("Investment with high returns!", "financial")
print(result)

# Check relevance
gate = ConsentGate()
print(gate._is_relevant("We collect your personal data"))  # True
print(gate._is_relevant("Tax information"))  # False
```

## Legal Reference Quick Guide

- **FCA COBS** - Conduct of Business Sourcebook
- **FCA PROD** - Product Intervention and Product Governance Sourcebook
- **FCA DISP** - Dispute Resolution Sourcebook
- **FCA CASS** - Client Assets Sourcebook
- **GDPR** - General Data Protection Regulation
- **PECR** - Privacy and Electronic Communications Regulations
- **PIDA 1998** - Public Interest Disclosure Act 1998
- **ERA 1996/1999** - Employment Rights Act / Employment Relations Act
- **ACAS Code** - Advisory, Conciliation and Arbitration Service Code of Practice

## When to Use This Skill

Activate this skill when:
- Working with LOKI validation logic
- Adding or modifying compliance gates
- Debugging validation failures
- Understanding regulatory requirements
- Reviewing gate implementation
- Answering compliance questions
- Explaining validation results
