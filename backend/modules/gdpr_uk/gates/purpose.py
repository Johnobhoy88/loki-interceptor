import re


class PurposeGate:
    def __init__(self):
        self.name = 'gdpr_purpose_limitation'
        self.severity = 'critical'
        self.legal_source = 'GDPR Article 5(1)(b)'
        # Content relevance indicators: mentions data use/processing
        self.relevance_keywords = [
            'purpose', 'we process', 'process', 'processing', 'use of data', 'use your data',
            'we use', 'we collect', 'personal data', 'personal information',
            'privacy policy', 'privacy notice'
        ]
        self.patterns = [
            r'purpose(?:s)? of (?:the )?processing',
            r'we process (?:your )?data for',
            r'limited to (?:the )?purpose',
            r'not used for (?:other|any other) purposes',
            r'compatible with the (?:original )?purpose'
        ]

    def _is_relevant(self, text: str) -> bool:
        """Check if content contains indicators this gate applies"""
        t = (text or '').lower()
        return any(keyword in t for keyword in self.relevance_keywords)

    def check(self, text, document_type):
        content = text or ''
        content_lower = content.lower()

        # 1. Content detection - does this text actually need this gate?
        if not self._is_relevant(content):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not specify purposes for data processing',
                'legal_source': self.legal_source
            }

        # 2. Check for vague purposes (GDPR violation)
        vague_purposes = [
            r'improve.*business',
            r'business\s+purposes?',
            r'any\s+purpose',
            r'various\s+purposes?',
            r'other\s+purposes?',
            r'legitimate\s+purposes?' # Without specific details
        ]

        spans = []
        for pattern in vague_purposes:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                spans.append({
                    'type': 'vague_purpose',
                    'start': match.start(),
                    'end': match.end(),
                    'text': match.group(),
                    'severity': 'high'
                })

        if spans:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Purpose statement too vague - GDPR requires specific, explicit purposes',
                'spans': spans,
                'legal_source': self.legal_source,
                'suggestion': 'Specify exact purposes: e.g., "to process orders", "to send newsletters", "to improve website functionality"'
            }

        # 3. Check if proper purpose limitation is present
        for pattern in self.patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return {
                    'status': 'PASS',
                    'severity': 'none',
                    'message': 'Purpose limitation described'
                }

        return {
            'status': 'FAIL',
            'severity': 'critical',
            'message': 'No clear purpose limitation for data processing',
            'legal_source': self.legal_source,
            'suggestion': 'State the specific purposes for which personal data is processed and confirm it will not be used for incompatible purposes.'
        }
