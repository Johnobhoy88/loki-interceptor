import re


class CookiesTrackingGate:
    def __init__(self):
        self.name = "cookies_tracking"
        self.severity = "medium"
        self.legal_source = "PECR & GDPR"
    
    def _is_relevant(self, text):
        text_lower = text.lower()
        return any(kw in text_lower for kw in ['cookie', 'tracking', 'analytics', 'website'])
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not discuss cookies or tracking technologies',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()
        cookie_disclosure = [
            r'cookie',
            r'tracking.*technolog',
            r'analytics',
            r'similar.*technolog'
        ]

        mentions_cookies = any(re.search(p, text, re.IGNORECASE) for p in cookie_disclosure)

        if not mentions_cookies:
            return {'status': 'PASS', 'severity': 'none', 'message': 'No cookies/tracking mentioned', 'spans': []}

        issues = []
        warnings = []
        spans = []

        # Check for problematic patterns
        problematic_patterns = [
            (r'you\s+agree\s+to.*(?:cookie|privacy policy)', 'Implied consent without opt-in'),
            (r'by\s+(?:using|continuing|accessing).*you\s+(?:agree|consent)', 'Consent by use (not valid for cookies)'),
            (r'cannot\s+opt\s*out.*essential.*cookie', 'No opt-out for "essential" cookies claim'),
            (r'accept.*(?:all|our).*cookie', 'Pre-checked accept all cookies')
        ]

        for pattern, issue_text in problematic_patterns:
            if re.search(pattern, text_lower):
                issues.append(issue_text)

        # Check for consent/control mechanism
        control_patterns = [
            r'manage.*cookie',
            r'cookie.*setting',
            r'cookie.*preference',
            r'opt.*out',
            r'consent.*cookie',
            r'accept.*only.*necessary',
            r'reject.*all.*cookie'
        ]

        has_controls = any(re.search(p, text_lower) for p in control_patterns)

        # Check if mentions granular control
        has_granular = bool(re.search(r'(?:choose|select|customize).*(?:cookie|preference)', text_lower))

        if not has_controls:
            issues.append("No cookie control/opt-out mechanism mentioned")

        if has_controls and not has_granular:
            warnings.append("Cookie controls mentioned but no granular choice (accept/reject by category)")

        # Check for essential vs non-essential distinction
        mentions_essential = bool(re.search(r'essential.*cookie|strictly.*necessary', text_lower))
        if mentions_essential and not has_granular:
            warnings.append("Mentions essential cookies but doesn't distinguish from non-essential")

        for p in cookie_disclosure:
            for m in re.finditer(p, text, re.IGNORECASE):
                spans.append({'type': 'cookie_tracking', 'start': m.start(), 'end': m.end(), 'text': m.group(), 'severity': 'medium' if issues else 'low'})

        if issues:
            return {
                'status': 'FAIL',
                'severity': 'high',
                'message': 'Invalid cookie consent mechanism',
                'details': issues,
                'spans': spans,
                'legal_source': self.legal_source,
                'suggestion': 'Cookie consent must be: (1) opt-in not opt-out, (2) granular by category, (3) not implied by continued use',
                'penalty': 'ICO can fine up to £17.5M or 4% of global turnover (whichever is higher)'
            }

        if warnings:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Cookie controls could be clearer',
                'details': warnings,
                'spans': spans,
                'suggestion': 'Provide granular controls: Accept All / Reject All / Manage Preferences (by category)'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Cookie controls properly implemented',
            'spans': []
        }
