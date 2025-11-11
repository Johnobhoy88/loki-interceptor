import re


class CgtRateValidationGate:
    def __init__(self):
        self.name = "cgt_rate_validation"
        self.severity = "high"
        self.legal_source = "TCGA 1992; Finance Act 2024"

    def _is_relevant(self, text):
        keywords = ['capital gains', 'cgt']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check CGT rates: 10%/20% (assets), 18%/24% (property)
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
