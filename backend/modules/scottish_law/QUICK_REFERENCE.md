# Scottish Law Gates - Quick Reference

## Gate Summary

| Gate | File | Severity | Key Detections |
|------|------|----------|----------------|
| **Employment** | `scottish_employment.py` | High | 5-year prescription, ET Scotland, ACAS Scotland |
| **Contracts** | `scottish_contracts.py` | Critical | Consideration, consensus in idem, jus quaesitum tertio |
| **Data Protection** | `scottish_data_protection.py` | High | Scottish IC, FOI Scotland, Public Records Act |
| **Property** | `scottish_property.py` | High | Heritable property, PRT, Registers of Scotland |
| **Corporate** | `scottish_corporate.py` | Medium | OSCR, SC numbers, SLPs, SCIOs |

---

## Top Detection Patterns

### Employment Gate
```
✗ "six years" or "6 years" (limitation period)
✓ "five years" or "5 years" (prescription period)

✗ "Employment Tribunal" (without Scotland)
✓ "Employment Tribunal Scotland"

✗ "ACAS" (without Scotland specification)
✓ "ACAS Scotland"

✗ "limitation period"
✓ "prescription period"
```

### Contracts Gate
```
✗ "In consideration of £1..."
✓ No consideration clause needed

✗ "subject to contract" (may not protect)
✓ Warn that consensus in idem may override

✗ "Contracts (Rights of Third Parties) Act 1999"
✓ "Contract (Third Party Rights) (Scotland) Act 2017" or "jus quaesitum tertio"

✗ "offer and acceptance" (only)
✓ "consensus in idem" or "meeting of minds"

✗ "executed as a deed"
✓ No deed requirement in Scots law
```

### Data Protection Gate
```
✗ "Freedom of Information Act 2000"
✓ "Freedom of Information (Scotland) Act 2002"

✗ "Information Commissioner" or "ICO" (for FOI)
✓ "Scottish Information Commissioner" (for FOI)

✗ Missing "Records Management Plan"
✓ Reference RMP requirement for Scottish public authorities

✗ "Environmental Information Regulations"
✓ "Environmental Information (Scotland) Regulations 2004"
```

### Property Gate
```
✗ "freehold"
✓ "heritable property" or "ownership"

✗ "leasehold"
✓ "lease" or specific property interest

✗ "Land Registry" or "HM Land Registry"
✓ "Registers of Scotland" or "RoS"

✗ "Assured Shorthold Tenancy" or "AST"
✓ "Private Residential Tenancy" or "PRT"

✗ "Section 21"
✓ 18 statutory grounds (PRT Act)

✗ "exchange of contracts"
✓ "conclusion of missives"

✗ Missing "Home Report"
✓ Home Report required for residential sales
```

### Corporate Gate
```
✗ "Charity Commission" (in Scottish context)
✓ "OSCR" (Office of Scottish Charity Regulator)

✗ "Charity Number: 123456"
✓ "Scottish Charity Number: SC012345"

✗ Missing SCIO reference
✓ Mention SCIO as Scottish charitable option

✗ "Limited Partnership" (without SLP context)
✓ Note Scottish Limited Partnership rules

✗ "partnership" (without legal personality note)
✓ Note Scottish partnerships have separate legal personality
```

---

## Quick Test Commands

```python
# Import gates
from scottish_law.gates import *

# Test employment
gate = ScottishEmploymentGate()
result = gate.check("Employment contract in Scotland with six year limitation", "contract")
print(result['status'])  # Should be FAIL

# Test contracts
gate = ScottishContractsGate()
result = gate.check("Governed by Scots law. In consideration of £1...", "contract")
print(result['status'])  # Should be FAIL

# Test data protection
gate = ScottishDataProtectionGate()
result = gate.check("Scottish council complies with FOI Act 2000", "policy")
print(result['status'])  # Should be FAIL

# Test property
gate = ScottishPropertyGate()
result = gate.check("Freehold property registered with Land Registry", "lease")
print(result['status'])  # Should be FAIL

# Test corporate
gate = ScottishCorporateGate()
result = gate.check("Scottish charity registered with Charity Commission", "articles")
print(result['status'])  # Should be FAIL
```

---

## Common Scots Law Terms

| English Law | Scots Law | Context |
|-------------|-----------|---------|
| Limitation | Prescription | Time limits for claims |
| 6 years | 5 years | Contractual claims period |
| Consideration | Not required | Contract formation |
| Offer and acceptance | Consensus in idem | Contract formation principle |
| Third Party Rights Act 1999 | Jus quaesitum tertio / 2017 Act | Third-party enforcement |
| Freehold | Heritable property | Property ownership |
| Leasehold | Lease | Property tenure |
| Land Registry | Registers of Scotland | Land registration |
| AST | PRT | Residential tenancies |
| Section 21 | 18 statutory grounds | Eviction procedures |
| Exchange of contracts | Conclusion of missives | Conveyancing |
| Charity Commission | OSCR | Charity regulation |
| Charity Number | SC Number | Charity registration |
| FOI Act 2000 | FOI (Scotland) Act 2002 | Freedom of Information |
| EIR 2004 | EIR (Scotland) 2004 | Environmental information |

