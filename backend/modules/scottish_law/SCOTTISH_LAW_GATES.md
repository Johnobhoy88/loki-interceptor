# Scottish Law Compliance Gates

## Overview

This module implements 5 comprehensive compliance gates for detecting and correcting Scots law differences from English law. The gates cover employment, contracts, data protection, property, and corporate law.

## Key Scots Law Differences

### 1. Contract Formation
- **Consensus in idem** (meeting of minds) rather than strict offer and acceptance
- **No consideration requirement** - contracts valid without consideration
- **Earlier contract formation** - binding agreements can form before signature
- **"Subject to contract" less protective** - may not prevent binding contract

### 2. Third-Party Rights
- **Jus quaesitum tertio** - common law doctrine allowing third parties to enforce rights
- **Contract (Third Party Rights) (Scotland) Act 2017** (not English 1999 Act)

### 3. Prescription Periods
- **5-year prescription period** for contractual claims (not 6-year English limitation)
- Uses "prescription" terminology (not "limitation")

### 4. Property Law
- **Heritable property** (not freehold)
- **No freehold/leasehold distinction** as in English law
- **Registers of Scotland** (not Land Registry)
- **Conclusion of missives** (not exchange of contracts)
- **Private Residential Tenancies** (not Assured Shorthold Tenancies)

### 5. Public Bodies
- **Scottish Information Commissioner** for FOI matters (separate from UK ICO)
- **OSCR** (Office of Scottish Charity Regulator) not Charity Commission
- **FOI (Scotland) Act 2002** (not UK FOIA 2000)

---

## Gate 1: Scottish Employment Gate

**File:** `scottish_employment.py`

### Purpose
Detects employment law differences specific to Scotland including tribunals, prescription periods, and ACAS Scotland.

### Key Detection Patterns

#### 1. Prescription Period (5 years not 6)
```python
Pattern: r'(?:six|6)[\s-]year(?:s)?(?:\s+(?:period|limitation|time\s+limit))'
Issue: Six-year limitation period stated (incorrect for Scotland)
Correction: Replace with 5-year prescription period
Citation: Prescription and Limitation (Scotland) Act 1973, s.6
```

#### 2. Employment Tribunal References
```python
Pattern: r'employment\s+tribunal(?!\s+(?:scotland|for\s+scotland))'
Issue: Generic Employment Tribunal without Scotland specification
Correction: Use "Employment Tribunal Scotland"
Citation: Employment Tribunals (Scotland) Regulations 2013
```

#### 3. ACAS Scotland
```python
Pattern: r'\bACAS\b(?!\s+scotland)'
Issue: ACAS referenced without Scotland specification
Correction: Reference "ACAS Scotland" for Scottish matters
Citation: ACAS Scotland (separate from ACAS England & Wales)
```

#### 4. Terminology
```python
Pattern: r'\blimitation\s+(?:period|act)\b'
Issue: English "limitation" terminology used
Correction: Use "prescription" not "limitation" in Scots law
Citation: Prescription and Limitation (Scotland) Act 1973
```

### Test Cases
```python
# FAIL - Six-year period
"This employment contract is governed by Scots law. Claims within six years."

# FAIL - Generic tribunal reference
"This Scottish employment contract may be subject to Employment Tribunal."

# PASS - Correct Scottish references
"Employment Tribunal Scotland handles claims. ACAS Scotland provides guidance. 5-year prescription period."
```

---

## Gate 2: Scottish Contracts Gate

**File:** `scottish_contracts.py`

### Purpose
Detects contract law differences including consideration, consensus in idem, and third-party rights.

### Key Detection Patterns

#### 1. Consideration Clauses
```python
Pattern: r'in\s+consideration\s+of|good\s+and\s+valuable\s+consideration'
Issue: English law consideration language used
Correction: Consideration not required in Scots law
Citation: Scots contract law - no consideration requirement
```

#### 2. Subject to Contract
```python
Pattern: r'subject\s+to\s+(?:contract|formal\s+contract)'
Issue: "Subject to contract" may not prevent binding contract
Correction: Warn that consensus in idem may create binding contract despite this language
Citation: Stobo Ltd v Morrisons (Gowns) Ltd [1949]; Grant v Stoneham [2011]
```

#### 3. Third-Party Rights
```python
Pattern: r'contracts.*rights.*third\s+parties.*act\s+1999'
Issue: English Contracts (Rights of Third Parties) Act 1999 referenced
Correction: Reference Contract (Third Party Rights) (Scotland) Act 2017 or jus quaesitum tertio
Citation: Contract (Third Party Rights) (Scotland) Act 2017
```

