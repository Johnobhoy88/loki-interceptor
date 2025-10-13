import re


class GdprComplianceGate:
    def __init__(self):
        self.name = "gdpr_compliance"
        self.severity = "high"
        self.legal_source = "UK GDPR; Data Protection Act 2018"
    
    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        # Check if likely to involve personal data
        return any(kw in text_lower for kw in ['employee', 'customer', 'client', 'personal', 'data'])
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not an NDA involving personal data',
                'legal_source': self.legal_source
            }
        
        gdpr_patterns = [
            r'(?:uk )?gdpr',
            r'data protection',
            r'personal data.*process',
            r'data controller.*processor'
        ]
        
        has_gdpr = any(re.search(p, text, re.IGNORECASE) for p in gdpr_patterns)
        
        if has_gdpr:
            return {'status': 'PASS', 'severity': 'none', 'message': 'GDPR/data protection provisions present', 'legal_source': self.legal_source}
        
        return {
            'status': 'FAIL',
            'severity': 'high',
            'message': 'NDA likely involves personal data but no GDPR provisions',
            'legal_source': self.legal_source,
            'suggestion': 'Add: "Where Confidential Information includes Personal Data, Recipient shall process such data in compliance with UK GDPR and only for the Permitted Purpose."'
        }
