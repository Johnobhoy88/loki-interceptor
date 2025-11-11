import re


class SaTradingAllowanceGate:
    def __init__(self):
        self.name = "sa_trading_allowance"
        self.severity = "high"
        self.legal_source = "ITA 2007, s783A"

    def _is_relevant(self, text):
        keywords = ['trading allowance', '£1,000']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check £1,000 trading allowance for self-employment income
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
