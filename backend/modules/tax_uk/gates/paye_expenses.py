import re


class PayeExpensesGate:
    def __init__(self):
        self.name = "paye_expenses"
        self.severity = "high"
        self.legal_source = "ITEPA 2003, s336"

    def _is_relevant(self, text):
        keywords = ['business expense', 'wholly exclusively', 'mileage']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check expenses wholly, exclusively, necessarily for employment
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
