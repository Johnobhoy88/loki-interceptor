"""Costs and Charges Disclosure Gate - COBS 6.1ZA & MiFID II"""
import re

class CostsChargesDisclosureGate:
    def __init__(self):
        self.name = "costs_charges_disclosure"
        self.severity = "high"
        self.legal_source = "FCA COBS 6.1ZA (Costs and Charges)"

    def _is_relevant(self, text):
        return 'cost' in text.lower() or 'charge' in text.lower() or 'fee' in text.lower()

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'legal_source': self.legal_source}

        cost_elements = {
            'initial': r'initial\s+(?:charge|cost|fee)',
            'ongoing': r'ongoing\s+(?:charge|cost|fee)',
            'transaction': r'transaction\s+(?:cost|fee)',
            'exit': r'exit\s+(?:charge|cost|fee)',
            'total': r'total\s+cost'
        }

        found = [elem for elem, pattern in cost_elements.items() if re.search(pattern, text, re.IGNORECASE)]

        if len(found) < 3:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'Incomplete cost disclosure ({len(found)}/5 elements)',
                'legal_source': self.legal_source,
                'suggestion': 'Disclose all costs: initial, ongoing, transaction, exit, and total'
            }

        return {'status': 'PASS', 'message': f'Cost disclosure comprehensive ({len(found)} elements)', 'legal_source': self.legal_source}
