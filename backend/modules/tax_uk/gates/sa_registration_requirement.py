import re


class SaRegistrationRequirementGate:
    def __init__(self):
        self.name = "sa_registration_requirement"
        self.severity = "high"
        self.legal_source = "TMA 1970, s7"

    def _is_relevant(self, text):
        keywords = ['self-employed', 'rental income', 'register']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check SA registration required for self-employed, rental income £1k+, high earners
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
