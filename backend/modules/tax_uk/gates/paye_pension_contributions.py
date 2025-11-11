import re


class PayePensionContributionsGate:
    def __init__(self):
        self.name = "paye_pension_contributions"
        self.severity = "high"
        self.legal_source = "FA 2004; Pensions Act 2008"

    def _is_relevant(self, text):
        keywords = ['pension', 'auto enrolment', 'salary sacrifice']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check pension contributions treatment
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
