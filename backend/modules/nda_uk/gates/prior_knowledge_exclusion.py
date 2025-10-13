import re


class PriorKnowledgeExclusionGate:
    def __init__(self):
        self.name = "prior_knowledge_exclusion"
        self.severity = "high"
        self.legal_source = "Common Law principle of reasonableness"
    
    def _is_relevant(self, text):
        return 'confidential' in (text or '').lower()
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not an NDA or confidentiality agreement',
                'legal_source': self.legal_source
            }
        
        prior_knowledge_patterns = [
            r'(?:already|lawfully).*(?:known|possessed).*(?:by|to).*recipient',
            r'in.*possession.*prior to.*disclosure',
            r'independently developed'
        ]
        
        has_exclusion = any(re.search(p, text, re.IGNORECASE) for p in prior_knowledge_patterns)
        
        if has_exclusion:
            return {'status': 'PASS', 'severity': 'none', 'message': 'Prior knowledge/independent development exclusions present', 'legal_source': self.legal_source}
        
        return {
            'status': 'FAIL',
            'severity': 'high',
            'message': 'No prior knowledge or independent development exclusions',
            'legal_source': self.legal_source,
            'suggestion': 'Add: "Excludes information (a) lawfully known to Recipient prior to disclosure; (b) independently developed without reference to Confidential Information."'
        }