#### 4. Consensus in Idem
```python
Pattern: r'offer\s+and\s+acceptance' (without consensus in idem reference)
Issue: Strict offer and acceptance without Scots law principle
Correction: Reference "consensus in idem" (meeting of minds)
Citation: Scots contract law - consensus in idem principle
```

#### 5. Deed Execution
```python
Pattern: r'executed\s+as\s+a\s+deed|signed.*sealed.*delivered'
Issue: English deed execution language used
Correction: Scots law doesn't have same deed concept
Citation: Scots contract law - no deed requirement
```

### Test Cases
```python
# FAIL - Consideration clause
"This Agreement is governed by Scots law. In consideration of £1..."

# FAIL - Subject to contract
"This agreement is subject to contract and governed by law of Scotland."

# FAIL - English Third Party Rights Act
"Governed by Scots law. Third parties may enforce under 1999 Act."

# PASS - Proper Scottish contract
"Governed by Scots law. Parties reached consensus in idem. Jus quaesitum tertio applies."
```

---

## Gate 3: Scottish Data Protection Gate

**File:** `scottish_data_protection.py`

### Purpose
Detects data protection and FOI differences for Scottish public authorities.

### Key Detection Patterns

#### 1. FOI Legislation
```python
Pattern: r'Freedom\s+of\s+Information\s+Act\s+2000'
Issue: UK FOIA 2000 referenced instead of Scottish Act
Correction: Use Freedom of Information (Scotland) Act 2002
Citation: Freedom of Information (Scotland) Act 2002
```

#### 2. Information Commissioner
```python
Pattern: r'\bICO\b|Information\s+Commissioner' (in public authority context)
Issue: Generic ICO reference for FOI matters
Correction: Reference Scottish Information Commissioner (SIC) for FOI
Citation: FOI (Scotland) Act 2002 - enforced by SIC
```

#### 3. Environmental Information
```python
Pattern: r'Environmental\s+Information\s+Regulations' (without Scotland)
Issue: Generic EIR without Scotland specification
Correction: Reference Environmental Information (Scotland) Regulations 2004
Citation: EIR (Scotland) 2004 (SSI 2004/520)
```

#### 4. Records Management
```python
Pattern: Scottish public authority without records management plan reference
Issue: Missing records management plan requirement
Correction: Mention requirement for RMP approved by Keeper
Citation: Public Records (Scotland) Act 2011, s.1
```

#### 5. Dual Commissioner Jurisdiction
```python
Context: Scottish public authority with both data protection and FOI
Issue: Unclear which commissioner handles what
Correction: Clarify UK ICO for data protection; SIC for FOI Scotland
Citation: Dual regulatory framework in Scotland
```

### Test Cases
```python
# FAIL - UK FOI Act
"Scottish council complies with Freedom of Information Act 2000."

# PASS - Correct Scottish references
"Scottish authorities comply with FOI (Scotland) Act 2002 and Scottish Information Commissioner."

# WARNING - Missing records management plan
"Scottish Government agency is a Scottish public authority under UK GDPR."
```

---

## Gate 4: Scottish Property Gate

**File:** `scottish_property.py`

### Purpose
Detects property law differences including terminology, tenancies, and conveyancing.

### Key Detection Patterns

#### 1. Freehold/Leasehold Terminology
```python
Pattern: r'\bfreehold\b'
Issue: English freehold terminology used
Correction: Use "heritable property" or "ownership"
Citation: Scots property law - no freehold/leasehold distinction

Pattern: r'\bleasehold\b'
Issue: English leasehold terminology used
Correction: Use "lease" or describe specific property interest
Citation: Scots property law - different lease concepts
```

#### 2. Land Registry
```python
Pattern: r'Land\s+Registry|HM\s+Land\s+Registry|HMLR'
Issue: English Land Registry referenced
Correction: Use "Registers of Scotland" or "RoS"
Citation: Land Registration etc. (Scotland) Act 2012
```

#### 3. Tenancy Types
```python
Pattern: r'Assured\s+Shorthold\s+Tenancy|AST'
Issue: English AST referenced in Scottish context
Correction: Use "Private Residential Tenancy" (PRT)
Citation: Private Housing (Tenancies) (Scotland) Act 2016
```

#### 4. Eviction Procedures
```python
Pattern: r'Section\s+21' (in eviction context)
Issue: Section 21 "no-fault" eviction referenced
Correction: Scotland doesn't have Section 21; use 18 statutory grounds
Citation: Private Housing (Tenancies) (Scotland) Act 2016
```

#### 5. Conveyancing Process
```python
Pattern: r'exchange\s+of\s+contracts'
Issue: English exchange of contracts terminology
Correction: Use "conclusion of missives"
Citation: Scots conveyancing law - missives conclude the bargain
```

