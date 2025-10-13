import re


class OutcomesCoverageGate:
    def __init__(self):
        self.name = "outcomes_coverage"
        self.severity = "critical"
        self.legal_source = "FCA PRIN 2A (Consumer Duty)"

    def _is_relevant(self, text):
        """
        Check if document is a full product/service communication
        Only apply Consumer Duty outcomes to substantial product documents,
        not simple contact info or brief snippets
        """
        text_lower = text.lower()

        # Minimum length check - Consumer Duty applies to full communications
        if len(text) < 150:  # Less than ~150 chars = too short for full product comms
            return False

        # Must contain product/service indicators AND communication intent
        product_indicators = [
            'product', 'service', 'investment', 'account', 'plan',
            'policy', 'pension', 'savings', 'mortgage', 'loan'
        ]
        communication_indicators = [
            'designed for', 'suitable for', 'target market', 'designed to',
            'information about', 'details of', 'terms and conditions',
            'features include', 'benefits include', 'this product'
        ]

        has_product = any(ind in text_lower for ind in product_indicators)
        has_communication = any(ind in text_lower for ind in communication_indicators)

        # Only relevant if BOTH product AND communication intent present
        return has_product and has_communication

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a full product/service communication requiring Consumer Duty outcomes',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()

        # Check for all 4 Consumer Duty outcomes
        outcomes = {
            'products_services': [
                r'(?:product|service)s?\s+(?:design|fit|suitable|appropriate)',
                r'target\s+market',
                r'customer\s+need'
            ],
            'price_value': [
                r'fair\s+value',
                r'price.*reasonable',
                r'fee.*commensurate',
                r'value\s+(?:for\s+money|assessment)'
            ],
            'understanding': [
                r'clear(?:ly)?\s+(?:communicate|explain|inform)',
                r'(?:easy|plain)\s+(?:to\s+)?understand',
                r'comprehension',
                r'consumer\s+understanding'
            ],
            'support': [
                r'customer\s+support',
                r'assistance\s+available',
                r'help(?:line|desk)',
                r'support\s+(?:service|channel)'
            ]
        }

        covered = []
        missing = []
        spans = []

        for outcome_name, patterns in outcomes.items():
            found = False
            for pattern in patterns:
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
                if matches:
                    found = True
                    covered.append(outcome_name)
                    for m in matches:
                        spans.append({
                            'type': f'outcome_{outcome_name}',
                            'start': m.start(),
                            'end': m.end(),
                            'text': m.group(),
                            'severity': 'none'
                        })
                    break

            if not found:
                missing.append(outcome_name)

        # Critical if 3+ outcomes missing
        if len(missing) >= 3:
            details = []
            details.append(f'Covered outcomes: {", ".join(covered) if covered else "none"}')
            details.append(f'Missing outcomes: {", ".join(missing)}')
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': f'Consumer Duty: {len(missing)} of 4 outcomes not addressed',
                'legal_source': self.legal_source,
                'suggestion': f'Address missing outcomes: {", ".join(missing)}. Consumer Duty requires consideration of products/services, price/value, understanding, and support.',
                'spans': spans,
                'details': details
            }

        # Warning if 1-2 outcomes missing
        if len(missing) > 0:
            details = []
            details.append(f'Covered outcomes: {", ".join(covered)}')
            details.append(f'Missing outcomes: {", ".join(missing)}')
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'Consumer Duty: {len(missing)} outcome(s) not clearly addressed',
                'legal_source': self.legal_source,
                'suggestion': f'Consider addressing: {", ".join(missing)}',
                'spans': spans,
                'details': details
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'All 4 Consumer Duty outcomes referenced',
            'legal_source': self.legal_source,
            'spans': spans
        }
