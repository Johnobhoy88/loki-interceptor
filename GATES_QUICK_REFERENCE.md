# UK Compliance Gates - Quick Reference Card

## 10 NEW Compliance Gates - 2025 Regulations

### UK Employment Law (5 Gates)
Located in: `backend/modules/uk_employment/gates/`

| Gate | File | Key Detections | Critical Issues |
|------|------|----------------|-----------------|
| **Employment Contracts** | employment_contracts.py | Zero-hours exclusivity, fixed-term 4-year rule, probation limits, garden leave | Illegal exclusivity in zero-hours, excessive probation (>6 months) |
| **Redundancy Procedures** | redundancy_procedures.py | Collective consultation (20+), fair selection, TUPE transfers | Discriminatory selection criteria, missing consultation |
| **Discrimination Law** | discrimination_law.py | 9 protected characteristics, harassment, reasonable adjustments | Direct discrimination, missing adjustments for disabled |
| **Working Time** | working_time_regulations.py | 48-hour week, rest breaks, 28 days leave, night work | Excessive hours without opt-out, inadequate annual leave |
| **Health & Safety** | health_safety.py | Risk assessments, RIDDOR, PPE, first aid | Missing RIDDOR procedures, inadequate risk assessments |

### GDPR Advanced (3 Gates)
Located in: `backend/modules/gdpr_advanced/gates/`

| Gate | File | Key Detections | Critical Issues |
|------|------|----------------|-----------------|
| **Data Protection Advanced** | data_protection_advanced.py | DSAR (1-3 months), ICO complaints, right to erasure, portability | Missing ICO complaint disclosure, DSAR non-compliance |
| **Automated Decisions** | automated_decisions.py | Article 22, AI transparency, human review, profiling | Solely automated decisions without safeguards, no human review |
| **Children Data** | children_data.py | Age verification (13+), parental consent, privacy by default | No age verification, profiling ON by default |

### FCA Advanced (2 Gates)
Located in: `backend/modules/fca_advanced/gates/`

| Gate | File | Key Detections | Critical Issues |
|------|------|----------------|-----------------|
| **Financial Services** | financial_services.py | Consumer Duty, client money (CASS 7), complaints (FOS), vulnerable customers | Client money not segregated, no FOS reference |
| **Operational Resilience** | operational_resilience.py | IBS, impact tolerances, March 2025 deadline, testing | Missing impact tolerances (March 2025 critical) |

---

## Usage Examples

### Example 1: Check Employment Contract
```python
from backend.modules.uk_employment.gates import EmploymentContractsGate

gate = EmploymentContractsGate()
result = gate.check(contract_text, "employment_contract")

if result['status'] == 'FAIL':
    print(f"CRITICAL: {result['message']}")
    print(f"Fix: {result['suggestion']}")
```

### Example 2: Check DSAR Response
```python
from backend.modules.gdpr_advanced.gates import DataProtectionAdvancedGate

gate = DataProtectionAdvancedGate()
result = gate.check(privacy_notice, "privacy_notice")

if 'ICO' not in result['message']:
    print("WARNING: Missing ICO complaint procedure")
```

### Example 3: Check Operational Resilience (March 2025)
```python
from backend.modules.fca_advanced.gates import OperationalResilienceGate

gate = OperationalResilienceGate()
result = gate.check(resilience_doc, "resilience_framework")

if result['status'] == 'FAIL' and 'impact tolerance' in result['message']:
    print("URGENT: March 31, 2025 deadline - Set impact tolerances for IBS")
```

---

## Return Format

All gates return:
```python
{
    'status': 'PASS' | 'WARNING' | 'FAIL' | 'N/A',
    'severity': 'critical' | 'high' | 'medium' | 'low' | 'none',
    'message': 'Human-readable summary',
    'legal_source': 'Legislation reference',
    'suggestion': 'How to fix the issue',
    'spans': [
        {
            'type': 'issue_type',
            'start': 123,
            'end': 456,
            'text': 'problematic text',
            'severity': 'critical'
        }
    ],
    'details': ['Detailed issue 1', 'Detailed issue 2', ...]
}
```

---

## Top 10 Critical Detections

1. **Zero-Hours Exclusivity** (employment_contracts) - BANNED in 2025
2. **Missing ICO Complaint Right** (data_protection_advanced) - MANDATORY disclosure
3. **Impact Tolerances Missing** (operational_resilience) - March 31, 2025 DEADLINE
4. **Client Money Not Segregated** (financial_services) - CASS 7 violation
5. **Direct Discrimination** (discrimination_law) - Protected characteristics violation
6. **Solely Automated Decisions** (automated_decisions) - Article 22 prohibition
7. **Children Profiling ON by Default** (children_data) - 2025 enhanced protection
8. **Annual Leave < 28 Days** (working_time_regulations) - Statutory minimum
9. **Discriminatory Redundancy Selection** (redundancy_procedures) - Equality Act breach
10. **RIDDOR Non-Compliance** (health_safety) - HSE reporting requirement

---

## Severity Levels

- **CRITICAL:** Legal violation, immediate action required, high fines/penalties
- **HIGH:** Serious compliance gap, significant legal risk
- **MEDIUM:** Improvement needed, moderate risk
- **LOW:** Best practice recommendation, low risk

---

## 2025 Deadline Tracker

| Regulation | Deadline | Gate | Status |
|-----------|----------|------|--------|
| FCA Operational Resilience | March 31, 2025 | operational_resilience | URGENT |
| Employment Rights Bill | 2025 Q1-Q2 | employment_contracts | ACTIVE |
| Data Use and Access Act | 2025 | data_protection_advanced | ACTIVE |
| Consumer Duty (ongoing) | Continuous | financial_services | ACTIVE |

---

## Test Coverage

All gates include comprehensive test cases:
- Zero-hours contracts (compliant/non-compliant)
- DSAR procedures (with/without ICO)
- Operational resilience (with/without impact tolerances)
- Children data (privacy by default checks)
- And 37+ more scenarios

Run tests:
```bash
python -m pytest backend/modules/uk_employment/gates/employment_contracts.py
python -m pytest backend/modules/gdpr_advanced/gates/automated_decisions.py
python -m pytest backend/modules/fca_advanced/gates/operational_resilience.py
```

---

## Integration Checklist

- [ ] Import all 10 gates
- [ ] Initialize gate instances
- [ ] Run checks on relevant documents
- [ ] Handle FAIL status (block/warn user)
- [ ] Display suggestions for fixes
- [ ] Log compliance issues for audit
- [ ] Update patterns based on regulatory changes
- [ ] Schedule March 2025 operational resilience review

---

## Support & Maintenance

**Pattern Updates:** Monitor FCA Policy Statements, ICO guidance, Employment Rights Bill progress
**Testing:** Add new test cases as regulations clarified
**Performance:** Optimize regex patterns for speed
**Coverage:** Track false positives/negatives

---

**Quick Start:** Import gates → Initialize → Run checks → Handle results
**Documentation:** See COMPLIANCE_GATES_2025_SUMMARY.md for full details
**Version:** 1.0 (November 2025)
