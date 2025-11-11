import re


class StatutoryExceptionsGate:
    def __init__(self):
        self.name = "statutory_exceptions"
        self.severity = "critical"
        self.legal_source = "PIDA 1998, GDPR 2018, FCA SYSC, Employment Rights Act 1996"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['nda', 'non-disclosure', 'confidential', 'settlement'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a confidentiality agreement',
                'legal_source': self.legal_source
            }

        # Check for comprehensive statutory exceptions
        required_exceptions = {
            'whistleblowing': [
                r'public\s+interest\s+disclosure\s+act',
                r'whistleblow(?:ing|er)',
                r'protected\s+disclosure'
            ],
            'regulatory': [
                r'(?:FCA|PRA|regulatory\s+authority)',
                r'competent\s+authority',
                r'regulatory\s+report(?:ing)?'
            ],
            'legal_process': [
                r'court\s+order',
                r'legal\s+process',
                r'tribunal',
                r'subpoena'
            ],
            'law_enforcement': [
                r'police',
                r'law\s+enforcement',
                r'prevent.*crime'
            ],
            'gdpr': [
                r'data\s+subject\s+(?:access\s+)?request',
                r'(?:GDPR|data\s+protection)',
                r'information\s+commissioner'
            ],
            'professional_advisers': [
                r'legal\s+(?:adviser|counsel)',
                r'professional\s+adviser',
                r'auditor'
            ],
            'employment_rights': [
                r'employment\s+tribunal',
                r'ACAS',
                r'statutory\s+right'
            ]
        }

        found_exceptions = {}
        missing_exceptions = []

        for category, patterns in required_exceptions.items():
            found = any(re.search(p, text, re.IGNORECASE) for p in patterns)
            found_exceptions[category] = found
            if not found:
                missing_exceptions.append(category)

        # Calculate coverage
        coverage = sum(found_exceptions.values()) / len(required_exceptions) * 100

        if coverage >= 85:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive statutory exceptions covered ({coverage:.0f}%)',
                'legal_source': self.legal_source,
                'details': found_exceptions
            }

        if coverage >= 50:
            return {
                'status': 'WARNING',
                'severity': 'high',
                'message': f'Some statutory exceptions missing ({coverage:.0f}% coverage)',
                'legal_source': self.legal_source,
                'suggestion': f'Consider adding exceptions for: {", ".join(missing_exceptions)}',
                'missing': missing_exceptions
            }

        return {
            'status': 'FAIL',
            'severity': 'critical',
            'message': f'Insufficient statutory exceptions ({coverage:.0f}% coverage)',
            'legal_source': self.legal_source,
            'suggestion': 'Add comprehensive carve-outs for: whistleblowing, regulatory reporting, legal process, GDPR compliance, professional advisers',
            'penalty': 'Overly broad restrictions may be void and unenforceable',
            'missing': missing_exceptions
        }
