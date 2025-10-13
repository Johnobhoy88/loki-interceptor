import re


class DismissalGate:
    def __init__(self):
        self.name = "dismissal"
        self.severity = "critical"
        self.legal_source = "ACAS Code of Practice (Disciplinary & Grievance)"
        self.triggers = ['gross misconduct', 'theft', 'fraud', 'violence', 'serious breach']
        
    def _is_relevant(self, text):
        text_lower = text.lower()
        return 'disciplinary' in text_lower and any(trigger in text_lower for trigger in self.triggers)
    
    def check(self, text, document_type):
        text_lower = text.lower()
        
        # Check if serious misconduct is mentioned
        has_trigger = any(trigger in text_lower for trigger in self.triggers)
        
        if not has_trigger:
            return {'status': 'PASS', 'severity': 'none', 'message': 'No serious misconduct referenced.', 'legal_source': self.legal_source}
        
        # If serious misconduct mentioned, check for dismissal warning
        has_warning = bool(re.search(r'(?:dismissal|termination|summary dismissal)', text_lower))
        
        if has_warning:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Appropriate warning present for serious misconduct.',
                'legal_source': self.legal_source
            }
        
        return {
            'status': 'FAIL',
            'severity': 'critical',
            'message': 'Serious misconduct alleged but no warning that dismissal is a potential outcome',
            'suggestion': 'Add: "Please note that a potential outcome of this hearing could be summary dismissal."',
            'legal_source': self.legal_source
        }
