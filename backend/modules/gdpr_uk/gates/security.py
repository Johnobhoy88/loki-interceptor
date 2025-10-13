import re


class SecurityGate:
    def __init__(self):
        self.name = 'gdpr_security_measures'
        self.severity = 'high'
        self.legal_source = 'GDPR Article 32'
        # Content relevance indicators: mentions data protection
        self.relevance_keywords = [
            'data protection', 'protect', 'protection', 'security', 'encryption', 'breach'
        ]
        self.patterns = [
            r'encryption',
            r'pseudonymi[sz]ation',
            r'access controls?',
            r'security measures',
            r'appropriate technical (?:and|&) organisational measures',
            r'protect(?:ion)? of personal data'
        ]

    def _is_relevant(self, text: str) -> bool:
        """Check if content contains indicators this gate applies"""
        t = (text or '').lower()
        return any(keyword in t for keyword in self.relevance_keywords)

    def check(self, text, document_type):
        content = text or ''
        # 1. Content detection - does this text actually need this gate?
        if not self._is_relevant(content):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not discuss data security measures or safeguards',
                'legal_source': self.legal_source
            }

        # 2. Run the actual validation logic
        for pattern in self.patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return {
                    'status': 'PASS',
                    'severity': 'none',
                    'message': 'Security measures referenced'
                }

        return {
            'status': 'FAIL',
            'severity': 'high',
            'message': 'Security measures not clearly described',
            'legal_source': self.legal_source,
            'suggestion': 'Describe encryption, access controls, and organisational measures to protect personal data.'
        }
