import re


class PartiesIdentifiedGate:
    def __init__(self):
        self.name = "parties_identified"
        self.severity = "critical"
        self.legal_source = "Fundamental Contract Law"
    
    def _is_relevant(self, text):
        return 'agreement' in (text or '').lower()
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a formal NDA contract',
                'legal_source': self.legal_source
            }
        
        # Check for party identification patterns
        party_patterns = [
            r'(?:between|made by).*(?:\(.*\)|limited|ltd|plc|llp)',
            r'registered.*(?:number|office)',
            r'disclos(?:er|ing party).*\(',
            r'recipient.*\('
        ]
        
        has_parties = any(re.search(p, text, re.IGNORECASE) for p in party_patterns)
        
        if has_parties:
            return {'status': 'PASS', 'severity': 'none', 'message': 'Parties clearly identified', 'legal_source': self.legal_source}
        
        return {
            'status': 'FAIL',
            'severity': 'critical',
            'message': 'Parties not clearly identified',
            'legal_source': self.legal_source,
            'suggestion': 'State full legal names, registered office addresses, and company numbers for all parties'
        }
