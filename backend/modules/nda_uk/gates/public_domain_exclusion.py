import re


class PublicDomainExclusionGate:
    def __init__(self):
        self.name = "public_domain_exclusion"
        self.severity = "high"
        self.legal_source = "Common Law - information must have quality of confidence"
    
    def _is_relevant(self, text):
        return 'confidential' in (text or '').lower()
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not an NDA',
                'legal_source': self.legal_source
            }
        
        public_domain_patterns = [
            r'(?:is or becomes|becomes).*(?:public|publicly).*(?:available|known)',
            r'in the public domain',
            r'generally available to the public'
        ]
        
        has_exclusion = any(re.search(p, text, re.IGNORECASE) for p in public_domain_patterns)
        
        if has_exclusion:
            return {'status': 'PASS', 'severity': 'none', 'message': 'Public domain exclusion present', 'legal_source': self.legal_source}
        
        return {
            'status': 'FAIL',
            'severity': 'high',
            'message': 'No public domain exclusion',
            'legal_source': self.legal_source,
            'suggestion': 'Add: "Confidential Information does not include information that is or becomes publicly available other than through breach of this Agreement."'
        }
