"""
Test Helper Utilities

Common utility functions for tests including:
- Data generation
- Assertion helpers
- Mock builders
- Test utilities
"""

import json
import hashlib
import random
import string
from typing import Dict, Any, List
from datetime import datetime


class ValidationResultBuilder:
    """Builder for creating mock validation results."""

    def __init__(self):
        self.result = {
            'status': 'PASS',
            'overall_risk': 'LOW',
            'modules': {},
            'timestamp': datetime.utcnow().isoformat(),
            'violations_count': 0
        }

    def add_module(self, module_id: str, status: str = 'PASS', violations: int = 0):
        """Add a module result."""
        self.result['modules'][module_id] = {
            'status': status,
            'risk': 'LOW' if status == 'PASS' else 'HIGH',
            'violations': violations,
            'gates': {}
        }
        return self

    def add_gate_failure(self, module_id: str, gate_id: str, severity: str = 'HIGH'):
        """Add a failed gate to a module."""
        if module_id not in self.result['modules']:
            self.add_module(module_id, 'FAIL', 1)

        self.result['modules'][module_id]['gates'][gate_id] = {
            'status': 'FAIL',
            'severity': severity,
            'message': f'{gate_id} violation detected',
            'legal_source': 'Test Source'
        }
        self.result['modules'][module_id]['violations'] += 1
        self.result['violations_count'] += 1
        self.result['status'] = 'FAIL'
        self.result['overall_risk'] = 'HIGH'
        return self

    def build(self) -> Dict[str, Any]:
        """Build the validation result."""
        return self.result


class DocumentGenerator:
    """Generate test documents with specific characteristics."""

    @staticmethod
    def generate_financial_document(compliant: bool = True) -> str:
        """Generate a financial document."""
        if compliant:
            return """
            Investment Information

            Our fund invests in a diversified portfolio of assets. Past performance
            is not indicative of future results, and the value of investments may
            fluctuate.

            Risk Warning: You may get back less than you originally invested.
            This product may not be suitable for all investors.

            Please read the full prospectus and consider seeking independent
            financial advice before investing.
            """
        else:
            return """
            GUARANTEED 20% Returns!

            Our fund has NEVER lost money. Zero risk investment!
            Past performance: 20% every single year for 10 years.

            Suitable for everyone. Act now before it's too late!
            Limited time offer - invest today!
            """

    @staticmethod
    def generate_privacy_policy(compliant: bool = True) -> str:
        """Generate a privacy policy."""
        if compliant:
            return """
            Privacy Policy

            We collect personal data with your consent. You have the right to:
            - Access your data
            - Correct inaccurate information
            - Request deletion
            - Withdraw consent at any time

            We process data lawfully under GDPR Article 6(1)(a) (consent).
            Data is retained only as necessary.

            Contact our DPO at dpo@company.com
            """
        else:
            return """
            Privacy Policy

            We collect your data. By using our site you agree to everything.
            We may share data with anyone. No opt-out available.
            Data stored forever.
            """

    @staticmethod
    def generate_random_text(length: int = 1000) -> str:
        """Generate random text of specified length."""
        words = ['test', 'document', 'content', 'sample', 'data', 'information',
                 'compliance', 'legal', 'business', 'professional']
        text = []
        current_length = 0

        while current_length < length:
            word = random.choice(words)
            text.append(word)
            current_length += len(word) + 1

        return ' '.join(text)


class AssertionHelpers:
    """Helper functions for common assertions."""

    @staticmethod
    def assert_valid_validation_response(data: Dict[str, Any]):
        """Assert response is a valid validation response."""
        assert 'validation' in data
        assert 'risk' in data
        assert data['risk'] in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']

        validation = data['validation']
        assert 'status' in validation
        assert 'modules' in validation
        assert validation['status'] in ['PASS', 'WARN', 'FAIL']

    @staticmethod
    def assert_valid_correction_response(data: Dict[str, Any]):
        """Assert response is a valid correction response."""
        assert 'original' in data
        assert 'corrected' in data
        assert 'corrections' in data
        assert isinstance(data['corrections'], list)

    @staticmethod
    def assert_module_present(data: Dict[str, Any], module_id: str):
        """Assert module is present in validation results."""
        assert 'validation' in data
        assert 'modules' in data['validation']
        assert module_id in data['validation']['modules']

    @staticmethod
    def assert_has_violations(data: Dict[str, Any], module_id: str):
        """Assert module has violations."""
        module_result = data['validation']['modules'][module_id]
        assert module_result['violations'] > 0
        assert module_result['status'] == 'FAIL'

    @staticmethod
    def assert_no_violations(data: Dict[str, Any], module_id: str):
        """Assert module has no violations."""
        module_result = data['validation']['modules'][module_id]
        assert module_result['violations'] == 0
        assert module_result['status'] in ['PASS', 'WARN']


