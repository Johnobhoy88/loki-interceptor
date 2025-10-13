import re


class ConfidentialityGate:
    def __init__(self):
        self.name = "confidentiality"
        self.severity = "high"
        self.legal_source = "ACAS Code of Practice (Disciplinary & Grievance)"
        self.relevance_keywords = ['disciplinary', 'hearing', 'meeting', 'investigation']

    def _is_relevant(self, text):
        t = (text or '').lower()
        return ('disciplinary' in t or 'investigation' in t) and any(k in t for k in ['hearing', 'meeting'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not involve disciplinary or HR processes',
                'legal_source': self.legal_source
            }

        if re.search(r'confidential', text, re.IGNORECASE):
            return {'status': 'PASS', 'severity': 'none', 'message': 'Confidentiality of the process is stated', 'legal_source': self.legal_source}
        return {'status': 'FAIL', 'severity': 'high', 'message': 'No statement about confidentiality of the process', 'legal_source': self.legal_source}
