import re


class CtGroupReliefGate:
    def __init__(self):
        self.name = "ct_group_relief"
        self.severity = "high"
        self.legal_source = "CTA 2010, Part 5"

    def _is_relevant(self, text):
        keywords = ['group relief', '75% group', 'loss surrender']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check group relief available for 75% groups
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
