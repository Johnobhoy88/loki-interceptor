import re


class ParentalLeaveGate:
    def __init__(self):
        self.name = "parental_leave"
        self.severity = "medium"
        self.legal_source = "Maternity and Parental Leave Regulations 1999, Employment Rights Act 1996"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['parental', 'leave', 'child', 'care'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        parental_patterns = [
            r'parental\s+leave',
            r'(?:care|time\s+off).*(?:child|dependant)',
            r'unpaid.*(?:leave|time\s+off).*(?:child|family)'
        ]

        has_parental = any(re.search(p, text, re.IGNORECASE) for p in parental_patterns)

        if not has_parental:
            return {'status': 'N/A', 'message': 'No parental leave provisions', 'legal_source': self.legal_source}

        elements = {
            '18_weeks': r'(?:18|eighteen)\s+weeks?',
            'per_child': r'(?:per|each)\s+child',
            'age_18': r'(?:before|until|child.*18).*(?:18(?:th)?|eighteen)',
            'one_year_service': r'(?:one|1)\s+year.*(?:continuous|service|employed)',
            'unpaid': r'unpaid',
            'notice_21_days': r'21\s+days?.*notice|(?:three|3)\s+weeks?.*notice',
            'blocks_of_weeks': r'(?:week|block).*(?:at\s+a\s+time|maximum)',
            'postponement': r'(?:postpone|defer).*(?:business|operational)\s+(?:reason|ground)',
            'protection_from_detriment': r'(?:not|no).*detriment.*parental',
            'return_to_work': r'right.*return.*(?:same|similar)\s+(?:job|role)'
        }

        found = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in elements.items()}
        score = sum(found.values())

        if score >= 7:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive parental leave provisions ({score}/10 elements)',
                'legal_source': self.legal_source,
                'elements_found': [k for k, v in found.items() if v]
            }

        if score >= 4:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Basic parental leave provisions ({score}/10)',
                'legal_source': self.legal_source,
                'suggestion': 'Add: 21 days notice, postponement rights, blocks of weeks, protection from detriment'
            }

        return {
            'status': 'WARNING',
            'severity': 'medium',
            'message': f'Parental leave provisions incomplete ({score}/10)',
            'legal_source': self.legal_source,
            'suggestion': 'Parental leave per MPL Regs 1999: 18 weeks per child, before 18th birthday, 1 year service, unpaid, 21 days notice, blocks of weeks, employer can postpone for business reasons, return rights'
        }
