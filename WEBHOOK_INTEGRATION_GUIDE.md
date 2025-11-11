# LOKI Webhook & Integration Guide

Comprehensive guide for implementing and managing webhooks and third-party integrations in LOKI Interceptor.

## Table of Contents

1. [Overview](#overview)
2. [Webhook System](#webhook-system)
3. [Integration Connectors](#integration-connectors)
4. [API Reference](#api-reference)
5. [Examples](#examples)
6. [Security](#security)
7. [Monitoring & Analytics](#monitoring--analytics)
8. [Troubleshooting](#troubleshooting)

---

## Overview

LOKI's webhook and integration system enables real-time notifications and event-driven workflows across your compliance infrastructure. It provides:

- **Event-Driven Architecture**: Automatic notifications on compliance events
- **Multiple Integrations**: Slack, Teams, Email, Zapier, and custom webhooks
- **Reliable Delivery**: Exponential backoff retry logic with configurable strategies
- **Security**: HMAC-SHA256 signature verification and TLS encryption
- **Analytics**: Comprehensive delivery tracking and performance metrics
- **Rate Limiting**: Per-webhook and global rate limiting controls

### Key Features

| Feature | Description |
|---------|-------------|
| **Webhook Management** | Create, update, delete, and test webhooks |
| **Event Subscriptions** | Subscribe to specific event types |
| **Retry Logic** | Exponential backoff, linear, fixed interval, or no retry |
| **Signature Verification** | HMAC-SHA256 signed payloads for security |
| **Rate Limiting** | Configurable per-minute and per-hour limits |
| **Delivery Tracking** | Complete delivery history with status and timing |
| **Analytics** | Success rates, response times, and error tracking |
| **Integrations** | Slack, Teams, Email, Zapier for notifications |

---

## Webhook System

### Architecture

The webhook system consists of:

```
┌─────────────────────────────────────────────────────┐
│              LOKI Event Sources                      │
│  (Validation, Correction, Compliance, Batch, etc)   │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│         Webhook Event Dispatcher                     │
│  • Routes events to subscribed webhooks             │
│  • Filters by event type and webhook status         │
│  • Handles batching and scheduling                  │
└──────────────────┬──────────────────────────────────┘
                   │
        ┌──────────┴──────────┬─────────────┐
        ▼                     ▼             ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Webhook 1   │  │  Webhook 2   │  │  Webhook N   │
│  (Direct)    │  │  (Slack)     │  │  (Custom)    │
└──────────────┘  └──────────────┘  └──────────────┘
        │                     │             │
        ▼                     ▼             ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Retry Queue │  │  Retry Queue │  │  Retry Queue │
│  & Analytics │  │  & Analytics │  │  & Analytics │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Database Models

#### Webhook
Stores webhook configuration and metadata.

```python
class Webhook:
    id: int                           # Primary key
    name: str                         # Webhook name
    url: str                          # Webhook URL (HTTPS required)
    secret: str                       # For HMAC signature
    status: WebhookStatus             # active, inactive, paused
    event_types: List[str]            # Subscribed event types
    retry_strategy: RetryStrategy     # Retry strategy
    max_retries: int                  # Max retry attempts (0-20)
    retry_delay_seconds: int          # Initial retry delay
    rate_limit_per_minute: int        # Per-minute rate limit
    rate_limit_per_hour: int          # Per-hour rate limit
    custom_headers: Dict[str, str]    # Custom HTTP headers
    metadata: Dict[str, Any]          # Additional metadata
    created_at: datetime              # Creation timestamp
    updated_at: datetime              # Last update
    last_triggered_at: datetime       # Last event sent
```

#### WebhookDelivery
Tracks each delivery attempt with full request/response details.

```python
class WebhookDelivery:
    id: int                          # Primary key
    webhook_id: int                  # FK to Webhook
    event_type: str                  # Type of event
    event_id: str                    # UUID for idempotency
    event_data: Dict                 # Full event payload
    attempt_number: int              # Retry attempt number
    status: DeliveryStatus           # pending, delivered, failed, etc.
    request_headers: Dict            # Sent request headers
    request_body: Dict               # Sent request body
    signature: str                   # HMAC-SHA256 signature
    response_status_code: int        # HTTP response code
    response_headers: Dict           # Response headers
    response_body: str               # Response body
    sent_at: datetime                # When sent
    responded_at: datetime           # When responded
    duration_ms: float               # Round trip duration
    next_retry_at: datetime          # Scheduled retry time
    last_error: str                  # Error message
    created_at: datetime             # Creation timestamp
```

#### WebhookEvent
Represents an event that triggered deliveries.

```python
class WebhookEvent:
    id: int                          # Primary key
    event_id: str                    # UUID
    event_type: str                  # Type of event
    source: str                      # Source system
    source_id: str                   # Related resource ID
    payload: Dict                    # Event payload
    total_deliveries: int            # Total delivery attempts
    successful_deliveries: int       # Successful count
    failed_deliveries: int           # Failed count
    created_at: datetime             # When occurred
    processed_at: datetime           # When processed
```

#### WebhookAnalytics
Aggregated metrics for webhook performance.

```python
class WebhookAnalytics:
    id: int
    webhook_id: int                  # FK to Webhook
    period_date: datetime            # Date of metrics
    total_events: int                # Events sent
    successful_deliveries: int       # Successful count
    failed_deliveries: int           # Failed count
    retry_count: int                 # Retry attempts
    avg_response_time_ms: float      # Average response time
    min_response_time_ms: float      # Minimum response time
    max_response_time_ms: float      # Maximum response time
    p95_response_time_ms: float      # 95th percentile
    http_4xx_errors: int             # 4xx error count
    http_5xx_errors: int             # 5xx error count
    timeout_errors: int              # Timeout count
    network_errors: int              # Network error count
    success_rate: float              # Success percentage
    created_at: datetime             # Created timestamp
```

### Event Types

LOKI generates the following webhook events:

| Event Type | Triggered When | Payload |
|-----------|----------------|---------|
| `validation.completed` | Document validation finishes | Validation results, gates passed/failed |
| `validation.failed` | Validation encounters errors | Error details, error code, stack trace |
| `correction.applied` | Corrections applied to document | Changes made, confidence score, before/after |
| `document.processed` | Document fully processed | Processing time, all results, status |
| `compliance.alert` | Compliance violation detected | Alert level, type, affected documents |
| `system.error` | System error occurs | Error code, component, severity |
| `batch.completed` | Batch processing completes | Documents processed, success rate |
| `report.generated` | Report is generated | Report type, URL, document count |

### Retry Strategies

LOKI supports four retry strategies:

#### 1. Exponential Backoff (Recommended)
Each retry doubles the delay: 60s, 120s, 240s, 480s, 960s, ...

```python
RetryStrategy.EXPONENTIAL_BACKOFF
max_retries: 5
retry_delay_seconds: 60
backoff_multiplier: 2.0
max_delay: 3600s  # 1 hour cap
```

**Use Case**: Most webhooks should use exponential backoff. It prevents overwhelming receivers and adapts to transient failures.

#### 2. Linear Backoff
Delays increase linearly: 60s, 120s, 180s, 240s, 300s, ...

```python
RetryStrategy.LINEAR_BACKOFF
max_retries: 5
retry_delay_seconds: 60
```

**Use Case**: For services with consistent response times that don't degrade under load.

#### 3. Fixed Interval
Same delay between retries: 60s, 60s, 60s, 60s, 60s, ...

```python
RetryStrategy.FIXED_INTERVAL
max_retries: 5
retry_delay_seconds: 60
```

**Use Case**: For critical webhooks that must retry consistently.

#### 4. No Retry
Attempt delivery once, no retries.

```python
RetryStrategy.NO_RETRY
```

**Use Case**: For non-critical notifications or fire-and-forget scenarios.

### Rate Limiting

Each webhook has configurable rate limits:

```python
webhook.rate_limit_per_minute = 60      # Max 60 deliveries per minute
webhook.rate_limit_per_hour = 3600      # Max 3600 deliveries per hour
```

When a webhook exceeds its rate limit, further deliveries are queued and scheduled for the next available time window.

---

## Integration Connectors

LOKI provides built-in connectors for popular platforms:

### 1. Slack Integration

Send notifications to Slack channels with rich formatting.

#### Features
- Channel and thread support
- Rich message blocks with formatting
- Color-coded alerts
- Customizable headers and footers
- Interactive message elements

#### Setup

```python
from integrations import SlackIntegration

slack = SlackIntegration(
    name="Compliance Alerts",
    webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    config={
        'default_channel': '#compliance',
        'include_footer': True,
        'include_timestamp': True,
    }
)

await slack.connect()
```

#### Example Notification

Validation completion event sends:

```
┌─────────────────────────────────────┐
│ Document Validation Completed       │
├─────────────────────────────────────┤
│ document_id: doc_12345              │
│ validation_status: pass             │
│ gates_passed: 8                     │
│ gates_failed: 0                     │
│ processing_time_ms: 523.45          │
├─────────────────────────────────────┤
│ LOKI Interceptor | 2024-01-15 14:30 │
└─────────────────────────────────────┘
```

### 2. Microsoft Teams Integration

Send notifications to Teams channels with Adaptive Card formatting.

#### Features
- Adaptive card support
- Section and field formatting
- Color-coded severity levels
- Direct message support
- Deep linking to dashboard

#### Setup

```python
from integrations import TeamsIntegration

teams = TeamsIntegration(
    name="Compliance Team",
    webhook_url="https://outlook.webhook.office.com/webhookb2/...",
    config={
        'theme_color': '0078D4',
        'include_footer': True,
    }
)

await teams.connect()
```

### 3. Email Integration

Send email notifications with HTML formatting and attachments.

#### Features
- SMTP support (Gmail, Outlook, custom servers)
- HTML email templates
- File attachments
- Distribution lists
- Automatic retry

#### Setup

```python
from integrations import EmailIntegration

email = EmailIntegration(
    name="Alerts Email",
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    smtp_username="your-email@gmail.com",
    smtp_password="app-specific-password",
    from_address="alerts@company.com",
    config={
        'use_tls': True,
        'default_recipients': ['admin@company.com', 'compliance@company.com'],
        'html_format': True,
    }
)

await email.connect()
```

#### Gmail Setup

1. Enable 2-factor authentication
2. Generate an [App Password](https://myaccount.google.com/apppasswords)
3. Use the app password (not your regular password)

#### Configuration Examples

**Gmail:**
```json
{
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_username": "your-email@gmail.com",
  "smtp_password": "your-app-password"
}
```

**Outlook:**
```json
{
  "smtp_host": "smtp-mail.outlook.com",
  "smtp_port": 587,
  "smtp_username": "your-email@outlook.com",
  "smtp_password": "your-password"
}
```

**Custom SMTP:**
```json
{
  "smtp_host": "mail.company.com",
  "smtp_port": 587,
  "smtp_username": "username",
  "smtp_password": "password"
}
```

### 4. Zapier Integration

Connect to 5000+ apps and services through Zapier.

#### Features
- Workflow automation
- Data transformation
- Event filtering and routing
- Error handling and retries
- Batch processing support

#### Setup

```python
from integrations import ZapierIntegration

zapier = ZapierIntegration(
    name="Automation Hub",
    webhook_url="https://hooks.zapier.com/hooks/catch/YOUR_ID/",
    config={
        'batch_events': True,
        'batch_size': 10,
        'batch_timeout_seconds': 30,
    }
)

await zapier.connect()
```

#### Example Workflows

1. **Create Jira Issues**: Send compliance alerts to Jira
2. **Update Spreadsheets**: Log validation results to Google Sheets
3. **Send Webhooks**: Forward to custom endpoints
4. **Create Records**: Store in Salesforce, HubSpot, etc.

---

## API Reference

### Webhook Endpoints

#### Create Webhook
```http
POST /api/v1/webhooks/
Content-Type: application/json

{
  "name": "Compliance Alerts",
  "url": "https://example.com/webhooks/compliance",
  "description": "Send compliance violations",
  "event_types": ["compliance.alert", "validation.failed"],
  "retry_strategy": "exponential_backoff",
  "max_retries": 5,
  "retry_delay_seconds": 60,
  "rate_limit_per_minute": 60,
  "custom_headers": {
    "Authorization": "Bearer token-xyz"
  },
  "metadata": {
    "team": "compliance",
    "priority": "high"
  }
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "Compliance Alerts",
  "url": "https://example.com/webhooks/compliance",
  "status": "active",
  "event_types": ["compliance.alert", "validation.failed"],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### List Webhooks
```http
GET /api/v1/webhooks/?status=active&limit=50&offset=0
```

#### Get Webhook
```http
GET /api/v1/webhooks/{webhook_id}
```

#### Update Webhook
```http
PUT /api/v1/webhooks/{webhook_id}
Content-Type: application/json

{
  "status": "paused",
  "max_retries": 10,
  "metadata": {
    "updated_reason": "Receiver maintenance"
  }
}
```

#### Delete Webhook
```http
DELETE /api/v1/webhooks/{webhook_id}
```

#### Test Webhook
```http
POST /api/v1/webhooks/{webhook_id}/test
Content-Type: application/json

{
  "event_type": "validation.completed"
}
```

#### Get Delivery History
```http
GET /api/v1/webhooks/{webhook_id}/deliveries?status=failed&limit=100
```

#### Get Analytics
```http
GET /api/v1/webhooks/{webhook_id}/analytics?period_days=7
```

**Response:**
```json
{
  "webhook_id": 1,
  "period_days": 7,
  "total_events": 150,
  "successful_deliveries": 147,
  "failed_deliveries": 3,
  "success_rate": 98.0,
  "avg_response_time_ms": 125.5,
  "min_response_time_ms": 42,
  "max_response_time_ms": 892,
  "p95_response_time_ms": 450.5
}
```

#### Retry Failed Deliveries
```http
POST /api/v1/webhooks/{webhook_id}/retry?max_age_hours=24
```

### Integration Endpoints

#### Register Integration
```http
POST /api/v1/integrations/
Content-Type: application/json

{
  "name": "Slack Alerts",
  "integration_type": "slack",
  "credentials": {
    "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  },
  "event_subscriptions": ["compliance.alert", "validation.failed"]
}
```

#### List Integrations
```http
GET /api/v1/integrations/?integration_type=slack
```

#### Get Integration
```http
GET /api/v1/integrations/{integration_name}
```

#### Test Integration
```http
POST /api/v1/integrations/{integration_name}/test
```

#### Subscribe to Event
```http
POST /api/v1/integrations/{integration_name}/subscribe/compliance.alert
```

#### Unsubscribe from Event
```http
DELETE /api/v1/integrations/{integration_name}/subscribe/compliance.alert
```

#### Get Subscriptions
```http
GET /api/v1/integrations/{integration_name}/subscriptions
```

---

## Examples

### Example 1: Basic Webhook Setup

```python
from webhooks import WebhookManager

manager = WebhookManager()

# Create a webhook
webhook = await manager.create_webhook(
    name="Production Alerts",
    url="https://api.example.com/webhooks/loki",
    event_types=["compliance.alert", "system.error"],
    max_retries=5,
    retry_strategy="exponential_backoff",
)

# Test the webhook
result = await manager.test_webhook(webhook.id)
print(f"Test result: {result['status_code']}")

# Trigger an event
from webhooks.event_types import ComplianceAlertEvent

alert = ComplianceAlertEvent(
    source_id="doc_12345",
    alert_level="critical",
    alert_type="gdpr_violation",
    message="Personal data found in document",
    affected_documents=["doc_12345"],
    recommended_actions=["Redact personal data", "Review GDPR compliance"]
)

delivery_result = await manager.trigger_event(alert)
print(f"Delivered to {delivery_result['deliveries']} webhooks")
```

### Example 2: Slack Integration

```python
from integrations import SlackIntegration, IntegrationManager

manager = IntegrationManager()

# Register Slack integration
await manager.register_integration(
    name="Compliance Alerts",
    integration_type="slack",
    credentials={
        "webhook_url": "https://hooks.slack.com/services/..."
    },
    event_subscriptions=[
        "compliance.alert",
        "validation.failed",
        "batch.completed"
    ]
)

# Test integration
test_result = await manager.test_integration("Compliance Alerts")
print(f"Slack connection: {'✓ Connected' if test_result['success'] else '✗ Failed'}")

# Route event
from webhooks.event_types import ComplianceAlertEvent

alert = ComplianceAlertEvent(
    source_id="batch_123",
    alert_level="high",
    alert_type="fca_violation",
    message="Potential FCA rule violation detected",
    affected_documents=["doc_001", "doc_002"],
    recommended_actions=["Review FCA requirements", "Check document content"]
)

result = await manager.route_event("compliance.alert", alert.to_dict())
print(f"Event routed to {result['routed_to']} integrations")
```

### Example 3: Email Integration with Distribution List

```python
from integrations import EmailIntegration

email = EmailIntegration(
    name="Daily Reports",
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    smtp_username="alerts@company.com",
    smtp_password="app-specific-password",
    from_address="loki-alerts@company.com",
    config={
        'default_recipients': [
            'compliance-team@company.com',
            'admin@company.com',
            'cto@company.com'
        ]
    }
)

await email.connect()

# Send event
from webhooks.event_types import BatchCompletedEvent

batch_event = BatchCompletedEvent(
    source_id="batch_daily_001",
    batch_id="batch_daily_001",
    total_documents=500,
    processed_documents=498,
    failed_documents=2,
    processing_time_ms=45230.5,
    results_summary={
        "compliance_issues": 12,
        "average_confidence": 0.95,
        "processed_in": "45.2 seconds"
    }
)

success = await email.on_batch_completed(batch_event.payload)
print(f"Email sent: {'✓ Success' if success else '✗ Failed'}")
```

### Example 4: Advanced Retry Configuration

```python
from webhooks import WebhookManager
from webhooks.retry_handler import RetryConfig, RetryStrategy

# Create manager with custom retry config
config = RetryConfig(
    strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
    max_retries=10,
    initial_delay_seconds=30,
    max_delay_seconds=7200,  # 2 hours
    backoff_multiplier=1.5,
    jitter_enabled=True,
    jitter_percentage=0.2,
)

manager = WebhookManager(config=config)

# Create webhook with custom retry schedule
webhook = await manager.create_webhook(
    name="Critical Alerts",
    url="https://critical-service.example.com/webhook",
    event_types=["compliance.alert"],
    max_retries=10,
    retry_delay_seconds=30,
)

# Get retry schedule
schedule = manager.retry_handler.create_retry_schedule(webhook.id)
print(f"Total retry time: {schedule['total_retry_time_seconds']} seconds")
for attempt in schedule['attempts']:
    print(f"  Attempt {attempt['attempt']}: Retry at {attempt['retry_at']}")
```

### Example 5: Comprehensive Integration Setup

```python
from integrations import IntegrationManager
from webhooks import WebhookManager

# Initialize managers
webhook_manager = WebhookManager()
integration_manager = IntegrationManager()

# Register multiple integrations
await integration_manager.register_integration(
    name="Slack Compliance",
    integration_type="slack",
    credentials={
        "webhook_url": "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX"
    },
    event_subscriptions=[
        "compliance.alert",
        "validation.failed",
    ]
)

await integration_manager.register_integration(
    name="Email Team",
    integration_type="email",
    credentials={
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "smtp_username": "alerts@company.com",
        "smtp_password": "app-password",
        "from_address": "loki@company.com"
    },
    config={
        "default_recipients": ["compliance@company.com"]
    },
    event_subscriptions=[
        "compliance.alert",
        "batch.completed",
        "system.error",
    ]
)

await integration_manager.register_integration(
    name="Zapier Automation",
    integration_type="zapier",
    credentials={
        "webhook_url": "https://hooks.zapier.com/hooks/catch/12345678/abcdef/"
    },
    config={
        "batch_events": True,
        "batch_size": 10,
    },
    event_subscriptions=[
        "batch.completed",
        "report.generated",
    ]
)

# Check integration health
health = await integration_manager.integration_health()
print(f"Integration Status: {health['status']}")

# Get metrics
metrics = integration_manager.get_metrics()
print(f"Total Integrations: {metrics['total_integrations']}")
print(f"Total Subscriptions: {metrics['total_subscriptions']}")
```

---

## Security

### HMAC-SHA256 Signature Verification

All webhook payloads are signed with HMAC-SHA256 using the webhook secret. Recipients should verify signatures to ensure authenticity.

#### Signature Header
```
X-Webhook-Signature: sha256=abc123def456...
```

#### Python Verification Example
```python
import hmac
import hashlib

def verify_webhook_signature(secret: str, payload: bytes, signature: str) -> bool:
    """Verify HMAC-SHA256 signature"""
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

# In your webhook receiver
@app.post("/webhook")
async def receive_webhook(request: Request):
    payload = await request.body()
    signature = request.headers.get("X-Webhook-Signature", "").replace("sha256=", "")

    if not verify_webhook_signature(WEBHOOK_SECRET, payload, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Process webhook...
```

#### Node.js Verification Example
```javascript
const crypto = require('crypto');

function verifyWebhookSignature(secret, payload, signature) {
  const expected = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');
  return crypto.timingSafeEqual(expected, signature);
}

// In your Express endpoint
app.post('/webhook', (req, res) => {
  const signature = req.headers['x-webhook-signature']?.replace('sha256=', '');

  if (!verifyWebhookSignature(WEBHOOK_SECRET, req.body, signature)) {
    return res.status(401).json({ error: 'Invalid signature' });
  }

  // Process webhook...
});
```

### Best Practices

1. **Use HTTPS Only**: Webhooks must use HTTPS URLs
2. **Verify Signatures**: Always verify HMAC signatures
3. **Validate Event IDs**: Check `event_id` for idempotency
4. **Rate Limiting**: Implement rate limiting on webhook receivers
5. **Secure Secrets**: Store webhook secrets securely
6. **Timeout Handling**: Implement request timeouts
7. **Error Responses**: Return 2xx for successful processing
8. **Logging**: Log all webhook activity for audit trails

### Custom Headers

Add custom headers for additional security:

```python
webhook = await manager.create_webhook(
    name="Secure Webhook",
    url="https://example.com/webhook",
    event_types=["validation.completed"],
    custom_headers={
        "Authorization": "Bearer your-api-key",
        "X-Custom-Header": "custom-value",
        "X-Client-ID": "loki-prod-01"
    }
)
```

---

## Monitoring & Analytics

### Dashboard Metrics

LOKI provides comprehensive metrics for monitoring webhook performance:

```python
# Get webhook-specific analytics
analytics = await manager.get_delivery_analytics(
    webhook_id=1,
    period_days=7
)

print(f"Success Rate: {analytics['success_rate']:.1f}%")
print(f"Avg Response Time: {analytics['avg_response_time_ms']:.0f}ms")
print(f"Total Events: {analytics['total_events']}")
print(f"Failed Deliveries: {analytics['failed_deliveries']}")
```

### Key Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| **Success Rate** | % of deliveries successful | > 99% |
| **Avg Response Time** | Average delivery time | < 500ms |
| **P95 Response Time** | 95th percentile latency | < 2000ms |
| **4xx Errors** | Client error count | 0 |
| **5xx Errors** | Server error count | < 1% |
| **Timeout Errors** | Timeout count | < 0.5% |
| **Retry Rate** | % of events retried | < 5% |

### Alerting Recommendations

Set up alerts for:
- Success rate drops below 95%
- Average response time exceeds 1000ms
- 5xx error rate exceeds 1%
- Webhook hasn't been triggered in 24 hours
- Delivery queue exceeds 1000 pending

### Integration Health Checks

```python
# Check all integrations
health = await integration_manager.integration_health()

for integration_name, status in health['integrations'].items():
    print(f"{integration_name}: {status['status']}")
    if status.get('error'):
        print(f"  Error: {status['error']}")
    if status.get('last_event'):
        print(f"  Last event: {status['last_event']}")
```

---

## Troubleshooting

### Common Issues

#### 1. Webhook Not Receiving Events

**Symptoms**: Webhook created but no deliveries

**Debugging Steps**:
```python
# 1. Check webhook status
webhook = await manager.get_webhook(webhook_id)
print(f"Status: {webhook.status}")  # Should be 'active'

# 2. Test webhook
result = await manager.test_webhook(webhook_id)
print(f"Test result: {result}")  # Should succeed

# 3. Check event subscriptions
print(f"Subscribed to: {webhook.event_types}")

# 4. Verify events are being triggered
events = await manager.get_recent_webhook_events(limit=10)
print(f"Recent events: {events}")
```

**Solutions**:
- Ensure webhook status is `active`
- Check event subscriptions match event types
- Verify webhook URL is correct
- Test with `/test` endpoint
- Check firewall rules allow LOKI to connect

#### 2. High Failure Rate

**Symptoms**: Many deliveries failing, low success rate

**Debugging Steps**:
```python
# 1. Get recent failed deliveries
deliveries = await manager.get_webhook_deliveries(
    webhook_id,
    status_filter="failed",
    limit=10
)

# 2. Examine errors
for delivery in deliveries:
    print(f"Error: {delivery.last_error}")
    print(f"Status Code: {delivery.response_status_code}")

# 3. Check analytics
analytics = await manager.get_delivery_analytics(webhook_id)
print(f"Success Rate: {analytics['success_rate']}%")
```

**Solutions**:
- Check webhook receiver logs for errors
- Verify endpoint is responding
- Check response status codes (4xx vs 5xx)
- Increase timeout if responses are slow
- Check rate limits aren't being exceeded
- Verify signature verification is correct

#### 3. Retries Not Working

**Symptoms**: Failed deliveries not being retried

**Debugging Steps**:
```python
# 1. Check retry configuration
webhook = await manager.get_webhook(webhook_id)
print(f"Retry Strategy: {webhook.retry_strategy}")
print(f"Max Retries: {webhook.max_retries}")
print(f"Retry Delay: {webhook.retry_delay_seconds}s")

# 2. Check delivery status
delivery = await manager.get_delivery_details(webhook_id, delivery_id)
print(f"Status: {delivery.status}")  # Should be 'retrying' if scheduled
print(f"Next Retry: {delivery.next_retry_at}")
print(f"Attempt: {delivery.attempt_number}")
```

**Solutions**:
- Ensure `max_retries > 0`
- Check `next_retry_at` timestamp is in the future
- Verify retry strategy is not `NO_RETRY`
- Manually trigger retry with `/retry` endpoint

#### 4. Integration Not Connecting

**Symptoms**: Integration fails to connect

**Debugging Steps**:
```python
# 1. Test integration
result = await integration_manager.test_integration("integration_name")
print(f"Success: {result['success']}")
if not result['success']:
    print(f"Error: {result.get('error')}")

# 2. Check credentials
integration = integration_manager.get_integration("integration_name")
print(f"Status: {integration.status}")

# 3. Validate credentials separately
is_valid = await integration.validate_credentials()
print(f"Credentials Valid: {is_valid}")
```

**Solutions**:
- Verify credentials are correct
- Check service is accessible (firewall, DNS)
- Verify webhook URL format
- Test with `/test` endpoint
- Check API key/token permissions

### Getting Help

Enable debug logging:
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('webhooks')
logger.setLevel(logging.DEBUG)
```

Check logs for:
- Connection attempts and failures
- Signature verification issues
- Rate limit hits
- Timeout errors
- Retry scheduling

---

## Advanced Topics

### Custom Webhook Payloads

Customize webhook payload format:

```python
webhook = await manager.create_webhook(
    name="Custom Format",
    url="https://example.com/webhook",
    metadata={
        "payload_format": "custom",
        "include_raw_payload": True,
        "compression": "gzip"
    }
)
```

### Webhook Transformations

Apply transformations to payloads:

```python
# Example: Include only specific fields
webhook = await manager.create_webhook(
    name="Minimal Payload",
    url="https://example.com/webhook",
    metadata={
        "transformation_rules": {
            "include_fields": ["event_type", "status", "timestamp"],
            "exclude_fields": ["stack_trace", "request_body"]
        }
    }
)
```

### Rate Limiting Strategies

Configure per-webhook rate limiting:

```python
webhook = await manager.create_webhook(
    name="Rate Limited",
    url="https://example.com/webhook",
    rate_limit_per_minute=30,      # 30 per minute
    rate_limit_per_hour=500,        # 500 per hour
)
```

### Batch Processing

Group events for batch delivery:

```python
# For Zapier or similar batch-friendly services
zapier = ZapierIntegration(
    name="Batch Processor",
    webhook_url="https://hooks.zapier.com/...",
    config={
        'batch_events': True,
        'batch_size': 50,             # Batch after 50 events
        'batch_timeout_seconds': 60,  # Or after 60 seconds
    }
)
```

---

## References

- [Webhook Best Practices](https://webhook.cool/)
- [HMAC-SHA256 RFC 2104](https://tools.ietf.org/html/rfc2104)
- [HTTP Status Codes](https://httpwg.org/specs/rfc7231.html#status.codes)
- [Slack API Documentation](https://api.slack.com/messaging/webhooks)
- [Microsoft Teams Webhooks](https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/connectors-using)
- [Zapier Documentation](https://zapier.com/help/webhooks)

---

**Last Updated**: 2024-01-15
**Version**: 1.0.0
**Author**: LOKI Engineering Team
