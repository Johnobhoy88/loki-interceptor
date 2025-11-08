# Scottish Law Gates - Detection Patterns Summary

## Overview
This document provides a comprehensive summary of all detection patterns across the 5 Scottish law compliance gates.

---

## Gate 1: Scottish Employment (scottish_employment.py)

### Pattern 1: Six-Year Limitation Period (FAIL)
```regex
Pattern: (?:six|6)[\s-]year(?:s)?(?:\s+(?:period|limitation|time\s+limit))
Context: Contract-related text
Issue: Six-year limitation period stated (incorrect for Scotland)
Correction: Replace with "five years" or "5 years"
Citation: Prescription and Limitation (Scotland) Act 1973, s.6
Severity: High

Example FAIL: "Claims must be brought within six years."
Example PASS: "Claims have a 5-year prescription period."
```

### Pattern 2: Employment Tribunal without Scotland (FAIL)
```regex
Pattern: employment\s+tribunal(?!\s+(?:scotland|for\s+scotland))
Issue: Employment Tribunal referenced without Scotland specification
Correction: Use "Employment Tribunal Scotland" or "Employment Tribunal (Scotland)"
Citation: Employment Tribunals (Scotland) Regulations 2013
Severity: High

Example FAIL: "Disputes may be referred to the Employment Tribunal."
Example PASS: "Disputes handled by Employment Tribunal Scotland."
```

### Pattern 3: ACAS without Scotland (FAIL)
```regex
Pattern: \bACAS\b(?!\s+scotland)
Issue: ACAS referenced without Scotland specification
Correction: Reference "ACAS Scotland" for Scottish employment matters
Citation: ACAS Scotland (separate organization)
Severity: High

Example FAIL: "Contact ACAS for early conciliation."
Example PASS: "Contact ACAS Scotland for early conciliation."
```

### Pattern 4: Limitation Terminology (FAIL)
```regex
Pattern: \blimitation\s+(?:period|act)\b
Issue: English "limitation" terminology instead of Scots "prescription"
Correction: Replace "limitation period" with "prescription period"
Citation: Prescription and Limitation (Scotland) Act 1973
Severity: Medium

Example FAIL: "Subject to limitation period."
Example PASS: "Subject to prescription period."
```

### Pattern 5: Offer and Acceptance (WARNING)
```regex
Pattern: offer\s+and\s+acceptance (without consensus in idem)
Issue: English contract formation terminology
Correction: Reference "consensus in idem" (meeting of minds)
Citation: Scots contract law
Severity: Medium

Example WARNING: "Contract formed by offer and acceptance."
Example PASS: "Contract formed by consensus in idem."
```

**Total Patterns: 9 detection patterns**

---

## Gate 2: Scottish Contracts (scottish_contracts.py)

### Pattern 1: Consideration Clauses (FAIL)
```regex
Patterns:
  - in\s+consideration\s+of
  - good\s+and\s+valuable\s+consideration
  - for\s+and\s+in\s+consideration
  - receipt.*consideration.*acknowledged

Issue: English law consideration language used in Scottish contract
Correction: Remove consideration clauses (not required in Scots law)
Citation: Scots contract law - no consideration requirement
Severity: Critical

Example FAIL: "In consideration of £1 and other valuable consideration..."
Example PASS: "The parties agree..." (no consideration clause)
```

### Pattern 2: Subject to Contract (FAIL)
```regex
Pattern: subject\s+to\s+(?:contract|formal\s+contract)
Issue: "Subject to contract" may not prevent binding contract formation
Correction: Warn that consensus in idem may override this language
Citation: Stobo Ltd v Morrisons (Gowns) Ltd [1949]; Grant v Stoneham [2011]
Severity: Critical

Example FAIL: "This agreement is subject to contract."
Example PASS: "Subject to contract (noting consensus in idem may apply)."
```

