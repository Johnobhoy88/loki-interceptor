import re


class BusinessStructureConsistencyGate:
    def __init__(self):
        self.name = "business_structure_consistency"
        self.severity = "medium"
        self.legal_source = "Companies Act 2006; HMRC terminology"
    
    def _is_relevant(self, text):
        t = text.lower()
        return any(k in t for k in ['sole trader', 'director', 'company', 'limited', 'self-employed', 'partnership'])
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not reference business structures (sole trader, limited company, partnership)',
                'legal_source': self.legal_source
            }
        
        # Check for terminology mismatches
        errors = []
        
        # Sole traders called "directors" or "companies"
        sole_trader_pattern = r'sole trader.*(?:director|company|corporation tax)'
        if re.search(sole_trader_pattern, text, re.IGNORECASE):
            errors.append('Sole traders are not directors and do not pay corporation tax')
        
        # Directors called "self-employed"
        director_pattern = r'director.*self[- ]?employed'
        if re.search(director_pattern, text, re.IGNORECASE):
            errors.append('Directors are not self-employed; they are officers of the company')
        
        # Company owners taking "drawings" (should be salary/dividends)
        drawings_pattern = r'(?:limited company|director).*drawings'
        if re.search(drawings_pattern, text, re.IGNORECASE):
            errors.append('Limited companies use salaries/dividends, not drawings')
        
        if errors:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'Structure terminology issues: {"; ".join(errors)}',
                'legal_source': self.legal_source,
                'suggestion': 'Sole traders: self-employed, take drawings, pay income tax. Directors: company officers, take salary/dividends, company pays corporation tax.'
            }
        
        return {'status': 'PASS', 'severity': 'none', 'message': 'Business structure terminology correct'}
