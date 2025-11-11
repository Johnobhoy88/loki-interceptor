"""Product Information Disclosure Gate - COBS 14"""
import re

class ProductInformationDisclosureGate:
    def __init__(self):
        self.name = "product_information_disclosure"
        self.severity = "medium"
        self.legal_source = "FCA COBS 14 (Providing Product Information)"

    def _is_relevant(self, text):
        product_terms = ['product', 'fund', 'investment', 'policy', 'pension', 'isa']
        return any(term in text.lower() for term in product_terms)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'legal_source': self.legal_source}

        key_info = {
            'name': r'(?:product|fund)\s+name',
            'provider': r'provider',
            'objectives': r'(?:aim|objective|goal)',
            'risks': r'risk',
            'costs': r'(?:cost|charge|fee)',
            'features': r'(?:feature|benefit|key\s+point)'
        }

        found = [info for info, pattern in key_info.items() if re.search(pattern, text, re.IGNORECASE)]

        if len(found) < 4:
            return {
                'status': 'WARNING',
                'message': f'Product information incomplete ({len(found)}/6 elements)',
                'legal_source': self.legal_source,
                'suggestion': 'Include: name, provider, objectives, risks, costs, key features'
            }

        return {'status': 'PASS', 'message': 'Product information adequate', 'legal_source': self.legal_source}
