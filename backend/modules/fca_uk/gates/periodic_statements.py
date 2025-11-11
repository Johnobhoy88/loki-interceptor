"""Periodic Statements Requirements Gate - COBS 16.3"""
import re

class PeriodicStatementsGate:
    def __init__(self):
        self.name = "periodic_statements"
        self.severity = "medium"
        self.legal_source = "FCA COBS 16.3 (Periodic Statements)"

    def _is_relevant(self, text):
        return 'periodic statement' in text.lower() or 'quarterly statement' in text.lower() or 'portfolio statement' in text.lower()

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'legal_source': self.legal_source}

        required_info = {
            'portfolio_value': r'(?:portfolio|account)\s+value',
            'performance': r'performance',
            'costs': r'(?:cost|charge|fee)s?',
            'holdings': r'holding',
            'transactions': r'transaction'
        }

        found = [info for info, pattern in required_info.items() if re.search(pattern, text, re.IGNORECASE)]

        if len(found) < 3:
            return {
                'status': 'WARNING',
                'message': f'Periodic statement incomplete ({len(found)}/5 elements)',
                'legal_source': self.legal_source,
                'suggestion': 'Include: portfolio value, performance, costs, holdings, transactions'
            }

        return {'status': 'PASS', 'message': 'Periodic statement requirements met', 'legal_source': self.legal_source}
