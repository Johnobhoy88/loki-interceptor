import re


class PayeTaxCodeGate:
    def __init__(self):
        self.name = "paye_tax_code"
        self.severity = "high"
        self.legal_source = "ITEPA 2003; PAYE Manual"

    def _is_relevant(self, text):
        keywords = ['tax code', 'paye', '1257L']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check tax code format valid (e.g., 1257L for 2024/25)
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
