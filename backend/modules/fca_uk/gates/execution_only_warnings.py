"""Execution-Only Warnings Gate - COBS 10.3"""
import re

class ExecutionOnlyWarningsGate:
    def __init__(self):
        self.name = "execution_only_warnings"
        self.severity = "medium"
        self.legal_source = "FCA COBS 10.3 (Execution-Only)"

    def _is_relevant(self, text):
        return 'execution only' in text.lower() or 'execution-only' in text.lower()

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'legal_source': self.legal_source}

        required_warnings = [
            r'no\s+advice',
            r'not\s+(?:assessed|checked)\s+(?:suitability|appropriateness)',
            r'(?:your|own)\s+(?:decision|responsibility)',
            r'(?:may\s+not\s+be\s+)?suitable'
        ]

        warnings_found = sum(1 for warning in required_warnings if re.search(warning, text, re.IGNORECASE))

        if warnings_found < 2:
            return {
                'status': 'WARNING',
                'message': 'Execution-only warnings insufficient',
                'legal_source': self.legal_source,
                'suggestion': 'Warn: no advice given, suitability not assessed, own decision/responsibility'
            }

        return {'status': 'PASS', 'message': 'Execution-only warnings adequate', 'legal_source': self.legal_source}
