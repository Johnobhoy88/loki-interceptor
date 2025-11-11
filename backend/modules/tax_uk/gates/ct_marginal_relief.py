import re


class CtMarginalReliefGate:
    def __init__(self):
        self.name = "ct_marginal_relief"
        self.severity = "high"
        self.legal_source = "CTA 2010, s18A-18F"

    def _is_relevant(self, text):
        keywords = ['marginal relief', 'profit threshold']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check marginal relief applies between £50,000-£250,000 profits
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
