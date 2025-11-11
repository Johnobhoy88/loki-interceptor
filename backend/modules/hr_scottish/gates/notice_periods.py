import re


class NoticePeriodsGate:
    def __init__(self):
        self.name = "notice_periods"
        self.severity = "high"
        self.legal_source = "Employment Rights Act 1996 s.86"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['notice', 'terminat', 'resign', 'contract', 'employment'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        notice_patterns = [
            r'notice\s+period',
            r'notice.*(?:terminat|end|resign)',
            r'(?:give|provide).*notice'
        ]

        has_notice = any(re.search(p, text, re.IGNORECASE) for p in notice_patterns)

        if not has_notice:
            return {
                'status': 'WARNING',
                'severity': 'high',
                'message': 'No notice period provisions',
                'legal_source': self.legal_source,
                'suggestion': 'Specify notice periods: employer (statutory minimum), employee (contractual)',
                'note': 'Statutory minimum: 1 week after 1 month, 1 week per year of service (max 12 weeks) for employer notice'
            }

        # Check for employer notice period
        employer_notice_patterns = [
            r'(?:employer|company|we).*(?:give|provide).*(\d+)\s+(?:week|month).*notice',
            r'(?:entitled\s+to|receive).*(\d+)\s+(?:week|month).*notice',
            r'statutory\s+(?:minimum\s+)?notice'
        ]

        has_employer_notice = any(re.search(p, text, re.IGNORECASE) for p in employer_notice_patterns)

        # Check for employee notice period
        employee_notice_patterns = [
            r'(?:employee|you).*(?:must\s+give|provide|required).*(\d+)\s+(?:week|month).*notice',
            r'(?:resign|leave).*(?:giving|provide).*(\d+)\s+(?:week|month)'
        ]

        has_employee_notice = any(re.search(p, text, re.IGNORECASE) for p in employee_notice_patterns)

        # Check for statutory minimum compliance
        statutory_patterns = [
            r'statutory\s+(?:minimum|entitlement)',
            r'(?:whichever|greater|longer).*(?:statutory|required\s+by\s+law)',
            r'1\s+week.*1\s+month|one\s+week.*one\s+month',
            r'1\s+week.*year.*(?:service|employment)'
        ]

        mentions_statutory = any(re.search(p, text, re.IGNORECASE) for p in statutory_patterns)

        # Check for payment in lieu of notice (PILON)
        pilon_patterns = [
            r'payment\s+in\s+lieu.*notice|PILON',
            r'pay.*instead\s+of.*notice',
            r'(?:may|right\s+to).*pay.*(?:rather\s+than|lieu)'
        ]

        has_pilon = any(re.search(p, text, re.IGNORECASE) for p in pilon_patterns)

        # Check for garden leave
        garden_leave_patterns = [
            r'garden\s+leave',
            r'(?:require|direct).*(?:not\s+attend|stay\s+away).*(?:during\s+notice|notice\s+period)'
        ]

        has_garden_leave = any(re.search(p, text, re.IGNORECASE) for p in garden_leave_patterns)

        # Check for notice during probation
        probation_notice_patterns = [
            r'(?:during|whilst).*probation.*notice',
            r'probation.*(?:shorter|reduced|one\s+week).*notice'
        ]

        has_probation_notice = any(re.search(p, text, re.IGNORECASE) for p in probation_notice_patterns)

        elements_present = sum([
            has_employer_notice,
            has_employee_notice,
            mentions_statutory,
            has_pilon,
            has_garden_leave,
            has_probation_notice
        ])

        if not mentions_statutory and has_employer_notice:
            return {
                'status': 'WARNING',
                'severity': 'high',
                'message': 'Employer notice period specified without statutory minimum reference',
                'legal_source': 'Employment Rights Act 1996 s.86',
                'suggestion': 'Add: "whichever is greater: [X weeks/months] or statutory minimum (1 week after 1 month, 1 week per year up to 12 weeks)"',
                'note': 'Contractual notice cannot be less than statutory minimum'
            }

        if elements_present >= 4:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive notice provisions ({elements_present}/6 elements)',
                'legal_source': self.legal_source,
                'elements_found': {
                    'employer_notice': has_employer_notice,
                    'employee_notice': has_employee_notice,
                    'statutory_minimum': mentions_statutory,
                    'pilon': has_pilon,
                    'garden_leave': has_garden_leave,
                    'probation_notice': has_probation_notice
                }
            }

        if elements_present >= 2:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Basic notice provisions ({elements_present}/6)',
                'legal_source': self.legal_source,
                'suggestion': 'Consider adding: statutory minimum reference, PILON clause, garden leave provisions'
            }

        return {
            'status': 'WARNING',
            'severity': 'high',
            'message': 'Notice provisions incomplete',
            'legal_source': self.legal_source,
            'suggestion': 'Specify: employer notice (statutory minimum: 1 week after 1 month, 1 week/year up to 12), employee notice (typically 1-3 months), PILON rights'
        }
