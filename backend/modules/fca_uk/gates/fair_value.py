import re


class FairValueGate:
    def __init__(self):
        self.name = "fair_value"
        self.severity = "high"
        self.legal_source = "FCA PRIN 2A.4 (Price and Value Outcome)"

    def _is_relevant(self, text):
        """Check if document mentions pricing or value"""
        text_lower = text.lower()
        keywords = [
            'price', 'fee', 'charge', 'cost', 'premium', 'rate',
            'value', 'benefit', 'product', 'service'
        ]
        return any(kw in text_lower for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not discuss pricing or fees',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()

        # Check if pricing is mentioned
        has_pricing = any(re.search(pattern, text, re.IGNORECASE) for pattern in [
            r'£\s*\d+',
            r'\d+(?:\.\d+)?%',
            r'(?:fee|charge|cost|price|premium)s?\s*:?\s*(?:£|\d)',
            r'(?:annual|monthly|quarterly)\s+(?:fee|charge|cost)'
        ])

        if not has_pricing:
            return {'status': 'N/A'}

        # Check for fair value indicators
        value_patterns = [
            r'fair\s+value',
            r'value\s+for\s+money',
            r'reasonable\s+(?:price|fee|charge|cost)',
            r'commensurate\s+(?:with|to)',
            r'justified\s+by',
            r'benefit.*(?:outweigh|exceed|justify).*(?:cost|fee)',
            r'cost.*reasonable.*given'
        ]

        spans = []
        has_value_justification = False

        for pattern in value_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_value_justification = True
                for m in matches:
                    spans.append({
                        'type': 'value_justification',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for benefits mentioned alongside fees
        has_benefits = any(re.search(pattern, text, re.IGNORECASE) for pattern in [
            r'benefit(?:s)?\s+include',
            r'you\s+(?:will\s+)?(?:get|receive)',
            r'includes?(?:\s+access\s+to)?',
            r'cover(?:s|age)\s+(?:includes?|provides?)',
            r'feature(?:s)?\s+include'
        ])

        # Flag high fees without justification
        high_fee_patterns = [
            (r'(?:£\s*[1-9]\d{2,}|[5-9]\d+%)', 'high_amount'),
            (r'(?:annual|yearly)\s+(?:fee|charge).*£\s*[1-9]\d{2,}', 'high_annual_fee'),
            (r'(?:exit|early\s+withdrawal|surrender)\s+(?:fee|charge|penalty)', 'exit_fee')
        ]

        high_fees_found = []
        for pattern, fee_type in high_fee_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                high_fees_found.append(fee_type)
                for m in matches:
                    spans.append({
                        'type': f'high_fee_{fee_type}',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'medium' if has_value_justification else 'high'
                    })

        # Fail if high fees without value justification
        if high_fees_found and not has_value_justification:
            return {
                'status': 'FAIL',
                'severity': 'high',
                'message': 'Pricing mentioned without fair value rationale',
                'legal_source': self.legal_source,
                'suggestion': 'Consumer Duty requires firms to demonstrate that products represent fair value. Include rationale showing fees are reasonable relative to benefits.',
                'spans': spans
            }

        # Warning if pricing without clear benefits
        if has_pricing and not has_benefits:
            return {
                'status': 'WARNING',
                'severity': 'high',
                'message': 'Fees mentioned without clear benefit description',
                'legal_source': self.legal_source,
                'suggestion': 'Describe what customers receive for the fees charged to support fair value assessment.',
                'spans': spans
            }

        # Pass if value justification present
        if has_value_justification:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Fair value considerations evident',
                'legal_source': self.legal_source,
                'spans': spans
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Pricing structure appears reasonable',
            'legal_source': self.legal_source,
            'spans': spans
        }
