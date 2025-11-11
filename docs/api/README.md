# LOKI Interceptor REST API Reference

**Production-Ready Compliance Validation & Correction API**

## Overview

The LOKI Interceptor API is a comprehensive REST API for document compliance validation and automatic correction. It provides endpoints for validating documents against UK regulatory frameworks and applying rule-based corrections.

### Base URL
```
http://localhost:8000/api/v1
```

### API Documentation
- **Interactive Docs**: `http://localhost:8000/api/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8000/api/redoc` (ReDoc)
- **OpenAPI Schema**: `http://localhost:8000/api/openapi.json`

## Quick Start

### 1. Health Check
```bash
curl http://localhost:8000/api/health
```

### 2. Validate a Document
```bash
curl -X POST http://localhost:8000/api/v1/validate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Investment returns guaranteed at 15% annually",
    "document_type": "financial_promotion",
    "modules": ["fca_uk"],
    "use_cache": false
  }'
```

### 3. Apply Corrections
```bash
curl -X POST http://localhost:8000/api/v1/correct \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Investment returns guaranteed at 15% annually",
    "validation_results": {...},
    "auto_apply": true,
    "confidence_threshold": 0.8
  }'
```

## Authentication

Currently, the API uses **rate limiting** based on IP address. For production use, API key authentication is recommended.

### Future Authentication
API key authentication support is planned for v1.1. Use the following format:
```bash
curl -H "X-API-Key: your_api_key_here" \
  http://localhost:8000/api/v1/validate
```

## Rate Limiting

- **Default Limit**: 100 requests per minute per IP
- **Headers**:
  - `X-Rate-Limit-Limit`: Total requests allowed
  - `X-Rate-Limit-Remaining`: Requests remaining
  - `X-Rate-Limit-Reset`: Unix timestamp when limit resets

## API Endpoints

### Health & Info

#### Health Check
```
GET /api/health
GET /api/v1/health
```

