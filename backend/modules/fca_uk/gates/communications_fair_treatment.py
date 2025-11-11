"""Fair Treatment Communications Gate - PRIN 2A.2"""
import re

class CommunicationsFairTreatmentGate:
    def __init__(self):
        self.name = "communications_fair_treatment"
        self.severity = "high"
        self.legal_source = "FCA PRIN 2A.2 (Act in Good Faith)"

    def _is_relevant(self, text):
        return len(text.split()) > 50  # Check documents with substance

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'legal_source': self.legal_source}

        red_flags = [
            r'(?:fine\s+print|small\s+print)',
            r'(?:hidden|buried|obscured)',
            r'(?:mislead|deceptive|false)',
            r'(?:manipulative|pressure|coerce)',
            r'(?:exploit|take\s+advantage)'
        ]

        violations = [flag for flag in red_flags if re.search(flag, text, re.IGNORECASE)]

        if violations:
            return {
                'status': 'FAIL',
                'severity': 'high',
                'message': 'Communication fails fair treatment test',
                'legal_source': self.legal_source,
                'suggestion': 'Remove misleading, manipulative, or exploitative content'
            }

        return {'status': 'PASS', 'message': 'Fair treatment standards met', 'legal_source': self.legal_source}
