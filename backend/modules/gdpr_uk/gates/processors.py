import re


class ProcessorsGate:
    def __init__(self):
        self.name = 'gdpr_processors_third_parties'
        self.severity = 'high'
        self.legal_source = 'UK GDPR Articles 28, 13/14'
        self.relevance_keywords = ['share', 'third parties', 'service providers', 'processors']

    def _is_relevant(self, text):
        t = (text or '').lower()
        return any(k in t for k in ['share', 'third', 'processor', 'service provider'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not involve third-party data processors',
                'legal_source': self.legal_source
            }

        patterns = [r'third part(y|ies)', r'processors?', r'service providers?', r'share (?:your )?data']
        if any(re.search(p, text, re.IGNORECASE) for p in patterns):
            return {'status': 'PASS', 'severity': 'none', 'message': 'Third parties/processors and sharing referenced'}
        return {'status': 'FAIL', 'severity': 'high', 'message': 'No information about processors/third parties and data sharing'}

