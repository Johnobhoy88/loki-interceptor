import re


class AppealGate:
    def __init__(self):
        self.name = "appeal"
        self.severity = "critical"
        self.legal_source = "ACAS Code of Practice, Paragraph 21"
        
    def _is_relevant(self, text):
        text_lower = text.lower()
        # Only relevant for outcome letters (warnings, dismissals, decisions)
        outcome_indicators = ['warning', 'dismissal', 'dismissed', 'terminated', 'terminate', 'decision', 'outcome', 'concluded', 'uphold']
        return any(ind in text_lower for ind in outcome_indicators)
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a disciplinary outcome or dismissal letter',
                'legal_source': self.legal_source
            }
        
        appeal_patterns = [
            r'right.*appeal',
            r'appeal.*decision',
            r'wish to appeal'
        ]
        
        for pattern in appeal_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return {
                    'status': 'PASS',
                    'severity': 'none',
                    'message': 'Right of appeal mentioned',
                    'legal_source': self.legal_source
                }
        
        return {
            'status': 'FAIL',
            'severity': 'critical',
            'message': 'No right of appeal stated',
            'legal_source': self.legal_source,
            'suggestion': 'Add: "You have the right to appeal this decision. Please submit your appeal in writing within [X] days."'
        }
