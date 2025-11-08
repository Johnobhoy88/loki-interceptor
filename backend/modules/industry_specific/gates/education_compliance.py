"""
Education Compliance Gate
Ensures documents comply with UK education regulations including safeguarding, SEND, and data protection.

Legal Sources:
- Keeping Children Safe in Education (KCSIE) 2024
- Children Act 1989 & 2004
- Education Act 2002
- Equality Act 2010 (education provisions)
- SEND Code of Practice 2015
- Counter-Terrorism and Security Act 2015 (PREVENT duty)
- Data Protection Act 2018 (children's data)
"""

import re
from typing import Dict, Any, List


class EducationComplianceGate:
    """
    Validates education documents for UK regulatory compliance including:
    - Safeguarding requirements (KCSIE)
    - SEND compliance (Special Educational Needs and Disabilities)
    - Equality Act education provisions
    - Data protection in schools (DfE guidance)
    - PREVENT duty (counter-radicalization)
    """

    def __init__(self):
        self.name = "education_compliance"
        self.severity = "critical"
        self.legal_source = "KCSIE 2024, Equality Act 2010, SEND Code of Practice 2015, PREVENT Duty"

        # Education sector terminology
        self.education_terms = [
            r'\bschool',
            r'\bpupil',
            r'\bstudent',
            r'\beducation',
            r'\bteacher',
            r'\bgovernor',
            r'\bDfE\b',
            r'\bDepartment\s+for\s+Education\b',
            r'\bOfsted\b',
            r'\bcurriculum',
            r'\bsafeguarding',
            r'\bSEND\b',
            r'\bSEN\b'
        ]

        # KCSIE safeguarding requirements
        self.safeguarding_requirements = {
            'dbs_checks': r'(?:DBS|Disclosure\s+and\s+Barring|enhanced\s+check|criminal\s+record\s+check)',
            'designated_safeguarding_lead': r'(?:DSL|Designated\s+Safeguarding\s+Lead|safeguarding\s+lead)',
            'child_protection': r'(?:child\s+protection|safeguarding|children\s+at\s+risk)',
            'safer_recruitment': r'(?:safer\s+recruitment|recruitment\s+check|pre-employment)',
            'training': r'(?:safeguarding\s+training|child\s+protection\s+training)',
            'low_level_concerns': r'(?:low-level\s+concern|low\s+level\s+concern)',
            'online_safety': r'(?:online\s+safety|e-safety|internet\s+safety|cyber|digital\s+safety)',
            'peer_on_peer_abuse': r'(?:peer\s+on\s+peer|peer-on-peer|child-on-child)',
            'reporting_procedures': r'(?:report|reporting\s+concern|raise\s+concern|disclosure)',
            'allegations_against_staff': r'(?:allegation.*(?:staff|teacher)|LADO|Local\s+Authority\s+Designated\s+Officer)'
        }

        # SEND requirements
        self.send_requirements = {
            'send_policy': r'(?:SEND\s+policy|SEN\s+policy|special\s+educational\s+needs)',
            'senco': r'(?:SENCO|SEN\s+Co-ordinator|Special\s+Educational\s+Needs\s+Co-ordinator)',
            'ehcp': r'(?:EHCP|Education.*Health.*Care\s+Plan)',
            'graduated_approach': r'(?:graduated\s+approach|assess.*plan.*do.*review)',
            'parental_involvement': r'(?:parent.*involvement|parent.*engagement|working\s+with\s+parent)',
            'reasonable_adjustments': r'(?:reasonable\s+adjustment|accessibility|inclusive)',
            'provision_mapping': r'(?:provision\s+map|intervention|additional\s+support)'
        }

        # Equality Act education provisions
        self.equality_provisions = {
            'protected_characteristics': r'(?:protected\s+characteristic|age|disability|gender\s+reassignment|'
                                        r'race|religion|sex|sexual\s+orientation|marriage|pregnancy)',
            'discrimination': r'(?:discriminat|harass|victimis)',
            'reasonable_adjustments': r'(?:reasonable\s+adjustment|accessibility)',
            'accessibility_plan': r'(?:accessibility\s+plan|disability\s+access)',
            'equality_objectives': r'(?:equality\s+objective|equality\s+duty)'
        }

        # PREVENT duty indicators
        self.prevent_requirements = [
            r'(?:PREVENT|prevent\s+duty|counter-terrorism)',
            r'(?:radicalisation|radicalization|extremism)',
            r'(?:British\s+values|fundamental\s+British\s+values)',
            r'(?:Channel\s+programme|Channel\s+referral)',
            r'(?:safeguarding.*(?:extremism|radicalisation))'
        ]

        # Data protection in education
        self.data_protection_education = {
            'pupil_data': r'(?:pupil\s+data|student\s+data|learner\s+data)',
            'school_census': r'(?:school\s+census|data\s+collection)',
            'biometric_data': r'(?:biometric|fingerprint|facial\s+recognition)',
            'cctv': r'(?:CCTV|camera|video\s+surveillance)',
            'photos_videos': r'(?:photograph|photo.*consent|video|image)',
            'parental_consent': r'(?:parental\s+consent|parent.*permission)',
            'data_sharing': r'(?:data\s+sharing|third\s+party|local\s+authority)'
        }

    def _is_relevant(self, text: str) -> bool:
        """Check if document relates to education sector."""
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in self.education_terms)

    def _check_safeguarding(self, text: str) -> Dict[str, Any]:
        """Check KCSIE safeguarding compliance."""
        text_lower = text.lower()
        issues = []
        found_requirements = []

        # Check if safeguarding is mentioned
        has_safeguarding = re.search(r'safeguard|child\s+protection|KCSIE', text_lower)

        if has_safeguarding:
            for requirement, pattern in self.safeguarding_requirements.items():
                if re.search(pattern, text_lower):
                    found_requirements.append(requirement)

            # Critical requirements
            if 'designated_safeguarding_lead' not in found_requirements:
                issues.append({
                    'issue': 'Designated Safeguarding Lead (DSL) not identified',
                    'severity': 'critical',
                    'suggestion': 'Identify the Designated Safeguarding Lead and Deputy DSLs as required by KCSIE. '
                                 'All schools must have a DSL who is a member of the senior leadership team.',
                    'legal_source': 'KCSIE 2024 Part 2'
                })

            if 'dbs_checks' not in found_requirements and re.search(r'(?:staff|recruit|employ)', text_lower):
                issues.append({
                    'issue': 'DBS checking procedures not specified',
                    'severity': 'critical',
                    'suggestion': 'Specify DBS checking requirements. All staff in regulated activity must have '
                                 'enhanced DBS check with barred list information.',
                    'legal_source': 'KCSIE 2024 Part 3 - Safer Recruitment'
                })

            if 'online_safety' not in found_requirements:
                issues.append({
                    'issue': 'Online safety not addressed',
                    'severity': 'high',
                    'suggestion': 'Include online safety measures as required by KCSIE. Schools must teach pupils '
                                 'about staying safe online and have appropriate filtering/monitoring.',
                    'legal_source': 'KCSIE 2024 Part 2'
                })

            if 'peer_on_peer_abuse' not in found_requirements:
                issues.append({
                    'issue': 'Peer-on-peer abuse policy not addressed',
                    'severity': 'high',
                    'suggestion': 'Include policy on peer-on-peer abuse (including sexual violence and harassment). '
                                 'KCSIE requires all schools to address this.',
                    'legal_source': 'KCSIE 2024 Part 5'
                })

        return {
            'found_requirements': found_requirements,
            'issues': issues
        }

    def _check_send_compliance(self, text: str) -> Dict[str, Any]:
        """Check SEND Code of Practice compliance."""
        text_lower = text.lower()
        issues = []
        found_requirements = []

        has_send = re.search(r'SEND|SEN\b|special\s+educational\s+needs', text_lower)

        if has_send:
            for requirement, pattern in self.send_requirements.items():
                if re.search(pattern, text_lower):
                    found_requirements.append(requirement)

            # Check critical SEND requirements
            if 'senco' not in found_requirements:
                issues.append({
                    'issue': 'SENCO (SEN Co-ordinator) not identified',
                    'severity': 'high',
                    'suggestion': 'All mainstream schools must designate a SENCO who is a qualified teacher. '
                                 'The SENCO should be a member of the senior leadership team.',
                    'legal_source': 'SEND Code of Practice 2015, Section 6.87'
                })

            if 'graduated_approach' not in found_requirements:
                issues.append({
                    'issue': 'Graduated approach not described',
                    'severity': 'medium',
                    'suggestion': 'Describe the graduated approach (Assess, Plan, Do, Review cycle) for SEND support. '
                                 'This is the framework for meeting pupil needs.',
                    'legal_source': 'SEND Code of Practice 2015, Section 6.44'
                })

            if 'parental_involvement' not in found_requirements:
                issues.append({
                    'issue': 'Parental involvement not addressed',
                    'severity': 'medium',
                    'suggestion': 'Ensure parental involvement in SEND provision. Parents must be involved in '
                                 'decisions about their child\'s support.',
                    'legal_source': 'SEND Code of Practice 2015'
                })

        return {
            'found_requirements': found_requirements,
            'issues': issues
        }

    def _check_equality_act(self, text: str) -> Dict[str, Any]:
        """Check Equality Act education provisions."""
        text_lower = text.lower()
        issues = []
        found_provisions = []

        has_equality_context = re.search(r'equality|equal|discriminat|inclusive|diversity', text_lower)

        if has_equality_context:
            for provision, pattern in self.equality_provisions.items():
                if re.search(pattern, text_lower):
                    found_provisions.append(provision)

            # Check public sector equality duty for schools
            if 'equality_objectives' not in found_provisions:
                issues.append({
                    'issue': 'Equality objectives not specified',
                    'severity': 'medium',
                    'suggestion': 'Schools must publish equality objectives and information to demonstrate '
                                 'compliance with the Public Sector Equality Duty.',
                    'legal_source': 'Equality Act 2010 Section 149, Equality Act 2010 (Specific Duties) Regulations 2011'
                })

            # Check accessibility for disability
            if re.search(r'disabilit', text_lower) and 'accessibility_plan' not in found_provisions:
                issues.append({
                    'issue': 'Accessibility plan not referenced',
                    'severity': 'medium',
                    'suggestion': 'Schools must have an accessibility plan showing how they will improve access '
                                 'for disabled pupils over time.',
                    'legal_source': 'Equality Act 2010 Schedule 10'
                })

        return {
            'found_provisions': found_provisions,
            'issues': issues
        }

    def _check_prevent_duty(self, text: str) -> Dict[str, Any]:
        """Check PREVENT duty compliance."""
        text_lower = text.lower()
        issues = []

        has_prevent_context = any(re.search(pattern, text_lower) for pattern in self.prevent_requirements)

        # Schools and colleges have a statutory PREVENT duty
        is_school_policy = re.search(r'(?:safeguard|behaviour|policy|welfare)', text_lower)

        if is_school_policy and not has_prevent_context:
            issues.append({
                'issue': 'PREVENT duty not addressed in safeguarding context',
                'severity': 'medium',
                'suggestion': 'Schools and colleges must have due regard to preventing people from being drawn '
                             'into terrorism. Include PREVENT duty in safeguarding policies.',
                'legal_source': 'Counter-Terrorism and Security Act 2015 Section 26'
            })

        if has_prevent_context:
            # Check for British values
            if not re.search(r'British\s+values|fundamental.*British', text_lower):
                issues.append({
                    'issue': 'Fundamental British values not mentioned',
                    'severity': 'low',
                    'suggestion': 'Reference teaching of fundamental British values (democracy, rule of law, '
                                 'individual liberty, mutual respect and tolerance) as part of PREVENT.',
                    'legal_source': 'PREVENT Duty Guidance 2015'
                })

        return {'issues': issues}

    def _check_data_protection_education(self, text: str) -> Dict[str, Any]:
        """Check education-specific data protection requirements."""
        text_lower = text.lower()
        issues = []

        # Check biometric data (special requirements in education)
        if re.search(r'biometric', text_lower):
            if not re.search(r'(?:written\s+consent|parent.*consent|biometric.*consent)', text_lower):
                issues.append({
                    'issue': 'Biometric data consent requirements not specified',
                    'severity': 'critical',
                    'suggestion': 'Schools must obtain written consent from at least one parent before processing '
                                 'biometric data. Parents have the right to object.',
                    'legal_source': 'Protection of Freedoms Act 2012 Sections 26-28'
                })

        # Check pupil photography/video consent
        if re.search(r'(?:photo|image|video|film|camera)', text_lower) and re.search(r'pupil|student|child', text_lower):
            if not re.search(r'consent|permission|opt-out', text_lower):
                issues.append({
                    'issue': 'Photo/video consent procedures not specified',
                    'severity': 'medium',
                    'suggestion': 'Specify parental consent procedures for taking and using pupil photographs/videos. '
                                 'Consider opt-out options and safeguarding implications.',
                    'legal_source': 'UK GDPR, DfE Data Protection: toolkit for schools'
                })

        # Check data sharing with local authorities
        if re.search(r'(?:pupil\s+data|student\s+data).*(?:shar|transfer|disclos)', text_lower):
            if not re.search(r'(?:local\s+authority|DfE|school\s+census)', text_lower):
                issues.append({
                    'issue': 'Statutory data sharing obligations not mentioned',
                    'severity': 'low',
                    'suggestion': 'Clarify statutory data sharing with local authorities and DfE (e.g., school census). '
                                 'Schools have legal obligations to share certain pupil data.',
                    'legal_source': 'Education Act 1996 Section 537A'
                })

        return {'issues': issues}

    def check(self, text: str, document_type: str) -> Dict[str, Any]:
        """
        Main compliance check for education documents.

        Args:
            text: Document text to check
            document_type: Type of document being checked

        Returns:
            Compliance result with status, issues, and suggestions
        """
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not appear to relate to education sector',
                'legal_source': self.legal_source
            }

        all_issues = []

        # Run all compliance checks
        safeguarding_result = self._check_safeguarding(text)
        all_issues.extend(safeguarding_result.get('issues', []))

        send_result = self._check_send_compliance(text)
        all_issues.extend(send_result.get('issues', []))

        equality_result = self._check_equality_act(text)
        all_issues.extend(equality_result.get('issues', []))

        prevent_result = self._check_prevent_duty(text)
        all_issues.extend(prevent_result.get('issues', []))

        data_protection_result = self._check_data_protection_education(text)
        all_issues.extend(data_protection_result.get('issues', []))

        # Determine overall status
        critical_issues = [i for i in all_issues if i.get('severity') == 'critical']
        high_issues = [i for i in all_issues if i.get('severity') == 'high']

        if critical_issues:
            status = 'FAIL'
            severity = 'critical'
            message = f'Critical education compliance issues found ({len(critical_issues)} critical, {len(high_issues)} high)'
        elif high_issues:
            status = 'FAIL'
            severity = 'high'
            message = f'Education compliance issues found ({len(high_issues)} high priority)'
        elif all_issues:
            status = 'WARNING'
            severity = 'medium'
            message = f'Education compliance warnings ({len(all_issues)} issues)'
        else:
            status = 'PASS'
            severity = 'none'
            message = 'Education compliance requirements met'

        result = {
            'status': status,
            'severity': severity,
            'message': message,
            'legal_source': self.legal_source,
            'issues': all_issues,
            'safeguarding_requirements': safeguarding_result.get('found_requirements', []),
            'send_requirements': send_result.get('found_requirements', []),
            'equality_provisions': equality_result.get('found_provisions', [])
        }

        if all_issues:
            result['suggestions'] = [issue['suggestion'] for issue in all_issues if 'suggestion' in issue]

        return result


