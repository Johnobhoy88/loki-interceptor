import re


class BreachNotificationGate:
    def __init__(self):
        self.name = "breach_notification"
        self.severity = "medium"
        self.legal_source = "GDPR Article 33-34"
    
    def _is_relevant(self, text):
        text_lower = text.lower()
        return 'privacy' in text_lower or 'data protection' in text_lower
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not discuss data breaches or breach notification procedures',
                'legal_source': self.legal_source
            }
        
        breach_patterns = [
            r'(?:data )?breach',
            r'security incident',
            r'notify.*(?:ico|supervisory)',
            r'breach.*notification'
        ]
        
        if any(re.search(p, text, re.IGNORECASE) for p in breach_patterns):
            return {'status': 'PASS', 'severity': 'none', 'message': 'Breach notification process mentioned'}
        
        return {
            'status': 'WARNING',
            'severity': 'medium',
            'message': 'No data breach notification process stated',
            'suggestion': 'Add: "In the event of a data breach, we will notify affected individuals and the ICO as required."'
        }
