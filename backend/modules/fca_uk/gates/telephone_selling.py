"""Telephone Selling Requirements Gate - COBS 5.1"""
import re

class TelephoneSellingGate:
    def __init__(self):
        self.name = "telephone_selling"
        self.severity = "medium"
        self.legal_source = "FCA COBS 5.1 (Non-Real Time Communications)"

    def _is_relevant(self, text):
        telephone_terms = ['telephone', 'phone call', 'call script', 'telemarketing', 'telesales']
        return any(term in text.lower() for term in telephone_terms)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'legal_source': self.legal_source}

        required_info = {
            'firm_identity': r'(?:we\s+are|firm\s+name|company\s+name)',
            'purpose': r'(?:purpose|reason\s+for\s+call)',
            'confirmation': r'(?:confirm|follow[- ]up|written\s+confirmation)',
            'opt_out': r'(?:opt[- ]out|unsubscribe|do\s+not\s+call)'
        }

        found = [info for info, pattern in required_info.items() if re.search(pattern, text, re.IGNORECASE)]

        if len(found) < 3:
            return {
                'status': 'WARNING',
                'message': 'Telephone selling script lacks required elements',
                'legal_source': self.legal_source,
                'suggestion': 'Include: firm identity, call purpose, written confirmation, opt-out'
            }

        return {'status': 'PASS', 'message': 'Telephone selling requirements met', 'legal_source': self.legal_source}
