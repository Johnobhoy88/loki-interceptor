"""Adviser Charging Disclosure Gate - COBS 6.1A"""
import re

class AdviserChargingGate:
    def __init__(self):
        self.name = "adviser_charging"
        self.severity = "high"
        self.legal_source = "FCA COBS 6.1A (Adviser Charging and Remuneration)"

    def _is_relevant(self, text):
        adviser_terms = ['adviser charge', 'advice fee', 'advisory fee', 'adviser remuneration']
        return any(term in text.lower() for term in adviser_terms)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'legal_source': self.legal_source}

        required_disclosures = {
            'amount': r'£\d+|(\d+\.?\d*%)',
            'when_payable': r'(?:payable|due|charged)\s+(?:when|on|at)',
            'method': r'(?:initial|ongoing|percentage|fixed|hourly)',
            'right_to_cancel': r'(?:cancel|cooling[- ]off)'
        }

        found = [disc for disc, pattern in required_disclosures.items() if re.search(pattern, text, re.IGNORECASE)]

        if len(found) < 3:
            return {
                'status': 'FAIL',
                'severity': 'high',
                'message': 'Adviser charging disclosure incomplete',
                'legal_source': self.legal_source,
                'suggestion': 'Disclose: amount, when payable, payment method, cancellation rights'
            }

        return {'status': 'PASS', 'message': 'Adviser charging properly disclosed', 'legal_source': self.legal_source}
