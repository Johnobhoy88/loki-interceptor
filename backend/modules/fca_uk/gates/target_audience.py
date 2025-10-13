import re


class TargetAudienceGate:
    def __init__(self):
        self.name = "target_audience"
        self.severity = "high"
        self.legal_source = "FCA COBS 4.7 (Direct Offer Financial Promotions)"

    def _is_relevant(self, text):
        """Check if document is promotional or product-related"""
        text_lower = text.lower()
        keywords = [
            'product', 'service', 'offer', 'invest', 'policy',
            'account', 'fund', 'suitable', 'appropriate', 'designed for'
        ]
        return any(kw in text_lower for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a financial promotion or does not specify audience',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()
        spans = []

        # Check for target market/audience statements
        target_market_patterns = [
            r'(?:designed|suitable|intended|appropriate)\s+for',
            r'target\s+(?:market|audience|customer)',
            r'this\s+product\s+is\s+(?:for|aimed\s+at)',
            r'ideal\s+for',
            r'who\s+(?:is\s+)?this\s+(?:product|service|policy)\s+for',
            r'not\s+suitable\s+for'
        ]

        has_target_market = False
        for pattern in target_market_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_target_market = True
                for m in matches:
                    spans.append({
                        'type': 'target_market_statement',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for overly broad/generic targeting
        generic_patterns = [
            r'(?:suitable|appropriate|ideal)\s+for\s+(?:everyone|anyone|all|everybody)',
            r'anyone\s+can\s+(?:invest|apply|join)',
            r'no\s+(?:minimum|requirements|restrictions)',
            r'open\s+to\s+(?:all|everyone|anyone)'
        ]

        is_generic = False
        for pattern in generic_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                is_generic = True
                for m in matches:
                    spans.append({
                        'type': 'generic_targeting',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'high'
                    })

        # Check for specific target characteristics
        specific_characteristics = [
            r'aged?\s+(?:between\s+)?\d+',
            r'\d+\s+years?\s+old',
            r'(?:high|medium|low)\s+risk\s+(?:appetite|tolerance)',
            r'(?:existing|current)\s+(?:customer|client)',
            r'(?:experienced|sophisticated|professional)\s+investor',
            r'(?:first-time|new)\s+(?:buyer|investor)',
            r'(?:income|salary)\s+(?:of|above|over)',
            r'retire(?:d|ment|es)'
        ]

        has_specific_criteria = False
        for pattern in specific_characteristics:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_specific_criteria = True
                for m in matches:
                    spans.append({
                        'type': 'target_criteria',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for exclusions (negative targeting)
        exclusion_patterns = [
            r'not\s+(?:suitable|appropriate|recommended)\s+for',
            r'(?:exclude|excluding|excluded)',
            r'should\s+not\s+(?:invest|apply)',
            r'do\s+not\s+(?:invest|apply)\s+if'
        ]

        has_exclusions = False
        for pattern in exclusion_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_exclusions = True
                for m in matches:
                    spans.append({
                        'type': 'exclusion_criteria',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Determine status
        issues = []

        # Critical: Generic "for everyone" targeting
        if is_generic:
            return {
                'status': 'FAIL',
                'severity': 'high',
                'message': 'Generic "for everyone" targeting detected',
                'legal_source': self.legal_source,
                'suggestion': 'Product governance requires defined target markets. No product is suitable for everyone. Specify who the product IS and ISN\'T for.',
                'spans': spans
            }

        # Missing target market statement
        if not has_target_market:
            issues.append('No target market statement found')

        # Target market without specific criteria
        if has_target_market and not has_specific_criteria and not has_exclusions:
            issues.append('Target market mentioned but lacks specific criteria')

        # Warning level issues
        if issues:
            details = []
            for issue in issues:
                details.append(issue)
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Target market definition could be clearer',
                'legal_source': self.legal_source,
                'suggestion': 'Define target market with specific characteristics (age, risk tolerance, experience, needs) and/or exclusions.',
                'spans': spans,
                'details': details
            }

        # Pass
        pass_details = []
        if has_specific_criteria:
            pass_details.append('specific criteria defined')
        if has_exclusions:
            pass_details.append('exclusions stated')

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': f'Target market defined ({", ".join(pass_details)})',
            'legal_source': self.legal_source,
            'spans': spans
        }
