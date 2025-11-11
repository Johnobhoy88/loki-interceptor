"""Best Execution Policy Gate - COBS 11.2A"""
import re

class BestExecutionGate:
    def __init__(self):
        self.name = "best_execution"
        self.severity = "high"
        self.legal_source = "FCA COBS 11.2A (Best Execution)"

    def _is_relevant(self, text):
        exec_terms = ['execution', 'order handling', 'trading', 'venue', 'execution policy']
        return any(term in text.lower() for term in exec_terms)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'legal_source': self.legal_source}

        has_policy = bool(re.search(r'(?:best\s+)?execution\s+policy', text, re.IGNORECASE))
        has_factors = bool(re.search(r'execution\s+factor', text, re.IGNORECASE))

        if not has_policy:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Execution discussed but no best execution policy reference',
                'legal_source': self.legal_source,
                'suggestion': 'Reference best execution policy and execution factors'
            }

        return {'status': 'PASS', 'message': 'Best execution policy referenced', 'legal_source': self.legal_source}
