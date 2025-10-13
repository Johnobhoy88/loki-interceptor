import re


class VatRateAccuracyGate:
    def __init__(self):
        self.name = "vat_rate_accuracy"
        self.severity = "high"
        self.legal_source = "VAT Act 1994; HMRC Guidance on VAT rates"
    
    def _is_relevant(self, text):
        return 'vat' in (text or '').lower()
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not mention VAT rates',
                'legal_source': self.legal_source
            }
        
        # Find VAT rates mentioned
        rate_pattern = r'vat.*?(\d+(?:\.\d+)?)%|(\d+(?:\.\d+)?)%.*?vat'
        
        spans = []
        for match in re.finditer(rate_pattern, text, re.IGNORECASE):
            rate_str = match.group(1) or match.group(2)
            try:
                rate = float(rate_str)
            except Exception:
                continue
            
            # Valid UK VAT rates: 20%, 5%, 0%
            valid_rates = [0, 5, 20]
            
            if rate not in valid_rates:
                spans.append({
                    'type': 'invalid_vat_rate',
                    'start': match.start(),
                    'end': match.end(),
                    'text': f'{rate}%',
                    'severity': 'high'
                })
        
        if spans:
            return {
                'status': 'FAIL',
                'severity': 'high',
                'message': f'Invalid VAT rate detected: {spans[0]["text"]}',
                'spans': spans,
                'legal_source': self.legal_source,
                'suggestion': "UK VAT rates: 20% (standard), 5% (reduced - fuel, children's car seats), 0% (zero-rated - food, books, children's clothes)"
            }
        
        return {'status': 'PASS', 'severity': 'none', 'message': 'VAT rates valid'}

