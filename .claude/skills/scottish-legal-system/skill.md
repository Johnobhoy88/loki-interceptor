# Scottish Legal System

Expert in Scots law differences from English law relevant to LOKI compliance.

## Key Differences

### 1. Legal System Structure

**Scotland:** Separate legal system (since Act of Union 1707)
- Court of Session (civil)
- High Court of Justiciary (criminal)
- Sheriff Courts (local)
- Scottish Land Court

**Different from England/Wales:** Distinct legal tradition, precedents, terminology

### 2. Contract Law

**Scots Law Specifics:**
- **Consensus in idem** (meeting of minds) required
- No requirement for consideration (unlike English law)
- **Unilateral obligations** enforceable (e.g., promises)
- Different rules on penalty clauses

**LOKI Implications:**
```python
# Scottish NDAs may not need consideration clause
scots_contract_valid_without_consideration = True

# But English contracts require it
english_contract_requires_consideration = True
```

### 3. Employment Law (Scottish Specificities)

**Generally:** UK-wide employment law applies (ERA, Equality Act, ACAS Code)

**Scottish Differences:**
- **ACAS Scotland** - Separate arm of ACAS
- **Scottish Employment Tribunals** - Sit in Glasgow, Edinburgh, Dundee, Aberdeen
- **Different terminology** - Some Scottish legal terms
- **Different regulatory bodies** - For Scottish public sector

**LOKI hr_scottish Module:**
- Applies UK employment law gates
- Adds Scottish context where relevant
- Uses Scottish terminology where appropriate

### 4. Data Protection

**UK GDPR applies uniformly** BUT:
- **Scottish Information Commissioner** - Separate regulator for Scottish public authorities
- **FOI Scotland** - Different FOI regime (Freedom of Information (Scotland) Act 2002)

### 5. Tax Law

**Different tax rates:**

**Scottish Income Tax (Scotland Act 2016):**
```python
SCOTTISH_TAX_BANDS_2024 = {
    'starter_rate': (0, 14_876, 0.19),
    'basic_rate': (14_877, 26_561, 0.20),
    'intermediate_rate': (26_562, 43_662, 0.21),
    'higher_rate': (43_663, 75_000, 0.42),  # Different from rUK
    'top_rate': (75_001, float('inf'), 0.47),
}

# Rest of UK (England, Wales, NI)
RUK_TAX_BANDS_2024 = {
    'basic_rate': (0, 37_700, 0.20),
    'higher_rate': (37_701, 125_140, 0.40),
    'additional_rate': (125_141, float('inf'), 0.45),
}
```

**VAT, Corporation Tax:** Same as rest of UK

## LOKI Scottish-Specific Gates

### Tax Module: scottish_tax_specifics

```python
class ScottishTaxSpecificsGate:
    """
    Warns if Scottish income tax referenced without clarifying Scottish bands

    Legal Source: Scotland Act 2016
    """

    def check(self, text, document_type):
        # Check if Scottish context
        scotland_indicators = [
            r'\bScottish\s+(?:income\s+)?tax\b',
            r'\bScotland\s+Act\b',
            r'\bScottish\s+bands?\b',
        ]

        has_scottish_tax = any(re.search(p, text, re.I) for p in scotland_indicators)

        if not has_scottish_tax:
            return {'status': 'N/A'}

        # Check if bands clarified
        band_clarification = [
            r'\b(?:starter|intermediate)\s+rate\b',  # Scottish-specific bands
            r'\bdifferent\s+(?:from|to)\s+(?:rest\s+of\s+)?(?:UK|England)\b',
            r'\bScottish\s+(?:resident|taxpayer)s?\b',
        ]

        has_clarification = any(re.search(p, text, re.I) for p in band_clarification)

        if not has_clarification:
            return {
                'status': 'FAIL',
                'severity': 'medium',
                'message': 'Scottish tax mentioned without clarifying Scottish bands',
                'legal_source': 'Scotland Act 2016',
                'suggestion': 'Clarify Scottish income tax bands differ from rest of UK'
            }

        return {'status': 'PASS'}
```

## Scottish Employment Law Terminology

### Scots Law Employment Terms

