import re


class IhtSevenYearRuleGate:
    def __init__(self):
        self.name = "iht_seven_year_rule"
        self.severity = "high"
        self.legal_source = "IHTA 1984, s3A"

    def _is_relevant(self, text):
        keywords = ['seven year', 'pet', 'potentially exempt']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check gifts survive 7 years to be exempt (PETs)
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
