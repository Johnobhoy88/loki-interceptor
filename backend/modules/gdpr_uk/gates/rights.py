import re


class RightsGate:
    def __init__(self):
        self.name = "gdpr_rights"
        self.severity = "critical"
        self.legal_source = "GDPR Articles 12-22"
        # Content relevance indicators: relevant if privacy notice
        self.relevance_keywords = [
            'privacy notice', 'privacy policy', 'privacy',
            'personal data', 'personal information', 'data protection'
        ]
        
        # Must find at least 4 of these key rights mentioned
        self.key_rights = [
            r'access.*data',
            r'right.*access',
            r'rectification',
            r'correction.*data',
            r'erasure',
            r'deletion.*data',
            r'delete.*data',
            r'portability',
            r'data.*portability',
            r'restriction.*processing',
            r'object.*processing',
            r'right.*object'
        ]

    def _is_relevant(self, text: str) -> bool:
        """Check if content contains indicators this gate applies"""
        t = (text or '').lower()
        return any(keyword in t for keyword in self.relevance_keywords)

    def check(self, text, document_type):
        text_lower = (text or '').lower()
        # 1. Content detection - does this text actually need this gate?
        if not self._is_relevant(text_lower):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a privacy notice requiring data subject rights information',
                'legal_source': self.legal_source
            }
        
        # 2. Run the actual validation logic
        # Count how many rights are mentioned
        rights_found = 0
        for pattern in self.key_rights:
            if re.search(pattern, text_lower, re.IGNORECASE):
                rights_found += 1
        
        # Need at least 4 different rights mentioned
        if rights_found >= 4:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Data subject rights stated ({rights_found} rights found)'
            }
        
        return {
            'status': 'FAIL',
            'severity': 'critical',
            'message': 'Data subject rights not clearly stated',
            'legal_source': self.legal_source,
            'suggestion': 'List the rights to access, rectification, erasure, portability, restriction, objection, and how to contact the ICO or the DPO.'
        }
