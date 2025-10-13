import re


class ReturnDestructionGate:
    def __init__(self):
        self.name = "return_destruction"
        self.severity = "medium"
        self.legal_source = "Best practice (strengthens confidentiality claim)"
    
    def _is_relevant(self, text):
        return 'confidential' in (text or '').lower()
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a confidentiality agreement',
                'legal_source': self.legal_source
            }
        
        return_patterns = [
            r'return.*(?:or|and).*(?:destroy|delete)',
            r'destruction.*confidential',
            r'upon.*(?:request|termination).*return'
        ]
        
        has_return = any(re.search(p, text, re.IGNORECASE) for p in return_patterns)
        
        if has_return:
            return {'status': 'PASS', 'severity': 'none', 'message': 'Return/destruction obligations stated'}
        
        return {
            'status': 'WARNING',
            'severity': 'medium',
            'message': 'No return or destruction clause',
            'suggestion': 'Add: "Upon request, Recipient shall return or destroy all Confidential Information and certify compliance."'
        }

