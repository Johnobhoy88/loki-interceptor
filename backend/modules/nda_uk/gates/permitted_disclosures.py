import re


class PermittedDisclosuresGate:
    def __init__(self):
        self.name = "permitted_disclosures"
        self.severity = "high"
        self.legal_source = "Common Law; SRA Guidance"
    
    def _is_relevant(self, text):
        return 'confidential' in (text or '').lower()
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a non-disclosure agreement',
                'legal_source': self.legal_source
            }
        
        permitted_patterns = [
            r'(?:required|compelled).*(?:by|under).*law',
            r'court.*order',
            r'regulatory.*(?:authority|requirement)',
            r'legal.*(?:obligation|requirement)'
        ]
        
        has_permitted = any(re.search(p, text, re.IGNORECASE) for p in permitted_patterns)
        
        if has_permitted:
            return {'status': 'PASS', 'severity': 'none', 'message': 'Permitted legal/regulatory disclosures stated', 'legal_source': self.legal_source}
        
        return {
            'status': 'FAIL',
            'severity': 'high',
            'message': 'No exception for legally required disclosures',
            'legal_source': self.legal_source,
            'suggestion': 'Add: "Recipient may disclose Confidential Information to the extent required by law, court order, or regulatory authority."'
        }
