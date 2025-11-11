"""Aggregated Costs Disclosure Gate - COBS 6.1ZA"""
import re

class AggregatedCostsGate:
    def __init__(self):
        self.name = "aggregated_costs"
        self.severity = "high"
        self.legal_source = "FCA COBS 6.1ZA (Aggregated Costs)"

    def _is_relevant(self, text):
        cost_terms = ['total cost', 'aggregated cost', 'cumulative cost', 'all-in cost']
        return any(term in text.lower() for term in cost_terms)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'legal_source': self.legal_source}

        required_elements = {
            'percentage': r'\d+\.?\d*%',
            'pounds': r'£\d+',
            'illustration': r'(?:illustration|example|scenario)',
            'impact': r'impact\s+(?:on|of)\s+(?:return|performance)'
        }

        found = [elem for elem, pattern in required_elements.items() if re.search(pattern, text, re.IGNORECASE)]

        if len(found) < 2:
            return {
                'status': 'WARNING',
                'message': 'Aggregated costs disclosure lacks detail',
                'legal_source': self.legal_source,
                'suggestion': 'Show costs in % AND £, with illustration of impact on returns'
            }

        return {'status': 'PASS', 'message': 'Aggregated costs properly disclosed', 'legal_source': self.legal_source}
