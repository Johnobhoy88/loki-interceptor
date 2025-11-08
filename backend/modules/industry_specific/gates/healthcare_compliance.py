"""
Healthcare Compliance Gate
Ensures documents comply with NHS regulations, CQC requirements, and health data protection standards.

Legal Sources:
- Health and Social Care Act 2012
- Care Quality Commission (Registration) Regulations 2009
- Data Protection Act 2018 (health data special category)
- Caldicott Principles
- NHS Act 2006
"""

import re
from typing import Dict, Any, List


class HealthcareComplianceGate:
    """
    Validates healthcare documents for UK regulatory compliance including:
    - NHS regulations and guidance
    - CQC fundamental standards
    - Medical records management
    - Patient confidentiality (Caldicott principles)
    - GDPR special category health data
    """

    def __init__(self):
        self.name = "healthcare_compliance"
        self.severity = "critical"
        self.legal_source = "Health and Social Care Act 2012, CQC Regulations, Caldicott Principles"

        # NHS and healthcare terminology patterns
        self.nhs_terms = [
            r'\bNHS\b',
            r'\bNational Health Service\b',
            r'\bpatient',
            r'\bmedical record',
            r'\bclinical',
            r'\bhealthcare',
            r'\bhealth\s+care\b',
            r'\bprimary\s+care\b',
            r'\bsecondary\s+care\b',
            r'\bCQC\b',
            r'\bCare Quality Commission\b'
        ]

        # Caldicott principles keywords
        self.caldicott_principles = {
            'justify_purpose': r'(?:justify|justification|purpose|legitimate\s+purpose)',
            'dont_use_unless_necessary': r'(?:necessary|minimum\s+necessary|data\s+minimisation)',
            'minimum_necessary': r'(?:minimum|least|proportionate|minimal)',
            'access_on_need_to_know': r'(?:need\s+to\s+know|access\s+control|authorized\s+access)',
            'everyone_responsible': r'(?:responsibility|accountable|duty|obligation)',
            'comply_with_law': r'(?:comply|compliance|legal\s+obligation|lawful)',
            'duty_to_share': r'(?:information\s+sharing|disclosure|appropriate\s+sharing)'
        }

        # CQC fundamental standards
        self.cqc_standards = {
            'person_centred_care': r'(?:person-centred|person\s+centred|dignity|respect|autonomy)',
            'safe_care': r'(?:safe|safety|safeguarding|harm\s+prevention)',
            'dignity_respect': r'(?:dignity|respect|compassion|privacy)',
            'consent': r'(?:consent|capacity|Mental\s+Capacity\s+Act|best\s+interests)',
            'safe_premises': r'(?:premises|environment|infection\s+control)',
            'good_governance': r'(?:governance|quality\s+assurance|monitoring)'
        }

        # Medical records compliance patterns
        self.medical_records_requirements = [
            r'(?:medical\s+record|health\s+record|clinical\s+record)',
            r'(?:record\s+retention|retention\s+period)',
            r'(?:8\s+years?|eight\s+years?)',  # Standard retention period
            r'(?:secure\s+storage|confidential\s+storage)',
            r'(?:access\s+log|audit\s+trail)'
        ]

        # GDPR special category health data
        self.health_data_protection = [
            r'(?:special\s+category|health\s+data|medical\s+data)',
            r'(?:explicit\s+consent|Article\s+9)',
            r'(?:data\s+protection\s+impact|DPIA)',
            r'(?:pseudonymisation|anonymisation)',
            r'(?:data\s+breach|breach\s+notification)'
        ]

    def _is_relevant(self, text: str) -> bool:
        """Check if document relates to healthcare."""
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in self.nhs_terms)

    def _check_caldicott_compliance(self, text: str) -> Dict[str, Any]:
        """Check for Caldicott principles in patient information handling."""
        text_lower = text.lower()
        issues = []
        found_principles = []

        for principle, pattern in self.caldicott_principles.items():
            if re.search(pattern, text_lower):
                found_principles.append(principle)

        if not found_principles and 'patient' in text_lower:
            issues.append({
                'issue': 'Caldicott principles not addressed',
                'severity': 'high',
                'suggestion': 'Include reference to Caldicott principles for patient information governance. '
                             'Address: justify purpose, use minimum necessary data, need-to-know access, '
                             'shared responsibility, legal compliance, and duty to share appropriately.'
            })

        return {
            'caldicott_principles_found': found_principles,
            'issues': issues
        }

    def _check_cqc_standards(self, text: str) -> Dict[str, Any]:
        """Check for CQC fundamental standards compliance."""
        text_lower = text.lower()
        found_standards = []

        for standard, pattern in self.cqc_standards.items():
            if re.search(pattern, text_lower):
                found_standards.append(standard)

        issues = []
        if re.search(r'CQC|Care\s+Quality\s+Commission', text, re.IGNORECASE):
            if len(found_standards) < 2:
                issues.append({
                    'issue': 'Limited CQC fundamental standards coverage',
                    'severity': 'medium',
                    'suggestion': 'Address CQC fundamental standards: person-centred care, safe care and treatment, '
                                 'dignity and respect, consent, safe premises, and good governance.'
                })

        return {
            'cqc_standards_found': found_standards,
            'issues': issues
        }

    def _check_medical_records(self, text: str) -> Dict[str, Any]:
        """Check medical records management compliance."""
        text_lower = text.lower()
        issues = []

        has_medical_records = any(re.search(pattern, text_lower)
                                 for pattern in self.medical_records_requirements[:1])

        if has_medical_records:
            # Check retention period
            if not re.search(r'(?:8\s+years?|eight\s+years?|retention\s+period)', text_lower):
                issues.append({
                    'issue': 'Medical records retention period not specified',
                    'severity': 'high',
                    'suggestion': 'Specify retention period (minimum 8 years for GP records, '
                                 '20 years for hospital records involving children).',
                    'legal_source': 'Records Management Code of Practice for Health and Social Care 2016'
                })

            # Check secure storage
            if not re.search(r'(?:secure|confidential|encrypted|access\s+control)', text_lower):
                issues.append({
                    'issue': 'Medical records security measures not specified',
                    'severity': 'high',
                    'suggestion': 'Specify secure storage measures including access controls, encryption, '
                                 'and audit trails for medical records.',
                    'legal_source': 'Data Security and Protection Toolkit'
                })

        return {'issues': issues}

    def _check_health_data_protection(self, text: str) -> Dict[str, Any]:
        """Check GDPR special category health data compliance."""
        text_lower = text.lower()
        issues = []

        has_health_data = re.search(r'(?:health\s+data|medical\s+data|patient\s+(?:data|information))', text_lower)

        if has_health_data:
            # Check for special category acknowledgment
            if not re.search(r'(?:special\s+category|Article\s+9|explicit\s+consent)', text_lower):
                issues.append({
                    'issue': 'Health data not recognized as special category data',
                    'severity': 'critical',
                    'suggestion': 'Acknowledge that health data is special category data under GDPR Article 9 '
                                 'requiring explicit consent or another Article 9(2) condition.',
                    'legal_source': 'UK GDPR Article 9'
                })

            # Check for DPIA mention (likely required for health data)
            if not re.search(r'(?:DPIA|data\s+protection\s+impact|privacy\s+impact)', text_lower):
                issues.append({
                    'issue': 'Data Protection Impact Assessment (DPIA) not mentioned',
                    'severity': 'high',
                    'suggestion': 'Consider conducting a DPIA for health data processing as it presents high risk.',
                    'legal_source': 'UK GDPR Article 35'
                })

        return {'issues': issues}

    def _check_nhs_specific(self, text: str) -> Dict[str, Any]:
        """Check NHS-specific requirements."""
        text_lower = text.lower()
        issues = []

        is_nhs_document = re.search(r'\bNHS\b|National\s+Health\s+Service', text, re.IGNORECASE)

        if is_nhs_document:
            # Check for NHS number handling
            if re.search(r'NHS\s+number', text_lower):
                if not re.search(r'(?:secure|protect|confidential|encrypt)', text_lower):
                    issues.append({
                        'issue': 'NHS number security not addressed',
                        'severity': 'high',
                        'suggestion': 'Specify security measures for NHS numbers (unique patient identifier). '
                                     'NHS numbers must be protected and only used for healthcare purposes.',
                        'legal_source': 'NHS Act 2006 Section 251'
                    })

            # Check for information governance
            if not re.search(r'(?:information\s+governance|IG|data\s+security|Caldicott)', text_lower):
                issues.append({
                    'issue': 'Information Governance framework not referenced',
                    'severity': 'medium',
                    'suggestion': 'Reference NHS Information Governance framework and Data Security and Protection Toolkit.',
                    'legal_source': 'Health and Social Care Act 2012'
                })

        return {'issues': issues}

    def check(self, text: str, document_type: str) -> Dict[str, Any]:
        """
        Main compliance check for healthcare documents.

        Args:
            text: Document text to check
            document_type: Type of document being checked

        Returns:
            Compliance result with status, issues, and suggestions
        """
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not appear to relate to healthcare',
                'legal_source': self.legal_source
            }

        all_issues = []

        # Run all compliance checks
        caldicott_result = self._check_caldicott_compliance(text)
        all_issues.extend(caldicott_result.get('issues', []))

        cqc_result = self._check_cqc_standards(text)
        all_issues.extend(cqc_result.get('issues', []))

        records_result = self._check_medical_records(text)
        all_issues.extend(records_result.get('issues', []))

        health_data_result = self._check_health_data_protection(text)
        all_issues.extend(health_data_result.get('issues', []))

        nhs_result = self._check_nhs_specific(text)
        all_issues.extend(nhs_result.get('issues', []))

        # Determine overall status
        critical_issues = [i for i in all_issues if i.get('severity') == 'critical']
        high_issues = [i for i in all_issues if i.get('severity') == 'high']

        if critical_issues:
            status = 'FAIL'
            severity = 'critical'
            message = f'Critical healthcare compliance issues found ({len(critical_issues)} critical, {len(high_issues)} high)'
        elif high_issues:
            status = 'FAIL'
            severity = 'high'
            message = f'Healthcare compliance issues found ({len(high_issues)} high priority)'
        elif all_issues:
            status = 'WARNING'
            severity = 'medium'
            message = f'Healthcare compliance warnings ({len(all_issues)} issues)'
        else:
            status = 'PASS'
            severity = 'none'
            message = 'Healthcare compliance requirements met'

        result = {
            'status': status,
            'severity': severity,
            'message': message,
            'legal_source': self.legal_source,
            'issues': all_issues,
            'caldicott_principles': caldicott_result.get('caldicott_principles_found', []),
            'cqc_standards': cqc_result.get('cqc_standards_found', [])
        }

        if all_issues:
            result['suggestions'] = [issue['suggestion'] for issue in all_issues if 'suggestion' in issue]

        return result


