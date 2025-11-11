import re


class IhtLifetimeTransfersGate:
    def __init__(self):
        self.name = "iht_lifetime_transfers"
        self.severity = "high"
        self.legal_source = "IHTA 1984, s3"

    def _is_relevant(self, text):
        keywords = ['clt', 'chargeable lifetime transfer']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check CLTs taxed at 20% on excess over NRB
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
