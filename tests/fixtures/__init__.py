"""
Test Fixtures and Sample Data for LOKI Tests

This module provides shared fixtures for test data generation,
mock objects, and test utilities.
"""

import json
from pathlib import Path
from typing import Dict, Any


class SampleDocuments:
    """Collection of sample documents for testing."""

    @staticmethod
    def employment_contract() -> Dict[str, Any]:
        """Sample employment contract."""
        return {
            "title": "Employment Contract",
            "content": """
            EMPLOYMENT AGREEMENT

            This agreement is entered into on 1st January 2024 between:

            EMPLOYER: Highland AI Ltd
            EMPLOYEE: John Smith

            1. POSITION AND DUTIES
            Employee will hold the position of Senior Compliance Officer
            and will perform all duties as assigned by the Employer.

            2. COMMENCEMENT DATE
            Employment shall commence on 15th January 2024.

            3. REMUNERATION
            The Employee shall receive an annual salary of £60,000 payable
            in 12 equal monthly instalments.

            4. WORKING HOURS
            The Employee shall work 40 hours per week, typically Monday to Friday,
            9:00 AM to 5:00 PM with one hour lunch break.

            5. HOLIDAY ENTITLEMENT
            The Employee is entitled to 25 days paid holiday per annum,
            plus statutory bank holidays.

            6. NOTICE PERIOD
            Either party may terminate this agreement by providing 3 months
            written notice.

            7. CONFIDENTIALITY
            The Employee shall maintain confidentiality of all business information.

            Signed: _________________
            Date: 1st January 2024
            """,
            "metadata": {
                "jurisdiction": "UK",
                "document_type": "employment",
                "industry": "Financial Services",
                "status": "executed",
            },
        }

    @staticmethod
    def gdpr_privacy_policy() -> Dict[str, Any]:
        """Sample GDPR-compliant privacy policy."""
        return {
            "title": "Privacy Policy",
            "content": """
            PRIVACY POLICY

            Last Updated: 1st January 2024

            1. INTRODUCTION
            Highland AI Ltd (\"we\", \"us\", \"our\") is committed to protecting your privacy.

            2. DATA WE COLLECT
            We collect the following types of personal data:
            - Name and email address
            - Company and position
            - Usage analytics and preferences
            - Payment information (when applicable)

            3. LEGAL BASIS
            We process your personal data based on:
            - Your explicit consent
            - Legitimate business interests
            - Contractual obligations
            - Legal compliance

            4. DATA RETENTION
            We retain personal data only as long as necessary for the stated purposes:
            - Customer data: Until account closure + 7 years for tax purposes
            - Marketing data: Until withdrawal of consent
            - Behavioral data: 12 months maximum

            5. YOUR RIGHTS
            Under GDPR, you have the right to:
            - Access your personal data
            - Correct inaccurate data
            - Request deletion
            - Restrict processing
            - Data portability
            - Object to processing

            6. SECURITY
            We implement appropriate technical and organizational security measures
            including encryption, access controls, and regular security audits.

            7. DATA PROTECTION OFFICER
            For privacy inquiries, contact our DPO at: dpo@highland-ai.com

            8. GOVERNING LAW
            This policy is governed by UK GDPR and UK data protection law.
            """,
            "metadata": {
                "jurisdiction": "UK",
                "document_type": "privacy_policy",
                "compliance": "GDPR",
                "status": "current",
            },
        }

    @staticmethod
    def financial_disclosure() -> Dict[str, Any]:
        """Sample financial service disclosure."""
        return {
            "title": "Investment Service Disclosure",
            "content": """
            FINANCIAL SERVICE DISCLOSURE

            1. SERVICE DESCRIPTION
            Highland AI provides investment advisory services to retail and professional clients.

            2. CLIENT CLASSIFICATION
            This service is provided to:
            - Retail clients
            - Professional clients

            3. RISK WARNINGS
            IMPORTANT NOTICE:
            - Investments can go down as well as up in value
            - You may not recover the amount you invest
            - Past performance is not a guide to future performance
            - Funds are not protected by FSCS if the firm is insolvent

            4. FEES AND CHARGES
            Annual management fee: 0.5% of assets under management
            Trading costs vary by market

            5. FCA REGULATION
            Highland AI Ltd is authorized and regulated by the Financial Conduct Authority
            under reference number: 123456

            6. COMPLAINTS PROCEDURE
            If you have a complaint, contact us at:
            Email: complaints@highland-ai.com
            Phone: +44 (0)20 7123 4567

            7. CONFLICT OF INTEREST POLICY
            We maintain a conflict of interest policy available on request.
            """,
            "metadata": {
                "jurisdiction": "UK",
                "document_type": "financial_disclosure",
                "regulator": "FCA",
                "client_type": "retail",
            },
        }

    @staticmethod
    def tax_invoice() -> Dict[str, Any]:
        """Sample UK tax invoice."""
        return {
            "title": "VAT Invoice",
            "content": """
            INVOICE

            Invoice Number: INV-2024-001
            Invoice Date: 1st January 2024
            Due Date: 31st January 2024

            FROM:
            Highland AI Ltd
            123 Business Park
            London, EC1A 1BB
            United Kingdom
            Company Number: 12345678
            VAT Number: GB 123456789

            TO:
            Acme Corporation
            456 Corporate Avenue
            Manchester, M1 1AA
            United Kingdom

            DESCRIPTION OF SERVICES:
            Consulting services for Q1 2024

            AMOUNT DETAILS:
            Net Amount: £5,000.00
            VAT (20%): £1,000.00
            Total Due: £6,000.00

            PAYMENT TERMS:
            Payment is due within 30 days of invoice date.

            BANK DETAILS:
            Bank: Highland Bank
            Sort Code: 12-34-56
            Account: 98765432
            """,
            "metadata": {
                "jurisdiction": "UK",
                "document_type": "invoice",
                "tax_type": "VAT",
                "amount": 6000.00,
            },
        }

    @staticmethod
    def nda_agreement() -> Dict[str, Any]:
        """Sample Non-Disclosure Agreement."""
        return {
            "title": "Non-Disclosure Agreement",
            "content": """
            NON-DISCLOSURE AGREEMENT

            This Non-Disclosure Agreement (\"Agreement\") is entered into on
            1st January 2024 between:

            DISCLOSING PARTY: Highland AI Ltd
            RECEIVING PARTY: Acme Corporation

            1. DEFINITION OF CONFIDENTIAL INFORMATION
            \"Confidential Information\" means all business, technical, and financial
            information disclosed by the Disclosing Party in any form.

            2. OBLIGATIONS OF RECEIVING PARTY
            The Receiving Party shall:
            - Not disclose Confidential Information without prior written consent
            - Use Confidential Information solely for evaluation purposes
            - Protect Confidential Information with reasonable security measures
            - Limit access to employees with a need to know

            3. EXCLUSIONS
            Confidential Information does not include information that:
            - Is already in the public domain
            - Is rightfully obtained from third parties without confidentiality obligations
            - Is independently developed
            - Is required to be disclosed by law

            4. DURATION
            This Agreement remains in effect for a period of 5 years from signature
            unless earlier terminated by either party.

            5. REMEDIES
            The Receiving Party acknowledges that breach may cause irreparable harm
            for which monetary damages are inadequate.

            6. GOVERNING LAW
            This Agreement is governed by the laws of England and Wales.

            SIGNATURES:

            Disclosing Party: _________________
            Date: _________________

            Receiving Party: _________________
            Date: _________________
            """,
            "metadata": {
                "jurisdiction": "UK",
                "document_type": "nda",
                "duration_years": 5,
                "status": "executed",
            },
        }


