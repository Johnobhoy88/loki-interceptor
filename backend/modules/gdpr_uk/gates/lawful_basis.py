import re


class LawfulBasisGate:
    def __init__(self):
        self.name = "lawful_basis"
        self.severity = "critical"
        self.legal_source = "GDPR Article 6"
    
    def _is_relevant(self, text):
        text_lower = text.lower()
        return any(kw in text_lower for kw in ['privacy', 'data', 'personal information', 'processing'])
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not discuss personal data processing or lawful bases',
                'legal_source': self.legal_source
            }
        
        lawful_bases = [
            r'legitimate interest',
            r'legal obligation',
            r'contract.*necessary',
            r'vital interest',
            r'public task',
            r'consent.*process'
        ]
        
        for pattern in lawful_bases:
            if re.search(pattern, text, re.IGNORECASE):
                return {'status': 'PASS', 'severity': 'none', 'message': 'Lawful basis for processing stated'}
        
        return {
            'status': 'FAIL',
            'severity': 'critical',
            'message': 'No lawful basis for data processing stated',
            'legal_source': self.legal_source,
            'suggestion': 'State lawful basis: consent, contract, legal obligation, legitimate interest, vital interest, or public task.'
        }
