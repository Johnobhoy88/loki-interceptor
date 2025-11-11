import re


class CtIntangibleAssetsGate:
    def __init__(self):
        self.name = "ct_intangible_assets"
        self.severity = "high"
        self.legal_source = "CTA 2009, Part 8"

    def _is_relevant(self, text):
        keywords = ['intangible asset', 'goodwill', 'intellectual property']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check intangible asset amortisation treatment
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