### Pattern 3: English Third Party Rights Act (FAIL)
```regex
Pattern: contracts.*rights.*third\s+parties.*act\s+1999
Issue: English Contracts (Rights of Third Parties) Act 1999 does not apply
Correction: Reference Contract (Third Party Rights) (Scotland) Act 2017
Citation: Contract (Third Party Rights) (Scotland) Act 2017
Severity: Critical

Example FAIL: "Third parties may enforce under 1999 Act."
Example PASS: "Third parties: Contract (Third Party Rights) (Scotland) Act 2017."
```

### Pattern 4: Jus Quaesitum Tertio (WARNING)
```regex
Pattern: third[\s-]part(?:y|ies) + enforce|right|benefit
Context: Without jus quaesitum tertio reference
Issue: Third-party rights without Scottish doctrine reference
Correction: Reference jus quaesitum tertio or 2017 Act
Citation: Jus quaesitum tertio doctrine; 2017 Act
Severity: Medium

Example WARNING: "Third parties may enforce rights."
Example PASS: "Third parties: jus quaesitum tertio applies."
```

### Pattern 5: Deed Execution (WARNING)
```regex
Pattern: executed\s+as\s+a\s+deed|signed.*sealed.*delivered
Issue: English deed execution concept not applicable in Scotland
Correction: Note deed execution is English law concept
Citation: Scots contract law - no deed requirement
Severity: Medium

Example WARNING: "This contract executed as a deed."
Example PASS: "This contract binding based on consensus in idem."
```

**Total Patterns: 10 detection patterns**

---

## Gate 3: Scottish Data Protection (scottish_data_protection.py)

### Pattern 1: FOI Act 2000 instead of FOI Scotland (FAIL)
```regex
Pattern: Freedom\s+of\s+Information\s+Act\s+2000
Context: Scottish public authority
Issue: UK FOIA 2000 referenced instead of FOI (Scotland) Act 2002
Correction: Replace with "Freedom of Information (Scotland) Act 2002"
Citation: Freedom of Information (Scotland) Act 2002
Severity: High

Example FAIL: "Complies with Freedom of Information Act 2000."
Example PASS: "Complies with Freedom of Information (Scotland) Act 2002."
```

### Pattern 2: ICO without Scottish IC for FOI (WARNING)
```regex
Pattern: \bICO\b|Information\s+Commissioner
Context: Scottish public authority + FOI context
Issue: Generic ICO reference for FOI matters
Correction: Reference Scottish Information Commissioner for FOI
Citation: FOI (Scotland) Act 2002 - enforced by SIC
Severity: High

Example WARNING: "Report FOI issues to ICO."
Example PASS: "FOI: Scottish Information Commissioner; Data: UK ICO."
```

### Pattern 3: Environmental Information Regulations (WARNING)
```regex
Pattern: Environmental\s+Information\s+Regulations
Context: Without Scotland specification
Issue: Generic EIR without Scotland specification
Correction: Reference Environmental Information (Scotland) Regulations 2004
Citation: EIR (Scotland) 2004 (SSI 2004/520)
Severity: Medium

Example WARNING: "Complies with Environmental Information Regulations."
Example PASS: "Complies with Environmental Information (Scotland) Regulations 2004."
```

### Pattern 4: Records Management Plan (WARNING)
```regex
Pattern: scottish.*public\s+(?:authority|body)
Context: Without records management plan mention
Issue: Missing RMP requirement for Scottish public authorities
Correction: Note requirement for RMP approved by Keeper
Citation: Public Records (Scotland) Act 2011, s.1
Severity: Medium

Example WARNING: "Scottish council processes data under UK GDPR."
Example PASS: "Scottish council has Records Management Plan under PRSA 2011."
```

### Pattern 5: National Records of Scotland (WARNING)
```regex
Pattern: national\s+archives|public\s+records
Context: Without NRS reference
Issue: Missing National Records of Scotland reference
Correction: Reference National Records of Scotland and Keeper
Citation: Public Records (Scotland) Act 2011; NRS
Severity: Low

Example WARNING: "Public records stored in archives."
Example PASS: "Records with National Records of Scotland (NRS)."
```

**Total Patterns: 11 detection patterns**

---

## Gate 4: Scottish Property (scottish_property.py)

