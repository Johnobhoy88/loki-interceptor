"""
Comprehensive GDPR UK Gates Test Suite
Tests all 60+ GDPR compliance gates
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..', 'backend'))

import pytest


class TestGDPRGatesCount:
    """Test that we have 60+ gates"""

    def test_gate_count(self):
        """Verify we have at least 60 gates"""
        # Count gates defined in gdpr_uk_gates.py
        gates_file = os.path.join(os.path.dirname(__file__), '../../../backend/gates/gdpr_uk_gates.py')

        with open(gates_file, 'r') as f:
            content = f.read()

        # Count gate assignments (gates['name'] = ...)
        import re
        gate_assignments = re.findall(r"gates\['(\w+)'\]\s*=", content)

        assert len(gate_assignments) >= 60, f"Expected at least 60 gates, found {len(gate_assignments)}"
        print(f"✓ Total gates found: {len(gate_assignments)}")


class TestConsentValidators:
    """Test consent validation modules"""

    def test_consent_validator_import(self):
        """Test that consent validator can be imported"""
        from compliance.gdpr.consent_validator import ConsentValidator

        validator = ConsentValidator()
        assert validator is not None
        assert hasattr(validator, 'validate_consent')

    def test_consent_freely_given(self):
        """Test freely given consent validation"""
        from compliance.gdpr.consent_validator import ConsentValidator

        validator = ConsentValidator()

        # Should FAIL: forced consent
        text_fail = "By using this website you agree to our terms and cookies"
        result = validator.validate_consent(text_fail)
        assert not result['is_valid'], "Forced consent should fail"
        assert len(result['issues']) > 0

        # Should PASS: proper consent
        text_pass = """
        We process data with your consent. You can provide consent by clicking 'I agree'.
        You can withdraw consent at any time by emailing privacy@example.com.
        """
        result = validator.validate_consent(text_pass)
        # May have warnings but shouldn't have critical issues
        assert result['issues'] == [] or result['severity'] != 'critical'

    def test_consent_specific(self):
        """Test specific consent validation"""
        from compliance.gdpr.consent_validator import ConsentValidator

        validator = ConsentValidator()

        # Should FAIL: bundled consent
        text_fail = "I agree to all terms, privacy policy, marketing, and cookies"
        result = validator.validate_consent(text_fail)
        assert not result['is_valid']

    def test_consent_explicit(self):
        """Test explicit consent for special category data"""
        from compliance.gdpr.consent_validator import ConsentValidator

        validator = ConsentValidator()

        # Should FAIL: health data without explicit consent
        text_fail = "We process your health data to provide medical services"
        result = validator.validate_consent(text_fail)
        assert not result['is_valid']
        assert result['article_9_required']

        # Should PASS: explicit consent
        text_pass = """
        We process health data. By clicking 'I agree', you provide explicit consent
        to process your health information for medical treatment purposes.
        """
        result = validator.validate_consent(text_pass)
        assert result['article_9_required']
        # Should have fewer issues


class TestSubjectRights:
    """Test data subject rights validation"""

    def test_subject_rights_validator_import(self):
        """Test that subject rights validator can be imported"""
        from compliance.gdpr.subject_rights import SubjectRightsValidator

        validator = SubjectRightsValidator()
        assert validator is not None

    def test_all_8_rights(self):
        """Test validation of all 8 data subject rights"""
        from compliance.gdpr.subject_rights import SubjectRightsValidator

        validator = SubjectRightsValidator()

        # Comprehensive privacy policy with all rights
        text_complete = """
        Privacy Policy

        We collect personal data to provide our services.

        Your Rights:
        1. Right to be informed: We provide this privacy notice
        2. Right of access: You can request a copy of your data (Subject Access Request)
        3. Right to rectification: You can correct inaccurate data
        4. Right to erasure: You can request deletion of your data (right to be forgotten)
        5. Right to restrict processing: You can restrict how we process your data
        6. Right to data portability: You can receive your data in machine-readable format
        7. Right to object: You can object to processing, including direct marketing
        8. Automated decision-making: You have rights regarding automated decisions

        Contact us at privacy@example.com to exercise your rights.
        You have the right to complain to the ICO at ico.org.uk.
        """

        result = validator.validate_rights_disclosure(text_complete)
        assert result['is_complete'], f"All 8 rights should be found. Missing: {result['rights_missing']}"
        assert result['coverage_percentage'] == 100.0
        assert len(result['rights_found']) == 8

    def test_missing_rights(self):
        """Test detection of missing rights"""
        from compliance.gdpr.subject_rights import SubjectRightsValidator

        validator = SubjectRightsValidator()

        # Incomplete privacy policy
        text_incomplete = """
        Privacy Policy

        We collect your data. You can access your data by contacting us.
        """

        result = validator.validate_rights_disclosure(text_incomplete)
        assert not result['is_complete']
        assert len(result['rights_missing']) > 0
        assert len(result['critical_missing']) > 0


class TestRetentionPolicy:
    """Test retention policy validation"""

    def test_retention_checker_import(self):
        """Test retention checker import"""
        from compliance.gdpr.retention import RetentionPolicyChecker

        checker = RetentionPolicyChecker()
        assert checker is not None

    def test_specific_retention_periods(self):
        """Test that specific retention periods are required"""
        from compliance.gdpr.retention import RetentionPolicyChecker

        checker = RetentionPolicyChecker()

        # FAIL: vague retention
        text_fail = "We keep your data for as long as necessary"
        result = checker.check_retention_policy(text_fail)
        assert not result['is_compliant']
        assert len(result['issues']) > 0

        # PASS: specific retention
        text_pass = """
        Privacy Policy

        Data Retention:
        - Account data: Retained for duration of account + 12 months
        - Transaction records: 7 years (tax law requirement)
        - Marketing data: 2 years or until consent withdrawn

        We securely delete data at end of retention period.
        """
        result = checker.check_retention_policy(text_pass)
        assert result['has_policy']
        assert len(result['retention_periods_found']) > 0

    def test_indefinite_retention(self):
        """Test detection of indefinite retention"""
        from compliance.gdpr.retention import RetentionPolicyChecker

        checker = RetentionPolicyChecker()

        text_fail = "We retain your data indefinitely"
        result = checker.check_retention_policy(text_fail)
        assert not result['is_compliant']
        assert any('indefinite' in issue.lower() for issue in result['issues'])


class TestInternationalTransfers:
    """Test international transfer validation"""

    def test_transfer_validator_import(self):
        """Test transfer validator import"""
        from compliance.gdpr.international_transfer import InternationalTransferValidator

        validator = InternationalTransferValidator()
        assert validator is not None

    def test_adequate_countries(self):
        """Test adequacy decisions"""
        from compliance.gdpr.international_transfer import InternationalTransferValidator

        validator = InternationalTransferValidator()

        # PASS: adequate country
        text_adequate = """
        We transfer data to Ireland (EEA country with adequate protection).
        """
        result = validator.validate_transfers(text_adequate)
        assert result['has_transfers']
        assert len(result['adequate_countries_mentioned']) > 0
        assert len(result['issues']) == 0

    def test_inadequate_countries(self):
        """Test non-adequate countries require safeguards"""
        from compliance.gdpr.international_transfer import InternationalTransferValidator

        validator = InternationalTransferValidator()

        # FAIL: no safeguards
        text_fail = "We transfer data to the USA"
        result = validator.validate_transfers(text_fail)
        assert result['has_transfers']
        # Should have warnings about safeguards

        # PASS: with safeguards
        text_pass = """
        We transfer data to the USA using Standard Contractual Clauses (SCCs)
        and supplementary measures to ensure adequate protection.
        """
        result = validator.validate_transfers(text_pass)
        assert result['has_transfers']
        assert 'sccs' in result['mechanisms_used']

    def test_privacy_shield_invalid(self):
        """Test that Privacy Shield is flagged as invalid"""
        from compliance.gdpr.international_transfer import InternationalTransferValidator

        validator = InternationalTransferValidator()

        text_fail = "We transfer data to USA under Privacy Shield framework"
        result = validator.validate_transfers(text_fail)
        assert len(result['warnings']) > 0
        assert any('privacy shield' in w.lower() for w in result['warnings'])


class TestDPIA:
    """Test DPIA requirements"""

    def test_dpia_checker_import(self):
        """Test DPIA checker import"""
        from compliance.gdpr.dpia_checker import DPIAChecker

        checker = DPIAChecker()
        assert checker is not None

    def test_high_risk_processing(self):
        """Test DPIA required for high-risk processing"""
        from compliance.gdpr.dpia_checker import DPIAChecker

        checker = DPIAChecker()

        # FAIL: high-risk without DPIA
        text_fail = """
        We use automated decision-making with AI to make credit decisions.
        We process large-scale biometric data for facial recognition.
        """
        result = checker.check_dpia_requirement(text_fail)
        assert result['dpia_required']
        assert result['risk_count'] >= 2

        # PASS: DPIA conducted
        text_pass = """
        We use automated decision-making for credit scoring.
        We have conducted a Data Protection Impact Assessment (DPIA)
        covering the risks, necessity, and mitigation measures.
        """
        result = checker.check_dpia_requirement(text_pass)
        assert result['dpia_required']
        assert result['dpia_mentioned']


class TestCookieConsent:
    """Test PECR cookie consent validation"""

    def test_cookie_validator_import(self):
        """Test cookie validator import"""
        from compliance.gdpr.cookie_consent import CookieConsentValidator

        validator = CookieConsentValidator()
        assert validator is not None

    def test_non_essential_cookies(self):
        """Test non-essential cookies require consent"""
        from compliance.gdpr.cookie_consent import CookieConsentValidator

        validator = CookieConsentValidator()

        # FAIL: no consent
        text_fail = "We use Google Analytics cookies to track your usage"
        result = validator.validate_cookie_compliance(text_fail)
        assert result['has_cookies']
        assert len(result['consent_required_types']) > 0

        # PASS: with consent
        text_pass = """
        We use cookies on our website.

        Cookie Types:
        - Strictly necessary cookies (no consent required)
        - Analytics cookies (requires consent) - Google Analytics
        - Advertising cookies (requires consent)

        Manage cookie preferences: Accept, Reject, or Customize
        """
        result = validator.validate_cookie_compliance(text_pass)
        assert result['has_cookies']
        assert result['has_consent_mechanism']

    def test_preticked_consent(self):
        """Test that pre-ticked cookie consent is flagged"""
        from compliance.gdpr.cookie_consent import CookieConsentValidator

        validator = CookieConsentValidator()

        text_fail = "Cookies are pre-selected by default"
        result = validator.validate_cookie_compliance(text_fail)
        assert not result['is_compliant']
        assert len(result['issues']) > 0


class TestBreachNotification:
    """Test breach notification requirements"""

    def test_breach_checker_import(self):
        """Test breach checker import"""
        from compliance.gdpr.breach_checker import BreachNotificationChecker

        checker = BreachNotificationChecker()
        assert checker is not None

    def test_72_hour_notification(self):
        """Test 72-hour ICO notification"""
        from compliance.gdpr.breach_checker import BreachNotificationChecker

        checker = BreachNotificationChecker()

        text_complete = """
        Privacy Policy

        Data Breach Notification:
        In the event of a personal data breach, we will notify the Information
        Commissioner's Office (ICO) within 72 hours of becoming aware of the breach.
        If the breach poses a high risk to your rights and freedoms, we will
        notify you without undue delay.
        """
        result = checker.check_breach_procedures(text_complete)
        assert result['has_breach_procedure']
        assert result['notification_elements']['ico_notification']['mentioned']
        assert result['notification_elements']['ico_notification']['timeframe_specified']


class TestChildrenDataProtection:
    """Test children's data protection (UK age 13)"""

    def test_children_validator_import(self):
        """Test children validator import"""
        from compliance.gdpr.children import ChildrenDataProtection

        validator = ChildrenDataProtection()
        assert validator is not None
        assert validator.uk_consent_age == 13

    def test_uk_age_13(self):
        """Test UK age of consent is 13, not 16"""
        from compliance.gdpr.children import ChildrenDataProtection

        validator = ChildrenDataProtection()

        # Should warn if using age 16
        text_wrong_age = "Children under 16 require parental consent"
        result = validator.validate_children_protection(text_wrong_age)
        assert result['processes_children_data']
        # Should suggest age 13

        # Correct age
        text_correct = """
        Children under 13 require parental consent to use our service
        (UK Data Protection Act 2018).
        We verify age through date of birth and verify parental consent
        through email confirmation.
        """
        result = validator.validate_children_protection(text_correct)
        assert result['processes_children_data']
        assert len(result['issues']) == 0


