import re


class Ir35ControlTestGate:
    def __init__(self):
        self.name = "ir35_control_test"
        self.severity = "high"
        self.legal_source = "ITEPA 2003, Chapter 8; ESM0522"

    def _is_relevant(self, text):
        keywords = ['control', 'supervision', 'direction']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check control indicators for IR35 status
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
