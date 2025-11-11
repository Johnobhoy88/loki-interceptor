import re


class SeverabilityGate:
    def __init__(self):
        self.name = "severability"
        self.severity = "medium"
        self.legal_source = "Contract Law, Blue pencil test (Attwood v Lamont [1920])"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['agreement', 'contract', 'nda'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not an agreement',
                'legal_source': self.legal_source
            }

        # Check for severability clause
        severability_patterns = [
            r'severab(?:ility|le)',
            r'(?:any|each)\s+provision.*(?:invalid|unenforceable).*(?:remainder|remaining|other\s+provisions)',
            r'if\s+any.*(?:term|clause|provision).*(?:held|found).*(?:invalid|unenforceable)',
            r'savings?\s+clause',
            r'blue\s+pencil'
        ]

        has_severability = any(re.search(p, text, re.IGNORECASE) for p in severability_patterns)

        # Check for modification/narrowing language
        modification_patterns = [
            r'modified.*enforceable\s+extent',
            r'reduced\s+in\s+scope',
            r'narrowed.*necessary',
            r'interpreted.*give.*effect'
        ]

        has_modification = any(re.search(p, text, re.IGNORECASE) for p in modification_patterns)

        if has_severability and has_modification:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Comprehensive severability clause with modification provisions',
                'legal_source': self.legal_source
            }

        if has_severability:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Severability clause present',
                'legal_source': self.legal_source,
                'suggestion': 'Consider adding language allowing court to modify overbroad provisions'
            }

        return {
            'status': 'WARNING',
            'severity': 'medium',
            'message': 'No severability clause found',
            'legal_source': self.legal_source,
            'suggestion': 'Add severability clause to preserve valid provisions if any term is held unenforceable',
            'risk': 'If one provision is invalid, entire agreement could fail'
        }
