# UK Employment Law Expert

Specialist knowledge of UK employment law, ACAS Code, and tribunal procedures for LOKI compliance.

## Core Knowledge Areas

### 1. Employment Rights Act 1996/1999

**Key Provisions:**
- **ERA 1999 s10** - Right to be accompanied at disciplinary/grievance hearings
- **ERA 1996 s94-98** - Unfair dismissal protection
- **ERA 1996 s86** - Notice periods
- **ERA 1996 s13-27** - Deductions from wages

**LOKI Relevance:**
- Validate disciplinary procedures include accompaniment rights
- Check notice periods are reasonable
- Ensure dismissal procedures are fair

### 2. ACAS Code of Practice

**Disciplinary and Grievance Procedures (2015)**

**Key Requirements:**

```markdown
## Establish Facts (Para 5-7)
- Conduct investigation before disciplinary meeting
- Gather statements, documents
- Consider suspension if necessary (paid, not disciplinary)

## Inform Employee (Para 9-12)
- Provide written notice of meeting
- State nature of complaint/allegations
- Provide copies of evidence
- Give reasonable advance notice (usually 48 hours minimum)

## Meeting (Para 13-21)
- Employee right to be accompanied (trade union rep or colleague)
- Employer explains case
- Employee responds and presents evidence
- Adjourn if new information emerges

## Decision (Para 22-24)
- Based on evidence and employee response
- Communicated in writing
- Include appeal rights and timeframe

## Appeal (Para 26-29)
- Employee has right to appeal
- Heard by more senior manager if possible
- Final decision communicated in writing
```

**Sanctions Graduation:**
- First misconduct: Verbal warning (or first written)
- Repeat misconduct: Final written warning
- Further misconduct: Dismissal
- Gross misconduct: Summary dismissal (no notice) permitted if reasonable

### 3. Natural Justice Principles

**Procedural Fairness Requirements:**

```python
# Audi alteram partem - Right to be heard
RIGHT_TO_BE_HEARD = {
    'opportunity_to_respond': 'Employee must have chance to answer allegations',
    'present_evidence': 'Employee can present their case',
    'call_witnesses': 'Employee can request witness statements',
    'challenge_evidence': 'Employee can question evidence against them',
}

# Nemo judex in causa sua - No bias
IMPARTIALITY = {
    'independent_decision_maker': 'Person who investigated should not decide outcome',
    'no_predetermined_outcome': 'Decision must be open-minded',
    'no_personal_interest': 'Decision-maker must not have personal stake',
}

# Evidence-based decisions
EVIDENCE_REQUIREMENTS = {
    'reasonable_belief': 'Employer must reasonably believe misconduct occurred',
    'reasonable_investigation': 'Investigation must be adequate in circumstances',
    'proportionate_sanction': 'Penalty must fit the misconduct',
}
```

### 4. Unfair Dismissal Law

**Potentially Fair Reasons (ERA 1996 s98):**
- Capability/qualifications
- Conduct
- Redundancy
- Statutory restriction
- Some other substantial reason (SOSR)

**Reasonable Response Test:**
Did the employer act within the "band of reasonable responses" that a reasonable employer might adopt?

**Common Reasons for Tribunal Findings:**

```markdown
## Procedural Unfairness
- No investigation before dismissal
- No disciplinary meeting held
- Employee not given opportunity to respond
- No appeal offered
- Wrong person made decision (e.g., same person investigated and decided)

## Substantive Unfairness
- Dismissal too harsh for the conduct
- Inconsistent application of rules
- Sanctions not graduated
- No consideration of mitigation
- Alternative sanctions not considered
```

### 5. Protected Characteristics (Equality Act 2010)

**Nine Protected Characteristics:**
- Age
- Disability
- Gender reassignment
- Marriage/civil partnership
- Pregnancy/maternity
- Race
- Religion/belief
- Sex
- Sexual orientation

**Discrimination Types:**
- Direct discrimination
- Indirect discrimination
- Harassment
- Victimisation

**Reasonable Adjustments (Disability):**
- Employer must make reasonable adjustments for disabled employees
- Failure to do so is discrimination

## ACAS Code Compliance Patterns

### Pattern 1: Disciplinary Notice

```python
# Required elements for compliant disciplinary notice

REQUIRED_ELEMENTS = {
    'allegations': {
        'pattern': r'\b(?:allegation|alleged|complaint|concern)\b',
        'requirement': 'Specific allegations must be stated',
        'example': 'It is alleged that you...',
    },
    'meeting_details': {
        'date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        'time': r'\b\d{1,2}:\d{2}\b',
        'location': r'\b(?:room|office|location)\s*:?\s*\w+',
        'requirement': 'Date, time, and location must be provided',
    },
    'accompaniment': {
        'pattern': r'\b(?:accompanied|right\s+to.*?colleague|trade\s+union)\b',
        'requirement': 'Right to be accompanied must be stated',
        'example': 'You have the right to be accompanied by a trade union representative or work colleague',
    },
    'evidence': {
        'pattern': r'\b(?:evidence|documents|statements|attached|enclosed)\b',
        'requirement': 'Reference to evidence being provided',
    },
    'potential_outcome': {
        'pattern': r'\b(?:may\s+result|could\s+lead|potential|possible).*?(?:warning|dismissal|action)\b',
        'requirement': 'Potential outcomes should be indicated',
    },
}
```

### Pattern 2: Appeal Rights

