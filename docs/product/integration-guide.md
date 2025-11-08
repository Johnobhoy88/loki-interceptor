# LOKI Compliance Platform - Integration Guide

**Document Version:** 1.0
**Last Updated:** November 2025
**Target Audience:** Developers, System Integrators, IT Teams

---

## Table of Contents

- [Integration Overview](#integration-overview)
- [Integration Patterns](#integration-patterns)
- [Desktop Application Integration](#desktop-application-integration)
- [REST API Integration](#rest-api-integration)
- [Webhook Integration](#webhook-integration)
- [Enterprise Integrations](#enterprise-integrations)
- [Security Considerations](#security-considerations)
- [Testing & QA](#testing--qa)
- [Troubleshooting](#troubleshooting)

---

## Integration Overview

LOKI offers multiple integration approaches to fit your existing infrastructure:

### Integration Options

| Method | Use Case | Complexity | Best For |
|--------|----------|------------|----------|
| **Desktop App** | Manual document review | Low | Small teams, ad-hoc compliance |
| **REST API** | Programmatic access | Medium | Custom workflows, automation |
| **Webhooks** | Event-driven workflows | Medium | Real-time notifications |
| **SDK** | Native language integration | Low | Application embedding |
| **Enterprise SSO** | User management | High | Large organizations |

### Architecture Models

**Model 1: Local Processing**
```
[User Application] → [LOKI Desktop] → [Claude API]
    ↓
[Local Audit DB]
```

**Model 2: API Gateway**
```
[Your Application] → [LOKI API] → [Validation Engine] → [Claude API]
                                         ↓
                                   [Audit Database]
```

**Model 3: Hybrid**
```
[Web UI] → [LOKI API] → [Validation]
                            ↓
[Desktop App] ← [Sync] ← [Results]
```

---

## Integration Patterns

### Pattern 1: Pre-Submit Validation

**Use Case:** Validate documents before submission/publication

**Flow:**
```
1. User completes document
2. Click "Check Compliance"
3. LOKI validates in real-time
4. User reviews violations
5. Apply corrections
6. Submit compliant document
```

**Implementation (JavaScript):**
```javascript
async function preSubmitValidation(documentText) {
  const response = await fetch('https://api.loki-compliance.com/v1/validate', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${LOKI_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      text: documentText,
      document_type: 'financial_promotion',
      modules: ['fca_uk', 'gdpr_uk']
    })
  });

  const result = await response.json();

  if (result.status === 'FAIL') {
    showViolations(result.modules);
    return false; // Block submission
  }

  return true; // Allow submission
}

// Hook into form submission
document.getElementById('submitForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const docText = document.getElementById('documentContent').value;

  if (await preSubmitValidation(docText)) {
    e.target.submit();
  }
});
```

### Pattern 2: Batch Processing Pipeline

**Use Case:** Process large volumes of documents overnight

**Flow:**
```
1. Collect documents from source (S3, SharePoint, etc.)
2. Queue for processing
3. Validate each document
4. Auto-correct where possible
5. Flag manual review items
6. Store results
7. Send notification
```

**Implementation (Python):**
```python
import boto3
from loki_compliance import LokiClient
from concurrent.futures import ThreadPoolExecutor

def process_document_batch(s3_bucket, prefix):
    s3 = boto3.client('s3')
    loki = LokiClient(api_key=os.environ['LOKI_API_KEY'])

    # Get all documents
    objects = s3.list_objects_v2(Bucket=s3_bucket, Prefix=prefix)

    def process_doc(obj):
        # Download document
        response = s3.get_object(Bucket=s3_bucket, Key=obj['Key'])
        text = response['Body'].read().decode('utf-8')

        # Validate
        validation = loki.validate(
            text=text,
            document_type='financial_promotion',
            modules=['fca_uk', 'gdpr_uk']
        )

        # Correct if needed
        if validation.status == 'FAIL':
            correction = loki.correct(
                text=text,
                document_type='financial_promotion',
                modules=['fca_uk'],
                validation_id=validation.document_id
            )

            # Upload corrected version
            s3.put_object(
                Bucket=s3_bucket,
                Key=obj['Key'].replace('.txt', '_corrected.txt'),
                Body=correction.corrected_text
            )

            return {'file': obj['Key'], 'status': 'corrected'}

        return {'file': obj['Key'], 'status': 'passed'}

    # Process in parallel (respect rate limits)
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(process_doc, objects['Contents']))

    return results

# Schedule with cron or AWS Lambda
if __name__ == '__main__':
    results = process_document_batch('my-bucket', 'documents/')
    print(f"Processed {len(results)} documents")
```

### Pattern 3: Real-Time Content Moderation

**Use Case:** Live content validation (emails, chat, CRM)

**Flow:**
```
1. User types content
2. On blur/save, trigger validation
3. Show inline warnings
4. Suggest corrections
5. User applies fixes
```

**Implementation (React):**
```javascript
import React, { useState, useEffect } from 'react';
import { debounce } from 'lodash';

function ComplianceEditor() {
  const [content, setContent] = useState('');
  const [violations, setViolations] = useState([]);
  const [validating, setValidating] = useState(false);

  // Debounced validation
  const validateContent = debounce(async (text) => {
    if (text.length < 50) return; // Skip short text

    setValidating(true);
    const response = await fetch('/api/loki/validate', {
      method: 'POST',
      body: JSON.stringify({ text, modules: ['fca_uk', 'gdpr_uk'] })
    });

    const result = await response.json();
    setViolations(result.violations || []);
    setValidating(false);
  }, 1000);

  useEffect(() => {
    validateContent(content);
  }, [content]);

  return (
    <div>
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="Enter document text..."
      />

      {validating && <div>Checking compliance...</div>}

      {violations.length > 0 && (
        <div className="violations">
          <h3>Compliance Issues:</h3>
          {violations.map((v, i) => (
            <div key={i} className={`violation ${v.severity}`}>
              <strong>{v.reason}</strong>
              <p>{v.text}</p>
              <button onClick={() => applySuggestion(v)}>
                Fix This
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

### Pattern 4: Document Workflow Integration

**Use Case:** Approval workflows with compliance gates

**Flow:**
```
1. Document created (Draft)
2. Compliance check (LOKI validation)
3. If FAIL → Send to Legal Review
4. If PASS → Send to Manager Approval
5. Manager approves → Publish
```

**Implementation (Node.js + Express):**
```javascript
const express = require('express');
const { LokiClient } = require('@loki-compliance/sdk');

const app = express();
const loki = new LokiClient({ apiKey: process.env.LOKI_API_KEY });

// Workflow endpoint
app.post('/api/documents/submit', async (req, res) => {
  const { documentId, text, documentType } = req.body;

  // Step 1: Validate compliance
  const validation = await loki.validate({
    text,
    documentType,
    modules: ['fca_uk', 'gdpr_uk']
  });

  // Update document status
  await db.documents.update(documentId, {
    validation_status: validation.status,
    validation_results: validation
  });

  // Step 2: Route based on result
  if (validation.status === 'FAIL') {
    // Critical violations → Legal review required
    if (validation.summary.critical > 0) {
      await workflows.routeTo(documentId, 'legal_review');
      await notifications.send('legal@company.com', {
        subject: `Document ${documentId} requires legal review`,
        body: `${validation.summary.critical} critical violations found`
      });
    } else {
      // Non-critical → Auto-correct and route to manager
      const correction = await loki.correct({
        text,
        documentType,
        modules: ['fca_uk'],
        validationId: validation.document_id
      });

      await db.documents.update(documentId, {
        text: correction.corrected_text
      });

      await workflows.routeTo(documentId, 'manager_approval');
    }
  } else {
    // Passed → Direct to manager approval
    await workflows.routeTo(documentId, 'manager_approval');
  }

  res.json({ status: 'submitted', validation });
});
```

---

## Desktop Application Integration

### Embedding LOKI Desktop

**Windows Integration:**
```powershell
# Silent install
LOKI-Setup.exe /S /D=C:\Program Files\LOKI

# Launch with parameters
Start-Process "C:\Program Files\LOKI\LOKI.exe" -ArgumentList "--file", "C:\path\to\document.txt"
```

**macOS Integration:**
```bash
# Open document with LOKI
open -a "LOKI" /path/to/document.txt

# AppleScript automation
osascript <<EOF
tell application "LOKI"
    activate
    open "/path/to/document.txt"
    validate modules {"fca_uk", "gdpr_uk"}
end tell
EOF
```

### Command-Line Interface

**Validate document:**
```bash
loki validate --file document.txt --modules fca_uk gdpr_uk --output report.json
```

**Correct document:**
```bash
loki correct --file document.txt --modules fca_uk --output corrected.txt --auto-apply
```

**Batch processing:**
```bash
loki batch --folder ./documents --modules fca_uk gdpr_uk --export-folder ./corrected
```

---

## REST API Integration

### Authentication Setup

**Environment Variables (Recommended):**
```bash
export LOKI_API_KEY="lok_live_..."
export LOKI_BASE_URL="https://api.loki-compliance.com/v1"
```

**Configuration File:**
```yaml
# config/loki.yml
api_key: ${LOKI_API_KEY}
base_url: https://api.loki-compliance.com/v1
timeout: 30
retry_attempts: 3
modules:
  - fca_uk
  - gdpr_uk
  - tax_uk
```

### Rate Limiting Strategy

```python
import time
from functools import wraps

def rate_limit_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                return func(*args, **kwargs)
            except RateLimitError as e:
                retry_count += 1
                if retry_count >= max_retries:
                    raise
                time.sleep(e.retry_after)

        return None
    return wrapper

@rate_limit_handler
def validate_document(text):
    return loki_client.validate(text, 'financial_promotion', ['fca_uk'])
```

### Error Handling

```javascript
async function safeValidation(text, options) {
  try {
    const result = await loki.validate(text, options);
    return { success: true, data: result };
  } catch (error) {
    if (error.code === 'rate_limit_exceeded') {
      return {
        success: false,
        error: 'Rate limit exceeded',
        retryAfter: error.retryAfter
      };
    } else if (error.code === 'text_too_large') {
      return {
        success: false,
        error: 'Document too large (max 100,000 chars)'
      };
    } else {
      // Log unexpected errors
      logger.error('LOKI validation error:', error);
      return {
        success: false,
        error: 'Validation service unavailable'
      };
    }
  }
}
```

---

## Webhook Integration

### Setting Up Webhooks

**1. Create Endpoint:**
```python
from flask import Flask, request, jsonify
import hmac
import hashlib

app = Flask(__name__)
WEBHOOK_SECRET = os.environ['LOKI_WEBHOOK_SECRET']

@app.route('/webhooks/loki', methods=['POST'])
def loki_webhook():
    # Verify signature
    signature = request.headers.get('X-LOKI-Signature')
    payload = request.get_data()

    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(f"sha256={expected}", signature):
        return jsonify({'error': 'Invalid signature'}), 401

    # Process event
    event = request.json
    if event['event'] == 'validation.completed':
        handle_validation_completed(event['data'])
    elif event['event'] == 'correction.applied':
        handle_correction_applied(event['data'])

    return jsonify({'status': 'received'}), 200

def handle_validation_completed(data):
    document_id = data['document_id']
    status = data['status']

    # Update database
    db.documents.update(document_id, {'validation_status': status})

    # Notify user
    if status == 'FAIL':
        notifications.send_email(
            to='compliance@company.com',
            subject=f'Document {document_id} failed validation',
            body=f'{data["violations_count"]} violations detected'
        )
```

**2. Register Webhook:**
```bash
curl -X POST https://api.loki-compliance.com/v1/webhooks \
  -H "Authorization: Bearer lok_live_..." \
  -d '{
    "url": "https://yourapp.com/webhooks/loki",
    "events": ["validation.completed", "correction.applied"],
    "secret": "your_webhook_secret"
  }'
```

### Testing Webhooks

```python
import requests

def test_webhook():
    payload = {
        "event": "validation.completed",
        "event_id": "evt_test123",
        "timestamp": "2025-11-08T10:30:00Z",
        "data": {
            "document_id": "doc_test",
            "status": "FAIL",
            "violations_count": 3
        }
    }

    response = requests.post(
        'http://localhost:5000/webhooks/loki',
        json=payload,
        headers={'X-LOKI-Signature': 'sha256=test'}
    )

    assert response.status_code == 200
```

---

## Enterprise Integrations

### SharePoint Integration

**Setup:**
1. Create Azure AD application
2. Grant SharePoint permissions
3. Configure LOKI webhook
4. Map document libraries

**Auto-Validation on Upload:**
```python
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext

def monitor_sharepoint_folder(site_url, folder_path):
    ctx = ClientContext(site_url).with_credentials(
        UserCredential(username, password)
    )

    folder = ctx.web.get_folder_by_server_relative_url(folder_path)
    files = folder.files
    ctx.load(files)
    ctx.execute_query()

    for file in files:
        # Download file
        response = file.download()
        ctx.execute_query()

        # Validate with LOKI
        validation = loki.validate(
            text=response.content.decode('utf-8'),
            document_type='financial_promotion',
            modules=['fca_uk', 'gdpr_uk']
        )

        # Add metadata
        file.properties['ComplianceStatus'] = validation.status
        file.properties['ValidationDate'] = datetime.now().isoformat()
        file.update()
        ctx.execute_query()
```

### Salesforce Integration

**Custom Apex Trigger:**
```apex
trigger DocumentValidation on Document__c (before insert, before update) {
    for (Document__c doc : Trigger.new) {
        if (doc.Text__c != null && doc.Text__c.length() > 0) {
            // Call LOKI API via HTTP callout
            HttpRequest req = new HttpRequest();
            req.setEndpoint('callout:LOKI_API/validate');
            req.setMethod('POST');
            req.setHeader('Content-Type', 'application/json');

            Map<String, Object> body = new Map<String, Object>{
                'text' => doc.Text__c,
                'document_type' => 'financial_promotion',
                'modules' => new List<String>{'fca_uk', 'gdpr_uk'}
            };
            req.setBody(JSON.serialize(body));

            Http http = new Http();
            HttpResponse res = http.send(req);

            if (res.getStatusCode() == 200) {
                Map<String, Object> result = (Map<String, Object>)JSON.deserializeUntyped(res.getBody());
                doc.Compliance_Status__c = (String)result.get('status');
                doc.Validation_Date__c = System.now();
            }
        }
    }
}
```

### Microsoft Teams Integration

**Bot Notification:**
```javascript
const { TeamsActivityHandler, MessageFactory } = require('botbuilder');

class ComplianceBot extends TeamsActivityHandler {
  async sendComplianceAlert(conversationId, documentId, violations) {
    const card = MessageFactory.attachment({
      contentType: 'application/vnd.microsoft.card.adaptive',
      content: {
        type: 'AdaptiveCard',
        version: '1.2',
        body: [
          {
            type: 'TextBlock',
            text: `Document ${documentId} Compliance Alert`,
            weight: 'Bolder',
            size: 'Large'
          },
          {
            type: 'TextBlock',
            text: `${violations.length} violations detected`,
            color: 'Attention'
          },
          {
            type: 'ActionSet',
            actions: [
              {
                type: 'Action.OpenUrl',
                title: 'Review in LOKI',
                url: `https://portal.loki-compliance.com/documents/${documentId}`
              }
            ]
          }
        ]
      }
    });

    await this.sendMessageToConversation(conversationId, card);
  }
}
```

---

## Security Considerations

### API Key Management

**Best Practices:**
1. **Use Environment Variables:**
   ```bash
   # .env (never commit this)
   LOKI_API_KEY=lok_live_...
   ```

2. **Rotate Keys Regularly:**
   - Set 90-day expiration
   - Automate rotation with AWS Secrets Manager or Azure Key Vault

3. **Separate Keys by Environment:**
   - Development: `lok_dev_...`
   - Staging: `lok_staging_...`
   - Production: `lok_live_...`

4. **Monitor Key Usage:**
   - Track API calls per key
   - Alert on suspicious activity
   - Revoke compromised keys immediately

### Data Security

**Encryption in Transit:**
```python
# Always use HTTPS (enforced by API)
import requests

# Good
response = requests.post('https://api.loki-compliance.com/v1/validate', ...)

# Bad - Will fail
response = requests.post('http://api.loki-compliance.com/v1/validate', ...)
```

**Data Retention:**
```python
# Configure audit log retention
loki_config = {
    'audit': {
        'enabled': True,
        'retention_days': 90,
        'encrypt': True,
        'auto_delete': True
    }
}
```

**PII Handling:**
- LOKI does not store document content
- Only validation metadata is logged
- Enable audit log encryption for sensitive data
- GDPR-compliant data processing

---

## Testing & QA

### Unit Testing

```python
import unittest
from unittest.mock import patch, Mock
from loki_compliance import LokiClient

class TestLokiIntegration(unittest.TestCase):
    def setUp(self):
        self.client = LokiClient(api_key='test_key')

    @patch('loki_compliance.client.requests.post')
    def test_validation_success(self, mock_post):
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'PASS',
            'summary': {'total_violations': 0}
        }
        mock_post.return_value = mock_response

        # Test validation
        result = self.client.validate(
            text='Test document',
            document_type='financial_promotion',
            modules=['fca_uk']
        )

        self.assertEqual(result.status, 'PASS')
        self.assertEqual(result.summary['total_violations'], 0)

    @patch('loki_compliance.client.requests.post')
    def test_rate_limit_handling(self, mock_post):
        # Mock rate limit error
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {'Retry-After': '60'}
        mock_post.return_value = mock_response

        # Should raise RateLimitError
        with self.assertRaises(RateLimitError) as context:
            self.client.validate('Test', 'financial_promotion', ['fca_uk'])

        self.assertEqual(context.exception.retry_after, 60)
```

### Integration Testing

```javascript
describe('LOKI API Integration', () => {
  let client;

  beforeAll(() => {
    client = new LokiClient({
      apiKey: process.env.LOKI_TEST_API_KEY,
      baseUrl: 'https://api-staging.loki-compliance.com/v1'
    });
  });

  test('validates financial promotion', async () => {
    const result = await client.validate({
      text: 'Investment Opportunity - Guaranteed 15% Returns!',
      documentType: 'financial_promotion',
      modules: ['fca_uk']
    });

    expect(result.status).toBe('FAIL');
    expect(result.summary.critical).toBeGreaterThan(0);
  });

  test('applies corrections', async () => {
    const correction = await client.correct({
      text: 'Investment Opportunity - Guaranteed 15% Returns!',
      documentType: 'financial_promotion',
      modules: ['fca_uk'],
      options: { autoApply: true }
    });

    expect(correction.correctedText).not.toContain('Guaranteed');
    expect(correction.summary.correctionsApplied).toBeGreaterThan(0);
  });
});
```

### Load Testing

```python
from locust import HttpUser, task, between

class LokiLoadTest(HttpUser):
    wait_time = between(1, 3)
    host = "https://api.loki-compliance.com"

    def on_start(self):
        self.headers = {
            "Authorization": f"Bearer {os.environ['LOKI_API_KEY']}",
            "Content-Type": "application/json"
        }

    @task
    def validate_document(self):
        payload = {
            "text": "Sample financial promotion text",
            "document_type": "financial_promotion",
            "modules": ["fca_uk", "gdpr_uk"]
        }

        self.client.post(
            "/v1/validate",
            json=payload,
            headers=self.headers
        )

# Run: locust -f load_test.py --users 50 --spawn-rate 5
```

---

## Troubleshooting

### Common Integration Issues

**Issue 1: 401 Unauthorized**
```
Error: {"error": {"code": "invalid_api_key"}}

Solution:
1. Verify API key format (lok_live_...)
2. Check key is not expired
3. Ensure Authorization header is correct:
   Authorization: Bearer lok_live_...
4. Verify key has necessary permissions
```

**Issue 2: 413 Payload Too Large**
```
Error: {"error": {"code": "text_too_large"}}

Solution:
1. Split document into chunks (max 100,000 chars)
2. Process chunks separately
3. Combine results

Example:
def split_document(text, max_chars=90000):
    chunks = []
    while len(text) > max_chars:
        split_at = text.rfind(' ', 0, max_chars)
        chunks.append(text[:split_at])
        text = text[split_at:]
    chunks.append(text)
    return chunks
```

**Issue 3: Timeout Errors**
```
Error: Request timeout after 30 seconds

Solution:
1. Increase client timeout
2. Check network connectivity
3. Verify API status: https://status.loki-compliance.com

Example (Python):
response = requests.post(url, json=data, timeout=60)
```

### Debugging Tips

**Enable Debug Logging:**
```python
import logging

logging.basicConfig(level=logging.DEBUG)
loki_client = LokiClient(api_key='...', debug=True)
```

**Inspect API Responses:**
```javascript
const response = await fetch(url, options);
console.log('Status:', response.status);
console.log('Headers:', response.headers);
const data = await response.json();
console.log('Body:', JSON.stringify(data, null, 2));
```

**Monitor API Status:**
- Status Page: https://status.loki-compliance.com
- Subscribe to status updates
- Check rate limit headers

---

## Support

**Integration Support:**
- Email: integrations@highlandai.com
- Documentation: https://docs.loki-compliance.com
- GitHub Examples: https://github.com/HighlandAI/loki-examples

**Enterprise Support:**
- Dedicated integration engineer
- Custom integration development
- On-site training and support

---

*Last Updated: November 2025*
*Version: 1.0*
