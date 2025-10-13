import re


class InducementsReferralsGate:
    def __init__(self):
        self.name = "inducements_referrals"
        self.severity = "high"
        self.legal_source = "FCA COBS 2.3 (Inducements)"

    def _is_relevant(self, text):
        """Check if document mentions referrals, commissions, or third parties"""
        text_lower = text.lower()
        keywords = [
            'referral', 'refer', 'commission', 'fee', 'payment',
            'introduce', 'third party', 'partner', 'arrangement'
        ]
        return any(kw in text_lower for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not mention commissions, referrals, or inducement arrangements',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()
        spans = []

        # Detect referral arrangements
        referral_patterns = [
            r'\b(?:referral|refer(?:ring)?)\s+(?:you|customer|client)',
            r'(?:introduce|introduction)\s+(?:to|you\s+to)',
            r'(?:partner|partnership)\s+(?:with|arrangement)',
            r'(?:work|working)\s+(?:with|alongside)',
            r'(?:in\s+)?(?:association|collaboration)\s+with'
        ]

        has_referral = False
        for pattern in referral_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_referral = True
                for m in matches:
                    spans.append({
                        'type': 'referral_arrangement',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'medium'
                    })

        # Detect commission/fee mentions
        commission_patterns = [
            r'\b(?:commission|fee|payment|remuneration|compensation)\b',
            r'(?:receive|earn|paid|get)\s+(?:a\s+)?(?:fee|commission|payment)',
            r'(?:fee|commission)\s+(?:from|paid\s+by)',
            r'referral\s+(?:fee|commission|payment)'
        ]

        has_commission = False
        for pattern in commission_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_commission = True
                for m in matches:
                    spans.append({
                        'type': 'commission_mention',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'medium'
                    })

        # If no referrals or commissions, gate not applicable
        if not has_referral and not has_commission:
            return {'status': 'N/A'}

        # Check for inducement disclosures
        disclosure_patterns = [
            r'(?:we\s+)?(?:receive|earn|are\s+paid|get)\s+(?:a\s+)?(?:commission|fee|payment|benefit)',
            r'(?:commission|fee|payment)\s+(?:of|equivalent\s+to)\s+(?:£|[0-9])',
            r'(?:disclose|disclosure)\s+(?:of\s+)?(?:commission|fee|inducement)',
            r'(?:you\s+)?(?:will\s+)?(?:not\s+)?pay\s+(?:any\s+)?(?:extra|additional|more)',
            r'(?:no\s+)?(?:additional\s+)?(?:cost|charge|fee)\s+(?:to\s+you|for\s+(?:the\s+)?customer)'
        ]

        has_disclosure = False
        for pattern in disclosure_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_disclosure = True
                for m in matches:
                    spans.append({
                        'type': 'inducement_disclosure',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for amount disclosure
        amount_patterns = [
            r'(?:commission|fee|payment)\s+(?:of|is)\s+(?:£|[0-9]|up\s+to)',
            r'(?:£|[0-9])[0-9,]+(?:\.[0-9]{2})?\s+(?:commission|fee|referral)',
            r'[0-9]+%\s+(?:of\s+)?(?:the\s+)?(?:premium|value|amount)',
            r'up\s+to\s+(?:£|[0-9])'
        ]

        has_amount = False
        for pattern in amount_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_amount = True
                for m in matches:
                    spans.append({
                        'type': 'inducement_amount',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for who pays disclosure
        payer_patterns = [
            r'(?:paid|provided)\s+(?:to\s+us\s+)?(?:by|from)\s+(?:the\s+)?(?:provider|lender|insurer|company)',
            r'(?:provider|lender|insurer|company)\s+(?:pay|provide)s?\s+(?:us\s+)?(?:a\s+)?(?:commission|fee)',
            r'(?:from|by)\s+(?:the\s+)?(?:product\s+)?provider'
        ]

        has_payer = False
        for pattern in payer_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_payer = True
                for m in matches:
                    spans.append({
                        'type': 'inducement_payer',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for benefit to customer statement
        benefit_patterns = [
            r'(?:enhance|improve)\s+(?:the\s+)?(?:quality|service)',
            r'benefit\s+(?:to\s+)?(?:you|customer|client)',
            r'no\s+(?:extra|additional)\s+(?:cost|charge|fee)',
            r'does\s+not\s+(?:affect|impact|change)\s+(?:the\s+)?(?:price|cost|fee)'
        ]

        has_benefit_statement = False
        for pattern in benefit_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_benefit_statement = True
                for m in matches:
                    spans.append({
                        'type': 'customer_benefit',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Determine status
        issues = []
        missing_elements = []

        # Critical: Referral/commission but no disclosure at all
        if (has_referral or has_commission) and not has_disclosure:
            return {
                'status': 'FAIL',
                'severity': 'high',
                'message': 'Referral or commission arrangement without disclosure',
                'legal_source': self.legal_source,
                'suggestion': 'COBS 2.3 requires disclosure of inducements. State: (1) that you receive a fee/commission, (2) from whom, (3) the amount or how it\'s calculated, (4) that it doesn\'t increase customer cost.',
                'spans': spans
            }

        # Has disclosure but missing key elements
        if has_disclosure:
            if not has_amount:
                missing_elements.append('amount or calculation method')
            if not has_payer:
                missing_elements.append('who pays the commission')
            if not has_benefit_statement:
                missing_elements.append('statement that it doesn\'t increase cost to customer')

        # Warning: Incomplete disclosure
        if missing_elements:
            details = []
            for element in missing_elements:
                details.append(f'Missing: {element}')
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'Inducement disclosed but incomplete ({len(missing_elements)} elements missing)',
                'legal_source': self.legal_source,
                'suggestion': f'Add: {", ".join(missing_elements)}. Full disclosure enhances trust and meets COBS 2.3 requirements.',
                'spans': spans,
                'details': details
            }

        # Pass: Good disclosure
        disclosure_elements = []
        if has_disclosure:
            disclosure_elements.append('inducement disclosed')
        if has_amount:
            disclosure_elements.append('amount specified')
        if has_payer:
            disclosure_elements.append('payer identified')
        if has_benefit_statement:
            disclosure_elements.append('customer benefit/no extra cost stated')

        details = []
        for element in disclosure_elements:
            details.append(element)
        return {
            'status': 'PASS',
            'severity': 'none',
            'message': f'Inducement/referral appropriately disclosed ({len(disclosure_elements)} elements)',
            'legal_source': self.legal_source,
            'spans': spans,
            'details': details
        }
