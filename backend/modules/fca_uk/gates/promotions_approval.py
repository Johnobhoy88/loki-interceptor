import re


class PromotionsApprovalGate:
    def __init__(self):
        self.name = "promotions_approval"
        self.severity = "critical"
        self.legal_source = "FCA FSMA s.21 & s.24 (Financial Promotion Approval)"

    def _is_relevant(self, text):
        """Check if document is promotional material"""
        text_lower = text.lower()
        # ENHANCED: Expanded keywords and lowered threshold
        promo_keywords = [
            'invest', 'offer', 'promotion', 'apply', 'sign up',
            'buy', 'exclusive', 'limited', 'opportunity', 'return',
            'benefit', 'product', 'service', 'advertisement', 'guarantee', 'guaranteed',
            'exempt', 'exemption',  # Catches exemption claims
            'sophisticated', 'certified',  # Catches investor qualifications
            'financial promotion'  # Direct mention
        ]
        # Need at least 1 promotional indicator (lowered from 2 to catch strong claims)
        matches = sum(1 for kw in promo_keywords if kw in text_lower)
        return matches >= 1

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a financial promotion or lacks promotional content',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()
        spans = []

        # Check for strong promotional content
        promotional_patterns = [
            r'(?:apply|invest|buy|sign\s+up|join|register)\s+(?:now|today)',
            r'limited\s+(?:time|offer|spaces?|availability)',
            r'(?:exclusive|special)\s+(?:offer|opportunity|access)',
            r'don\'t\s+miss\s+out',
            r'(?:high|attractive|excellent)\s+(?:return|yield|rate)',
            r'act\s+(?:now|fast|quickly)',
            r'(?:call|contact|visit)\s+(?:us\s+)?(?:now|today)'
        ]

        is_promotional = False
        for pattern in promotional_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                is_promotional = True
                for m in matches:
                    spans.append({
                        'type': 'promotional_content',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'high'
                    })

        # Check if it's a financial promotion (investment-related)
        # ENHANCED: Added "financial promotion" and "investor" patterns
        financial_promotion_patterns = [
            r'(?:invest|investment|fund|share|bond|security|derivative)',
            r'(?:pension|retirement|isa|savings)',
            r'(?:mortgage|loan|credit|insurance|policy)',
            r'financial\s+(?:product|service|promotion)',
            r'\b(?:return|returns|yield|profit|gain)s?\b',  # Simplified - just check if financial terms present
            r'\d+%\s*(?:return|returns|yield|gain|profit)',  # Percentage returns
            r'investor'  # Catches "sophisticated investors"
        ]

        is_financial_promotion = False
        for pattern in financial_promotion_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                is_financial_promotion = True
                break

        # ENHANCED: Check for exemption claims early - if found, mark as financial promotion
        exemption_early_check = [
            r's\.?21\s+exempt',
            r'(?:exempt|exemption)\s+(?:from|under|applies)',
            r'(?:certified|sophisticated|high\s+net\s+worth)\s+investor'
        ]
        has_exemption_early = any(re.search(p, text, re.IGNORECASE) for p in exemption_early_check)

        # If exemption claim exists, treat as financial promotion
        if has_exemption_early:
            is_financial_promotion = True
            is_promotional = True

        # If promotional and financial, check for approval
        if not (is_promotional and is_financial_promotion):
            return {'status': 'N/A'}

        # Check for FCA authorization/approval
        approval_patterns = [
            r'(?:approved|authorised)\s+(?:by\s+)?(?:an?\s+)?(?:fca|pra)[\s-]?(?:authorised|regulated)',
            r'fca\s+(?:authorised|regulated|approved)',
            r'(?:section|s\.?)\s*21\s+(?:approved|exempt)',
            r'(?:section|s\.?)\s*24\s+approval',
            r'(?:issued|approved|authorised)\s+by.*(?:authorised|regulated)\s+(?:person|firm)',
            r'(?:we\s+are\s+)?(?:authorised|regulated)\s+by\s+(?:the\s+)?fca'
        ]

        has_approval = False
        for pattern in approval_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_approval = True
                for m in matches:
                    spans.append({
                        'type': 'fca_approval',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for approver identification
        approver_patterns = [
            r'approved\s+by:\s*[A-Z]',
            r'approver:\s*[A-Z]',
            r'(?:compliance|financial\s+promotion)\s+(?:officer|manager|team)\s+approval',
            r'approved\s+by.*(?:compliance|risk|legal)',
            r'reference\s+(?:number|code|id):\s*[A-Z0-9]'
        ]

        has_approver = False
        for pattern in approver_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_approver = True
                for m in matches:
                    spans.append({
                        'type': 'approver_identified',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for FCA reference number
        fca_number_patterns = [
            r'(?:fca|firm\s+reference|frn)(?:\s+(?:number|no\.?|#))?\s*:?\s*[0-9]{5,7}',
            r'(?:register(?:ed)?|authorised)\s+(?:number|no\.?)?\s*:?\s*[0-9]{5,7}'
        ]

        has_fca_number = False
        for pattern in fca_number_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_fca_number = True
                for m in matches:
                    spans.append({
                        'type': 'fca_reference_number',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for exemption claims
        # ENHANCED: Added more exemption patterns
        exemption_patterns = [
            r's\.?21\s+exempt',
            r'(?:exempt|exemption)\s+(?:from|under|applies)',
            r'(?:certified|sophisticated|high\s+net\s+worth)\s+investor',
            r'(?:self-?certified|restricted)\s+to',
            r'(?:FCA\s+)?(?:rules|exemption)\s+(?:applies?|exempt)'
        ]

        has_exemption = False
        for pattern in exemption_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_exemption = True
                for m in matches:
                    spans.append({
                        'type': 'exemption_claim',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'medium'
                    })

        # ENHANCED: If exemption claim is made, treat as promotional even without strong CTA
        if has_exemption and not is_promotional:
            is_promotional = True  # Exemption claims indicate it's a financial promotion

        # Determine status
        # Critical failure: Financial promotion without approval
        if not has_approval and not has_exemption:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Financial promotion without FCA s.21 approval',
                'legal_source': self.legal_source,
                'suggestion': 'FSMA s.21 prohibits unauthorized financial promotions. This must be approved by an FCA-authorized person (s.24). State: "Approved by [FCA Authorized Firm Name], FCA No. XXXXXX".',
                'spans': spans
            }

        # Warning: Has approval but no specific approver/number
        if has_approval and not has_approver and not has_fca_number:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'FCA approval claimed but approver not identified',
                'legal_source': self.legal_source,
                'suggestion': 'Identify the specific FCA-authorized firm that approved this promotion, including FCA reference number.',
                'spans': spans
            }

        # Warning: Exemption claimed (needs careful validation)
        if has_exemption and not has_approval:
            details = []
            details.append('Exemption claimed - verify eligibility')
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'S.21 exemption claimed - ensure criteria met',
                'legal_source': self.legal_source,
                'suggestion': 'Exemptions (certified/sophisticated investors, etc.) have strict criteria. Ensure promotion genuinely qualifies and is properly restricted.',
                'spans': spans,
                'details': details
            }

        # Pass: Good approval
        approval_quality = []
        if has_approval:
            approval_quality.append('FCA approval stated')
        if has_approver:
            approval_quality.append('approver identified')
        if has_fca_number:
            approval_quality.append('FCA number provided')
        if has_exemption:
            approval_quality.append('exemption noted')

        details = []
        for element in approval_quality:
            details.append(element)
        return {
            'status': 'PASS',
            'severity': 'none',
            'message': f'Financial promotion approval requirements met ({len(approval_quality)} elements: {", ".join(approval_quality)})',
            'legal_source': self.legal_source,
            'spans': spans,
            'details': details
        }
