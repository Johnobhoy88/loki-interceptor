"""MiFID Client Categorization Gate - COBS 3"""
import re

class MiFIDCategorizationGate:
    def __init__(self):
        self.name = "mifid_categorization"
        self.severity = "high"
        self.legal_source = "FCA COBS 3 (Client Categorization)"

    def _is_relevant(self, text):
        cat_terms = ['retail', 'professional', 'eligible counterparty', 'client categor']
        return any(term in text.lower() for term in cat_terms)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'legal_source': self.legal_source}

        categories = ['retail', 'professional', 'eligible counterparty']
        found = [cat for cat in categories if cat in text.lower()]

        if not found:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Client categorization mentioned but not specified',
                'legal_source': self.legal_source,
                'suggestion': 'Specify client category: retail, professional, or eligible counterparty'
            }

        return {'status': 'PASS', 'message': f'Client categorization specified ({", ".join(found)})', 'legal_source': self.legal_source}