```python
APPEAL_REQUIREMENTS = {
    'right_stated': {
        'pattern': r'\b(?:right\s+to\s+appeal|appeal|challenge).*?decision\b',
        'requirement': 'Employee must be informed of appeal right',
    },
    'timeframe': {
        'pattern': r'\bappeal.*?within\s+(\d+)\s+(?:days?|working\s+days?)\b',
        'requirement': 'Time limit for appeal should be stated',
        'typical': '5-10 working days',
    },
    'method': {
        'pattern': r'\bappeal.*?(?:in\s+writing|written|email|letter)\b',
        'requirement': 'How to submit appeal should be stated',
    },
    'addressee': {
        'pattern': r'\bappeal.*?(?:to|contact|send\s+to)\b',
        'requirement': 'Who receives appeal should be stated',
    },
}
```

## Tribunal Procedure

### Employment Tribunal Process

**Timeline:**
1. **Dismissal** - Employee dismissed
2. **ACAS Early Conciliation** - Mandatory (EC certificate required)
   - Employee contacts ACAS within 3 months minus 1 day
   - ACAS attempts conciliation for up to 1 month
3. **ET1 Claim Form** - Filed within 3 months (extended by EC period)
4. **ET3 Response** - Employer responds within 28 days
5. **Preliminary Hearing** - Case management
6. **Final Hearing** - Evidence, witnesses, decision

**Common Awards:**
- **Basic Award**: Up to £21,000 (based on age, length of service, weekly pay)
- **Compensatory Award**: Up to £115,115 or 52 weeks' pay (whichever lower)
- **ACAS Uplift**: Up to 25% if employer unreasonably failed to follow ACAS Code

### ACAS Code Uplift/Reduction

```python
# Tribunal can adjust compensation for ACAS Code breaches

ACAS_ADJUSTMENTS = {
    'uplift_employee': {
        'range': '0-25%',
        'trigger': 'Employer unreasonably failed to follow ACAS Code',
        'examples': [
            'No investigation before dismissal',
            'No disciplinary meeting held',
            'No appeal offered',
        ],
    },
    'reduction_employee': {
        'range': '0-25%',
        'trigger': 'Employee unreasonably failed to follow ACAS Code',
        'examples': [
            'Refused to attend meetings without good reason',
            'Did not raise grievance when should have',
        ],
    },
}
```

## Common LOKI Gate Scenarios

### Scenario 1: Immediate Dismissal

```markdown
**Text:** "You are dismissed with immediate effect for gross misconduct."

**Issues:**
- No investigation mentioned
- No disciplinary meeting offered
- No right to respond
- No appeal rights stated

**Gates that should FAIL:**
- investigation
- meeting_notice
- right_to_be_heard
- appeal

**Severity:** HIGH (tribunal risk)

**Legal Basis:**
- ACAS Code Para 5-7 (investigation)
- ACAS Code Para 9-12 (meeting)
- Natural justice principles
- ERA 1996 s98 (procedural fairness)
```

### Scenario 2: Vague Allegations

```markdown
**Text:** "Your recent behaviour has been unacceptable. Attend a meeting on Friday."

**Issues:**
- Allegations not specific ("behaviour", "unacceptable")
- No date/time details
- No accompaniment rights mentioned
- No evidence referenced

**Gates that should FAIL:**
- allegations (vague)
- meeting_details (incomplete)
- accompaniment (missing)
- evidence (not referenced)

**Severity:** HIGH

**Correction Needed:**
"It is alleged that you [specific incident with date and details].
Meeting: Friday 15 March 2024, 2:00 PM, Room 101.
You have the right to be accompanied by a trade union representative or work colleague.
Evidence is attached."
```

### Scenario 3: First-Time Dismissal

```markdown
**Text:** "Due to lateness on 1 March 2024, your employment is terminated."

**Issues:**
- First offense leading to dismissal
- No prior warnings
- Sanction not graduated
- Dismissal disproportionate to offense

**Gates that should FAIL:**
- sanction_graduation
- previous_warnings
- proportionality

**Severity:** HIGH

**Legal Basis:**
- ACAS Code (sanctions should be graduated)
- ERA 1996 s98 (reasonable response test)
- Case law: Iceland Frozen Foods v Jones [1983]
```

## Best Practices

1. **Always cite ACAS Code paragraph numbers** - e.g., "ACAS Code Para 15"
2. **Reference case law where applicable** - e.g., "British Home Stores v Burchell [1980]"
3. **Consider Scottish differences** - See scottish-legal-system skill
4. **Check qualification periods** - Unfair dismissal: 2 years service (except protected reasons)
5. **Note automatic unfair dismissal** - Whistleblowing, discrimination, pregnancy, etc.

## Employment Law Resources

### Official Sources
- **ACAS**: https://www.acas.org.uk (Code of Practice, guidance)
- **GOV.UK**: https://www.gov.uk/employment-tribunal-decisions
- **Legislation**: https://www.legislation.gov.uk (ERA 1996, Equality Act 2010)

### Key Cases
- **British Home Stores v Burchell [1980]** - Reasonable belief test
- **Iceland Frozen Foods v Jones [1983]** - Band of reasonable responses
- **Polkey v AE Dayton Services [1988]** - Procedural fairness
- **Taylor v OCS [2006]** - ACAS Code importance

## File Locations

- HR Scottish gates: `backend/modules/hr_scottish/gates/`
- ACAS test fixtures: `backend/tests/semantic/gold_fixtures/hr_scottish/`
- Employment law patterns: See compliance-gate-developer skill

## See Also

- **acas-guidance.md** - Detailed ACAS Code interpretation
- **tribunal-procedures.md** - ET process and awards
- **2025-updates.md** - Employment Rights Bill changes
- **scottish-differences.md** - Scottish employment law specifics
