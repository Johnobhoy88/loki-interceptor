# Gate Design Patterns

Comprehensive regex pattern library for LOKI compliance gates.

## Pattern Categories

### 1. Financial Compliance Patterns (FCA)

#### Guaranteed Returns Detection

```python
# Detect absolute/guaranteed return claims
GUARANTEE_PATTERNS = [
    r'\b(?:guarantee[d]?|certain|assured|promised?|definite)\s+(?:return|profit|gain|income|yield)\b',
    r'\b(?:zero|no)\s+risk\b',
    r'\b(?:safe|secure)\s+investment\b',
    r'\b(?:always|consistently|every\s+(?:year|time))\s+(?:deliver|return|profit)\b',
]

# Detect performance claims without risk warnings
PERFORMANCE_WITHOUT_RISK = r'\b\d+%\s+(?:return|profit|gain)\b(?!.*\b(?:risk|may fall|not guaranteed)\b)'

# Detect pressure tactics
PRESSURE_TACTICS = [
    r'\b(?:limited|exclusive|one-time)\s+(?:offer|opportunity|time)\b',
    r'\b(?:act|invest|buy)\s+(?:now|today|immediately)\b',
    r'\b(?:don\'t|do not)\s+(?:miss|wait)\b',
    r'\bonly\s+\d+\s+(?:spots|places)\s+(?:left|remaining)\b',
]

# Detect past performance issues
PAST_PERFORMANCE_CLAIMS = r'\b(?:past|historical|previous|last\s+\d+\s+years?)\s+(?:return|performance|result)\b'
PAST_PERFORMANCE_WARNING = r'\bpast\s+performance.*?not.*?(?:guarantee|indication|reliable\s+guide)\b'
```

#### Risk Warning Requirements

```python
# Required risk disclosures for investments
INVESTMENT_CONTEXT = r'\b(?:invest|return|profit|performance|portfolio|fund|stock|share)\b'

RISK_WARNINGS = [
    r'\b(?:capital|investment|money)\s+(?:at\s+)?risk\b',
    r'\bvalue\s+(?:can|may)\s+(?:fall|go\s+down)\b',
    r'\byou\s+(?:may|could)\s+(?:lose|get\s+back\s+less)\b',
    r'\bnot\s+guaranteed\b',
    r'\bpast\s+performance.*?not.*?guide\b',
]

def check_risk_warnings(text):
    """Ensure risk warnings present when investment context exists"""
    if re.search(INVESTMENT_CONTEXT, text, re.IGNORECASE):
        has_warning = any(re.search(pattern, text, re.IGNORECASE) for pattern in RISK_WARNINGS)
        return has_warning
    return True  # Not applicable
```

#### Suitability Assessment

```python
# Detect unsuitable recommendations
SUITABILITY_CONTEXT = r'\b(?:recommend|suitable\s+for|ideal\s+for|perfect\s+for)\b'

UNSUITABLE_CLAIMS = [
    r'\b(?:suitable|perfect|ideal)\s+for\s+(?:everyone|all|anyone)\b',
    r'\b(?:no|zero)\s+(?:experience|knowledge)\s+(?:required|needed)\b',
    r'\b(?:anyone|everyone)\s+can\s+(?:invest|profit)\b',
]

# Detect missing suitability assessment
def requires_suitability_check(text):
    """Check if suitability assessment is needed"""
    high_risk_indicators = [
        r'\b(?:derivatives|options|futures|CFD|forex|cryptocurrency)\b',
        r'\b(?:leveraged|margin)\s+trading\b',
        r'\b(?:high|significant)\s+(?:risk|return)\b',
    ]
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in high_risk_indicators)
```

### 2. Data Protection Patterns (GDPR)

#### Lawful Basis Detection

```python
# Six lawful bases for processing
LAWFUL_BASIS_PATTERNS = {
    'consent': r'\b(?:consent|agree|permission|opt-in)\b',
    'contract': r'\b(?:contract|agreement|terms|service|provide)\b',
    'legal_obligation': r'\b(?:legal\s+(?:obligation|requirement|duty)|comply\s+with\s+law)\b',
    'vital_interests': r'\b(?:vital\s+interest|life-threatening|medical\s+emergency)\b',
    'public_task': r'\b(?:public\s+(?:task|interest|function)|official\s+authority)\b',
    'legitimate_interests': r'\b(?:legitimate\s+interest|necessary\s+for\s+our)\b',
}

def check_lawful_basis(text):
    """Verify at least one lawful basis is cited"""
    return any(re.search(pattern, text, re.IGNORECASE)
               for pattern in LAWFUL_BASIS_PATTERNS.values())
```

#### Vague Purpose Detection

