import re


class RelationshipOfPartiesGate:
    def __init__(self):
        self.name = "relationship_of_parties"
        self.severity = "low"
        self.legal_source = "Agency Law, Partnership Act 1890"

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

        # Check for relationship of parties clause
        relationship_patterns = [
            r'relationship.*(?:between|of)\s+(?:the\s+)?parties',
            r'independent\s+contractor',
            r'(?:not|nothing).*(?:partnership|joint\s+venture|agency)',
            r'no\s+(?:partnership|agency|employment)'
        ]

        has_relationship_clause = any(re.search(p, text, re.IGNORECASE) for p in relationship_patterns)

        if not has_relationship_clause:
            return {
                'status': 'WARNING',
                'severity': 'low',
                'message': 'No relationship of parties provision',
                'legal_source': self.legal_source,
                'suggestion': 'Add clause clarifying parties are independent contractors, not partners/agents',
                'risk': 'Ambiguity about legal relationship could create unintended liability'
            }

        # Check for specific disclaimers
        disclaimers = {
            'not_partnership': r'(?:not|nothing).*(?:partnership|partners)',
            'not_joint_venture': r'(?:not|nothing).*joint\s+venture',
            'not_agency': r'(?:not|nothing|no).*(?:agent|agency)',
            'not_employment': r'(?:not|nothing|no).*(?:employment|employee|employer)',
            'independent_contractor': r'independent\s+contractor',
            'no_authority': r'no\s+(?:power|authority).*(?:bind|commit|represent)'
        }

        found_disclaimers = {}
        for disclaimer_type, pattern in disclaimers.items():
            found_disclaimers[disclaimer_type] = bool(re.search(pattern, text, re.IGNORECASE))

        disclaimer_count = sum(found_disclaimers.values())

        if disclaimer_count >= 4:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive relationship disclaimers ({disclaimer_count}/6)',
                'legal_source': self.legal_source,
                'disclaimers': [k for k, v in found_disclaimers.items() if v]
            }

        if disclaimer_count >= 2:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Basic relationship provisions',
                'legal_source': self.legal_source,
                'disclaimers': [k for k, v in found_disclaimers.items() if v],
                'suggestion': 'Consider adding: no authority to bind, not employment relationship'
            }

        return {
            'status': 'WARNING',
            'severity': 'low',
            'message': 'Relationship clause lacks specificity',
            'legal_source': self.legal_source,
            'suggestion': 'Clarify: independent contractors, not partnership, no agency, no authority to bind'
        }
