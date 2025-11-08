"""
Technology Compliance Gate
Ensures documents comply with software licensing, cloud computing, and technology contract requirements.

Legal Sources:
- Copyright, Designs and Patents Act 1988
- Computer Misuse Act 1990
- Various open source licenses (GPL, MIT, Apache, etc.)
- Software licensing case law
- Cloud computing contract best practices
"""

import re
from typing import Dict, Any, List


class TechnologyComplianceGate:
    """
    Validates technology documents for compliance including:
    - Software licensing compliance
    - Open source license detection and requirements (GPL, MIT, Apache)
    - SaaS agreement requirements
    - Cloud computing contracts (UK data residency)
    - Acceptable Use Policies
    """

    def __init__(self):
        self.name = "technology_compliance"
        self.severity = "high"
        self.legal_source = "Copyright Act 1988, Computer Misuse Act 1990, Open Source Licenses"

        # Technology terminology
        self.technology_terms = [
            r'\bsoftware\b',
            r'\bSaaS\b',
            r'\bcloud\b',
            r'\bAPI\b',
            r'\blicense\s*agreement\b',
            r'\bopen\s+source\b',
            r'\bsource\s+code\b',
            r'\bintellectual\s+property\b',
            r'\bcopyright',
            r'\bdata\s+processing',
            r'\bacceptable\s+use\b',
            r'\bservice\s+level\b'
        ]

        # Open source licenses and their requirements
        self.open_source_licenses = {
            'gpl_v2': {
                'pattern': r'(?:GPL|GNU\s+General\s+Public\s+License).*(?:v2|version\s+2)',
                'type': 'copyleft',
                'requirements': ['source_code_disclosure', 'license_preservation', 'derivative_must_be_gpl']
            },
            'gpl_v3': {
                'pattern': r'(?:GPL|GNU\s+General\s+Public\s+License).*(?:v3|version\s+3)',
                'type': 'copyleft',
                'requirements': ['source_code_disclosure', 'license_preservation', 'patent_grant', 'anti_tivoization']
            },
            'lgpl': {
                'pattern': r'LGPL|GNU\s+Lesser\s+General\s+Public\s+License',
                'type': 'weak_copyleft',
                'requirements': ['source_code_disclosure_if_modified', 'license_preservation']
            },
            'mit': {
                'pattern': r'MIT\s+License|MIT\s+Licence',
                'type': 'permissive',
                'requirements': ['license_preservation', 'copyright_notice']
            },
            'apache_2': {
                'pattern': r'Apache\s+License.*(?:v2|version\s+2|2\.0)',
                'type': 'permissive',
                'requirements': ['license_preservation', 'copyright_notice', 'patent_grant', 'notice_file']
            },
            'bsd': {
                'pattern': r'BSD\s+License|BSD[- ](?:2|3)[- ]Clause',
                'type': 'permissive',
                'requirements': ['license_preservation', 'copyright_notice', 'no_endorsement']
            },
            'mozilla': {
                'pattern': r'Mozilla\s+Public\s+License|MPL',
                'type': 'weak_copyleft',
                'requirements': ['source_code_disclosure_per_file', 'license_preservation']
            },
            'agpl': {
                'pattern': r'AGPL|GNU\s+Affero\s+General\s+Public\s+License',
                'type': 'network_copyleft',
                'requirements': ['source_code_disclosure', 'network_use_triggers_distribution', 'license_preservation']
            }
        }

        # Software licensing terms
        self.software_licensing = {
            'license_grant': r'(?:license\s+grant|hereby\s+grants?|grants?\s+(?:you|licensee))',
            'intellectual_property': r'(?:intellectual\s+property|IP\s+rights|proprietary)',
            'license_scope': r'(?:perpetual|term|subscription|concurrent|named\s+user|site\s+license)',
            'restrictions': r'(?:may\s+not|shall\s+not|prohibited|restricted|limitation)',
            'modifications': r'(?:modif|derivative|adapt|alter|enhance)',
            'reverse_engineering': r'(?:reverse\s+engineer|decompile|disassemble)',
            'transfer': r'(?:transfer|assign|sublicense)',
            'updates_support': r'(?:update|upgrade|maintenance|support|patch)',
            'warranty': r'(?:warrant|as\s+is|without\s+warranty)',
            'indemnity': r'(?:indemni|defend|hold\s+harmless)',
            'liability': r'(?:liabilit|consequential\s+damage|limitation\s+of\s+liability)',
            'termination': r'(?:terminat|expire|cancel)'
        }

        # SaaS agreement essentials
        self.saas_requirements = {
            'service_description': r'(?:service\s+description|scope\s+of\s+service|features)',
            'sla': r'(?:SLA|service\s+level\s+agreement|uptime|availability|99\.)',
            'data_location': r'(?:data\s+(?:location|residency)|stored\s+in|servers?\s+located)',
            'data_ownership': r'(?:data\s+ownership|customer\s+data|your\s+data)',
            'data_security': r'(?:data\s+security|encryption|security\s+measure|ISO\s+27001|SOC\s+2)',
            'data_portability': r'(?:data\s+portability|export|data\s+extract)',
            'backup': r'(?:backup|disaster\s+recovery|business\s+continuity)',
            'api_access': r'(?:API|application\s+programming\s+interface|integration)',
            'subscription_fees': r'(?:subscription|fee|pricing|payment\s+term)',
            'usage_limits': r'(?:usage\s+limit|quota|rate\s+limit|fair\s+use)',
            'acceptable_use': r'(?:acceptable\s+use|prohibited\s+use|restrictions\s+on\s+use)'
        }

        # Cloud computing contract terms
        self.cloud_computing = {
            'shared_responsibility': r'(?:shared\s+responsibility|customer\s+responsible|provider\s+responsible)',
            'data_processing': r'(?:data\s+processing\s+agreement|DPA|processor|controller)',
            'subprocessors': r'(?:sub-?processor|third\s+party\s+service)',
            'data_transfer': r'(?:international\s+transfer|cross-border|data\s+transfer|adequacy)',
            'security_certifications': r'(?:ISO\s+27001|SOC\s+2|Cyber\s+Essentials|certification)',
            'incident_response': r'(?:incident\s+response|security\s+incident|breach\s+notification)',
            'audit_rights': r'(?:audit\s+right|inspect|right\s+to\s+audit)',
            'data_deletion': r'(?:data\s+deletion|data\s+destruction|right\s+to\s+delete)',
            'service_suspension': r'(?:suspend|service\s+interruption|downtime)',
            'change_management': r'(?:change\s+management|notice\s+of\s+change|30\s+day|notification)'
        }

        # Acceptable Use Policy essentials
        self.aup_requirements = {
            'prohibited_activities': r'(?:prohibit|forbidden|not\s+permitted|illegal)',
            'security_obligations': r'(?:security|password|unauthorised\s+access|protect)',
            'lawful_use': r'(?:lawful|legal|comply\s+with\s+law|applicable\s+law)',
            'no_harmful_content': r'(?:harmful|offensive|malicious|virus|malware)',
            'intellectual_property_respect': r'(?:respect.*intellectual\s+property|infringe|copyright)',
            'no_interference': r'(?:interfere|disrupt|overload|denial\s+of\s+service)',
            'monitoring': r'(?:monitor|log|review|audit\s+usage)',
            'reporting_violations': r'(?:report|notify|violation)',
            'consequences': r'(?:consequenc|terminat|suspend|breach)',
            'data_protection_compliance': r'(?:GDPR|data\s+protection|privacy|personal\s+data)'
        }

    def _is_relevant(self, text: str) -> bool:
        """Check if document relates to technology/software."""
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in self.technology_terms)

    def _check_open_source_licenses(self, text: str) -> Dict[str, Any]:
        """Detect and check open source license compliance."""
        text_lower = text.lower()
        issues = []
        detected_licenses = []

        for license_name, license_info in self.open_source_licenses.items():
            if re.search(license_info['pattern'], text, re.IGNORECASE):
                detected_licenses.append({
                    'name': license_name,
                    'type': license_info['type'],
                    'requirements': license_info['requirements']
                })

                # Check for copyleft compliance
                if license_info['type'] in ['copyleft', 'network_copyleft']:
                    if not re.search(r'(?:source\s+code|provide.*source|make.*available)', text_lower):
                        issues.append({
                            'issue': f'{license_name.upper()} copyleft license detected - source code disclosure required',
                            'severity': 'critical',
                            'suggestion': f'{license_name.upper()} is a copyleft license requiring you to disclose '
                                         f'source code of derivative works. Ensure you can comply with this requirement '
                                         f'or use a different library.',
                            'legal_source': f'{license_name.upper()} license terms'
                        })

                # Check for patent grant compliance (Apache, GPL v3)
                if 'patent_grant' in license_info['requirements']:
                    if not re.search(r'patent', text_lower):
                        issues.append({
                            'issue': f'{license_name} includes patent grant provisions',
                            'severity': 'medium',
                            'suggestion': f'{license_name} includes patent grants. Review patent implications if '
                                         f'you hold patents related to this software.',
                            'legal_source': f'{license_name} license terms'
                        })

                # Check for license preservation
                if 'license_preservation' in license_info['requirements']:
                    if not re.search(r'(?:copyright\s+notice|license\s+notice|retain.*notice)', text_lower):
                        issues.append({
                            'issue': f'{license_name} license notice not mentioned',
                            'severity': 'high',
                            'suggestion': f'Must preserve copyright notices and license text when using {license_name} '
                                         f'licensed software. Include original license in your distribution.',
                            'legal_source': f'{license_name} license terms'
                        })

        # Check for potential GPL contamination
        gpl_licenses = [l for l in detected_licenses if 'gpl' in l['name'] or l['type'] == 'copyleft']
        if gpl_licenses:
            if re.search(r'proprietar|commercial|closed\s+source', text_lower):
                issues.append({
                    'issue': 'GPL licensed code detected in potentially proprietary software',
                    'severity': 'critical',
                    'suggestion': 'GPL licenses require derivative works to also be GPL licensed. You cannot combine '
                                 'GPL code with proprietary software without releasing your code under GPL. '
                                 'Consider using LGPL or permissive licenses instead.',
                    'legal_source': 'GPL license Section 2'
                })

        return {
            'detected_licenses': detected_licenses,
            'issues': issues
        }

    def _check_software_licensing(self, text: str) -> Dict[str, Any]:
        """Check software license agreement completeness."""
        text_lower = text.lower()
        issues = []
        found_terms = []

        is_license_agreement = re.search(r'license\s+agreement|software\s+license|end\s+user\s+license|EULA',
                                         text, re.IGNORECASE)

        if is_license_agreement:
            for term, pattern in self.software_licensing.items():
                if re.search(pattern, text_lower):
                    found_terms.append(term)

            # Critical terms
            if 'license_grant' not in found_terms:
                issues.append({
                    'issue': 'License grant not clearly stated',
                    'severity': 'critical',
                    'suggestion': 'Clearly state what rights are granted to the licensee. Specify scope: '
                                 'non-exclusive, non-transferable, limited right to use the software.',
                    'legal_source': 'Copyright, Designs and Patents Act 1988'
                })

            if 'restrictions' not in found_terms:
                issues.append({
                    'issue': 'Usage restrictions not specified',
                    'severity': 'high',
                    'suggestion': 'Specify restrictions on use such as: no reverse engineering, no modification, '
                                 'no sublicensing, no transfer to third parties.',
                    'legal_source': 'Standard software licensing practice'
                })

            if 'intellectual_property' not in found_terms:
                issues.append({
                    'issue': 'Intellectual property ownership not stated',
                    'severity': 'high',
                    'suggestion': 'Clarify that licensor retains all intellectual property rights and licensee '
                                 'only receives a limited license to use.',
                    'legal_source': 'Copyright, Designs and Patents Act 1988'
                })

            if 'liability' not in found_terms:
                issues.append({
                    'issue': 'Limitation of liability not included',
                    'severity': 'high',
                    'suggestion': 'Include limitation of liability clause to cap financial exposure. Note: cannot '
                                 'exclude liability for death/personal injury under UK law.',
                    'legal_source': 'Unfair Contract Terms Act 1977'
                })

            if 'termination' not in found_terms:
                issues.append({
                    'issue': 'Termination provisions not specified',
                    'severity': 'medium',
                    'suggestion': 'Specify termination conditions including grounds for termination, notice period, '
                                 'and post-termination obligations.',
                    'legal_source': 'Contract law best practice'
                })

        return {
            'found_terms': found_terms,
            'issues': issues
        }

    def _check_saas_agreement(self, text: str) -> Dict[str, Any]:
        """Check SaaS agreement completeness."""
        text_lower = text.lower()
        issues = []
        found_requirements = []

        is_saas = re.search(r'SaaS|software\s+as\s+a\s+service|cloud\s+service|hosted\s+service', text, re.IGNORECASE)

        if is_saas:
            for requirement, pattern in self.saas_requirements.items():
                if re.search(pattern, text_lower):
                    found_requirements.append(requirement)

            # Critical SaaS terms
            if 'sla' not in found_requirements:
                issues.append({
                    'issue': 'Service Level Agreement (SLA) not specified',
                    'severity': 'high',
                    'suggestion': 'Include SLA specifying uptime guarantees (e.g., 99.9%), response times, and '
                                 'remedies for non-compliance (e.g., service credits).',
                    'legal_source': 'SaaS contract best practice'
                })

            if 'data_location' not in found_requirements:
                issues.append({
                    'issue': 'Data location/residency not specified',
                    'severity': 'high',
                    'suggestion': 'Specify where customer data is stored (UK, EEA, etc.) to ensure GDPR compliance '
                                 'and address data sovereignty concerns.',
                    'legal_source': 'UK GDPR requirements for international transfers'
                })

            if 'data_ownership' not in found_requirements:
                issues.append({
                    'issue': 'Data ownership not clarified',
                    'severity': 'critical',
                    'suggestion': 'Clarify that customer retains ownership of their data and provider only processes '
                                 'data as per instructions. This is crucial for GDPR compliance.',
                    'legal_source': 'UK GDPR Article 28'
                })

            if 'data_security' not in found_requirements:
                issues.append({
                    'issue': 'Data security measures not described',
                    'severity': 'high',
                    'suggestion': 'Describe security measures including encryption (in transit and at rest), '
                                 'access controls, and security certifications (ISO 27001, SOC 2).',
                    'legal_source': 'UK GDPR Article 32'
                })

            if 'acceptable_use' not in found_requirements:
                issues.append({
                    'issue': 'Acceptable Use Policy not referenced',
                    'severity': 'medium',
                    'suggestion': 'Include or reference an Acceptable Use Policy defining prohibited activities.',
                    'legal_source': 'SaaS contract best practice'
                })

            if 'data_portability' not in found_requirements:
                issues.append({
                    'issue': 'Data portability/export not addressed',
                    'severity': 'medium',
                    'suggestion': 'Specify customer ability to export data in standard format to avoid vendor lock-in.',
                    'legal_source': 'UK GDPR Article 20 (right to data portability)'
                })

        return {
            'found_requirements': found_requirements,
            'issues': issues
        }

    def _check_cloud_computing(self, text: str) -> Dict[str, Any]:
        """Check cloud computing contract terms."""
        text_lower = text.lower()
        issues = []
        found_terms = []

        is_cloud = re.search(r'cloud|hosted|infrastructure\s+as\s+a\s+service|IaaS|PaaS', text, re.IGNORECASE)

        if is_cloud:
            for term, pattern in self.cloud_computing.items():
                if re.search(pattern, text_lower):
                    found_terms.append(term)

            if 'data_processing' not in found_terms:
                issues.append({
                    'issue': 'Data Processing Agreement (DPA) not referenced',
                    'severity': 'critical',
                    'suggestion': 'Include Data Processing Agreement specifying processor obligations under GDPR. '
                                 'Cloud provider acts as data processor for customer data.',
                    'legal_source': 'UK GDPR Article 28'
                })

            if 'shared_responsibility' not in found_terms:
                issues.append({
                    'issue': 'Shared responsibility model not defined',
                    'severity': 'high',
                    'suggestion': 'Define shared responsibility model clarifying what security aspects the provider '
                                 'handles vs. customer responsibilities (e.g., provider secures infrastructure, '
                                 'customer secures applications).',
                    'legal_source': 'Cloud security best practice'
                })

            if 'data_location' not in found_terms:
                issues.append({
                    'issue': 'Data residency not specified',
                    'severity': 'high',
                    'suggestion': 'Specify data center locations and whether data stays within UK/EEA for compliance.',
                    'legal_source': 'UK GDPR Chapter V'
                })

            if 'incident_response' not in found_terms:
                issues.append({
                    'issue': 'Security incident response not addressed',
                    'severity': 'medium',
                    'suggestion': 'Specify incident notification procedures and timelines, especially for data breaches '
                                 '(GDPR requires notification within 72 hours).',
                    'legal_source': 'UK GDPR Article 33'
                })

        return {
            'found_terms': found_terms,
            'issues': issues
        }

    def _check_acceptable_use_policy(self, text: str) -> Dict[str, Any]:
        """Check Acceptable Use Policy completeness."""
        text_lower = text.lower()
        issues = []
        found_requirements = []

        is_aup = re.search(r'acceptable\s+use|usage\s+policy|AUP|terms\s+of\s+use', text, re.IGNORECASE)

        if is_aup:
            for requirement, pattern in self.aup_requirements.items():
                if re.search(pattern, text_lower):
                    found_requirements.append(requirement)

            if 'prohibited_activities' not in found_requirements:
                issues.append({
                    'issue': 'Prohibited activities not listed',
                    'severity': 'high',
                    'suggestion': 'List prohibited activities such as: illegal use, harassment, spam, malware, '
                                 'hacking attempts, copyright infringement.',
                    'legal_source': 'Computer Misuse Act 1990, Copyright Act 1988'
                })

            if 'lawful_use' not in found_requirements:
                issues.append({
                    'issue': 'Requirement for lawful use not stated',
                    'severity': 'medium',
                    'suggestion': 'Require users to comply with all applicable laws and regulations.',
                    'legal_source': 'AUP best practice'
                })

            if 'consequences' not in found_requirements:
                issues.append({
                    'issue': 'Consequences of violations not specified',
                    'severity': 'medium',
                    'suggestion': 'Specify consequences for AUP violations including warning, suspension, termination, '
                                 'and potential legal action.',
                    'legal_source': 'Contract law'
                })

            if 'intellectual_property_respect' not in found_requirements:
                issues.append({
                    'issue': 'Intellectual property respect not mentioned',
                    'severity': 'medium',
                    'suggestion': 'Require users to respect intellectual property rights and not infringe copyrights, '
                                 'trademarks, or patents.',
                    'legal_source': 'Copyright, Designs and Patents Act 1988'
                })

        return {
            'found_requirements': found_requirements,
            'issues': issues
        }

    def check(self, text: str, document_type: str) -> Dict[str, Any]:
        """
        Main compliance check for technology documents.

        Args:
            text: Document text to check
            document_type: Type of document being checked

        Returns:
            Compliance result with status, issues, and suggestions
        """
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not appear to relate to technology/software',
                'legal_source': self.legal_source
            }

        all_issues = []

        # Run all compliance checks
        oss_result = self._check_open_source_licenses(text)
        all_issues.extend(oss_result.get('issues', []))

        licensing_result = self._check_software_licensing(text)
        all_issues.extend(licensing_result.get('issues', []))

        saas_result = self._check_saas_agreement(text)
        all_issues.extend(saas_result.get('issues', []))

        cloud_result = self._check_cloud_computing(text)
        all_issues.extend(cloud_result.get('issues', []))

        aup_result = self._check_acceptable_use_policy(text)
        all_issues.extend(aup_result.get('issues', []))

        # Determine overall status
        critical_issues = [i for i in all_issues if i.get('severity') == 'critical']
        high_issues = [i for i in all_issues if i.get('severity') == 'high']

        if critical_issues:
            status = 'FAIL'
            severity = 'critical'
            message = f'Critical technology compliance issues found ({len(critical_issues)} critical, {len(high_issues)} high)'
        elif high_issues:
            status = 'FAIL'
            severity = 'high'
            message = f'Technology compliance issues found ({len(high_issues)} high priority)'
        elif all_issues:
            status = 'WARNING'
            severity = 'medium'
            message = f'Technology compliance warnings ({len(all_issues)} issues)'
        else:
            status = 'PASS'
            severity = 'none'
            message = 'Technology compliance requirements met'

        result = {
            'status': status,
            'severity': severity,
            'message': message,
            'legal_source': self.legal_source,
            'issues': all_issues,
            'open_source_licenses': oss_result.get('detected_licenses', []),
            'software_licensing_terms': licensing_result.get('found_terms', []),
            'saas_requirements': saas_result.get('found_requirements', []),
            'cloud_terms': cloud_result.get('found_terms', []),
            'aup_requirements': aup_result.get('found_requirements', [])
        }

        if all_issues:
            result['suggestions'] = [issue['suggestion'] for issue in all_issues if 'suggestion' in issue]

        return result