### Pattern 1: Freehold Terminology (FAIL)
```regex
Pattern: \bfreehold\b
Issue: English freehold terminology used in Scottish property context
Correction: Replace with "heritable property" or "ownership"
Citation: Scots property law - no freehold/leasehold distinction
Severity: High

Example FAIL: "This freehold property in Scotland..."
Example PASS: "This heritable property in Scotland..."
```

### Pattern 2: Leasehold Terminology (FAIL)
```regex
Pattern: \bleasehold\b
Issue: English leasehold terminology used
Correction: Use "lease" or describe specific property interest
Citation: Scots property law - different lease concepts
Severity: High

Example FAIL: "Leasehold flat in Edinburgh."
Example PASS: "Lease of flat in Edinburgh."
```

### Pattern 3: Land Registry (FAIL)
```regex
Pattern: Land\s+Registry|HM\s+Land\s+Registry|HMLR
Issue: English Land Registry referenced instead of Registers of Scotland
Correction: Replace with "Registers of Scotland" or "RoS"
Citation: Land Registration etc. (Scotland) Act 2012
Severity: High

Example FAIL: "Registered with Land Registry."
Example PASS: "Registered with Registers of Scotland."
```

### Pattern 4: Assured Shorthold Tenancy (FAIL)
```regex
Pattern: Assured\s+Shorthold\s+Tenancy|AST
Issue: English AST referenced in Scottish context
Correction: Replace with "Private Residential Tenancy" (PRT)
Citation: Private Housing (Tenancies) (Scotland) Act 2016
Severity: High

Example FAIL: "This AST is for property in Glasgow."
Example PASS: "This Private Residential Tenancy is in Glasgow."
```

### Pattern 5: Section 21 Eviction (FAIL)
```regex
Pattern: Section\s+21|s\.?\s*21 (in eviction context)
Issue: English Section 21 "no-fault" eviction referenced
Correction: Reference 18 statutory grounds under PRT Act
Citation: Private Housing (Tenancies) (Scotland) Act 2016
Severity: High

Example FAIL: "Landlord issued Section 21 notice."
Example PASS: "Landlord uses statutory ground under PRT Act."
```

### Pattern 6: Exchange of Contracts (FAIL)
```regex
Pattern: exchange\s+of\s+contracts
Issue: English exchange of contracts terminology
Correction: Replace with "conclusion of missives"
Citation: Scots conveyancing law
Severity: High

Example FAIL: "Upon exchange of contracts..."
Example PASS: "Upon conclusion of missives..."
```

### Pattern 7: Home Report (WARNING)
```regex
Pattern: (?:selling|sale\s+of).*(?:property|house|flat)
Context: Without Home Report mention
Issue: Missing Home Report requirement for residential sales
Correction: Note sellers must provide Home Report before marketing
Citation: Housing (Scotland) Act 2006, Part 3
Severity: Medium

Example WARNING: "Selling residential property in Scotland."
Example PASS: "Selling property with Home Report (Housing Act 2006)."
```

### Pattern 8: Deposit Protection (WARNING)
```regex
Pattern: deposit.*(?:protection|scheme)|tenancy\s+deposit
Context: Without Scottish scheme reference
Issue: Missing Scottish deposit scheme reference
Correction: Reference approved Scottish schemes
Citation: Tenancy Deposit Schemes (Scotland) Regulations 2011
Severity: Medium

Example WARNING: "Tenant deposit protected."
Example PASS: "Deposit with SafeDeposits Scotland."
```

### Pattern 9: Right to Buy (WARNING)
```regex
Pattern: Right\s+to\s+Buy
Issue: Right to Buy abolished in Scotland
Correction: Note abolished from 1 August 2016
Citation: Housing (Scotland) Act 2014
Severity: Medium

Example WARNING: "Tenants may have Right to Buy."
Example PASS: "Right to Buy abolished in Scotland (2016)."
```

**Total Patterns: 15 detection patterns**

---

## Gate 5: Scottish Corporate (scottish_corporate.py)

