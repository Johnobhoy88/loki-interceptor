import re


class AmendmentProceduresGate:
    def __init__(self):
        self.name = "amendment_procedures"
        self.severity = "low"
        self.legal_source = "Contract Law, Variation principles"

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

        # Check for amendment/variation provisions
        amendment_patterns = [
            r'amend(?:ment|ed)?(?!\s+and\s+restated)',
            r'variat(?:ion|ed)',
            r'modif(?:y|ication)',
            r'change.*(?:terms|agreement)',
            r'alter(?:ation)?'
        ]

        has_amendment_clause = any(re.search(p, text, re.IGNORECASE) for p in amendment_patterns)

        if not has_amendment_clause:
            return {
                'status': 'WARNING',
                'severity': 'low',
                'message': 'No amendment/variation provisions',
                'legal_source': self.legal_source,
                'suggestion': 'Consider adding clause specifying how agreement may be amended',
                'note': 'Without explicit provisions, oral amendments may be enforceable'
            }

        # Check for writing requirement
        writing_patterns = [
            r'in\s+writing',
            r'written\s+(?:amendment|variation|agreement)',
            r'signed.*(?:amendment|variation)',
            r'no\s+(?:oral|verbal).*(?:amendment|variation)'
        ]

        requires_writing = any(re.search(p, text, re.IGNORECASE) for p in writing_patterns)

        # Check for mutual consent requirement
        consent_patterns = [
            r'(?:mutual|both\s+parties).*(?:agree|consent)',
            r'agreed.*in\s+writing.*(?:both|all)\s+parties',
            r'signed.*(?:both|all)\s+parties'
        ]

        requires_consent = any(re.search(p, text, re.IGNORECASE) for p in consent_patterns)

        # Check for no oral modification (NOM) clause
        nom_patterns = [
            r'no\s+(?:oral|verbal).*(?:amendment|variation|modification)',
            r'only.*written.*(?:amendment|variation)',
            r'oral.*(?:amendment|variation).*(?:not|invalid)'
        ]

        has_nom = any(re.search(p, text, re.IGNORECASE) for p in nom_patterns)

        if requires_writing and requires_consent and has_nom:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Comprehensive amendment procedures with NOM clause',
                'legal_source': self.legal_source,
                'note': 'NOM clauses are enforceable per MWB v Rock [2018] UKSC 24'
            }

        if requires_writing and requires_consent:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Written amendment with mutual consent required',
                'legal_source': self.legal_source
            }

        if requires_writing:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Written amendment requirement specified',
                'legal_source': self.legal_source,
                'suggestion': 'Consider adding that amendments must be signed by both parties'
            }

        return {
            'status': 'WARNING',
            'severity': 'low',
            'message': 'Amendment provisions lack formality requirements',
            'legal_source': self.legal_source,
            'suggestion': 'Specify that amendments must be in writing and signed by both parties',
            'risk': 'Oral amendments may be enforceable, creating uncertainty'
        }
