import re


class AccuracyGate:
    def __init__(self):
        self.name = 'gdpr_accuracy'
        self.severity = 'high'
        self.legal_source = 'UK GDPR Article 5(1)(d)'
        self.relevance_keywords = ['accurate', 'update', 'correct', 'rectify']

    def _is_relevant(self, text):
        t = (text or '').lower()
        return any(k in t for k in ['accurate', 'update', 'correct', 'rectify']) or 'privacy' in t

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not discuss data accuracy or correction procedures',
                'legal_source': self.legal_source
            }

        patterns = [r'keep.*data.*accurate', r'update (?:your )?information', r'how to request corrections?']
        if any(re.search(p, text, re.IGNORECASE) for p in patterns):
            return {'status': 'PASS', 'severity': 'none', 'message': 'Accuracy and correction mechanisms described'}
        return {'status': 'FAIL', 'severity': 'high', 'message': 'No reference to maintaining accuracy or rectification process'}

