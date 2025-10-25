import re


class RiskBenefitBalanceGate:
    def __init__(self):
        self.name = "risk_benefit_balance"
        self.severity = "high"
        self.legal_source = "FCA COBS 4.2.3 (Risk Warnings Equally Prominent)"

    def _is_relevant(self, text):
        """Check if document mentions investment benefits or returns"""
        text_lower = text.lower()
        return any(kw in text_lower for kw in [
            'return', 'profit', 'gain', 'growth', 'performance',
            'yield', 'benefit', 'invest', 'opportunity'
        ])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not present product benefits or features',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()
        spans = []

        # Count benefit mentions
        benefit_patterns = [
            r'(?:return|yield|profit|gain)s?\s+of\s+\d+',
            r'\d+%\s+(?:return|yield|gain|growth)',
            r'(?:high|significant|attractive|strong|excellent)\s+(?:return|yield|performance|growth)',
            r'(?:potential|possible)\s+(?:for\s+)?(?:return|gain|profit|growth)',
            r'(?:great|good|excellent)\s+(?:investment|opportunity)',
            r'benefit(?:s)?\s+include',
            r'advantage(?:s)?\s+of'
        ]

        benefit_count = 0
        for pattern in benefit_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            benefit_count += len(matches)
            for m in matches:
                spans.append({
                    'type': 'benefit_mention',
                    'start': m.start(),
                    'end': m.end(),
                    'text': m.group(),
                    'severity': 'none'
                })

        # Count risk mentions
        risk_patterns = [
            r'(?:capital|investment|money)\s+(?:is\s+)?at\s+risk',
            r'(?:you\s+)?may\s+lose\s+(?:some|all)\s+(?:of\s+your\s+)?(?:capital|money|investment)',
            r'value\s+(?:can|may|could)\s+(?:go\s+down|fall|decrease)',
            r'returns?\s+(?:are\s+)?not\s+guaranteed',
            r'no\s+guarantee\s+of\s+(?:returns?|profits?)',
            r'past\s+performance\s+.*not\s+(?:a\s+)?(?:guide|indicator|guarantee)',
            r'risk\s+warning',
            r'loss\s+of\s+capital'
        ]

        risk_count = 0
        for pattern in risk_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            risk_count += len(matches)
            for m in matches:
                spans.append({
                    'type': 'risk_mention',
                    'start': m.start(),
                    'end': m.end(),
                    'text': m.group(),
                    'severity': 'none'
                })

        # Check for specific required warnings
        required_warnings = {
            'capital_at_risk': r'(?:capital|investment|money)\s+(?:is\s+)?at\s+risk',
            'not_guaranteed': r'not\s+guaranteed',
            'can_go_down': r'(?:can|may|could)\s+(?:go\s+down|fall|decrease)',
            'past_performance': r'past\s+performance.*not.*(?:guide|indicator|guarantee)'
        }

        missing_warnings = []
        for warning_name, pattern in required_warnings.items():
            if not re.search(pattern, text, re.IGNORECASE):
                missing_warnings.append(warning_name)

        # Check prominence (rough heuristic - risks should appear early if benefits mentioned)
        first_benefit_pos = float('inf')
        first_risk_pos = float('inf')

        for pattern in benefit_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                first_benefit_pos = min(first_benefit_pos, match.start())

        for pattern in risk_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                first_risk_pos = min(first_risk_pos, match.start())

        risks_less_prominent = first_benefit_pos < first_risk_pos and (first_risk_pos - first_benefit_pos) > 500

        # Determine status
        issues = []

        # Critical: Benefits without risks
        if benefit_count > 0 and risk_count == 0:
            return {
                'status': 'FAIL',
                'severity': 'high',
                'message': 'Benefits mentioned without any risk warnings',
                'legal_source': self.legal_source,
                'suggestion': 'Include risk warnings that are equally prominent to benefit statements. Capital at risk warnings are mandatory for investment promotions.',
                'spans': spans
            }

        # Critical: Significant imbalance (3:1 ratio or worse)
        if benefit_count > 0 and risk_count > 0:
            ratio = benefit_count / risk_count
            if ratio > 3:
                issues.append(f'Benefit/risk imbalance: {benefit_count} benefit mentions vs {risk_count} risk mentions (ratio {ratio:.1f}:1)')

        # Check missing required warnings
        if benefit_count > 0 and missing_warnings:
            issues.append(f'Missing required warnings: {", ".join(missing_warnings)}')

        # Check prominence
        if risks_less_prominent:
            issues.append('Risk warnings appear significantly after benefits (less prominent)')

        # Determine final status
        if issues:
            severity = 'high'
            details = []
            for issue in issues:
                details.append(issue)
            details.append(f'Benefit mentions: {benefit_count}, Risk mentions: {risk_count}')
            if missing_warnings:
                details.append(f'Missing warnings: {", ".join(missing_warnings)}')
            return {
                'status': 'FAIL' if severity == 'high' and len(issues) >= 2 else 'WARNING',
                'severity': 'medium' if 'WARNING' in ['WARNING'] else severity,
                'message': 'Risk/benefit balance issues detected',
                'legal_source': self.legal_source,
                'suggestion': 'COBS 4.2.3 requires risk warnings to be as prominent as benefits. Place warnings early, repeat throughout, and ensure visibility.',
                'spans': spans,
                'details': details
            }

        # Pass
        details = []
        details.append(f'Benefit mentions: {benefit_count}, Risk mentions: {risk_count}')
        return {
            'status': 'PASS',
            'severity': 'none',
            'message': f'Balanced risk/benefit presentation ({risk_count} risk mentions, {benefit_count} benefit mentions)',
            'legal_source': self.legal_source,
            'spans': spans,
            'details': details
        }
