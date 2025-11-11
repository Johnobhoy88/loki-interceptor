import re


class PaternityLeaveGate:
    def __init__(self):
        self.name = "paternity_leave"
        self.severity = "high"
        self.legal_source = "Paternity and Adoption Leave Regulations 2002, Employment Rights Act 1996"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['paternity', 'father', 'partner', 'parental', 'leave'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        paternity_patterns = [
            r'paternity\s+leave',
            r'father.*leave',
            r'partner.*(?:leave|birth)'
        ]

        has_paternity = any(re.search(p, text, re.IGNORECASE) for p in paternity_patterns)

        if not has_paternity:
            return {'status': 'N/A', 'message': 'No paternity leave provisions', 'legal_source': self.legal_source}

        elements = {
            'two_weeks': r'(?:two|2)\s+weeks?|(?:one|1|two|2)\s+weeks?.*paternity',
            'notification': r'(?:notify|notice).*(?:15th\s+week|15\s+weeks?).*(?:before|prior)',
            'eligibility_26_weeks': r'(?:26|twenty[- ]six)\s+weeks?.*(?:continuous|employed)',
            'statutory_pay': r'(?:statutory\s+paternity\s+pay|SPP)',
            'timing': r'(?:56|fifty[- ]six)\s+days?.*(?:birth|placement)',
            'one_or_two_weeks': r'(?:one|two|1|2)\s+(?:consecutive\s+)?weeks?.*(?:block|together)',
            'adoption': r'adoption|adopt(?:ed|ing)',
            'protection_from_detriment': r'(?:not|no).*detriment.*paternity',
            'return_to_work': r'right.*return.*(?:same|similar)\s+(?:job|role)'
        }

        found = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in elements.items()}
        score = sum(found.values())

        if score >= 6:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive paternity leave provisions ({score}/9 elements)',
                'legal_source': self.legal_source,
                'elements_found': [k for k, v in found.items() if v]
            }

        if score >= 4:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'Paternity leave provisions incomplete ({score}/9)',
                'legal_source': self.legal_source,
                'missing': [k for k, v in found.items() if not v],
                'suggestion': 'Add: 2 weeks leave, notification (15th week before EWC), 26 weeks service, SPP, within 56 days of birth, protection from detriment'
            }

        return {
            'status': 'WARNING',
            'severity': 'high',
            'message': 'Paternity leave lacks statutory requirements',
            'legal_source': self.legal_source,
            'suggestion': 'Must provide: 2 weeks paternity leave (can take 1 or 2 weeks in one block), within 56 days of birth, notification by 15th week before EWC, 26 weeks service, SPP, return rights'
        }
