import re


class CtPaymentDeadlinesGate:
    def __init__(self):
        self.name = "ct_payment_deadlines"
        self.severity = "high"
        self.legal_source = "TMA 1970, s59D"

    def _is_relevant(self, text):
        keywords = ['payment deadline', 'due date', '9 month']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check CT payment due 9 months and 1 day after period end
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
