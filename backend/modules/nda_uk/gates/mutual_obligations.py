import re


class MutualObligationsGate:
    def __init__(self):
        self.name = "mutual_obligations"
        self.severity = "medium"
        self.legal_source = "Contract Law, Consideration doctrine"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['nda', 'non-disclosure', 'confidentiality agreement'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a non-disclosure agreement',
                'legal_source': self.legal_source
            }

        # Check for mutual vs unilateral structure
        mutual_indicators = [
            r'each\s+party',
            r'both\s+parties',
            r'mutual(?:ly)?',
            r'parties\s+(?:each\s+)?agree',
            r'either\s+party.*other\s+party'
        ]

        unilateral_indicators = [
            r'the\s+recipient\s+(?:agrees|shall)',
            r'the\s+(?:employee|consultant)\s+(?:agrees|shall)',
            r'you\s+(?:agree|shall)',
            r'(?:I|my)\s+(?:agree|shall)'
        ]

        has_mutual = any(re.search(p, text, re.IGNORECASE) for p in mutual_indicators)
        has_unilateral = any(re.search(p, text, re.IGNORECASE) for p in unilateral_indicators)

        # Check for balanced obligations
        if has_mutual:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Mutual obligations structure detected',
                'legal_source': self.legal_source
            }

        if has_unilateral:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Unilateral obligations detected - ensure adequate consideration provided',
                'legal_source': self.legal_source,
                'suggestion': 'For employment NDAs, ensure consideration is provided (e.g., employment, payment). Consider mutual obligations for business NDAs.'
            }

        return {
            'status': 'WARNING',
            'severity': 'low',
            'message': 'Unable to determine if obligations are mutual or unilateral',
            'legal_source': self.legal_source
        }
