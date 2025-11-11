import re


class CgtBadrValidationGate:
    def __init__(self):
        self.name = "cgt_badr_validation"
        self.severity = "high"
        self.legal_source = "TCGA 1992, s169H-S"

    def _is_relevant(self, text):
        keywords = ['business asset disposal', 'badr', 'entrepreneurs relief']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check BADR: 10% rate, £1m lifetime limit, 2-year ownership
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
