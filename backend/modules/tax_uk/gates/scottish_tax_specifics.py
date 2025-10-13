import re


class ScottishTaxSpecificsGate:
    def __init__(self):
        self.name = "scottish_tax_specifics"
        self.severity = "medium"
        self.legal_source = "Scotland Act 2016; Scottish income tax bands"
    
    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return 'scotland' in text_lower or 'scottish' in text_lower
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not reference Scottish tax or Scotland-specific tax rules',
                'legal_source': self.legal_source
            }
        
        # Check for Scottish income tax mentions
        if re.search(r'scottish.*(?:income tax|tax rate|tax band)', text, re.IGNORECASE):
            # Verify it mentions different rates from rUK
            if not re.search(r'different.*(?:rate|band)|starter.*rate|intermediate', text, re.IGNORECASE):
                return {
                    'status': 'WARNING',
                    'severity': 'medium',
                    'message': 'Scottish income tax mentioned but rates not clarified',
                    'legal_source': self.legal_source,
                    'suggestion': "Scottish taxpayers have different income tax rates: Starter (19%), Basic (20%), Intermediate (21%), Higher (42%), Top (47%)"
                }
        
        return {'status': 'PASS', 'severity': 'none', 'message': 'Scottish tax information appropriate'}

