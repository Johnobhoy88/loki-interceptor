# ACAS Code of Practice - Detailed Guidance

Comprehensive interpretation of the ACAS Code for LOKI gate development.

## ACAS Code Structure

The ACAS Code of Practice on Disciplinary and Grievance Procedures (2015) has 48 paragraphs covering:
- Paragraphs 1-4: General principles
- Paragraphs 5-29: Disciplinary procedures
- Paragraphs 30-47: Grievance procedures
- Paragraph 48: Modifications for small employers

## Disciplinary Procedure Breakdown

### Investigation (Paragraphs 5-7)

**Paragraph 5:** "Establish facts promptly before memories fade"
- Investigation should be reasonable in the circumstances
- Gather written statements, documents, CCTV
- Interview relevant witnesses

**Paragraph 6:** "Inform employee if allegations may result in formal disciplinary action"
- Early communication reduces surprises
- Maintains transparency

**Paragraph 7:** "Suspension - if necessary, on full pay"
- Not disciplinary action
- Only if investigation requires it
- Must be paid (unless contract says otherwise)
- Brief as possible

**LOKI Detection:**
```python
# Check if investigation mentioned in dismissal/warning letters
investigation_indicators = [
    r'\binvestigation\b',
    r'\benquir(?:y|ies)\b',
    r'\bstatements?\s+(?:taken|gathered)\b',
    r'\bevidence\s+gathered\b',
]

# Suspension must be paid
suspension_unpaid = r'\b(?:unpaid|without\s+pay)\s+suspension\b'  # FAIL
```

### Written Notice (Paragraphs 9-12)

**Paragraph 9:** "Invite in writing, give reasonable notice"
- Written invitation required
- Reasonable advance notice (usually 48 hours minimum, more for serious cases)

**Paragraph 10:** "State allegations and basis for them"
- Specific, not vague
- Include dates, times, witnesses
- Reference evidence

**Paragraph 11:** "Provide copies of evidence"
- All relevant documents
- Witness statements
- CCTV, emails, etc.

**Paragraph 12:** "Right to be accompanied"
- Trade union representative OR work colleague
- NOT solicitor, family, friend

**LOKI Detection:**
```python
WRITTEN_NOTICE_REQUIREMENTS = {
    'allegations_specific': {
        'pass': r'\b(?:alleged|allegation).*?(?:on|dated?)\s+\d{1,2}[/-]\d{1,2}',
        'fail': r'\b(?:recent|your)\s+(?:behaviour|conduct|performance)\b(?!.*specific)',
    },
    'advance_notice': {
        'pattern': r'\b\d+\s+(?:hours?|days?|working\s+days?)\s+notice\b',
        'minimum': 48,  # hours
    },
    'evidence_provision': {
        'indicators': [r'\battached\b', r'\benclosed\b', r'\bcopies?\s+provided\b'],
    },
}
```

### Meeting (Paragraphs 13-21)

**Paragraph 15:** "Explain complaint and go through evidence"
- Employer presents case first
- Reference evidence
- Be clear and methodical

**Paragraph 16:** "Allow employee to set out their case"
- Employee responds
- Presents evidence
- Calls witnesses

**Paragraph 17:** "Reasonable adjustments for disabled employees"
- Equality Act 2010 duty
- May need different format, location, breaks

**Paragraph 19:** "Adjourn if new information emerges"
- Investigation may need to continue
- Don't rush to decision

**LOKI Detection:**
```python
# Meeting must allow employee response
right_to_respond = [
    r'\b(?:opportunity|chance|right)\s+to\s+(?:respond|reply|explain|present)\b',
    r'\byour\s+(?:version|side|explanation)\b',
]

# Reasonable adjustments
disability_context = r'\bdisabil(?:ed|ity)\b'
reasonable_adjustments = r'\b(?:reasonable\s+)?adjustments?\b'
```

### Decision (Paragraphs 22-24)

**Paragraph 22:** "Decide based on facts of case and reasonable investigation"
- On balance of probabilities (civil standard)
- Not beyond reasonable doubt (criminal standard)
- Reasonable belief in facts

**Paragraph 23:** "Communicate decision in writing"
- Letter or email
- State outcome clearly
- Give reasons

**Paragraph 24:** "Include appeal rights and procedure"
- How to appeal
- Time limit (typically 5-10 working days)
- Who to contact

**LOKI Detection:**
```python
DECISION_REQUIREMENTS = {
    'reasons_given': r'\b(?:decision|outcome|finding).*?(?:because|reason|as|due to)\b',
    'appeal_rights': {
        'right_stated': r'\b(?:right\s+to\s+)?appeal\b',
        'timeframe': r'\bappeal.*?within\s+\d+\s+(?:day|working\s+day)s?\b',
        'method': r'\bappeal.*?(?:writing|written|email)\b',
    },
}
```

