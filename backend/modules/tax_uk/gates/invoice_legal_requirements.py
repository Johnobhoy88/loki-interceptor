import re


class InvoiceLegalRequirementsGate:
    def __init__(self):
        self.name = "invoice_legal_requirements"
        self.severity = "high"
        self.legal_source = "Companies Act 2006; GOV.UK Guidance on Invoicing"
    
    def _is_relevant(self, text):
        return 'invoice' in (text or '').lower()
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not an invoice',
                'legal_source': self.legal_source
            }
        
        required = {
            'unique_number': r'invoice\s*(?:no|number|#)?\s*:?\s*\d+',
            'business_name': r'(?:from|issued by|supplier)',
            'business_address': r'\d+.*(?:street|road|avenue|lane|way|place)',
            'customer_name': r'(?:to|bill to|customer)',
            'date': r'date\s*:?\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            'description': r'(?:description|item|service|product)',
            'total': r'total.*£?\d+'
        }
        
        missing = []
        for field, pattern in required.items():
            if not re.search(pattern, text, re.IGNORECASE):
                missing.append(field.replace('_', ' '))
        
        if not missing:
            return {'status': 'PASS', 'severity': 'none', 'message': 'All required invoice elements present'}
        
        return {
            'status': 'FAIL',
            'severity': 'high',
            'message': f'Invoice missing: {", ".join(missing)}',
            'legal_source': self.legal_source,
            'suggestion': 'UK invoices require: unique number, business name & address, customer name & address, date, description of goods/services, amounts.'
        }

