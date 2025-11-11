"""
LOKI Interceptor FastAPI Application

Production-ready REST API for compliance validation and document correction
"""

import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

from .routes import validation, correction, history, modules, stats, websocket
from .dependencies import get_engine, get_corrector, get_audit_logger, get_cache
from .models.common import ErrorResponse, HealthResponse

# Application startup time
_startup_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Initialize resources on startup, cleanup on shutdown
    """
    # Startup
    print("🚀 LOKI Interceptor API starting...")

    # Initialize engine and load modules
    engine = get_engine()
    core_modules = [
        'hr_scottish', 'gdpr_uk', 'nda_uk', 'tax_uk', 'fca_uk'
    ]
    optional_modules = [
        'uk_employment', 'gdpr_advanced', 'fca_advanced',
        'scottish_law', 'industry_specific'
    ]

    for module_name in core_modules:
        try:
            engine.load_module(module_name)
            print(f"  ✓ Loaded core module: {module_name}")
        except Exception as e:
            print(f"  ✗ Failed to load core module {module_name}: {e}")

    for module_name in optional_modules:
        try:
            engine.load_module(module_name)
            print(f"  ✓ Loaded optional module: {module_name}")
        except Exception as e:
            print(f"  ⚠ Optional module {module_name} not available: {e}")

    print(f"📦 Loaded {len(engine.modules)} compliance modules")
    print("✅ API ready")

    yield

    # Shutdown
    print("🛑 LOKI Interceptor API shutting down...")
    # Cleanup resources if needed


# Create FastAPI application
app = FastAPI(
    title="LOKI Interceptor API",
    description="""
    Production-ready REST API for AI compliance validation and document correction.

    ## Features

    - **Document Validation**: Validate documents against compliance modules
    - **Document Correction**: Apply rule-based corrections to compliance issues
    - **Validation History**: Track and analyze validation history
    - **Module Management**: Query available compliance modules and gates
    - **System Statistics**: Get comprehensive system analytics
    - **Real-time Validation**: WebSocket support for streaming validation

    ## Authentication

    Currently, the API uses rate limiting based on IP address.
    API key authentication can be enabled for production use.

    ## Rate Limiting

    - Default: 100 requests per minute per IP
    - Configurable per endpoint

    ## Versioning

    All endpoints are versioned (v1) to ensure backward compatibility.
    """,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:*",
        "http://127.0.0.1:*",
        "https://*.trycloudflare.com",
        "file://*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Rate-Limit-Remaining"]
)

# Gzip compression for responses
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
    return response


# Exception handlers
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle value errors"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            error="VALIDATION_ERROR",
            message=str(exc),
            timestamp=datetime.utcnow().isoformat()
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred",
            details={"type": type(exc).__name__},
            timestamp=datetime.utcnow().isoformat()
        ).model_dump()
    )


# Health check endpoint
@app.get(
    "/api/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check",
    description="Check API health status and uptime"
)
async def health_check(detailed: Optional[bool] = False):
    """
    Health check endpoint

    Returns basic health information including:
    - Status
    - Version
    - Timestamp
    - Modules loaded
    - Uptime
    """
    engine = get_engine()
    uptime = time.time() - _startup_time

    response = HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat(),
        modules_loaded=len(engine.modules),
        uptime_seconds=uptime
    )

    return response


@app.get(
    "/api/v1/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check (versioned)",
    description="Check API health status and uptime (versioned endpoint)"
)
async def health_check_v1(detailed: Optional[bool] = False):
    """Versioned health check endpoint"""
    return await health_check(detailed)


# Root endpoint
@app.get(
    "/api",
    tags=["Info"],
    summary="API information",
    description="Get basic API information"
)
async def api_info():
    """
    API information endpoint

    Returns basic information about the API
    """
    return {
        "name": "LOKI Interceptor API",
        "version": "1.0.0",
        "description": "Production-ready compliance validation and document correction API",
        "docs_url": "/api/docs",
        "redoc_url": "/api/redoc",
        "openapi_url": "/api/openapi.json"
    }


# Include routers
app.include_router(
    validation.router,
    prefix="/api/v1",
    tags=["Validation"]
)

app.include_router(
    correction.router,
    prefix="/api/v1",
    tags=["Correction"]
)

app.include_router(
    history.router,
    prefix="/api/v1",
    tags=["History"]
)

app.include_router(
    modules.router,
    prefix="/api/v1",
    tags=["Modules"]
)

app.include_router(
    stats.router,
    prefix="/api/v1",
    tags=["Statistics"]
)

app.include_router(
    websocket.router,
    prefix="/api/v1",
    tags=["WebSocket"]
)


# Custom OpenAPI schema
def custom_openapi():
    """Generate custom OpenAPI schema"""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="LOKI Interceptor API",
        version="1.0.0",
        description=app.description,
        routes=app.routes,
    )

    # Add custom schema elements
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }

    # Add security schemes (for future authentication)
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting LOKI Interceptor API...")
    print("📖 Documentation: http://localhost:8000/api/docs")
    print("📊 ReDoc: http://localhost:8000/api/redoc")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
