import re


class InternationalTransfersGate:
    def __init__(self):
        self.name = 'gdpr_international_transfers'
        self.severity = 'high'
        self.legal_source = 'UK GDPR Chapter V'
        self.relevance_keywords = ['transfer', 'international', 'outside uk', 'outside eea', 'overseas']

    def _is_relevant(self, text):
        t = (text or '').lower()
        return any(k in t for k in ['transfer', 'international', 'outside uk', 'outside eea', 'overseas'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not involve international data transfers outside UK/EEA',
                'legal_source': self.legal_source
            }

        patterns = [r'adequac(y|ies)', r'standard contractual clauses|sccs?', r'appropriate safeguards', r'transfer risk assessment']
        if any(re.search(p, text, re.IGNORECASE) for p in patterns):
            return {'status': 'PASS', 'severity': 'none', 'message': 'International transfers and safeguards described'}
        return {'status': 'FAIL', 'severity': 'high', 'message': 'International transfers not accompanied by safeguards (adequacy, SCCs)'}

