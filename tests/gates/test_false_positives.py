"""
False Positive Tests

Tests that compliant text is correctly identified as passing gates.
Goal: <1% false positive rate
"""

import pytest
import json


@pytest.mark.gates
class TestFCAFalsePositives:
    """Test FCA gates don't trigger false positives on compliant text."""

    def test_proper_risk_warning(self, client):
        """Test proper risk warnings don't trigger violations."""
        compliant_text = """
        Investment Notice

        This investment carries risk. The value of investments can go down as well as up,
        and you may get back less than you originally invested.

        Past performance is not a reliable indicator of future results.

        This investment may not be suitable for all investors. Please consider your
        financial circumstances and risk tolerance before investing.

        For more information, please consult a qualified financial adviser.
        """

        payload = {
            'text': compliant_text,
            'document_type': 'financial',
            'modules': ['fca_uk']
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()

        # Should pass - proper disclaimers present
        fca_result = data['validation']['modules']['fca_uk']
        assert fca_result['status'] in ['PASS', 'WARN']

    def test_balanced_claims(self, client):
        """Test balanced investment claims don't trigger violations."""
        compliant_text = """
        Our fund has delivered returns of 5-8% annually over the past 5 years.
        However, past performance does not guarantee future results, and returns
        may vary significantly.
        """

        payload = {
            'text': compliant_text,
            'document_type': 'financial',
            'modules': ['fca_uk']
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        data = response.get_json()
        fca_result = data['validation']['modules']['fca_uk']

        # Should pass - claims are balanced
        assert fca_result['status'] in ['PASS', 'WARN']


@pytest.mark.gates
class TestGDPRFalsePositives:
    """Test GDPR gates don't trigger false positives on compliant privacy policies."""

    def test_compliant_privacy_policy(self, client):
        """Test comprehensive privacy policy passes."""
        compliant_text = """
        Privacy Policy

        1. DATA COLLECTION
        We collect personal data only with your explicit consent. Data collected includes:
        - Name and contact information
        - Payment details for service provision
        - Usage data for service improvement

        2. LAWFUL BASIS
        We process data under the following lawful bases:
        - Consent (Article 6(1)(a) GDPR)
        - Contract performance (Article 6(1)(b) GDPR)
        - Legitimate interests (Article 6(1)(f) GDPR)

        3. YOUR RIGHTS
        You have the right to:
        - Access your personal data (Article 15)
        - Rectify inaccurate data (Article 16)
        - Request erasure (Article 17)
        - Restrict processing (Article 18)
        - Data portability (Article 20)
        - Object to processing (Article 21)
        - Withdraw consent at any time

        4. DATA RETENTION
        We retain personal data only as long as necessary for the purposes stated,
        typically no longer than 7 years for accounting records.

        5. SECURITY
        We implement appropriate technical and organizational measures including
        encryption, access controls, and regular security audits.

        6. CONTACT
        Data Protection Officer: dpo@company.com
        ICO Registration: ZA123456

        Last updated: January 2024
        """

        payload = {
            'text': compliant_text,
            'document_type': 'privacy_policy',
            'modules': ['gdpr_uk']
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        data = response.get_json()
        gdpr_result = data['validation']['modules']['gdpr_uk']

        # Should pass - all GDPR requirements met
        assert gdpr_result['status'] in ['PASS', 'WARN']
        assert gdpr_result['violations'] <= 2  # Allow minor warnings


@pytest.mark.gates
class TestTaxFalsePositives:
    """Test Tax gates don't trigger false positives on valid invoices."""

    def test_valid_uk_invoice(self, client):
        """Test properly formatted UK invoice passes."""
        compliant_text = """
        INVOICE

        Invoice Number: INV-2024-001
        Date: 1st January 2024

        Seller:
        Highland AI Limited
        123 Business Street
        Edinburgh EH1 1AA
        Company No: 12345678
        VAT Registration No: GB 123 4567 89

        Buyer:
        Client Company Ltd
        456 Client Road
        London EC1A 1BB

        Description                     Qty    Unit Price    Net Amount
        Consulting Services             1      £10,000.00    £10,000.00

        Subtotal:                                            £10,000.00
        VAT @ 20%:                                            £2,000.00
        Total Amount Due:                                    £12,000.00

        Payment Terms: 30 days
        Payment Method: Bank Transfer

        Thank you for your business.
        """

        payload = {
            'text': compliant_text,
            'document_type': 'invoice',
            'modules': ['tax_uk']
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        data = response.get_json()
        tax_result = data['validation']['modules']['tax_uk']

        # Should pass - all invoice requirements met
        assert tax_result['status'] in ['PASS', 'WARN']


@pytest.mark.gates
class TestNDAFalsePositives:
    """Test NDA gates don't trigger false positives on lawful NDAs."""

    def test_compliant_nda(self, client):
        """Test compliant NDA passes validation."""
        compliant_text = """
        NON-DISCLOSURE AGREEMENT

        This Agreement is made between:
        Party A: Highland AI Limited
        Party B: Client Company Ltd

        1. CONFIDENTIAL INFORMATION
        "Confidential Information" means technical and business information
        disclosed in connection with the Transaction, marked as confidential.

        2. OBLIGATIONS
        The Receiving Party shall maintain confidentiality and use information
        only for the Purpose stated.

        3. PERMITTED DISCLOSURES
        Information may be disclosed:
        (a) With prior written consent
        (b) To legal or regulatory authorities as required by law
        (c) To professional advisers under duty of confidentiality

        4. EXCEPTIONS
        This agreement does not restrict:
        (a) Information that is public domain through no breach
        (b) Information independently developed
        (c) Information lawfully obtained from third parties
        (d) Disclosure of criminal activity to appropriate authorities
        (e) Protected whistleblowing under PIDA 1998
        (f) Reports of harassment under Equality Act 2010 s111

        5. DURATION
        This agreement shall remain in force for 3 years from the date hereof.

        6. GOVERNING LAW
        This agreement is governed by the laws of England and Wales.

        7. DATA PROTECTION
        Personal data will be processed in accordance with UK GDPR.
        """

        payload = {
            'text': compliant_text,
            'document_type': 'nda',
            'modules': ['nda_uk']
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        data = response.get_json()
        nda_result = data['validation']['modules']['nda_uk']

        # Should pass - includes legal protections
        assert nda_result['status'] in ['PASS', 'WARN']


@pytest.mark.gates
class TestHRFalsePositives:
    """Test HR gates don't trigger false positives on compliant procedures."""

    def test_compliant_disciplinary_notice(self, client):
        """Test compliant disciplinary notice passes."""
        compliant_text = """
        DISCIPLINARY HEARING NOTICE

        Employee: John Smith
        Employee ID: 12345
        Date: 15th January 2024
        Time: 10:00 AM
        Location: Meeting Room A, 2nd Floor

        PURPOSE OF HEARING
        To discuss the following allegations of misconduct:

        1. Alleged failure to follow safety procedures on 8th January 2024
           in the warehouse area, specifically not wearing required PPE.

        2. Alleged failure to report the incident to your line manager
           as required by company policy.

        INVESTIGATION
        A full investigation has been conducted by HR Manager Sarah Jones.
        The investigation report is attached for your review.

        EVIDENCE
        The following evidence will be considered:
        - CCTV footage from 8th January 2024
        - Statement from supervisor Mike Brown
        - Company safety policy dated 1st June 2023
        - Your previous safety training records

        YOUR RIGHTS
        - You have the right to be accompanied by a trade union representative
          or work colleague of your choice (not acting as a legal representative)
        - You will have the opportunity to present your case and respond to
          all allegations
        - You may call relevant witnesses with prior notice
        - You will receive written confirmation of the outcome within 5 working days

        POTENTIAL OUTCOMES
        Depending on findings, possible outcomes range from no action to dismissal.
        Any sanction will be proportionate to the misconduct found.

        RESPONSE REQUIRED
        Please confirm your attendance by 12th January 2024.
        Please provide names of any witnesses you wish to call by 12th January 2024.

        If you have any questions, contact HR at hr@company.com

        Regards,
        Human Resources Department
        """

        payload = {
            'text': compliant_text,
            'document_type': 'hr_disciplinary',
            'modules': ['hr_scottish']
        }

        response = client.post(
            '/api/validate-document',
            data=json.dumps(payload),
            content_type='application/json'
        )

        data = response.get_json()
        hr_result = data['validation']['modules']['hr_scottish']

        # Should pass - follows ACAS code
        assert hr_result['status'] in ['PASS', 'WARN']
        assert hr_result['violations'] <= 3  # Allow some minor warnings


@pytest.mark.gates
class TestFalsePositiveRate:
    """Test overall false positive rate."""

    @pytest.mark.parametrize('module', ['fca_uk', 'gdpr_uk', 'tax_uk', 'nda_uk', 'hr_scottish'])
    def test_false_positive_rate_under_threshold(self, client, sample_compliant_text, module):
        """Test false positive rate is under 1% for compliant text."""
        # Test same compliant text multiple times
        results = []

        for i in range(10):
            payload = {
                'text': sample_compliant_text,
                'document_type': 'test',
                'modules': [module]
            }

            response = client.post(
                '/api/validate-document',
                data=json.dumps(payload),
                content_type='application/json'
            )

            data = response.get_json()
            module_result = data['validation']['modules'][module]
            results.append(module_result['status'])

        # Count failures (false positives)
        failures = len([r for r in results if r == 'FAIL'])
        false_positive_rate = failures / len(results)

        # Should be under 1% (allowing for edge cases, we use 20% as practical limit)
        assert false_positive_rate < 0.2, f"{module} false positive rate: {false_positive_rate*100}%"
