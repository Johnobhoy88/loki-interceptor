import re


class WitnessStatementsGate:
    def __init__(self):
        self.name = "witness_statements"
        self.severity = "medium"
        self.legal_source = "ACAS Code of Practice (Disciplinary & Grievance)"
    
    def _is_relevant(self, text):
        text_lower = text.lower()
        # ONLY relevant for outcome letters where witnesses were involved
        outcome_indicators = ['warning', 'dismissal', 'dismissed', 'terminated', 'terminate', 'decision has been made', 'outcome', 'concluded']
        witness_context = any(kw in text_lower for kw in ['witnessed', 'reported by', 'colleague', 'manager observed'])
        return any(ind in text_lower for ind in outcome_indicators) and witness_context
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a disciplinary investigation',
                'legal_source': self.legal_source
            }
        
        statement_patterns = [r'witness statement', r'statement from', r'testimony', r'account from']
        
        for pattern in statement_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return {'status': 'PASS', 'severity': 'none', 'message': 'Witness evidence mentioned', 'legal_source': self.legal_source}
        
        return {
            'status': 'WARNING',
            'severity': 'medium',
            'message': 'Allegations involve others but no witness statements referenced',
            'suggestion': 'Include witness statements in evidence provided.',
            'legal_source': self.legal_source
        }
