import re


class ConsiderationGate:
    def __init__(self):
        self.name = "consideration"
        self.severity = "critical"
        self.legal_source = "English Contract Law (not applicable in Scotland)"
    
    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        # Only check for English law unilateral NDAs
        is_english = 'england' in text_lower or 'wales' in text_lower
        is_scottish = 'scotland' in text_lower or 'scots law' in text_lower
        
        if is_scottish:
            return False
        
        # Check if unilateral (one-way)
        is_mutual = bool(re.search(r'both parties|each party|mutual', text_lower))
        
        return is_english and not is_mutual
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable (Scots law or mutual NDA)'}
        
        # Check if executed as deed
        deed_indicators = [
            r'executed as a deed',
            r'signed.*sealed.*delivered',
            r'signed in the presence of.*witness'
        ]
        
        is_deed = any(re.search(p, text, re.IGNORECASE) for p in deed_indicators)
        
        # Check for stated consideration
        has_consideration = bool(re.search(r'in consideration of', text, re.IGNORECASE))
        
        if is_deed or has_consideration:
            return {'status': 'PASS', 'severity': 'none', 'message': 'Consideration present or executed as deed'}
        
        return {
            'status': 'FAIL',
            'severity': 'critical',
            'message': 'Unilateral NDA under English law lacks consideration',
            'legal_source': self.legal_source,
            'suggestion': 'Either: (1) Execute as a deed with witness, or (2) State nominal consideration: "In consideration of £1 and other valuable consideration"'
        }

