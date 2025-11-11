import re


class RemediesEnforcementGate:
    def __init__(self):
        self.name = "remedies_enforcement"
        self.severity = "medium"
        self.legal_source = "Contract Law, Injunctive Relief principles"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['agreement', 'contract', 'nda'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable',
                'legal_source': self.legal_source
            }

        # Check for remedy provisions
        remedy_types = {
            'injunctive_relief': [
                r'injunct(?:ion|ive\s+relief)',
                r'equitable\s+relief',
                r'specific\s+performance'
            ],
            'damages': [
                r'damages',
                r'compensation',
                r'monetary\s+(?:loss|damages)'
            ],
            'liquidated_damages': [
                r'liquidated\s+damages',
                r'agreed\s+damages',
                r'penalty\s+of.*(?:£|\$|GBP)'
            ],
            'account_of_profits': [
                r'account\s+of\s+profits',
                r'disgorgement'
            ]
        }

        found_remedies = {}
        for remedy_type, patterns in remedy_types.items():
            found = any(re.search(p, text, re.IGNORECASE) for p in patterns)
            found_remedies[remedy_type] = found

        # Check for penalty clause (unenforceable in UK)
        penalty_patterns = [
            r'penalty\s+(?:of|clause)',
            r'(?:pay|liable).*(?:£|\$|GBP)\s*\d+(?:,\d{3})*(?:\.\d{2})?.*(?:breach|violation)',
            r'fine.*breach'
        ]
        has_penalty = any(re.search(p, text, re.IGNORECASE) for p in penalty_patterns)

        # Check for non-exclusivity of remedies
        non_exclusive_patterns = [
            r'remedies.*not\s+exclusive',
            r'in\s+addition\s+to',
            r'without\s+prejudice\s+to.*other\s+(?:remedies|rights)'
        ]
        has_non_exclusive = any(re.search(p, text, re.IGNORECASE) for p in non_exclusive_patterns)

        if has_penalty:
            return {
                'status': 'FAIL',
                'severity': 'high',
                'message': 'Penalty clause detected - unenforceable in UK law',
                'legal_source': 'Cavendish Square v Makdessi [2015] UKSC 67',
                'suggestion': 'Replace penalty with genuine pre-estimate of loss (liquidated damages) or remove',
                'penalty': 'Penalty clauses are void and unenforceable'
            }

        if found_remedies['liquidated_damages']:
            # Check if it's reasonable
            reasonable_patterns = [
                r'genuine\s+(?:pre-)?estimate',
                r'reasonable\s+(?:estimate|pre-estimate)',
                r'anticipated\s+(?:loss|damages)'
            ]
            is_reasonable = any(re.search(p, text, re.IGNORECASE) for p in reasonable_patterns)

            if not is_reasonable:
                return {
                    'status': 'WARNING',
                    'severity': 'high',
                    'message': 'Liquidated damages without reasonableness language',
                    'legal_source': 'Cavendish Square v Makdessi [2015]',
                    'suggestion': 'Clarify that liquidated damages are genuine pre-estimate of loss'
                }

        remedy_count = sum(found_remedies.values())

        if remedy_count >= 2:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Multiple remedies specified ({remedy_count} types)',
                'legal_source': self.legal_source,
                'remedies': [k for k, v in found_remedies.items() if v]
            }

        if remedy_count == 1:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Basic remedy provisions included',
                'legal_source': self.legal_source,
                'suggestion': 'Consider specifying additional remedies (injunctive relief, damages)'
            }

        return {
            'status': 'WARNING',
            'severity': 'low',
            'message': 'No explicit remedy provisions',
            'legal_source': self.legal_source,
            'suggestion': 'Consider adding remedy provisions to clarify enforcement options'
        }
