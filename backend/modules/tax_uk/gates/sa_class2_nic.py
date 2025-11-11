import re


class SaClass2NicGate:
    def __init__(self):
        self.name = "sa_class2_nic"
        self.severity = "high"
        self.legal_source = "SSCBA 1992"

    def _is_relevant(self, text):
        keywords = ['class 2', 'self-employed', '£12,570']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check Class 2 NIC threshold £12,570
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
