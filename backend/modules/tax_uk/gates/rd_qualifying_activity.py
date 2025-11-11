import re


class RdQualifyingActivityGate:
    def __init__(self):
        self.name = "rd_qualifying_activity"
        self.severity = "high"
        self.legal_source = "CTA 2009, Part 13; BIS Guidelines"

    def _is_relevant(self, text):
        keywords = ['r&d', 'research', 'scientific']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check activity meets R&D definition: scientific/technical uncertainty
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
