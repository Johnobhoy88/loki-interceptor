"""
PECR Cookie Consent Validator
Validates cookie compliance under PECR (Privacy and Electronic Communications Regulations)

UK PECR Regulation 6: Cookies require consent unless:
- Strictly necessary for service requested by user
- For communication transmission

ICO Guidance: Cookies and similar technologies
"""

import re
from typing import Dict, List, Set


class CookieConsentValidator:
    """
    Validates cookie consent compliance with PECR
    References: PECR Regulation 6; ICO Cookies Guidance; ePrivacy Directive
    """

    def __init__(self):
        self.legal_source = "PECR Regulation 6; ICO Cookies Guidance; ePrivacy Directive"

        # Cookie types
        self.cookie_types = {
            'strictly_necessary': {
                'patterns': [
                    r'strictly\s+necessary',
                    r'essential\s+cookies?',
                    r'required\s+for.*(?:function|operation)',
                    r'necessary\s+for.*service',
                ],
                'consent_required': False
            },
            'functional': {
                'patterns': [
                    r'functional\s+cookies?',
                    r'preference\s+cookies?',
                    r'remember.*(?:settings|preference)',
                ],
                'consent_required': True
            },
            'analytics': {
                'patterns': [
                    r'analytics?\s+cookies?',
                    r'performance\s+cookies?',
                    r'google\s+analytics',
                    r'tracking.*(?:usage|behavior)',
                    r'(?:measure|monitor).*(?:traffic|usage)',
                ],
                'consent_required': True
            },
            'advertising': {
                'patterns': [
                    r'advertising\s+cookies?',
                    r'marketing\s+cookies?',
                    r'targeted\s+(?:ads|advertising)',
                    r'personali[sz]ed\s+(?:ads|advertising)',
                    r'behavioral\s+advertising',
                ],
                'consent_required': True
            },
            'social_media': {
                'patterns': [
                    r'social\s+media\s+cookies?',
                    r'(?:facebook|twitter|linkedin|instagram).*(?:cookie|pixel)',
                    r'social\s+(?:sharing|plugin)',
                ],
                'consent_required': True
            }
        }

        # Third-party cookie providers that need special attention
        self.third_party_providers = [
            'google analytics', 'facebook pixel', 'doubleclick',
            'google tag manager', 'hotjar', 'mixpanel', 'segment',
            'hubspot', 'intercom', 'drift'
        ]

    def validate_cookie_compliance(self, text: str) -> Dict:
        """
        Validates cookie consent compliance with PECR

        Returns:
            Dict with validation results including:
            - has_cookies: bool
            - is_compliant: bool
            - cookie_types_found: List[str]
            - consent_required_types: List[str]
            - has_consent_mechanism: bool
            - issues: List[str]
            - warnings: List[str]
            - suggestions: List[str]
        """
        results = {
            'has_cookies': False,
            'is_compliant': False,
            'cookie_types_found': [],
            'consent_required_types': [],
            'has_consent_mechanism': False,
            'has_granular_control': False,
            'third_party_cookies': [],
            'issues': [],
            'warnings': [],
            'suggestions': [],
            'severity': 'none'
        }

        if not text:
            return results

        text_lower = text.lower()

        # 1. Check if cookies are mentioned
        cookies_mentioned = self._check_cookies_mentioned(text_lower)

        if not cookies_mentioned:
            # No cookies mentioned - compliant by default
            return results

        results['has_cookies'] = True

        # 2. Identify cookie types
        cookie_types = self._identify_cookie_types(text_lower)
        results['cookie_types_found'] = list(cookie_types.keys())

        # 3. Identify which types need consent
        for cookie_type, info in cookie_types.items():
            if info['consent_required']:
                results['consent_required_types'].append(cookie_type)

        # 4. Check for consent mechanism
        consent_info = self._check_consent_mechanism(text_lower)
        results['has_consent_mechanism'] = consent_info['has_mechanism']
        results['has_granular_control'] = consent_info['is_granular']

        # 5. Check for third-party cookies
        third_party = self._check_third_party_cookies(text_lower)
        results['third_party_cookies'] = third_party

        # 6. Validate consent for non-essential cookies
        if results['consent_required_types'] and not results['has_consent_mechanism']:
            results['issues'].append(
                f"Non-essential cookies ({', '.join(results['consent_required_types'])}) "
                f"require consent but no consent mechanism described (PECR violation)"
            )
            results['severity'] = 'high'
            results['suggestions'].append(
                "Implement cookie consent banner with: (1) Clear information about cookies, "
                "(2) Opt-in consent (not pre-ticked), (3) Granular controls, (4) Easy to decline"
            )

        # 7. Check for pre-ticked boxes (illegal)
        preticked_issues = self._check_preticked_consent(text_lower)
        results['issues'].extend(preticked_issues)

        # 8. Check for cookie wall (questionable)
        wall_warnings = self._check_cookie_wall(text_lower)
        results['warnings'].extend(wall_warnings)

        # 9. Check for granular controls
        if results['consent_required_types'] and len(results['consent_required_types']) > 1:
            if not results['has_granular_control']:
                results['warnings'].append(
                    "Multiple cookie types require granular consent controls (separate opt-in for each type)"
                )
                results['suggestions'].append(
                    "Provide separate consent toggles for: analytics, advertising, functional, and social media cookies"
                )

        # 10. Check for cookie information requirements
        info_warnings = self._check_cookie_information(text_lower)
        results['warnings'].extend(info_warnings)

        # 11. Check for cookie duration/retention
        if not self._check_cookie_duration(text_lower):
            results['warnings'].append(
                "Cookie retention periods not specified - should state how long cookies last"
            )

        # 12. Check for third-party cookie disclosure
        if results['third_party_cookies']:
            if not self._check_third_party_disclosure(text_lower):
                results['warnings'].append(
                    f"Third-party cookies used ({', '.join(results['third_party_cookies'][:3])}) "
                    f"- should name all third parties"
                )

        # Determine compliance
        results['is_compliant'] = (
            len(results['issues']) == 0 and
            (not results['consent_required_types'] or results['has_consent_mechanism'])
        )

        return results

    def _check_cookies_mentioned(self, text_lower: str) -> bool:
        """Check if cookies are mentioned"""
        cookie_keywords = [
            'cookie', 'tracking technolog', 'similar technolog',
            'local storage', 'pixel', 'web beacon'
        ]
        return any(kw in text_lower for kw in cookie_keywords)

    def _identify_cookie_types(self, text_lower: str) -> Dict:
        """Identify which types of cookies are mentioned"""
        types_found = {}

        for cookie_type, info in self.cookie_types.items():
            if any(re.search(p, text_lower) for p in info['patterns']):
                types_found[cookie_type] = {
                    'consent_required': info['consent_required']
                }

        return types_found

    def _check_consent_mechanism(self, text_lower: str) -> Dict:
        """Check if consent mechanism is described"""
        result = {
            'has_mechanism': False,
            'is_granular': False
        }

        # Consent mechanism patterns
        consent_patterns = [
            r'cookie\s+(?:consent|banner|notice|popup)',
            r'accept\s+cookies',
            r'cookie\s+settings',
            r'manage\s+cookies',
            r'cookie\s+preference',
        ]

        result['has_mechanism'] = any(re.search(p, text_lower) for p in consent_patterns)

        if result['has_mechanism']:
            # Check for granular controls
            granular_patterns = [
                r'(?:choose|select|control).*(?:which|type).*cookie',
                r'granular.*(?:control|consent)',
                r'(?:accept|reject).*(?:individual|specific).*cookie',
                r'customize.*cookie.*(?:setting|preference)',
            ]

            result['is_granular'] = any(re.search(p, text_lower) for p in granular_patterns)

        return result

    def _check_third_party_cookies(self, text_lower: str) -> List[str]:
        """Check for third-party cookie providers"""
        third_party_found = []

        for provider in self.third_party_providers:
            if provider in text_lower:
                third_party_found.append(provider)

        return third_party_found

    def _check_preticked_consent(self, text_lower: str) -> List[str]:
        """Check for pre-ticked consent (illegal under PECR)"""
        issues = []

        preticked_patterns = [
            (r'pre.?ticked', "Pre-ticked cookie consent is illegal (PECR violation)"),
            (r'pre.?selected', "Pre-selected cookie consent is illegal (must be opt-in)"),
            (r'default.*accept', "Default acceptance of cookies is illegal (must be opt-in)"),
            (r'automatically.*accept', "Automatic cookie acceptance is illegal (must be active opt-in)"),
        ]

        for pattern, message in preticked_patterns:
            if re.search(pattern, text_lower):
                issues.append(message)

        return issues

    def _check_cookie_wall(self, text_lower: str) -> List[str]:
        """Check for cookie walls (access denial)"""
        warnings = []

        wall_patterns = [
            r'(?:cannot|unable\s+to).*(?:access|use).*without.*(?:accept|cookie)',
            r'must\s+accept\s+cookies.*(?:to|for).*(?:use|access)',
            r'cookie.*(?:required|mandatory|necessary).*(?:for|to)\s+(?:access|use)',
        ]

        for pattern in wall_patterns:
            if re.search(pattern, text_lower):
                warnings.append(
                    "Cookie wall detected (blocking access without consent) - "
                    "may violate GDPR freely given consent principle"
                )
                break

        return warnings

    def _check_cookie_information(self, text_lower: str) -> List[str]:
        """Check if adequate cookie information is provided"""
        warnings = []

        required_info = {
            'purpose': (
                r'(?:purpose|use|reason).*cookie',
                "Cookie purposes not clearly explained"
            ),
            'types': (
                r'(?:type|categor(?:y|ies)).*cookie',
                "Cookie types/categories not described"
            ),
            'third_party': (
                r'third.?party.*cookie',
                "Third-party cookies not disclosed"
            ),
        }

        for info_type, (pattern, message) in required_info.items():
            if not re.search(pattern, text_lower):
                warnings.append(message)

        return warnings

    def _check_cookie_duration(self, text_lower: str) -> bool:
        """Check if cookie duration/expiry is mentioned"""
        duration_patterns = [
            r'cookie.*(?:last|remain|stored).*(?:for|until)',
            r'(?:expire|expiration|expiry).*cookie',
            r'(?:session|persistent)\s+cookie',
            r'cookie.*(?:duration|retention)',
            r'\d+\s+(?:day|month|year)s?.*cookie',
        ]

        return any(re.search(p, text_lower) for p in duration_patterns)

    def _check_third_party_disclosure(self, text_lower: str) -> bool:
        """Check if third parties are named"""
        disclosure_patterns = [
            r'(?:list|name|identif(?:y|ies)).*third.?part(?:y|ies)',
            r'third.?part(?:y|ies).*(?:include|such\s+as)',
            r'(?:use|work\s+with).*(?:google|facebook|twitter)',
        ]

        return any(re.search(p, text_lower) for p in disclosure_patterns)


def validate_cookie_consent(text: str) -> Dict:
    """
    Convenience function to validate cookie consent compliance

    Args:
        text: The text to validate

    Returns:
        Dictionary with validation results
    """
    validator = CookieConsentValidator()
    return validator.validate_cookie_compliance(text)
