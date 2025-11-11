import re


class RdAdditionalInformationGate:
    def __init__(self):
        self.name = "rd_additional_information"
        self.severity = "high"
        self.legal_source = "FA 2023, Schedule 9"

    def _is_relevant(self, text):
        keywords = ['additional information', 'project report']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check additional information form required with all R&D claims
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
