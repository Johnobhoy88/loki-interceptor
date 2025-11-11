"""Platform Services Disclosure Gate - COBS 6.1ZB"""
import re

class PlatformDisclosureGate:
    def __init__(self):
        self.name = "platform_disclosure"
        self.severity = "medium"
        self.legal_source = "FCA COBS 6.1ZB (Platform Services)"

    def _is_relevant(self, text):
        platform_terms = ['platform', 'wrap', 'investment platform', 'platform service']
        return any(term in text.lower() for term in platform_terms)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'legal_source': self.legal_source}

        disclosures = {
            'platform_charge': r'platform\s+(?:charge|fee)',
            'fund_charges': r'fund\s+(?:charge|fee)',
            'transaction_costs': r'transaction\s+(?:cost|fee)',
            'adviser_charge': r'adviser\s+charge',
            'total_costs': r'total\s+(?:cost|charge)'
        }

        found = [disc for disc, pattern in disclosures.items() if re.search(pattern, text, re.IGNORECASE)]

        if len(found) < 3:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'Platform disclosure incomplete ({len(found)} elements)',
                'legal_source': self.legal_source,
                'suggestion': 'Disclose: platform charges, fund charges, transaction costs, adviser charges, total'
            }

        return {'status': 'PASS', 'message': f'Platform disclosures adequate ({len(found)} elements)', 'legal_source': self.legal_source}
