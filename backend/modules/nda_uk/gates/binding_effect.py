import re


class BindingEffectGate:
    def __init__(self):
        self.name = "binding_effect"
        self.severity = "low"
        self.legal_source = "Contract Law"

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

        # Check for binding effect provisions
        binding_patterns = [
            r'binding\s+(?:on|upon)',
            r'inure.*benefit',
            r'(?:apply|extend)\s+to.*(?:successor|assign|heir)',
            r'bind.*(?:successor|assign|personal\s+representative)'
        ]

        has_binding_clause = any(re.search(p, text, re.IGNORECASE) for p in binding_patterns)

        if not has_binding_clause:
            return {
                'status': 'N/A',
                'message': 'No explicit binding effect provisions',
                'legal_source': self.legal_source,
                'note': 'Agreements are generally binding on parties; clause clarifies extension to successors'
            }

        # Check for parties bound
        bound_parties = {
            'successors': r'successor(?:s)?',
            'assigns': r'assign(?:s|ee)?',
            'heirs': r'heir(?:s)?',
            'personal_representatives': r'personal\s+representative(?:s)?',
            'executors': r'executor(?:s)?',
            'administrators': r'administrator(?:s)?',
            'permitted_assigns': r'permitted\s+assign'
        }

        found_bound_parties = {}
        for party_type, pattern in bound_parties.items():
            found_bound_parties[party_type] = bool(re.search(pattern, text, re.IGNORECASE))

        # Check for benefit language
        benefit_patterns = [
            r'inure.*benefit',
            r'benefit.*(?:of|extend)',
            r'enforceable\s+by'
        ]

        mentions_benefit = any(re.search(p, text, re.IGNORECASE) for p in benefit_patterns)

        party_count = sum(found_bound_parties.values())

        if party_count >= 3 and mentions_benefit:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive binding effect clause ({party_count} parties)',
                'legal_source': self.legal_source,
                'bound_parties': [k for k, v in found_bound_parties.items() if v]
            }

        if party_count >= 2:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Binding on successors and assigns',
                'legal_source': self.legal_source,
                'bound_parties': [k for k, v in found_bound_parties.items() if v]
            }

        if party_count >= 1:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Basic binding effect provision',
                'legal_source': self.legal_source,
                'bound_parties': [k for k, v in found_bound_parties.items() if v],
                'suggestion': 'Consider adding: successors, assigns, personal representatives'
            }

        return {
            'status': 'WARNING',
            'severity': 'low',
            'message': 'Binding effect mentioned but parties unclear',
            'legal_source': self.legal_source,
            'suggestion': 'Specify: binding on parties, their successors, assigns, and permitted transferees'
        }
