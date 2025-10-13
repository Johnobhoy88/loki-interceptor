import re


class OutcomeReasonsGate:
    def __init__(self):
        self.name = "outcome_reasons"
        self.severity = "high"
        self.legal_source = "ACAS Code of Practice (Disciplinary & Grievance)"
    
    def _is_relevant(self, text):
        text_lower = text.lower()
        outcome_indicators = ['warning', 'dismissal', 'dismissed', 'terminated', 'terminate', 'decision', 'outcome', 'concluded', 'uphold']
        return any(ind in text_lower for ind in outcome_indicators)
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a disciplinary outcome decision',
                'legal_source': self.legal_source
            }
        
        reason_patterns = [r'following.*investigation', r'reason.*decision', r'found that', r'concluded that']
        
        for pattern in reason_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return {'status': 'PASS', 'severity': 'none', 'message': 'Reasons for decision stated', 'legal_source': self.legal_source}
        
        return {
            'status': 'FAIL',
            'severity': 'high',
            'message': 'Outcome letter missing clear reasons for decision',
            'suggestion': 'State: "Following investigation, we found that... Our decision is based on..."',
            'legal_source': self.legal_source
        }
