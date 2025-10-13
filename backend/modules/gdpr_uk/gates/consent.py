import re


class ConsentGate:
    def __init__(self):
        self.name = "gdpr_consent"
        self.severity = "critical"
        self.legal_source = "GDPR Article 6 & 7"
        # Content relevance indicators: mentions data collection/processing
        self.relevance_keywords = [
            'collect', 'collection', 'process', 'processing', 'data collection', 'data processing',
            'personal data', 'personal information', 'your data', 'your information',
            'privacy policy', 'privacy notice'
        ]

        self.patterns = [
            r'consent',
            r'agree to',
            r'opt.?in',
            r'permission to process',
            r'lawful basis'
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
                'message': 'Not applicable - document does not involve data collection or consent for processing',
                'legal_source': self.legal_source
            }

        # 2. Check for forced/implied consent (GDPR violation)
        issues = []
        spans = []

        forced_consent_patterns = [
            r'by\s+using.*(?:you\s+)?agree',
            r'by\s+(?:accessing|visiting|browsing).*(?:you\s+)?(?:agree|consent)',
            r'continued\s+use.*constitutes.*(?:agreement|consent)',
            r'use\s+of.*(?:implies|indicates).*(?:agreement|consent)',
            r'if\s+you\s+(?:continue|proceed).*you\s+(?:agree|consent)',
            r'access.*(?:means|implies).*(?:you\s+)?(?:agree|accept)'
        ]

        for pattern in forced_consent_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                spans.append({
                    'type': 'forced_consent',
                    'start': match.start(),
                    'end': match.end(),
                    'text': match.group(),
                    'severity': 'critical'
                })
                issues.append(f"Forced consent: '{match.group()}'")

        # Check for bundled consent (asking for multiple things at once)
        bundled_patterns = [
            r'(?:agree|consent)\s+to.*(?:and|,).*(?:and|,)',  # consent to X, Y, and Z
            r'accept\s+(?:all|the).*terms.*(?:and|including).*privacy',
            r'consent.*(?:processing|use|sharing).*and.*(?:marketing|advertising)'
        ]

        for pattern in bundled_patterns:
            match = re.search(pattern, content_lower)
            if match:
                issues.append("Bundled consent detected - must be separate for each purpose")

        # Check for pre-selected/default consent
        pre_selected_patterns = [
            r'automatically.*(?:agree|consent|subscribe)',
            r'opt.?out.*if\s+you\s+(?:do\s+not|don.?t)\s+want',
            r'unless\s+you\s+(?:tell|notify|inform)\s+us\s+otherwise',
            r'presumed.*consent',
            r'deemed.*(?:to\s+have\s+)?(?:agreed|consented)'
        ]

        for pattern in pre_selected_patterns:
            match = re.search(pattern, content_lower)
            if match:
                issues.append("Pre-selected/opt-out consent - must be opt-in")

        # Check for vague consent language
        vague_patterns = [
            r'(?:agree|consent).*(?:to\s+)?(?:everything|all|any)',
            r'accept.*any.*changes',
            r'consent.*(?:now\s+and\s+)?in\s+the\s+future'
        ]

        for pattern in vague_patterns:
            match = re.search(pattern, content_lower)
            if match:
                issues.append("Vague consent scope - must be specific and granular")

        # Check for conditional service
        conditional_patterns = [
            r'(?:cannot|unable to|will not).*(?:provide|offer|use).*(?:service|feature).*(?:without|unless).*(?:consent|agree)',
            r'must\s+(?:agree|consent|accept).*(?:to\s+)?(?:use|access)',
            r'consent.*(?:is\s+)?(?:required|mandatory|necessary).*(?:for|to\s+use)'
        ]

        has_conditional = False
        for pattern in conditional_patterns:
            if re.search(pattern, content_lower):
                has_conditional = True
                # This is only OK if it's strictly necessary for the service
                if not re.search(r'(?:strictly\s+)?necessary|essential|required\s+for\s+the\s+service', content_lower):
                    issues.append("Consent tied to service without showing it's strictly necessary")

        if spans or len(issues) > 0:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': f'Consent violations detected ({len(issues)} issues)',
                'spans': spans,
                'details': issues,
                'legal_source': self.legal_source,
                'suggestion': 'Consent must be: (1) Freely given (not forced), (2) Specific (separate for each purpose), (3) Informed (clear info), (4) Unambiguous (clear affirmative action), (5) Easy to withdraw',
                'penalty': 'GDPR fines up to €20M or 4% global revenue'
            }

        # 3. Check if proper consent mechanism is present
        has_consent_mechanism = False
        for pattern in self.patterns:
            if re.search(pattern, content, re.IGNORECASE):
                has_consent_mechanism = True
                break

        # Check for withdrawal mechanism
        withdrawal_patterns = [
            r'withdraw.*consent',
            r'opt.?out',
            r'unsubscribe',
            r'remove.*consent',
            r'revoke.*consent'
        ]

        has_withdrawal = any(re.search(p, content_lower) for p in withdrawal_patterns)

        if has_consent_mechanism:
            if not has_withdrawal:
                return {
                    'status': 'WARNING',
                    'severity': 'high',
                    'message': 'Consent mechanism present but no clear withdrawal method',
                    'suggestion': 'Include information about how users can withdraw consent',
                    'legal_source': self.legal_source
                }

            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Consent mechanism and withdrawal properly described'
            }

        return {
            'status': 'FAIL',
            'severity': 'critical',
            'message': 'No consent or lawful basis for data processing',
            'legal_source': self.legal_source,
            'suggestion': 'State the lawful basis for processing (consent, legitimate interest, contract, legal obligation, vital interests, or public task)',
            'penalty': 'GDPR fines up to €20M or 4% global revenue'
        }
