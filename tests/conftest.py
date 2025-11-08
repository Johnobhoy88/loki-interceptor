"""
Pytest Configuration and Shared Fixtures for LOKI Compliance Testing Framework

This module provides comprehensive fixtures for:
- Database setup and teardown
- Flask test client
- Mock API responses
- Test data generators
- Authentication mocks
- Performance monitoring
"""

import os
import sys
import pytest
import json
import tempfile
import sqlite3
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / 'backend'))

from backend.server import app as flask_app
from backend.core.async_engine import AsyncLOKIEngine
from backend.core.providers import ProviderRouter
from backend.core.security import SecurityManager, RateLimiter
from backend.core.audit_log import AuditLogger
from backend.core.cache import ValidationCache
from backend.core.corrector import DocumentCorrector


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "security: marks tests as security-focused"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance benchmarks"
    )
    config.addinivalue_line(
        "markers", "api: marks tests as API endpoint tests"
    )
    config.addinivalue_line(
        "markers", "gates: marks tests for gate accuracy"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test paths."""
    for item in items:
        # Add markers based on test file location
        if "security" in str(item.fspath):
            item.add_marker(pytest.mark.security)
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        if "api" in str(item.fspath):
            item.add_marker(pytest.mark.api)
        if "gates" in str(item.fspath):
            item.add_marker(pytest.mark.gates)
        if "load" in str(item.fspath):
            item.add_marker(pytest.mark.slow)
            item.add_marker(pytest.mark.performance)


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def temp_db_path():
    """Create a temporary database file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    yield db_path
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture(scope="function")
def test_db(temp_db_path):
    """Provide a fresh database connection for each test."""
    conn = sqlite3.connect(temp_db_path)
    conn.row_factory = sqlite3.Row

    # Create test tables
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

    yield conn

    # Cleanup
    conn.close()
    cursor.execute("DELETE FROM audit_log")
    conn.commit()


# ============================================================================
# FLASK APPLICATION FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def app():
    """Create Flask application for testing."""
    flask_app.config.update({
        "TESTING": True,
        "DEBUG": False,
        "SERVER_NAME": "localhost:5002",
        "APPLICATION_ROOT": "/",
        "PREFERRED_URL_SCHEME": "http",
        "MAX_CONTENT_LENGTH": 10 * 1024 * 1024,  # 10MB
    })

    yield flask_app


@pytest.fixture(scope="function")
def client(app):
    """Create Flask test client for API testing."""
    with app.test_client() as client:
        yield client


@pytest.fixture(scope="function")
def authenticated_client(client):
    """Create authenticated test client with valid API key."""
    client.environ_base['HTTP_X_API_KEY'] = 'test-api-key-12345'
    return client


# ============================================================================
# LOKI ENGINE FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def engine():
    """Create and configure LOKI engine for testing."""
    test_engine = AsyncLOKIEngine(max_workers=2)
    test_engine.load_module('hr_scottish')
    test_engine.load_module('gdpr_uk')
    test_engine.load_module('nda_uk')
    test_engine.load_module('tax_uk')
    test_engine.load_module('fca_uk')
    return test_engine


@pytest.fixture(scope="function")
def corrector():
    """Create document corrector instance."""
    return DocumentCorrector()


@pytest.fixture(scope="function")
def cache():
    """Create fresh cache for each test."""
    return ValidationCache(max_size=100, ttl_seconds=300)


# ============================================================================
# SECURITY FIXTURES
# ============================================================================

@pytest.fixture(scope="function")
def security_manager():
    """Create security manager instance."""
    return SecurityManager()


@pytest.fixture(scope="function")
def rate_limiter():
    """Create rate limiter instance."""
    limiter = RateLimiter()
    # Clear any existing limits
    limiter.clients.clear()
    return limiter


@pytest.fixture(scope="function")
def audit_logger(test_db):
    """Create audit logger with test database."""
    logger = AuditLogger()
    # Override database path for testing
    logger.db_path = test_db
    return logger


# ============================================================================
# MOCK FIXTURES
# ============================================================================

@pytest.fixture
def mock_anthropic_response():
    """Mock successful Anthropic API response."""
    return {
        "id": "msg_test123",
        "type": "message",
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": "This is a test response that complies with all regulations."
            }
        ],
        "model": "claude-3-5-sonnet-20241022",
        "stop_reason": "end_turn",
        "usage": {
            "input_tokens": 100,
            "output_tokens": 50
        }
    }


@pytest.fixture
def mock_openai_response():
    """Mock successful OpenAI API response."""
    return {
        "id": "chatcmpl-test123",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "This is a compliant test response."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        }
    }


@pytest.fixture
def mock_validation_pass():
    """Mock validation result with PASS status."""
    return {
        "status": "PASS",
        "overall_risk": "LOW",
        "modules": {
            "fca_uk": {
                "status": "PASS",
                "risk": "LOW",
                "violations": 0,
                "gates": {}
            }
        },
        "timestamp": datetime.utcnow().isoformat(),
        "violations_count": 0
    }


@pytest.fixture
def mock_validation_fail():
    """Mock validation result with FAIL status."""
    return {
        "status": "FAIL",
        "overall_risk": "HIGH",
        "modules": {
            "fca_uk": {
                "status": "FAIL",
                "risk": "HIGH",
                "violations": 3,
                "gates": {
                    "misleading_claims": {
                        "status": "FAIL",
                        "severity": "CRITICAL",
                        "message": "Document contains misleading claims",
                        "legal_source": "COBS 4.2.1"
                    }
                }
            }
        },
        "timestamp": datetime.utcnow().isoformat(),
        "violations_count": 3
    }


