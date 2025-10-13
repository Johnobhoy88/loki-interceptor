import re


class PreviousWarningsGate:
    def __init__(self):
        self.name = "previous_warnings"
        self.severity = "medium"
        self.legal_source = "ACAS Code of Practice (Disciplinary & Grievance)"
    
    def _is_relevant(self, text):
        text_lower = text.lower()
        return any(kw in text_lower for kw in ['dismissal', 'termination', 'terminated'])
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a disciplinary sanction decision',
                'legal_source': self.legal_source
            }
        
        # Check if it's gross misconduct (no warnings needed)
        if 'gross misconduct' in text.lower():
            return {'status': 'PASS', 'severity': 'none', 'message': 'Gross misconduct - warnings not required', 'legal_source': self.legal_source}
        
        # Check for reference to previous warnings
        warning_refs = [r'previous warning', r'final warning', r'earlier warning', r'warned on']
        
        for pattern in warning_refs:
            if re.search(pattern, text, re.IGNORECASE):
                return {'status': 'PASS', 'severity': 'none', 'message': 'Previous warnings referenced', 'legal_source': self.legal_source}
        
        return {
            'status': 'WARNING',
            'severity': 'medium',
            'message': 'Dismissal without reference to previous warnings',
            'suggestion': 'For non-gross misconduct, reference prior warnings: "Following your final written warning..."',
            'legal_source': self.legal_source
        }
