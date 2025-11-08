"""
Test Data Factories

Factory classes for generating test data using the Factory pattern.
"""

import random
import string
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional


class ValidationResultFactory:
    """Factory for creating validation result objects."""

    @staticmethod
    def create_pass_result(module_id: str = 'gdpr_uk') -> Dict[str, Any]:
        """Create a passing validation result."""
        return {
            'status': 'PASS',
            'overall_risk': 'LOW',
            'modules': {
                module_id: {
                    'status': 'PASS',
                    'risk': 'LOW',
                    'violations': 0,
                    'gates': {}
                }
            },
            'timestamp': datetime.utcnow().isoformat(),
            'violations_count': 0
        }

    @staticmethod
    def create_fail_result(
        module_id: str = 'fca_uk',
        violations: int = 3,
        severity: str = 'HIGH'
    ) -> Dict[str, Any]:
        """Create a failing validation result."""
        gates = {}
        for i in range(violations):
            gates[f'gate_{i}'] = {
                'status': 'FAIL',
                'severity': severity,
                'message': f'Violation {i + 1} detected',
                'legal_source': 'Test Regulation'
            }

        return {
            'status': 'FAIL',
            'overall_risk': severity,
            'modules': {
                module_id: {
                    'status': 'FAIL',
                    'risk': severity,
                    'violations': violations,
                    'gates': gates
                }
            },
            'timestamp': datetime.utcnow().isoformat(),
            'violations_count': violations
        }

    @staticmethod
    def create_multi_module_result(
        module_statuses: Dict[str, str]
    ) -> Dict[str, Any]:
        """Create validation result for multiple modules."""
        modules = {}
        total_violations = 0
        overall_status = 'PASS'
        max_risk = 'LOW'

        risk_levels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']

        for module_id, status in module_statuses.items():
            violations = 0 if status == 'PASS' else random.randint(1, 5)
            risk = 'LOW' if status == 'PASS' else random.choice(['MEDIUM', 'HIGH'])

            modules[module_id] = {
                'status': status,
                'risk': risk,
                'violations': violations,
                'gates': {}
            }

            total_violations += violations
            if status == 'FAIL':
                overall_status = 'FAIL'

            if risk_levels.index(risk) > risk_levels.index(max_risk):
                max_risk = risk

        return {
            'status': overall_status,
            'overall_risk': max_risk,
            'modules': modules,
            'timestamp': datetime.utcnow().isoformat(),
            'violations_count': total_violations
        }


class DocumentFactory:
    """Factory for creating test documents."""

    # Document templates
    FINANCIAL_COMPLIANT = """
    Investment Information

    Our fund provides diversified investment options. Past performance is not
    indicative of future results. The value of investments may go down as well
    as up, and you may not get back the full amount invested.

    Risk Warning: This product may not be suitable for all investors. Please
    read the Key Investor Information Document and consider seeking independent
    financial advice.

    For more information, visit our website or contact a financial adviser.
    """

    FINANCIAL_VIOLATION = """
    GUARANTEED 25% Returns Every Year!

    Our fund has NEVER lost money in 15 years. Zero risk, maximum profit!
    Past performance: 25% annually for 15 consecutive years.

    Suitable for EVERYONE regardless of experience or circumstances.
    ACT NOW - Limited spots available! Don't miss this opportunity!

    Invest today and secure your financial future!
    """

    PRIVACY_COMPLIANT = """
    Privacy Policy

    1. Data Collection
    We collect personal data with your explicit consent, including:
    - Name and contact details
    - Payment information (for transactions only)
    - Usage data (to improve our services)

    2. Legal Basis
    We process data under:
    - Consent (GDPR Article 6(1)(a))
    - Contract performance (Article 6(1)(b))
    - Legitimate interests (Article 6(1)(f))

    3. Your Rights
    You have the right to:
    - Access your personal data
    - Correct inaccurate data
    - Request deletion
    - Restrict processing
    - Data portability
    - Object to processing
    - Withdraw consent

    4. Retention
    Personal data is retained only as long as necessary, typically no more
    than 7 years for financial records.

    5. Security
    We implement appropriate technical and organizational security measures.

    6. Contact
    Data Protection Officer: dpo@company.com
    Last Updated: January 2024
    """

    PRIVACY_VIOLATION = """
    Privacy Policy

    We collect your data. By using our site you automatically agree.
    We may share your information with third parties for any purpose.
    Data is stored indefinitely on our servers.
    No opt-out available.
    """

    @classmethod
    def create_financial_document(cls, compliant: bool = True) -> str:
        """Create a financial document."""
        return cls.FINANCIAL_COMPLIANT if compliant else cls.FINANCIAL_VIOLATION

    @classmethod
    def create_privacy_policy(cls, compliant: bool = True) -> str:
        """Create a privacy policy."""
        return cls.PRIVACY_COMPLIANT if compliant else cls.PRIVACY_VIOLATION

    @staticmethod
    def create_custom_document(
        base_text: str,
        inject_violations: List[str] = None
    ) -> str:
        """Create custom document with optional violations."""
        text = base_text

        if inject_violations:
            text += "\n\n" + "\n".join(inject_violations)

        return text

    @staticmethod
    def create_large_document(size_kb: int = 100) -> str:
        """Create a large document of specified size."""
        words = ['compliance', 'legal', 'document', 'test', 'content',
                 'professional', 'business', 'information', 'data']

        target_size = size_kb * 1024
        text_parts = []
        current_size = 0

        while current_size < target_size:
            sentence = ' '.join(random.choices(words, k=10)) + '. '
            text_parts.append(sentence)
            current_size += len(sentence)

        return ''.join(text_parts)