### Pattern 1: Charity Commission (FAIL)
```regex
Pattern: Charity\s+Commission
Context: Scottish charity
Issue: English Charity Commission referenced in Scottish charity context
Correction: Replace with "OSCR (Office of the Scottish Charity Regulator)"
Citation: Charities and Trustee Investment (Scotland) Act 2005
Severity: Medium

Example FAIL: "Registered with Charity Commission."
Example PASS: "Registered with OSCR."
```

### Pattern 2: Charity Number Format (WARNING)
```regex
Pattern: Charity\s+(?:Number|No\.?)\s*:?\s*(\d+)
Context: Without SC prefix
Issue: English charity number format used
Correction: Scottish charities have SC prefix (e.g., SC012345)
Citation: OSCR - Scottish Charity Numbers
Severity: Medium

Example WARNING: "Charity Number: 123456"
Example PASS: "Scottish Charity Number: SC012345"
```

### Pattern 3: SCIO (WARNING)
```regex
Pattern: \bSCIO\b|Scottish\s+Charitable\s+Incorporated\s+Organisation
Issue: SCIO mentioned (Scottish-only structure)
Correction: Note SCIOs registered only with OSCR, not Companies House
Citation: Charities and Trustee Investment (Scotland) Act 2005, Part 7
Severity: Low

Example: "This SCIO is registered with OSCR."
Note: Informational - confirms Scottish-specific structure
```

### Pattern 4: Scottish Limited Partnership (WARNING)
```regex
Pattern: Limited\s+Partnership|L\.?P\.?
Context: Scottish context
Issue: SLP referenced
Correction: Note SLPs have distinct rules and transparency requirements
Citation: Limited Partnerships Act 1907; Scottish Partnerships Regulations 2017
Severity: Low

Example WARNING: "This Limited Partnership operates in Scotland."
Example PASS: "This SLP complies with Scottish transparency requirements."
```

### Pattern 5: Partnership Legal Personality (WARNING)
```regex
Pattern: partnership(?!.*limited)
Context: Scottish context
Issue: Scottish partnership referenced
Correction: Note Scottish partnerships have separate legal personality
Citation: Partnership Act 1890, s.4(2)
Severity: Low

Example WARNING: "Partnership registered in Scotland."
Example PASS: "Partnership (separate legal personality under Scots law)."
```

### Pattern 6: Insolvency Procedures (WARNING)
```regex
Pattern: insolvenc(?:y|ies)|liquidation|administration
Context: Without Scots insolvency reference
Issue: Insolvency mentioned without Scottish procedures
Correction: Note Scottish insolvency procedures (e.g., sequestration)
Citation: Insolvency Act 1986 (Scotland); Bankruptcy (Scotland) Act 2016
Severity: Medium

Example WARNING: "Company faces liquidation."
Example PASS: "Company subject to Scottish insolvency procedures."
```

**Total Patterns: 15 detection patterns**

---

## Pattern Summary by Severity

### Critical (4 patterns)
1. Consideration clauses in Scottish contracts
2. Subject to contract warnings
3. English Third Party Rights Act 1999
4. (All from Contracts Gate)

### High (24 patterns)
1. Six-year limitation period (Employment)
2. Employment Tribunal without Scotland (Employment)
3. ACAS without Scotland (Employment)
4. FOI Act 2000 instead of Scotland (Data Protection)
5. ICO for FOI matters (Data Protection)
6. Freehold terminology (Property)
7. Leasehold terminology (Property)
8. Land Registry (Property)
9. AST references (Property)
10. Section 21 eviction (Property)
11. Exchange of contracts (Property)

### Medium (18 patterns)
- Limitation vs prescription terminology
- Records management plans
- Environmental Information Regulations
- Home Report requirements
- Deposit protection schemes
- Charity Commission references
- Charity number formats
- Insolvency procedures

### Low (14 patterns)
- SCIO informational
- Partnership legal personality
- Various informational warnings

---

## Detection Statistics

| Gate | Total Patterns | FAIL Patterns | WARNING Patterns | Lines of Code |
|------|---------------|---------------|------------------|---------------|
| Employment | 9 | 4 | 5 | ~240 |
| Contracts | 10 | 5 | 5 | ~310 |
| Data Protection | 11 | 2 | 9 | ~280 |
| Property | 15 | 6 | 9 | ~400 |
| Corporate | 15 | 1 | 14 | ~360 |
| **TOTAL** | **60** | **18** | **42** | **~1,590** |

