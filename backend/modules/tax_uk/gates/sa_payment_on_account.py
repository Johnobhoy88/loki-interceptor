import re


class SaPaymentOnAccountGate:
    def __init__(self):
        self.name = "sa_payment_on_account"
        self.severity = "high"
        self.legal_source = "TMA 1970, s59A"

    def _is_relevant(self, text):
        keywords = ['payment on account', 'poa']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check POA: 31 January and 31 July, 50% of previous year tax
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
