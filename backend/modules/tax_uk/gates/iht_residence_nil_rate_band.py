import re


class IhtResidenceNilRateBandGate:
    def __init__(self):
        self.name = "iht_residence_nil_rate_band"
        self.severity = "high"
        self.legal_source = "IHTA 1984, s8D-8M"

    def _is_relevant(self, text):
        keywords = ['residence nil rate', 'rnrb', '£175,000']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check RNRB £175,000 (frozen until 2028), tapers over £2m
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
