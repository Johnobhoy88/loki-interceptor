"""
GDPR Consent Validator
Validates consent mechanisms against UK GDPR Articles 6, 7, and 9
ICO Guidance: Consent

Consent must be:
1. Freely given - No coercion, detriment, or bundling
2. Specific - Separate consent for different purposes
3. Informed - Clear information about processing
4. Unambiguous - Clear affirmative action required
5. Withdrawable - Easy to withdraw consent
"""

import re
from typing import Dict, List, Tuple


class ConsentValidator:
    """
    Comprehensive consent validation for UK GDPR compliance
    References: UK GDPR Articles 6, 7, 9; ICO Consent Guidance
    """

    def __init__(self):
        self.legal_source = "UK GDPR Articles 6, 7, 9; DPA 2018; ICO Consent Guidance"

        # Special category data patterns (Article 9)
        self.special_category_patterns = [
            r'health\s+(?:data|information|records)',
            r'medical\s+(?:history|data|information|records)',
            r'biometric\s+(?:data|information)',
            r'genetic\s+(?:data|information)',
            r'racial\s+(?:or\s+)?ethnic\s+origin',
            r'political\s+opinion',
            r'religious\s+(?:or\s+)?philosophical\s+belief',
            r'trade\s+union\s+membership',
            r'sex\s+life',
            r'sexual\s+orientation',
            r'criminal\s+(?:conviction|offence)',
            r'lifestyle\s+(?:data|information)'
        ]

        # Explicit consent patterns (required for Article 9)
        self.explicit_consent_patterns = [
            r'explicit\s+consent',
            r'express\s+(?:written\s+)?consent',
            r'clear\s+affirmative\s+action',
            r'unambiguous\s+indication',
            r'specifically\s+(?:agree|consent)'
        ]

    def validate_consent(self, text: str) -> Dict:
        """
        Validates consent mechanisms in the provided text

        Returns:
            Dict with validation results including:
            - is_valid: bool
            - issues: List[str]
            - warnings: List[str]
            - suggestions: List[str]
            - severity: str
        """
        results = {
            'is_valid': True,
            'issues': [],
            'warnings': [],
            'suggestions': [],
            'severity': 'none',
            'article_9_required': False
        }

        if not text:
            return results

        text_lower = text.lower()

        # Check for special category data processing
        has_special_category = self._check_special_category(text_lower)
        if has_special_category:
            results['article_9_required'] = True
            has_explicit_consent = self._check_explicit_consent(text_lower)

            if not has_explicit_consent:
                results['is_valid'] = False
                results['severity'] = 'critical'
                results['issues'].append(
                    "Special category data processing requires explicit consent (Article 9)"
                )
                results['suggestions'].append(
                    "Add: 'By clicking [I agree], you provide explicit consent to process your "
                    "[health/biometric/etc.] data for [specific purpose].'"
                )

        # 1. Check for freely given consent
        freely_given_issues = self._check_freely_given(text, text_lower)
        results['issues'].extend(freely_given_issues)

        # 2. Check for specific consent (granularity)
        specific_issues = self._check_specific_consent(text_lower)
        results['issues'].extend(specific_issues)

        # 3. Check for informed consent
        informed_issues = self._check_informed_consent(text_lower)
        results['issues'].extend(informed_issues)

        # 4. Check for unambiguous consent
        unambiguous_issues = self._check_unambiguous_consent(text_lower)
        results['issues'].extend(unambiguous_issues)

        # 5. Check for withdrawal mechanism
        withdrawal_issues = self._check_withdrawal_mechanism(text_lower)
        results['issues'].extend(withdrawal_issues)

        # 6. Check for consent records
        if 'consent' in text_lower or 'agree' in text_lower:
            if not re.search(r'(?:record|log|maintain|keep).*consent', text_lower):
                results['warnings'].append(
                    "No mention of consent record keeping (Article 7(1) requires proof)"
                )
                results['suggestions'].append(
                    "Add: 'We maintain records of consent including date, method, and information provided.'"
                )

        # Determine overall validity
        if results['issues']:
            results['is_valid'] = False
            if not results['severity'] or results['severity'] == 'none':
                results['severity'] = 'high' if len(results['issues']) > 2 else 'medium'

        return results

    def _check_special_category(self, text_lower: str) -> bool:
        """Check if text mentions special category data"""
        return any(re.search(pattern, text_lower) for pattern in self.special_category_patterns)

    def _check_explicit_consent(self, text_lower: str) -> bool:
        """Check for explicit consent language"""
        return any(re.search(pattern, text_lower) for pattern in self.explicit_consent_patterns)

    def _check_freely_given(self, text: str, text_lower: str) -> List[str]:
        """
        Check if consent is freely given (not coerced or bundled)
        ICO: Consent cannot be forced or tied to services unnecessarily
        """
        issues = []

        # Forced consent patterns
        forced_patterns = [
            (r'by\s+using.*(?:you\s+)?(?:agree|consent)',
             "Forced consent: 'by using' implies non-optional consent"),
            (r'by\s+(?:accessing|visiting|browsing).*(?:agree|consent)',
             "Forced consent: access should not automatically imply consent"),
            (r'continued\s+use.*constitutes.*(?:agreement|consent)',
             "Forced consent: continued use cannot constitute consent"),
            (r'if\s+you\s+(?:continue|proceed).*you\s+(?:agree|consent)',
             "Forced consent: proceeding should not imply consent"),
            (r'(?:cannot|unable to|will not).*(?:provide|offer).*(?:without|unless).*(?:consent|agree)',
             "Conditional consent: service tied to consent (only valid if strictly necessary)"),
        ]

        for pattern, message in forced_patterns:
            if re.search(pattern, text_lower):
                issues.append(message)

        # Bundled consent (all-or-nothing)
        bundled_patterns = [
            r'(?:agree|consent)\s+to\s+(?:all|everything|the\s+following)',
            r'accept\s+(?:all|the).*terms.*and.*privacy',
            r'consent.*(?:and|&).*(?:marketing|advertising|profiling)',
        ]

        for pattern in bundled_patterns:
            if re.search(pattern, text_lower):
                issues.append(
                    "Bundled consent: Must provide separate consent for different purposes"
                )
                break

        # Negative consequences for non-consent
        if re.search(r'if\s+you\s+(?:do\s+not|don.?t)\s+(?:agree|consent).*(?:will\s+not|cannot|unable)', text_lower):
            if not re.search(r'strictly\s+necessary|essential\s+for\s+the\s+service', text_lower):
                issues.append(
                    "Negative consequences implied for not consenting (only valid if strictly necessary)"
                )

        return issues

    def _check_specific_consent(self, text_lower: str) -> List[str]:
        """
        Check if consent is specific and granular
        ICO: Separate consent required for different purposes
        """
        issues = []

        # Check for vague/blanket consent
        vague_patterns = [
            r'consent.*(?:to\s+)?(?:any|all|everything)',
            r'agree.*(?:to\s+)?any.*changes',
            r'consent.*in\s+the\s+future',
            r'general\s+consent',
            r'blanket\s+(?:consent|agreement)',
        ]

        for pattern in vague_patterns:
            if re.search(pattern, text_lower):
                issues.append(
                    "Vague/blanket consent: Must be specific to particular purposes"
                )
                break

        # If multiple purposes mentioned, should have granular consent
        purposes_count = 0
        purpose_keywords = ['marketing', 'advertising', 'analytics', 'profiling',
                           'sharing', 'third party', 'research', 'direct marketing']

        for keyword in purpose_keywords:
            if keyword in text_lower:
                purposes_count += 1

        if purposes_count > 1:
            # Check for granular consent options
            if not re.search(r'(?:separate|individual|granular|each)\s+(?:consent|choice|option)', text_lower):
                issues.append(
                    f"Multiple purposes detected ({purposes_count}) - must provide granular consent options"
                )

        return issues

    def _check_informed_consent(self, text_lower: str) -> List[str]:
        """
        Check if consent is informed (clear information provided)
        ICO: Must clearly explain what users are consenting to
        """
        issues = []

        has_consent_request = re.search(r'consent|agree|permission', text_lower)

        if has_consent_request:
            # Check for key information elements
            info_elements = {
                'identity': r'(?:we|our company|data controller|identity)',
                'purpose': r'purpose|reason|why we',
                'data_types': r'(?:personal\s+)?data|information.*(?:collect|process)',
                'rights': r'right.*(?:withdraw|access|erasure)',
            }

            missing_elements = []
            for element, pattern in info_elements.items():
                if not re.search(pattern, text_lower):
                    missing_elements.append(element)

            if len(missing_elements) >= 2:
                issues.append(
                    f"Insufficient information for informed consent. Missing: {', '.join(missing_elements)}"
                )

        return issues

    def _check_unambiguous_consent(self, text_lower: str) -> List[str]:
        """
        Check if consent requires clear affirmative action
        ICO: Pre-ticked boxes, inactivity, and silence are not valid consent
        """
        issues = []

        # Pre-selected/default consent patterns
        preselected_patterns = [
            (r'automatically.*(?:agree|consent|subscribe)', "Automatic consent is not valid"),
            (r'opt.?out.*if\s+you\s+(?:do\s+not|don.?t)\s+want', "Opt-out is not valid consent (must be opt-in)"),
            (r'unless\s+you\s+(?:tell|notify|inform)\s+us\s+otherwise', "Silence/inactivity cannot constitute consent"),
            (r'presumed.*consent', "Presumed consent is not valid"),
            (r'deemed.*(?:to\s+have\s+)?(?:agreed|consented)', "Deemed consent is not valid"),
            (r'pre.?selected|pre.?ticked', "Pre-selected boxes are not valid consent"),
        ]

        for pattern, message in preselected_patterns:
            if re.search(pattern, text_lower):
                issues.append(message)

        return issues

    def _check_withdrawal_mechanism(self, text_lower: str) -> List[str]:
        """
        Check if withdrawal mechanism is described
        ICO: Must be as easy to withdraw as to give consent
        """
        issues = []

        has_consent_request = re.search(r'consent|agree', text_lower)

        if has_consent_request:
            withdrawal_patterns = [
                r'withdraw.*consent',
                r'opt.?out',
                r'unsubscribe',
                r'remove.*consent',
                r'revoke.*consent',
                r'change.*(?:your\s+)?(?:mind|preference)',
            ]

            has_withdrawal = any(re.search(p, text_lower) for p in withdrawal_patterns)

            if not has_withdrawal:
                issues.append(
                    "No withdrawal mechanism described (Article 7(3) requires easy withdrawal)"
                )
            else:
                # Check if withdrawal is made difficult
                difficult_patterns = [
                    r'withdraw.*(?:by\s+)?(?:writing\s+to|contacting)',
                    r'(?:must|need\s+to).*write.*(?:to\s+)?(?:withdraw|opt.?out)',
                ]

                for pattern in difficult_patterns:
                    if re.search(pattern, text_lower):
                        issues.append(
                            "Withdrawal appears difficult (must be as easy as giving consent)"
                        )
                        break

        return issues


def validate_consent_text(text: str) -> Dict:
    """
    Convenience function to validate consent in text

    Args:
        text: The text to validate

    Returns:
        Dictionary with validation results
    """
    validator = ConsentValidator()
    return validator.validate_consent(text)
