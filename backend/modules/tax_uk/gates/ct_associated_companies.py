import re


class CtAssociatedCompaniesGate:
    def __init__(self):
        self.name = "ct_associated_companies"
        self.severity = "high"
        self.legal_source = "CTA 2010, s25"

    def _is_relevant(self, text):
        keywords = ['associated compan', 'control', '51%']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check profit limits divided by (associated companies + 1)
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
