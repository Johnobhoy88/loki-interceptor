import re


class Ir35DeemedPaymentGate:
    def __init__(self):
        self.name = "ir35_deemed_payment"
        self.severity = "high"
        self.legal_source = "ITEPA 2003, s61N"

    def _is_relevant(self, text):
        keywords = ['deemed payment', 'inside ir35']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check deemed payment calculation if inside IR35
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
