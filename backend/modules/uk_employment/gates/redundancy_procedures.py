import re


class RedundancyProceduresGate:
    """
    Redundancy and TUPE Compliance - 2025 Standards
    Covers: Consultation, selection criteria, payments, TUPE transfers
    """
    def __init__(self):
        self.name = "redundancy_procedures"
        self.severity = "critical"
        self.legal_source = "Employment Rights Act 1996 s.135-181, TULRCA 1992 s.188, TUPE 2006"

    def _is_relevant(self, text):
        """Check if document relates to redundancy or TUPE"""
        text_lower = text.lower()
        keywords = [
            'redundanc', 'redundant', 'restructur', 'reorganis', 'reorganiz',
            'dismissal', 'termination', 'layoff', 'retrenchment',
            'tupe', 'transfer of undertaking', 'business transfer',
            'consultation', 'collective consultation', 'pool',
            'selection criteria', 'redundancy pay'
        ]
        return any(kw in text_lower for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not relate to redundancy or TUPE',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()
        spans = []
        issues = []
        warnings = []

        # 1. CONSULTATION REQUIREMENTS
        consultation_patterns = [
            r'consultation',
            r'consult\s+with',
            r'(?:discuss|meet)\s+with\s+(?:employees|staff|workers|representatives)',
            r'collective\s+consultation'
        ]

        has_consultation = any(re.search(p, text, re.IGNORECASE) for p in consultation_patterns)

        # Check for collective consultation thresholds
        collective_patterns = [
            r'20\s+or\s+more\s+(?:employees|redundancies)',
            r'(?:within\s+)?(?:90|ninety)\s+days?',
            r'(?:45|forty[\s-]five)\s+days?\s+(?:notice|consultation)',
            r'(?:30|thirty)\s+days?\s+(?:notice|consultation)'
        ]

        has_collective_threshold = any(re.search(p, text, re.IGNORECASE) for p in collective_patterns)

        # Check for 20+ redundancies in 90 days (collective consultation required)
        large_redundancy_match = re.search(r'(\d+)\s+(?:employees|redundancies|dismissals)', text, re.IGNORECASE)
        if large_redundancy_match:
            number = int(large_redundancy_match.group(1))
            if number >= 20 and not has_collective_threshold:
                issues.append('CRITICAL: 20+ redundancies requires collective consultation (45 days for 100+, 30 days for 20-99)')

        if has_consultation:
            # Check for individual consultation mention
            individual_patterns = [
                r'individual\s+consultation',
                r'one[\s-]to[\s-]one\s+(?:meeting|consultation)',
                r'(?:meet|consult)\s+(?:with\s+)?(?:each|every)\s+(?:employee|affected\s+(?:employee|worker))',
                r'personal\s+consultation'
            ]

            has_individual = any(re.search(p, text, re.IGNORECASE) for p in individual_patterns)
            if not has_individual:
                warnings.append('Should include individual consultation with each affected employee')

            # Check for consultation information requirements
            info_requirements = {
                'reasons': r'(?:reason|rationale|why|cause).*(?:for|of)\s+(?:the\s+)?redundanc',
                'numbers': r'(?:number|how\s+many).*(?:employees|affected|at\s+risk)',
                'selection': r'selection\s+(?:criteria|process|method)',
                'timing': r'(?:timescale|timeline|when|proposed\s+date)',
                'method': r'(?:method|process|procedure)\s+(?:of|for)\s+(?:dismissal|redundancy)'
            }

            missing_info = []
            for item, pattern in info_requirements.items():
                if not re.search(pattern, text, re.IGNORECASE):
                    missing_info.append(item)

            if missing_info and len(missing_info) >= 3:
                warnings.append(f'Consultation should cover: reasons, numbers affected, selection criteria, timing, and dismissal method')

            # Check for meaningful consultation (not just notification)
            meaningful_patterns = [
                r'(?:consider|take\s+into\s+account|listen\s+to)\s+(?:views|feedback|representations|comments)',
                r'opportunity\s+to\s+(?:respond|comment|make\s+representations)',
                r'(?:discuss|explore)\s+(?:alternatives|options)',
                r'ways\s+to\s+avoid\s+redundanc'
            ]

            has_meaningful = any(re.search(p, text, re.IGNORECASE) for p in meaningful_patterns)
            if not has_meaningful:
                warnings.append('Consultation must be meaningful - consider views and explore alternatives to redundancy')

        else:
            # No consultation mentioned at all
            warnings.append('Redundancy process must include consultation with affected employees')

        # 2. SELECTION CRITERIA
        selection_patterns = [
            r'selection\s+(?:criteria|method|process|procedure)',
            r'(?:criteria|basis)\s+(?:for|used\s+to)\s+select',
            r'(?:how|method\s+of)\s+select(?:ing|ion)',
            r'matrix|scoring\s+(?:system|method)'
        ]

        has_selection = any(re.search(p, text, re.IGNORECASE) for p in selection_patterns)

        if has_selection:
            # Check for objective criteria
            objective_criteria = [
                r'(?:skills?|qualifications?|experience|competenc)',
                r'performance\s+(?:record|appraisal|review)',
                r'attendance\s+(?:record|history)',
                r'disciplinary\s+(?:record|history)',
                r'length\s+of\s+service',
                r'(?:last\s+in|LIFO)',
                r'redundancy\s+points?\s+(?:system|matrix|score)'
            ]

            has_objective = any(re.search(p, text, re.IGNORECASE) for p in objective_criteria)
            if not has_objective:
                warnings.append('Selection criteria should be objective and measurable (e.g., skills, performance, attendance)')

            # Check for prohibited criteria
            prohibited_patterns = [
                r'(?:age|older|younger|senior)',
                r'(?:pregnant|pregnancy|maternity|paternity)',
                r'(?:part[\s-]time|full[\s-]time)\s+(?:status|workers)',
                r'(?:union|trade\s+union)\s+(?:member|activity)',
                r'(?:disability|disabled)',
                r'(?:race|religion|belief|sex|gender|sexual\s+orientation)'
            ]

            prohibited_found = []
            for pattern in prohibited_patterns:
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
                if matches:
                    # Context check - if mentioned as "not discriminatory" it's OK
                    for m in matches:
                        context_start = max(0, m.start() - 50)
                        context = text[context_start:m.end() + 50].lower()
                        if not any(phrase in context for phrase in ['not', 'without', 'regardless of', 'irrespective of']):
                            prohibited_found.append(m.group())
                            spans.append({
                                'type': 'prohibited_selection_criterion',
                                'start': m.start(),
                                'end': m.end(),
                                'text': m.group(),
                                'severity': 'critical'
                            })

            if prohibited_found:
                issues.append('CRITICAL: Selection criteria must not discriminate based on protected characteristics')

            # Check for pooling
            pool_patterns = [
                r'redundancy\s+pool',
                r'pool\s+(?:of\s+)?(?:employees|workers|staff)',
                r'(?:identified|defined|selected)\s+(?:the\s+)?pool',
                r'who\s+(?:is|will\s+be)\s+at\s+risk'
            ]

            has_pool = any(re.search(p, text, re.IGNORECASE) for p in pool_patterns)
            if not has_pool:
                warnings.append('Should define redundancy pool (who is at risk) with clear, objective rationale')

        else:
            # No selection criteria mentioned
            warnings.append('Must establish fair and objective selection criteria')

        # 3. REDUNDANCY PAYMENTS
        payment_patterns = [
            r'redundancy\s+(?:pay|payment|compensation)',
            r'statutory\s+redundancy\s+pay',
            r'enhanced\s+redundancy',
            r'severance\s+(?:pay|payment|package)',
            r'ex[\s-]gratia'
        ]

        has_payment = any(re.search(p, text, re.IGNORECASE) for p in payment_patterns)

        if has_payment:
            # Check for statutory redundancy pay calculation
            statutory_calc_patterns = [
                r'(?:0\.5|half|½)\s+(?:week|weeks?).*(?:age|under)\s+22',
                r'(?:1|one)\s+(?:week|weeks?).*(?:age|22\s+to\s+41)',
                r'(?:1\.5|1\s+½|one\s+and\s+a\s+half)\s+(?:week|weeks?).*(?:age|41\s+(?:and\s+)?over)',
                r'statutory\s+redundancy\s+pay\s+(?:calculation|formula)',
                r'£\d+\s+(?:per\s+)?week.*cap|maximum\s+(?:of\s+)?£\d+'
            ]

            has_calc = any(re.search(p, text, re.IGNORECASE) for p in statutory_calc_patterns)
            if not has_calc:
                warnings.append('Should explain redundancy pay calculation (0.5 week <22yrs, 1 week 22-40yrs, 1.5 weeks 41+)')

            # Check for 2-year qualifying service mention
            qualifying_patterns = [
                r'(?:2|two)\s+years?\s+(?:continuous\s+)?(?:service|employment)',
                r'qualify(?:ing)?.*(?:2|two)\s+years?',
                r'(?:worked\s+for|been\s+employed).*(?:2|two)\s+years?'
            ]

            has_qualifying = any(re.search(p, text, re.IGNORECASE) for p in qualifying_patterns)
            if not has_qualifying:
                warnings.append('Should reference 2-year qualifying period for statutory redundancy pay')

            # Check for enhanced/contractual redundancy
            enhanced_patterns = [
                r'enhanced\s+redundancy',
                r'(?:above|more\s+than|exceeds?)\s+statutory',
                r'contractual\s+redundancy',
                r'(?:\d+)\s+(?:weeks?|months?)\s+(?:per\s+year|for\s+each\s+year)'
            ]

            has_enhanced = any(re.search(p, text, re.IGNORECASE) for p in enhanced_patterns)
            # Enhanced is optional but good practice

            # Check for notice pay and payment in lieu
            notice_pay_patterns = [
                r'notice\s+pay',
                r'payment\s+in\s+lieu\s+of\s+notice',
                r'PILON',
                r'(?:pay|paid)\s+during\s+notice\s+period'
            ]

            has_notice_pay = any(re.search(p, text, re.IGNORECASE) for p in notice_pay_patterns)
            # Good to clarify notice pay separate from redundancy pay

        # 4. ALTERNATIVE EMPLOYMENT / MITIGATION
        alternative_patterns = [
            r'alternative\s+(?:employment|role|position|work)',
            r'suitable\s+(?:alternative\s+)?(?:employment|role|position)',
            r'redeployment',
            r'vacancy|vacancies',
            r'trial\s+period'
        ]

        has_alternative = any(re.search(p, text, re.IGNORECASE) for p in alternative_patterns)

        if has_alternative:
            # Check for trial period (statutory 4 weeks)
            trial_patterns = [
                r'(?:4|four)\s+weeks?\s+trial',
                r'trial\s+period\s+of\s+(?:4|four)\s+weeks?',
                r'statutory\s+trial\s+period'
            ]

            has_trial = any(re.search(p, text, re.IGNORECASE) for p in trial_patterns)
            if has_trial:
                # Good - trial period mentioned
                pass

        else:
            warnings.append('Should consider and offer suitable alternative employment if available')

        # 5. APPEALS PROCESS
        appeal_patterns = [
            r'appeal',
            r'(?:right\s+to\s+)?challenge\s+(?:the\s+)?decision',
            r'review\s+(?:of\s+)?(?:the\s+)?(?:decision|selection)',
            r'grievance'
        ]

        has_appeal = any(re.search(p, text, re.IGNORECASE) for p in appeal_patterns)

        if has_appeal:
            # Check for appeal timeframe
            appeal_time_patterns = [
                r'(?:within\s+)?(\d+)\s+(?:days?|weeks?|working\s+days?).*appeal',
                r'appeal.*(?:within\s+)?(\d+)\s+(?:days?|weeks?)'
            ]

            has_appeal_time = any(re.search(p, text, re.IGNORECASE) for p in appeal_time_patterns)
            if not has_appeal_time:
                warnings.append('Appeal process should specify timeframe (typically 5-10 working days)')

        else:
            warnings.append('Should include right to appeal redundancy decision')

        # 6. TUPE (Transfer of Undertakings) - if mentioned
        tupe_patterns = [
            r'\bTUPE\b',
            r'transfer\s+of\s+undertakings?',
            r'business\s+transfer',
            r'service\s+provision\s+change'
        ]

        has_tupe = any(re.search(p, text, re.IGNORECASE) for p in tupe_patterns)

        if has_tupe:
            # Check for automatic transfer of employment
            transfer_patterns = [
                r'employment\s+(?:will\s+)?(?:transfer|transfers)',
                r'(?:employees|staff)\s+(?:will\s+)?(?:transfer|move)\s+(?:to|with)',
                r'automatic\s+transfer',
                r'continuity\s+of\s+employment'
            ]

            has_transfer_mention = any(re.search(p, text, re.IGNORECASE) for p in transfer_patterns)
            if not has_transfer_mention:
                warnings.append('TUPE transfers: employment contracts transfer automatically to new employer')

            # Check for protection of terms
            protection_patterns = [
                r'terms\s+and\s+conditions\s+(?:protected|maintained|preserved)',
                r'same\s+terms',
                r'no\s+(?:less\s+)?favourable\s+terms',
                r'(?:cannot|must\s+not)\s+(?:worsen|reduce|diminish)\s+terms'
            ]

            has_protection = any(re.search(p, text, re.IGNORECASE) for p in protection_patterns)
            if not has_protection:
                warnings.append('TUPE: terms and conditions are protected - cannot be worsened due to transfer')

            # Check for consultation on TUPE transfer
            tupe_consultation_patterns = [
                r'(?:inform|notify|consult).*(?:about|regarding)\s+(?:the\s+)?transfer',
                r'transfer\s+information',
                r'employee\s+liability\s+information',
                r'ELI'
            ]

            has_tupe_consultation = any(re.search(p, text, re.IGNORECASE) for p in tupe_consultation_patterns)
            if not has_tupe_consultation:
                warnings.append('TUPE: must inform and consult employees about transfer')

            # Check for ETO reason (Economic, Technical, Organisational)
            eto_patterns = [
                r'\bETO\b',
                r'economic,?\s+technical,?\s+(?:or\s+)?organisational',
                r'entailing\s+changes\s+(?:in|to)\s+(?:the\s+)?workforce'
            ]

            has_eto = any(re.search(p, text, re.IGNORECASE) for p in eto_patterns)
            # ETO is exception to TUPE protection - if mentioned, should be carefully justified

            if has_eto:
                warnings.append('ETO reason for changes must be genuine economic, technical or organisational reason entailing workforce changes')

        # 7. NOTICE PERIODS
        notice_patterns = [
            r'notice\s+period',
            r'(?:statutory|minimum)\s+notice',
            r'(?:\d+)\s+(?:weeks?|months?)\s+notice'
        ]

        has_notice = any(re.search(p, text, re.IGNORECASE) for p in notice_patterns)

        if has_notice:
            # Check for statutory minimum compliance
            statutory_notice_patterns = [
                r'(?:1|one)\s+week\s+(?:per|for\s+each)\s+year',
                r'statutory\s+(?:minimum\s+)?notice',
                r'(?:up\s+to\s+)?(?:12|twelve)\s+weeks?'
            ]

            has_statutory = any(re.search(p, text, re.IGNORECASE) for p in statutory_notice_patterns)
            if not has_statutory:
                warnings.append('Notice period should reference statutory minimum (1 week per year, max 12 weeks)')

        # Determine overall status
        if issues:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Redundancy process has serious compliance issues',
                'legal_source': self.legal_source,
                'suggestion': 'Address critical issues: ' + '; '.join(issues[:2]),
                'spans': spans,
                'details': issues + warnings
            }

        if len(warnings) >= 3:
            return {
                'status': 'WARNING',
                'severity': 'high',
                'message': 'Redundancy process requires improvements',
                'legal_source': self.legal_source,
                'suggestion': 'Review: ' + '; '.join(warnings[:3]),
                'spans': spans,
                'details': warnings
            }

        if warnings:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Minor improvements recommended for redundancy process',
                'legal_source': self.legal_source,
                'suggestion': '; '.join(warnings[:2]),
                'spans': spans,
                'details': warnings
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Redundancy procedures appear compliant',
            'legal_source': self.legal_source,
            'spans': spans
        }


