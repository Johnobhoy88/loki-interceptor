"""
GDPR Privacy Notice Completeness Checker
Validates privacy notice/policy against UK GDPR Articles 13-14 requirements

Required information (Article 13 - data collected from subject):
1. Identity and contact details of controller
2. Contact details of DPO (if applicable)
3. Purposes and lawful basis
4. Legitimate interests (if applicable)
5. Recipients or categories of recipients
6. International transfers (if applicable)
7. Retention periods
8. Data subject rights
9. Right to withdraw consent (if applicable)
10. Right to complain to ICO
11. Source of data (if not from subject - Article 14)
12. Automated decision-making (if applicable)

ICO Guidance: The right to be informed
"""

import re
from typing import Dict, List, Set


class PrivacyNoticeChecker:
    """
    Checks privacy notice completeness against UK GDPR requirements
    References: UK GDPR Articles 13-14; ICO Right to be Informed Guidance
    """

    def __init__(self):
        self.legal_source = "UK GDPR Articles 13-14; ICO Right to be Informed Guidance"

        # Required elements for privacy notice (Article 13)
        self.required_elements = {
            'controller_identity': {
                'patterns': [
                    r'(?:we|our company|data controller|controller)',
                    r'(?:name|identity).*(?:of|:).*(?:controller|company|organization)',
                ],
                'article': 'Article 13(1)(a)',
                'critical': True
            },
            'contact_details': {
                'patterns': [
                    r'contact\s+(?:us|details|information)',
                    r'(?:email|phone|address).*:',
                    r'reach\s+us\s+at',
                ],
                'article': 'Article 13(1)(a)',
                'critical': True
            },
            'dpo_contact': {
                'patterns': [
                    r'data\s+protection\s+officer',
                    r'\bDPO\b',
                    r'privacy\s+officer',
                ],
                'article': 'Article 13(1)(b)',
                'critical': False  # Only if DPO appointed
            },
            'purposes': {
                'patterns': [
                    r'purpose[s]?.*(?:of|for).*(?:processing|collect)',
                    r'(?:why|reason).*(?:we|collect|process)',
                    r'use.*(?:your|personal).*data.*(?:for|to)',
                ],
                'article': 'Article 13(1)(c)',
                'critical': True
            },
            'lawful_basis': {
                'patterns': [
                    r'lawful\s+basis',
                    r'legal\s+basis',
                    r'(?:consent|contract|legal\s+obligation|vital\s+interest|public\s+task|legitimate\s+interest)',
                ],
                'article': 'Article 13(1)(c)',
                'critical': True
            },
            'legitimate_interests': {
                'patterns': [
                    r'legitimate\s+interest',
                ],
                'article': 'Article 13(1)(d)',
                'critical': False  # Only if using LI as basis
            },
            'recipients': {
                'patterns': [
                    r'(?:share|disclose|provide).*(?:with|to)',
                    r'recipient[s]?',
                    r'third\s+part(?:y|ies)',
                ],
                'article': 'Article 13(1)(e)',
                'critical': False  # Only if sharing
            },
            'international_transfers': {
                'patterns': [
                    r'international\s+transfer',
                    r'outside.*(?:uk|eu|eea)',
                    r'third\s+countr(?:y|ies)',
                ],
                'article': 'Article 13(1)(f)',
                'critical': False  # Only if transferring
            },
            'retention_period': {
                'patterns': [
                    r'retention\s+period',
                    r'how\s+long.*(?:keep|retain|store)',
                    r'(?:keep|retain|store).*(?:for|until)',
                ],
                'article': 'Article 13(2)(a)',
                'critical': True
            },
            'data_subject_rights': {
                'patterns': [
                    r'your\s+rights',
                    r'data\s+subject\s+rights',
                    r'right\s+to\s+(?:access|rectification|erasure)',
                ],
                'article': 'Article 13(2)(b)',
                'critical': True
            },
            'right_to_withdraw': {
                'patterns': [
                    r'withdraw\s+consent',
                    r'opt.?out',
                    r'unsubscribe',
                ],
                'article': 'Article 13(2)(c)',
                'critical': False  # Only if using consent
            },
            'right_to_complain': {
                'patterns': [
                    r'complain\s+to.*(?:ICO|information\s+commissioner)',
                    r'supervisory\s+authority',
                    r'right\s+to\s+lodge.*complaint',
                ],
                'article': 'Article 13(2)(d)',
                'critical': True
            },
            'automated_decisions': {
                'patterns': [
                    r'automated\s+decision',
                    r'profiling',
                    r'algorithmic.*decision',
                ],
                'article': 'Article 13(2)(f)',
                'critical': False  # Only if using automated decisions
            },
        }

    def check_privacy_notice(self, text: str) -> Dict:
        """
        Checks privacy notice completeness

        Returns:
            Dict with validation results including:
            - is_privacy_notice: bool
            - is_complete: bool
            - completeness_percentage: float
            - elements_present: List[str]
            - elements_missing: List[str]
            - critical_missing: List[str]
            - issues: List[str]
            - warnings: List[str]
            - suggestions: List[str]
        """
        results = {
            'is_privacy_notice': False,
            'is_complete': False,
            'completeness_percentage': 0.0,
            'elements_present': [],
            'elements_missing': [],
            'critical_missing': [],
            'element_details': {},
            'issues': [],
            'warnings': [],
            'suggestions': [],
            'severity': 'none'
        }

        if not text:
            results['issues'].append("No text provided for privacy notice validation")
            return results

        text_lower = text.lower()

        # Check if this is a privacy notice
        is_privacy = self._is_privacy_notice(text_lower)
        results['is_privacy_notice'] = is_privacy

        if not is_privacy:
            results['warnings'].append(
                "Document does not appear to be a privacy notice/policy"
            )
            return results

        # Check each required element
        total_elements = 0
        present_count = 0

        for element_name, element_info in self.required_elements.items():
            # Check if element is contextually required
            is_required = self._is_element_required(element_name, text_lower)

            if is_required:
                total_elements += 1

            # Check if element is present
            is_present = self._check_element(text_lower, element_info['patterns'])

            results['element_details'][element_name] = {
                'present': is_present,
                'required': is_required,
                'article': element_info['article'],
                'critical': element_info['critical']
            }

            if is_present:
                results['elements_present'].append(element_name)
                if is_required:
                    present_count += 1
            else:
                if is_required:
                    results['elements_missing'].append(element_name)
                    if element_info['critical']:
                        results['critical_missing'].append(element_name)

        # Calculate completeness
        if total_elements > 0:
            results['completeness_percentage'] = (present_count / total_elements) * 100

        # Generate issues for critical missing elements
        if results['critical_missing']:
            results['issues'].append(
                f"Critical privacy notice elements missing: {', '.join(results['critical_missing'])}"
            )
            results['severity'] = 'high'

            # Generate specific suggestions
            for element in results['critical_missing']:
                suggestion = self._generate_element_suggestion(element)
                results['suggestions'].append(suggestion)

        # Generate warnings for non-critical missing elements
        non_critical_missing = [e for e in results['elements_missing'] if e not in results['critical_missing']]
        if non_critical_missing:
            results['warnings'].append(
                f"Optional but recommended elements missing: {', '.join(non_critical_missing)}"
            )

        # Additional checks
        additional_checks = self._additional_checks(text_lower)
        results['warnings'].extend(additional_checks)

        # Determine completeness
        results['is_complete'] = (
            len(results['critical_missing']) == 0 and
            results['completeness_percentage'] >= 80
        )

        return results

    def _is_privacy_notice(self, text_lower: str) -> bool:
        """Check if document is a privacy notice/policy"""
        privacy_indicators = [
            'privacy policy', 'privacy notice', 'privacy statement',
            'data protection policy', 'how we use your',
            'personal data', 'personal information'
        ]
        indicator_count = sum(1 for ind in privacy_indicators if ind in text_lower)
        return indicator_count >= 2

    def _check_element(self, text_lower: str, patterns: List[str]) -> bool:
        """Check if element is present using patterns"""
        return any(re.search(p, text_lower) for p in patterns)

    def _is_element_required(self, element_name: str, text_lower: str) -> bool:
        """Check if element is contextually required"""
        # Always required elements
        always_required = [
            'controller_identity', 'contact_details', 'purposes',
            'lawful_basis', 'retention_period', 'data_subject_rights',
            'right_to_complain'
        ]

        if element_name in always_required:
            return True

        # Conditionally required elements
        if element_name == 'dpo_contact':
            # Required if DPO mentioned anywhere
            return 'dpo' in text_lower or 'data protection officer' in text_lower

        if element_name == 'legitimate_interests':
            # Required if using legitimate interest
            return 'legitimate interest' in text_lower

        if element_name == 'recipients':
            # Required if sharing/disclosing
            return any(kw in text_lower for kw in ['share', 'disclose', 'third party', 'recipient'])

        if element_name == 'international_transfers':
            # Required if transferring internationally
            return any(kw in text_lower for kw in ['international', 'outside', 'third country'])

        if element_name == 'right_to_withdraw':
            # Required if using consent
            return 'consent' in text_lower

        if element_name == 'automated_decisions':
            # Required if using automated decisions
            return any(kw in text_lower for kw in ['automated', 'profiling', 'algorithm'])

        return False

    def _generate_element_suggestion(self, element: str) -> str:
        """Generate suggestion for missing element"""
        suggestions = {
            'controller_identity': "Add controller identity: 'We are [Company Name], registered in [location].'",
            'contact_details': "Add contact details: email, postal address, and phone number.",
            'purposes': "List specific purposes: 'We process your data for: [list purposes].'",
            'lawful_basis': "State lawful basis: consent, contract, legal obligation, legitimate interest, etc.",
            'retention_period': "Specify retention: 'We keep your data for [period] or until [event].'",
            'data_subject_rights': "List rights: access, rectification, erasure, restriction, portability, objection.",
            'right_to_complain': "Add: 'You can complain to the ICO at ico.org.uk.'",
        }

        return suggestions.get(element, f"Add required element: {element}")

    def _additional_checks(self, text_lower: str) -> List[str]:
        """Additional privacy notice quality checks"""
        warnings = []

        # Check for clear language
        if not self._check_clear_language(text_lower):
            warnings.append(
                "Privacy notice should use clear, plain language (Article 12 requirement)"
            )

        # Check for layered approach mention
        if len(text_lower) > 5000:  # Long privacy notice
            if not re.search(r'(?:summary|short\s+version|at\s+a\s+glance)', text_lower):
                warnings.append(
                    "Long privacy notice - consider layered approach with summary"
                )

        # Check for last updated date
        if not self._check_last_updated(text_lower):
            warnings.append(
                "No 'last updated' date - best practice to show when policy was last revised"
            )

        # Check for version control
        if not re.search(r'version\s+\d+', text_lower):
            warnings.append(
                "No version number - consider adding for change tracking"
            )

        # Check for how to access full rights
        if not re.search(r'(?:contact\s+us|email\s+us|write\s+to\s+us).*(?:exercise|request)', text_lower):
            warnings.append(
                "Should clearly explain how to exercise rights (contact method)"
            )

        # Check for response timeframe
        if not re.search(r'(?:within|up\s+to)\s+(?:one|1)\s+month', text_lower):
            warnings.append(
                "Should mention response timeframe (1 month for rights requests)"
            )

        return warnings

    def _check_clear_language(self, text_lower: str) -> bool:
        """Check for indicators of clear language"""
        clear_indicators = [
            r'(?:in\s+simple\s+terms|in\s+plain\s+english)',
            r'(?:this\s+means|for\s+example|such\s+as)',
        ]

        # Also check for absence of very complex language
        complex_indicators = [
            r'notwithstanding',
            r'hereinafter',
            r'aforementioned',
        ]

        has_clear = any(re.search(p, text_lower) for p in clear_indicators)
        has_complex = any(re.search(p, text_lower) for p in complex_indicators)

        return has_clear or not has_complex

    def _check_last_updated(self, text_lower: str) -> bool:
        """Check for last updated date"""
        date_patterns = [
            r'last\s+updated',
            r'effective\s+date',
            r'revised\s+(?:on|date)',
            r'version\s+date',
        ]

        return any(re.search(p, text_lower) for p in date_patterns)


def check_privacy_notice_completeness(text: str) -> Dict:
    """
    Convenience function to check privacy notice completeness

    Args:
        text: The text to validate

    Returns:
        Dictionary with validation results
    """
    checker = PrivacyNoticeChecker()
    return checker.check_privacy_notice(text)
