import re


class ChildrenDataAdvancedGate:
    """
    UK GDPR Article 8 + Data Use and Access Act 2025 - Children's Data Protection
    Covers: Age verification, parental consent, children's rights, best interests, online services
    """
    def __init__(self):
        self.name = "children_data_advanced"
        self.severity = "critical"
        self.legal_source = "UK GDPR Article 8, Data Use and Access Act 2025 (Children's Code), Age Appropriate Design Code"

    def _is_relevant(self, text):
        """Check if document relates to children's data"""
        text_lower = text.lower()
        keywords = [
            'child', 'children', 'kid', 'minor', 'under 13', 'under 16', 'under 18',
            'parental', 'parent', 'guardian', 'young person', 'youth',
            'age verification', 'age appropriate', 'school', 'education'
        ]
        return any(kw in text_lower for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not process children\'s personal data',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()
        spans = []
        issues = []
        warnings = []

        # 1. AGE THRESHOLDS (UK: 13 for online services, Article 8)
        age_patterns = [
            r'under\s+(?:13|16|18)',
            r'(?:13|16|18)\s+(?:years?\s+)?(?:old|of\s+age)',
            r'age\s+(?:of\s+)?(?:13|16|18)',
            r'(?:at\s+least|minimum\s+age|over)\s+(?:13|16|18)'
        ]

        ages_mentioned = []
        for pattern in age_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                age_num = re.search(r'\d+', match)
                if age_num:
                    ages_mentioned.append(int(age_num.group()))

        has_age_threshold = len(ages_mentioned) > 0

        # UK standard is 13 for online services (Article 8)
        if 13 not in ages_mentioned and has_age_threshold:
            warnings.append('UK age threshold is 13 for online services requiring consent (Article 8)')

        # 2. AGE VERIFICATION (2025 strengthened requirements)
        age_verification_patterns = [
            r'age\s+verification',
            r'verify.*age',
            r'age\s+check',
            r'confirm.*(?:age|date\s+of\s+birth)',
            r'prove.*age',
            r'age\s+assurance'
        ]

        has_age_verification = any(re.search(p, text, re.IGNORECASE) for p in age_verification_patterns)

        if has_age_threshold and not has_age_verification:
            issues.append('CRITICAL: Must implement age verification to ensure children under 13 do not provide consent (2025 strengthened)')

        if has_age_verification:
            # Check for appropriate methods (2025 guidance)
            verification_methods = {
                'date_of_birth': r'date\s+of\s+birth',
                'document': r'(?:ID|identification|document)\s+(?:verification|check)',
                'credit_card': r'credit\s+card',
                'biometric': r'biometric',
                'self_declaration': r'self[\s-]declar(?:e|ation)',
                'email': r'email\s+verification'
            }

            methods_mentioned = sum(1 for p in verification_methods.values() if re.search(p, text, re.IGNORECASE))

            # Self-declaration alone is insufficient (2025 requirement)
            if re.search(r'self[\s-]declar(?:e|ation)', text, re.IGNORECASE) and methods_mentioned == 1:
                warnings.append('2025 requirement: self-declaration alone insufficient for age verification - use more robust methods')

        # 3. PARENTAL CONSENT (Required for under 13s)
        parental_consent_patterns = [
            r'parental\s+consent',
            r'parent(?:al)?\s+(?:or\s+)?guardian\s+(?:consent|permission|approval)',
            r'consent.*(?:parent|guardian)',
            r'parent.*(?:agree|authorize|authorise|approve)',
            r'holder\s+of\s+parental\s+responsibility'
        ]

        has_parental_consent = any(re.search(p, text, re.IGNORECASE) for p in parental_consent_patterns)

        if has_age_threshold and any(age < 13 for age in ages_mentioned) and not has_parental_consent:
            issues.append('CRITICAL: Parental consent required for processing data of children under 13')

        if has_parental_consent:
            # Check for verification of parental consent (2025 requirement)
            parent_verification_patterns = [
                r'verif(?:y|ication).*(?:parent|guardian)',
                r'confirm.*parent(?:al)?\s+(?:status|identity)',
                r'reasonable\s+efforts?.*verif',
                r'parent.*(?:email|phone|contact)\s+(?:verification|confirmation)'
            ]

            has_parent_verification = any(re.search(p, text, re.IGNORECASE) for p in parent_verification_patterns)

            if not has_parent_verification:
                warnings.append('2025 requirement: must make reasonable efforts to verify holder of parental responsibility')

        # 4. CHILD'S BEST INTERESTS (Article 8, 2025 emphasis)
        best_interests_patterns = [
            r'best\s+interests?.*child',
            r'child\'?s\s+(?:welfare|wellbeing|well[\s-]being)',
            r'protect.*child(?:ren)?',
            r'child[\s-]friendly',
            r'age[\s-]appropriate'
        ]

        has_best_interests = any(re.search(p, text, re.IGNORECASE) for p in best_interests_patterns)

        if not has_best_interests:
            warnings.append('2025 emphasis: processing children\'s data must consider child\'s best interests')

        # 5. AGE-APPROPRIATE DESIGN (Age Appropriate Design Code 2020, updated 2025)
        aadc_principles = {
            'best_interests': r'best\s+interests?',
            'data_minimisation': r'(?:minimum|minimal|only\s+necessary)\s+data',
            'default_settings': r'(?:default|privacy).*settings?',
            'transparency': r'(?:clear|transparent|understandable)\s+(?:language|information|explanation)',
            'detrimental_use': r'(?:not|no).*(?:detrimental|harmful)\s+use',
            'policies': r'(?:child[\s-]friendly|age[\s-]appropriate|understandable)\s+(?:policy|policies|terms)',
            'parental_controls': r'parental\s+controls?',
            'profiling': r'(?:no|not|off\s+by\s+default).*profiling.*child',
            'nudge': r'(?:no|not).*nudge.*child',
            'connected_toys': r'(?:toys?|devices?|connected).*(?:security|protection)',
            'geolocation': r'geolocation.*(?:off|disabled|not\s+enabled)\s+by\s+default',
            'parental_monitoring': r'parental\s+(?:monitoring|oversight|access)',
            'online_tools': r'(?:report|block|flag)\s+(?:content|concerns?)',
            'data_sharing': r'(?:no|not|minimal)\s+data\s+sharing',
            'standards': r'(?:high|appropriate)\s+standards?.*(?:privacy|data\s+protection)'
        }

        aadc_compliance = sum(1 for p in aadc_principles.values() if re.search(p, text, re.IGNORECASE))

        if aadc_compliance < 5:
            warnings.append('2025 Age Appropriate Design Code: apply 15 standards including best interests, data minimisation, privacy by default, transparency')

        # 6. PROFILING OF CHILDREN (Generally prohibited - 2025)
        child_profiling_patterns = [
            r'(?:profil(?:e|ing)|behavioral\s+advertising|targeted\s+(?:ads?|advertising)).*child',
            r'child(?:ren)?.*(?:profil(?:e|ing)|track|behavioral\s+advertising)',
            r'child(?:ren)?.*(?:personaliz|personalis)(?:e|ation|ed)'
        ]

        has_child_profiling = any(re.search(p, text, re.IGNORECASE) for p in child_profiling_patterns)

        if has_child_profiling:
            # Check if turned off by default
            off_by_default_patterns = [
                r'off\s+by\s+default',
                r'disabled\s+(?:by\s+default|unless)',
                r'opt[\s-]in',
                r'(?:must|need\s+to)\s+(?:enable|activate|turn\s+on)',
                r'not\s+(?:enabled|active|on)\s+(?:by\s+default|automatically)'
            ]

            is_off_by_default = any(re.search(p, text, re.IGNORECASE) for p in off_by_default_patterns)

            if not is_off_by_default:
                issues.append('CRITICAL: Profiling of children must be off by default (2025 requirement)')

        # 7. GEOLOCATION (Must be off by default for children)
        geolocation_patterns = [
            r'geolocation',
            r'location\s+(?:tracking|data|services?)',
            r'GPS',
            r'track.*location',
            r'where\s+(?:you\s+)?are'
        ]

        has_geolocation = any(re.search(p, text, re.IGNORECASE) for p in geolocation_patterns)

        if has_geolocation:
            # Check if off by default
            geo_off_patterns = [
                r'(?:geolocation|location).*(?:off|disabled|not\s+enabled)\s+by\s+default',
                r'(?:must|need\s+to)\s+(?:enable|activate|turn\s+on).*(?:location|geolocation)',
                r'opt[\s-]in.*(?:location|geolocation)'
            ]

            is_geo_off = any(re.search(p, text, re.IGNORECASE) for p in geo_off_patterns)

            if not is_geo_off:
                warnings.append('Geolocation must be off by default for children (unless integral to service)')

        # 8. NUDGE TECHNIQUES (Prohibited for children - 2025)
        nudge_patterns = [
            r'nudge',
            r'(?:dark|deceptive)\s+patterns?',
            r'manipulat(?:e|ive)',
            r'persuasive\s+design',
            r'(?:encourage|prompt|push).*(?:share|disclose|provide)\s+(?:more\s+)?data'
        ]

        has_nudge = any(re.search(p, text, re.IGNORECASE) for p in nudge_patterns)

        if has_nudge:
            warnings.append('2025 prohibition: do not use nudge techniques to encourage children to provide unnecessary personal data')

        # 9. DATA SHARING (Minimise for children)
        child_data_sharing_patterns = [
            r'(?:share|sharing|disclose|disclosing)\s+(?:child(?:ren)?\'?s?\s+)?(?:personal\s+)?data',
            r'third[\s-]part(?:y|ies).*(?:child|under\s+(?:13|16|18))',
            r'child(?:ren)?\'?s?\s+data.*(?:third[\s-]part|partner|other)'
        ]

        has_child_data_sharing = any(re.search(p, text, re.IGNORECASE) for p in child_data_sharing_patterns)

        if has_child_data_sharing:
            # Check if minimised/disclosed
            minimisation_patterns = [
                r'(?:only|solely|minimum|minimal)\s+(?:necessary|when\s+needed)',
                r'(?:no|not|zero)\s+(?:unnecessary\s+)?sharing',
                r'limited\s+(?:to|sharing)',
                r'essential\s+(?:partners|services)\s+only'
            ]

            is_minimised = any(re.search(p, text, re.IGNORECASE) for p in minimisation_patterns)

            if not is_minimised:
                warnings.append('Data sharing with third parties should be minimised for children\'s data')

        # 10. TRANSPARENCY (Child-friendly language)
        transparency_patterns = [
            r'(?:child[\s-]friendly|age[\s-]appropriate|simple|clear|easy\s+to\s+understand)\s+(?:language|explanation|terms|policy)',
            r'explain.*(?:way.*child|children)\s+(?:can\s+)?understand',
            r'written\s+for\s+child(?:ren)?'
        ]

        has_child_friendly = any(re.search(p, text, re.IGNORECASE) for p in transparency_patterns)

        if not has_child_friendly:
            warnings.append('Privacy information for children must be in child-friendly, age-appropriate language')

        # 11. PARENTAL CONTROLS AND TOOLS
        parental_tools_patterns = [
            r'parental\s+controls?',
            r'parent.*(?:monitor|supervise|oversee|manage)',
            r'parent.*(?:dashboard|portal|account)',
            r'parent.*(?:access|view|manage).*child\'?s?\s+(?:account|data|information)'
        ]

        has_parental_tools = any(re.search(p, text, re.IGNORECASE) for p in parental_tools_patterns)

        if has_parental_consent and not has_parental_tools:
            warnings.append('2025 best practice: provide parental controls and tools to monitor/manage child\'s data')

        # 12. ONLINE SAFETY TOOLS (Reporting, blocking)
        safety_tools_patterns = [
            r'(?:report|flag)\s+(?:content|concerns?|inappropriate)',
            r'block\s+(?:users?|content)',
            r'(?:safety|moderation)\s+(?:tools?|features?)',
            r'(?:report|complain)\s+(?:button|option|link)'
        ]

        has_safety_tools = any(re.search(p, text, re.IGNORECASE) for p in safety_tools_patterns)

        if not has_safety_tools:
            warnings.append('Provide online safety tools for children: reporting, blocking, flagging inappropriate content')

        # 13. CONNECTED TOYS AND DEVICES (Special protections)
        connected_toy_patterns = [
            r'(?:connected|smart)\s+toy',
            r'IoT\s+(?:toy|device)',
            r'internet[\s-]connected.*(?:toy|device)',
            r'voice[\s-]activated.*(?:toy|device)'
        ]

        has_connected_toy = any(re.search(p, text, re.IGNORECASE) for p in connected_toy_patterns)

        if has_connected_toy:
            # Check for security measures
            toy_security_patterns = [
                r'securit(?:y|e)',
                r'encryption',
                r'(?:protect|safeguard).*(?:data|information)',
                r'(?:password|authentication)',
                r'default\s+(?:password|credentials).*(?:changed|unique)'
            ]

            has_toy_security = any(re.search(p, text, re.IGNORECASE) for p in toy_security_patterns)

            if not has_toy_security:
                warnings.append('Connected toys must have strong security: encryption, unique passwords, secure by design')

        # 14. SCHOOL CONTEXT (Additional protections)
        school_patterns = [
            r'school',
            r'educational',
            r'pupil',
            r'student',
            r'learning',
            r'classroom'
        ]

        is_school_context = any(re.search(p, text, re.IGNORECASE) for p in school_patterns)

        if is_school_context:
            # Check for appropriate basis (not consent)
            school_basis_patterns = [
                r'(?:public\s+task|legitimate\s+interest|legal\s+obligation)',
                r'(?:not|without)\s+consent',
                r'educational\s+purposes?'
            ]

            has_appropriate_basis = any(re.search(p, text, re.IGNORECASE) for p in school_basis_patterns)

            if not has_appropriate_basis:
                warnings.append('School context: should rely on public task or legitimate interests, not children\'s consent')

        # 15. CHILDREN'S RIGHTS (Access, erasure, portability)
        childrens_rights_patterns = [
            r'child(?:ren)?\'?s?\s+rights?',
            r'child.*(?:access|view|delete|erase)\s+(?:their\s+)?(?:own\s+)?data',
            r'parent.*(?:access|delete|manage).*child\'?s?\s+data'
        ]

        has_childrens_rights = any(re.search(p, text, re.IGNORECASE) for p in childrens_rights_patterns)

        if not has_childrens_rights:
            warnings.append('Clarify how children (or parents) can exercise data subject rights: access, rectification, erasure')

        # Determine overall status
        if issues:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Children\'s data processing violates UK GDPR and 2025 Act requirements',
                'legal_source': self.legal_source,
                'suggestion': 'Urgent compliance required: ' + '; '.join(issues[:2]),
                'spans': spans,
                'details': issues + warnings
            }

        if len(warnings) >= 5:
            return {
                'status': 'WARNING',
                'severity': 'high',
                'message': 'Children\'s data protections need strengthening for 2025 compliance',
                'legal_source': self.legal_source,
                'suggestion': 'Priority improvements: ' + '; '.join(warnings[:3]),
                'spans': spans,
                'details': warnings
            }

        if warnings:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Children\'s data protections could be improved',
                'legal_source': self.legal_source,
                'suggestion': '; '.join(warnings[:2]),
                'spans': spans,
                'details': warnings
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Children\'s data protections appear compliant with 2025 requirements',
            'legal_source': self.legal_source,
            'spans': spans
        }


