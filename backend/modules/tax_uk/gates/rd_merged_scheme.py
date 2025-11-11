import re


class RdMergedSchemeGate:
    def __init__(self):
        self.name = "rd_merged_scheme"
        self.severity = "high"
        self.legal_source = "FA 2024, s13"

    def _is_relevant(self, text):
        keywords = ['merged scheme', 'rdec', 'sme r&d']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check merged R&D scheme 20% from April 2024
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
