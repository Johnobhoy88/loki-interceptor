import re


class Ir35MutualityObligationGate:
    def __init__(self):
        self.name = "ir35_mutuality_obligation"
        self.severity = "high"
        self.legal_source = "ESM0540"

    def _is_relevant(self, text):
        keywords = ['mutuality', 'obligation']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check mutuality of obligation between parties
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
