import re


class AllowableExpensesGate:
    def __init__(self):
        self.name = "allowable_expenses"
        self.severity = "high"
        self.legal_source = "Income Tax Act 2005 §34 / Corporation Tax Act 2009 §54"
    
    def _is_relevant(self, text):
        t = text.lower()
        return any(k in t for k in ['expense', 'claim', 'deduct', 'allowable', 'entertainment', 'client'])
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not discuss business expenses or tax deductions',
                'legal_source': self.legal_source
            }
        
        # If explicitly states no expenses, treat as not applicable
        tl = (text or '').lower()
        if 'no ' in tl and 'expense' in tl:
            return {
                'status': 'N/A',
                'message': 'Not applicable - document explicitly states no expenses',
                'legal_source': self.legal_source
            }
        
        # Known non-allowable expenses
        non_allowable = {
            'client entertainment': r'(?:client|customer|business).*(?:entertainment|meals?|dining)',
            'commuting': r'(?:commut(?:e|ing)|daily.*(?:travel|journey).*(?:office|work)|travel.*(?:home.*work|work.*home))',
            'personal clothing': r'(?:personal|everyday).*(?:clothing|clothes)',
            'fines and penalties': r'(?:fine|penalty|penalties|speeding|parking|traffic).*(?:fine|penalty)',
            'gifts over £50': r'gift.*(?:£[5-9]\d|£\d{3,})',
        }
        
        errors = []
        spans = []
        
        for expense_type, pattern in non_allowable.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                # Check if it's being claimed as allowable
                context_start = max(0, match.start() - 50)
                context_end = min(len(text), match.end() + 50)
                context = text[context_start:context_end].lower()
                
                if any(kw in context for kw in ['claim', 'deduct', 'allowable', 'expense']):
                    errors.append(f'{expense_type.title()} is not allowable')
                    spans.append({
                        'type': 'non_allowable_expense',
                        'start': match.start(),
                        'end': match.end(),
                        'text': match.group(),
                        'severity': 'high'
                    })
        
        if errors:
            return {
                'status': 'FAIL',
                'severity': 'high',
                'message': f'Non-allowable expenses mentioned: {"; ".join(errors)}',
                'spans': spans,
                'legal_source': self.legal_source,
                'suggestion': 'Expenses must be "wholly and exclusively" for business. Not allowable: client entertainment, commuting, personal clothing, fines, gifts over £50.'
            }
        
        return {'status': 'PASS', 'severity': 'none', 'message': 'No non-allowable expenses detected'}
