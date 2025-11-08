"""
Finance Compliance Gate
Ensures documents comply with UK financial services regulations including AML, PSD2, and FCA requirements.

Legal Sources:
- Money Laundering Regulations 2017 (5th Money Laundering Directive)
- Payment Services Regulations 2017 (PSD2)
- Financial Services and Markets Act 2000
- Senior Managers & Certification Regime (SMCR)
- Open Banking Standards
- Proceeds of Crime Act 2002
"""

import re
from typing import Dict, Any, List


class FinanceComplianceGate:
    """
    Validates finance documents for UK regulatory compliance including:
    - AML/KYC checks (5th Money Laundering Directive)
    - PSD2 compliance (Payment Services Directive)
    - Open banking requirements
    - Financial crime prevention
    - Senior Managers & Certification Regime (SMCR)
    """

    def __init__(self):
        self.name = "finance_compliance"
        self.severity = "critical"
        self.legal_source = "MLR 2017, PSD2, SMCR, Financial Services and Markets Act 2000"

        # Financial services terminology
        self.finance_terms = [
            r'\bFCA\b',
            r'\bFinancial\s+Conduct\s+Authority\b',
            r'\bPRA\b',
            r'\bPrudential\s+Regulation\s+Authority\b',
            r'\bbank(?:ing)?\b',
            r'\bfinancial\s+service',
            r'\bpayment',
            r'\bcustomer\s+due\s+diligence\b',
            r'\bAML\b',
            r'\bmoney\s+laundering\b',
            r'\bKYC\b'
        ]

        # AML/KYC requirements (MLR 2017)
        self.aml_requirements = {
            'customer_due_diligence': r'(?:customer\s+due\s+diligence|CDD|know\s+your\s+customer|KYC)',
            'enhanced_due_diligence': r'(?:enhanced\s+due\s+diligence|EDD|high-risk|PEP|politically\s+exposed)',
            'identity_verification': r'(?:identity\s+verification|verify\s+identity|ID\s+check|proof\s+of\s+identity)',
            'source_of_funds': r'(?:source\s+of\s+funds|source\s+of\s+wealth|SOF|SOW)',
            'beneficial_ownership': r'(?:beneficial\s+owner|ultimate\s+beneficial\s+owner|UBO|controlling\s+interest)',
            'peps_sanctions': r'(?:PEP|politically\s+exposed|sanction|embargo|prohibited)',
            'ongoing_monitoring': r'(?:ongoing\s+monitoring|continuous\s+monitoring|periodic\s+review)',
            'risk_assessment': r'(?:risk\s+assessment|risk-based\s+approach|ML\s+risk)',
            'suspicious_activity': r'(?:suspicious\s+activity\s+report|SAR|suspicious\s+transaction)',
            'record_keeping': r'(?:record.*retention|keep.*record|5\s+year|five\s+year)'
        }

        # PSD2 requirements
        self.psd2_requirements = {
            'strong_customer_authentication': r'(?:strong\s+customer\s+authentication|SCA|two-factor|2FA|multi-factor)',
            'account_information': r'(?:account\s+information\s+service|AIS|AISP)',
            'payment_initiation': r'(?:payment\s+initiation\s+service|PIS|PISP)',
            'api_access': r'(?:API|application\s+programming\s+interface|XS2A|access\s+to\s+accounts?)',
            'consent': r'(?:explicit\s+consent|customer\s+consent|authorisation|authorization)',
            'payer_authentication': r'(?:payer\s+authentication|authentication\s+requirement)',
            'transaction_monitoring': r'(?:transaction\s+monitoring|fraud\s+detection|fraud\s+prevention)',
            'secure_communication': r'(?:secure\s+communication|encryption|TLS|qualified\s+certificate)'
        }

        # Open Banking requirements
        self.open_banking_requirements = {
            'open_banking_api': r'(?:open\s+banking|read/write\s+API|account\s+information\s+API)',
            'cma_order': r'(?:CMA|Competition\s+and\s+Markets\s+Authority|CMA\s+Order)',
            'tpp': r'(?:TPP|third\s+party\s+provider|AISP|PISP)',
            'data_sharing': r'(?:data\s+sharing|customer\s+data|account\s+data)',
            'consent_dashboard': r'(?:consent\s+dashboard|manage\s+consent|revoke\s+consent)',
            'standards': r'(?:Open\s+Banking\s+Standard|OBIE|open\s+banking\s+implementation)'
        }

        # SMCR requirements
        self.smcr_requirements = {
            'senior_manager': r'(?:Senior\s+Manager|SMF|Senior\s+Management\s+Function)',
            'certification_regime': r'(?:Certification\s+Regime|certified\s+person|fitness\s+and\s+propriety)',
            'conduct_rules': r'(?:conduct\s+rule|individual\s+conduct|FCA\s+conduct)',
            'statement_responsibilities': r'(?:statement\s+of\s+responsibilities|prescribed\s+responsibilities)',
            'regulatory_references': r'(?:regulatory\s+reference|employment\s+reference)',
            'reasonable_steps': r'(?:reasonable\s+step|prevent\s+regulatory\s+breach)',
            'accountability': r'(?:accountability|personal\s+accountability|senior\s+person)'
        }

        # Financial crime prevention
        self.financial_crime = {
            'fraud_prevention': r'(?:fraud\s+prevention|anti-fraud|fraud\s+detection)',
            'transaction_monitoring': r'(?:transaction\s+monitoring|unusual\s+transaction|pattern\s+detection)',
            'sanctions_screening': r'(?:sanction.*screening|embargo.*check|prohibited.*countr)',
            'terrorist_financing': r'(?:terrorist\s+financing|counter.*terrorist|CTF)',
            'whistleblowing': r'(?:whistleblow|protected\s+disclosure)',
            'financial_crime_policy': r'(?:financial\s+crime|economic\s+crime|proceeds\s+of\s+crime)'
        }

    def _is_relevant(self, text: str) -> bool:
        """Check if document relates to financial services."""
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in self.finance_terms)

    def _check_aml_kyc(self, text: str) -> Dict[str, Any]:
        """Check AML/KYC compliance."""
        text_lower = text.lower()
        issues = []
        found_requirements = []

        has_aml_context = re.search(r'(?:AML|KYC|money\s+laundering|customer\s+due\s+diligence)', text_lower)

        if has_aml_context:
            for requirement, pattern in self.aml_requirements.items():
                if re.search(pattern, text_lower):
                    found_requirements.append(requirement)

            # Critical requirements
            if 'customer_due_diligence' not in found_requirements:
                issues.append({
                    'issue': 'Customer Due Diligence (CDD) procedures not specified',
                    'severity': 'critical',
                    'suggestion': 'Specify Customer Due Diligence procedures as required by MLR 2017. '
                                 'Must verify customer identity and assess ML/TF risk.',
                    'legal_source': 'Money Laundering Regulations 2017 Regulation 27'
                })

            if 'beneficial_ownership' not in found_requirements:
                issues.append({
                    'issue': 'Beneficial ownership identification not addressed',
                    'severity': 'critical',
                    'suggestion': 'Require identification and verification of beneficial owners (persons owning >25% '
                                 'or exercising control) as per MLR 2017.',
                    'legal_source': 'Money Laundering Regulations 2017 Regulation 28'
                })

            if 'risk_assessment' not in found_requirements:
                issues.append({
                    'issue': 'ML/TF risk assessment not mentioned',
                    'severity': 'high',
                    'suggestion': 'Conduct and document risk assessment for money laundering and terrorist financing. '
                                 'Apply risk-based approach to CDD.',
                    'legal_source': 'Money Laundering Regulations 2017 Regulation 18'
                })

            if 'record_keeping' not in found_requirements:
                issues.append({
                    'issue': 'Record keeping requirements not specified',
                    'severity': 'high',
                    'suggestion': 'Specify record retention requirements. MLR 2017 requires keeping CDD records for '
                                 '5 years after end of business relationship.',
                    'legal_source': 'Money Laundering Regulations 2017 Regulation 40'
                })

            if 'suspicious_activity' not in found_requirements:
                issues.append({
                    'issue': 'Suspicious Activity Report (SAR) procedures not mentioned',
                    'severity': 'critical',
                    'suggestion': 'Include procedures for submitting Suspicious Activity Reports to the National Crime '
                                 'Agency when knowledge or suspicion of ML/TF exists.',
                    'legal_source': 'Proceeds of Crime Act 2002 Sections 330-332'
                })

            if 'peps_sanctions' not in found_requirements:
                issues.append({
                    'issue': 'PEPs and sanctions screening not addressed',
                    'severity': 'high',
                    'suggestion': 'Implement screening for Politically Exposed Persons (PEPs) and sanctions lists. '
                                 'Apply Enhanced Due Diligence for PEPs.',
                    'legal_source': 'Money Laundering Regulations 2017 Regulation 35'
                })

        return {
            'found_requirements': found_requirements,
            'issues': issues
        }

    def _check_psd2(self, text: str) -> Dict[str, Any]:
        """Check PSD2 compliance."""
        text_lower = text.lower()
        issues = []
        found_requirements = []

        has_psd2_context = re.search(r'(?:PSD2|payment\s+service|payment\s+initiation|'
                                     r'account\s+information|strong\s+customer\s+authentication)', text_lower)

        if has_psd2_context:
            for requirement, pattern in self.psd2_requirements.items():
                if re.search(pattern, text_lower):
                    found_requirements.append(requirement)

            # Check SCA requirement
            if 'strong_customer_authentication' not in found_requirements:
                issues.append({
                    'issue': 'Strong Customer Authentication (SCA) not implemented',
                    'severity': 'critical',
                    'suggestion': 'Implement Strong Customer Authentication requiring two-factor authentication for '
                                 'electronic payments. SCA is mandatory under PSD2.',
                    'legal_source': 'Payment Services Regulations 2017, FCA SCA RTS'
                })

            # Check consent for account access
            if ('account_information' in found_requirements or 'payment_initiation' in found_requirements):
                if 'consent' not in found_requirements:
                    issues.append({
                        'issue': 'Customer consent procedures not specified',
                        'severity': 'high',
                        'suggestion': 'Specify explicit consent procedures for payment initiation and account '
                                     'information services. Customers must give explicit consent.',
                        'legal_source': 'Payment Services Regulations 2017 Regulation 67'
                    })

            if 'secure_communication' not in found_requirements:
                issues.append({
                    'issue': 'Secure communication requirements not addressed',
                    'severity': 'high',
                    'suggestion': 'Implement secure communication channels with encryption and qualified certificates '
                                 'for payment services.',
                    'legal_source': 'PSD2 RTS on SCA and CSC'
                })

        return {
            'found_requirements': found_requirements,
            'issues': issues
        }

    def _check_open_banking(self, text: str) -> Dict[str, Any]:
        """Check Open Banking compliance."""
        text_lower = text.lower()
        issues = []
        found_requirements = []

        has_open_banking = re.search(r'open\s+banking|CMA\s+order|OBIE', text_lower)

        if has_open_banking:
            for requirement, pattern in self.open_banking_requirements.items():
                if re.search(pattern, text_lower):
                    found_requirements.append(requirement)

            if 'data_sharing' in found_requirements and 'consent_dashboard' not in found_requirements:
                issues.append({
                    'issue': 'Consent dashboard not mentioned',
                    'severity': 'medium',
                    'suggestion': 'Provide consent dashboard for customers to view and manage third party access '
                                 'to their account data.',
                    'legal_source': 'CMA Retail Banking Market Investigation Order 2017'
                })

            if 'tpp' in found_requirements and 'api_access' not in found_requirements:
                issues.append({
                    'issue': 'API access for TPPs not specified',
                    'severity': 'high',
                    'suggestion': 'Provide API access to authorized Third Party Providers (TPPs) in compliance with '
                                 'Open Banking Standards.',
                    'legal_source': 'CMA Order, Open Banking Implementation Entity Standards'
                })

        return {
            'found_requirements': found_requirements,
            'issues': issues
        }

    def _check_smcr(self, text: str) -> Dict[str, Any]:
        """Check Senior Managers & Certification Regime compliance."""
        text_lower = text.lower()
        issues = []
        found_requirements = []

        has_smcr_context = re.search(r'(?:SMCR|Senior\s+Manager|Certification\s+Regime|conduct\s+rule)', text_lower)

        if has_smcr_context:
            for requirement, pattern in self.smcr_requirements.items():
                if re.search(pattern, text_lower):
                    found_requirements.append(requirement)

            if 'senior_manager' in found_requirements:
                if 'statement_responsibilities' not in found_requirements:
                    issues.append({
                        'issue': 'Statement of Responsibilities not mentioned',
                        'severity': 'high',
                        'suggestion': 'Senior Managers must have a Statement of Responsibilities setting out their '
                                     'prescribed responsibilities.',
                        'legal_source': 'FSMA 2000 (as amended), FCA SYSC'
                    })

            if 'certification_regime' in found_requirements:
                if 'regulatory_references' not in found_requirements:
                    issues.append({
                        'issue': 'Regulatory references not addressed',
                        'severity': 'medium',
                        'suggestion': 'Firms must provide and obtain regulatory references for certified persons, '
                                     'covering 6 years of employment history.',
                        'legal_source': 'FCA SYSC 22 (Regulatory References)'
                    })

            if not found_requirements:
                # If SMCR mentioned but no specifics
                issues.append({
                    'issue': 'SMCR requirements not detailed',
                    'severity': 'medium',
                    'suggestion': 'Detail SMCR requirements including Senior Manager Functions, Certification Regime, '
                                 'and Conduct Rules applicable to your firm.',
                    'legal_source': 'FCA Handbook SYSC, COCON'
                })

        return {
            'found_requirements': found_requirements,
            'issues': issues
        }

    def _check_financial_crime(self, text: str) -> Dict[str, Any]:
        """Check financial crime prevention measures."""
        text_lower = text.lower()
        issues = []
        found_measures = []

        has_crime_context = re.search(r'(?:financial\s+crime|fraud|sanction|terrorist\s+financing)', text_lower)

        if has_crime_context:
            for measure, pattern in self.financial_crime.items():
                if re.search(pattern, text_lower):
                    found_measures.append(measure)

            if 'fraud_prevention' in found_measures:
                if 'transaction_monitoring' not in found_measures:
                    issues.append({
                        'issue': 'Transaction monitoring not specified',
                        'severity': 'medium',
                        'suggestion': 'Implement transaction monitoring systems to detect unusual patterns and '
                                     'suspicious activity.',
                        'legal_source': 'FCA Principle 3 - Management and Control'
                    })

            if 'terrorist_financing' in text_lower:
                if 'sanctions_screening' not in found_measures:
                    issues.append({
                        'issue': 'Sanctions screening not addressed',
                        'severity': 'high',
                        'suggestion': 'Implement sanctions screening against UK, UN, and EU sanctions lists to '
                                     'prevent terrorist financing.',
                        'legal_source': 'Terrorism Act 2000, Sanctions and Anti-Money Laundering Act 2018'
                    })

        return {
            'found_measures': found_measures,
            'issues': issues
        }

    def check(self, text: str, document_type: str) -> Dict[str, Any]:
        """
        Main compliance check for finance documents.

        Args:
            text: Document text to check
            document_type: Type of document being checked

        Returns:
            Compliance result with status, issues, and suggestions
        """
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not appear to relate to financial services',
                'legal_source': self.legal_source
            }

        all_issues = []

        # Run all compliance checks
        aml_result = self._check_aml_kyc(text)
        all_issues.extend(aml_result.get('issues', []))

        psd2_result = self._check_psd2(text)
        all_issues.extend(psd2_result.get('issues', []))

        open_banking_result = self._check_open_banking(text)
        all_issues.extend(open_banking_result.get('issues', []))

        smcr_result = self._check_smcr(text)
        all_issues.extend(smcr_result.get('issues', []))

        financial_crime_result = self._check_financial_crime(text)
        all_issues.extend(financial_crime_result.get('issues', []))

        # Determine overall status
        critical_issues = [i for i in all_issues if i.get('severity') == 'critical']
        high_issues = [i for i in all_issues if i.get('severity') == 'high']

        if critical_issues:
            status = 'FAIL'
            severity = 'critical'
            message = f'Critical financial compliance issues found ({len(critical_issues)} critical, {len(high_issues)} high)'
        elif high_issues:
            status = 'FAIL'
            severity = 'high'
            message = f'Financial compliance issues found ({len(high_issues)} high priority)'
        elif all_issues:
            status = 'WARNING'
            severity = 'medium'
            message = f'Financial compliance warnings ({len(all_issues)} issues)'
        else:
            status = 'PASS'
            severity = 'none'
            message = 'Financial compliance requirements met'

        result = {
            'status': status,
            'severity': severity,
            'message': message,
            'legal_source': self.legal_source,
            'issues': all_issues,
            'aml_requirements': aml_result.get('found_requirements', []),
            'psd2_requirements': psd2_result.get('found_requirements', []),
            'smcr_requirements': smcr_result.get('found_requirements', [])
        }

        if all_issues:
            result['suggestions'] = [issue['suggestion'] for issue in all_issues if 'suggestion' in issue]

        return result