# Test cases
def test_children_data_advanced_gate():
    gate = ChildrenDataAdvancedGate()

    # Test 1: No age verification
    test1 = """
    CHILDREN'S ONLINE SERVICE

    Our service is available to users aged 10 and above.
    By using this service, you confirm you are over 10 years old.
    """
    result1 = gate.check(test1, "terms_of_service")
    assert result1['status'] == 'FAIL'
    assert 'age verification' in str(result1).lower() or 'parental consent' in str(result1).lower()

    # Test 2: Profiling not off by default
    test2 = """
    CHILDREN'S APP

    We profile children's behavior to personalize content.
    Children can disable profiling in settings.
    """
    result2 = gate.check(test2, "privacy_policy")
    assert result2['status'] == 'FAIL'
    assert 'off by default' in str(result2).lower() or 'profiling' in str(result2).lower()

    # Test 3: Compliant children's service (2025)
    test3 = """
    CHILDREN'S ONLINE PLATFORM

    Age Requirements: Must be 13 or older (under 13s require parental consent)

    Age Verification: We use email verification and date of birth checks to verify age.

    Parental Consent: For under 13s, we verify parental responsibility through email confirmation.

    Best Interests: All processing considers the child's best interests and welfare.

    Privacy by Default:
    - Profiling is OFF by default
    - Geolocation is OFF by default
    - Privacy settings are most restrictive by default
    - We collect only minimum necessary data

    Child-Friendly Information: Our privacy policy is written in clear, age-appropriate language.

    Parental Controls: Parents can access, manage, and delete their child's data.

    Safety Tools: Children can report, block, or flag inappropriate content.

    No Nudge Techniques: We do not manipulate children into sharing more data.

    Data Sharing: Minimal sharing with third parties - essential services only.
    """
    result3 = gate.check(test3, "privacy_policy")
    assert result3['status'] in ['PASS', 'WARNING']

    # Test 4: Connected toy with security
    test4 = """
    SMART TOY PRIVACY

    Our connected toy is designed with children's safety in mind.

    Security Features:
    - All data is encrypted
    - Each device has a unique password (no default passwords)
    - Secure by design principles
    - Regular security updates

    Parental Controls: Parents must set up and manage the device.

    Age-Appropriate: Designed for children 8+ with parental supervision.
    """
    result4 = gate.check(test4, "product_privacy")
    assert result4['status'] in ['PASS', 'WARNING']

    print("All children data advanced gate tests passed!")


if __name__ == "__main__":
    test_children_data_advanced_gate()
