import re


class SuspensionGate:
    def __init__(self):
        self.name = "suspension"
        self.severity = "high"
        self.legal_source = "ACAS Code of Practice (Disciplinary & Grievance)"
    
    def _is_relevant(self, text):
        return 'suspend' in text.lower()
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not involve suspension during investigation',
                'legal_source': self.legal_source
            }
        
        # Check if suspension is stated as paid
        if re.search(r'(?:paid|full pay).*suspen|suspen.*(?:paid|full pay)', text, re.IGNORECASE):
            return {'status': 'PASS', 'severity': 'none', 'message': 'Suspension stated as paid', 'spans': [], 'legal_source': self.legal_source}
        
        # Check for unpaid suspension (problematic)
        unpaid_rx = r'unpaid.*suspen|suspen.*without pay'
        if re.search(unpaid_rx, text, re.IGNORECASE):
            spans = []
            for m in re.finditer(unpaid_rx, text, re.IGNORECASE):
                spans.append({
                    'type': 'unpaid_suspension',
                    'start': m.start(),
                    'end': m.end(),
                    'text': m.group(),
                    'severity': 'high'
                })
            return {
                'status': 'FAIL',
                'severity': 'high',
                'message': 'Unpaid suspension mentioned - likely unlawful',
                'spans': spans,
                'suggestion': 'Suspension should normally be on full pay during investigation.'
            }
        
        return {
            'status': 'WARNING',
            'severity': 'medium',
            'message': 'Suspension mentioned but pay status unclear',
            'spans': [],
            'suggestion': 'Clarify: "You will be suspended on full pay pending investigation."',
            'legal_source': self.legal_source
        }
