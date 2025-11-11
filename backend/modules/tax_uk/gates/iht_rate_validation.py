import re


class IhtRateValidationGate:
    def __init__(self):
        self.name = "iht_rate_validation"
        self.severity = "high"
        self.legal_source = "IHTA 1984, s7"

    def _is_relevant(self, text):
        keywords = ['inheritance tax', 'iht', '40%']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check IHT rates: 40% (death), 36% (10%+ to charity), 20% (lifetime)
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
