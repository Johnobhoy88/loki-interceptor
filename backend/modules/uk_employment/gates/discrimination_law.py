import re


class DiscriminationLawGate:
    """
    Equality Act 2010 - Protected Characteristics & Discrimination
    Covers: 9 protected characteristics, direct/indirect discrimination, harassment, victimisation, reasonable adjustments
    """
    def __init__(self):
        self.name = "discrimination_law"
        self.severity = "critical"
        self.legal_source = "Equality Act 2010, Public Sector Equality Duty 2011"

        # Nine protected characteristics
        self.protected_characteristics = {
            'age': r'\b(?:age|older|younger|elderly|senior)\b',
            'disability': r'\b(?:disab(?:led|ility)|impairment|wheelchair|medical\s+condition)\b',
            'gender_reassignment': r'\b(?:trans(?:gender|sexual)?|gender\s+reassignment|gender\s+identity)\b',
            'marriage_civil_partnership': r'\b(?:marr(?:ied|iage)|civil\s+partnership|spouse|partner)\b',
            'pregnancy_maternity': r'\b(?:pregnan(?:t|cy)|maternity|expecting|mother|maternal)\b',
            'race': r'\b(?:race|racial|ethnic|nationality|national\s+origin|color|colour)\b',
            'religion_belief': r'\b(?:religion|religious|belief|faith|atheist|christian|muslim|jewish|hindu|sikh)\b',
            'sex': r'\b(?:sex|gender|male|female|man|woman|men|women)\b',
            'sexual_orientation': r'\b(?:sexual\s+orientation|gay|lesbian|heterosexual|bisexual|homosexual)\b'
        }

    def _is_relevant(self, text):
        """Check if document relates to discrimination or equality"""
        text_lower = text.lower()
        keywords = [
            'discriminat', 'equal', 'diversity', 'inclusion', 'protected characteristic',
            'harassment', 'victimisation', 'victimization', 'reasonable adjustment',
            'disability', 'race', 'gender', 'age', 'religion', 'sexual orientation',
            'pregnancy', 'maternity', 'transgender', 'marriage'
        ]
        return any(kw in text_lower for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not relate to discrimination or equality',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()
        spans = []
        issues = []
        warnings = []

        # 1. DETECT MENTIONS OF PROTECTED CHARACTERISTICS
        characteristics_found = []
        for char_name, pattern in self.protected_characteristics.items():
            if re.search(pattern, text, re.IGNORECASE):
                characteristics_found.append(char_name.replace('_', ' '))

        # 2. DIRECT DISCRIMINATION - Treating someone less favourably because of protected characteristic
        direct_discrimination_patterns = [
            r'(?:only|must\s+be|should\s+be|prefer(?:ence)?|required\s+to\s+be)\s+(?:young|male|female|british|christian|able[\s-]bodied)',
            r'no\s+(?:women|men|disabled|over\s+\d+|muslims|gay)',
            r'(?:women|men|disabled|older\s+workers)\s+(?:not\s+suitable|cannot|will\s+not\s+be\s+considered)',
            r'because\s+(?:of\s+)?(?:your|their|his|her)\s+(?:age|disability|race|gender|religion|sexual\s+orientation)',
            r'due\s+to\s+(?:your|their|his|her)\s+(?:age|disability|pregnancy|race)'
        ]

        for pattern in direct_discrimination_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                for m in matches:
                    spans.append({
                        'type': 'potential_direct_discrimination',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'critical'
                    })
                issues.append('CRITICAL: Language suggests potential direct discrimination based on protected characteristic')

        # 3. INDIRECT DISCRIMINATION - Applying provision, criterion or practice that disadvantages
        indirect_patterns = [
            r'(?:must|required\s+to|need\s+to)\s+be\s+(?:available|flexible)\s+(?:24/7|at\s+all\s+times|evenings?|weekends?)',
            r'(?:full[\s-]time\s+only|no\s+part[\s-]time)',
            r'minimum\s+height',
            r'(?:clean[\s-]shaven|no\s+(?:beard|facial\s+hair))',
            r'english\s+(?:as\s+)?(?:first|native)\s+language',
            r'(?:recent|new|fresh)\s+graduate'
        ]

        for pattern in indirect_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                for m in matches:
                    # Check if justified
                    context_start = max(0, m.start() - 100)
                    context_end = min(len(text), m.end() + 100)
                    context = text[context_start:context_end].lower()

                    justified = any(phrase in context for phrase in [
                        'justified', 'proportionate', 'legitimate aim', 'business necessity',
                        'genuine occupational requirement', 'GOR', 'essential'
                    ])

                    if not justified:
                        spans.append({
                            'type': 'potential_indirect_discrimination',
                            'start': m.start(),
                            'end': m.end(),
                            'text': m.group(),
                            'severity': 'high'
                        })
                        warnings.append('Requirement may indirectly discriminate - ensure it is objectively justified and proportionate')

        # 4. HARASSMENT - Unwanted conduct related to protected characteristic
        harassment_patterns = [
            r'harassment',
            r'unwanted\s+(?:conduct|behaviour|attention|advance)',
            r'hostile\s+(?:environment|atmosphere)',
            r'intimidat(?:ing|ion)',
            r'offensive\s+(?:language|behavior|behaviour|comments)',
            r'bullying',
            r'derogatory\s+(?:comments|remarks)',
            r'sexual\s+harassment'
        ]

        has_harassment_ref = any(re.search(p, text, re.IGNORECASE) for p in harassment_patterns)

        if has_harassment_ref:
            # Check for policy against harassment
            policy_patterns = [
                r'(?:zero\s+tolerance|will\s+not\s+tolerate|prohibit)',
                r'harassment\s+(?:policy|procedure)',
                r'(?:report|complaint)\s+(?:procedure|process)',
                r'(?:investigation|disciplinary\s+action)'
            ]

            has_policy = any(re.search(p, text, re.IGNORECASE) for p in policy_patterns)
            if not has_policy:
                warnings.append('Harassment mentioned - should include clear policy and reporting procedures')

            # Check for three types of harassment
            harassment_types = {
                'conduct_related': r'(?:related\s+to|because\s+of)\s+(?:protected\s+characteristic|age|disability|race|gender)',
                'sexual': r'sexual\s+(?:harassment|nature)',
                'less_favourable_treatment': r'treated\s+(?:less\s+)?favourably.*rejected.*(?:harassment|unwanted)'
            }

            # Good practice to cover all three types

        # 5. VICTIMISATION - Treating someone badly because they complained
        victimisation_patterns = [
            r'victimis[ae]tion',
            r'(?:retaliat(?:ion|e)|retribut(?:ion|ive))',
            r'(?:because|due\s+to).*(?:complained|raised\s+(?:a\s+)?(?:concern|grievance|complaint))',
            r'detriment.*(?:complaint|allegation|proceedings)'
        ]

        has_victimisation = any(re.search(p, text, re.IGNORECASE) for p in victimisation_patterns)

        if has_victimisation:
            # Check for protection statement
            protection_patterns = [
                r'(?:protected|will\s+not\s+suffer|no\s+detriment)',
                r'safe\s+to\s+(?:raise|report|complain)',
                r'without\s+fear\s+of\s+(?:reprisal|retaliation)'
            ]

            has_protection = any(re.search(p, text, re.IGNORECASE) for p in protection_patterns)
            if not has_protection:
                warnings.append('Should clarify that employees are protected from victimisation for raising concerns')

        # 6. REASONABLE ADJUSTMENTS (Disability-specific duty)
        adjustment_patterns = [
            r'reasonable\s+adjustment',
            r'(?:adapt|modify|adjust).*(?:workplace|role|duties|hours)',
            r'disability\s+accommodat',
            r'equipment\s+(?:or\s+)?(?:aids|support)',
            r'workplace\s+modification'
        ]

        has_adjustments = any(re.search(p, text, re.IGNORECASE) for p in adjustment_patterns)

        if 'disability' in characteristics_found and not has_adjustments:
            warnings.append('Disability mentioned - should reference duty to make reasonable adjustments')

        if has_adjustments:
            # Check for examples of adjustments
            examples_patterns = [
                r'(?:for\s+example|such\s+as|including)',
                r'flexible\s+working',
                r'special\s+equipment',
                r'modified\s+duties',
                r'additional\s+(?:breaks|support|training)'
            ]

            has_examples = any(re.search(p, text, re.IGNORECASE) for p in examples_patterns)
            if not has_examples:
                warnings.append('Good practice to provide examples of reasonable adjustments')

            # Check for interactive process
            interactive_patterns = [
                r'discuss\s+(?:with|your\s+needs)',
                r'individual\s+(?:assessment|basis)',
                r'consultation',
                r'work\s+(?:with|together)'
            ]

            has_interactive = any(re.search(p, text, re.IGNORECASE) for p in interactive_patterns)
            if not has_interactive:
                warnings.append('Reasonable adjustments should involve discussion with disabled person')

        # 7. POSITIVE ACTION (Permitted under Equality Act)
        positive_action_patterns = [
            r'positive\s+action',
            r'(?:under[\s-]?represented|disadvantaged)\s+group',
            r'(?:encourag|support).*(?:applications?\s+from|diverse)',
            r'proportionate\s+means'
        ]

        has_positive_action = any(re.search(p, text, re.IGNORECASE) for p in positive_action_patterns)

        if has_positive_action:
            # Check not positive discrimination (illegal)
            discrimination_indicators = [
                r'(?:only|exclusively|must\s+be)',
                r'guarantee',
                r'automatically\s+(?:selected|appointed)'
            ]

            has_discrimination_language = any(re.search(p, text, re.IGNORECASE) for p in discrimination_indicators)
            if has_discrimination_language:
                warnings.append('Positive action must not become positive discrimination - merit must remain the deciding factor')

        # 8. OCCUPATIONAL REQUIREMENTS (GOR - Genuine Occupational Requirement)
        gor_patterns = [
            r'genuine\s+occupational\s+(?:requirement|qualification)',
            r'\bGOR\b',
            r'occupational\s+requirement',
            r'essential\s+(?:for\s+the\s+)?(?:nature|purposes?)\s+of\s+the\s+(?:job|role|work)'
        ]

        has_gor = any(re.search(p, text, re.IGNORECASE) for p in gor_patterns)

        if has_gor:
            # Check for proportionality and legitimate aim
            justification_patterns = [
                r'proportionate',
                r'legitimate\s+aim',
                r'strictly\s+necessary',
                r'essential\s+(?:to|for)',
                r'determining\s+factor'
            ]

            has_justification = any(re.search(p, text, re.IGNORECASE) for p in justification_patterns)
            if not has_justification:
                warnings.append('Genuine Occupational Requirement must be proportionate means of achieving legitimate aim')

        # 9. EQUAL PAY (Sex-specific)
        equal_pay_patterns = [
            r'equal\s+pay',
            r'gender\s+pay\s+gap',
            r'same\s+(?:pay|salary).*(?:work|role)',
            r'pay\s+(?:equality|parity|equity)'
        ]

        has_equal_pay = any(re.search(p, text, re.IGNORECASE) for p in equal_pay_patterns)

        if has_equal_pay:
            # Check for material factor defence if different pay mentioned
            material_factor_patterns = [
                r'material\s+factor',
                r'objectively\s+justif(?:ied|iable)',
                r'(?:legitimate|genuine)\s+reason',
                r'not\s+(?:due\s+to|because\s+of)\s+sex'
            ]

            pay_difference_patterns = [
                r'different\s+(?:pay|salary)',
                r'(?:higher|lower)\s+(?:pay|salary)',
                r'pay\s+(?:difference|disparity)'
            ]

            has_pay_difference = any(re.search(p, text, re.IGNORECASE) for p in pay_difference_patterns)
            has_justification = any(re.search(p, text, re.IGNORECASE) for p in material_factor_patterns)

            if has_pay_difference and not has_justification:
                warnings.append('Pay differences between sexes must be objectively justified by material factors')

        # 10. PREGNANCY AND MATERNITY PROTECTION
        if 'pregnancy_maternity' in characteristics_found:
            protection_patterns = [
                r'(?:protected|cannot\s+be\s+discriminated)',
                r'maternity\s+leave',
                r'risk\s+assessment',
                r'health\s+and\s+safety',
                r'right\s+to\s+return',
                r'(?:suspend|alternative\s+work)'
            ]

            has_pregnancy_protection = any(re.search(p, text, re.IGNORECASE) for p in protection_patterns)
            if not has_pregnancy_protection:
                warnings.append('Pregnancy/maternity mentioned - should reference protection rights and risk assessment')

        # 11. PUBLIC SECTOR EQUALITY DUTY (if public sector context)
        psed_patterns = [
            r'public\s+sector\s+equality\s+duty',
            r'\bPSED\b',
            r'due\s+regard',
            r'eliminate\s+discrimination',
            r'advance\s+equality\s+of\s+opportunity',
            r'foster\s+good\s+relations'
        ]

        has_psed = any(re.search(p, text, re.IGNORECASE) for p in psed_patterns)

        public_sector_indicators = [
            r'(?:local\s+)?(?:authority|council)',
            r'NHS',
            r'(?:government|public)\s+(?:body|sector|service)',
            r'statutory\s+(?:body|duty)'
        ]

        is_public_sector = any(re.search(p, text, re.IGNORECASE) for p in public_sector_indicators)

        if is_public_sector and not has_psed:
            warnings.append('Public sector bodies must have due regard to Public Sector Equality Duty')

        # 12. EQUALITY IMPACT ASSESSMENT
        eia_patterns = [
            r'equality\s+impact\s+assessment',
            r'\bEIA\b',
            r'(?:assess|consider)\s+(?:the\s+)?(?:equality\s+)?impact',
            r'protected\s+characteristics?\s+(?:assessment|analysis)'
        ]

        has_eia = any(re.search(p, text, re.IGNORECASE) for p in eia_patterns)

        # 13. TRAINING AND AWARENESS
        training_patterns = [
            r'(?:equality|diversity|discrimination|unconscious\s+bias)\s+training',
            r'awareness\s+(?:training|programme)',
            r'education.*(?:equality|diversity|inclusion)'
        ]

        has_training = any(re.search(p, text, re.IGNORECASE) for p in training_patterns)

        # 14. MONITORING AND DATA
        monitoring_patterns = [
            r'monitor(?:ing)?.*(?:equality|diversity)',
            r'equality\s+data',
            r'workforce\s+(?:composition|demographics|data)',
            r'diversity\s+(?:metrics|statistics|reporting)'
        ]

        has_monitoring = any(re.search(p, text, re.IGNORECASE) for p in monitoring_patterns)

        # Determine overall status
        if issues:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Document contains potential unlawful discrimination',
                'legal_source': self.legal_source,
                'suggestion': 'URGENT: Remove discriminatory language. All employment decisions must be based on objective job-related criteria, not protected characteristics.',
                'spans': spans,
                'details': issues + warnings
            }

        if len(warnings) >= 4:
            return {
                'status': 'WARNING',
                'severity': 'high',
                'message': 'Equality and discrimination provisions need strengthening',
                'legal_source': self.legal_source,
                'suggestion': 'Key improvements needed: ' + '; '.join(warnings[:3]),
                'spans': spans,
                'details': warnings
            }

        if warnings:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Minor equality and discrimination improvements recommended',
                'legal_source': self.legal_source,
                'suggestion': '; '.join(warnings[:2]),
                'spans': spans,
                'details': warnings
            }

        if characteristics_found:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Equality and discrimination provisions appear compliant (characteristics mentioned: {", ".join(characteristics_found[:3])})',
                'legal_source': self.legal_source,
                'spans': spans
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'No obvious discrimination issues detected',
            'legal_source': self.legal_source,
            'spans': spans
        }


