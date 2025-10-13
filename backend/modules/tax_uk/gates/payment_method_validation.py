import re


class PaymentMethodValidationGate:
    def __init__(self):
        self.name = "payment_method_validation"
        self.severity = "critical"
        self.legal_source = "GOV.UK guidance on paying HMRC"

    def _is_relevant(self, text):
        t = text.lower()
        return any(k in t for k in ['pay', 'payment', 'bank', 'hmrc', 'gift', 'bitcoin', 'crypto'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not contain payment instructions or bank details',
                'legal_source': self.legal_source
            }
        
        # If the text explicitly denies payment context, treat as N/A
        if 'no payment' in (text or '').lower():
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not contain payment instructions or bank details',
                'legal_source': self.legal_source
            }

        suspicious = {
            'gift cards': r'(?:itunes|amazon|google\s*play|gift)\s*(?:card|voucher)',
            'crypto': r'\b(?:bitcoin|crypto(?:currency)?|wallet\s*address)\b',
            'personal account': r'personal\s+(?:bank\s*)?account',
            'bank details changed': r'bank\s+details\s+chang(?:e|ed)'
        }

        spans = []
        flags = []
        for label, pat in suspicious.items():
            for m in re.finditer(pat, text, re.IGNORECASE):
                flags.append(label)
                spans.append({
                    'type': 'suspicious_payment_request',
                    'start': m.start(),
                    'end': m.end(),
                    'text': m.group(),
                    'severity': 'critical'
                })

        if flags:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Suspicious payment method detected: ' + ', '.join(sorted(set(flags))),
                'spans': spans,
                'legal_source': self.legal_source,
                'suggestion': 'Only pay HMRC via official methods: Direct Debit, HMRC online services, or verified HMRC bank accounts.'
            }

        return {'status': 'PASS', 'severity': 'none', 'message': 'No suspicious payment methods detected'}
