# Regulatory Research Guide

How to research and translate UK regulations into LOKI compliance gates.

## Research Methodology

### 1. Identify Primary Sources

UK regulatory compliance gates must cite **primary legal sources**:

#### Financial Services (FCA)
- **FCA Handbook** - [handbook.fca.org.uk](https://www.handbook.fca.org.uk)
  - COBS (Conduct of Business Sourcebook)
  - PRIN (Principles for Businesses)
  - SYSC (Senior Management Arrangements)
- **Consumer Duty** - PS22/9 guidance
- **FCA Policy Statements** - For recent rule changes

#### Data Protection (GDPR/DPA)
- **UK GDPR** - Retained EU law (Data Protection Act 2018)
- **ICO Guidance** - [ico.org.uk](https://ico.org.uk)
- **PECR** - Privacy and Electronic Communications Regulations
- **Article 29 Working Party Opinions** - Interpretive guidance

#### Tax (HMRC)
- **VAT Act 1994** - Primary legislation
- **HMRC Manuals** - [gov.uk/hmrc-internal-manuals](https://www.gov.uk/hmrc-internal-manuals)
  - VAT Registration Manual (VATREG)
  - Business Income Manual (BIM)
- **VAT Notices** - Official HMRC guidance (e.g., Notice 700/21)
- **Making Tax Digital Regulations** - Finance (No.2) Act 2017

#### Employment Law (ACAS/UK)
- **Employment Rights Act 1996/1999**
- **ACAS Code of Practice** - [acas.org.uk](https://www.acas.org.uk)
- **Employment Tribunals** - Case law and precedents
- **Equality Act 2010**

#### Contract Law (NDAs)
- **Public Interest Disclosure Act 1998** (Whistleblowing)
- **Equality Act 2010 s111** (Harassment NDAs)
- **Contract Law Principles** - Reasonableness, enforceability

### 2. Research Process

#### Step 1: Understand the Regulation

```markdown
**Example: FCA COBS 4.2.1R - Fair, Clear, Not Misleading**

1. Read primary source:
   - COBS 4.2.1R: "A firm must ensure that a communication or a
     financial promotion is fair, clear and not misleading."

2. Find interpretive guidance:
   - FCA Handbook Guidance (COBS 4.2.1G)
   - FCA Policy Statements
   - Enforcement case studies

3. Identify key requirements:
   - Must be FAIR: Balanced risk/reward presentation
   - Must be CLEAR: Understandable to target audience
   - Must be NOT MISLEADING: No omissions, no false impressions

4. Note enforcement examples:
   - FCA fined XYZ Ltd for "guaranteed returns" claims
   - Warning notice for omitting risk warnings
```

#### Step 2: Extract Detectable Patterns

```python
# Translate regulation into detectable violations

# COBS 4.2.1R Violation Patterns:

# 1. UNFAIR - One-sided presentation
UNFAIR_PATTERNS = [
    r'\bguarantee[d]?\s+(?:return|profit)\b',  # Absolute claims
    r'\bzero\s+risk\b',                         # No risk acknowledgment
    r'\b(?:safe|secure)\s+investment\b',        # False security
]

# 2. UNCLEAR - Jargon without explanation
UNCLEAR_PATTERNS = [
    r'\b(?:derivative|CFD|forex)\b(?!.*(?:means|is|refers to))',
]

# 3. MISLEADING - Omissions
MISLEADING_PATTERNS = [
    # Past performance without warning
    r'\bpast\s+performance\b(?!.*not.*(?:guarantee|reliable))',
    # High returns without risk disclosure
    r'\b\d+%\s+return\b(?!.*\brisk\b)',
]
```

#### Step 3: Determine Severity

```python
# Map regulatory requirement to severity level

severity_mapping = {
    'criminal_offense': 'critical',          # Fraud Act violations
    'regulatory_breach_with_fines': 'critical',  # FCA fines
    'tribunal_risk': 'high',                 # Employment tribunal risk
    'civil_liability': 'high',               # Contract unenforceability
    'best_practice': 'medium',               # ACAS guidance
    'style_clarity': 'low',                  # Readability improvements
}

# COBS 4.2.1R breach -> FCA fines possible -> critical
```

#### Step 4: Verify with Case Law

```markdown
**Check Enforcement Actions:**

1. FCA Enforcement Database:
   - Search for relevant violations
   - Note common patterns in enforcement
   - Extract example language from warnings

2. Employment Tribunal Decisions:
   - Search for unfair dismissal cases
   - Note procedural failures cited
   - Extract tribunal language

3. ICO Enforcement:
   - Review GDPR enforcement actions
   - Note specific violations cited
   - Understand regulator priorities
```

### 3. Documenting Research

Create gate documentation with full citations:

```python
class FairClearNotMisleadingGate:
    """
    Validates financial promotions against FCA COBS 4.2.1R

    Legal Basis:
    - FCA Handbook COBS 4.2.1R (Fair, Clear, Not Misleading)
    - COBS 4.2.1G (Guidance on application)
    - FCA Policy Statement PS21/19

    Enforcement Precedents:
    - FCA Final Notice: XYZ Ltd (2023) - £50k fine for guaranteed returns
    - FCA Warning: ABC Partners (2022) - Missing risk warnings

    Severity: critical
    - FCA fines up to £500k for breaches
    - Criminal prosecution possible for fraud (Fraud Act 2006 s2-4)

    Detection Strategy:
    - Detect absolute/guaranteed return claims
    - Check for risk warnings when returns mentioned
    - Flag pressure tactics and urgency language
    """

    def __init__(self):
        self.name = "fair_clear_not_misleading"
        self.severity = "critical"
        self.legal_source = "FCA COBS 4.2.1R (Fair, Clear, Not Misleading)"
        # ...
```

## Regulation Translation Examples

### Example 1: GDPR Article 13

```markdown
**Regulation:**
"Article 13(1) - Information to be provided where personal data
are collected from the data subject"

**Requirements:**
(a) identity and contact details of controller
(b) contact details of DPO (if applicable)
(c) purposes of processing and lawful basis
(d) legitimate interests (if applicable)
(e) recipients/categories of recipients
(f) international transfers (if applicable)

**Gate Implementation:**
```

```python
class Article13ComplianceGate:
    def check(self, text, document_type):
        if document_type != 'privacy_policy':
            return {'status': 'N/A'}

        missing_elements = []

        # (a) Controller identity
        if not re.search(r'\b(?:data\s+)?controller\b|\bwe\s+are\b', text, re.I):
            missing_elements.append('Controller identity')

        # (c) Purposes and lawful basis
        purposes_present = re.search(r'\bpurpose[s]?\b', text, re.I)
        lawful_basis_terms = r'\b(?:consent|contract|legal\s+obligation|legitimate\s+interest)\b'
        lawful_basis_present = re.search(lawful_basis_terms, text, re.I)

        if not (purposes_present and lawful_basis_present):
            missing_elements.append('Purposes and lawful basis')

        # (f) International transfers
        transfer_indicators = r'\b(?:outside\s+(?:UK|EEA)|third\s+country|international)\b'
        if re.search(transfer_indicators, text, re.I):
            safeguards = r'\b(?:adequacy|standard\s+contractual\s+clauses|appropriate\s+safeguards)\b'
            if not re.search(safeguards, text, re.I):
                missing_elements.append('Transfer safeguards')

        if missing_elements:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': f'Missing GDPR Article 13 requirements: {", ".join(missing_elements)}',
                'legal_source': 'GDPR Article 13(1)',
                'suggestion': 'Include all required information per Article 13'
            }

        return {'status': 'PASS'}
```

### Example 2: ACAS Code - Right to be Accompanied

```markdown
**Regulation:**
Employment Relations Act 1999 s10 + ACAS Code para 15

"Workers have a statutory right to be accompanied by a companion
where the disciplinary meeting could result in:
- a formal warning
- some other disciplinary action
- the confirmation of a warning or other disciplinary action"

**Companion:**
- Trade union representative OR
- Work colleague

**NOT:**
- Solicitor/lawyer
- Family member
```

```python
class AccompanimentGate:
    def __init__(self):
        self.legal_source = "ERA 1999 s10 + ACAS Code para 15"
        self.severity = "high"  # Tribunal risk if not provided

    def check(self, text, document_type):
        # Check if accompaniment mentioned
        accompaniment_mentioned = bool(re.search(
            r'\b(?:accompanied|accompaniment|companion|representative)\b',
            text, re.IGNORECASE
        ))

        if not accompaniment_mentioned:
            return {
                'status': 'FAIL',
                'severity': 'high',
                'message': 'No mention of right to be accompanied',
                'legal_source': self.legal_source,
                'suggestion': 'State: "You have the right to be accompanied by a trade union representative or work colleague."'
            }

        # Check if valid companions specified
        valid_companions = r'\b(?:trade\s+union|colleague|work\s+colleague)\b'
        if re.search(valid_companions, text, re.IGNORECASE):
            return {'status': 'PASS'}

        # Check for invalid companions
        invalid_companions = r'\b(?:solicitor|lawyer|family|friend)\b'
        if re.search(invalid_companions, text, re.IGNORECASE):
            return {
                'status': 'FAIL',
                'severity': 'high',
                'message': 'Invalid companion types mentioned',
                'legal_source': self.legal_source,
                'suggestion': 'Companion must be trade union rep or work colleague (not solicitor/family)'
            }

        return {'status': 'PASS'}
```

## Research Tools

### Official Sources

1. **FCA Handbook**
   - URL: https://www.handbook.fca.org.uk
   - Search functionality for rules and guidance
   - Download PDF versions of sourcebooks

2. **ICO Website**
   - URL: https://ico.org.uk/for-organisations/
   - Guidance documents
   - Data protection checklists

3. **GOV.UK**
   - HMRC manuals: https://www.gov.uk/hmrc-internal-manuals
   - Legislation: https://www.legislation.gov.uk
   - Employment law: https://www.gov.uk/employment-tribunal-decisions

4. **ACAS**
   - URL: https://www.acas.org.uk
   - Code of Practice (download PDF)
   - Guidance on disciplinary procedures

### Case Law Research

1. **FCA Enforcement**
   - https://www.fca.org.uk/publication/corporate/enforcement-annual-performance-report.pdf
   - Search enforcement notices

2. **Employment Tribunals**
   - https://www.gov.uk/employment-tribunal-decisions
   - Search by keywords (e.g., "unfair dismissal", "disciplinary")

3. **ICO Enforcement**
   - https://ico.org.uk/action-weve-taken/enforcement/
   - GDPR penalty notices

## Common Pitfalls

1. **Using secondary sources** - Always cite primary legislation
2. **Outdated regulations** - Check for recent amendments
3. **Misunderstanding guidance vs rules** - Know the difference
4. **Over-generalization** - Be specific to jurisdiction (UK not EU)
5. **Ignoring case law** - Enforcement reveals real-world interpretation

## Checklist for New Gate

- [ ] Primary legal source identified and cited
- [ ] Regulation requirement fully understood
- [ ] Detectable patterns extracted
- [ ] Severity level justified
- [ ] Enforcement precedents researched
- [ ] Edge cases considered
- [ ] Examples of violations collected
- [ ] Examples of compliance collected
- [ ] Test fixtures created
- [ ] Documentation complete

## Resources

- FCA Handbook: https://www.handbook.fca.org.uk
- UK GDPR: https://ico.org.uk/for-organisations/guide-to-data-protection/
- HMRC Manuals: https://www.gov.uk/hmrc-internal-manuals
- ACAS: https://www.acas.org.uk
- Legislation.gov.uk: https://www.legislation.gov.uk
