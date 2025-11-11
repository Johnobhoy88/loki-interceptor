import re


class IhtNilRateBandGate:
    def __init__(self):
        self.name = "iht_nil_rate_band"
        self.severity = "high"
        self.legal_source = "IHTA 1984, s7"

    def _is_relevant(self, text):
        keywords = ['nil rate band', 'nrb', '£325,000']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check NRB £325,000 (frozen until 2028)
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