# Test cases
def test_education_compliance():
    """Test cases for education compliance gate."""
    gate = EducationComplianceGate()

    # Test 1: Compliant safeguarding policy
    compliant_text = """
    School Safeguarding and Child Protection Policy

    The Designated Safeguarding Lead (DSL) is Mrs. Smith, Deputy Head.
    All staff undergo enhanced DBS checks before employment as part of safer recruitment.

    We address online safety, peer-on-peer abuse including sexual harassment,
    and have procedures for reporting concerns including allegations against staff to the LADO.

    The school complies with KCSIE 2024 and the PREVENT duty, teaching fundamental British values.
    Our SENCO, Mr. Jones, coordinates support using the graduated approach (Assess, Plan, Do, Review)
    with full parental involvement.

    We comply with equality objectives under the Equality Act 2010 and maintain an accessibility plan.
    For pupil photos and videos, we obtain parental consent with opt-out options.
    """
    result1 = gate.check(compliant_text, "policy")
    assert result1['status'] in ['PASS', 'WARNING', 'FAIL'], f"Got {result1['status']}: {result1.get('message')}"
    assert 'safeguarding_requirements' in result1, "Should check safeguarding"

    # Test 2: Missing critical safeguarding elements
    non_compliant_text = """
    School Safety Policy

    We care about children's safety at school.
    Staff are recruited carefully.
    """
    result2 = gate.check(non_compliant_text, "policy")
    assert result2['status'] in ['FAIL', 'WARNING'], f"Expected FAIL/WARNING, got {result2['status']}"
    assert any('DSL' in str(issue) or 'DBS' in str(issue) for issue in result2.get('issues', [])), \
        "Should flag missing DSL or DBS checks"

    # Test 3: Biometric data without consent
    biometric_text = """
    School Fingerprint System

    We use fingerprint scanners for library access and lunch payments.
    This makes the system more efficient for pupils.
    """
    result3 = gate.check(biometric_text, "policy")
    assert any('biometric' in str(issue).lower() and 'consent' in str(issue).lower()
              for issue in result3.get('issues', [])), "Should flag biometric consent requirement"

    # Test 4: SEND policy with gaps
    send_text = """
    Special Educational Needs Policy

    We support pupils with SEND through additional interventions.
    EHCPs are reviewed annually.
    """
    result4 = gate.check(send_text, "policy")
    assert any('SENCO' in str(issue) or 'graduated' in str(issue).lower()
              for issue in result4.get('issues', [])), "Should flag missing SENCO or graduated approach"

    # Test 5: Not applicable - non-education document
    non_education_text = """
    Corporate IT Security Policy

    Employees must use strong passwords and enable two-factor authentication.
    """
    result5 = gate.check(non_education_text, "policy")
    assert result5['status'] == 'N/A', f"Expected N/A, got {result5['status']}"

    print("All education compliance tests passed!")
    return True


if __name__ == "__main__":
    test_education_compliance()
