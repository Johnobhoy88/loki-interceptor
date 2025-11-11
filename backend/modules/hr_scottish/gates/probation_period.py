import re


class ProbationPeriodGate:
    def __init__(self):
        self.name = "probation_period"
        self.severity = "medium"
        self.legal_source = "Contract Law, Unfair Dismissal (qualifying period)"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['probation', 'trial', 'initial period', 'contract'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        probation_patterns = [
            r'probation(?:ary)?\s+period',
            r'trial\s+period',
            r'initial\s+(?:employment\s+)?period'
        ]

        has_probation = any(re.search(p, text, re.IGNORECASE) for p in probation_patterns)

        if not has_probation:
            return {'status': 'N/A', 'message': 'No probation period', 'legal_source': self.legal_source}

        # Check for duration
        duration_patterns = [
            r'(\d+)\s+(?:month|week)',
            r'(?:three|six|3|6)\s+months?',
            r'(?:twelve|12)\s+weeks?'
        ]

        duration_matches = [re.search(p, text, re.IGNORECASE) for p in duration_patterns]
        has_duration = any(duration_matches)

        # Check for excessive duration (>6 months)
        excessive_patterns = [
            r'(?:nine|twelve|18|9|12)\s+months?',
            r'one\s+year'
        ]

        is_excessive = any(re.search(p, text, re.IGNORECASE) for p in excessive_patterns)

        elements = {
            'duration_specified': has_duration,
            'objectives': r'(?:objective|target|goal|expectation)',
            'review_meetings': r'(?:review|appraisal|feedback|one-to-one).*(?:meeting|discussion)',
            'assessment': r'(?:assess|evaluat|performance)',
            'extension': r'extend.*probation|extend.*period',
            'confirmation': r'confirm(?:ation)?.*(?:employment|appointment|permanent)',
            'notice_period': r'notice.*(?:probation|shorter|reduced)',
            'support': r'(?:support|training|induction)',
            'fair_procedure': r'(?:fair|reasonable).*(?:procedure|process)',
            'right_to_appeal': r'appeal'
        }

        found_elements = {k: bool(re.search(p, text, re.IGNORECASE)) if isinstance(p, str) else p for k, p in elements.items()}
        score = sum(found_elements.values())

        if is_excessive:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Probation period may be unreasonably long',
                'legal_source': self.legal_source,
                'suggestion': 'Typical probation: 3-6 months. Longer periods may be unfair unless justified',
                'note': 'Employees gain unfair dismissal rights after 2 years (1 year if started before 6 April 2012)'
            }

        if score >= 6:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive probation provisions ({score}/10 elements)',
                'legal_source': self.legal_source,
                'elements_found': [k for k, v in found_elements.items() if v]
            }

        if score >= 3:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Basic probation provisions ({score}/10)',
                'legal_source': self.legal_source,
                'suggestion': 'Consider adding: objectives, review meetings, assessment criteria, extension provisions, support/training'
            }

        return {
            'status': 'WARNING',
            'severity': 'medium',
            'message': 'Probation period lacks detail',
            'legal_source': self.legal_source,
            'suggestion': 'Specify: duration (typically 3-6 months), objectives, review meetings, assessment process, notice period, confirmation procedure'
        }
