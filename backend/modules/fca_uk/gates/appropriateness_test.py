"""Appropriateness Test Requirements Gate - COBS 10"""
import re

class AppropriatenessTestGate:
    def __init__(self):
        self.name = "appropriateness_test"
        self.severity = "high"
        self.legal_source = "FCA COBS 10 (Appropriateness)"

    def _is_relevant(self, text):
        terms = ['complex', 'derivative', 'execution only', 'non-advised', 'appropriateness']
        return any(term in text.lower() for term in terms)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'legal_source': self.legal_source}

        has_test = bool(re.search(r'appropriateness\s+(?:test|assessment|check)', text, re.IGNORECASE))
        is_complex = bool(re.search(r'complex', text, re.IGNORECASE))

        if is_complex and not has_test:
            return {
                'status': 'FAIL',
                'severity': 'high',
                'message': 'Complex product without appropriateness test',
                'legal_source': self.legal_source,
                'suggestion': 'COBS 10 requires appropriateness assessment for complex products'
            }

        return {'status': 'PASS', 'message': 'Appropriateness requirements met', 'legal_source': self.legal_source}