# Test cases
def test_finance_compliance():
    """Test cases for finance compliance gate."""
    gate = FinanceComplianceGate()

    # Test 1: Compliant AML/KYC policy
    compliant_text = """
    Anti-Money Laundering and KYC Policy

    Customer Due Diligence: We verify identity and assess ML/TF risk for all customers.
    Beneficial ownership is identified for entities with ownership >25%.
    Enhanced Due Diligence is applied to PEPs and high-risk jurisdictions.

    We maintain ongoing monitoring and submit Suspicious Activity Reports to the NCA.
    Records are retained for 5 years. PEPs and sanctions screening is conducted.
    Risk assessment is performed annually and documented.
    """
    result1 = gate.check(compliant_text, "policy")
    assert result1['status'] == 'PASS', f"Expected PASS, got {result1['status']}: {result1.get('message')}"

    # Test 2: PSD2 compliance with SCA
    psd2_text = """
    Payment Services Policy

    Strong Customer Authentication (SCA) with two-factor authentication is required.
    Payment initiation services require explicit customer consent.
    Secure communication channels use TLS encryption and qualified certificates.
    Transaction monitoring detects fraud patterns.
    """
    result2 = gate.check(psd2_text, "policy")
    assert result2['status'] in ['PASS', 'WARNING'], f"Expected PASS/WARNING, got {result2['status']}"
    assert 'strong_customer_authentication' in result2.get('psd2_requirements', [])

    # Test 3: Missing critical AML requirements
    non_compliant_text = """
    Anti-Money Laundering Policy

    We conduct KYC checks on customers.
    Identity verification is performed.
    """
    result3 = gate.check(non_compliant_text, "policy")
    assert result3['status'] in ['FAIL', 'WARNING'], f"Expected FAIL/WARNING, got {result3['status']}"
    assert len(result3.get('issues', [])) > 0, "Should flag missing critical AML requirements"

    # Test 4: SMCR requirements
    smcr_text = """
    Senior Managers and Certification Regime Policy

    Senior Managers have Statements of Responsibilities for prescribed responsibilities.
    The Certification Regime applies to certified persons with fitness and propriety assessments.
    Conduct Rules apply to all staff. Regulatory references cover 6 years employment history.
    """
    result4 = gate.check(smcr_text, "policy")
    assert result4['status'] in ['PASS', 'WARNING', 'FAIL'], "Should return valid status"
    assert 'smcr_requirements' in result4, "Should check SMCR"

    # Test 5: Not applicable - non-financial document
    non_finance_text = """
    Employee Handbook

    Work hours are 9am to 5pm Monday to Friday.
    Annual leave entitlement is 25 days per year.
    """
    result5 = gate.check(non_finance_text, "handbook")
    assert result5['status'] == 'N/A', f"Expected N/A, got {result5['status']}"

    # Test 6: Open Banking
    open_banking_text = """
    Open Banking API Policy

    API access provided to TPPs (AISPs and PISPs) under CMA Order.
    Consent dashboard allows customers to manage third party data sharing.
    Strong Customer Authentication protects account access.
    """
    result6 = gate.check(open_banking_text, "policy")
    assert len(result6.get('psd2_requirements', [])) > 0, "Should identify PSD2/Open Banking requirements"

    print("All finance compliance tests passed!")
    return True


if __name__ == "__main__":
    test_finance_compliance()
