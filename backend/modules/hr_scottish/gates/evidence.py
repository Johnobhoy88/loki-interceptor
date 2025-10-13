import re


class EvidenceGate:
    def __init__(self):
        self.name = "evidence"
        self.severity = "high"  # Lowered from critical - brief notices may not reference evidence
        self.legal_source = "ACAS Code of Practice, Paragraph 9"
        self.relevance_keywords = ['disciplinary', 'hearing', 'meeting', 'allegations', 'investigation']
        self.patterns = [
            r'evidence',
            r'enclosed',
            r'attached',
            r'documentation',
            r'(?:witness )?statements?',
            r'investigation report'
        ]
    
    def _is_relevant(self, text):
        text_lower = text.lower()
        # Relevant for any disciplinary process (invitations, hearings, outcomes)
        process_keywords = ['disciplinary', 'grievance', 'allegations', 'complaints',
                           'misconduct', 'investigation', 'concerns', 'dismissed',
                           'dismissal', 'terminated', 'warning', 'hearing', 'meeting']
        return any(kw in text_lower for kw in process_keywords)
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a disciplinary investigation or hearing',
                'legal_source': self.legal_source
            }
        
        for pattern in self.patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return {
                    'status': 'PASS',
                    'severity': 'none',
                    'message': 'Evidence or documentation referenced',
                    'legal_source': self.legal_source
                }
        
        return {
            'status': 'FAIL',
            'severity': 'critical',
            'message': 'No evidence or documentation references found',
            'legal_source': self.legal_source,
            'suggestion': 'Refer to the evidence relied upon and state what is attached/enclosed.'
        }
