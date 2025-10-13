import re


class VatThresholdGate:
    def __init__(self):
        self.name = "vat_threshold"
        self.severity = "critical"
        self.legal_source = "VAT Act 1994 §3; HMRC Guidance (Threshold £90,000 from April 2024)"
    
    def _is_relevant(self, text):
        t = text.lower()
        return any(k in t for k in ['vat', 'threshold', 'register', '£', 'turnover'])
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not discuss VAT registration thresholds or turnover limits',
                'legal_source': self.legal_source
            }
        
        # Find threshold mentions
        threshold_pattern = r'£?(\d{2,3}),?(\d{3})'
        
        spans = []
        for match in re.finditer(threshold_pattern, text):
            amount_str = match.group(1) + match.group(2)
            try:
                amount = int(amount_str)
            except Exception:
                continue
            
            # Check if it's being stated as THE threshold
            context_start = max(0, match.start() - 50)
            context_end = min(len(text), match.end() + 50)
            context = text[context_start:context_end].lower()
            
            if 'threshold' in context or 'register' in context:
                # Current threshold is £90,000 (as of April 2024)
                if amount != 90000:
                    spans.append({
                        'type': 'incorrect_vat_threshold',
                        'start': match.start(),
                        'end': match.end(),
                        'text': f'£{amount:,}',
                        'severity': 'critical'
                    })
        
        if spans:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': f'Incorrect VAT registration threshold stated: {spans[0]["text"]}',
                'spans': spans,
                'legal_source': self.legal_source,
                'suggestion': 'Current VAT registration threshold is £90,000 (effective April 2024). Must register if turnover exceeds £90k in rolling 12 months OR expects to exceed in next 30 days.'
            }
        
        return {'status': 'PASS', 'severity': 'none', 'message': 'VAT threshold information correct or not stated'}
