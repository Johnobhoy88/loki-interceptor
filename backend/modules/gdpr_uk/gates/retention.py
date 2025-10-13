import re


class RetentionGate:
    def __init__(self):
        self.name = "gdpr_retention"
        self.severity = "high"
        self.legal_source = "GDPR Article 5(1)(e)"
        # Content relevance indicators: privacy notice or data handling
        self.relevance_keywords = [
            'privacy notice', 'privacy policy', 'data handling', 'retain', 'retention', 'storage', 'keep', 'delete', 'stored', 'how long'
        ]
        
        self.patterns = [
            r'retain.*data.*for.*(?:\d+\s+(?:year|month|day))',
            r'retention\s+period',
            r'storage\s+limitation',
            r'keep.*data.*for',
            r'held\s+for.*(?:\d+)',
            r'deleted\s+after'
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
                'message': 'Not applicable - document does not discuss data retention periods or deletion',
                'legal_source': self.legal_source
            }

        # 2. Check for indefinite retention (GDPR violation)
        indefinite_patterns = [
            r'indefinitely',
            r'as\s+long\s+as\s+necessary',
            r'for\s+as\s+long\s+as',
            r'may\s+be\s+retained\s+indefinitely',
            r'permanently',
            r'forever'
        ]

        spans = []
        for pattern in indefinite_patterns:
            for match in re.finditer(pattern, text_lower, re.IGNORECASE):
                spans.append({
                    'type': 'indefinite_retention',
                    'start': match.start(),
                    'end': match.end(),
                    'text': match.group(),
                    'severity': 'high'
                })

        if spans:
            return {
                'status': 'FAIL',
                'severity': 'high',
                'message': 'Indefinite data retention detected - GDPR requires specific timeframes',
                'spans': spans,
                'legal_source': self.legal_source,
                'suggestion': 'Specify exact retention periods (e.g., "6 years for tax records", "2 years for marketing data")'
            }

        # 3. Check if proper retention period is specified
        for pattern in self.patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return {
                    'status': 'PASS',
                    'severity': 'none',
                    'message': 'Retention period specified'
                }

        return {
            'status': 'FAIL',
            'severity': 'high',
            'message': 'No retention period or storage limitation stated',
            'legal_source': self.legal_source,
            'suggestion': 'Specify how long personal data is retained and the criteria used to determine retention periods.'
        }
