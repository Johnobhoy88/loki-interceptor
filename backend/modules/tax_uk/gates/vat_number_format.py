import re


class VatNumberFormatGate:
    def __init__(self):
        self.name = "vat_number_format"
        self.severity = "critical"
        self.legal_source = "HMRC VAT Registration Manual (VATREG03700)"
    
    def _is_relevant(self, text):
        return 'vat' in (text or '').lower()
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not reference VAT numbers',
                'legal_source': self.legal_source
            }
        
        # Find VAT number patterns
        vat_pattern = r'vat\s*(?:reg|registration)?\s*(?:no|number)?\s*:?\s*([A-Z]{2}?\d{9,12}|XI\d{9})'
        
        matches = list(re.finditer(vat_pattern, text, re.IGNORECASE))
        
        if not matches:
            # VAT mentioned but no valid number found → FAIL
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'VAT referenced but valid VAT number not found',
                'spans': [],
                'suggestion': 'Provide a valid UK VAT number: GB123456789 (or XI123456789 for NI)'
            }
        
        spans = []
        for match in matches:
            number = match.group(1).upper()
            
            # Check format without regex escape pitfalls
            if number.startswith('GB') and number[2:].isdigit() and len(number) in (11, 14):
                is_valid = True
            elif number.startswith('XI') and number[2:].isdigit() and len(number) == 11:
                is_valid = True
            else:
                is_valid = False
            
            if not is_valid:
                spans.append({
                    'type': 'invalid_vat_number',
                    'start': match.start(1),
                    'end': match.end(1),
                    'text': number,
                    'severity': 'critical'
                })
        
        if spans:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': f'Invalid VAT number format detected: {spans[0]["text"]}',
                'spans': spans,
                'legal_source': self.legal_source,
                'suggestion': 'UK VAT numbers: GB + 9 digits (or 12 for branch traders), or XI + 9 digits for NI'
            }
        
        return {'status': 'PASS', 'severity': 'none', 'message': 'VAT number format valid'}
