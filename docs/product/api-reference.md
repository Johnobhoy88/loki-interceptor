# LOKI Compliance Platform - API Reference

**API Version:** 1.0
**Last Updated:** November 2025
**Base URL:** `https://api.loki-compliance.com/v1`

---

## Table of Contents

- [Authentication](#authentication)
- [Rate Limiting](#rate-limiting)
- [Error Handling](#error-handling)
- [Endpoints](#endpoints)
  - [Validation](#validation)
  - [Correction](#correction)
  - [Modules](#modules)
  - [Health](#health)
  - [Audit](#audit)
- [Webhooks](#webhooks)
- [SDKs](#sdks)
- [Code Examples](#code-examples)

---

## Authentication

All API requests require authentication using an API key.

### Obtaining an API Key

1. Log in to your account: https://portal.loki-compliance.com
2. Navigate to **Settings > API Keys**
3. Click **Create New Key**
4. Name your key (e.g., "Production API")
5. Copy and securely store the key

**Key Format:** `lok_live_...` (48 characters)

### Authentication Methods

#### Method 1: Authorization Header (Recommended)

```http
Authorization: Bearer lok_live_abcd1234efgh5678ijkl9012mnop3456qrst
```

#### Method 2: Query Parameter

```http
GET /v1/health?api_key=lok_live_abcd1234...
```

**Warning:** Query parameters are logged. Use Authorization header for production.

### API Key Security

**Best Practices:**
- Store keys in environment variables
- Never commit keys to version control
- Rotate keys every 90 days
- Use separate keys for dev/staging/production
- Revoke compromised keys immediately

---

## Rate Limiting

Rate limits protect API stability and ensure fair usage.

### Limits by Plan

| Plan | Requests/Minute | Requests/Hour | Requests/Day |
|------|----------------|---------------|--------------|
| Starter | 10 | 500 | 5,000 |
| Professional | 30 | 1,500 | 20,000 |
| Enterprise | Custom | Custom | Custom |

### Rate Limit Headers

Every response includes rate limit information:

```http
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 28
X-RateLimit-Reset: 1699564800
```

### Handling Rate Limits

**HTTP 429 Response:**
```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Try again in 45 seconds.",
    "retry_after": 45
  }
}
```

**Retry Strategy:**
```python
import time
import requests

def api_call_with_retry(url, headers, data):
    while True:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 429:
            return response

        retry_after = int(response.headers.get('Retry-After', 60))
        time.sleep(retry_after)
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Invalid or missing API key |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Temporary unavailability |

### Error Response Format

```json
{
  "error": {
    "code": "invalid_request",
    "message": "Human-readable error message",
    "details": {
      "field": "document_type",
      "issue": "Must be one of: financial, privacy_policy, employment, contract"
    },
    "request_id": "req_abc123def456",
    "timestamp": "2025-11-08T10:30:00Z"
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `invalid_api_key` | 401 | API key is invalid or expired |
| `rate_limit_exceeded` | 429 | Too many requests |
| `invalid_request` | 400 | Malformed request body |
| `validation_failed` | 422 | Document validation failed |
| `module_not_found` | 404 | Requested module doesn't exist |
| `text_too_large` | 413 | Document exceeds size limit |
| `internal_error` | 500 | Server-side error |

---

## Endpoints

### Validation

Validate a document against compliance modules.

#### POST /v1/validate

**Request:**

```http
POST /v1/validate
Authorization: Bearer lok_live_...
Content-Type: application/json

{
  "text": "Your document text here",
  "document_type": "financial_promotion",
  "modules": ["fca_uk", "gdpr_uk"],
  "options": {
    "severity_threshold": "HIGH",
    "return_details": true
  }
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `text` | string | Yes | Document text to validate (max 100,000 chars) |
| `document_type` | string | Yes | Type: `financial_promotion`, `privacy_policy`, `employment`, `contract`, `invoice`, `nda` |
| `modules` | array | Yes | List of modules: `fca_uk`, `gdpr_uk`, `tax_uk`, `nda_uk`, `hr_scottish` |
| `options.severity_threshold` | string | No | Minimum severity: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW` (default: `LOW`) |
| `options.return_details` | boolean | No | Include detailed violation info (default: `true`) |

**Response (200 OK):**

```json
{
  "request_id": "req_abc123def456",
  "processed_at": "2025-11-08T10:30:00Z",
  "document_id": "doc_xyz789ghi012",
  "status": "FAIL",
  "summary": {
    "total_violations": 3,
    "critical": 2,
    "high": 1,
    "medium": 0,
    "low": 0
  },
  "modules": {
    "fca_uk": {
      "status": "FAIL",
      "gates": {
        "fair_clear_not_misleading": {
          "status": "FAIL",
          "severity": "CRITICAL",
          "violations": [
            {
              "pattern": "misleading_guarantee",
              "text": "Guaranteed 15% returns",
              "location": {
                "line": 1,
                "paragraph": 1,
                "character_start": 0,
                "character_end": 24
              },
              "reason": "Financial guarantees are prohibited under FCA COBS 4.2.1",
              "regulation": "FCA COBS 4.2.1(1)R",
              "severity": "CRITICAL"
            }
          ]
        },
        "risk_warnings": {
          "status": "FAIL",
          "severity": "CRITICAL",
          "violations": [
            {
              "pattern": "missing_risk_warning",
              "reason": "Financial promotion missing mandatory risk warning",
              "regulation": "FCA COBS 4.2.1(3)R",
              "severity": "CRITICAL"
            }
          ]
        }
      }
    },
    "gdpr_uk": {
      "status": "PASS",
      "gates": {}
    }
  },
  "metadata": {
    "character_count": 256,
    "word_count": 42,
    "processing_time_ms": 2341
  }
}
```

**Example cURL:**

```bash
curl -X POST https://api.loki-compliance.com/v1/validate \
  -H "Authorization: Bearer lok_live_..." \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Investment Opportunity - Guaranteed 15% Returns!",
    "document_type": "financial_promotion",
    "modules": ["fca_uk", "gdpr_uk"]
  }'
```

---

### Correction

Correct a document based on validation results.

#### POST /v1/correct

**Request:**

```http
POST /v1/correct
Authorization: Bearer lok_live_...
Content-Type: application/json

{
  "text": "Your document text here",
  "document_type": "financial_promotion",
  "modules": ["fca_uk", "gdpr_uk"],
  "options": {
    "auto_apply": true,
    "preserve_formatting": true,
    "return_audit_trail": true
  }
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `text` | string | Yes | Document text to correct |
| `document_type` | string | Yes | Document type |
| `modules` | array | Yes | Compliance modules |
| `validation_id` | string | No | Previous validation ID (skip re-validation) |
| `options.auto_apply` | boolean | No | Auto-apply all corrections (default: `true`) |
| `options.preserve_formatting` | boolean | No | Maintain original formatting (default: `true`) |
| `options.return_audit_trail` | boolean | No | Include full audit trail (default: `false`) |

**Response (200 OK):**

```json
{
  "request_id": "req_def456ghi789",
  "processed_at": "2025-11-08T10:30:05Z",
  "document_id": "doc_xyz789ghi012",
  "correction_id": "cor_jkl345mno678",
  "status": "CORRECTED",
  "original_text": "Investment Opportunity - Guaranteed 15% Returns!...",
  "corrected_text": "Investment Opportunity - Targeted 15% Returns\n\nRISK WARNING: Capital at risk...",
  "summary": {
    "corrections_applied": 4,
    "corrections_suggested": 1,
    "text_length_change": 156,
    "validation_status": "PASS"
  },
  "corrections": [
    {
      "id": "cor_001",
      "pattern": "misleading_guarantee",
      "strategy": "regex_replacement",
      "before": "Guaranteed 15% Returns",
      "after": "Targeted 15% Returns",
      "reason": "Removed misleading guarantee (FCA COBS 4.2.1)",
      "module": "fca_uk",
      "severity": "CRITICAL",
      "applied": true,
      "location": {
        "line_start": 1,
        "line_end": 1,
        "char_start": 26,
        "char_end": 48
      }
    },
    {
      "id": "cor_002",
      "pattern": "add_risk_warning",
      "strategy": "template_insertion",
      "before": "",
      "after": "\n\nRISK WARNING: Capital at risk. The value of investments can go down as well as up. Past performance is not indicative of future results.",
      "reason": "Added mandatory risk warning (FCA COBS 4.2.1)",
      "module": "fca_uk",
      "severity": "CRITICAL",
      "applied": true,
      "location": {
        "line_start": 1,
        "line_end": 1,
        "char_start": 48,
        "char_end": 48
      }
    }
  ],
  "suggestions": [
    {
      "id": "sug_001",
      "message": "Consider adding FCA authorization statement",
      "module": "fca_uk",
      "severity": "HIGH",
      "example": "We are authorized and regulated by the FCA (FRN: 123456)"
    }
  ],
  "deterministic_hash": "a3b2c1d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "metadata": {
    "processing_time_ms": 3782,
    "validation_time_ms": 2341,
    "correction_time_ms": 1441
  }
}
```

**Example cURL:**

```bash
curl -X POST https://api.loki-compliance.com/v1/correct \
  -H "Authorization: Bearer lok_live_..." \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Investment Opportunity - Guaranteed 15% Returns!",
    "document_type": "financial_promotion",
    "modules": ["fca_uk"],
    "options": {
      "auto_apply": true,
      "return_audit_trail": true
    }
  }'
```

---

### Modules

Retrieve information about available compliance modules.

#### GET /v1/modules

**Request:**

```http
GET /v1/modules
Authorization: Bearer lok_live_...
```

**Response (200 OK):**

```json
{
  "modules": [
    {
      "id": "fca_uk",
      "name": "FCA UK - Financial Conduct Authority",
      "description": "UK financial services compliance",
      "version": "1.0.0",
      "rules_count": 51,
      "pattern_groups": 35,
      "supported_document_types": [
        "financial_promotion",
        "investment_advice",
        "product_disclosure"
      ],
      "regulations": [
        "COBS 4.2.1",
        "COBS 4.2.3",
        "COBS 9",
        "Consumer Duty"
      ],
      "gates": [
        {
          "id": "fair_clear_not_misleading",
          "name": "Fair, Clear, Not Misleading",
          "regulation": "COBS 4.2.1(1)R",
          "severity": "CRITICAL"
        }
      ]
    },
    {
      "id": "gdpr_uk",
      "name": "GDPR UK - Data Protection",
      "description": "UK GDPR and Data Protection Act 2018",
      "version": "1.0.0",
      "rules_count": 29,
      "pattern_groups": 16,
      "supported_document_types": [
        "privacy_policy",
        "data_processing_agreement",
        "consent_form"
      ]
    }
  ],
  "total_modules": 5,
  "total_rules": 141
}
```

#### GET /v1/modules/{module_id}

**Request:**

```http
GET /v1/modules/fca_uk
Authorization: Bearer lok_live_...
```

**Response (200 OK):**

```json
{
  "id": "fca_uk",
  "name": "FCA UK - Financial Conduct Authority",
  "description": "Validates financial documents against FCA regulations",
  "version": "1.0.0",
  "last_updated": "2025-11-01",
  "rules_count": 51,
  "pattern_groups": 35,
  "gates": [
    {
      "id": "fair_clear_not_misleading",
      "name": "Fair, Clear, Not Misleading",
      "regulation": "COBS 4.2.1(1)R",
      "description": "Ensures financial promotions are fair, clear, and not misleading",
      "severity": "CRITICAL",
      "detects": [
        "Misleading guarantees",
        "False risk representations",
        "Omission of material information"
      ]
    }
  ],
  "supported_document_types": [
    "financial_promotion",
    "investment_advice",
    "product_disclosure",
    "client_agreement"
  ]
}
```

---

### Health

Check API health and status.

#### GET /v1/health

**Request:**

```http
GET /v1/health
```

**No authentication required.**

**Response (200 OK):**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-08T10:30:00Z",
  "services": {
    "api": "operational",
    "database": "operational",
    "ai_provider": "operational"
  },
  "performance": {
    "avg_response_time_ms": 320,
    "requests_per_minute": 24
  }
}
```

---

### Audit

Retrieve audit logs and correction history.

#### GET /v1/audit/corrections

**Request:**

```http
GET /v1/audit/corrections?limit=10&offset=0
Authorization: Bearer lok_live_...
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | No | Results per page (default: 50, max: 100) |
| `offset` | integer | No | Pagination offset (default: 0) |
| `start_date` | string | No | ISO 8601 date (e.g., `2025-11-01`) |
| `end_date` | string | No | ISO 8601 date |
| `module` | string | No | Filter by module (e.g., `fca_uk`) |

**Response (200 OK):**

```json
{
  "corrections": [
    {
      "correction_id": "cor_abc123",
      "document_id": "doc_xyz789",
      "processed_at": "2025-11-08T10:30:00Z",
      "document_type": "financial_promotion",
      "modules": ["fca_uk", "gdpr_uk"],
      "corrections_applied": 4,
      "original_hash": "a3b2c1...",
      "corrected_hash": "d4e5f6...",
      "user_id": "usr_123",
      "metadata": {
        "ip_address": "192.168.1.1",
        "user_agent": "LOKI Desktop/1.0.0"
      }
    }
  ],
  "pagination": {
    "total": 247,
    "limit": 10,
    "offset": 0,
    "has_more": true
  }
}
```

#### GET /v1/audit/corrections/{correction_id}

**Request:**

```http
GET /v1/audit/corrections/cor_abc123
Authorization: Bearer lok_live_...
```

**Response (200 OK):**

```json
{
  "correction_id": "cor_abc123",
  "document_id": "doc_xyz789",
  "processed_at": "2025-11-08T10:30:00Z",
  "original_text": "...",
  "corrected_text": "...",
  "corrections": [
    {
      "pattern": "misleading_guarantee",
      "before": "Guaranteed returns",
      "after": "Targeted returns",
      "reason": "FCA COBS 4.2.1",
      "module": "fca_uk"
    }
  ],
  "deterministic_hash": "a3b2c1...",
  "validation_results": { /* Full validation response */ }
}
```

---

## Webhooks

Configure webhooks to receive real-time notifications.

### Webhook Events

| Event | Description |
|-------|-------------|
| `validation.completed` | Document validation completed |
| `correction.applied` | Corrections applied to document |
| `validation.failed` | Validation failed with error |
| `module.updated` | Compliance module updated |

### Webhook Configuration

1. Log in to portal: https://portal.loki-compliance.com
2. Navigate to **Settings > Webhooks**
3. Click **Add Webhook Endpoint**
4. Enter your webhook URL
5. Select events to subscribe
6. Save configuration

### Webhook Payload

**Example: `validation.completed`**

```json
{
  "event": "validation.completed",
  "event_id": "evt_abc123",
  "timestamp": "2025-11-08T10:30:00Z",
  "data": {
    "document_id": "doc_xyz789",
    "status": "FAIL",
    "violations_count": 3,
    "modules": ["fca_uk", "gdpr_uk"]
  }
}
```

### Webhook Security

**Signature Verification:**

Every webhook includes a signature header:

```http
X-LOKI-Signature: sha256=abcdef123456...
```

**Verification Code (Python):**

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

---

## SDKs

Official SDKs for popular languages.

### Python SDK

**Installation:**

```bash
pip install loki-compliance
```

**Usage:**

```python
from loki_compliance import LokiClient

client = LokiClient(api_key="lok_live_...")

# Validate document
result = client.validate(
    text="Your document text",
    document_type="financial_promotion",
    modules=["fca_uk", "gdpr_uk"]
)

print(result.status)  # PASS or FAIL
print(result.violations)  # List of violations

# Correct document
correction = client.correct(
    text="Your document text",
    document_type="financial_promotion",
    modules=["fca_uk"]
)

print(correction.corrected_text)
print(correction.corrections_applied)
```

### JavaScript/Node.js SDK

**Installation:**

```bash
npm install @loki-compliance/sdk
```

**Usage:**

```javascript
const { LokiClient } = require('@loki-compliance/sdk');

const client = new LokiClient({
  apiKey: 'lok_live_...'
});

// Validate document
const result = await client.validate({
  text: 'Your document text',
  documentType: 'financial_promotion',
  modules: ['fca_uk', 'gdpr_uk']
});

console.log(result.status);
console.log(result.violations);

// Correct document
const correction = await client.correct({
  text: 'Your document text',
  documentType: 'financial_promotion',
  modules: ['fca_uk']
});

console.log(correction.correctedText);
```

### Other Languages

**Ruby, PHP, Java, Go:** Coming Q1 2026

---

## Code Examples

### Python: Complete Validation & Correction Workflow

```python
import requests
import json

API_KEY = "lok_live_..."
BASE_URL = "https://api.loki-compliance.com/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Step 1: Validate document
validate_payload = {
    "text": "Investment Opportunity - Guaranteed 15% Returns!",
    "document_type": "financial_promotion",
    "modules": ["fca_uk", "gdpr_uk"]
}

response = requests.post(
    f"{BASE_URL}/validate",
    headers=headers,
    json=validate_payload
)

validation = response.json()

if validation["status"] == "FAIL":
    print(f"Violations found: {validation['summary']['total_violations']}")

    # Step 2: Apply corrections
    correct_payload = {
        "text": validate_payload["text"],
        "document_type": "financial_promotion",
        "modules": ["fca_uk"],
        "options": {
            "auto_apply": True,
            "return_audit_trail": True
        }
    }

    response = requests.post(
        f"{BASE_URL}/correct",
        headers=headers,
        json=correct_payload
    )

    correction = response.json()
    print(f"Corrected text: {correction['corrected_text']}")
    print(f"Corrections applied: {correction['summary']['corrections_applied']}")
else:
    print("Document is compliant!")
```

### Node.js: Batch Processing

```javascript
const axios = require('axios');

const API_KEY = 'lok_live_...';
const BASE_URL = 'https://api.loki-compliance.com/v1';

const headers = {
  'Authorization': `Bearer ${API_KEY}`,
  'Content-Type': 'application/json'
};

async function processDocuments(documents) {
  const results = [];

  for (const doc of documents) {
    try {
      // Validate
      const validateResponse = await axios.post(
        `${BASE_URL}/validate`,
        {
          text: doc.text,
          document_type: 'financial_promotion',
          modules: ['fca_uk', 'gdpr_uk']
        },
        { headers }
      );

      const validation = validateResponse.data;

      // Correct if needed
      if (validation.status === 'FAIL') {
        const correctResponse = await axios.post(
          `${BASE_URL}/correct`,
          {
            text: doc.text,
            document_type: 'financial_promotion',
            modules: ['fca_uk'],
            validation_id: validation.document_id
          },
          { headers }
        );

        results.push({
          id: doc.id,
          status: 'corrected',
          correctedText: correctResponse.data.corrected_text
        });
      } else {
        results.push({
          id: doc.id,
          status: 'passed',
          originalText: doc.text
        });
      }
    } catch (error) {
      results.push({
        id: doc.id,
        status: 'error',
        error: error.message
      });
    }
  }

  return results;
}

// Usage
const documents = [
  { id: 1, text: '...' },
  { id: 2, text: '...' }
];

processDocuments(documents).then(results => {
  console.log(JSON.stringify(results, null, 2));
});
```

---

## Best Practices

### Performance Optimization

1. **Reuse Validation Results:**
   ```python
   validation = client.validate(text, document_type, modules)
   correction = client.correct(
       text,
       document_type,
       modules,
       validation_id=validation.document_id  # Skip re-validation
   )
   ```

2. **Batch Requests:**
   - Group documents by type and modules
   - Process in parallel with async/await
   - Respect rate limits

3. **Cache Module Information:**
   ```python
   modules = client.get_modules()  # Cache this response
   # Don't fetch on every request
   ```

### Error Handling

```python
from loki_compliance import LokiClient, LokiError, RateLimitError

client = LokiClient(api_key="...")

try:
    result = client.validate(text, document_type, modules)
except RateLimitError as e:
    time.sleep(e.retry_after)
    # Retry request
except LokiError as e:
    logger.error(f"Validation failed: {e.message}")
    # Handle error appropriately
```

### Security

1. **Never expose API keys:**
   ```python
   # Good
   api_key = os.environ.get('LOKI_API_KEY')

   # Bad
   api_key = "lok_live_..." # Hardcoded key
   ```

2. **Validate webhook signatures:**
   Always verify webhook signatures before processing

3. **Use HTTPS:**
   Never make HTTP requests (all endpoints enforce HTTPS)

---

## API Changelog

### Version 1.0 (November 2025)
- Initial API release
- Core validation and correction endpoints
- Module information endpoints
- Audit log access
- Webhook support

### Planned (Q1 2026)
- Batch validation endpoint
- Document comparison endpoint
- Compliance scoring endpoint
- Advanced analytics APIs

---

## Support

**API Support:**
- Email: api-support@highlandai.com
- Documentation: https://api-docs.loki-compliance.com
- Status Page: https://status.loki-compliance.com

**Report Issues:**
- GitHub: https://github.com/HighlandAI/loki-interceptor/issues
- Email: bugs@highlandai.com

---

*Last Updated: November 2025*
*API Version: 1.0*
