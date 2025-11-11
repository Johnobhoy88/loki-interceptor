"""
Chaos Engineering Tests for LOKI Platform

Chaos tests validate system resilience under failure conditions.
"""

import os
import pytest


@pytest.fixture(scope="session")
def chaos_config():
    """Load chaos engineering configuration."""
    return {
        "enabled": os.getenv("CHAOS_ENABLED", "true").lower() == "true",
        "failure_rate": float(os.getenv("CHAOS_FAILURE_RATE", "0.1")),
        "delay_ms": int(os.getenv("CHAOS_DELAY_MS", "100")),
        "timeout": int(os.getenv("CHAOS_TIMEOUT", "30")),
    }
