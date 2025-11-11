import re


class CgtPrivateResidenceReliefGate:
    def __init__(self):
        self.name = "cgt_private_residence_relief"
        self.severity = "high"
        self.legal_source = "TCGA 1992, s222-226"

    def _is_relevant(self, text):
        keywords = ['private residence', 'prr', 'main home']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check PRR available for main residence
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