class MockResponseBuilder:
    """Build mock API responses."""

    @staticmethod
    def anthropic_response(text: str) -> Dict[str, Any]:
        """Build mock Anthropic API response."""
        return {
            'id': f'msg_{hashlib.md5(text.encode()).hexdigest()[:10]}',
            'type': 'message',
            'role': 'assistant',
            'content': [
                {
                    'type': 'text',
                    'text': text
                }
            ],
            'model': 'claude-3-5-sonnet-20241022',
            'stop_reason': 'end_turn',
            'usage': {
                'input_tokens': len(text.split()) * 2,
                'output_tokens': len(text.split())
            }
        }

    @staticmethod
    def openai_response(text: str) -> Dict[str, Any]:
        """Build mock OpenAI API response."""
        return {
            'id': f'chatcmpl_{hashlib.md5(text.encode()).hexdigest()[:10]}',
            'object': 'chat.completion',
            'created': int(datetime.utcnow().timestamp()),
            'model': 'gpt-4',
            'choices': [
                {
                    'index': 0,
                    'message': {
                        'role': 'assistant',
                        'content': text
                    },
                    'finish_reason': 'stop'
                }
            ],
            'usage': {
                'prompt_tokens': len(text.split()) * 2,
                'completion_tokens': len(text.split()),
                'total_tokens': len(text.split()) * 3
            }
        }


class TestDataGenerator:
    """Generate test data for various scenarios."""

    @staticmethod
    def generate_api_key(provider: str = 'anthropic') -> str:
        """Generate a mock API key."""
        prefixes = {
            'anthropic': 'sk-ant-',
            'openai': 'sk-',
            'gemini': 'AIza'
        }

        prefix = prefixes.get(provider, 'sk-')
        suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=40))
        return prefix + suffix

    @staticmethod
    def generate_test_payload(
        text: str = None,
        document_type: str = 'test',
        modules: List[str] = None
    ) -> Dict[str, Any]:
        """Generate a test validation payload."""
        if text is None:
            text = DocumentGenerator.generate_random_text(500)

        if modules is None:
            modules = ['gdpr_uk']

        return {
            'text': text,
            'document_type': document_type,
            'modules': modules
        }


class PerformanceHelpers:
    """Helpers for performance testing."""

    @staticmethod
    def measure_execution_time(func, *args, **kwargs):
        """Measure function execution time."""
        import time
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        return result, duration

    @staticmethod
    def assert_within_threshold(duration: float, threshold: float, label: str = 'Operation'):
        """Assert operation completed within time threshold."""
        assert duration <= threshold, \
            f"{label} took {duration:.2f}s, exceeding threshold of {threshold}s"


class ComparisonHelpers:
    """Helpers for comparing test results."""

    @staticmethod
    def compare_validation_results(result1: Dict, result2: Dict) -> Dict[str, Any]:
        """Compare two validation results."""
        differences = {
            'status_match': result1.get('status') == result2.get('status'),
            'risk_match': result1.get('overall_risk') == result2.get('overall_risk'),
            'module_count_match': len(result1.get('modules', {})) == len(result2.get('modules', {})),
            'identical': result1 == result2
        }
        return differences

    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        """Calculate simple similarity score between two texts."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 and not words2:
            return 1.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0


def create_test_database():
    """Create a test database with sample data."""
    import sqlite3
    import tempfile

    db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    conn = sqlite3.connect(db_file.name)

    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            client_id TEXT,
            document_type TEXT,
            modules TEXT,
            status TEXT,
            risk_level TEXT,
            violations INTEGER,
            metadata TEXT
        )
    """)

    conn.commit()
    return conn, db_file.name


def cleanup_test_database(db_path: str):
    """Clean up test database."""
    import os
    if os.path.exists(db_path):
        os.unlink(db_path)
