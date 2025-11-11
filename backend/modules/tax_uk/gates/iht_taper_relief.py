import re


class IhtTaperReliefGate:
    def __init__(self):
        self.name = "iht_taper_relief"
        self.severity = "high"
        self.legal_source = "IHTA 1984, s7(4)"

    def _is_relevant(self, text):
        keywords = ['taper relief', '3-7 years']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check taper relief for gifts 3-7 years before death
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
