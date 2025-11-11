"""
GDPR Data Breach Notification Checker
Validates data breach notification requirements under UK GDPR Articles 33-34

Notification requirements:
- To ICO: Within 72 hours (Article 33)
- To individuals: Without undue delay if high risk (Article 34)

ICO Guidance: Personal data breaches
"""

import re
from typing import Dict, List


class BreachNotificationChecker:
    """
    Validates data breach notification procedures
    References: UK GDPR Articles 33-34; DPA 2018; ICO Breach Guidance
    """

    def __init__(self):
        self.legal_source = "UK GDPR Articles 33-34; DPA 2018 s67-68; ICO Breach Guidance"

    def check_breach_procedures(self, text: str) -> Dict:
        """
        Validates data breach notification procedures

        Returns:
            Dict with validation results including:
            - has_breach_procedure: bool
            - is_compliant: bool
            - notification_elements: Dict
            - issues: List[str]
            - warnings: List[str]
            - suggestions: List[str]
        """
        results = {
            'has_breach_procedure': False,
            'is_compliant': False,
            'notification_elements': {},
            'issues': [],
            'warnings': [],
            'suggestions': [],
            'severity': 'none'
        }

        if not text:
            return results

        text_lower = text.lower()

        # Check if breach procedures are mentioned
        breach_mentioned = self._check_breach_mentioned(text_lower)

        if not breach_mentioned:
            # Check if this is a privacy policy that should mention breaches
            if self._is_privacy_document(text_lower):
                results['warnings'].append(
                    "Privacy policy does not mention data breach notification procedures"
                )
                results['suggestions'].append(
                    "Add: 'In case of a personal data breach, we will notify the ICO within 72 hours "
                    "and inform affected individuals if the breach poses a high risk.'"
                )
            return results

        results['has_breach_procedure'] = True

        # 1. Check for ICO notification (72 hours)
        ico_notification = self._check_ico_notification(text_lower)
        results['notification_elements']['ico_notification'] = ico_notification

        if not ico_notification['mentioned']:
            results['issues'].append(
                "Breach procedure does not mention ICO notification (Article 33 requirement)"
            )
            results['severity'] = 'high'
            results['suggestions'].append(
                "Add: 'We will notify the ICO within 72 hours of becoming aware of a breach.'"
            )
        elif not ico_notification['timeframe_specified']:
            results['warnings'].append(
                "ICO notification mentioned but 72-hour timeframe not specified"
            )

        # 2. Check for individual notification
        individual_notification = self._check_individual_notification(text_lower)
        results['notification_elements']['individual_notification'] = individual_notification

        if not individual_notification['mentioned']:
            results['issues'].append(
                "Breach procedure does not mention notification to affected individuals (Article 34 requirement)"
            )
            results['severity'] = 'high'
            results['suggestions'].append(
                "Add: 'If a breach poses a high risk to your rights and freedoms, "
                "we will notify you without undue delay.'"
            )
        elif not individual_notification['high_risk_condition']:
            results['warnings'].append(
                "Individual notification mentioned but 'high risk' condition not specified"
            )

        # 3. Check for required breach information (Article 33)
        breach_content = self._check_breach_content_requirements(text_lower)
        results['notification_elements']['content_requirements'] = breach_content

        missing_elements = [elem for elem, present in breach_content.items() if not present]
        if missing_elements:
            results['warnings'].append(
                f"Breach notification content incomplete. Missing: {', '.join(missing_elements)}"
            )
            results['suggestions'].append(
                "Breach notifications should include: nature of breach, likely consequences, "
                "measures taken/proposed, and contact point for more information"
            )

        # 4. Check for breach documentation
        if not self._check_breach_documentation(text_lower):
            results['warnings'].append(
                "No mention of breach documentation/records (Article 33(5) requires breach register)"
            )
            results['suggestions'].append(
                "Add: 'We maintain a register of all personal data breaches as required by Article 33(5).'"
            )

        # 5. Check for DPO involvement (if DPO required)
        if self._check_dpo_mentioned(text_lower):
            if not self._check_dpo_breach_involvement(text_lower):
                results['warnings'].append(
                    "DPO mentioned but not referenced in breach procedures"
                )

        # 6. Check for exceptions (when notification not required)
        if not self._check_notification_exceptions(text_lower):
            results['warnings'].append(
                "No mention of when breach notification may not be required "
                "(e.g., encrypted data, low risk breaches)"
            )

        # Determine compliance
        results['is_compliant'] = (
            results['has_breach_procedure'] and
            len(results['issues']) == 0
        )

        return results

    def _is_privacy_document(self, text_lower: str) -> bool:
        """Check if document appears to be a privacy policy"""
        privacy_indicators = [
            'privacy policy', 'privacy notice', 'data protection',
            'personal data', 'how we use'
        ]
        return any(indicator in text_lower for indicator in privacy_indicators)

    def _check_breach_mentioned(self, text_lower: str) -> bool:
        """Check if data breach is mentioned"""
        breach_keywords = [
            'data breach', 'personal data breach', 'security breach',
            'breach notification', 'security incident'
        ]
        return any(kw in text_lower for kw in breach_keywords)

    def _check_ico_notification(self, text_lower: str) -> Dict:
        """Check for ICO notification requirements"""
        result = {
            'mentioned': False,
            'timeframe_specified': False
        }

        # ICO notification patterns
        ico_patterns = [
            r'notify.*(?:ICO|information\s+commissioner)',
            r'report.*breach.*(?:to\s+)?(?:ICO|supervisory\s+authority)',
            r'inform.*(?:ICO|information\s+commissioner).*breach',
        ]

        result['mentioned'] = any(re.search(p, text_lower) for p in ico_patterns)

        if result['mentioned']:
            # Check for 72-hour timeframe
            timeframe_patterns = [
                r'(?:within|up\s+to)\s+72\s+hours',
                r'(?:within|up\s+to)\s+(?:three|3)\s+days',
                r'72.?hour',
            ]
            result['timeframe_specified'] = any(re.search(p, text_lower) for p in timeframe_patterns)

        return result

    def _check_individual_notification(self, text_lower: str) -> Dict:
        """Check for individual notification requirements"""
        result = {
            'mentioned': False,
            'high_risk_condition': False,
            'timeframe_specified': False
        }

        # Individual notification patterns
        individual_patterns = [
            r'notify.*(?:you|affected\s+individuals|data\s+subjects)',
            r'inform.*(?:you|affected\s+individuals).*breach',
            r'notification.*(?:to\s+)?(?:you|individuals|data\s+subjects)',
        ]

        result['mentioned'] = any(re.search(p, text_lower) for p in individual_patterns)

        if result['mentioned']:
            # Check for high risk condition
            risk_patterns = [
                r'high\s+risk',
                r'likely\s+to\s+result\s+in.*risk',
                r'significant\s+risk',
            ]
            result['high_risk_condition'] = any(re.search(p, text_lower) for p in risk_patterns)

            # Check for timeframe
            timeframe_patterns = [
                r'without\s+undue\s+delay',
                r'promptly',
                r'as\s+soon\s+as\s+(?:possible|practicable)',
            ]
            result['timeframe_specified'] = any(re.search(p, text_lower) for p in timeframe_patterns)

        return result

    def _check_breach_content_requirements(self, text_lower: str) -> Dict:
        """Check if breach notification content requirements are mentioned"""
        content_elements = {
            'nature_of_breach': re.search(r'nature.*breach', text_lower) is not None,
            'data_categories': re.search(r'(?:categor(?:y|ies)|type).*(?:data|information).*affected', text_lower) is not None,
            'affected_individuals': re.search(r'number.*(?:individuals|data\s+subjects).*affected', text_lower) is not None,
            'consequences': re.search(r'(?:consequences|impact|effect).*breach', text_lower) is not None,
            'measures_taken': re.search(r'(?:measures?|actions?|steps).*(?:taken|implemented|mitigate)', text_lower) is not None,
            'contact_point': re.search(r'contact.*(?:point|details|information)', text_lower) is not None,
        }

        return content_elements

    def _check_breach_documentation(self, text_lower: str) -> bool:
        """Check if breach documentation is mentioned"""
        documentation_patterns = [
            r'(?:record|register|log|document).*breach',
            r'breach.*(?:register|record|log)',
            r'maintain.*(?:record|documentation).*breach',
        ]

        return any(re.search(p, text_lower) for p in documentation_patterns)

    def _check_dpo_mentioned(self, text_lower: str) -> bool:
        """Check if DPO is mentioned"""
        return bool(re.search(r'data\s+protection\s+officer|DPO', text_lower))

    def _check_dpo_breach_involvement(self, text_lower: str) -> bool:
        """Check if DPO is involved in breach procedures"""
        patterns = [
            r'DPO.*(?:notif|inform|consult).*breach',
            r'breach.*(?:notif|inform|consult).*DPO',
            r'data\s+protection\s+officer.*breach',
        ]

        return any(re.search(p, text_lower) for p in patterns)

    def _check_notification_exceptions(self, text_lower: str) -> bool:
        """Check if exceptions to notification are mentioned"""
        exception_patterns = [
            r'(?:not\s+required|unnecessary).*notify',
            r'exception.*notification',
            r'(?:encrypted|pseudonymised).*(?:data|breach)',
            r'low\s+risk.*breach',
            r'unlikely.*(?:risk|adverse\s+effect)',
        ]

        return any(re.search(p, text_lower) for p in exception_patterns)


def check_breach_notification(text: str) -> Dict:
    """
    Convenience function to check breach notification procedures

    Args:
        text: The text to validate

    Returns:
        Dictionary with validation results
    """
    checker = BreachNotificationChecker()
    return checker.check_breach_procedures(text)
