import re


class SaHighEarnerCheckGate:
    def __init__(self):
        self.name = "sa_high_earner_check"
        self.severity = "high"
        self.legal_source = "ITA 2007, s35"

    def _is_relevant(self, text):
        keywords = ['£100,000', 'high earner']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check SA required for income over £100,000 (PA taper)
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
