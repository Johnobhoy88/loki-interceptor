import re


class GoverningLawGate:
    def __init__(self):
        self.name = "governing_law"
        self.severity = "critical"
        self.legal_source = "UK Contract Law"
    
    def _is_relevant(self, text):
        return 'agreement' in (text or '').lower() or 'nda' in (text or '').lower()
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a non-disclosure or confidentiality agreement',
                'legal_source': self.legal_source
            }
        
        uk_jurisdictions = [
            r'england.*wales',
            r'scottish.*law',
            r'scotland',
            r'northern.*ireland'
        ]
        
        has_uk_law = any(re.search(p, text, re.IGNORECASE) for p in uk_jurisdictions)
        
        if has_uk_law:
            return {'status': 'PASS', 'severity': 'none', 'message': 'UK governing law specified', 'legal_source': self.legal_source}
        
        return {
            'status': 'FAIL',
            'severity': 'critical',
            'message': 'No UK governing law clause',
            'legal_source': self.legal_source,
            'suggestion': 'Add: "This Agreement shall be governed by the laws of England and Wales" (or Scotland/Northern Ireland as appropriate)'
        }
