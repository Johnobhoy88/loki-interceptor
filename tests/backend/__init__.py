"""
Backend testing module for LOKI Interceptor.

This package contains comprehensive tests for all backend components including:
- Core modules (cache, security, audit logging, correction, etc.)
- Enterprise features (RBAC, multi-tenancy, audit trails)
- API endpoints and integration tests
- Compliance modules (FCA, GDPR, Tax, etc.)
- Performance and load testing
"""

__all__ = [
    'test_core_cache',
    'test_core_security',
    'test_core_audit_log',
    'test_core_corrector',
    'test_data_generators',
]
