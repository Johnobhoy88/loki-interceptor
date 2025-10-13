import re


class ChildrenDataGate:
    def __init__(self):
        self.name = "children_data"
        self.severity = "critical"
        self.legal_source = "GDPR Article 8"
    
    def _is_relevant(self, text):
        text_lower = text.lower()
        return any(kw in text_lower for kw in ['child', 'children', 'minor', 'under 13', 'under 16', 'parental'])
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not involve processing of children\'s personal data',
                'legal_source': self.legal_source
            }
        
        child_safeguards = [
            r'parental.*consent',
            r'age verification',
            r'over.*(?:13|16)',
            r'guardian.*permission'
        ]
        
        if any(re.search(p, text, re.IGNORECASE) for p in child_safeguards):
            return {'status': 'PASS', 'severity': 'none', 'message': 'Child data safeguards mentioned'}
        
        return {
            'status': 'FAIL',
            'severity': 'critical',
            'message': 'Children mentioned but no age verification/parental consent safeguards',
            'legal_source': self.legal_source,
            'suggestion': 'State: "Users under 13 require parental consent. We verify age through..."'
        }

