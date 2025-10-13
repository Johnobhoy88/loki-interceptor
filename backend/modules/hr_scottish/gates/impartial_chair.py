import re


class ImpartialChairGate:
    def __init__(self):
        self.name = "impartial_chair"
        self.severity = "high"
        self.legal_source = "ACAS Code of Practice (impartiality)"
        self.relevance_keywords = ['disciplinary', 'hearing', 'meeting']

    def _is_relevant(self, text):
        t = (text or '').lower()
        return 'disciplinary' in t and any(k in t for k in self.relevance_keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not describe a disciplinary hearing process',
                'legal_source': self.legal_source
            }

        patterns = [r'(?:impartial|independent) (?:chair|manager)', r'not previously involved', r'fair and unbiased']
        if any(re.search(p, text, re.IGNORECASE) for p in patterns):
            return {'status': 'PASS', 'severity': 'none', 'message': 'Impartial chair/manager referenced', 'legal_source': self.legal_source}
        return {
            'status': 'FAIL',
            'severity': 'high',
            'message': 'No reassurance about an impartial chair or lack of prior involvement',
            'legal_source': self.legal_source,
            'suggestion': 'State that the hearing will be chaired by someone impartial and not previously involved.'
        }
