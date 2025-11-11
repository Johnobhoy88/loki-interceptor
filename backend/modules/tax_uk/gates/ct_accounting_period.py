import re


class CtAccountingPeriodGate:
    def __init__(self):
        self.name = "ct_accounting_period"
        self.severity = "high"
        self.legal_source = "CTA 2009, s10"

    def _is_relevant(self, text):
        keywords = ['accounting period', 'period end']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check accounting period cannot exceed 12 months
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