# Test cases
def test_discrimination_law_gate():
    gate = DiscriminationLawGate()

    # Test 1: Direct discrimination
    test1 = """
    JOB ADVERT

    We are looking for a young, energetic male candidate for this role.
    No women or disabled people will be considered.
    """
    result1 = gate.check(test1, "job_advert")
    assert result1['status'] == 'FAIL'
    assert 'direct discrimination' in str(result1).lower()

    # Test 2: Indirect discrimination not justified
    test2 = """
    ROLE REQUIREMENTS

    - Must be full-time only (no part-time)
    - Must be available evenings and weekends
    - Clean-shaven appearance required
    - Must be a recent graduate
    """
    result2 = gate.check(test2, "job_specification")
    assert result2['status'] == 'WARNING'

    # Test 3: Reasonable adjustments - compliant
    test3 = """
    DISABILITY POLICY

    We will make reasonable adjustments for disabled employees, such as:
    - Modified duties or flexible working
    - Special equipment or workplace adaptations
    - Additional breaks or support

    We will discuss your individual needs to determine appropriate adjustments.
    """
    result3 = gate.check(test3, "disability_policy")
    assert result3['status'] in ['PASS', 'WARNING']

    # Test 4: Harassment policy
    test4 = """
    HARASSMENT AND DISCRIMINATION POLICY

    We have zero tolerance for harassment related to any protected characteristic.

    Harassment includes unwanted conduct that violates dignity or creates
    an intimidating, hostile, degrading or offensive environment.

    Report any concerns to HR. You will be protected from victimisation
    for raising genuine complaints.
    """
    result4 = gate.check(test4, "harassment_policy")
    assert result4['status'] in ['PASS', 'WARNING']

    # Test 5: Equal pay
    test5 = """
    PAY POLICY

    We are committed to equal pay for equal work.
    Any pay differences are objectively justified by material factors
    such as experience, qualifications, and performance, not sex.
    """
    result5 = gate.check(test5, "pay_policy")
    assert result5['status'] in ['PASS', 'WARNING']

    print("All discrimination law gate tests passed!")


if __name__ == "__main__":
    test_discrimination_law_gate()
