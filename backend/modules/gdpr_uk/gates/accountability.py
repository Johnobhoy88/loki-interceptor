import re


class AccountabilityGate:
    def __init__(self):
        self.name = 'gdpr_accountability_controller'
        self.severity = 'high'
        self.legal_source = 'UK GDPR Articles 5(2), 13/14'
        self.relevance_keywords = ['controller', 'we are', 'who we are', 'privacy']

    def _is_relevant(self, text):
        t = (text or '').lower()
        return 'privacy' in t or 'controller' in t

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not discuss data protection accountability or governance',
                'legal_source': self.legal_source
            }

        patterns = [r'controller', r'who we are', r'contact details', r'registered address']
        if any(re.search(p, text, re.IGNORECASE) for p in patterns):
            return {'status': 'PASS', 'severity': 'none', 'message': 'Controller/accountability information provided'}
        return {'status': 'FAIL', 'severity': 'high', 'message': 'No controller/accountability information provided'}

