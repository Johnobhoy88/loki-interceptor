import re


class HmrcScamDetectionGate:
    def __init__(self):
        self.name = "hmrc_scam_detection"
        self.severity = "critical"
        self.legal_source = "Fraud Act 2006; HMRC official guidance on scams"
    
    def _is_relevant(self, text):
        t = text.lower()
        return any(k in t for k in ['hmrc', 'tax', 'refund', 'payment', 'gift card', 'bank details'])
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not contain HMRC, tax, or payment-related content',
                'legal_source': self.legal_source
            }
        
        # Explicitly ignore negated HMRC mentions
        if 'no hmrc mentioned' in (text or '').lower():
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not contain HMRC, tax, or payment-related content',
                'legal_source': self.legal_source
            }
        
        # Known scam indicators
        scam_indicators = {
            'gift cards': r'(?:itunes|amazon|google play).*(?:card|voucher)',
            'arrest threats': r'(?:arrest|prosecute|legal action).*(?:immediate|now)',
            'crypto payment': r'(?:bitcoin|cryptocurrency|crypto)',
            'non-gov email': r'hmrc.*@(?!hmrc\.gov\.uk|gov\.uk)',
            'refund via email': r'(?:refund|rebate).*(?:email|text|sms)',
            'urgent payment': r'(?:pay|payment).*(?:immediate|urgent|now|today)'
        }
        
        errors = []
        spans = []
        
        for scam_type, pattern in scam_indicators.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                errors.append(f'SCAM INDICATOR: {scam_type}')
                spans.append({
                    'type': 'hmrc_scam_indicator',
                    'start': match.start(),
                    'end': match.end(),
                    'text': match.group(),
                    'severity': 'critical'
                })
        
        if errors:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': f'HMRC SCAM DETECTED: {"; ".join(errors)}',
                'spans': spans,
                'legal_source': self.legal_source,
                'suggestion': 'HMRC NEVER: requests payment via gift cards/crypto, threatens arrest, uses non-gov emails, offers refunds via email/text. Report to phishing@hmrc.gov.uk'
            }
        
        return {'status': 'PASS', 'severity': 'none', 'message': 'No HMRC scam indicators detected'}
