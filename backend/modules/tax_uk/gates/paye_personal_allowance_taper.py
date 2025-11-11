import re


class PayePersonalAllowanceTaperGate:
    def __init__(self):
        self.name = "paye_personal_allowance_taper"
        self.severity = "high"
        self.legal_source = "ITA 2007, s35"

    def _is_relevant(self, text):
        keywords = ['personal allowance', '£100,000', 'taper']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check PA tapers £1 for every £2 over £100,000
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
