# LOKI Interceptor API Documentation

**Version:** 1.0.0
**Base URL:** `http://localhost:8000/api/v1`
**Documentation:** `http://localhost:8000/api/docs`
**ReDoc:** `http://localhost:8000/api/redoc`

---

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Authentication](#authentication)
4. [Rate Limiting](#rate-limiting)
5. [API Endpoints](#api-endpoints)
6. [WebSocket API](#websocket-api)
7. [Python Client SDK](#python-client-sdk)
8. [Error Handling](#error-handling)
9. [Examples](#examples)

---

## Overview

The LOKI Interceptor API provides comprehensive compliance validation and document correction capabilities. It supports multiple compliance modules, real-time validation via WebSocket, and includes a full Python client SDK.

### Key Features

- ✅ **Document Validation** - Validate documents against compliance modules
- ✅ **Document Correction** - Apply rule-based corrections to compliance issues
- ✅ **Validation History** - Track and analyze validation history
- ✅ **Module Management** - Query available compliance modules and gates
- ✅ **System Statistics** - Get comprehensive analytics
- ✅ **Real-time Validation** - WebSocket support for streaming validation
- ✅ **Python SDK** - Easy-to-use Python client library

### Supported Compliance Modules

- **GDPR UK** - UK-specific GDPR compliance
- **HR Scottish** - Scottish employment law
- **UK Employment** - UK employment regulations
- **FCA UK** - Financial Conduct Authority rules
- **NDA UK** - Non-disclosure agreements
- **Tax UK** - UK tax regulations
- **Industry Specific** - Industry-focused compliance

---

## Getting Started

### Installation

1. **Install Dependencies:**
```bash
pip install fastapi uvicorn[standard] pydantic websockets requests
```

2. **Start the API Server:**
```bash
# Development mode with auto-reload
cd /home/user/loki-interceptor/backend/api
python main.py

# Or with uvicorn directly
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
```

3. **Access Documentation:**
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### Quick Test

```bash
curl -X GET http://localhost:8000/api/health
```

---

## Authentication

Currently, the API uses **rate limiting based on IP address**. API key authentication can be enabled for production use.

### Future: API Key Authentication

When enabled, include the API key in the request header:

```http
X-API-Key: your-api-key-here
```

---

## Rate Limiting

**Default Limits:**
- 100 requests per minute per IP
- Configurable per endpoint

**Rate Limit Headers:**
- `X-Rate-Limit-Remaining` - Remaining requests
- `X-Process-Time` - Request processing time (ms)

**Rate Limit Exceeded:**
```json
{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "Rate limit exceeded. Please try again later.",
  "timestamp": "2025-11-11T10:30:00Z"
}
```

---

## API Endpoints

### Health & Info

#### GET `/api/health`

Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-11T10:30:00Z",
  "modules_loaded": 10,
  "uptime_seconds": 3600.5
}
```

---

### Validation

#### POST `/api/v1/validate`

Validate a document against compliance modules.

**Request Body:**
```json
{
  "text": "This employment contract is subject to Scottish law...",
  "document_type": "employment_contract",
  "modules": ["hr_scottish", "uk_employment"],
  "use_cache": true,
  "include_suggestions": true,
  "metadata": {
    "client_id": "CLIENT123",
    "industry": "technology"
  }
}
```

**Response:**
```json
{
  "validation": {
    "document_hash": "a1b2c3d4e5f6...",
    "timestamp": "2025-11-11T10:30:00Z",
    "overall_risk": "MEDIUM",
    "modules": [
      {
        "module_id": "hr_scottish",
        "module_name": "HR Scottish Law",
        "gates_checked": 12,
        "gates_passed": 10,
        "gates_failed": 2,
        "risk_level": "MEDIUM",
        "gates": [
          {
            "gate_id": "hr_scot_minimum_wage",
            "gate_name": "Scottish Minimum Wage",
            "passed": false,
            "severity": "ERROR",
            "message": "Wage below Scottish minimum",
            "legal_source": "Scottish Employment Act 2024",
            "snippets": ["£8.50 per hour"],
            "suggestions": ["Update to £11.44 per hour (2024 rate)"]
          }
        ],
        "execution_time_ms": 45.3
      }
    ],
    "universal_analyzers": [
      {
        "name": "PII Scanner",
        "detected": true,
        "count": 3,
        "details": {"types": ["email", "phone"]}
      }
    ],
    "total_gates_checked": 45,
    "total_gates_failed": 5,
    "execution_time_ms": 234.5,
    "cached": false
  },
  "risk": "MEDIUM",
  "suggestions_available": true
}
```

**Risk Levels:**
- `LOW` - No significant issues
- `MEDIUM` - Some non-critical issues
- `HIGH` - Multiple issues or critical issues
- `CRITICAL` - Severe compliance violations

#### POST `/api/v1/validate/batch`

Validate multiple documents (max 10 per request).

**Request Body:**
```json
[
  {
    "text": "Document 1...",
    "document_type": "contract"
  },
  {
    "text": "Document 2...",
    "document_type": "policy"
  }
]
```

**Response:** Array of validation responses

---

### Correction

#### POST `/api/v1/correct`

Apply rule-based corrections to compliance issues.

**Request Body:**
```json
{
  "text": "We may use your data for marketing purposes.",
  "validation_results": { /* from /validate endpoint */ },
  "auto_apply": true,
  "confidence_threshold": 0.8,
  "issue_ids": null
}
```

**Response:**
```json
{
  "original_text": "We may use your data for marketing purposes.",
  "corrected_text": "With your explicit consent, we will use your data for marketing purposes.",
  "issues_found": 5,
  "issues_corrected": 4,
  "corrections": [
    {
      "issue_id": "ISSUE_001",
      "position": 0,
      "length": 20,
      "original": "We may use your data",
      "corrected": "With your explicit consent, we will use your data"
    }
  ],
  "suggestions": [
    {
      "issue_id": "ISSUE_001",
      "gate_id": "gdpr_uk_consent",
      "severity": "ERROR",
      "original_text": "We may use your data",
      "suggested_text": "With your explicit consent, we will use your data",
      "explanation": "GDPR requires explicit consent language",
      "confidence": 0.95,
      "applied": true
    }
  ],
  "improvement_score": 0.8,
  "metadata": {
    "execution_time_ms": 123.4
  }
}
```

#### POST `/api/v1/synthesize`

Generate compliant document draft (deterministic synthesis).

**Request Body:**
```json
{
  "base_text": "Employment contract...",
  "validation": { /* validation results */ },
  "context": {
    "jurisdiction": "UK",
    "industry": "tech"
  },
  "modules": ["hr_scottish"]
}
```

---

### History

#### GET `/api/v1/history`

Get paginated validation history with filters.

**Query Parameters:**
- `page` (int, default: 1) - Page number
- `page_size` (int, default: 50, max: 100) - Items per page
- `risk_level` (string) - Filter by risk level
- `document_type` (string) - Filter by document type
- `module_id` (string) - Filter by module
- `date_from` (ISO date) - Start date
- `date_to` (ISO date) - End date
- `client_id` (string) - Filter by client
- `include_stats` (bool) - Include statistics

**Example:**
```bash
GET /api/v1/history?page=1&page_size=50&risk_level=HIGH&include_stats=true
```

**Response:**
```json
{
  "entries": [
    {
      "id": "HIST_12345",
      "timestamp": "2025-11-11T10:30:00Z",
      "document_hash": "a1b2c3d4...",
      "document_type": "employment_contract",
      "overall_risk": "MEDIUM",
      "modules_checked": ["hr_scottish", "uk_employment"],
      "gates_failed": 3,
      "execution_time_ms": 234.5,
      "client_id": "CLIENT123"
    }
  ],
  "total": 1250,
  "page": 1,
  "page_size": 50,
  "total_pages": 25,
  "stats": {
    "total_validations": 1250,
    "risk_distribution": {
      "LOW": 800,
      "MEDIUM": 300,
      "HIGH": 120,
      "CRITICAL": 30
    },
    "document_type_distribution": {
      "contract": 500,
      "policy": 300,
      "email": 450
    },
    "average_execution_time_ms": 234.5,
    "peak_usage_hour": 14
  }
}
```

#### GET `/api/v1/history/{entry_id}`

Get specific history entry.

#### DELETE `/api/v1/history`

Clear history (with optional days filter).

---

### Modules & Gates

#### GET `/api/v1/modules`

List all compliance modules.

**Response:**
```json
{
  "modules": [
    {
      "id": "gdpr_uk",
      "name": "GDPR UK Compliance",
      "version": "3.2.1",
      "description": "UK-specific GDPR compliance validation",
      "gates_count": 45,
      "active_gates": 43,
      "deprecated_gates": 2,
      "categories": ["data_protection", "privacy"],
      "jurisdictions": ["UK", "EU"],
      "industry": null
    }
  ],
  "total": 10,
  "total_gates": 234
}
```

#### GET `/api/v1/modules/{module_id}`

Get specific module details.

#### GET `/api/v1/gates`

List all compliance gates.

**Query Parameters:**
- `module_id` (string) - Filter by module
- `active_only` (bool, default: true) - Only active gates

**Response:**
```json
{
  "gates": [
    {
      "id": "gdpr_uk_consent",
      "name": "GDPR Consent Requirement",
      "version": "2.1.0",
      "module_id": "gdpr_uk",
      "severity": "ERROR",
      "description": "Validates explicit consent requirements",
      "legal_source": "GDPR Article 7",
      "active": true,
      "deprecated": false
    }
  ],
  "total": 234,
  "module_id": null
}
```

#### GET `/api/v1/gates/{gate_id}`

Get specific gate details.

---

### Statistics & Analytics

#### GET `/api/v1/stats`

Get system-wide statistics.

**Query Parameters:**
- `include_trends` (bool) - Include 7-day risk trends

**Response:**
```json
{
  "total_validations": 15250,
  "total_corrections": 8340,
  "total_modules": 10,
  "total_gates": 234,
  "uptime_seconds": 86400.5,
  "average_validation_time_ms": 234.5,
  "peak_validations_per_hour": 450,
  "risk_distribution": {
    "LOW": 10000,
    "MEDIUM": 3000,
    "HIGH": 2000,
    "CRITICAL": 250
  },
  "cache_stats": {
    "total_entries": 500,
    "cache_hits": 3450,
    "cache_misses": 1250,
    "hit_rate": 0.734,
    "memory_usage_mb": 12.5
  },
  "recent_trends": []
}
```

#### GET `/api/v1/stats/analytics`

Get comprehensive analytics for a time period.

**Query Parameters:**
- `days` (int, default: 7, max: 365) - Days to analyze

#### GET `/api/v1/stats/cache`

Get cache statistics.

#### POST `/api/v1/stats/cache/clear`

Clear validation cache.

---

## WebSocket API

### Connection

**Endpoint:** `ws://localhost:8000/api/v1/ws/validate`

### Protocol

#### 1. Client Sends Validation Request

```json
{
  "type": "validation_request",
  "request_id": "REQ_12345",
  "timestamp": "2025-11-11T10:30:00Z",
  "text": "Document text...",
  "document_type": "contract",
  "modules": ["gdpr_uk", "hr_scottish"],
  "include_progress": true,
  "metadata": {}
}
```

#### 2. Server Sends Progress Updates

```json
{
  "type": "validation_progress",
  "request_id": "REQ_12345",
  "timestamp": "2025-11-11T10:30:01Z",
  "module_id": "gdpr_uk",
  "modules_completed": 1,
  "modules_total": 2,
  "progress_percent": 50.0,
  "current_status": "Processing GDPR UK module..."
}
```

#### 3. Server Sends Final Results

```json
{
  "type": "validation_response",
  "request_id": "REQ_12345",
  "timestamp": "2025-11-11T10:30:05Z",
  "validation": { /* full validation results */ },
  "risk": "MEDIUM",
  "success": true
}
```

#### 4. Error Handling

```json
{
  "type": "error",
  "request_id": "REQ_12345",
  "timestamp": "2025-11-11T10:30:00Z",
  "error": "VALIDATION_ERROR",
  "message": "Invalid request parameters",
  "details": {"field": "text"}
}
```

### JavaScript Example

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/validate');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'validation_request',
    request_id: 'REQ_001',
    timestamp: new Date().toISOString(),
    text: 'Document text...',
    document_type: 'contract',
    modules: ['gdpr_uk'],
    include_progress: true
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'validation_progress') {
    console.log(`Progress: ${data.progress_percent}%`);
    console.log(`Status: ${data.current_status}`);
  } else if (data.type === 'validation_response') {
    console.log('Validation complete!');
    console.log(`Risk: ${data.risk}`);
  } else if (data.type === 'error') {
    console.error('Error:', data.message);
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

---

## Python Client SDK

### Installation

```bash
# SDK is included in the repository
# No additional installation needed
```

### Quick Start

```python
from sdk.loki_client import LOKIClient

# Create client
client = LOKIClient(base_url="http://localhost:8000")

# Validate document
result = client.validate(
    text="This employment contract is subject to Scottish law...",
    document_type="employment_contract",
    modules=["hr_scottish", "uk_employment"]
)

print(f"Risk Level: {result.overall_risk}")
print(f"Gates Failed: {result.total_gates_failed}")
print(f"Execution Time: {result.execution_time_ms:.2f}ms")

# Correct document if needed
if result.total_gates_failed > 0:
    correction = client.correct(
        text="This employment contract...",
        validation_results=result.__dict__,
        auto_apply=True,
        confidence_threshold=0.8
    )

    print(f"Issues Corrected: {correction.issues_corrected}")
    print(f"Improvement: {correction.improvement_score:.2%}")
    print(f"Corrected Text: {correction.corrected_text}")
```

### SDK Methods

```python
# Validation
result = client.validate(text, document_type, modules, use_cache, ...)
results = client.validate_batch(documents)

# Correction
correction = client.correct(text, validation_results, auto_apply, ...)

# Modules & Gates
modules = client.get_modules()
module = client.get_module(module_id)
gates = client.get_gates(module_id, active_only)

# Statistics
stats = client.get_stats(include_trends)
analytics = client.get_analytics(days)

# History
history = client.get_history(page, page_size, risk_level, ...)

# Cache
client.clear_cache()

# Health
health = client.health_check()
```

### Convenience Functions

```python
from sdk.loki_client import validate_document, correct_document

# Quick validation
result = validate_document(
    text="Document text...",
    document_type="contract"
)

# Quick correction
correction = correct_document(
    text="Document text...",
    validation_results=result.__dict__
)
```

### Error Handling

```python
from sdk.loki_client import LOKIClient, LOKIAPIError, LOKIClientError

try:
    client = LOKIClient(base_url="http://localhost:8000")
    result = client.validate("Document text...", "contract")

except LOKIAPIError as e:
    # API returned an error
    print(f"API Error {e.status_code}: {e.message}")
    print(f"Details: {e.details}")

except LOKIClientError as e:
    # Client-side error (network, etc.)
    print(f"Client Error: {e}")
```

---

## Error Handling

### Standard Error Response

```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {
    "field": "text",
    "issue": "Text cannot be empty"
  },
  "timestamp": "2025-11-11T10:30:00Z"
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request parameters |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_SERVER_ERROR` | 500 | Server error |
| `NOT_FOUND` | 404 | Resource not found |
| `REQUEST_TOO_LARGE` | 413 | Request size exceeds limit |

---

## Examples

### Complete Validation Workflow

```python
from sdk.loki_client import LOKIClient

client = LOKIClient(base_url="http://localhost:8000")

# 1. Check available modules
modules = client.get_modules()
print(f"Available modules: {len(modules)}")

# 2. Validate document
text = """
This employment contract is governed by Scottish law.
The employee will be paid £8.50 per hour.
"""

result = client.validate(
    text=text,
    document_type="employment_contract",
    modules=["hr_scottish", "uk_employment"]
)

print(f"Risk: {result.overall_risk}")
print(f"Gates Failed: {result.total_gates_failed}")

# 3. Apply corrections if needed
if result.total_gates_failed > 0:
    correction = client.correct(
        text=text,
        validation_results=result.__dict__,
        auto_apply=True
    )

    print(f"Corrected Text: {correction.corrected_text}")
    print(f"Improvement: {correction.improvement_score:.2%}")

# 4. Get statistics
stats = client.get_stats(include_trends=True)
print(f"Total Validations: {stats['total_validations']}")
```

### Batch Validation

```python
documents = [
    {
        "text": "Contract 1...",
        "document_type": "employment_contract"
    },
    {
        "text": "Policy 1...",
        "document_type": "privacy_policy"
    }
]

results = client.validate_batch(documents)

for i, result in enumerate(results):
    print(f"Document {i+1}: {result.overall_risk}")
```

### WebSocket Real-time Validation

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/validate');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'validation_request',
    request_id: `REQ_${Date.now()}`,
    timestamp: new Date().toISOString(),
    text: document.getElementById('contract-text').value,
    document_type: 'contract',
    modules: ['gdpr_uk', 'hr_scottish'],
    include_progress: true
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  switch(data.type) {
    case 'validation_progress':
      updateProgressBar(data.progress_percent);
      break;

    case 'validation_response':
      displayResults(data.validation);
      break;

    case 'error':
      showError(data.message);
      break;
  }
};
```

---

## Best Practices

1. **Use Caching** - Enable `use_cache=true` for repeated validations
2. **Batch Requests** - Use batch endpoints for multiple documents
3. **Handle Rate Limits** - Implement exponential backoff
4. **WebSocket for Real-time** - Use WebSocket for long validations
5. **Monitor Statistics** - Track API usage via `/stats` endpoint
6. **Error Handling** - Always catch and handle exceptions
7. **Keep SDK Updated** - Use latest SDK version

---

## Support

- **Documentation:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc
- **GitHub Issues:** Report bugs and request features
- **API Version:** Check `/api/health` for current version

---

## License

LOKI Interceptor API © 2025

---

*Generated: 2025-11-11*
*Version: 1.0.0*
