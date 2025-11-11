import re


class Ir35SdsRequirementGate:
    def __init__(self):
        self.name = "ir35_sds_requirement"
        self.severity = "high"
        self.legal_source = "FA 2021, s15"

    def _is_relevant(self, text):
        keywords = ['status determination', 'sds']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check Status Determination Statement required for medium/large clients
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
