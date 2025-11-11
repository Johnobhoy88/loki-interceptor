"""Past Performance Warnings Gate - COBS 4.6"""
import re

class PastPerformanceWarningsGate:
    def __init__(self):
        self.name = "past_performance_warnings"
        self.severity = "high"
        self.legal_source = "FCA COBS 4.6 (Past Performance)"

    def _is_relevant(self, text):
        perf_terms = ['past performance', 'historical return', 'track record', 'performance history']
        return any(term in text.lower() for term in perf_terms)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'legal_source': self.legal_source}

        required_warning = "past performance is not a reliable indicator of future results"

        if required_warning.lower() not in text.lower():
            return {
                'status': 'FAIL',
                'severity': 'high',
                'message': 'Past performance shown without required warning',
                'legal_source': self.legal_source,
                'suggestion': 'Include: "Past performance is not a reliable indicator of future results"'
            }

        return {'status': 'PASS', 'message': 'Past performance warnings present', 'legal_source': self.legal_source}
