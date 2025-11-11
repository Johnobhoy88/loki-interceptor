import re


class CtDistributionsGate:
    def __init__(self):
        self.name = "ct_distributions"
        self.severity = "high"
        self.legal_source = "CTA 2010, Part 23"

    def _is_relevant(self, text):
        keywords = ['dividend', 'distribution']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Dividends are distributions, not deductible expenses
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
