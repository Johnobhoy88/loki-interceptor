"""
End-to-End Tests for LOKI Compliance Platform

This module contains comprehensive E2E test scenarios that validate
the complete user workflows and integration between frontend and backend.
"""

import os
import pytest
from typing import Generator


@pytest.fixture(scope="session")
def test_config():
    """Load test configuration from environment."""
    return {
        "backend_url": os.getenv("BACKEND_URL", "http://localhost:5002"),
        "frontend_url": os.getenv("FRONTEND_URL", "http://localhost:80"),
        "api_timeout": int(os.getenv("API_TIMEOUT", "30")),
        "headless": os.getenv("HEADLESS_BROWSER", "true").lower() == "true",
    }


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    import asyncio
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()
