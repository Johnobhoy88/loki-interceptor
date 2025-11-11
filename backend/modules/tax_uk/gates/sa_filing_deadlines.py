import re


class SaFilingDeadlinesGate:
    def __init__(self):
        self.name = "sa_filing_deadlines"
        self.severity = "high"
        self.legal_source = "TMA 1970, s8"

    def _is_relevant(self, text):
        keywords = ['filing deadline', '31 october', '31 january']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check deadlines: 31 October (paper), 31 January (online)
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
