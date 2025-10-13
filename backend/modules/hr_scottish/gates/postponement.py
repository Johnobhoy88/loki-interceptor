import re


class PostponementGate:
    def __init__(self):
        self.name = "postponement"
        self.severity = "high"
        self.legal_source = "Employment Relations Act 1999 s.10(5)"
        self.relevance_keywords = ['disciplinary', 'hearing', 'meeting']

    def _is_relevant(self, text):
        t = (text or '').lower()
        return 'disciplinary' in t and any(k in t for k in self.relevance_keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not involve disciplinary meeting scheduling',
                'legal_source': self.legal_source
            }

        patterns = [r'postpone', r'rearrange', r'reschedule', r'adjourn', r'if.*(companion|representative).*unavailable']
        if any(re.search(p, text, re.IGNORECASE) for p in patterns):
            return {'status': 'PASS', 'severity': 'none', 'message': 'Right to reasonable postponement mentioned', 'legal_source': self.legal_source}
        return {
            'status': 'FAIL',
            'severity': 'high',
            'message': 'No right to request postponement if companion unavailable',
            'legal_source': self.legal_source,
            'suggestion': 'State that the meeting may be postponed if the companion is unavailable on the proposed date.'
        }