#### 6. Home Reports
```python
Context: Residential property sale without Home Report mention
Issue: Missing Home Report requirement
Correction: Sellers must provide Home Report before marketing
Citation: Housing (Scotland) Act 2006, Part 3
```

#### 7. Deposit Protection
```python
Context: Deposit mentioned without Scottish scheme
Issue: Missing Scottish deposit scheme reference
Correction: Must use approved Scottish schemes (SafeDeposits Scotland, etc.)
Citation: Tenancy Deposit Schemes (Scotland) Regulations 2011
```

### Test Cases
```python
# FAIL - Freehold and Land Registry
"This freehold property in Scotland is registered with Land Registry."

# FAIL - AST
"This Assured Shorthold Tenancy is for property in Edinburgh, Scotland."

# FAIL - Section 21
"Scottish landlord issued Section 21 notice."

# FAIL - Exchange of contracts
"Upon exchange of contracts, sale of Scottish property complete."

# PASS - Correct terminology
"Heritable property registered with Registers of Scotland. Private Residential Tenancy."
```

---

## Gate 5: Scottish Corporate Gate

**File:** `scottish_corporate.py`

### Purpose
Detects corporate law differences including charity regulation, company structures, and partnerships.

### Key Detection Patterns

#### 1. Charity Regulation
```python
Pattern: r'Charity\s+Commission' (in Scottish charity context)
Issue: English Charity Commission referenced
Correction: Use "OSCR (Office of the Scottish Charity Regulator)"
Citation: Charities and Trustee Investment (Scotland) Act 2005
```

#### 2. Charity Numbers
```python
Pattern: r'Charity\s+(?:Number|No\.?)\s*:?\s*(\d+)' (without SC prefix)
Issue: English charity number format
Correction: Scottish charity numbers have "SC" prefix (e.g., SC012345)
Citation: OSCR - Scottish Charity Numbers begin with "SC"
```

#### 3. SCIO (Scottish Charitable Incorporated Organisation)
```python
Pattern: r'\bSCIO\b|Scottish\s+Charitable\s+Incorporated\s+Organisation'
Detection: SCIO mentioned
Correction: Note SCIOs are Scottish-only, registered only with OSCR
Citation: Charities and Trustee Investment (Scotland) Act 2005, Part 7
```

#### 4. Scottish Limited Partnerships
```python
Pattern: r'Limited\s+Partnership' (in Scottish context)
Issue: SLP referenced
Correction: Note SLPs have distinct rules and transparency requirements
Citation: Limited Partnerships Act 1907; Scottish Partnerships Regulations 2017
```

#### 5. Partnership Legal Personality
```python
Pattern: r'partnership(?!.*limited)' (in Scottish context)
Issue: Scottish partnership referenced
Correction: Note Scottish partnerships have separate legal personality (unlike English)
Citation: Partnership Act 1890, s.4(2)
```

#### 6. Insolvency Procedures
```python
Pattern: r'insolvenc(?:y|ies)|liquidation|administration' (without Scots reference)
Issue: Insolvency mentioned without Scottish procedures
Correction: Note Scottish insolvency procedures (e.g., sequestration)
Citation: Insolvency Act 1986 (Scotland); Bankruptcy (Scotland) Act 2016
```

### Test Cases
```python
# FAIL - Charity Commission
"Scottish charity registered with Charity Commission. Number: 123456."

# PASS - Correct OSCR reference
"Scottish charity registered with OSCR. Scottish Charity Number: SC012345."

# WARNING - SLP
"Scottish Limited Partnership operates in Scotland under Scots law."

# PASS - SCIO
"This SCIO is registered with OSCR in Scotland."
```

---

## Integration Usage

### Basic Usage
```python
from scottish_law.gates import (
    ScottishEmploymentGate,
    ScottishContractsGate,
    ScottishDataProtectionGate,
    ScottishPropertyGate,
    ScottishCorporateGate
)

# Initialize gates
employment_gate = ScottishEmploymentGate()
contracts_gate = ScottishContractsGate()
data_protection_gate = ScottishDataProtectionGate()
property_gate = ScottishPropertyGate()
corporate_gate = ScottishCorporateGate()

# Check document
document_text = "Your Scottish legal document here..."
result = employment_gate.check(document_text, 'employment_contract')

# Process result
if result['status'] == 'FAIL':
    print(f"Issues: {result['issues']}")
    print(f"Corrections: {result['corrections']}")
elif result['status'] == 'WARNING':
    print(f"Suggestions: {result['corrections']}")
else:  # PASS or N/A
    print(f"Status: {result['status']}")
```