```python
# Patterns indicating vague/non-specific purposes
VAGUE_PURPOSES = [
    r'\b(?:various|many|several|other)\s+purpose[s]?\b',
    r'\b(?:business|operational|legitimate|necessary)\s+purpose[s]?\b',
    r'\b(?:improve|enhance|develop)\s+(?:our\s+)?(?:service|business|operation)s?\b',
    r'\bcollect.*?data.*?for.*?purposes?\b(?!.*specifically)',
]

# Acceptable specific purposes
SPECIFIC_PURPOSES = [
    r'\bprocess.*?(?:order|payment|transaction)\b',
    r'\b(?:provide|deliver).*?(?:service|product)\b',
    r'\brespond.*?(?:query|request|enquiry)\b',
    r'\bcomply.*?(?:legal|regulatory|tax)\b',
]
```

#### Consent Validity

```python
# Invalid consent patterns
INVALID_CONSENT = [
    r'\b(?:by\s+using|accessing)\s+(?:this\s+)?(?:site|website|service).*?(?:you\s+)?(?:agree|consent)\b',
    r'\b(?:continued\s+use|using\s+our).*?(?:consent|agreement)\b',
    r'\bpre-ticked\s+box\b',
    r'\bopt-out\s+(?:if|unless)\b',
    r'\bimplied\s+consent\b',
]

# Valid consent requirements
VALID_CONSENT_REQUIREMENTS = [
    r'\b(?:freely\s+given|voluntary)\b',
    r'\b(?:specific|informed|unambiguous)\b',
    r'\b(?:clear\s+affirmative|positive)\s+action\b',
    r'\bwithdraw.*?consent\b',
]
```

#### International Transfers

```python
# Detect international data transfers
TRANSFER_INDICATORS = [
    r'\b(?:transfer|send|share).*?(?:outside|abroad|internationally)\b',
    r'\b(?:third\s+country|non-EEA|non-EU|international)\b',
    r'\b(?:USA|United\s+States|America|China|India|[A-Z]{2}\s+(?:server|datacenter))\b',
]

# Required safeguards
TRANSFER_SAFEGUARDS = [
    r'\b(?:adequacy\s+decision|standard\s+contractual\s+clauses|SCCs?)\b',
    r'\b(?:binding\s+corporate\s+rules|BCRs?)\b',
    r'\b(?:appropriate\s+safeguards|protection)\b',
]
```

### 3. Tax Compliance Patterns (HMRC)

#### VAT Number Validation

```python
# UK VAT number formats
VAT_PATTERNS = {
    'standard': r'\bGB\d{9}\b',           # GB123456789
    'branch': r'\bGB\d{12}\b',            # GB123456789001
    'government': r'\bGD\d{3}\b',         # GD001
    'health': r'\bHA\d{3}\b',             # HA501
    'northern_ireland': r'\bXI\d{9}\b',   # XI123456789 (post-Brexit)
}

def validate_vat_number(text):
    """Validate VAT number format and checksum"""
    import re

    # Find VAT numbers
    vat_matches = re.findall(r'\b(?:VAT\s*(?:No\.?|Number)?\s*:?\s*)?([GX][BDHI]\d{9,12})\b', text, re.IGNORECASE)

    for vat in vat_matches:
        # Validate format
        if not any(re.match(pattern, vat) for pattern in VAT_PATTERNS.values()):
            return False, f"Invalid VAT format: {vat}"

        # Validate checksum (for standard GB numbers)
        if vat.startswith('GB') and len(vat) == 11:
            digits = [int(d) for d in vat[2:]]
            weights = [8, 7, 6, 5, 4, 3, 2, 10, 1]
            total = sum(d * w for d, w in zip(digits, weights))
            if total % 97 != 0:
                return False, f"Invalid VAT checksum: {vat}"

    return True, "Valid"
```

#### VAT Rate Validation

```python
# Current UK VAT rates (as of 2024)
VALID_VAT_RATES = ['0%', '5%', '20%']

# Detect VAT rate mentions
VAT_RATE_PATTERN = r'\b(?:VAT|tax)(?:\s+rate)?.*?(\d+(?:\.\d+)?%)'

def check_vat_rates(text):
    """Validate all mentioned VAT rates are correct"""
    matches = re.findall(VAT_RATE_PATTERN, text, re.IGNORECASE)
    invalid_rates = [rate for rate in matches if rate not in VALID_VAT_RATES]
    return len(invalid_rates) == 0, invalid_rates
```

#### Invoice Requirements

