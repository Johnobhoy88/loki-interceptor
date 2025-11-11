"""24-Hour Cooling-Off Period Gate - COBS 4.12C (Crypto)"""
import re

class CoolingOffPeriodGate:
    def __init__(self):
        self.name = "cooling_off_period"
        self.severity = "critical"
        self.legal_source = "FCA COBS 4.12C (24-Hour Cooling-Off)"

    def _is_relevant(self, text):
        crypto_terms = ['crypto', 'bitcoin', 'ethereum', 'digital currency', 'blockchain token']
        return any(term in text.lower() for term in crypto_terms)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'legal_source': self.legal_source}

        has_cooling_off = bool(re.search(r'(?:24|twenty[- ]four)\s+hour', text, re.IGNORECASE))
        has_immediate = bool(re.search(r'(?:buy|invest|purchase)\s+(?:now|immediately)', text, re.IGNORECASE))

        if has_immediate and not has_cooling_off:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Crypto promotion without 24-hour cooling-off',
                'legal_source': self.legal_source,
                'suggestion': 'COBS 4.12C requires 24-hour delay between risk warning and investment'
            }

        return {'status': 'PASS', 'message': 'Cooling-off period complied with', 'legal_source': self.legal_source}