**Description**: Check API health status and uptime

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-11T21:00:00Z",
  "modules_loaded": 5,
  "uptime_seconds": 3600
}
```

#### API Information
```
GET /api
```

**Description**: Get basic API information

**Response**:
```json
{
  "name": "LOKI Interceptor API",
  "version": "1.0.0",
  "description": "Production-ready compliance validation and document correction API",
  "docs_url": "/api/docs",
  "redoc_url": "/api/redoc",
  "openapi_url": "/api/openapi.json"
}
```

### Validation Endpoints

#### Validate Document
```
POST /api/v1/validate
```

**Description**: Validate a document against compliance modules

**Request Body**:
```json
{
  "text": "string (required) - Document text to validate",
  "document_type": "string (required) - Type of document",
  "modules": [
    "string (optional) - Compliance modules to check"
  ],
  "use_cache": "boolean (optional, default: false) - Use cached results",
  "include_suggestions": "boolean (optional, default: true) - Include suggestions",
  "metadata": {
    "client_id": "string (optional)",
    "reference_id": "string (optional)"
  }
}
```

**Supported Modules**:
- `fca_uk` - Financial Conduct Authority
- `gdpr_uk` - GDPR & Data Protection
- `tax_uk` - HMRC Tax Compliance
- `nda_uk` - Non-Disclosure Agreements
- `hr_scottish` - Employment Law

**Response (Success 200)**:
```json
{
  "validation": {
    "document_hash": "sha256_hash",
    "timestamp": "2025-11-11T21:00:00Z",
    "overall_risk": "MEDIUM",
    "modules": [
      {
        "module_id": "fca_uk",
        "module_name": "Financial Conduct Authority",
        "gates_checked": 15,
        "gates_passed": 12,
        "gates_failed": 3,
        "risk_level": "MEDIUM",
        "execution_time_ms": 245.5,
        "gates": [
          {
            "gate_id": "fair_clear_not_misleading",
            "gate_name": "Fair, Clear, Not Misleading",
            "passed": false,
            "severity": "HIGH",
            "message": "Document contains misleading claims",
            "legal_source": "COBS 4.2.1",
            "suggestions": ["Remove unsubstantiated claims", "Add risk warnings"]
          }
        ]
      }
    ],
    "total_gates_checked": 75,
    "total_gates_failed": 8,
    "execution_time_ms": 1245.5,
    "cached": false
  },
  "risk": "MEDIUM",
  "suggestions_available": true
}
```

**Risk Levels**:
- `LOW` - No significant issues
- `MEDIUM` - Minor issues, review recommended
- `HIGH` - Multiple issues or critical violations
- `CRITICAL` - Severe compliance violations

#### Batch Validate Documents
```
POST /api/v1/validate/batch
```

**Description**: Validate multiple documents (max 10 per request)

**Request Body**:
```json
[
  {
    "text": "Document 1...",
    "document_type": "financial",
    "modules": ["fca_uk"]
  },
  {
    "text": "Document 2...",
    "document_type": "privacy_policy",
    "modules": ["gdpr_uk"]
  }
]
```

**Response**: Array of validation responses (same format as single validation)

**Limitations**:
- Maximum 10 documents per batch
- Each document validated independently
- Results returned in same order as requests

### Correction Endpoints

#### Correct Document
```
POST /api/v1/correct
```

**Description**: Apply rule-based corrections to compliance issues

**Request Body**:
```json
{
  "text": "string (required) - Document text to correct",
  "validation_results": "object (required) - Validation results from /validate",
  "auto_apply": "boolean (optional, default: false) - Auto-apply corrections",
  "confidence_threshold": "float (optional, default: 0.8) - Minimum confidence for auto-apply",
  "preserve_formatting": "boolean (optional, default: true) - Maintain original formatting"
}
```

**Confidence Scoring**:
- `0.95-1.0` - High confidence (safe to auto-apply)
- `0.8-0.95` - Medium-high confidence
- `0.6-0.8` - Medium confidence (review recommended)
- `<0.6` - Low confidence (manual review required)

**Response (Success 200)**:
```json
{
  "original_text": "Investment returns guaranteed at 15% annually",
  "corrected_text": "Investment returns are projected at 15% annually based on historical performance",
  "issues_found": 2,
  "issues_corrected": 2,
  "corrections": [
    {
      "index": 0,
      "original": "guaranteed",
      "corrected": "projected",
      "reason": "FCA COBS 4.2.1 - Avoid guarantees without substantiation",
      "strategy": "regex_replacement",
      "confidence": 0.95
    },
    {
      "index": 1,
      "original": "at 15% annually",
      "corrected": "at 15% annually based on historical performance",
      "reason": "Add context for performance claims",
      "strategy": "template_insertion",
      "confidence": 0.85
    }
  ],
  "suggestions": [
    "Consider adding risk warnings",
    "Specify investment objectives"
  ],
  "execution_time_ms": 456.3
}
```

**Correction Strategies**:
- `suggestion` (Priority 20) - Recommendation only
- `regex_replacement` (Priority 30) - Text replacement
- `template_insertion` (Priority 40) - Add standard text
- `structural_reform` (Priority 60) - Reorganize content

### Module Endpoints

#### List Available Modules
```
GET /api/v1/modules
```

**Description**: Get list of available compliance modules

**Response**:
```json
{
  "modules": [
    {
      "id": "fca_uk",
      "name": "Financial Conduct Authority",
      "description": "Validates financial promotions and documents",
      "rules_count": 51,
      "pattern_groups": 35,
      "version": "1.0.0",
      "status": "production"
    }
  ],
  "total": 5,
  "production_modules": 5,
  "beta_modules": 0
}
```

#### Get Module Details
```
GET /api/v1/modules/{module_id}
```

**Description**: Get detailed information about a specific module

**Parameters**:
- `module_id` (path) - Module identifier (e.g., "fca_uk")

**Response**:
```json
{
  "id": "fca_uk",
  "name": "Financial Conduct Authority",
  "description": "Validates financial documents against FCA COBS regulations",
  "rules_count": 51,
  "pattern_groups": 35,
  "gates": [
    {
      "id": "fair_clear_not_misleading",
      "name": "Fair, Clear, Not Misleading",
      "description": "COBS 4.2.1 requirement",
      "severity_levels": ["CRITICAL", "HIGH"],
      "examples": [...]
    }
  ],
  "legal_references": [
    "COBS 4.2.1", "COBS 4.2.3", "COBS 9"
  ],
  "version": "1.0.0",
  "status": "production",
  "last_updated": "2025-11-11"
}
```

### Statistics Endpoints

#### Get System Statistics
```
GET /api/v1/stats
```

**Description**: Get comprehensive system analytics

**Query Parameters**:
- `period` (optional) - Time period: "hour", "day", "week", "month" (default: "day")

**Response**:
```json
{
  "timestamp": "2025-11-11T21:00:00Z",
  "validations": {
    "total": 1250,
    "successful": 1200,
    "failed": 50,
    "average_execution_time_ms": 450.5,
    "cache_hit_rate": 0.35
  },
  "corrections": {
    "total": 875,
    "auto_applied": 750,
    "manual_review": 125,
    "average_issues_corrected": 4.2
  },
  "modules": {
    "fca_uk": {
      "validations": 450,
      "failures": 180,
      "average_execution_time_ms": 320
    },
    "gdpr_uk": {
      "validations": 400,
      "failures": 150,
      "average_execution_time_ms": 280
    }
  },
  "cache": {
    "items": 950,
    "hit_rate": 0.35,
    "total_size_mb": 125
  }
}
```

### History Endpoints

#### Get Validation History
```
GET /api/v1/history/validations
```

**Description**: Get recent validation history

**Query Parameters**:
- `limit` (optional, default: 10) - Number of results
- `offset` (optional, default: 0) - Result offset
- `module` (optional) - Filter by module
- `status` (optional) - Filter by status (PASS, FAIL)

**Response**:
```json
{
  "validations": [
    {
      "id": "validation_12345",
      "timestamp": "2025-11-11T20:55:00Z",
      "document_type": "financial_promotion",
      "modules": ["fca_uk", "gdpr_uk"],
      "overall_risk": "MEDIUM",
      "gates_checked": 30,
      "gates_failed": 5,
      "cached": false
    }
  ],
  "total": 1250,
  "limit": 10,
  "offset": 0
}
```

#### Get Correction History
```
GET /api/v1/history/corrections
```

**Description**: Get recent correction history

**Query Parameters**:
- `limit` (optional, default: 10)
- `offset` (optional, default: 0)
- `auto_applied_only` (optional, default: false)

**Response**:
```json
{
  "corrections": [
    {
      "id": "correction_12345",
      "timestamp": "2025-11-11T20:55:30Z",
      "issues_found": 3,
      "issues_corrected": 2,
      "auto_applied": true,
      "average_confidence": 0.87
    }
  ],
  "total": 875,
  "limit": 10,
  "offset": 0
}
```

### WebSocket Endpoints

#### Real-time Validation Stream
```
WS /api/v1/ws/validate
```

**Description**: Stream validation results in real-time

**Connection**:
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/validate');

// Send validation request
ws.send(JSON.stringify({
  "text": "Document text...",
  "document_type": "financial",
  "modules": ["fca_uk"]
}));

// Receive updates
ws.onmessage = (event) => {
  const result = JSON.parse(event.data);
  console.log('Module result:', result);
};
```

