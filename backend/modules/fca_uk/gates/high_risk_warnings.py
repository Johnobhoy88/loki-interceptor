"""High-Risk Investment Warnings Gate - PS22/10"""
import re

class HighRiskWarningsGate:
    def __init__(self):
        self.name = "high_risk_warnings"
        self.severity = "critical"
        self.legal_source = "FCA PS22/10 (High-Risk Investment Warnings)"

    def _is_relevant(self, text):
        high_risk_terms = ['high-risk', 'high risk', 'speculative', 'unregulated', 'p2p', 'crowdfund', 'mini-bond']
        return any(term in text.lower() for term in high_risk_terms)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not high-risk investment', 'legal_source': self.legal_source}

        required_warning = "don't invest unless you're prepared to lose all the money you invest"

        if required_warning.lower() not in text.lower():
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Missing mandatory high-risk warning',
                'legal_source': self.legal_source,
                'suggestion': 'Include: "Don\'t invest unless you\'re prepared to lose all the money you invest."'
            }

        return {'status': 'PASS', 'message': 'High-risk warnings present', 'legal_source': self.legal_source}
