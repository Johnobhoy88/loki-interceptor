import re


class CrossCuttingRulesGate:
    def __init__(self):
        self.name = "cross_cutting_rules"
        self.severity = "critical"
        self.legal_source = "FCA PRIN 2A.2 (Consumer Duty Cross-Cutting Rules)"

    def _is_relevant(self, text):
        """
        Check if document is substantial enough for Consumer Duty cross-cutting rules
        Only applies to full product/service communications with customer impact
        """
        text_lower = text.lower()

        # ENHANCED: Reduced minimum length from 200 to 100 chars to catch more cases
        if len(text) < 100:  # Too short for cross-cutting rules assessment
            return False

        # Must be about regulated products/services
        # ENHANCED: Added "operations" and "provide" to catch service providers
        product_indicators = [
            'product', 'service', 'investment', 'account', 'policy',
            'pension', 'mortgage', 'loan', 'savings', 'insurance',
            'operations', 'operational', 'provide', 'offering'
        ]

        # ENHANCED: Expanded decision indicators to include customer-facing language
        decision_indicators = [
            'apply', 'purchase', 'buy', 'choose', 'select', 'decide',
            'terms and conditions', 'agreement', 'contract', 'offer',
            'customer', 'consumer', 'client',  # Customer-facing language
            'commitment', 'duty', 'requirement', 'obligation'  # Consumer Duty contexts
        ]

        has_product = any(ind in text_lower for ind in product_indicators)
        has_decision = any(ind in text_lower for ind in decision_indicators)

        # Only relevant if BOTH present
        return has_product and has_decision

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is too short or does not involve substantial product/customer decisions',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()

        # Check for the 3 cross-cutting rules
        rules = {
            'good_faith': [
                r'good\s+faith',
                r'honest(?:ly|y)',
                r'transparent(?:ly|cy)',
                r'open(?:ly|ness)',
                r'fair(?:ly|ness)'
            ],
            'avoid_harm': [
                r'avoid(?:ing)?\s+(?:foreseeable\s+)?harm',
                r'prevent\s+detriment',
                r'no\s+(?:unfair|undue)\s+harm',
                r'protect\s+(?:customer|consumer)'
            ],
            'enable_objectives': [
                r'enable.*(?:pursue|achieve|meet).*objective',
                r'support.*financial\s+(?:objective|goal)',
                r'help.*(?:customer|consumer).*outcome',
                r'facilitate.*(?:decision|choice)'
            ]
        }

        covered = []
        missing = []
        spans = []

        for rule_name, patterns in rules.items():
            found = False
            for pattern in patterns:
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
                if matches:
                    found = True
                    covered.append(rule_name)
                    for m in matches:
                        spans.append({
                            'type': f'rule_{rule_name}',
                            'start': m.start(),
                            'end': m.end(),
                            'text': m.group(),
                            'severity': 'none'
                        })
                    break

            if not found:
                missing.append(rule_name)

        # Check for negative indicators (bad faith, harm, barriers)
        negative_patterns = [
            (r'(?:mis(?:lead|inform|represent)|deceive|hide|conceal)', 'misleading_language'),
            (r'(?:difficult|hard|complex|confusing).*(?:cancel|exit|withdraw)', 'exit_barriers'),
            (r'(?:penalty|fee|charge).*(?:cancel|exit|early|withdrawal)', 'exit_penalties')
        ]

        violations = []
        for pattern, viol_type in negative_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                violations.append(viol_type)
                for m in matches:
                    spans.append({
                        'type': f'violation_{viol_type}',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'critical'
                    })

        # Fail if violations detected
        if violations:
            details = []
            details.append(f'Violations detected: {", ".join(violations)}')
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Potential Consumer Duty violations detected',
                'legal_source': self.legal_source,
                'suggestion': 'Remove language that may mislead, cause harm, or create barriers to customer objectives. Act in good faith.',
                'spans': spans,
                'details': details
            }

        # Critical if all 3 rules missing
        if len(missing) == 3:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'No Consumer Duty cross-cutting rules evident',
                'legal_source': self.legal_source,
                'suggestion': 'Demonstrate: (1) acting in good faith, (2) avoiding foreseeable harm, (3) enabling customers to pursue their financial objectives.',
                'spans': spans
            }

        # Warning if some rules missing
        if len(missing) > 0:
            details = []
            details.append(f'Covered rules: {", ".join(covered)}')
            details.append(f'Missing rules: {", ".join(missing)}')
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'{len(missing)} cross-cutting rule(s) not evident',
                'legal_source': self.legal_source,
                'suggestion': f'Consider addressing: {", ".join(missing)}',
                'spans': spans,
                'details': details
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Consumer Duty cross-cutting rules evident',
            'legal_source': self.legal_source,
            'spans': spans
        }