**Message Format**:
```json
{
  "type": "module_result",
  "module": "fca_uk",
  "result": {...},
  "progress": 0.6
}
```

## Error Handling

### Error Response Format
```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {
    "field": "additional_context"
  },
  "timestamp": "2025-11-11T21:00:00Z"
}
```

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request body |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_SERVER_ERROR` | 500 | Server error |
| `RESOURCE_NOT_FOUND` | 404 | Module or resource not found |
| `UNAUTHORIZED` | 401 | Authentication required |

### Error Examples

**Invalid Request (400)**:
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Field validation error",
  "details": {
    "text": "Field is required"
  },
  "timestamp": "2025-11-11T21:00:00Z"
}
```

**Rate Limit (429)**:
```json
{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "Too many requests",
  "details": {
    "limit": 100,
    "window_seconds": 60,
    "reset_timestamp": 1699723260
  },
  "timestamp": "2025-11-11T21:00:00Z"
}
```

## Response Headers

Standard response headers included with all responses:

| Header | Description |
|--------|-------------|
| `X-Process-Time` | Processing time in milliseconds |
| `X-Request-ID` | Unique request identifier |
| `X-Rate-Limit-Limit` | Total requests allowed |
| `X-Rate-Limit-Remaining` | Requests remaining in window |
| `Content-Type` | Response content type (application/json) |
| `Content-Encoding` | Compression (gzip if applicable) |

## Best Practices

### 1. Caching
```bash
# Use cache for repeated validations
curl -X POST http://localhost:8000/api/v1/validate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "...",
    "document_type": "financial",
    "modules": ["fca_uk"],
    "use_cache": true
  }'
```

### 2. Batch Operations
```bash
# Validate multiple documents in one request (max 10)
curl -X POST http://localhost:8000/api/v1/validate/batch \
  -H "Content-Type: application/json" \
  -d '[
    {"text": "Doc1...", "document_type": "contract"},
    {"text": "Doc2...", "document_type": "policy"}
  ]'
```

### 3. Confidence Thresholds
```bash
# Only auto-apply high-confidence corrections
curl -X POST http://localhost:8000/api/v1/correct \
  -d '{
    "text": "...",
    "validation_results": {...},
    "auto_apply": true,
    "confidence_threshold": 0.95
  }'
```

### 4. Error Handling
Always implement proper error handling:
```python
import requests

try:
    response = requests.post(
        'http://localhost:8000/api/v1/validate',
        json={...},
        timeout=30
    )
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    print(f"API Error: {e.response.status_code}")
    print(e.response.json())
except requests.exceptions.Timeout:
    print("Request timeout - document may be too large")
```

## Integration Examples

See [API Examples](examples.md) for complete examples in:
- Python (requests, asyncio)
- JavaScript (fetch, axios)
- cURL
- Postman

## Support & Documentation

- **Interactive API Docs**: http://localhost:8000/api/docs
- **Full Documentation**: See [docs/INDEX.md](../INDEX.md)
- **Issues**: https://github.com/Johnobhoy88/loki-interceptor/issues
- **Email Support**: support@highlandai.com

---

**Version**: 1.0.0
**Last Updated**: 2025-11-11
