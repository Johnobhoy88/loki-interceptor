"""
GDPR Data Retention Policy Checker
Validates data retention policies against UK GDPR Article 5(1)(e)

Storage Limitation Principle:
"Personal data shall be kept in a form which permits identification of data subjects
for no longer than is necessary for the purposes for which the personal data are processed"

ICO Guidance: Data Retention and Deletion
"""

import re
from typing import Dict, List, Tuple, Optional


class RetentionPolicyChecker:
    """
    Validates data retention policies for UK GDPR compliance
    References: UK GDPR Article 5(1)(e); ICO Guidance on Retention and Deletion
    """

    def __init__(self):
        self.legal_source = "UK GDPR Article 5(1)(e); DPA 2018; ICO Retention Guidance"

        # Time period patterns (months, years, days)
        self.time_patterns = [
            r'\d+\s+(?:year|yr)s?',
            r'\d+\s+months?',
            r'\d+\s+days?',
            r'(?:one|two|three|four|five|six|seven|eight|nine|ten)\s+(?:year|month|day)s?',
        ]

    def check_retention_policy(self, text: str) -> Dict:
        """
        Validates data retention policy compliance

        Returns:
            Dict with validation results including:
            - has_policy: bool
            - is_compliant: bool
            - issues: List[str]
            - warnings: List[str]
            - suggestions: List[str]
            - retention_periods_found: List[Dict]
        """
        results = {
            'has_policy': False,
            'is_compliant': False,
            'issues': [],
            'warnings': [],
            'suggestions': [],
            'retention_periods_found': [],
            'severity': 'none'
        }

        if not text:
            results['issues'].append("No text provided for retention policy validation")
            return results

        text_lower = text.lower()

        # Check if retention is mentioned
        retention_mentioned = self._check_retention_mentioned(text_lower)

        if not retention_mentioned:
            # Check if this is a privacy document that should have retention info
            if self._is_privacy_document(text_lower):
                results['issues'].append(
                    "Privacy policy does not describe data retention periods (Article 5(1)(e) violation)"
                )
                results['severity'] = 'high'
                results['suggestions'].append(
                    "Add: 'We retain personal data for [specific period] or until [specific event]. "
                    "Different data types have different retention periods as follows: [list].'"
                )
            return results

        results['has_policy'] = True

        # Extract retention periods
        periods = self._extract_retention_periods(text, text_lower)
        results['retention_periods_found'] = periods

        # 1. Check if retention periods are specific (not vague)
        vague_issues = self._check_vague_retention(text_lower)
        results['issues'].extend(vague_issues)

        # 2. Check if retention is justified
        justification_issues = self._check_retention_justification(text_lower, periods)
        results['issues'].extend(justification_issues)

        # 3. Check for deletion/anonymization procedures
        deletion_issues = self._check_deletion_procedures(text_lower)
        results['issues'].extend(deletion_issues)

        # 4. Check for review procedures
        review_issues = self._check_review_procedures(text_lower)
        results['warnings'].extend(review_issues)

        # 5. Check for different retention periods for different data types
        granularity_issues = self._check_retention_granularity(text_lower, periods)
        results['warnings'].extend(granularity_issues)

        # 6. Check for indefinite retention (red flag)
        indefinite_issues = self._check_indefinite_retention(text_lower)
        results['issues'].extend(indefinite_issues)

        # 7. Check for legal basis for retention
        legal_basis_issues = self._check_legal_basis(text_lower)
        results['warnings'].extend(legal_basis_issues)

        # Determine compliance
        results['is_compliant'] = (
            results['has_policy'] and
            len(results['issues']) == 0 and
            len(periods) > 0
        )

        if results['issues']:
            results['severity'] = 'high' if len(results['issues']) > 2 else 'medium'

        return results

    def _is_privacy_document(self, text_lower: str) -> bool:
        """Check if document appears to be a privacy policy"""
        privacy_indicators = [
            'privacy policy', 'privacy notice', 'data protection',
            'personal data', 'personal information'
        ]
        return any(indicator in text_lower for indicator in privacy_indicators)

    def _check_retention_mentioned(self, text_lower: str) -> bool:
        """Check if retention is mentioned at all"""
        retention_keywords = [
            'retention', 'retain', 'keep', 'store', 'held for',
            'delete', 'deletion', 'erase', 'disposal'
        ]
        return any(keyword in text_lower for keyword in retention_keywords)

    def _extract_retention_periods(self, text: str, text_lower: str) -> List[Dict]:
        """Extract specific retention periods mentioned in the text"""
        periods = []

        # Look for retention statements with time periods
        retention_statements = re.finditer(
            r'(?:retain|keep|store|held).*?(?:for|up to)\s+(\d+\s+(?:year|month|day)s?)',
            text_lower
        )

        for match in retention_statements:
            period = match.group(1)
            context = text[max(0, match.start()-50):min(len(text), match.end()+50)]
            periods.append({
                'period': period,
                'context': context.strip()
            })

        # Also check for event-based retention
        event_patterns = [
            r'until\s+(?:the\s+)?(?:end\s+of\s+)?(?:contract|relationship|employment)',
            r'for\s+the\s+duration\s+of\s+(?:the\s+)?(?:contract|relationship|employment)',
            r'(?:during|throughout)\s+(?:your|the)\s+(?:employment|contract)',
        ]

        for pattern in event_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                context = text[max(0, match.start()-30):min(len(text), match.end()+30)]
                periods.append({
                    'period': 'event-based',
                    'event': match.group(),
                    'context': context.strip()
                })

        return periods

    def _check_vague_retention(self, text_lower: str) -> List[str]:
        """Check for vague retention language"""
        issues = []

        vague_patterns = [
            (r'as\s+long\s+as\s+necessary', "Vague retention: 'as long as necessary' - must specify actual periods"),
            (r'for\s+(?:a\s+)?reasonable\s+(?:period|time)', "Vague retention: 'reasonable period' - must be specific"),
            (r'indefinitely', "Indefinite retention violates storage limitation principle"),
            (r'permanently', "Permanent retention violates storage limitation principle"),
            (r'forever', "Perpetual retention violates storage limitation principle"),
            (r'as\s+long\s+as\s+(?:we|you)\s+(?:need|want|require)', "Vague retention based on organizational needs only"),
        ]

        for pattern, message in vague_patterns:
            if re.search(pattern, text_lower):
                issues.append(message)

        return issues

    def _check_retention_justification(self, text_lower: str, periods: List[Dict]) -> List[str]:
        """Check if retention periods are justified"""
        issues = []

        if periods and len(periods) > 0:
            # Check if justification is provided
            justification_patterns = [
                r'(?:retain|keep).*(?:for|because|to)\s+(?:fulfil|comply|meet|satisfy)',
                r'retention.*(?:based\s+on|justified\s+by|necessary\s+for)',
                r'(?:legal|regulatory|contractual|business)\s+(?:requirement|obligation|reason)',
            ]

            has_justification = any(re.search(p, text_lower) for p in justification_patterns)

            if not has_justification:
                issues.append(
                    "Retention periods specified but no justification provided (must explain why data is kept)"
                )

        return issues

    def _check_deletion_procedures(self, text_lower: str) -> List[str]:
        """Check if deletion/anonymization procedures are described"""
        issues = []

        deletion_patterns = [
            r'(?:delete|erase|destroy|remove).*data',
            r'(?:secure\s+)?(?:deletion|erasure|disposal)',
            r'anonymi[sz]ed?',
            r'pseudonymised',
        ]

        has_deletion = any(re.search(p, text_lower) for p in deletion_patterns)

        if not has_deletion:
            issues.append(
                "No deletion or anonymization procedures described (ICO requires secure deletion process)"
            )

        return issues

    def _check_review_procedures(self, text_lower: str) -> List[str]:
        """Check if retention policy review is mentioned"""
        warnings = []

        review_patterns = [
            r'review.*retention',
            r'retention.*(?:policy|schedule).*review',
            r'regularly.*(?:review|assess).*(?:retention|data)',
            r'periodic.*assessment',
        ]

        has_review = any(re.search(p, text_lower) for p in review_patterns)

        if not has_review:
            warnings.append(
                "No mention of retention policy review (best practice: review retention schedules regularly)"
            )

        return warnings

    def _check_retention_granularity(self, text_lower: str, periods: List[Dict]) -> List[str]:
        """Check if different retention periods for different data types"""
        warnings = []

        data_types = ['account', 'transaction', 'marketing', 'analytics',
                      'financial', 'health', 'employee', 'customer']

        types_mentioned = sum(1 for dt in data_types if dt in text_lower)

        if types_mentioned > 1 and len(periods) <= 1:
            warnings.append(
                f"Multiple data types mentioned ({types_mentioned}) but only one retention period - "
                f"consider specifying different periods for different data types"
            )

        return warnings

    def _check_indefinite_retention(self, text_lower: str) -> List[str]:
        """Check for indefinite/permanent retention"""
        issues = []

        indefinite_patterns = [
            r'(?:keep|retain|store).*(?:indefinitely|permanently|forever)',
            r'never\s+(?:delete|erase|remove)',
            r'no\s+deletion\s+(?:policy|schedule)',
        ]

        for pattern in indefinite_patterns:
            if re.search(pattern, text_lower):
                issues.append(
                    "Indefinite/permanent retention detected - violates storage limitation principle (Article 5(1)(e))"
                )
                break

        return issues

    def _check_legal_basis(self, text_lower: str) -> List[str]:
        """Check if legal basis for retention is mentioned"""
        warnings = []

        legal_basis_patterns = [
            r'(?:legal|statutory|regulatory)\s+(?:requirement|obligation)',
            r'(?:comply|compliance)\s+with.*(?:law|regulation|statute)',
            r'(?:tax|accounting|employment)\s+law',
            r'limitation\s+period',
        ]

        has_legal_basis = any(re.search(p, text_lower) for p in legal_basis_patterns)

        if not has_legal_basis:
            warnings.append(
                "No mention of legal basis for retention periods (e.g., tax laws, limitation periods)"
            )

        return warnings


def check_retention_compliance(text: str) -> Dict:
    """
    Convenience function to check retention policy compliance

    Args:
        text: The text to validate

    Returns:
        Dictionary with validation results
    """
    checker = RetentionPolicyChecker()
    return checker.check_retention_policy(text)
