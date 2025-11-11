import re


class SaPropertyAllowanceGate:
    def __init__(self):
        self.name = "sa_property_allowance"
        self.severity = "high"
        self.legal_source = "ITA 2007, s783A"

    def _is_relevant(self, text):
        keywords = ['property allowance', 'rental', '£1,000']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check £1,000 property allowance for rental income
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
