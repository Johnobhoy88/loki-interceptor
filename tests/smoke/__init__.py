"""
Smoke Tests for LOKI Platform

Smoke tests provide quick validation that the system is operational.
These are the first tests run after deployment.
"""

import os
import pytest


@pytest.fixture(scope="session")
def smoke_config():
    """Load smoke test configuration."""
    return {
        "backend_url": os.getenv("BACKEND_URL", "http://localhost:5002"),
        "frontend_url": os.getenv("FRONTEND_URL", "http://localhost:80"),
        "timeout": int(os.getenv("SMOKE_TEST_TIMEOUT", "10")),
    }
