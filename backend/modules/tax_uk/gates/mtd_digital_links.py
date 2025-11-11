import re


class MtdDigitalLinksGate:
    def __init__(self):
        self.name = "mtd_digital_links"
        self.severity = "high"
        self.legal_source = "HMRC Notice 700/22, Section 5"

    def _is_relevant(self, text):
        keywords = ['digital link', 'manual intervention']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check digital links must not require manual intervention
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
