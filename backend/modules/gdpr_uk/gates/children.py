import re


class ChildrenDataGate:
    def __init__(self):
        self.name = 'gdpr_children_data'
        self.severity = 'high'
        self.legal_source = 'UK GDPR Article 8'
        self.relevance_keywords = ['children', 'child', 'under 13', 'under 16', 'minor', 'age']

    def _is_relevant(self, text):
        t = (text or '').lower()
        return any(k in t for k in ['children', 'child', 'under 13', 'under 16', 'minor'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not involve children or processing of children's data',
                'legal_source': self.legal_source
            }

        patterns = [r'parental consent', r'age verification', r'consent of (?:a )?parent', r'guardian']
        if any(re.search(p, text, re.IGNORECASE) for p in patterns):
            return {'status': 'PASS', 'severity': 'none', 'message': 'Children’s data protections (consent/verification) referenced'}
        return {'status': 'FAIL', 'severity': 'high', 'message': 'Children’s data referenced without parental consent/age verification'}

