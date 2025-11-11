import re


class EntireAgreementGate:
    def __init__(self):
        self.name = "entire_agreement"
        self.severity = "low"
        self.legal_source = "Contract Law, Parol Evidence Rule"

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

        # Check for entire agreement clause
        entire_agreement_patterns = [
            r'entire\s+agreement',
            r'entire\s+understanding',
            r'complete\s+agreement',
            r'supersedes?\s+(?:all\s+)?(?:prior|previous)',
            r'represents?\s+the\s+(?:complete|entire)'
        ]

        has_entire_agreement = any(re.search(p, text, re.IGNORECASE) for p in entire_agreement_patterns)

        if not has_entire_agreement:
            return {
                'status': 'WARNING',
                'severity': 'low',
                'message': 'No entire agreement clause',
                'legal_source': self.legal_source,
                'suggestion': 'Consider adding entire agreement clause to supersede prior negotiations',
                'risk': 'Prior representations or negotiations may be enforceable'
            }

        # Check for misrepresentation carve-out
        misrep_patterns = [
            r'(?:nothing|not).*exclude.*(?:fraud|fraudulent\s+misrepresentation)',
            r'(?:save|except).*fraud',
            r'subject\s+to.*fraud'
        ]

        has_misrep_carveout = any(re.search(p, text, re.IGNORECASE) for p in misrep_patterns)

        # Check for exclusion of prior agreements
        exclusion_patterns = [
            r'supersedes?.*(?:all\s+)?(?:prior|previous).*(?:agreement|understanding|negotiation)',
            r'replaces?.*prior',
            r'no\s+(?:prior|other).*(?:representation|statement)'
        ]

        has_exclusion = any(re.search(p, text, re.IGNORECASE) for p in exclusion_patterns)

        if has_entire_agreement and has_misrep_carveout and has_exclusion:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Comprehensive entire agreement clause with fraud carve-out',
                'legal_source': self.legal_source
            }

        if has_entire_agreement and has_misrep_carveout:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Entire agreement clause with fraud carve-out',
                'legal_source': self.legal_source
            }

        if has_entire_agreement and not has_misrep_carveout:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Entire agreement clause without fraud carve-out',
                'legal_source': 'Section 3 Misrepresentation Act 1967',
                'suggestion': 'Add carve-out: "Nothing in this clause excludes liability for fraudulent misrepresentation"',
                'risk': 'Clause may be unenforceable under Misrepresentation Act 1967'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Entire agreement clause present',
            'legal_source': self.legal_source
        }