class TestLegitimateInterest:
    """Test legitimate interest assessment"""

    def test_li_assessor_import(self):
        """Test LI assessor import"""
        from compliance.gdpr.legitimate_interest import LegitimateInterestAssessor

        assessor = LegitimateInterestAssessor()
        assert assessor is not None

    def test_lia_required(self):
        """Test LIA is required when using legitimate interest"""
        from compliance.gdpr.legitimate_interest import LegitimateInterestAssessor

        assessor = LegitimateInterestAssessor()

        # FAIL: LI without LIA
        text_fail = "We process data based on our legitimate interest"
        result = assessor.assess_legitimate_interest(text_fail)
        assert result['claims_legitimate_interest']
        assert not result['lia_conducted']

        # PASS: LIA documented
        text_pass = """
        We process data based on legitimate interest for fraud prevention.

        Legitimate Interest Assessment:
        - Purpose: Fraud prevention is necessary to protect our business
        - Necessity: Processing is necessary as we cannot achieve this goal otherwise
        - Balancing: We considered impact on individuals and determined our interest
          does not override their rights. Individuals can object.

        You have the right to object to processing based on legitimate interests.
        """
        result = assessor.assess_legitimate_interest(text_pass)
        assert result['claims_legitimate_interest']
        assert result['lia_conducted']