# ============================================================================
# TEST DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_compliant_text():
    """Sample text that should pass all gates."""
    return """
    Privacy Notice

    We collect personal data only with your explicit consent. You have the right to:
    - Access your data
    - Correct inaccurate data
    - Request deletion
    - Withdraw consent at any time

    We implement appropriate technical and organizational security measures.
    Data is retained only as long as necessary for the stated purposes.

    For questions, contact our Data Protection Officer at dpo@example.com
    """


@pytest.fixture
def sample_violation_text():
    """Sample text that should fail multiple gates."""
    return """
    GUARANTEED 15% ANNUAL RETURNS!

    Our investment fund has NEVER lost money. Zero risk, maximum profit!
    Act now - limited time offer. No experience needed.

    Past performance: 15% every single year for 10 years.
    Suitable for all investors regardless of circumstances.

    Send money immediately to secure your position.
    """


@pytest.fixture
def sample_gdpr_violation():
    """Sample GDPR privacy policy with violations."""
    return """
    Privacy Policy

    We collect your data. By using our site you agree.
    We may share with third parties for various purposes.
    Data is stored indefinitely.
    """


@pytest.fixture
def sample_tax_document():
    """Sample UK tax document."""
    return """
    INVOICE #INV-2024-001

    Date: 01/01/2024

    From: Highland AI Ltd
    Company No: 12345678
    VAT No: GB123456789

    To: Client Ltd

    Description: Consulting Services
    Net Amount: £1,000.00
    VAT (20%): £200.00
    Total: £1,200.00

    Payment Terms: 30 days
    """


@pytest.fixture
def sample_nda_document():
    """Sample NDA document."""
    return """
    NON-DISCLOSURE AGREEMENT

    Between Party A and Party B

    1. DEFINITION OF CONFIDENTIAL INFORMATION
    "Confidential Information" means all business, technical, and financial information.

    2. OBLIGATIONS
    The Receiving Party shall not disclose Confidential Information without prior written consent.

    3. DURATION
    This agreement shall remain in effect for a period of 5 years.

    4. GOVERNING LAW
    This agreement is governed by the laws of England and Wales.
    """


@pytest.fixture
def sample_hr_document():
    """Sample HR disciplinary document."""
    return """
    DISCIPLINARY MEETING NOTICE

    Employee: John Smith
    Date: 15th January 2024
    Time: 10:00 AM
    Location: Meeting Room A

    Purpose: To discuss allegations of misconduct on 10th January 2024.

    You have the right to be accompanied by a trade union representative or colleague.

    Please confirm your attendance by 12th January 2024.

    Regards,
    HR Department
    """


# ============================================================================
# PERFORMANCE MONITORING FIXTURES
# ============================================================================

@pytest.fixture
def performance_monitor():
    """Monitor test execution time and resource usage."""
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.metrics = {}

        def start(self):
            self.start_time = datetime.utcnow()

        def stop(self, label="test"):
            if self.start_time:
                duration = (datetime.utcnow() - self.start_time).total_seconds()
                self.metrics[label] = duration
                return duration
            return None

        def get_metrics(self):
            return self.metrics

    return PerformanceMonitor()


@pytest.fixture
def benchmark_threshold():
    """Define performance benchmark thresholds (in seconds)."""
    return {
        "api_response": 2.0,        # API should respond within 2s
        "validation": 5.0,          # Document validation within 5s
        "correction": 10.0,         # Document correction within 10s
        "gate_check": 0.5,          # Single gate check within 0.5s
        "synthesis": 15.0,          # Full synthesis within 15s
    }


# ============================================================================
# HELPER FIXTURES
# ============================================================================

@pytest.fixture
def api_headers():
    """Standard API headers for testing."""
    return {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key-12345",
        "User-Agent": "LOKI-Test-Client/1.0"
    }


@pytest.fixture
def compliance_modules():
    """List of all available compliance modules."""
    return ["fca_uk", "gdpr_uk", "tax_uk", "nda_uk", "hr_scottish"]


@pytest.fixture
def test_documents_path():
    """Path to test documents directory."""
    path = PROJECT_ROOT / "tests" / "test_data" / "documents"
    path.mkdir(parents=True, exist_ok=True)
    return path


@pytest.fixture
def temp_upload_dir():
    """Temporary directory for file uploads during testing."""
    temp_dir = tempfile.mkdtemp(prefix="loki_test_")
    yield Path(temp_dir)
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


# ============================================================================
# PARAMETRIZATION FIXTURES
# ============================================================================

@pytest.fixture(params=["fca_uk", "gdpr_uk", "tax_uk", "nda_uk", "hr_scottish"])
def module_name(request):
    """Parametrize tests across all modules."""
    return request.param


@pytest.fixture(params=["LOW", "MEDIUM", "HIGH", "CRITICAL"])
def severity_level(request):
    """Parametrize tests across severity levels."""
    return request.param


@pytest.fixture(params=[1, 5, 10, 50, 100])
def concurrent_requests(request):
    """Parametrize tests for different concurrency levels."""
    return request.param


# ============================================================================
# CLEANUP HOOKS
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Automatic cleanup after each test."""
    yield
    # Clear any test artifacts
    # Reset global state if needed
    pass


@pytest.fixture(scope="session", autouse=True)
def session_cleanup():
    """Cleanup after entire test session."""
    yield
    # Final cleanup
    pass
