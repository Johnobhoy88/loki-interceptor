import re


class RepresentationChoiceGate:
    def __init__(self):
        self.name = "representation_choice"
        self.severity = "medium"
        self.legal_source = "Employment Relations Act 1999, Section 10"
    
    def _is_relevant(self, text):
        return 'accompan' in text.lower() or 'representative' in text.lower()
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a disciplinary or grievance procedure notice',
                'legal_source': self.legal_source
            }
        
        # Check for restrictions on choice
        restrictive_patterns = [
            r'(?:hr|management) approved',
            r'must be from.*department',
            r'cannot be.*union',
            r'not.*legal representative'
        ]
        
        for pattern in restrictive_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return {
                    'status': 'WARNING',
                    'severity': 'medium',
                    'message': 'Potentially restrictive language on choice of companion',
                    'suggestion': 'Employee should freely choose work colleague or trade union rep.',
                    'legal_source': self.legal_source
                }
        
        return {'status': 'PASS', 'severity': 'none', 'message': 'No restrictions on companion choice', 'legal_source': self.legal_source}