```python
SCOTTISH_EMPLOYMENT_TERMS = {
    # English term: Scottish equivalent (if different)
    'claimant': 'pursuer',  # In court context (not ET)
    'defendant': 'defender',
    'injunction': 'interdict',
    'cross-examination': 'cross-interrogatories',
}

# Note: Employment Tribunals use UK-wide terminology
# These differences apply in civil courts
```

## Scottish Regulatory Bodies

### Employment/HR
- **ACAS Scotland** - Advisory, Conciliation and Arbitration Service (Scottish arm)
- **Employment Tribunals Scotland** - Glasgow, Edinburgh, Dundee, Aberdeen
- **Scottish Government** - Employment policy (devolved matters)

### Data Protection
- **ICO** - UK-wide (including Scotland for private sector)
- **Scottish Information Commissioner** - Scottish public authorities

### Financial Services
- **FCA** - UK-wide (including Scotland)
- **Scottish Financial Enterprise** - Industry body

### Tax
- **HMRC** - UK-wide
- **Revenue Scotland** - Scottish taxes (LBTT, SLfT)

## Case Law Differences

### Scottish Court Structure

```markdown
**Supreme Court** (UK-wide, final appeal)
    ↑
**Court of Session** (Inner House - appeals)
    ↑
**Court of Session** (Outer House - first instance)
**Sheriff Courts** (local civil/criminal)

Employment Tribunals → Employment Appeal Tribunal → Court of Session → Supreme Court
```

### Key Scottish Cases

**Employment:**
- **Khaliq v Strathclyde Regional Council (1986)** - Disciplinary procedures
- **Scott v Richardson (2005)** - Unfair dismissal (Scottish court)

**Contract:**
- **McBryde on Contract** - Leading Scottish contract law text
- Different approach to contra proferentem rule

## LOKI Implementation for Scotland

### When to Use Scottish-Specific Logic

```python
def detect_scottish_context(text, document_metadata):
    """
    Determine if Scottish law applies

    Returns:
        bool: True if Scottish context detected
    """
    scottish_indicators = [
        r'\bScots?\s+law\b',
        r'\bCourt\s+of\s+Session\b',
        r'\bSheriff\s+Court\b',
        r'\bScottish\s+(?:Government|Parliament)\b',
        r'\b(?:governed|subject)\s+to.*?(?:Scots|Scottish)\s+law\b',
    ]

    # Check document text
    text_indicates_scottish = any(re.search(p, text, re.I) for p in scottish_indicators)

    # Check metadata
    metadata_indicates_scottish = (
        document_metadata.get('jurisdiction') == 'Scotland' or
        document_metadata.get('governing_law') == 'Scots'
    )

    return text_indicates_scottish or metadata_indicates_scottish
```

### Module Selection

```python
# For Scottish employment documents
if detect_scottish_context(text, metadata):
    modules = ['hr_scottish', 'gdpr_uk', 'nda_uk']
else:
    modules = ['hr_uk', 'gdpr_uk', 'nda_uk']  # Generic UK modules

# Tax module handles Scottish differences internally
modules.append('tax_uk')
```

## Best Practices

1. **Don't assume English law** - Check jurisdiction
2. **Use UK GDPR** - Data protection is UK-wide
3. **Note tax differences** - Scottish income tax has different bands
4. **ACAS Code applies** - Employment procedures are UK-wide
5. **Check governing law clause** - Contracts may specify Scots or English law
6. **Use correct terminology** - Scots law terms differ from English

## Resources

- **Scottish Courts**: https://www.scotcourts.gov.uk/
- **Scottish Parliament**: https://www.parliament.scot/
- **Revenue Scotland**: https://www.revenue.scot/
- **ACAS Scotland**: https://www.acas.org.uk/scotland
- **Employment Tribunals Scotland**: https://www.gov.uk/courts-tribunals/employment-tribunal-scotland

## File Locations

- Scottish gates: `backend/modules/hr_scottish/gates/`
- Scottish tax gate: `backend/modules/tax_uk/gates/scottish_tax_specifics.py`
- Tests: `backend/tests/semantic/gold_fixtures/hr_scottish/`

## See Also

- `contract-law.md` - Scots contract law differences
- `employment.md` - Scottish employment law specifics
- `regulatory-bodies.md` - Scottish regulators
- `legal-precedents.md` - Key Scottish cases
