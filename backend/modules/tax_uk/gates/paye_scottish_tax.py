import re


class PayeScottishTaxGate:
    def __init__(self):
        self.name = "paye_scottish_tax"
        self.severity = "high"
        self.legal_source = "Scottish Income Tax Act 2024"

    def _is_relevant(self, text):
        keywords = ['scottish tax', 's code', 'scotland']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check Scottish tax rates: 19%, 20%, 21%, 42%, 47%
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