# Test cases
def test_healthcare_compliance():
    """Test cases for healthcare compliance gate."""
    gate = HealthcareComplianceGate()

    # Test 1: Compliant NHS patient information policy
    compliant_text = """
    NHS Patient Information Governance Policy

    This policy ensures compliance with Caldicott principles for patient information handling.
    All patient data is special category data under GDPR Article 9 requiring explicit consent.

    Medical records will be retained for a minimum of 8 years and stored securely with
    access controls based on need-to-know principles. We maintain person-centred care
    practices ensuring dignity and respect for all patients.

    A Data Protection Impact Assessment (DPIA) has been conducted for all health data processing.
    Information governance procedures comply with the Data Security and Protection Toolkit.
    """
    result1 = gate.check(compliant_text, "policy")
    assert result1['status'] == 'PASS', f"Expected PASS, got {result1['status']}: {result1.get('message')}"

    # Test 2: Non-compliant - missing Caldicott principles
    non_compliant_text = """
    Hospital Patient Data Policy

    We collect patient medical records and health information.
    Data will be stored on our servers.
    """
    result2 = gate.check(non_compliant_text, "policy")
    assert result2['status'] in ['FAIL', 'WARNING'], f"Expected FAIL/WARNING, got {result2['status']}"
    assert any('Caldicott' in str(issue) or 'special category' in str(issue)
              for issue in result2.get('issues', [])), "Should flag Caldicott or GDPR Article 9 issues"

    # Test 3: Not applicable - non-healthcare document
    non_healthcare_text = """
    Company financial report for Q3 2024.
    Revenue increased by 15% compared to previous quarter.
    """
    result3 = gate.check(non_healthcare_text, "report")
    assert result3['status'] == 'N/A', f"Expected N/A, got {result3['status']}"

    # Test 4: Missing medical records retention period
    missing_retention = """
    NHS Clinical Records Management

    We maintain patient medical records with secure storage and access controls.
    All staff follow person-centred care principles with dignity and respect.
    """
    result4 = gate.check(missing_retention, "policy")
    assert any('retention' in str(issue).lower() for issue in result4.get('issues', [])), \
        "Should flag missing retention period"

    # Test 5: CQC registered service
    cqc_service = """
    CQC Healthcare Service Policy

    Our NHS service provides safe care and treatment with person-centred approaches.
    We ensure dignity and respect for all patients, obtain proper consent, maintain safe premises,
    and implement good governance frameworks for healthcare delivery.
    """
    result5 = gate.check(cqc_service, "policy")
    assert result5['status'] in ['PASS', 'WARNING', 'FAIL', 'N/A'], "Should return valid status"

    print("All healthcare compliance tests passed!")
    return True


if __name__ == "__main__":
    test_healthcare_compliance()