class CorrectionFactory:
    """Factory for creating correction objects."""

    @staticmethod
    def create_correction(
        pattern: str,
        before: str,
        after: str,
        reason: str = 'Compliance requirement'
    ) -> Dict[str, Any]:
        """Create a single correction object."""
        return {
            'pattern': pattern,
            'before': before,
            'after': after,
            'reason': reason,
            'strategy': 'regex',
            'timestamp': datetime.utcnow().isoformat()
        }

    @staticmethod
    def create_correction_result(
        original: str,
        corrected: str,
        corrections: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a complete correction result."""
        if corrections is None:
            corrections = []

        return {
            'original': original,
            'corrected': corrected,
            'corrections': corrections,
            'correction_count': len(corrections),
            'deterministic_hash': 'test_hash_' + str(hash(corrected))[:16]
        }


class AuditLogFactory:
    """Factory for creating audit log entries."""

    @staticmethod
    def create_entry(
        client_id: str = None,
        document_type: str = 'test',
        modules: List[str] = None,
        status: str = 'PASS',
        risk_level: str = 'LOW',
        violations: int = 0
    ) -> Dict[str, Any]:
        """Create an audit log entry."""
        if client_id is None:
            client_id = f'client_{random.randint(1000, 9999)}'

        if modules is None:
            modules = ['gdpr_uk']

        return {
            'timestamp': datetime.utcnow().isoformat(),
            'client_id': client_id,
            'document_type': document_type,
            'modules': ','.join(modules),
            'status': status,
            'risk_level': risk_level,
            'violations': violations,
            'metadata': '{}'
        }

    @staticmethod
    def create_batch(count: int = 10) -> List[Dict[str, Any]]:
        """Create a batch of audit log entries."""
        entries = []
        statuses = ['PASS', 'PASS', 'PASS', 'WARN', 'FAIL']  # 60% pass rate
        risk_levels = ['LOW', 'LOW', 'MEDIUM', 'HIGH']

        for i in range(count):
            entries.append(AuditLogFactory.create_entry(
                status=random.choice(statuses),
                risk_level=random.choice(risk_levels),
                violations=random.randint(0, 5)
            ))

        return entries


class APIPayloadFactory:
    """Factory for creating API request payloads."""

    @staticmethod
    def create_validation_payload(
        text: str = None,
        document_type: str = 'test',
        modules: List[str] = None
    ) -> Dict[str, Any]:
        """Create validation API payload."""
        if text is None:
            text = DocumentFactory.create_financial_document(compliant=True)

        if modules is None:
            modules = ['gdpr_uk']

        return {
            'text': text,
            'document_type': document_type,
            'modules': modules
        }

    @staticmethod
    def create_correction_payload(
        text: str = None,
        validation_results: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create correction API payload."""
        if text is None:
            text = DocumentFactory.create_financial_document(compliant=False)

        if validation_results is None:
            validation_results = ValidationResultFactory.create_fail_result()

        return {
            'text': text,
            'validation_results': validation_results
        }

    @staticmethod
    def create_synthesis_payload(
        base_text: str = '',
        validation: Dict[str, Any] = None,
        modules: List[str] = None
    ) -> Dict[str, Any]:
        """Create synthesis API payload."""
        if validation is None:
            validation = ValidationResultFactory.create_fail_result()

        if modules is None:
            modules = ['fca_uk']

        return {
            'base_text': base_text,
            'validation': validation,
            'modules': modules,
            'context': {}
        }


class UserFactory:
    """Factory for creating test users/clients."""

    @staticmethod
    def create_client_id() -> str:
        """Create a random client ID."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    @staticmethod
    def create_api_key(provider: str = 'anthropic') -> str:
        """Create a mock API key."""
        prefixes = {
            'anthropic': 'sk-ant-',
            'openai': 'sk-',
            'gemini': 'AIza'
        }

        prefix = prefixes.get(provider, 'sk-')
        suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=48))
        return prefix + suffix


class PerformanceDataFactory:
    """Factory for creating performance test data."""

    @staticmethod
    def create_benchmark_data() -> Dict[str, float]:
        """Create benchmark thresholds."""
        return {
            'api_response': 2.0,
            'validation': 5.0,
            'correction': 10.0,
            'gate_check': 0.5,
            'synthesis': 15.0
        }

    @staticmethod
    def create_load_test_scenario(
        name: str,
        users: int,
        duration_seconds: int,
        ramp_up_seconds: int = 10
    ) -> Dict[str, Any]:
        """Create load test scenario configuration."""
        return {
            'name': name,
            'users': users,
            'duration': duration_seconds,
            'ramp_up': ramp_up_seconds,
            'think_time': random.uniform(0.5, 2.0)
        }