---

## Most Common False Positives and Mitigations

### False Positive 1: Scottish References Already Present
**Issue:** Detecting "Employment Tribunal" even when "Employment Tribunal Scotland" is present
**Mitigation:** Negative lookahead in regex
```regex
r'employment\s+tribunal(?!\s+(?:scotland|for\s+scotland))'
```

### False Positive 2: Mixed Jurisdiction Documents
**Issue:** Document covers both England and Scotland
**Mitigation:** Check for explicit Scotland context before flagging
```python
if not re.search(r'scotland|scottish|scots law', text, re.IGNORECASE):
    return {'status': 'N/A'}
```

### False Positive 3: Historical References
**Issue:** Document discusses historical changes in law
**Mitigation:** Context checking (e.g., "previously", "until 2016")

### False Positive 4: UK-Wide Legislation
**Issue:** Flagging UK-wide laws that do apply in Scotland
**Mitigation:** Only flag Scotland-specific differences, not UK-wide laws

---

## Regex Performance Optimization

### Techniques Used
1. **Negative lookahead** - Exclude valid patterns
2. **Word boundaries** - `\b` for exact word matching
3. **Case-insensitive** - `re.IGNORECASE` flag
4. **Non-capturing groups** - `(?:)` for efficiency
5. **Specific patterns first** - Check specific before general

### Example Optimized Pattern
```python
# Inefficient
r'(.*)employment(.*)tribunal(.*)'

# Optimized
r'employment\s+tribunal(?!\s+(?:scotland|for\s+scotland))'
```

---

## Testing Coverage

### Test Cases by Gate
- **Employment:** 5 comprehensive test cases
- **Contracts:** 5 comprehensive test cases
- **Data Protection:** 5 comprehensive test cases
- **Property:** 6 comprehensive test cases
- **Corporate:** 6 comprehensive test cases

### Test Coverage
- **FAIL scenarios:** ~50% of tests
- **PASS scenarios:** ~30% of tests
- **WARNING scenarios:** ~20% of tests

### Running All Tests
```bash
cd backend/modules
python scottish_law/test_scottish_gates.py
```

---

## Pattern Maintenance Checklist

When adding/modifying patterns:

- [ ] Add regex pattern with proper escaping
- [ ] Define clear issue message
- [ ] Provide specific correction
- [ ] Include legal citation
- [ ] Add test case (FAIL and PASS examples)
- [ ] Update documentation
- [ ] Test for false positives
- [ ] Verify with actual legal text
- [ ] Check performance with long documents
- [ ] Consider cross-gate interactions

---

## Legal Authority Matrix

| Pattern Area | Primary Legislation | Secondary Sources | Case Law |
|-------------|---------------------|-------------------|----------|
| Employment | Prescription Act 1973 | ET Regs 2013 | - |
| Contracts | Contract Act 1997 | - | Stobo [1949], Grant [2011] |
| Data Protection | FOI Scotland 2002 | Public Records 2011 | - |
| Property | Land Reg 2012 | PRT Act 2016 | - |
| Corporate | Charities Act 2005 | Companies Act 2006 | - |

---

## Version History

**v1.0.0** (2025)
- Initial release
- 5 gates implemented
- 60 detection patterns
- 27 test cases
- Comprehensive documentation

---

## Future Pattern Additions

### Planned Enhancements
1. **Scottish criminal procedure patterns**
2. **Children's hearings system patterns**
3. **Scottish planning law patterns**
4. **Land and Buildings Transaction Tax (LBTT) patterns**
5. **Scottish Water charges patterns**

### Pattern Improvement Roadmap
1. Machine learning for pattern refinement
2. Natural language processing for context
3. Legislative update monitoring
4. Cross-reference with case law database

---

**Document Version:** 1.0.0
**Last Updated:** 2025
**Total Patterns Documented:** 60
**Gates Covered:** 5
