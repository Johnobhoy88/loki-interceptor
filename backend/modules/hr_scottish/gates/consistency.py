import re


class ConsistencyGate:
    def __init__(self):
        self.name = "consistency"
        self.severity = "low"
        self.legal_source = "ACAS Code of Practice (Disciplinary & Grievance)"
    
    def _is_relevant(self, text):
        return 'disciplinary' in text.lower() or 'grievance' in text.lower()
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not describe disciplinary sanctions or procedures',
                'legal_source': self.legal_source
            }
        
        policy_refs = [r'in accordance with', r'company policy', r'procedure', r'handbook']
        
        for pattern in policy_refs:
            if re.search(pattern, text, re.IGNORECASE):
                return {'status': 'PASS', 'severity': 'none', 'message': 'Policy/procedure referenced', 'legal_source': self.legal_source}
        
        return {
            'status': 'WARNING',
            'severity': 'low',
            'message': 'No reference to company policy or procedure',
            'suggestion': 'Reference: "In accordance with our disciplinary procedure..."',
            'legal_source': self.legal_source
        }