# Test cases
def test_technology_compliance():
    """Test cases for technology compliance gate."""
    gate = TechnologyComplianceGate()

    # Test 1: GPL contamination warning
    gpl_text = """
    Software License Agreement

    This software incorporates libraries licensed under GPL v3.
    The software is proprietary and closed source.
    All rights reserved.
    """
    result1 = gate.check(gpl_text, "license")
    assert result1['status'] in ['FAIL', 'WARNING'], f"Expected FAIL/WARNING for GPL contamination, got {result1['status']}"
    assert any('GPL' in str(issue) and 'proprietary' in str(issue).lower()
              for issue in result1.get('issues', [])), "Should flag GPL contamination risk"

    # Test 2: Compliant MIT license usage
    mit_text = """
    Software Attribution

    Uses library-x under MIT License. Copyright notice preserved.
    Original license text included in distribution.
    """
    result2 = gate.check(mit_text, "attribution")
    # MIT is permissive, should have fewer issues
    critical_issues = [i for i in result2.get('issues', []) if i.get('severity') == 'critical']
    assert len(critical_issues) == 0, "MIT license should not have critical issues"

    # Test 3: Incomplete SaaS agreement
    saas_text = """
    Software as a Service Agreement

    We provide cloud-based project management software.
    Monthly subscription fees apply.
    """
    result3 = gate.check(saas_text, "agreement")
    assert result3['status'] in ['FAIL', 'WARNING'], f"Expected FAIL/WARNING, got {result3['status']}"
    assert any('SLA' in str(issue) or 'data ownership' in str(issue).lower() or 'data location' in str(issue).lower()
              for issue in result3.get('issues', [])), "Should flag missing critical SaaS terms"

    # Test 4: Complete SaaS agreement
    complete_saas_text = """
    SaaS Agreement

    Service Level Agreement: 99.9% uptime with service credits for non-compliance.
    Data location: UK and EEA only. Customer retains ownership of all data.
    Data security: AES-256 encryption, ISO 27001 and SOC 2 certified.
    Data portability: export data in JSON/CSV format anytime.
    Acceptable Use Policy attached. Data Processing Agreement included.
    """
    result4 = gate.check(complete_saas_text, "agreement")
    assert len(result4.get('saas_requirements', [])) >= 5, "Should identify multiple SaaS requirements"

    # Test 5: Acceptable Use Policy
    aup_text = """
    Acceptable Use Policy

    Prohibited activities: illegal use, harassment, spam, malware distribution, hacking.
    Users must comply with all applicable laws and respect intellectual property rights.
    Violations will result in suspension or termination.
    We monitor usage for security purposes.
    """
    result5 = gate.check(aup_text, "policy")
    assert len(result5.get('aup_requirements', [])) >= 4, "Should identify multiple AUP requirements"

    # Test 6: Cloud DPA missing
    cloud_text = """
    Cloud Infrastructure Service Agreement

    We provide IaaS cloud computing services.
    Servers located in UK data centers.
    Security certifications: ISO 27001, SOC 2.
    """
    result6 = gate.check(cloud_text, "agreement")
    assert any('data processing agreement' in str(issue).lower() or 'DPA' in str(issue)
              for issue in result6.get('issues', [])), "Should flag missing DPA"

    # Test 7: Not applicable - non-technology document
    non_tech_text = """
    Employee Benefits Guide

    Annual leave: 25 days per year
    Pension scheme: 5% employer contribution
    Health insurance provided
    """
    result7 = gate.check(non_tech_text, "guide")
    assert result7['status'] == 'N/A', f"Expected N/A, got {result7['status']}"

    # Test 8: Apache license with patent grant
    apache_text = """
    Open Source Attribution

    Uses component-y under Apache License 2.0.
    Copyright notices and NOTICE file preserved.
    Patent grant provisions apply.
    """
    result8 = gate.check(apache_text, "attribution")
    detected = result8.get('open_source_licenses', [])
    assert any('apache' in l['name'] for l in detected), "Should detect Apache license"

    print("All technology compliance tests passed!")
    return True


if __name__ == "__main__":
    test_technology_compliance()
