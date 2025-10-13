import re


class ThirdPartySharingGate:
    def __init__(self):
        self.name = "third_party_sharing"
        self.severity = "high"
        self.legal_source = "GDPR Article 13(1)(e)"
    
    def _is_relevant(self, text):
        text_lower = text.lower()
        return any(kw in text_lower for kw in ['privacy', 'data', 'share', 'third party'])
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not involve sharing data with third parties',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()

        third_party_patterns = [
            r'third part(?:y|ies)',
            r'share.*(?:with|your\s+data)',
            r'(?:data )?processor',
            r'service provider'
        ]

        mentions_third_party = any(re.search(p, text, re.IGNORECASE) for p in third_party_patterns)

        if not mentions_third_party:
            return {'status': 'PASS', 'severity': 'none', 'message': 'No third party sharing mentioned', 'spans': []}

        # Check for sharing for marketing without clear consent
        marketing_patterns = [
            r'share.*(?:for|with).*marketing',
            r'marketing\s+purposes?',
            r'third\s+part(?:y|ies).*marketing'
        ]

        has_marketing = any(re.search(p, text, re.IGNORECASE) for p in marketing_patterns)

        # Check if explicit consent is mentioned
        consent_patterns = [
            r'with\s+your\s+(?:explicit\s+)?consent',
            r'if\s+you\s+consent',
            r'only\s+with\s+permission',
            r'opt.?in'
        ]

        has_consent = any(re.search(p, text, re.IGNORECASE) for p in consent_patterns)

        # Marketing sharing without clear consent = violation
        if has_marketing and not has_consent:
            spans = []
            for p in marketing_patterns:
                for m in re.finditer(p, text, re.IGNORECASE):
                    spans.append({'type': 'marketing_without_consent', 'start': m.start(), 'end': m.end(), 'text': m.group(), 'severity': 'critical'})

            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Third party marketing sharing without explicit consent',
                'legal_source': self.legal_source,
                'spans': spans,
                'suggestion': 'Marketing requires explicit consent. Add: "We will only share your data for marketing with your explicit consent, which you can provide/withdraw at any time."'
            }

        # If third parties mentioned, check for disclosure details
        disclosure_patterns = [r'listed below', r'including:', r'such as', r'specifically', r'named']

        if any(re.search(p, text, re.IGNORECASE) for p in disclosure_patterns):
            return {'status': 'PASS', 'severity': 'none', 'message': 'Third party sharing disclosed', 'spans': []}

        # Collect spans for third-party mentions if disclosure is missing
        spans = []
        for p in third_party_patterns:
            for m in re.finditer(p, text, re.IGNORECASE):
                spans.append({'type': 'third_party_mention', 'start': m.start(), 'end': m.end(), 'text': m.group(), 'severity': 'high'})

        return {
            'status': 'FAIL',
            'severity': 'high',
            'message': 'Third party sharing mentioned but not clearly disclosed',
            'legal_source': self.legal_source,
            'spans': spans,
            'suggestion': 'List specific third parties or categories: "We share data with: [service providers]"'
        }
