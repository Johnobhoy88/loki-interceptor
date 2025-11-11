"""
GDPR Data Subject Rights Validator
Validates compliance with all 8 data subject rights under UK GDPR

The 8 Data Subject Rights (GDPR Articles 12-22):
1. Right to be informed (Articles 12-14)
2. Right of access (Article 15)
3. Right to rectification (Article 16)
4. Right to erasure/'right to be forgotten' (Article 17)
5. Right to restrict processing (Article 18)
6. Right to data portability (Article 20)
7. Right to object (Article 21)
8. Rights related to automated decision making and profiling (Article 22)

ICO Guidance: Individual Rights
"""

import re
from typing import Dict, List, Set


class SubjectRightsValidator:
    """
    Validates data subject rights disclosure and implementation
    References: UK GDPR Articles 12-22; ICO Individual Rights Guidance
    """

    def __init__(self):
        self.legal_source = "UK GDPR Articles 12-22; DPA 2018; ICO Individual Rights Guidance"

        # Define patterns for each of the 8 rights
        self.rights_patterns = {
            'right_to_be_informed': {
                'patterns': [
                    r'right\s+to\s+be\s+informed',
                    r'inform.*(?:you|individuals).*(?:about|how).*(?:process|use).*data',
                    r'privacy\s+(?:notice|policy|information)',
                    r'transparent.*(?:about|how).*(?:process|use).*data',
                ],
                'article': 'Articles 12-14',
                'description': 'Right to be informed about data processing'
            },
            'right_of_access': {
                'patterns': [
                    r'right\s+(?:of\s+|to\s+)?access',
                    r'access.*(?:your|their).*(?:personal\s+)?data',
                    r'request.*(?:copy|access).*(?:of\s+)?(?:your|their).*data',
                    r'subject\s+access\s+request',
                    r'\bSAR\b',
                ],
                'article': 'Article 15',
                'description': 'Right to access personal data'
            },
            'right_to_rectification': {
                'patterns': [
                    r'right\s+to\s+rectification',
                    r'right\s+to\s+correct',
                    r'rectif(?:y|ication)',
                    r'correct.*(?:inaccurate|incorrect).*data',
                    r'update.*(?:your|their).*(?:personal\s+)?(?:data|information)',
                ],
                'article': 'Article 16',
                'description': 'Right to rectification of inaccurate data'
            },
            'right_to_erasure': {
                'patterns': [
                    r'right\s+to\s+erasure',
                    r'right\s+to\s+be\s+forgotten',
                    r'right\s+to\s+(?:delete|deletion)',
                    r'delete.*(?:your|their).*(?:personal\s+)?data',
                    r'erase.*(?:your|their).*(?:personal\s+)?data',
                    r'remove.*(?:your|their).*(?:personal\s+)?data',
                ],
                'article': 'Article 17',
                'description': 'Right to erasure (right to be forgotten)'
            },
            'right_to_restrict': {
                'patterns': [
                    r'right\s+to\s+restrict(?:ion)?',
                    r'restrict.*processing',
                    r'limit.*(?:how\s+)?(?:we\s+)?(?:process|use).*(?:your|their).*data',
                    r'suspend.*processing',
                ],
                'article': 'Article 18',
                'description': 'Right to restrict processing'
            },
            'right_to_portability': {
                'patterns': [
                    r'right\s+to\s+(?:data\s+)?portability',
                    r'data\s+portability',
                    r'port.*(?:your|their).*data',
                    r'transfer.*(?:your|their).*data.*another.*(?:provider|controller)',
                    r'move.*(?:your|their).*data',
                    r'export.*(?:your|their).*data',
                ],
                'article': 'Article 20',
                'description': 'Right to data portability'
            },
            'right_to_object': {
                'patterns': [
                    r'right\s+to\s+object',
                    r'object\s+to.*processing',
                    r'opt.?out.*processing',
                    r'object.*(?:direct\s+)?marketing',
                    r'stop.*(?:processing|using).*(?:your|their).*data',
                ],
                'article': 'Article 21',
                'description': 'Right to object to processing'
            },
            'automated_decision_rights': {
                'patterns': [
                    r'right.*(?:not\s+to\s+be\s+)?subject.*automated.*decision',
                    r'automated.*decision.?making',
                    r'right.*human.*intervention',
                    r'right.*(?:challenge|contest).*automated.*decision',
                    r'profiling.*right',
                    r'algorithmic.*decision.*right',
                ],
                'article': 'Article 22',
                'description': 'Rights related to automated decision-making'
            }
        }

    def validate_rights_disclosure(self, text: str) -> Dict:
        """
        Validates that all 8 data subject rights are properly disclosed

        Returns:
            Dict with validation results including:
            - is_complete: bool (all 8 rights mentioned)
            - rights_found: List[str] (which rights were found)
            - rights_missing: List[str] (which rights are missing)
            - issues: List[str]
            - suggestions: List[str]
            - coverage_percentage: float
        """
        results = {
            'is_complete': False,
            'rights_found': [],
            'rights_missing': [],
            'issues': [],
            'warnings': [],
            'suggestions': [],
            'coverage_percentage': 0.0,
            'details': {}
        }

        if not text:
            results['issues'].append("No text provided for rights validation")
            return results

        text_lower = text.lower()

        # Check if this is a privacy policy/notice (relevance check)
        is_privacy_doc = self._is_privacy_document(text_lower)

        if not is_privacy_doc:
            results['warnings'].append(
                "Document does not appear to be a privacy policy - rights disclosure may not be required"
            )
            return results

        # Check each of the 8 rights
        for right_name, right_info in self.rights_patterns.items():
            found = self._check_right(text, text_lower, right_info['patterns'])

            results['details'][right_name] = {
                'found': found,
                'article': right_info['article'],
                'description': right_info['description']
            }

            if found:
                results['rights_found'].append(right_name)
            else:
                results['rights_missing'].append(right_name)

        # Calculate coverage
        rights_count = len(self.rights_patterns)
        found_count = len(results['rights_found'])
        results['coverage_percentage'] = (found_count / rights_count) * 100

        # Determine completeness (need all 8 rights for UK GDPR compliance)
        results['is_complete'] = found_count == rights_count

        # Generate issues and suggestions
        if not results['is_complete']:
            results['issues'].append(
                f"Only {found_count} of 8 required data subject rights disclosed ({results['coverage_percentage']:.0f}%)"
            )

            # Critical missing rights
            critical_rights = ['right_of_access', 'right_to_erasure', 'right_to_rectification']
            missing_critical = [r for r in critical_rights if r in results['rights_missing']]

            if missing_critical:
                results['issues'].append(
                    f"Critical rights missing: {', '.join(missing_critical)}"
                )

            # Generate specific suggestions
            for missing_right in results['rights_missing']:
                right_info = self.rights_patterns[missing_right]
                suggestion = self._generate_suggestion(missing_right, right_info)
                results['suggestions'].append(suggestion)

        # Check for response timeframe (Article 12)
        if not self._check_response_timeframe(text_lower):
            results['warnings'].append(
                "No mention of response timeframe for rights requests (must respond within 1 month, extendable to 3)"
            )
            results['suggestions'].append(
                "Add: 'We will respond to your request within one month, or inform you if we need longer (up to 3 months for complex requests).'"
            )

        # Check for how to exercise rights
        if not self._check_exercise_mechanism(text_lower):
            results['warnings'].append(
                "No clear mechanism for exercising rights (should provide contact details/online portal)"
            )
            results['suggestions'].append(
                "Add contact details: email, postal address, or online portal for submitting rights requests."
            )

        # Check for verification process
        if not self._check_verification(text_lower):
            results['warnings'].append(
                "No mention of identity verification for rights requests"
            )
            results['suggestions'].append(
                "Add: 'We may request proof of identity to verify your request and protect your data.'"
            )

        # Check for ICO complaint rights
        if not self._check_ico_complaint(text_lower):
            results['warnings'].append(
                "No mention of right to complain to the ICO"
            )
            results['suggestions'].append(
                "Add: 'You have the right to complain to the Information Commissioner's Office (ICO) at ico.org.uk if you believe your rights have been infringed.'"
            )

        return results

    def _is_privacy_document(self, text_lower: str) -> bool:
        """Check if document appears to be a privacy policy/notice"""
        privacy_indicators = [
            'privacy policy', 'privacy notice', 'data protection',
            'personal data', 'personal information',
            'how we use', 'how we process', 'data controller'
        ]
        return any(indicator in text_lower for indicator in privacy_indicators)

    def _check_right(self, text: str, text_lower: str, patterns: List[str]) -> bool:
        """Check if a specific right is mentioned using the provided patterns"""
        return any(re.search(pattern, text_lower) for pattern in patterns)

    def _check_response_timeframe(self, text_lower: str) -> bool:
        """Check if response timeframe is mentioned"""
        timeframe_patterns = [
            r'(?:within|up\s+to)\s+(?:one|1)\s+month',
            r'(?:30|thirty)\s+days',
            r'respond.*(?:within|up\s+to).*(?:days|month)',
        ]
        return any(re.search(pattern, text_lower) for pattern in timeframe_patterns)

    def _check_exercise_mechanism(self, text_lower: str) -> bool:
        """Check if mechanism for exercising rights is provided"""
        mechanism_patterns = [
            r'contact.*(?:us|dpo|data\s+protection)',
            r'(?:email|write\s+to).*(?:dpo|data\s+protection)',
            r'submit.*request.*(?:via|through|at)',
            r'online\s+portal',
            r'privacy@',
            r'dpo@',
        ]
        return any(re.search(pattern, text_lower) for pattern in mechanism_patterns)

    def _check_verification(self, text_lower: str) -> bool:
        """Check if identity verification is mentioned"""
        verification_patterns = [
            r'verif(?:y|ication).*identity',
            r'proof\s+of\s+identity',
            r'confirm.*identity',
            r'validate.*identity',
        ]
        return any(re.search(pattern, text_lower) for pattern in verification_patterns)

    def _check_ico_complaint(self, text_lower: str) -> bool:
        """Check if right to complain to ICO is mentioned"""
        ico_patterns = [
            r'ico',
            r'information\s+commissioner',
            r'supervisory\s+authority',
            r'data\s+protection\s+authority',
            r'complain.*regulator',
        ]
        return any(re.search(pattern, text_lower) for pattern in ico_patterns)

    def _generate_suggestion(self, right_name: str, right_info: Dict) -> str:
        """Generate a suggestion for a missing right"""
        suggestions_map = {
            'right_to_be_informed': (
                f"Add {right_info['article']}: 'We provide transparent information about how we collect and use your personal data in this privacy notice.'"
            ),
            'right_of_access': (
                f"Add {right_info['article']}: 'You have the right to access your personal data. Submit a Subject Access Request (SAR) to receive a copy of your data.'"
            ),
            'right_to_rectification': (
                f"Add {right_info['article']}: 'You have the right to rectification of inaccurate or incomplete personal data. Contact us to update your information.'"
            ),
            'right_to_erasure': (
                f"Add {right_info['article']}: 'You have the right to erasure (right to be forgotten). Request deletion of your personal data in certain circumstances.'"
            ),
            'right_to_restrict': (
                f"Add {right_info['article']}: 'You have the right to restrict processing of your personal data in certain circumstances.'"
            ),
            'right_to_portability': (
                f"Add {right_info['article']}: 'You have the right to data portability. Request your data in a structured, machine-readable format to transfer to another provider.'"
            ),
            'right_to_object': (
                f"Add {right_info['article']}: 'You have the right to object to processing, including for direct marketing purposes. Contact us to opt out.'"
            ),
            'automated_decision_rights': (
                f"Add {right_info['article']}: 'You have the right not to be subject to automated decision-making, including profiling, which produces legal or significant effects.'"
            ),
        }

        return suggestions_map.get(right_name, f"Add disclosure for {right_info['description']}")


def validate_subject_rights(text: str) -> Dict:
    """
    Convenience function to validate data subject rights disclosure

    Args:
        text: The text to validate

    Returns:
        Dictionary with validation results
    """
    validator = SubjectRightsValidator()
    return validator.validate_rights_disclosure(text)