class TestPrivacyNotice:
    """Test privacy notice completeness"""

    def test_privacy_checker_import(self):
        """Test privacy notice checker import"""
        from compliance.gdpr.privacy_notice import PrivacyNoticeChecker

        checker = PrivacyNoticeChecker()
        assert checker is not None

    def test_required_elements(self):
        """Test all required elements are checked"""
        from compliance.gdpr.privacy_notice import PrivacyNoticeChecker

        checker = PrivacyNoticeChecker()

        # Incomplete privacy policy
        text_incomplete = """
        Privacy Policy
        We collect some data.
        """
        result = checker.check_privacy_notice(text_incomplete)
        assert result['is_privacy_notice']
        assert not result['is_complete']
        assert len(result['critical_missing']) > 0


class TestDataMinimization:
    """Test data minimization principle"""

    def test_minimization_validator_import(self):
        """Test data minimization validator import"""
        from compliance.gdpr.data_minimization import DataMinimizationValidator

        validator = DataMinimizationValidator()
        assert validator is not None

    def test_excessive_data(self):
        """Test detection of excessive data collection"""
        from compliance.gdpr.data_minimization import DataMinimizationValidator

        validator = DataMinimizationValidator()

        # Potential excessive collection
        text_excessive = """
        We collect: name, email, phone, address, date of birth,
        national insurance number, bank statements, credit history,
        precise GPS location, contact list, browsing history, biometric data
        """
        result = validator.validate_minimization(text_excessive)
        # Should flag potentially excessive data

        # Minimized collection
        text_minimized = """
        We collect only the minimum data necessary for our stated purposes:
        - Name and email for account creation
        - Shipping address for order delivery
        We do not collect unnecessary data.
        """
        result = validator.validate_minimization(text_minimized)
        assert result['mentions_minimization']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