# Test cases
def test_redundancy_procedures_gate():
    gate = RedundancyProceduresGate()

    # Test 1: Large redundancy without collective consultation
    test1 = """
    REDUNDANCY NOTICE

    Due to business restructuring, we are making 25 employees redundant.
    Selection will be based on performance reviews.
    Affected employees will receive statutory redundancy pay.
    """
    result1 = gate.check(test1, "redundancy_notice")
    assert result1['status'] == 'FAIL'
    assert 'collective consultation' in str(result1).lower()

    # Test 2: Discriminatory selection criteria
    test2 = """
    REDUNDANCY SELECTION CRITERIA

    The following criteria will be used:
    - Age (older workers will be selected first)
    - Performance rating
    - Attendance record
    """
    result2 = gate.check(test2, "redundancy_procedure")
    assert result2['status'] == 'FAIL'
    assert 'discriminat' in str(result2).lower() or 'prohibited' in str(result2).lower()

    # Test 3: Compliant redundancy process
    test3 = """
    REDUNDANCY CONSULTATION

    We will consult with all affected employees individually for at least 30 days.

    Selection Criteria:
    - Skills and qualifications
    - Performance record
    - Attendance history
    - Length of service

    Redundancy Pay:
    - Statutory redundancy pay (0.5 weeks <22, 1 week 22-40, 1.5 weeks 41+)
    - 2 years continuous service required
    - Notice pay as per contract

    We will consider alternative employment opportunities.
    You have the right to appeal within 10 working days.
    """
    result3 = gate.check(test3, "redundancy_procedure")
    assert result3['status'] in ['PASS', 'WARNING']

    # Test 4: TUPE transfer
    test4 = """
    TUPE TRANSFER NOTIFICATION

    Your employment will transfer automatically to NewCo Ltd under TUPE regulations.
    All terms and conditions will be protected and cannot be worsened.
    We will consult with all affected employees about the transfer.
    Employee Liability Information will be provided to the new employer.
    """
    result4 = gate.check(test4, "tupe_notice")
    assert result4['status'] in ['PASS', 'WARNING']

    print("All redundancy procedures gate tests passed!")


if __name__ == "__main__":
    test_redundancy_procedures_gate()
