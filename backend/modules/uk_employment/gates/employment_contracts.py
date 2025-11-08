import re


class EmploymentContractsGate:
    """
    Employment Rights Bill 2025 - Contract Terms Compliance
    Covers: Fixed-term, zero-hours, probation, notice periods, garden leave
    """
    def __init__(self):
        self.name = "employment_contracts"
        self.severity = "critical"
        self.legal_source = "Employment Rights Bill 2025, Employment Rights Act 1996 s.1"

    def _is_relevant(self, text):
        """Check if document relates to employment contracts"""
        text_lower = text.lower()
        keywords = [
            'employment contract', 'contract of employment', 'employment agreement',
            'zero hours', 'zero-hours', 'fixed term', 'fixed-term', 'probation',
            'notice period', 'garden leave', 'casual worker', 'employment terms',
            'statement of particulars', 'written statement'
        ]
        return any(kw in text_lower for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not relate to employment contracts',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()
        spans = []
        issues = []
        warnings = []

        # 1. ZERO-HOURS CONTRACTS - 2025 Regulations
        zero_hours_patterns = [
            r'zero[\s-]hours?\s+contract',
            r'casual\s+(?:worker|employment|contract)',
            r'no\s+guaranteed\s+hours',
            r'as\s+and\s+when\s+(?:required|needed)'
        ]

        has_zero_hours = any(re.search(p, text, re.IGNORECASE) for p in zero_hours_patterns)

        if has_zero_hours:
            # Check for prohibited exclusivity clauses (banned under 2025 reforms)
            exclusivity_patterns = [
                r'(?:not|shall\s+not|must\s+not|prohibited\s+from|forbidden\s+from)\s+(?:work|working|take|taking|accept|accepting)\s+(?:for|with)?\s*(?:other|another|any\s+other)\s+(?:employer|employment|job)',
                r'exclusive\s+(?:services|employment|engagement)',
                r'sole\s+(?:employer|employment)',
                r'no\s+(?:other|additional)\s+employment'
            ]

            has_exclusivity = False
            for pattern in exclusivity_patterns:
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
                if matches:
                    has_exclusivity = True
                    for m in matches:
                        spans.append({
                            'type': 'illegal_exclusivity_clause',
                            'start': m.start(),
                            'end': m.end(),
                            'text': m.group(),
                            'severity': 'critical'
                        })

            if has_exclusivity:
                issues.append('CRITICAL: Exclusivity clauses in zero-hours contracts are prohibited under Employment Rights Bill 2025')

            # Check for minimum hours guarantee (required under 2025 reforms)
            minimum_hours_patterns = [
                r'minimum\s+(?:guaranteed\s+)?hours',
                r'guaranteed\s+(?:\d+\s+)?hours',
                r'(?:at\s+least|minimum\s+of)\s+\d+\s+hours'
            ]

            has_min_hours = any(re.search(p, text, re.IGNORECASE) for p in minimum_hours_patterns)
            if not has_min_hours:
                warnings.append('Zero-hours contract should specify minimum hours guarantee (2025 requirement)')

            # Check for reasonable notice of shifts (2025 requirement)
            notice_shift_patterns = [
                r'(?:\d+\s+(?:days?|hours?|weeks?))\s+notice\s+(?:of|for)\s+(?:shifts?|work|assignment)',
                r'(?:shifts?|work)\s+(?:will\s+be\s+)?(?:notified|advised|confirmed)\s+(?:at\s+least\s+)?\d+',
                r'reasonable\s+notice\s+of\s+(?:shifts?|work)'
            ]

            has_shift_notice = any(re.search(p, text, re.IGNORECASE) for p in notice_shift_patterns)
            if not has_shift_notice:
                warnings.append('Must provide reasonable notice of shifts (minimum 4 days under 2025 reforms)')

        # 2. FIXED-TERM CONTRACTS
        fixed_term_patterns = [
            r'fixed[\s-]term',
            r'(?:contract|employment)\s+for\s+a\s+period\s+of',
            r'(?:contract|employment)\s+(?:ending|expiring|terminating)\s+on',
            r'temporary\s+contract'
        ]

        has_fixed_term = any(re.search(p, text, re.IGNORECASE) for p in fixed_term_patterns)

        if has_fixed_term:
            # Check for end date
            end_date_patterns = [
                r'(?:end|expiry|termination)\s+date[:\s]+(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'(?:until|ending|expiring)\s+(?:on\s+)?(?:\d{1,2}\s+\w+\s+\d{4})',
                r'(?:for\s+a\s+period\s+of|duration\s+of)\s+\d+\s+(?:months?|years?|weeks?)'
            ]

            has_end_date = any(re.search(p, text, re.IGNORECASE) for p in end_date_patterns)
            if not has_end_date:
                issues.append('Fixed-term contract must specify clear end date or duration')

            # Check for renewal terms
            renewal_patterns = [
                r'renew(?:al|ed)?',
                r'extend(?:ed|sion)?',
                r'continuation\s+(?:of|beyond)',
                r'subsequent\s+fixed[\s-]term'
            ]

            has_renewal_terms = any(re.search(p, text, re.IGNORECASE) for p in renewal_patterns)

            # Check for 4-year rule (automatic permanent status)
            four_year_patterns = [
                r'(?:4|four)\s+years?',
                r'permanent\s+(?:status|employment)\s+after',
                r'continuous\s+(?:fixed[\s-]term\s+)?contracts'
            ]

            has_four_year_rule = any(re.search(p, text, re.IGNORECASE) for p in four_year_patterns)
            if not has_four_year_rule and has_renewal_terms:
                warnings.append('Should reference 4-year rule: employees on successive fixed-term contracts become permanent')

        # 3. PROBATION PERIODS
        probation_patterns = [
            r'probation(?:ary)?\s+period',
            r'trial\s+period',
            r'initial\s+(?:\d+\s+)?(?:months?|weeks?)\s+(?:period|employment)'
        ]

        has_probation = any(re.search(p, text, re.IGNORECASE) for p in probation_patterns)

        if has_probation:
            # Check probation duration (max 6 months recommended)
            duration_match = re.search(r'(?:probation|trial)\s+(?:period\s+(?:of\s+)?)?(\d+)\s+(months?|weeks?)', text, re.IGNORECASE)
            if duration_match:
                duration = int(duration_match.group(1))
                unit = duration_match.group(2).lower()

                if 'month' in unit and duration > 6:
                    warnings.append(f'Probation period of {duration} months exceeds recommended maximum of 6 months')
                elif 'week' in unit and duration > 26:
                    warnings.append(f'Probation period of {duration} weeks exceeds recommended maximum of 26 weeks')

            # Check for review process
            review_patterns = [
                r'probation(?:ary)?\s+review',
                r'performance\s+review\s+(?:during|in)\s+probation',
                r'assessment\s+(?:during|at\s+end\s+of)\s+probation',
                r'probation\s+meeting'
            ]

            has_review = any(re.search(p, text, re.IGNORECASE) for p in review_patterns)
            if not has_review:
                warnings.append('Probation period should include review process and assessment criteria')

            # Check for extension clause
            extension_patterns = [
                r'(?:extend|extension\s+of)\s+probation',
                r'probation\s+(?:may\s+be\s+)?extended',
                r'further\s+probation(?:ary)?\s+period'
            ]

            has_extension = any(re.search(p, text, re.IGNORECASE) for p in extension_patterns)
            if has_extension:
                # Check for maximum extended duration
                max_extension_patterns = [
                    r'(?:maximum\s+)?(?:total\s+)?probation\s+(?:of\s+)?(?:up\s+to\s+)?(\d+)\s+(months?|weeks?)',
                    r'extended\s+(?:by\s+)?(?:up\s+to\s+)?(\d+)\s+(months?|weeks?)'
                ]

                has_max_extension = any(re.search(p, text, re.IGNORECASE) for p in max_extension_patterns)
                if not has_max_extension:
                    warnings.append('If probation can be extended, specify maximum total duration')

        # 4. NOTICE PERIODS
        notice_patterns = [
            r'notice\s+period',
            r'(?:give|provide|serve)\s+(?:\d+\s+)?(?:weeks?|months?)\s+(?:written\s+)?notice',
            r'terminate\s+(?:on|with)\s+(?:\d+\s+)?(?:weeks?|months?)\s+notice',
            r'termination\s+notice'
        ]

        has_notice = any(re.search(p, text, re.IGNORECASE) for p in notice_patterns)

        if has_notice:
            # Check for statutory minimum compliance
            notice_duration_patterns = [
                r'(?:employee\s+(?:must\s+)?(?:give|provide))\s+(\d+)\s+(weeks?|months?)\s+notice',
                r'(?:employer\s+(?:must\s+)?(?:give|provide))\s+(\d+)\s+(weeks?|months?)\s+notice',
                r'(?:notice\s+period\s+(?:of|is))\s+(\d+)\s+(weeks?|months?)'
            ]

            for pattern in notice_duration_patterns:
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
                for m in matches:
                    spans.append({
                        'type': 'notice_period_specified',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

            # Check for statutory minimum reference (1 week per year of service)
            statutory_patterns = [
                r'statutory\s+(?:minimum\s+)?notice',
                r'notice\s+(?:required\s+)?(?:by|under)\s+(?:law|statute|Employment\s+Rights\s+Act)',
                r'one\s+week\s+(?:for\s+)?(?:each|per)\s+year\s+(?:of\s+)?(?:service|employment)'
            ]

            has_statutory_ref = any(re.search(p, text, re.IGNORECASE) for p in statutory_patterns)
            if not has_statutory_ref:
                warnings.append('Should reference statutory minimum notice requirements (ERA 1996 s.86)')

            # Check for payment in lieu clause
            pil_patterns = [
                r'payment\s+in\s+lieu\s+(?:of\s+)?notice',
                r'PILON',
                r'pay\s+(?:in\s+)?lieu',
                r'(?:employer\s+)?may\s+(?:elect\s+to\s+)?pay.*instead\s+of\s+notice'
            ]

            has_pil = any(re.search(p, text, re.IGNORECASE) for p in pil_patterns)
            # Payment in lieu is optional but should be clear if mentioned

        # 5. GARDEN LEAVE
        garden_leave_patterns = [
            r'garden\s+leave',
            r'paid\s+leave\s+during\s+notice',
            r'(?:required\s+to\s+)?(?:stay\s+away|not\s+attend|remain\s+at\s+home)\s+(?:during|in)\s+notice',
            r'exclude.*from\s+(?:workplace|premises)\s+during\s+notice'
        ]

        has_garden_leave = any(re.search(p, text, re.IGNORECASE) for p in garden_leave_patterns)

        if has_garden_leave:
            # Check for continued pay confirmation
            pay_patterns = [
                r'(?:full\s+)?(?:salary|pay|remuneration)\s+(?:will\s+)?(?:be\s+)?(?:continue|paid|maintained)',
                r'(?:continue\s+to\s+)?(?:receive|be\s+paid)\s+(?:full\s+)?(?:salary|pay)',
                r'normal\s+(?:salary|pay|remuneration)\s+during'
            ]

            has_continued_pay = any(re.search(p, text, re.IGNORECASE) for p in pay_patterns)
            if not has_continued_pay:
                issues.append('Garden leave must confirm continued full pay and benefits')

            # Check for restrictions during garden leave
            restriction_patterns = [
                r'(?:not|shall\s+not|must\s+not)\s+(?:contact|communicate\s+with|approach)\s+(?:clients|customers|staff)',
                r'(?:not|shall\s+not|must\s+not)\s+(?:work\s+for|provide\s+services\s+to)\s+(?:any\s+)?(?:other|another)\s+employer',
                r'restrictive\s+covenants?\s+(?:apply|remain\s+in\s+force)',
                r'confidentiality\s+(?:obligations|duties)\s+(?:continue|remain)'
            ]

            has_restrictions = any(re.search(p, text, re.IGNORECASE) for p in restriction_patterns)
            # Note: Restrictions should be reasonable and clearly stated

            # Check for maximum garden leave period
            max_period_patterns = [
                r'garden\s+leave\s+(?:period\s+)?(?:of\s+)?(?:up\s+to\s+)?(\d+)\s+(months?|weeks?)',
                r'(?:up\s+to\s+)?(\d+)\s+(months?|weeks?)\s+garden\s+leave'
            ]

            has_max_period = any(re.search(p, text, re.IGNORECASE) for p in max_period_patterns)
            if not has_max_period:
                warnings.append('Should specify maximum garden leave duration (typically matches notice period)')

        # 6. WRITTEN STATEMENT OF PARTICULARS (Day 1 right from 2025)
        particulars_patterns = [
            r'written\s+statement\s+(?:of\s+)?(?:particulars|terms)',
            r'statement\s+of\s+(?:employment\s+)?(?:particulars|terms)',
            r'(?:provided|issued|given)\s+(?:on|by|within)\s+(?:day\s+one|day\s+1|first\s+day)'
        ]

        has_particulars_ref = any(re.search(p, text, re.IGNORECASE) for p in particulars_patterns)

        # Check for mandatory items (2025 requirements)
        mandatory_items = {
            'hours': r'(?:working\s+)?hours|hours\s+of\s+work',
            'pay': r'(?:salary|pay|remuneration|wage)',
            'holiday': r'(?:holiday|annual\s+leave|vacation)\s+entitlement',
            'job_title': r'job\s+title|position|role',
            'start_date': r'(?:start|commencement)\s+date|date\s+of\s+commencement',
            'location': r'(?:place|location)\s+of\s+work|work\s+location',
            'probation': r'probation(?:ary)?\s+period'
        }

        missing_items = []
        for item, pattern in mandatory_items.items():
            if not re.search(pattern, text, re.IGNORECASE):
                missing_items.append(item.replace('_', ' '))

        if missing_items and has_particulars_ref:
            warnings.append(f'Employment contract should include: {", ".join(missing_items)}')

        # 7. FLEXIBLE WORKING (Day 1 right from 2025)
        flexible_working_patterns = [
            r'flexible\s+working\s+(?:request|arrangements?)',
            r'(?:right\s+to\s+)?request\s+flexible\s+working',
            r'(?:home|remote)\s+working',
            r'hybrid\s+working'
        ]

        has_flexible_working = any(re.search(p, text, re.IGNORECASE) for p in flexible_working_patterns)

        if has_flexible_working:
            # Check for day 1 right mention
            day_one_patterns = [
                r'(?:from\s+)?day\s+(?:one|1|1st)',
                r'(?:from\s+)?(?:start|commencement)\s+of\s+employment',
                r'immediately',
                r'no\s+qualifying\s+period'
            ]

            has_day_one_right = any(re.search(p, text, re.IGNORECASE) for p in day_one_patterns)
            if not has_day_one_right:
                warnings.append('Under 2025 reforms, flexible working requests can be made from day 1 (no 26-week qualifying period)')

        # Determine overall status
        if issues:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Employment contract contains serious compliance issues',
                'legal_source': self.legal_source,
                'suggestion': 'Address critical issues: ' + '; '.join(issues[:3]),
                'spans': spans,
                'details': issues + warnings
            }

        if warnings:
            return {
                'status': 'WARNING',
                'severity': 'high',
                'message': 'Employment contract requires improvements for 2025 compliance',
                'legal_source': self.legal_source,
                'suggestion': 'Review and address: ' + '; '.join(warnings[:2]),
                'spans': spans,
                'details': warnings
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Employment contract terms appear compliant with 2025 regulations',
            'legal_source': self.legal_source,
            'spans': spans
        }


# Test cases
def test_employment_contracts_gate():
    gate = EmploymentContractsGate()

    # Test 1: Zero-hours with illegal exclusivity clause
    test1 = """
    ZERO-HOURS EMPLOYMENT CONTRACT

    You are engaged on a casual basis with no guaranteed hours of work.

    You shall not work for any other employer during the term of this agreement.
    """
    result1 = gate.check(test1, "employment_contract")
    assert result1['status'] == 'FAIL'
    assert 'exclusivity' in result1['message'].lower() or any('exclusivity' in str(d).lower() for d in result1.get('details', []))

    # Test 2: Fixed-term contract compliant
    test2 = """
    FIXED-TERM EMPLOYMENT CONTRACT

    This contract is for a fixed period ending on 31 December 2025.

    The contract may be renewed by mutual agreement. Under the Fixed-Term Employees Regulations,
    continuous fixed-term contracts totaling 4 years will result in permanent status.
    """
    result2 = gate.check(test2, "employment_contract")
    assert result2['status'] in ['PASS', 'WARNING']

    # Test 3: Probation period excessive
    test3 = """
    EMPLOYMENT CONTRACT

    You will be subject to a probationary period of 9 months from your start date.
    The probation period may be extended at the employer's discretion.
    """
    result3 = gate.check(test3, "employment_contract")
    assert result3['status'] == 'WARNING'
    assert any('probation' in str(d).lower() and '6 months' in str(d).lower() for d in result3.get('details', []))

    # Test 4: Garden leave compliant
    test4 = """
    NOTICE AND GARDEN LEAVE

    Either party must give 3 months' written notice to terminate employment.

    The employer may place you on garden leave for up to 3 months during your notice period.
    During garden leave, you will continue to receive your full salary and benefits.
    You must not contact clients or work for other employers during garden leave.
    """
    result4 = gate.check(test4, "employment_contract")
    assert result4['status'] in ['PASS', 'WARNING']

    # Test 5: Zero-hours compliant (2025)
    test5 = """
    ZERO-HOURS CONTRACT

    We guarantee a minimum of 12 hours work per week.
    Shifts will be notified at least 4 days in advance.
    You are free to work for other employers when not working for us.
    """
    result5 = gate.check(test5, "employment_contract")
    assert result5['status'] in ['PASS', 'WARNING']

    print("All employment contracts gate tests passed!")


if __name__ == "__main__":
    test_employment_contracts_gate()