class SampleData:
    """Collection of sample data for testing."""

    @staticmethod
    def validation_request() -> Dict[str, Any]:
        """Sample validation request."""
        return {
            "title": "Test Document",
            "content": "This is a test document for validation.",
            "metadata": {"jurisdiction": "UK"},
        }

    @staticmethod
    def correction_request() -> Dict[str, Any]:
        """Sample correction request."""
        return {
            "title": "Test Document",
            "content": "Document with potential issues needing correction.",
            "metadata": {"jurisdiction": "UK"},
            "include_suggestions": True,
        }

    @staticmethod
    def batch_request() -> Dict[str, Any]:
        """Sample batch validation request."""
        return {
            "documents": [
                SampleDocuments.employment_contract(),
                SampleDocuments.gdpr_privacy_policy(),
                SampleDocuments.financial_disclosure(),
            ]
        }


def load_fixture(fixture_name: str) -> Dict[str, Any]:
    """Load fixture by name."""
    fixtures = {
        "employment_contract": SampleDocuments.employment_contract,
        "gdpr_privacy_policy": SampleDocuments.gdpr_privacy_policy,
        "financial_disclosure": SampleDocuments.financial_disclosure,
        "tax_invoice": SampleDocuments.tax_invoice,
        "nda_agreement": SampleDocuments.nda_agreement,
        "validation_request": SampleData.validation_request,
        "correction_request": SampleData.correction_request,
        "batch_request": SampleData.batch_request,
    }

    if fixture_name not in fixtures:
        raise ValueError(f"Unknown fixture: {fixture_name}")

    return fixtures[fixture_name]()
