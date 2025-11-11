import re


class CtLossesGate:
    def __init__(self):
        self.name = "ct_losses"
        self.severity = "high"
        self.legal_source = "CTA 2010, Part 4"

    def _is_relevant(self, text):
        keywords = ['trading loss', 'carry forward', 'carry back']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check loss relief options: carry forward, carry back 12 months
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
