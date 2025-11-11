"""Cancellation Rights Disclosure Gate - COBS 15"""
import re

class CancellationRightsGate:
    def __init__(self):
        self.name = "cancellation_rights"
        self.severity = "medium"
        self.legal_source = "FCA COBS 15 (Cancellation Rights)"

    def _is_relevant(self, text):
        product_terms = ['life insurance', 'pension', 'long-term care', 'personal pension', 'stakeholder']
        return any(term in text.lower() for term in product_terms)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'legal_source': self.legal_source}

        has_cancellation = bool(re.search(r'cancellation|cooling[- ]off|right\s+to\s+cancel', text, re.IGNORECASE))
        has_period = bool(re.search(r'(?:14|30)\s+day', text, re.IGNORECASE))

        if not has_cancellation:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'No cancellation rights disclosed',
                'legal_source': self.legal_source,
                'suggestion': 'Disclose cancellation rights and time period (typically 14 or 30 days)'
            }

        return {'status': 'PASS', 'message': 'Cancellation rights disclosed', 'legal_source': self.legal_source}
