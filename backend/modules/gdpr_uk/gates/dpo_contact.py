import re


class DpoContactGate:
    def __init__(self):
        self.name = "dpo_contact"
        self.severity = "high"
        self.legal_source = "GDPR Article 13(1)(b)"
    
    def _is_relevant(self, text):
        text_lower = text.lower()
        return 'privacy' in text_lower or 'data protection' in text_lower
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a privacy notice requiring DPO contact information',
                'legal_source': self.legal_source
            }
        
        dpo_patterns = [
            r'data protection officer',
            r'\bdpo\b',
            r'privacy.*officer',
            r'dpo@'
        ]
        
        if any(re.search(p, text, re.IGNORECASE) for p in dpo_patterns):
            return {'status': 'PASS', 'severity': 'none', 'message': 'DPO contact information present'}
        
        return {
            'status': 'FAIL',
            'severity': 'high',
            'message': 'No Data Protection Officer contact details',
            'legal_source': self.legal_source,
            'suggestion': 'Provide DPO contact: "Contact our Data Protection Officer at dpo@company.com"'
        }
