#!/usr/bin/env python3
"""
LOKI Interceptor API Launcher

Quick start script for the FastAPI application
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("🚀 LOKI Interceptor FastAPI Server")
    print("=" * 60)
    print()
    print("📖 Documentation: http://localhost:8000/api/docs")
    print("📊 ReDoc:         http://localhost:8000/api/redoc")
    print("❤️  Health Check:  http://localhost:8000/api/health")
    print()
    print("🛑 Press Ctrl+C to stop")
    print("=" * 60)
    print()

    # Start server
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
