import re


class WithdrawalConsentGate:
    def __init__(self):
        self.name = "withdrawal_consent"
        self.severity = "high"
        self.legal_source = "GDPR Article 7(3)"
    
    def _is_relevant(self, text):
        return 'consent' in (text or '').lower()
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not involve consent or consent withdrawal mechanisms',
                'legal_source': self.legal_source
            }
        
        withdrawal_patterns = [
            r'withdraw.*consent',
            r'opt.*out',
            r'unsubscribe',
            r'revoke.*consent'
        ]
        
        if any(re.search(p, text, re.IGNORECASE) for p in withdrawal_patterns):
            return {'status': 'PASS', 'severity': 'none', 'message': 'Consent withdrawal mechanism stated'}
        
        return {
            'status': 'FAIL',
            'severity': 'high',
            'message': 'Consent mentioned but no withdrawal mechanism',
            'legal_source': self.legal_source,
            'suggestion': 'Add: "You can withdraw consent at any time by contacting us or using the unsubscribe link."'
        }

