import re


class PermittedPurposeGate:
    def __init__(self):
        self.name = "permitted_purpose"
        self.severity = "high"
        self.legal_source = "Strengthens reasonableness of restrictions"
    
    def _is_relevant(self, text):
        return 'confidential' in (text or '').lower()
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a confidentiality agreement',
                'legal_source': self.legal_source
            }
        
        purpose_patterns = [
            r'(?:solely|only).*for.*purpose of',
            r'permitted purpose',
            r'purpose.*(?:evaluating|discussing|negotiating)'
        ]
        
        has_purpose = any(re.search(p, text, re.IGNORECASE) for p in purpose_patterns)
        
        if has_purpose:
            # Check if purpose is overly broad
            if re.search(r'for.*(?:general|any|all).*(?:business|commercial).*purpose', text, re.IGNORECASE):
                return {
                    'status': 'WARNING',
                    'severity': 'medium',
                    'message': 'Permitted Purpose is very broad',
                    'suggestion': 'Narrow purpose: "solely for evaluating a potential acquisition of..." rather than "general business purposes"'
                }
            
            return {'status': 'PASS', 'severity': 'none', 'message': 'Permitted Purpose defined', 'legal_source': self.legal_source}
        
        return {
            'status': 'WARNING',
            'severity': 'high',
            'message': 'No Permitted Purpose stated',
            'suggestion': 'Define narrow purpose: "Recipient shall use Confidential Information solely for the purpose of [specific transaction/evaluation]"',
            'legal_source': self.legal_source
        }
