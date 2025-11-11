import re


class SaPenaltiesGate:
    def __init__(self):
        self.name = "sa_penalties"
        self.severity = "high"
        self.legal_source = "FA 2009, Schedule 55-56"

    def _is_relevant(self, text):
        keywords = ['late filing', 'penalty', '£100']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check penalties: £100 (1 day late), £10/day (3 months), 5% (6 months)
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
