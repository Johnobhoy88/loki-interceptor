"""Tied Agent Disclosure Gate - COBS 2.4"""
import re

class TiedAgentDisclosureGate:
    def __init__(self):
        self.name = "tied_agent_disclosure"
        self.severity = "high"
        self.legal_source = "FCA COBS 2.4 (Tied Agents)"

    def _is_relevant(self, text):
        return 'tied agent' in text.lower() or 'appointed representative' in text.lower()

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'legal_source': self.legal_source}

        required_disclosures = {
            'tied_status': r'tied\s+(?:agent|to)',
            'principal_firm': r'(?:principal|on\s+behalf\s+of)',
            'limited_products': r'(?:limited|restricted)\s+(?:range|product)',
            'fca_register': r'fca\s+(?:register|number)'
        }

        found = [disc for disc, pattern in required_disclosures.items() if re.search(pattern, text, re.IGNORECASE)]

        if len(found) < 3:
            return {
                'status': 'FAIL',
                'severity': 'high',
                'message': 'Tied agent status not properly disclosed',
                'legal_source': self.legal_source,
                'suggestion': 'Disclose: tied status, principal firm, limited product range, FCA registration'
            }

        return {'status': 'PASS', 'message': 'Tied agent properly disclosed', 'legal_source': self.legal_source}
