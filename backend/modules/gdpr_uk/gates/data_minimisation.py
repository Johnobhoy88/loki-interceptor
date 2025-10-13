import re


class DataMinimisationGate:
    def __init__(self):
        self.name = "data_minimisation"
        self.severity = "medium"
        self.legal_source = "GDPR Article 5(1)(c)"
    
    def _is_relevant(self, text):
        text_lower = text.lower()
        return 'collect' in text_lower and 'data' in text_lower
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not discuss data collection or data minimisation principles',
                'legal_source': self.legal_source
            }
        
        minimisation_patterns = [
            r'only.*(?:necessary|required|essential)',
            r'minimal.*data',
            r'limited to',
            r'solely.*(?:purpose|necessary)'
        ]
        
        for pattern in minimisation_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return {'status': 'PASS', 'severity': 'none', 'message': 'Data minimisation principle stated'}
        
        return {
            'status': 'WARNING',
            'severity': 'medium',
            'message': 'No data minimisation statement',
            'suggestion': 'Add: "We only collect data necessary for the stated purposes."'
        }