```python
# Required VAT invoice fields (VAT Notice 700/21)
INVOICE_REQUIREMENTS = {
    'invoice_number': r'\b(?:Invoice|INV)(?:\s+No\.?|\s+Number)?\s*:?\s*[A-Z0-9-]+\b',
    'date': r'\b(?:Date|Dated)\s*:?\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
    'supplier_name': r'\b(?:From|Supplier|Company)\s*:?\s*[A-Z].+\b',
    'supplier_address': r'\b\d+\s+[A-Z].+(?:Road|Street|Avenue|Lane|Drive)\b',
    'customer_name': r'\b(?:To|Customer|Bill\s+To)\s*:?\s*[A-Z].+\b',
    'vat_number': r'\bVAT\s*(?:No\.?|Number)?\s*:?\s*GB\d{9,12}\b',
    'total': r'\b(?:Total|Amount\s+Due)\s*:?\s*£?\d+(?:\.\d{2})?\b',
}

def validate_invoice(text):
    """Check all required invoice fields present"""
    missing_fields = []
    for field, pattern in INVOICE_REQUIREMENTS.items():
        if not re.search(pattern, text, re.IGNORECASE):
            missing_fields.append(field)
    return len(missing_fields) == 0, missing_fields
```

#### Tax Deadline Accuracy

```python
# HMRC tax deadlines
TAX_DEADLINES = {
    'sa_online': {
        'pattern': r'\b(?:Self[\s-]Assessment|SA).*?(?:deadline|due|submit)',
        'correct': '31 January',
        'incorrect': [r'31st?\s+(?:Dec|February|March)']
    },
    'sa_paper': {
        'pattern': r'\b(?:paper|postal).*?(?:Self[\s-]Assessment|SA).*?(?:deadline|due)',
        'correct': '31 October',
        'incorrect': [r'31st?\s+(?:Jan|Nov|Dec)']
    },
    'ct_payment': {
        'pattern': r'\b(?:Corporation\s+Tax|CT).*?(?:payment|pay|due)',
        'correct': '9 months and 1 day',
        'incorrect': [r'9\s+months(?!\s+and\s+1\s+day)', r'12\s+months']
    },
    'vat_quarterly': {
        'pattern': r'\bVAT.*?(?:quarterly|return).*?(?:deadline|due)',
        'correct': '1 month and 7 days',
        'incorrect': [r'1\s+month(?!\s+and\s+7\s+days)', r'30\s+days']
    },
}
```

### 4. Employment Law Patterns (HR/Scottish)

#### ACAS Code Compliance

```python
# Right to be accompanied (ERA 1999 s10)
ACCOMPANIMENT_PATTERNS = {
    'right_mentioned': r'\b(?:accompanied|accompany|companion|representative)\b',
    'valid_companion': r'\b(?:trade\s+union|colleague|work\s+colleague)\b',
    'invalid_companion': r'\b(?:family|friend|solicitor|lawyer)\b',
}

# Notice requirements
NOTICE_REQUIREMENTS = {
    'advance_notice': r'\b(?:\d+)\s+(?:day|working\s+day)s?\s+(?:notice|advance\s+notice)\b',
    'meeting_datetime': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}.*?\d{1,2}:\d{2}\b',
    'meeting_location': r'\b(?:room|office|location|venue)\s*:?\s*[A-Z0-9].+\b',
}

# Appeal rights
APPEAL_PATTERNS = {
    'appeal_right': r'\b(?:right\s+to\s+appeal|appeal|challenge).*?(?:decision|outcome)\b',
    'appeal_timeframe': r'\b(?:appeal|challenge).*?(?:within|by)\s+\d+\s+(?:day|working\s+day)s?\b',
    'appeal_process': r'\b(?:appeal|challenge).*?(?:writing|written|email)\b',
}
```

#### Natural Justice Principles

```python
# Right to be heard
RIGHT_TO_BE_HEARD = [
    r'\b(?:right\s+to|opportunity\s+to|chance\s+to)\s+(?:respond|reply|explain|present)\b',
    r'\b(?:your|employee)\s+(?:version|side|explanation|response)\b',
]

# Impartial decision-maker
IMPARTIALITY_PATTERNS = {
    'conflict_of_interest': r'\b(?:independent|impartial|different|separate)\s+(?:person|manager|panel)\b',
    'same_investigator_and_chair': r'\b(?:investigated|investigation).*?(?:same|also).*?(?:chair|decide|decision)\b',
}

# Evidence disclosure
EVIDENCE_DISCLOSURE = [
    r'\b(?:see|review|access|provided\s+with)\s+(?:all\s+)?(?:evidence|document|statement|report)s?\b',
    r'\b(?:evidence|document)s?\s+(?:shared|disclosed|given)\b',
]
```

### 5. NDA Patterns (Contract Law)

#### Unlawful Restrictions

