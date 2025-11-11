import re


class SharedParentalLeaveGate:
    def __init__(self):
        self.name = "shared_parental_leave"
        self.severity = "medium"
        self.legal_source = "Shared Parental Leave Regulations 2014, Children and Families Act 2014"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['shared', 'parental', 'spl', 'leave'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        spl_patterns = [
            r'shared\s+parental\s+leave|SPL',
            r'share.*(?:maternity|leave)',
            r'curtail.*maternity'
        ]

        has_spl = any(re.search(p, text, re.IGNORECASE) for p in spl_patterns)

        if not has_spl:
            return {'status': 'N/A', 'message': 'No shared parental leave provisions', 'legal_source': self.legal_source}

        elements = {
            '52_weeks_total': r'(?:52|fifty[- ]two)\s+weeks?',
            'curtailment': r'curtail(?:ment)?.*maternity',
            'eligibility': r'26\s+weeks?.*(?:continuous|employed)|eligib(?:le|ility)',
            'notification': r'(?:8|eight)\s+weeks?.*(?:notice|before)',
            'flexible': r'(?:flexible|pattern|discontinuous|blocks?)',
            'shared_pay': r'(?:ShPP|shared\s+parental\s+pay)',
            'both_parents': r'(?:both|either)\s+(?:parent|partner)',
            'adoption': r'adoption|adopt(?:ed|ing)',
            'booking_notice': r'booking\s+notice|period\s+of\s+leave\s+notice',
            'variation': r'vary.*(?:booking|notice|period)'
        }

        found = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in elements.items()}
        score = sum(found.values())

        if score >= 7:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive SPL provisions ({score}/10 elements)',
                'legal_source': self.legal_source,
                'elements_found': [k for k, v in found.items() if v]
            }

        if score >= 4:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Basic SPL provisions ({score}/10)',
                'legal_source': self.legal_source,
                'suggestion': 'Consider adding: flexible booking, variation rights, ShPP details, adoption provisions'
            }

        return {
            'status': 'WARNING',
            'severity': 'medium',
            'message': f'SPL provisions incomplete ({score}/10)',
            'legal_source': self.legal_source,
            'suggestion': 'Shared Parental Leave Regs 2014: up to 52 weeks (shared between parents), curtail maternity, 8 weeks notice, flexible patterns, ShPP, eligibility 26 weeks service'
        }