### Result Structure
```python
{
    'status': 'FAIL' | 'WARNING' | 'PASS' | 'N/A',
    'severity': 'critical' | 'high' | 'medium' | 'low' | 'none',
    'message': 'Human-readable status message',
    'legal_source': 'Relevant legislation/case law',
    'issues': ['List of detected issues'],  # Only for FAIL
    'corrections': [                          # For FAIL or WARNING
        {
            'type': 'correction_type',
            'suggestion': 'What to do',
            'correction': 'Specific text correction (optional)',
            'citation': 'Legal authority'
        }
    ]
}
```

---

## Running Tests

### Run All Tests
```bash
cd backend/modules
python scottish_law/test_scottish_gates.py
```

### Run Individual Gate Tests
```python
from scottish_law.gates.scottish_employment import ScottishEmploymentGate, TEST_CASES

gate = ScottishEmploymentGate()
for test in TEST_CASES:
    result = gate.check(test['text'], 'contract')
    print(f"{test['name']}: {result['status']}")
```

---

## Regex Pattern Reference

### Common Scottish Law Indicators
```python
# Scottish jurisdiction detection
r'\bscot(?:land|tish|s law)\b'
r'governed\s+by.*\bscot(?:s|tish|land)\b'

# Employment patterns
r'employment\s+tribunal(?!\s+scotland)'
r'\bACAS\b(?!\s+scotland)'
r'(?:six|6)[\s-]year(?:s)?.*(?:period|limitation)'

# Contract patterns
r'in\s+consideration\s+of'
r'subject\s+to\s+contract'
r'consensus\s+in\s+idem'
r'jus\s+quaesitum\s+tertio'

# Property patterns
r'\bfreehold\b'
r'Land\s+Registry'
r'Assured\s+Shorthold\s+Tenancy'
r'Section\s+21'
r'exchange\s+of\s+contracts'
r'conclusion\s+of\s+missives'

# Data protection patterns
r'Freedom\s+of\s+Information\s+Act\s+2000'
r'Scottish\s+Information\s+Commissioner'
r'Public\s+Records\s+\(Scotland\)\s+Act'

# Corporate patterns
r'Charity\s+Commission'
r'\bOSCR\b'
r'SC\d{6}'  # Scottish charity number format
r'Scottish\s+Limited\s+Partnership'
```

---

## Citation Authority

### Legislation
- Prescription and Limitation (Scotland) Act 1973
- Contract (Scotland) Act 1997
- Contract (Third Party Rights) (Scotland) Act 2017
- Freedom of Information (Scotland) Act 2002
- Public Records (Scotland) Act 2011
- Land Registration etc. (Scotland) Act 2012
- Private Housing (Tenancies) (Scotland) Act 2016
- Charities and Trustee Investment (Scotland) Act 2005
- Companies Act 2006 (UK-wide)
- Partnership Act 1890

### Regulatory Bodies
- Employment Tribunal Scotland
- ACAS Scotland
- Scottish Information Commissioner (SIC)
- Office of the Scottish Charity Regulator (OSCR)
- Registers of Scotland (RoS)
- National Records of Scotland (NRS)
- First-tier Tribunal for Scotland (Housing and Property Chamber)

### Case Law
- Stobo Ltd v Morrisons (Gowns) Ltd [1949] - subject to contract
- Grant v Stoneham [2011] - contract formation in Scotland
- West Midlands Co-operative Society Ltd v Tipton [1986] - constructive dismissal

---

## Maintenance Notes

### Adding New Patterns
1. Add regex pattern to relevant gate
2. Define issue message and correction
3. Add legal citation
4. Create test case
5. Update documentation

### Pattern Priority
Gates process patterns in order and may return multiple issues. Organize patterns from most specific to most general.

### False Positive Mitigation
Use negative lookahead/lookbehind to exclude valid Scottish references:
```python
# Match Employment Tribunal but not "Employment Tribunal Scotland"
r'employment\s+tribunal(?!\s+(?:scotland|for\s+scotland))'
```

---

## Future Enhancements

### Potential Additions
1. **Scottish Criminal Law Gate** - prosecution procedures, Scottish courts
2. **Scottish Family Law Gate** - divorce, children's hearings
3. **Scottish Planning Law Gate** - planning permissions, listed buildings
4. **Scottish Intellectual Property Gate** - Scottish Patent Office considerations
5. **Scottish Tax Gate** (expand existing) - LBTT, Scottish income tax bands

### Integration Opportunities
- Document correction system integration
- Real-time document checking
- Cross-referencing with other UK modules
- Legislative update monitoring

---

## Support and Contact

For issues, suggestions, or contributions related to Scottish law gates:
- Review test cases in `test_scottish_gates.py`
- Check individual gate files for detailed pattern definitions
- Refer to legal citations for authoritative sources

**Version:** 1.0.0
**Last Updated:** 2025
**Jurisdiction:** Scotland (UK)
