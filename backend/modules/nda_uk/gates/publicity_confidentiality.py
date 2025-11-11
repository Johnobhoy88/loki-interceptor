import re


class PublicityConfidentialityGate:
    def __init__(self):
        self.name = "publicity_confidentiality"
        self.severity = "low"
        self.legal_source = "Contract Law, Breach of Confidence"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['nda', 'non-disclosure', 'confidential', 'agreement'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable',
                'legal_source': self.legal_source
            }

        # Check for publicity/announcement restrictions
        publicity_patterns = [
            r'(?:press\s+release|public\s+announcement|publicity)',
            r'announc(?:e|ement)',
            r'disclose.*(?:existence|terms).*(?:agreement|relationship)',
            r'not.*(?:publicize|announce|disclose).*(?:agreement|arrangement)'
        ]

        has_publicity_clause = any(re.search(p, text, re.IGNORECASE) for p in publicity_patterns)

        if not has_publicity_clause:
            return {
                'status': 'N/A',
                'message': 'No publicity/announcement provisions',
                'legal_source': self.legal_source,
                'note': 'Consider adding if parties want to restrict announcements about relationship'
            }

        # Check for mutual consent requirement
        consent_patterns = [
            r'(?:prior|advance).*(?:written\s+)?consent',
            r'(?:mutual|both\s+parties).*(?:agree|consent)',
            r'not.*without.*(?:consent|approval)',
            r'only.*with.*(?:consent|approval)'
        ]

        requires_consent = any(re.search(p, text, re.IGNORECASE) for p in consent_patterns)

        # Check for exceptions
        exception_patterns = {
            'legal_requirement': r'(?:required|compelled).*(?:by\s+)?law',
            'regulatory': r'regulat(?:or|ory).*(?:requirement|filing)',
            'stock_exchange': r'(?:stock\s+exchange|listing\s+rule)',
            'court_order': r'court\s+order',
            'investor_disclosure': r'(?:investor|shareholder).*disclosure'
        }

        found_exceptions = {}
        for exception_type, pattern in exception_patterns.items():
            found_exceptions[exception_type] = bool(re.search(pattern, text, re.IGNORECASE))

        # Check for notice requirement before disclosure
        notice_before_disclosure_patterns = [
            r'(?:notify|notice).*(?:before|prior\s+to).*(?:disclos|announc)',
            r'(?:advance|prior).*notice.*(?:disclosure|announcement)',
            r'reasonably\s+practicable.*notice'
        ]

        requires_notice = any(re.search(p, text, re.IGNORECASE) for p in notice_before_disclosure_patterns)

        # Check if agreement existence is confidential
        agreement_confidential_patterns = [
            r'(?:existence|terms).*(?:this\s+)?agreement.*confidential',
            r'not\s+disclose.*(?:existence|fact).*agreement',
            r'confidential.*(?:nature|existence).*(?:relationship|arrangement)'
        ]

        agreement_is_confidential = any(re.search(p, text, re.IGNORECASE) for p in agreement_confidential_patterns)

        exception_count = sum(found_exceptions.values())

        if requires_consent and exception_count >= 2 and requires_notice:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Comprehensive publicity restrictions with exceptions',
                'legal_source': self.legal_source,
                'requires_consent': requires_consent,
                'exceptions': [k for k, v in found_exceptions.items() if v],
                'agreement_confidential': agreement_is_confidential
            }

        if requires_consent and exception_count >= 1:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Publicity restrictions with consent requirement',
                'legal_source': self.legal_source,
                'suggestion': 'Consider adding notice requirement before mandatory disclosure'
            }

        if requires_consent:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Basic publicity consent requirement',
                'legal_source': self.legal_source,
                'suggestion': 'Add exceptions for legal/regulatory requirements'
            }

        return {
            'status': 'WARNING',
            'severity': 'low',
            'message': 'Publicity restrictions lack detail',
            'legal_source': self.legal_source,
            'suggestion': 'Specify: consent requirement, exceptions for legal obligations, notice requirement'
        }
