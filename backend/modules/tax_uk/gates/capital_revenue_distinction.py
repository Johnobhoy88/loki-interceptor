import re


class CapitalRevenueDistinctionGate:
    def __init__(self):
        self.name = "capital_revenue_distinction"
        self.severity = "high"
        self.legal_source = "Capital Allowances Act 2001; HMRC guidance"
    
    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['expense', 'equipment', 'asset', 'purchase', 'depreciation'])
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not discuss capital or revenue expenditure',
                'legal_source': self.legal_source
            }
        
        # Capital items being treated as revenue expenses
        capital_items = {
            'vehicles': r'\b(?:car|van|vehicle|truck|company car)\b',
            'equipment': r'\b(?:machinery|equipment|computer|laptop|server)\b',
            'property': r'\b(?:building|property|premises|office space)\b',
            'improvements': r'\b(?:renovation|extension|improvement)\b'
        }
        
        errors = []
        spans = []
        
        for item_type, pattern in capital_items.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                # Check if being expensed immediately or listed as claimable
                context_start = max(0, match.start() - 80)
                context_end = min(len(text), match.end() + 80)
                context = text[context_start:context_end].lower()

                # Flag if: expense/claim/allowable/deduct mentioned AND no capital allowance context
                problematic = any(kw in context for kw in ['expense', 'claim', 'allowable', 'deduct', 'full cost', 'can claim'])
                capital_aware = any(kw in context for kw in ['capital allowance', 'aia', 'writing down', 'depreciation'])

                if problematic and not capital_aware:
                    errors.append(f'{item_type.title()} should be capital expenditure')
                    spans.append({
                        'type': 'capital_as_revenue',
                        'start': match.start(),
                        'end': match.end(),
                        'text': match.group(),
                        'severity': 'high'
                    })
        
        # Check for depreciation mentions (not tax-deductible)
        if re.search(r'depreciation.*(?:deduct|expense|claim)', text, re.IGNORECASE):
            errors.append('Depreciation is not tax-deductible')
        
        if errors:
            return {
                'status': 'FAIL',
                'severity': 'high',
                'message': f'Capital/revenue errors: {"; ".join(errors)}',
                'spans': spans,
                'legal_source': self.legal_source,
                'suggestion': 'Capital expenditure (vehicles, equipment, buildings) cannot be fully expensed. Use capital allowances/AIA. Depreciation is added back for tax.'
            }
        
        return {'status': 'PASS', 'severity': 'none', 'message': 'No capital/revenue classification errors'}

