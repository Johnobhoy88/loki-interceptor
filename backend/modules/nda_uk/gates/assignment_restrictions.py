import re


class AssignmentRestrictionsGate:
    def __init__(self):
        self.name = "assignment_restrictions"
        self.severity = "low"
        self.legal_source = "Contract Law, Assignment principles"

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

        # Check for assignment provisions
        assignment_patterns = [
            r'assign(?:ment)?(?!ed\s+to)',
            r'transfer.*(?:rights|obligations)',
            r'novation',
            r'delegation'
        ]

        has_assignment_clause = any(re.search(p, text, re.IGNORECASE) for p in assignment_patterns)

        if not has_assignment_clause:
            return {
                'status': 'WARNING',
                'severity': 'low',
                'message': 'No assignment provisions',
                'legal_source': self.legal_source,
                'suggestion': 'Consider adding clause addressing assignment of rights and obligations',
                'note': 'Rights are generally assignable unless prohibited; obligations are not assignable without consent'
            }

        # Check for prohibition on assignment
        prohibition_patterns = [
            r'(?:not|shall\s+not|may\s+not).*assign',
            r'no\s+assignment.*without.*(?:consent|approval)',
            r'prohibited.*assign'
        ]

        has_prohibition = any(re.search(p, text, re.IGNORECASE) for p in prohibition_patterns)

        # Check for consent requirement
        consent_patterns = [
            r'(?:with|subject\s+to).*(?:prior\s+)?(?:written\s+)?consent',
            r'consent.*(?:not|to\s+be).*unreasonably\s+(?:withheld|delayed)',
            r'approval.*assign'
        ]

        has_consent = any(re.search(p, text, re.IGNORECASE) for p in consent_patterns)

        # Check for exceptions (e.g., affiliated entities)
        exception_patterns = [
            r'(?:affiliate|subsidiary|parent|group\s+compan(?:y|ies))',
            r'successor.*(?:merger|acquisition)',
            r'change\s+of\s+control'
        ]

        has_exceptions = any(re.search(p, text, re.IGNORECASE) for p in exception_patterns)

        # Check for binding on successors
        successors_patterns = [
            r'binding.*(?:successor|assign|heir)',
            r'inure.*benefit.*successor'
        ]

        binds_successors = any(re.search(p, text, re.IGNORECASE) for p in successors_patterns)

        if has_prohibition and has_consent:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Assignment restricted with consent requirement',
                'legal_source': self.legal_source,
                'has_exceptions': has_exceptions
            }

        if has_prohibition:
            return {
                'status': 'WARNING',
                'severity': 'low',
                'message': 'Absolute prohibition on assignment',
                'legal_source': self.legal_source,
                'suggestion': 'Consider allowing assignment with consent or to affiliated entities'
            }

        if has_consent:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Assignment permitted with consent',
                'legal_source': self.legal_source
            }

        return {
            'status': 'WARNING',
            'severity': 'low',
            'message': 'Assignment provisions unclear',
            'legal_source': self.legal_source,
            'suggestion': 'Clarify whether assignment is permitted, prohibited, or requires consent'
        }
