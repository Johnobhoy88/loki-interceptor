"""
GDPR Children's Data Protection Module
Validates children's data processing under UK GDPR Article 8

Age of consent: 13 in UK (DPA 2018 lowered from 16)
Parental consent required for children under 13 for information society services

ICO Guidance: Children and the UK GDPR
"""

import re
from typing import Dict, List


class ChildrenDataProtection:
    """
    Validates children's data protection compliance
    References: UK GDPR Article 8; DPA 2018 s9; ICO Children's Code
    """

    def __init__(self):
        self.legal_source = "UK GDPR Article 8; DPA 2018 s9; Age Appropriate Design Code"
        self.uk_consent_age = 13  # UK lowered from 16 to 13

    def validate_children_protection(self, text: str) -> Dict:
        """
        Validates children's data protection compliance

        Returns:
            Dict with validation results including:
            - processes_children_data: bool
            - is_compliant: bool
            - age_requirements: Dict
            - issues: List[str]
            - warnings: List[str]
            - suggestions: List[str]
        """
        results = {
            'processes_children_data': False,
            'is_compliant': False,
            'age_requirements': {},
            'safeguards_found': [],
            'issues': [],
            'warnings': [],
            'suggestions': [],
            'severity': 'none'
        }

        if not text:
            return results

        text_lower = text.lower()

        # Check if children's data is mentioned
        children_mentioned = self._check_children_mentioned(text_lower)

        if not children_mentioned:
            # Not processing children's data - compliant by default
            return results

        results['processes_children_data'] = True

        # 1. Check for age of consent (should be 13 in UK)
        age_info = self._check_age_requirements(text, text_lower)
        results['age_requirements'] = age_info

        if not age_info['age_mentioned']:
            results['issues'].append(
                "Children's data processing mentioned but no age requirements specified (Article 8 violation)"
            )
            results['severity'] = 'critical'
            results['suggestions'].append(
                "Specify: 'Children under 13 require parental consent to use our service "
                "(in line with UK Data Protection Act 2018).'"
            )
        elif age_info['incorrect_age']:
            results['warnings'].append(
                f"Age {age_info['ages_mentioned']} specified - UK age of consent is 13 (not 16)"
            )
            results['suggestions'].append(
                "Update age requirement to 13 (UK DPA 2018 lowered consent age from 16 to 13)"
            )

        # 2. Check for parental consent mechanism
        parental_consent = self._check_parental_consent(text_lower)
        results['safeguards_found'].extend(parental_consent['mechanisms'])

        if not parental_consent['mentioned']:
            results['issues'].append(
                "No parental consent mechanism for children under 13 (Article 8 requirement)"
            )
            results['severity'] = 'critical'
            results['suggestions'].append(
                "Implement parental consent mechanism: email verification, credit card check, "
                "or other age-appropriate verification method"
            )
        elif not parental_consent['verification_method']:
            results['warnings'].append(
                "Parental consent mentioned but verification method not specified"
            )
            results['suggestions'].append(
                "Describe verification method: 'We verify parental consent through [method].'"
            )

        # 3. Check for age verification
        age_verification = self._check_age_verification(text_lower)

        if not age_verification:
            results['warnings'].append(
                "No age verification mechanism described"
            )
            results['suggestions'].append(
                "Implement age verification: date of birth, age gate, or other appropriate method"
            )
        else:
            results['safeguards_found'].append('age_verification')

        # 4. Check for Age Appropriate Design Code (Children's Code)
        childrens_code = self._check_childrens_code(text_lower)

        if not childrens_code['mentioned']:
            results['warnings'].append(
                "No reference to Age Appropriate Design Code (ICO Children's Code)"
            )
            results['suggestions'].append(
                "Reference ICO Age Appropriate Design Code compliance for services likely "
                "to be accessed by children"
            )
        else:
            results['safeguards_found'].append('childrens_code_compliance')

        # 5. Check for child-friendly language
        if not self._check_child_friendly_language(text_lower):
            results['warnings'].append(
                "Privacy information should be clear and age-appropriate for children"
            )

        # 6. Check for harmful content safeguards
        harmful_content = self._check_harmful_content_safeguards(text_lower)
        if harmful_content['needed'] and not harmful_content['mentioned']:
            results['warnings'].append(
                "Service may expose children to harmful content but no safeguards mentioned"
            )

        # 7. Check for data minimization for children
        if not self._check_children_data_minimization(text_lower):
            results['warnings'].append(
                "No mention of minimizing children's data collection (best practice under Children's Code)"
            )

        # 8. Check for default privacy settings
        if not self._check_default_privacy_settings(text_lower):
            results['warnings'].append(
                "No mention of privacy-by-default for children (Children's Code requirement)"
            )
            results['suggestions'].append(
                "Implement: 'Children's accounts default to high privacy settings.'"
            )

        # 9. Check for profiling/marketing restrictions
        profiling_issues = self._check_children_profiling(text_lower)
        results['warnings'].extend(profiling_issues)

        # Determine compliance
        results['is_compliant'] = (
            results['processes_children_data'] and
            len(results['issues']) == 0 and
            age_info['age_mentioned'] and
            not age_info['incorrect_age'] and
            parental_consent['mentioned']
        )

        return results

    def _check_children_mentioned(self, text_lower: str) -> bool:
        """Check if children's data processing is mentioned"""
        children_keywords = [
            'child', 'children', 'minor', 'juvenile',
            'under 13', 'under 16', 'under 18',
            'parental consent', 'parent or guardian',
            'age of consent', 'age verification'
        ]
        return any(kw in text_lower for kw in children_keywords)

    def _check_age_requirements(self, text: str, text_lower: str) -> Dict:
        """Check for age of consent specification"""
        result = {
            'age_mentioned': False,
            'ages_mentioned': [],
            'incorrect_age': False
        }

        # Look for age specifications
        age_patterns = [
            r'under\s+(\d+)',
            r'below\s+(\d+)',
            r'age\s+(?:of\s+)?(\d+)',
            r'(\d+)\s+(?:years?\s+)?(?:old|of\s+age)',
        ]

        for pattern in age_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                age = int(match.group(1))
                if age <= 18:  # Relevant ages for child protection
                    result['ages_mentioned'].append(age)
                    result['age_mentioned'] = True

        # Check if age 13 is mentioned (correct UK age)
        if 13 in result['ages_mentioned']:
            result['incorrect_age'] = False
        elif 16 in result['ages_mentioned'] and 13 not in result['ages_mentioned']:
            # Using 16 instead of 13
            result['incorrect_age'] = True

        return result

    def _check_parental_consent(self, text_lower: str) -> Dict:
        """Check for parental consent mechanisms"""
        result = {
            'mentioned': False,
            'mechanisms': [],
            'verification_method': False
        }

        # Parental consent patterns
        consent_patterns = [
            r'parental\s+consent',
            r'parent.*(?:or|/).*guardian.*consent',
            r'consent.*(?:from|of).*parent',
            r'guardian.*(?:approval|permission|consent)',
        ]

        result['mentioned'] = any(re.search(p, text_lower) for p in consent_patterns)

        if result['mentioned']:
            result['mechanisms'].append('parental_consent')

            # Check for verification methods
            verification_patterns = [
                r'verif(?:y|ication).*(?:parent|guardian)',
                r'parent.*email.*verification',
                r'credit\s+card.*verification',
                r'government.*(?:id|identification)',
                r'age.*verification.*service',
            ]

            result['verification_method'] = any(re.search(p, text_lower) for p in verification_patterns)

        return result

    def _check_age_verification(self, text_lower: str) -> bool:
        """Check for age verification mechanisms"""
        verification_patterns = [
            r'age\s+verification',
            r'verif(?:y|ication).*age',
            r'age\s+gate',
            r'date\s+of\s+birth',
            r'confirm.*(?:age|over\s+\d+)',
        ]

        return any(re.search(p, text_lower) for p in verification_patterns)

    def _check_childrens_code(self, text_lower: str) -> Dict:
        """Check for Age Appropriate Design Code compliance"""
        result = {
            'mentioned': False,
            'standards_referenced': []
        }

        # Children's Code patterns
        code_patterns = [
            r'age\s+appropriate\s+design\s+code',
            r'children.?s\s+code',
            r'AADC',
            r'ICO.*children',
        ]

        result['mentioned'] = any(re.search(p, text_lower) for p in code_patterns)

        return result

    def _check_child_friendly_language(self, text_lower: str) -> bool:
        """Check for mentions of child-appropriate language"""
        friendly_patterns = [
            r'(?:clear|simple|plain).*language',
            r'age.?appropriate.*(?:language|information)',
            r'easy\s+to\s+understand',
            r'child.?friendly',
        ]

        return any(re.search(p, text_lower) for p in friendly_patterns)

    def _check_harmful_content_safeguards(self, text_lower: str) -> Dict:
        """Check for harmful content safeguards"""
        result = {
            'needed': False,
            'mentioned': False
        }

        # Services that may need harmful content safeguards
        risky_services = [
            'social media', 'social network', 'messaging',
            'chat', 'user.?generated', 'community', 'forum'
        ]

        result['needed'] = any(service in text_lower for service in risky_services)

        if result['needed']:
            safeguard_patterns = [
                r'(?:safe|protect).*(?:from|against).*(?:harm|abuse)',
                r'content\s+moderation',
                r'report.*(?:inappropriate|harmful)',
                r'safety.*(?:feature|tool|setting)',
            ]

            result['mentioned'] = any(re.search(p, text_lower) for p in safeguard_patterns)

        return result

    def _check_children_data_minimization(self, text_lower: str) -> bool:
        """Check for data minimization specifically for children"""
        minimization_patterns = [
            r'minim(?:ize|ise).*(?:data|information).*child',
            r'child.*minim(?:ize|ise).*data',
            r'only.*(?:necessary|essential).*data.*child',
            r'collect.*(?:only|minimum).*child',
        ]

        return any(re.search(p, text_lower) for p in minimization_patterns)

    def _check_default_privacy_settings(self, text_lower: str) -> bool:
        """Check for privacy-by-default for children"""
        default_patterns = [
            r'default.*(?:privacy|high\s+privacy).*(?:setting|configuration)',
            r'privacy.*by.*default',
            r'highest.*privacy.*setting.*default',
            r'child.*account.*default.*(?:private|high\s+privacy)',
        ]

        return any(re.search(p, text_lower) for p in default_patterns)

    def _check_children_profiling(self, text_lower: str) -> List[str]:
        """Check for inappropriate profiling/marketing to children"""
        warnings = []

        # Check for profiling
        if re.search(r'profil(?:e|ing).*child', text_lower):
            if not re.search(r'(?:do\s+not|will\s+not|never).*profil(?:e|ing).*child', text_lower):
                warnings.append(
                    "Profiling of children mentioned - Children's Code requires no profiling "
                    "unless demonstrably in child's best interests"
                )

        # Check for targeted advertising
        if re.search(r'(?:targeted|personali[sz]ed).*(?:ad|advertising|marketing).*child', text_lower):
            warnings.append(
                "Targeted advertising to children - Children's Code prohibits this practice"
            )

        # Check for nudge techniques
        if re.search(r'(?:nudge|encourage|persuade).*child', text_lower):
            warnings.append(
                "Nudge techniques mentioned - Children's Code limits persuasive design for children"
            )

        return warnings


def validate_children_data_protection(text: str) -> Dict:
    """
    Convenience function to validate children's data protection

    Args:
        text: The text to validate

    Returns:
        Dictionary with validation results
    """
    validator = ChildrenDataProtection()
    return validator.validate_children_protection(text)
