"""
GDPR Legitimate Interest Assessment (LIA) Module
Validates legitimate interest as lawful basis under UK GDPR Article 6(1)(f)

Legitimate Interest requires three-part test:
1. Purpose test: Is there a legitimate interest?
2. Necessity test: Is processing necessary for that interest?
3. Balancing test: Do individual's interests override the legitimate interest?

ICO Guidance: Legitimate interests
"""

import re
from typing import Dict, List


class LegitimateInterestAssessor:
    """
    Assesses legitimate interest claims for GDPR compliance
    References: UK GDPR Article 6(1)(f); ICO Legitimate Interests Guidance
    """

    def __init__(self):
        self.legal_source = "UK GDPR Article 6(1)(f); ICO Legitimate Interests Guidance"

        # Valid legitimate interests (examples from ICO)
        self.valid_interests = [
            'fraud prevention', 'security', 'network security',
            'direct marketing', 'customer service', 'business efficiency',
            'intra-group transfers', 'it security', 'safety'
        ]

    def assess_legitimate_interest(self, text: str) -> Dict:
        """
        Assesses legitimate interest as lawful basis

        Returns:
            Dict with validation results including:
            - claims_legitimate_interest: bool
            - is_valid: bool
            - lia_conducted: bool
            - test_results: Dict (purpose, necessity, balancing)
            - issues: List[str]
            - warnings: List[str]
            - suggestions: List[str]
        """
        results = {
            'claims_legitimate_interest': False,
            'is_valid': False,
            'lia_conducted': False,
            'test_results': {
                'purpose_test': {'passed': False, 'details': []},
                'necessity_test': {'passed': False, 'details': []},
                'balancing_test': {'passed': False, 'details': []}
            },
            'interests_claimed': [],
            'issues': [],
            'warnings': [],
            'suggestions': [],
            'severity': 'none'
        }

        if not text:
            return results

        text_lower = text.lower()

        # Check if legitimate interest is claimed
        li_claimed = self._check_legitimate_interest_claimed(text_lower)

        if not li_claimed:
            # Not using legitimate interest - N/A
            return results

        results['claims_legitimate_interest'] = True

        # 1. Check if LIA is documented
        lia_documented = self._check_lia_documented(text_lower)
        results['lia_conducted'] = lia_documented

        if not lia_documented:
            results['issues'].append(
                "Legitimate interest claimed but no Legitimate Interest Assessment (LIA) documented"
            )
            results['severity'] = 'high'
            results['suggestions'].append(
                "Conduct and document LIA covering: (1) Purpose test - what is the legitimate interest?, "
                "(2) Necessity test - is processing necessary?, (3) Balancing test - do individuals' "
                "interests override?"
            )

        # 2. Identify claimed interests
        interests = self._identify_claimed_interests(text_lower)
        results['interests_claimed'] = interests

        # 3. Assess Purpose Test
        purpose_test = self._assess_purpose_test(text_lower, interests)
        results['test_results']['purpose_test'] = purpose_test

        if not purpose_test['passed']:
            results['issues'].extend(purpose_test['issues'])
            results['suggestions'].extend(purpose_test['suggestions'])

        # 4. Assess Necessity Test
        necessity_test = self._assess_necessity_test(text_lower)
        results['test_results']['necessity_test'] = necessity_test

        if not necessity_test['passed']:
            results['warnings'].extend(necessity_test['warnings'])
            results['suggestions'].extend(necessity_test['suggestions'])

        # 5. Assess Balancing Test
        balancing_test = self._assess_balancing_test(text_lower)
        results['test_results']['balancing_test'] = balancing_test

        if not balancing_test['passed']:
            results['warnings'].extend(balancing_test['warnings'])
            results['suggestions'].extend(balancing_test['suggestions'])

        # 6. Check for right to object
        if not self._check_right_to_object(text_lower):
            results['issues'].append(
                "Legitimate interest used but no mention of right to object (Article 21 requirement)"
            )
            results['severity'] = 'high'
            results['suggestions'].append(
                "Add: 'You have the right to object to processing based on legitimate interests. "
                "Contact us to exercise this right.'"
            )

        # 7. Check for special category data (generally can't use LI)
        special_category_issue = self._check_special_category_data(text_lower)
        if special_category_issue:
            results['issues'].append(special_category_issue)
            results['severity'] = 'critical'

        # 8. Check for children's data (extra caution needed)
        if self._check_children_data(text_lower):
            results['warnings'].append(
                "Legitimate interest used for children's data - requires extra caution "
                "and strong justification (children's interests have more weight)"
            )

        # Determine validity
        results['is_valid'] = (
            results['claims_legitimate_interest'] and
            len(results['issues']) == 0 and
            purpose_test['passed'] and
            results['lia_conducted']
        )

        return results

    def _check_legitimate_interest_claimed(self, text_lower: str) -> bool:
        """Check if legitimate interest is claimed as lawful basis"""
        li_patterns = [
            r'legitimate\s+interest',
            r'lawful\s+basis.*legitimate',
            r'Article\s+6.*\(f\)',
            r'legal\s+basis.*legitimate',
        ]

        return any(re.search(p, text_lower) for p in li_patterns)

    def _check_lia_documented(self, text_lower: str) -> bool:
        """Check if LIA is documented"""
        lia_patterns = [
            r'legitimate\s+interest\s+assessment',
            r'\bLIA\b',
            r'balanc(?:e|ing).*(?:test|assessment)',
            r'assess.*legitimate\s+interest',
            r'three.?part\s+test',
        ]

        return any(re.search(p, text_lower) for p in lia_patterns)

    def _identify_claimed_interests(self, text_lower: str) -> List[str]:
        """Identify specific legitimate interests claimed"""
        interests_found = []

        # Check for common legitimate interests
        interest_patterns = {
            'fraud_prevention': r'fraud\s+(?:prevention|detection)',
            'security': r'(?:security|protect).*(?:system|network|data)',
            'direct_marketing': r'direct\s+marketing',
            'customer_service': r'customer\s+(?:service|support)',
            'analytics': r'analytics|improve.*service',
            'research': r'research|study|analysis',
            'legal_claims': r'legal\s+(?:claim|proceeding|right)',
        }

        for interest_name, pattern in interest_patterns.items():
            if re.search(pattern, text_lower):
                interests_found.append(interest_name)

        return interests_found

    def _assess_purpose_test(self, text_lower: str, interests: List[str]) -> Dict:
        """Assess Purpose Test - Is there a legitimate interest?"""
        result = {
            'passed': False,
            'issues': [],
            'suggestions': [],
            'details': []
        }

        # Check if interest is clearly stated
        if not interests:
            result['issues'].append(
                "Legitimate interest claimed but specific interest not clearly stated"
            )
            result['suggestions'].append(
                "Clearly state the legitimate interest(s): e.g., fraud prevention, "
                "network security, direct marketing, customer service"
            )
            return result

        # Check if interest is valid
        invalid_interests = []
        for interest in interests:
            # Some interests need special consideration
            if interest == 'direct_marketing':
                if not re.search(r'(?:market|advertis|promot).*(?:own|our)\s+(?:product|service)', text_lower):
                    result['details'].append(
                        "Direct marketing as LI only valid for own products/services, not third parties"
                    )

        result['passed'] = True
        result['details'].append(f"Legitimate interests identified: {', '.join(interests)}")

        return result

    def _assess_necessity_test(self, text_lower: str) -> Dict:
        """Assess Necessity Test - Is processing necessary?"""
        result = {
            'passed': False,
            'warnings': [],
            'suggestions': [],
            'details': []
        }

        # Check if necessity is discussed
        necessity_patterns = [
            r'necessary\s+(?:for|to)',
            r'(?:required|needed)\s+(?:for|to)',
            r'essential\s+(?:for|to)',
            r'proportionate',
        ]

        necessity_mentioned = any(re.search(p, text_lower) for p in necessity_patterns)

        if not necessity_mentioned:
            result['warnings'].append(
                "Necessity not demonstrated - must show processing is necessary for the legitimate interest"
            )
            result['suggestions'].append(
                "Explain: 'This processing is necessary because [specific reason] "
                "and we cannot achieve this in a less intrusive way.'"
            )
            return result

        # Check if alternatives considered
        if not re.search(r'(?:alternative|less\s+intrusive|other\s+means)', text_lower):
            result['warnings'].append(
                "No mention of considering less intrusive alternatives (required for necessity test)"
            )
            result['suggestions'].append(
                "Document consideration of alternatives: 'We considered [alternatives] "
                "but processing is necessary because [reason].'"
            )

        result['passed'] = True
        result['details'].append("Necessity appears to be addressed")

        return result

    def _assess_balancing_test(self, text_lower: str) -> Dict:
        """Assess Balancing Test - Do individuals' interests override?"""
        result = {
            'passed': False,
            'warnings': [],
            'suggestions': [],
            'details': []
        }

        # Check if balancing is discussed
        balancing_patterns = [
            r'balanc(?:e|ing)',
            r'weigh(?:ed|ing).*(?:interest|right)',
            r'(?:individual|data\s+subject).*(?:interest|right|expectation)',
            r'impact.*(?:on|to)\s+(?:individual|you|data\s+subject)',
        ]

        balancing_mentioned = any(re.search(p, text_lower) for p in balancing_patterns)

        if not balancing_mentioned:
            result['warnings'].append(
                "Balancing test not documented - must consider impact on individuals' rights and freedoms"
            )
            result['suggestions'].append(
                "Document balancing: 'We assessed the impact on individuals and determined "
                "our legitimate interest does not override their rights because [reasons]. "
                "Individuals can object to this processing.'"
            )
            return result

        # Check if individual expectations considered
        if not re.search(r'(?:expect|anticipate|reasonable|surprise)', text_lower):
            result['warnings'].append(
                "Individual expectations not considered (key factor in balancing test)"
            )

        # Check if impact assessed
        if not re.search(r'impact.*(?:on|to|assessment)', text_lower):
            result['warnings'].append(
                "Impact on individuals not assessed (required for balancing test)"
            )

        result['passed'] = True
        result['details'].append("Balancing test appears to be addressed")

        return result

    def _check_right_to_object(self, text_lower: str) -> bool:
        """Check if right to object is mentioned (required for LI)"""
        object_patterns = [
            r'right\s+to\s+object',
            r'object\s+to.*processing',
            r'opt.?out',
            r'stop.*processing',
        ]

        return any(re.search(p, text_lower) for p in object_patterns)

    def _check_special_category_data(self, text_lower: str) -> str:
        """Check if special category data is being processed under LI (usually invalid)"""
        special_patterns = [
            r'health\s+(?:data|information)',
            r'medical\s+(?:data|record)',
            r'biometric',
            r'genetic',
            r'racial',
            r'ethnic',
            r'religious',
            r'sexual\s+orientation',
        ]

        if any(re.search(p, text_lower) for p in special_patterns):
            return (
                "Legitimate interest cannot be used for special category data (Article 9) - "
                "requires explicit consent or other Article 9 condition"
            )

        return ""

    def _check_children_data(self, text_lower: str) -> bool:
        """Check if children's data is being processed"""
        children_keywords = ['child', 'children', 'minor', 'under 13', 'under 16']
        return any(kw in text_lower for kw in children_keywords)


def assess_legitimate_interest(text: str) -> Dict:
    """
    Convenience function to assess legitimate interest

    Args:
        text: The text to validate

    Returns:
        Dictionary with validation results
    """
    assessor = LegitimateInterestAssessor()
    return assessor.assess_legitimate_interest(text)