```python
# Whistleblowing protection (PIDA 1998)
WHISTLEBLOWING_RESTRICTION = [
    r'\b(?:prohibit|prevent|restrict).*?(?:disclosure|report|reporting)\b',
    r'\b(?:not|never)\s+(?:disclose|report|reveal).*?(?:to\s+(?:authorities|regulator|police))\b',
]

WHISTLEBLOWING_PROTECTION = r'\b(?:protected\s+disclosure|whistleblowing|PIDA|public\s+interest)\b'

# Harassment protection (Equality Act 2010 s111)
HARASSMENT_RESTRICTION = r'\b(?:prohibit|prevent).*?(?:harassment|discrimination)\s+claim\b'

# Crime reporting
CRIME_REPORTING_RESTRICTION = r'\b(?:not|never)\s+(?:report|disclose).*?(?:to\s+police|criminal|unlawful)\b'
```

#### Definition Specificity

```python
# Overly broad confidential information definitions
BROAD_DEFINITIONS = [
    r'\b(?:all|any|everything)\s+(?:information|data|knowledge)\b',
    r'\b(?:any\s+and\s+all|whatsoever)\b',
    r'\b(?:directly|indirectly)\s+(?:relate|concern|involve)\b',
]

# Proper exclusions
PROPER_EXCLUSIONS = [
    r'\b(?:public\s+(?:domain|knowledge)|publicly\s+available)\b',
    r'\b(?:independently\s+developed|known\s+prior)\b',
    r'\b(?:lawfully\s+(?:received|obtained)|required\s+by\s+law)\b',
]
```

#### Duration Reasonableness

```python
# Unreasonable duration detection
DURATION_PATTERNS = {
    'perpetual': r'\b(?:perpetual|forever|indefinite|permanently)\b',
    'unreasonable_years': r'\b(\d+)\s+year[s]?\b',  # > 5 years typically unreasonable
}

def check_nda_duration(text):
    """Validate NDA duration is reasonable"""
    # Check for perpetual terms
    if re.search(DURATION_PATTERNS['perpetual'], text, re.IGNORECASE):
        return False, "Perpetual confidentiality likely unenforceable"

    # Check for excessive years
    year_matches = re.findall(DURATION_PATTERNS['unreasonable_years'], text, re.IGNORECASE)
    excessive = [int(y) for y in year_matches if int(y) > 5]

    if excessive:
        return False, f"Duration of {max(excessive)} years may be unreasonable"

    return True, "Duration appears reasonable"
```

## Pattern Testing

### Regex Performance Testing

```python
import re
import time

def test_pattern_performance(pattern, text, iterations=10000):
    """Measure regex performance"""
    compiled = re.compile(pattern, re.IGNORECASE)

    start = time.time()
    for _ in range(iterations):
        compiled.search(text)
    elapsed = time.time() - start

    avg_time = (elapsed / iterations) * 1000  # ms
    return avg_time

# Example
pattern = r'\b(?:guarantee[d]?|certain|assured)\s+(?:return|profit)\b'
text = "Your test document here"
avg_ms = test_pattern_performance(pattern, text)
print(f"Average time: {avg_ms:.4f}ms")
```

### Catastrophic Backtracking Prevention

```python
# BAD: Can cause catastrophic backtracking
bad_pattern = r'(a+)+b'

# GOOD: More specific, no nested quantifiers
good_pattern = r'a+b'

# BAD: Overlapping alternatives
bad_pattern = r'\b(?:test|testing|tested)\b'

# GOOD: Use optional groups
good_pattern = r'\btest(?:ing|ed)?\b'
```

### Pattern Validation

```python
def validate_pattern(pattern, test_cases):
    """
    Test pattern against known cases

    Args:
        pattern: Regex pattern string
        test_cases: List of (text, should_match) tuples
    """
    compiled = re.compile(pattern, re.IGNORECASE)

    for text, should_match in test_cases:
        matches = bool(compiled.search(text))
        if matches != should_match:
            status = "FAIL"
            print(f"{status}: Expected {should_match}, got {matches} for: {text}")
        else:
            print(f"PASS: {text}")

# Example usage
test_cases = [
    ("Guaranteed 10% returns", True),
    ("Potential returns may vary", False),
    ("Past performance is not guaranteed", False),
]

validate_pattern(GUARANTEE_PATTERNS[0], test_cases)
```

## Best Practices

1. **Use word boundaries** (`\b`) to avoid partial matches
2. **Group alternatives efficiently** - Use `(?:test|testing)` not `(test|testing)`
3. **Avoid nested quantifiers** - Never use `(a+)+` or `(a*)*`
4. **Be case-insensitive** - Use `re.IGNORECASE` flag
5. **Compile patterns** - For repeated use, compile with `re.compile()`
6. **Test thoroughly** - Include edge cases, unicode, special characters
7. **Document patterns** - Explain what each pattern detects and why

## Resources

- [Python re module documentation](https://docs.python.org/3/library/re.html)
- [Regex101](https://regex101.com/) - Online regex tester
- [RegExr](https://regexr.com/) - Visual regex builder