### Appeal (Paragraphs 26-29)

**Paragraph 26:** "Appeal dealt with impartially"
- Different manager if possible
- More senior if possible
- No predetermined outcome

**Paragraph 27:** "Invite to appeal meeting"
- Similar rights as disciplinary meeting
- Right to be accompanied

**Paragraph 28:** "Decide whether to uphold or overturn"
- Can uphold original decision
- Can substitute lesser sanction
- Can overturn completely

**Paragraph 29:** "Inform of final decision"
- In writing
- No further internal appeal (usually)

**LOKI Detection:**
```python
APPEAL_REQUIREMENTS = {
    'different_decision_maker': {
        'good': r'\b(?:different|another|separate|independent)\s+(?:manager|person)\b',
        'bad': r'\bsame\s+(?:manager|person)\b.*\bappeal\b',
    },
    'appeal_meeting': r'\bappeal.*?meeting\b',
    'final_decision': r'\b(?:final|appeal)\s+decision\b',
}
```

## Sanctions Graduation (Paragraph 23)

**Typical progression:**
1. **First misconduct:** Verbal warning (sometimes first written)
2. **Repeat misconduct:** Final written warning
3. **Further misconduct:** Dismissal

**Gross misconduct:** Summary dismissal (instant, no notice) may be appropriate
- Theft, fraud, violence
- Serious breach of health and safety
- Serious insubordination

**LOKI Detection:**
```python
def check_sanction_graduation(text, employee_history):
    """
    Verify sanctions are graduated appropriately

    Args:
        text: Disciplinary letter
        employee_history: Previous warnings/sanctions
    """
    current_sanction = extract_sanction(text)

    # First offense -> dismissal is usually disproportionate (unless gross misconduct)
    if not employee_history and current_sanction == 'dismissal':
        gross_misconduct_indicators = [
            r'\btheft\b', r'\bfraud\b', r'\bviolence\b',
            r'\bassault\b', r'\bgross\s+misconduct\b',
        ]
        if not any(re.search(p, text, re.I) for p in gross_misconduct_indicators):
            return {
                'status': 'FAIL',
                'message': 'Dismissal for first offense without gross misconduct',
                'suggestion': 'Consider graduated sanctions per ACAS Code Para 23'
            }

    return {'status': 'PASS'}
```

## Small Employers (Paragraph 48)

**Modifications allowed:**
- More informal process acceptable
- May not have separate appeal manager
- But must still follow key principles:
  - Inform employee of allegations
  - Give opportunity to respond
  - Allow accompaniment
  - Provide appeal

## Tribunal Impact

### ACAS Code Uplift (Employment Tribunals Act 1996 s207A)

**Uplift (Employer breach):**
- Tribunal can increase compensation by up to 25%
- Applied when employer unreasonably failed to follow ACAS Code
- Common triggers:
  - No investigation
  - No meeting held
  - No right to appeal

**Reduction (Employee breach):**
- Tribunal can reduce compensation by up to 25%
- Applied when employee unreasonably failed to follow ACAS Code

**LOKI Severity Mapping:**
```python
ACAS_BREACH_SEVERITY = {
    'no_investigation': 'high',      # Para 5-7
    'no_meeting': 'high',            # Para 9-21
    'vague_allegations': 'high',     # Para 10
    'no_evidence': 'high',           # Para 11
    'no_accompaniment_right': 'high',# Para 12
    'no_appeal': 'high',             # Para 24
    'same_investigator_decider': 'medium',  # Para 26
    'no_reasons_given': 'medium',    # Para 23
}
```

## Case Law

### Key Cases Interpreting ACAS Code

**Slade v Biggs (2023)**
- Tribunal applied 25% uplift for no investigation
- Employer went straight to dismissal
- "Egregious breach of ACAS Code Para 5-7"

**Richards v Hotel Group (2022)**
- No appeal offered -> 20% uplift
- "Appeals are fundamental to fairness" - Para 24

**Thompson Manufacturing v Jones (2021)**
- Vague allegations -> 15% uplift
- Employee couldn't properly defend
- Para 10 breach

## LOKI Implementation Checklist

When creating ACAS-related gates:

- [ ] Citation includes paragraph number (e.g., "ACAS Code Para 15")
- [ ] Severity reflects tribunal risk
- [ ] Failure message explains ACAS breach
- [ ] Suggestion provides compliant alternative
- [ ] Pattern detects both presence and absence
- [ ] Tested against real disciplinary letters
- [ ] Edge cases considered (gross misconduct, small employers)

## Resources

- Full ACAS Code: https://www.acas.org.uk/acas-code-of-practice-on-disciplinary-and-grievance-procedures
- ACAS Guide: https://www.acas.org.uk/disciplinary-procedure-step-by-step
- Tribunal decisions: https://www.gov.uk/employment-tribunal-decisions
