import re


class MitigatingCircumstancesGate:
    def __init__(self):
        self.name = "mitigating_circumstances"
        self.severity = "high"
        self.legal_source = "ACAS Code of Practice (Disciplinary & Grievance)"
        self.relevance_keywords = ['disciplinary', 'hearing', 'meeting']

    def _is_relevant(self, text):
        t = (text or '').lower()
        return 'disciplinary' in t and any(k in t for k in self.relevance_keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a disciplinary hearing or outcome',
                'legal_source': self.legal_source
            }

        patterns = [r'mitigating circumstances', r'consider(?:ation)? of (?:mitigating|personal) factors', r'length of service', r'previous record']
        if any(re.search(p, text, re.IGNORECASE) for p in patterns):
            return {'status': 'PASS', 'severity': 'none', 'message': 'Mitigating/personal circumstances considered', 'legal_source': self.legal_source}
        return {'status': 'FAIL', 'severity': 'high', 'message': 'No reference to considering mitigating circumstances', 'legal_source': self.legal_source}
