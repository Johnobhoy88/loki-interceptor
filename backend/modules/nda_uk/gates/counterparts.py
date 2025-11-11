import re


class CounterpartsGate:
    def __init__(self):
        self.name = "counterparts"
        self.severity = "low"
        self.legal_source = "Contract Law, Execution principles"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['agreement', 'contract'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable',
                'legal_source': self.legal_source
            }

        # Check for counterparts clause
        counterparts_patterns = [
            r'counterpart(?:s)?',
            r'executed\s+in.*(?:duplicate|triplicate)',
            r'separate\s+(?:but\s+)?identical\s+copies',
            r'original(?:s)?.*(?:constitute|together)'
        ]

        has_counterparts = any(re.search(p, text, re.IGNORECASE) for p in counterparts_patterns)

        if not has_counterparts:
            return {
                'status': 'N/A',
                'message': 'No counterparts provision (not required but useful)',
                'legal_source': self.legal_source
            }

        # Check for electronic/PDF signatures
        electronic_patterns = [
            r'(?:electronic|digital|PDF|scanned)\s+(?:signature|copy|counterpart)',
            r'email.*(?:PDF|signed)',
            r'electronic\s+transmission'
        ]

        allows_electronic = any(re.search(p, text, re.IGNORECASE) for p in electronic_patterns)

        # Check for deemed single document language
        single_doc_patterns = [
            r'(?:constitute|deemed|treated\s+as).*single\s+(?:document|agreement|instrument)',
            r'together.*one\s+(?:and\s+the\s+same\s+)?(?:document|agreement)',
            r'same\s+effect.*(?:original|single)'
        ]

        has_single_doc = any(re.search(p, text, re.IGNORECASE) for p in single_doc_patterns)

        if has_counterparts and allows_electronic and has_single_doc:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Comprehensive counterparts clause with electronic signatures',
                'legal_source': self.legal_source
            }

        if has_counterparts and has_single_doc:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Counterparts clause with single document language',
                'legal_source': self.legal_source,
                'suggestion': 'Consider adding provision for electronic/PDF signatures'
            }

        if has_counterparts:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Counterparts clause present',
                'legal_source': self.legal_source,
                'suggestion': 'Consider adding that counterparts constitute single document'
            }

        return {
            'status': 'N/A',
            'message': 'No counterparts provision',
            'legal_source': self.legal_source
        }
