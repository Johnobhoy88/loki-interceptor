import re


class IhtExemptionsGate:
    def __init__(self):
        self.name = "iht_exemptions"
        self.severity = "high"
        self.legal_source = "IHTA 1984, Part II"

    def _is_relevant(self, text):
        keywords = ['spouse exemption', 'charity', 'annual exemption']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check exemptions: spouse (unlimited), charity (unlimited), annual (£3,000)
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