---

## Status Codes

| Status | Meaning | Action Required |
|--------|---------|-----------------|
| **FAIL** | Critical/High issues detected | Must fix before use |
| **WARNING** | Suggestions/improvements | Review and consider |
| **PASS** | No issues detected | Compliant |
| **N/A** | Gate not applicable | No action |

---

## Key Legislation Reference

### Employment
- Prescription and Limitation (Scotland) Act 1973
- Employment Tribunals (Scotland) Regulations 2013
- Employment Rights Act 1996 (UK-wide)

### Contracts
- Contract (Scotland) Act 1997
- Contract (Third Party Rights) (Scotland) Act 2017
- Partnership Act 1890

### Data Protection
- Freedom of Information (Scotland) Act 2002
- Public Records (Scotland) Act 2011
- Environmental Information (Scotland) Regulations 2004
- UK GDPR & Data Protection Act 2018 (UK-wide)

### Property
- Land Registration etc. (Scotland) Act 2012
- Private Housing (Tenancies) (Scotland) Act 2016
- Housing (Scotland) Act 2006
- Tenancy Deposit Schemes (Scotland) Regulations 2011

### Corporate
- Charities and Trustee Investment (Scotland) Act 2005
- Companies Act 2006 (UK-wide)
- Limited Partnerships Act 1907
- Insolvency Act 1986 (as applied to Scotland)

---

## Regex Cheat Sheet

```python
# Scottish jurisdiction
r'\bscot(?:land|tish|s law)\b'

# Prescription period
r'(?:six|6)[\s-]year(?:s)?'

# ACAS without Scotland
r'\bACAS\b(?!\s+scotland)'

# Consideration
r'in\s+consideration\s+of'

# Subject to contract
r'subject\s+to\s+contract'

# Third Party Rights
r'contracts.*rights.*third.*1999'

# Freehold
r'\bfreehold\b'

# Land Registry
r'Land\s+Registry|HMLR'

# AST
r'Assured\s+Shorthold\s+Tenancy|AST'

# Section 21
r'Section\s+21'

# FOI Act 2000
r'Freedom\s+of\s+Information\s+Act\s+2000'

# Charity Commission
r'Charity\s+Commission'

# Scottish charity number
r'SC\d{6}'
```

---

## Integration Example

```python
from scottish_law.gates import (
    ScottishEmploymentGate,
    ScottishContractsGate,
    ScottishDataProtectionGate,
    ScottishPropertyGate,
    ScottishCorporateGate
)

# Initialize all gates
gates = {
    'employment': ScottishEmploymentGate(),
    'contracts': ScottishContractsGate(),
    'data_protection': ScottishDataProtectionGate(),
    'property': ScottishPropertyGate(),
    'corporate': ScottishCorporateGate()
}

# Check document with all gates
def check_scottish_compliance(document_text, doc_type='contract'):
    results = {}
    for name, gate in gates.items():
        result = gate.check(document_text, doc_type)
        if result['status'] in ['FAIL', 'WARNING']:
            results[name] = result
    return results

# Example usage
document = """
This employment contract is governed by Scots law.
Claims must be brought within six years.
Property is freehold and registered with Land Registry.
"""

issues = check_scottish_compliance(document)
for gate_name, result in issues.items():
    print(f"\n{gate_name.upper()}: {result['status']}")
    if 'issues' in result:
        for issue in result['issues']:
            print(f"  - {issue}")
```

---

## File Structure

```
backend/modules/scottish_law/
├── __init__.py                    # Module initialization
├── gates/
│   ├── __init__.py               # Gates package init
│   ├── scottish_employment.py    # Employment gate
│   ├── scottish_contracts.py     # Contracts gate
│   ├── scottish_data_protection.py # Data protection gate
│   ├── scottish_property.py      # Property gate
│   └── scottish_corporate.py     # Corporate gate
├── test_scottish_gates.py        # Comprehensive tests
├── SCOTTISH_LAW_GATES.md         # Full documentation
└── QUICK_REFERENCE.md            # This file
```

---

## Version Info

**Version:** 1.0.0
**Gates:** 5 (Employment, Contracts, Data Protection, Property, Corporate)
**Total Patterns:** 60+ detection patterns
**Test Cases:** 25+ comprehensive tests
**Jurisdiction:** Scotland (UK)
