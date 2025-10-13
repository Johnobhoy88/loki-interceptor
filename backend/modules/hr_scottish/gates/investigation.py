import re


class InvestigationGate:
    def __init__(self):
        self.name = "investigation"
        self.severity = "high"
        self.legal_source = "ACAS Code, Paragraph 5"
    
    def _is_relevant(self, text):
        text_lower = text.lower()
        # ONLY relevant for outcome letters (warnings, dismissals, decisions)
        outcome_indicators = ['warning', 'dismissal', 'dismissed', 'terminated', 'terminate', 'decision has been made', 'outcome', 'concluded', 'uphold', 'following.*meeting']
        return any(ind in text_lower for ind in outcome_indicators)
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not involve disciplinary investigation procedures',
                'legal_source': self.legal_source
            }
        
        investigation_patterns = [r'investigation', r'investigated', r'enquiry', r'findings', r'investigation report']
        
        for pattern in investigation_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return {'status': 'PASS', 'severity': 'none', 'message': 'Investigation process referenced'}
        
        return {
            'status': 'FAIL',
            'severity': 'high',
            'message': 'No investigation referenced before disciplinary action',
            'legal_source': self.legal_source,
            'suggestion': 'Reference investigation: "Following an investigation into the allegations..."'
        }

