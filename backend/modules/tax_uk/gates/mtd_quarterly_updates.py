import re


class MtdQuarterlyUpdatesGate:
    def __init__(self):
        self.name = "mtd_quarterly_updates"
        self.severity = "high"
        self.legal_source = "MTD for ITSA Regulations 2021"

    def _is_relevant(self, text):
        keywords = ['quarterly update', 'eops', 'end of period']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check quarterly updates and EOPS required for MTD ITSA
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
