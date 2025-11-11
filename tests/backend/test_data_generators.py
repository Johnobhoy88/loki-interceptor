"""
Test data generators for comprehensive testing.

Provides factories and generators for creating test documents,
violations, validation results, and other test data with realistic
variations and edge cases.
"""

import pytest
import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
import json


class DocumentType(Enum):
    """Document types for testing."""
    INVESTMENT_PROSPECTUS = "investment_prospectus"
    PRIVACY_POLICY = "privacy_policy"
    INVOICE = "invoice"
    NDA = "nda"
    HR_POLICY = "hr_policy"
    CONTRACT = "contract"


class RiskLevel(Enum):
    """Risk levels for violations."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ComplianceModules(Enum):
    """Available compliance modules."""
    FCA_UK = "fca_uk"
    GDPR_UK = "gdpr_uk"
    TAX_UK = "tax_uk"
    NDA_UK = "nda_uk"
    HR_SCOTTISH = "hr_scottish"


class DocumentGenerator:
    """Generate realistic test documents."""

    @staticmethod
    def generate_compliant_investment_document() -> str:
        """Generate a compliant investment document."""
        return """
        INVESTMENT PROSPECTUS

        Risk Disclosure
        This investment carries market risk. Past performance is not indicative
        of future results. The value of your investment may go down as well as up.

        Key Features
        - Diversified portfolio management
        - Professional fund managers
        - Regular performance reporting
        - Flexible redemption terms

        Risk Profile: Medium
        Suitable for: Investors with medium to long-term investment horizon
        who can tolerate market volatility.

        Costs and Charges
        Annual management fee: 1.5%
        Performance fee: 20% of outperformance above benchmark

        Fund Performance
        5-year average return: 8.2% (before fees)
        Note: Past performance should not be relied upon as a guide to future performance.

        For more information, contact us at info@investmentfund.com
        """

    @staticmethod
    def generate_non_compliant_investment_document() -> str:
        """Generate non-compliant investment document."""
        return """
        GUARANTEED INVESTMENT FUND

        GUARANTEED 15% ANNUAL RETURNS!

        This is a risk-free investment. We have NEVER lost money.
        Guaranteed to double your money in 5 years!

        Suitable for all investors, regardless of experience or risk tolerance.
        ZERO RISK - MAXIMUM PROFIT!

        Join now - limited time offer! Only 100 slots available!
        Act immediately or miss out!

        Send your money today to secure your position.
        """

    @staticmethod
    def generate_compliant_privacy_policy() -> str:
        """Generate a compliant privacy policy."""
        return """
        PRIVACY POLICY

        Last Updated: January 2024

        1. Data Collection
        We collect personal data only with your explicit consent. We collect:
        - Name and contact information
        - Payment information
        - Service usage data

        2. Legal Basis
        We process your data under:
        - Your explicit consent
        - Contractual necessity
        - Legitimate interests

        3. Your Rights
        You have the right to:
        - Access your personal data
        - Correct inaccurate data
        - Request erasure ("right to be forgotten")
        - Data portability
        - Withdraw consent at any time

        4. Data Retention
        We retain personal data only for as long as necessary:
        - Customer data: Duration of relationship + 6 years (legal requirement)
        - Website analytics: 12 months maximum
        - Marketing data: Until consent withdrawal

        5. Data Security
        We implement:
        - Encryption in transit (TLS 1.3)
        - Encryption at rest (AES-256)
        - Access controls and authentication
        - Regular security audits
        - Staff training on data protection

        6. Third Parties
        We only share data with:
        - Service providers (processors)
        - Legal authorities (when required)
        - You don't share it with other organizations without consent

        7. Contact
        Data Protection Officer: dpo@company.com
        """

    @staticmethod
    def generate_non_compliant_privacy_policy() -> str:
        """Generate non-compliant privacy policy."""
        return """
        PRIVACY POLICY

        We collect your personal data. By using our website, you agree to this.
        We may share your data with anyone for any purpose.
        Your data is stored on our servers for as long as we want.
        We don't delete your data. Ever.
        """

    @staticmethod
    def generate_compliant_invoice() -> str:
        """Generate a compliant invoice."""
        return """
        INVOICE

        Invoice Number: INV-2024-00123
        Date: 15 January 2024
        Due Date: 15 February 2024

        From:
        Highland AI Ltd
        Company Number: 12345678
        VAT Number: GB123456789
        Email: billing@highlandai.com

        Bill To:
        Acme Corporation
        123 Business Street
        London, UK

        Description of Services | Quantity | Rate | Amount
        Cloud Compliance Platform | 1 | £5,000.00 | £5,000.00
        Professional Services | 10 hours | £150.00 | £1,500.00

        Subtotal: £6,500.00
        VAT (20%): £1,300.00
        Total Due: £7,800.00

        Payment Terms: Net 30 days
        Bank Details: [Account information]
        """

    @staticmethod
    def generate_compliant_nda() -> str:
        """Generate a compliant NDA."""
        return """
        NON-DISCLOSURE AGREEMENT

        Between Party A and Party B

        1. Definition of Confidential Information
        "Confidential Information" means any business, technical, or financial
        information disclosed by one party to the other.

        2. Obligations of Receiving Party
        The Receiving Party shall:
        - Not disclose Confidential Information without prior written consent
        - Protect the information with reasonable security measures
        - Use the information only for agreed purposes

        3. Exclusions
        Confidential Information does not include:
        - Information already in the public domain
        - Information rightfully obtained from third parties
        - Information independently developed

        4. Duration
        This agreement remains in effect for 5 years from the date of disclosure.

        5. Governing Law
        This agreement is governed by English law and courts.

        6. Entire Agreement
        This constitutes the entire agreement between parties.
        """


class ViolationGenerator:
    """Generate realistic compliance violations."""

    FCA_GATES = [
        "misleading_claims",
        "fair_clear_not_misleading",
        "risk_warning",
        "target_market",
        "inducements",
        "conflict_of_interest",
        "record_keeping",
    ]

    GDPR_GATES = [
        "data_retention",
        "consent_management",
        "data_minimization",
        "accuracy",
        "automated_decisions",
        "breach_notification",
    ]

    TAX_GATES = [
        "vat_calculation",
        "vat_disclosure",
        "invoice_requirements",
        "record_keeping",
    ]

    @staticmethod
    def generate_fca_violation(severity: str = "HIGH") -> Dict[str, Any]:
        """Generate FCA compliance violation."""
        return {
            "module": "fca_uk",
            "gate": random.choice(ViolationGenerator.FCA_GATES),
            "severity": severity,
            "message": f"FCA compliance violation detected",
            "legal_source": "COBS 4.2.1",
            "details": "Example violation for testing"
        }

    @staticmethod
    def generate_gdpr_violation(severity: str = "MEDIUM") -> Dict[str, Any]:
        """Generate GDPR compliance violation."""
        return {
            "module": "gdpr_uk",
            "gate": random.choice(ViolationGenerator.GDPR_GATES),
            "severity": severity,
            "message": f"GDPR compliance violation detected",
            "legal_source": "GDPR Article 5",
            "details": "Example violation for testing"
        }

    @staticmethod
    def generate_tax_violation(severity: str = "MEDIUM") -> Dict[str, Any]:
        """Generate tax compliance violation."""
        return {
            "module": "tax_uk",
            "gate": random.choice(ViolationGenerator.TAX_GATES),
            "severity": severity,
            "message": f"Tax compliance violation detected",
            "legal_source": "VAT Rules",
            "details": "Example violation for testing"
        }

    @staticmethod
    def generate_random_violation() -> Dict[str, Any]:
        """Generate random compliance violation."""
        modules = [
            (ViolationGenerator.generate_fca_violation, 0.4),
            (ViolationGenerator.generate_gdpr_violation, 0.35),
            (ViolationGenerator.generate_tax_violation, 0.25),
        ]

        rand = random.random()
        cumulative = 0
        for generator, weight in modules:
            cumulative += weight
            if rand <= cumulative:
                return generator()

        return ViolationGenerator.generate_fca_violation()

    @staticmethod
    def generate_violation_set(count: int = 3) -> List[Dict[str, Any]]:
        """Generate a set of violations."""
        return [ViolationGenerator.generate_random_violation() for _ in range(count)]


class ValidationResultGenerator:
    """Generate validation results."""

    @staticmethod
    def generate_pass_result() -> Dict[str, Any]:
        """Generate a PASS validation result."""
        return {
            "status": "PASS",
            "overall_risk": "LOW",
            "modules": {
                "fca_uk": {
                    "status": "PASS",
                    "risk": "LOW",
                    "violations": 0,
                    "gates": {}
                },
                "gdpr_uk": {
                    "status": "PASS",
                    "risk": "LOW",
                    "violations": 0,
                    "gates": {}
                },
                "tax_uk": {
                    "status": "PASS",
                    "risk": "LOW",
                    "violations": 0,
                    "gates": {}
                }
            },
            "timestamp": datetime.utcnow().isoformat(),
            "violations_count": 0,
            "processing_time_ms": random.randint(100, 500)
        }

    @staticmethod
    def generate_fail_result() -> Dict[str, Any]:
        """Generate a FAIL validation result."""
        return {
            "status": "FAIL",
            "overall_risk": "HIGH",
            "modules": {
                "fca_uk": {
                    "status": "FAIL",
                    "risk": "CRITICAL",
                    "violations": 3,
                    "gates": {
                        "misleading_claims": {
                            "status": "FAIL",
                            "severity": "CRITICAL",
                            "message": "Contains misleading claims",
                            "legal_source": "COBS 4.2.1"
                        },
                        "risk_warning": {
                            "status": "FAIL",
                            "severity": "HIGH",
                            "message": "Missing risk warning",
                            "legal_source": "COBS 2.1"
                        }
                    }
                },
                "gdpr_uk": {
                    "status": "PASS",
                    "risk": "LOW",
                    "violations": 0,
                    "gates": {}
                }
            },
            "timestamp": datetime.utcnow().isoformat(),
            "violations_count": 3,
            "processing_time_ms": random.randint(200, 800)
        }

    @staticmethod
    def generate_partial_result() -> Dict[str, Any]:
        """Generate a PARTIAL (some failures) validation result."""
        return {
            "status": "FAIL",
            "overall_risk": "MEDIUM",
            "modules": {
                "fca_uk": {
                    "status": "PASS",
                    "risk": "LOW",
                    "violations": 0,
                    "gates": {}
                },
                "gdpr_uk": {
                    "status": "FAIL",
                    "risk": "MEDIUM",
                    "violations": 1,
                    "gates": {
                        "data_retention": {
                            "status": "FAIL",
                            "severity": "MEDIUM",
                            "message": "Missing data retention period",
                            "legal_source": "GDPR Article 5"
                        }
                    }
                }
            },
            "timestamp": datetime.utcnow().isoformat(),
            "violations_count": 1,
            "processing_time_ms": random.randint(150, 600)
        }


class ClientFactory:
    """Factory for creating test client data."""

    @staticmethod
    def generate_client_id() -> str:
        """Generate a random client ID."""
        return f"client_{random.randint(1000, 9999)}"

    @staticmethod
    def generate_api_key() -> str:
        """Generate a test API key."""
        return f"sk_test_{random.choice(string.ascii_letters + string.digits)}"

    @staticmethod
    def generate_client_data() -> Dict[str, Any]:
        """Generate complete client data."""
        return {
            "client_id": ClientFactory.generate_client_id(),
            "api_key": ClientFactory.generate_api_key(),
            "name": f"Test Organization {random.randint(1, 1000)}",
            "email": f"contact@testorg{random.randint(1, 1000)}.com",
            "created_at": datetime.utcnow().isoformat(),
            "subscription": random.choice(["basic", "professional", "enterprise"])
        }


class AuditEventGenerator:
    """Generate audit log events."""

    @staticmethod
    def generate_validation_event() -> Dict[str, Any]:
        """Generate validation audit event."""
        return {
            "event_type": "validation_check",
            "client_id": ClientFactory.generate_client_id(),
            "document_id": f"doc_{random.randint(10000, 99999)}",
            "modules": random.sample([m.value for m in ComplianceModules], k=2),
            "status": random.choice(["PASS", "FAIL"]),
            "risk_level": random.choice(["LOW", "MEDIUM", "HIGH", "CRITICAL"]),
            "violations": random.randint(0, 5),
            "timestamp": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def generate_correction_event() -> Dict[str, Any]:
        """Generate correction audit event."""
        return {
            "event_type": "correction_applied",
            "client_id": ClientFactory.generate_client_id(),
            "document_id": f"doc_{random.randint(10000, 99999)}",
            "module": random.choice([m.value for m in ComplianceModules]),
            "violations_fixed": random.randint(1, 5),
            "timestamp": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def generate_api_call_event() -> Dict[str, Any]:
        """Generate API call audit event."""
        return {
            "event_type": "api_call",
            "client_id": ClientFactory.generate_client_id(),
            "endpoint": random.choice([
                "/api/validate",
                "/api/correct",
                "/api/check",
                "/api/export"
            ]),
            "method": random.choice(["GET", "POST", "PUT"]),
            "status_code": random.choice([200, 400, 401, 429, 500]),
            "response_time_ms": random.randint(10, 5000),
            "timestamp": datetime.utcnow().isoformat(),
        }


class ParametrizedDataGenerator:
    """Generate parametrized test data."""

    @staticmethod
    def get_severity_levels() -> List[str]:
        """Get all severity levels."""
        return ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    @staticmethod
    def get_risk_levels() -> List[str]:
        """Get all risk levels."""
        return ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    @staticmethod
    def get_compliance_modules() -> List[str]:
        """Get all compliance module names."""
        return [m.value for m in ComplianceModules]

    @staticmethod
    def get_document_types() -> List[str]:
        """Get all document types."""
        return [d.value for d in DocumentType]

    @staticmethod
    def get_status_codes() -> List[int]:
        """Get common HTTP status codes."""
        return [200, 201, 400, 401, 403, 404, 429, 500, 502, 503]

    @staticmethod
    def get_module_combinations() -> List[List[str]]:
        """Get various module combinations."""
        modules = ParametrizedDataGenerator.get_compliance_modules()
        combinations = [
            [modules[0]],
            [modules[1]],
            modules[:2],
            modules[:3],
            modules,
        ]
        return combinations


# Pytest fixtures

@pytest.fixture
def document_generator():
    """Provide document generator."""
    return DocumentGenerator()


@pytest.fixture
def violation_generator():
    """Provide violation generator."""
    return ViolationGenerator()


@pytest.fixture
def validation_result_generator():
    """Provide validation result generator."""
    return ValidationResultGenerator()


@pytest.fixture
def client_factory():
    """Provide client factory."""
    return ClientFactory()


@pytest.fixture
def audit_event_generator():
    """Provide audit event generator."""
    return AuditEventGenerator()


@pytest.fixture
def compliant_investment_doc():
    """Provide a compliant investment document."""
    return DocumentGenerator.generate_compliant_investment_document()


@pytest.fixture
def non_compliant_investment_doc():
    """Provide a non-compliant investment document."""
    return DocumentGenerator.generate_non_compliant_investment_document()


@pytest.fixture
def compliant_privacy_policy():
    """Provide a compliant privacy policy."""
    return DocumentGenerator.generate_compliant_privacy_policy()


@pytest.fixture
def non_compliant_privacy_policy():
    """Provide a non-compliant privacy policy."""
    return DocumentGenerator.generate_non_compliant_privacy_policy()


@pytest.fixture
def fca_violation():
    """Provide an FCA violation."""
    return ViolationGenerator.generate_fca_violation()


@pytest.fixture
def gdpr_violation():
    """Provide a GDPR violation."""
    return ViolationGenerator.generate_gdpr_violation()


@pytest.fixture
def pass_validation_result():
    """Provide a PASS validation result."""
    return ValidationResultGenerator.generate_pass_result()


@pytest.fixture
def fail_validation_result():
    """Provide a FAIL validation result."""
    return ValidationResultGenerator.generate_fail_result()
