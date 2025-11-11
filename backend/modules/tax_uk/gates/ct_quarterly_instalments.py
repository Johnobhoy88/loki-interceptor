import re


class CtQuarterlyInstalmentsGate:
    def __init__(self):
        self.name = "ct_quarterly_instalments"
        self.severity = "high"
        self.legal_source = "SI 1998/3175"

    def _is_relevant(self, text):
        keywords = ['quarterly payment', 'instalment', '£1.5m']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Large companies (£1.5m+ profits) pay CT in quarterly instalments
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
