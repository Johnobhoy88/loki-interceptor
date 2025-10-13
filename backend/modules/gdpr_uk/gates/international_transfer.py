import re


class InternationalTransferGate:
    def __init__(self):
        self.name = "international_transfer"
        self.severity = "high"
        self.legal_source = "GDPR Article 44-49"
    
    def _is_relevant(self, text):
        text_lower = text.lower()
        return any(kw in text_lower for kw in ['transfer', 'international', 'outside', 'third country'])
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not involve international data transfers',
                'legal_source': self.legal_source
            }
        
        transfer_mentions = re.search(r'outside.*(?:uk|eu|eea)|international.*transfer|third countr', text, re.IGNORECASE)
        
        if not transfer_mentions:
            return {'status': 'PASS', 'severity': 'none', 'message': 'No international transfers mentioned'}
        
        # Check for safeguards
        safeguard_patterns = [
            r'adequacy decision',
            r'standard.*contractual.*clauses',
            r'binding.*corporate.*rules',
            r'safeguards.*in place'
        ]
        
        if any(re.search(p, text, re.IGNORECASE) for p in safeguard_patterns):
            return {'status': 'PASS', 'severity': 'none', 'message': 'International transfer safeguards stated'}
        
        return {
            'status': 'FAIL',
            'severity': 'high',
            'message': 'International data transfers mentioned without safeguards',
            'legal_source': self.legal_source,
            'suggestion': 'State safeguards: adequacy decisions, standard contractual clauses, or other legal mechanisms.'
        }

