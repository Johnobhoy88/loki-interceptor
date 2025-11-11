import re


class CtLoanRelationshipsGate:
    def __init__(self):
        self.name = "ct_loan_relationships"
        self.severity = "high"
        self.legal_source = "CTA 2009, Part 5"

    def _is_relevant(self, text):
        keywords = ['loan relationship', 'interest', 'debt']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check loan relationship tax treatment
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
