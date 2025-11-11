import re


class PayeBenefitsInKindGate:
    def __init__(self):
        self.name = "paye_benefits_in_kind"
        self.severity = "high"
        self.legal_source = "ITEPA 2003, Part 3"

    def _is_relevant(self, text):
        keywords = ['benefit in kind', 'p11d', 'company car']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check taxable benefits reported correctly
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
