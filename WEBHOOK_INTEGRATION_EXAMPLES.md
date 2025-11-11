# LOKI Webhook Integration Examples

Complete, production-ready examples for implementing webhooks and integrations.

---

## Example 1: Complete Webhook Setup Flow

```python
import asyncio
from backend.webhooks import WebhookManager
from backend.webhooks.event_types import ComplianceAlertEvent

async def setup_webhooks():
    """Set up webhooks for compliance alerts"""
    manager = WebhookManager()

    # Create webhook for compliance alerts
    webhook = await manager.create_webhook(
        name="Compliance Alerts",
        url="https://example.com/webhooks/compliance",
        description="Send all compliance violations",
        event_types=["compliance.alert", "validation.failed"],
        retry_strategy="exponential_backoff",
        max_retries=5,
        retry_delay_seconds=60,
        rate_limit_per_minute=60,
        rate_limit_per_hour=3600,
        custom_headers={
            "Authorization": "Bearer your-api-key",
            "X-Service-ID": "loki-prod-01"
        },
        metadata={
            "team": "compliance",
            "priority": "critical",
            "notify_on_failure": True
        }
    )

    print(f"Created webhook: {webhook.name}")
    print(f"ID: {webhook.id}")
    print(f"Secret: {webhook.secret}")

    # Test the webhook
    test_result = await manager.test_webhook(webhook.id)
    print(f"Test result: {test_result}")

    return webhook


async def trigger_compliance_alert():
    """Trigger a compliance alert to all subscribed webhooks"""
    manager = WebhookManager()

    # Create alert event
    alert = ComplianceAlertEvent(
        source_id="doc_12345",
        alert_level="critical",
        alert_type="gdpr_violation",
        message="Personal email addresses found in marketing document",
        affected_documents=["doc_12345", "doc_12346"],
        recommended_actions=[
            "Immediately redact personal data",
            "Review GDPR Article 5 compliance",
            "Notify data subjects within 72 hours"
        ]
    )

    # Trigger event (sends to all subscribed webhooks)
    result = await manager.trigger_event(alert)

    print(f"Event ID: {result['event_id']}")
    print(f"Delivered to {result['successful']} of {result['deliveries']} webhooks")
    print(f"Details: {result['results']}")

    return result


async def monitor_webhook():
    """Monitor webhook performance and analytics"""
    manager = WebhookManager()
    webhook_id = 1

    # Get delivery history
    deliveries = await manager.get_webhook_deliveries(
        webhook_id,
        status_filter="failed",
        limit=20
    )

    print(f"Failed deliveries in last 24 hours:")
    for delivery in deliveries:
        print(f"  - {delivery.event_type}: {delivery.last_error}")

    # Get analytics
    analytics = await manager.get_delivery_analytics(
        webhook_id,
        period_days=7
    )

    print(f"\n7-Day Analytics:")
    print(f"  Total Events: {analytics['total_events']}")
    print(f"  Success Rate: {analytics['success_rate']:.1f}%")
    print(f"  Avg Response Time: {analytics['avg_response_time_ms']:.0f}ms")
    print(f"  P95 Response Time: {analytics['p95_response_time_ms']:.0f}ms")

    return analytics
```

---

## Example 2: Multi-Integration Setup

```python
from backend.integrations import IntegrationManager

async def setup_multi_channel_notifications():
    """Set up notifications across multiple platforms"""
    manager = IntegrationManager()

    # Register Slack integration
    await manager.register_integration(
        name="Slack Compliance Channel",
        integration_type="slack",
        credentials={
            "webhook_url": "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX"
        },
        config={
            "default_channel": "#compliance-alerts",
            "include_footer": True,
            "include_timestamp": True
        },
        event_subscriptions=[
            "compliance.alert",
            "validation.failed",
            "batch.completed"
        ]
    )

    # Register Teams integration
    await manager.register_integration(
        name="Teams Risk Management",
        integration_type="teams",
        credentials={
            "webhook_url": "https://outlook.webhook.office.com/webhookb2/..."
        },
        config={
            "theme_color": "dc3545",  # Red for alerts
        },
        event_subscriptions=[
            "compliance.alert",
            "system.error"
        ]
    )

    # Register Email integration
    await manager.register_integration(
        name="Email Alert Distribution",
        integration_type="email",
        credentials={
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_username": "alerts@company.com",
            "smtp_password": "app-specific-password",
            "from_address": "loki-alerts@company.com"
        },
        config={
            "default_recipients": [
                "compliance@company.com",
                "cto@company.com",
                "legal@company.com"
            ],
            "html_format": True
        },
        event_subscriptions=[
            "compliance.alert",
            "system.error",
            "batch.completed"
        ]
    )

    # Register Zapier integration for workflow automation
    await manager.register_integration(
        name="Zapier Workflow Hub",
        integration_type="zapier",
        credentials={
            "webhook_url": "https://hooks.zapier.com/hooks/catch/YOUR_ID/"
        },
        config={
            "batch_events": True,
            "batch_size": 10,
            "batch_timeout_seconds": 30
        },
        event_subscriptions=[
            "batch.completed",
            "report.generated"
        ]
    )

    print("All integrations registered successfully!")

    # Test each integration
    integrations = manager.list_integrations()
    for integration in integrations:
        print(f"\nTesting {integration['name']}...")
        result = await manager.test_integration(integration['name'])
        status = "✓ Connected" if result['success'] else "✗ Failed"
        print(f"  Status: {status}")


async def route_event_to_integrations():
    """Route an event to all subscribed integrations"""
    manager = IntegrationManager()

    # Create alert event
    from backend.webhooks.event_types import ComplianceAlertEvent

    alert = ComplianceAlertEvent(
        source_id="batch_001",
        alert_level="high",
        alert_type="fca_violation",
        message="Potential FCA rule 2.1.1.1 violation in batch",
        affected_documents=[
            "doc_001", "doc_002", "doc_003"
        ],
        recommended_actions=[
            "Review FCA handbook rules 2.1.1.1",
            "Check consumer communication standards",
            "Verify risk warnings are adequate"
        ]
    )

    # Route event to all subscribed integrations
    result = await manager.route_event("compliance.alert", alert.to_dict())

    print(f"Event routed to {result['routed_to']} integrations:")
    for integration_name, delivery_result in result['results'].items():
        status = "✓ Success" if delivery_result['success'] else "✗ Failed"
        print(f"  {integration_name}: {status}")

    return result
```

---

## Example 3: Advanced Retry Configuration

```python
from backend.webhooks import WebhookManager
from backend.webhooks.retry_handler import RetryConfig, RetryStrategy
import asyncio

async def create_webhook_with_custom_retry():
    """Create webhook with custom retry strategy"""

    # Configure exponential backoff with custom parameters
    config = RetryConfig(
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        max_retries=10,
        initial_delay_seconds=30,
        max_delay_seconds=7200,  # 2 hours
        backoff_multiplier=1.5,
        jitter_enabled=True,
        jitter_percentage=0.2  # 20% jitter
    )

    manager = WebhookManager(config=config)

    # Create webhook with critical retry configuration
    webhook = await manager.create_webhook(
        name="Critical Alerts",
        url="https://critical-service.example.com/webhook",
        description="Critical compliance alerts with aggressive retries",
        event_types=["compliance.alert"],
        retry_strategy="exponential_backoff",
        max_retries=10,
        retry_delay_seconds=30,
        rate_limit_per_minute=100
    )

    # Get retry schedule
    schedule = manager.retry_handler.create_retry_schedule(webhook.id)

    print(f"Retry Schedule for {webhook.name}:")
    print(f"Total potential retry time: {schedule['total_retry_time_seconds']} seconds")
    print("\nRetry attempts:")

    for attempt in schedule['attempts']:
        print(f"  Attempt {attempt['attempt']}: "
              f"Delay {attempt['delay_seconds']}s, "
              f"Retry at {attempt['retry_at']}")

    return webhook


async def simulate_delivery_with_retries():
    """Simulate a delivery with retry attempts"""
    from backend.webhooks.event_types import ValidationCompletedEvent

    manager = WebhookManager()
    webhook_id = 1

    # Simulate a delivery that fails initially
    print("Simulating delivery with retries...")

    # First attempt - fails
    print("\n✗ Attempt 1: Connection timeout")

    # System schedules retry
    next_delay = manager.retry_handler.calculate_next_retry_delay(2)
    print(f"→ Scheduled retry in {next_delay} seconds")

    # Wait a moment
    await asyncio.sleep(1)

    # Second attempt - fails
    print("\n✗ Attempt 2: 503 Service Unavailable")
    next_delay = manager.retry_handler.calculate_next_retry_delay(3)
    print(f"→ Scheduled retry in {next_delay} seconds")

    # Third attempt - succeeds
    print("\n✓ Attempt 3: Successfully delivered (200 OK)")
    print("→ No further retries needed")

    print("\nRetry statistics:")
    metrics = manager.retry_handler.get_retry_metrics()
    print(f"  Total retries: {metrics['total_retries']}")
    print(f"  Successful: {metrics['successful_retries']}")
    print(f"  Failed: {metrics['permanent_failures']}")
    print(f"  Success rate: {metrics['success_rate']:.1f}%")
```

---

## Example 4: Webhook Testing Suite

```python
from backend.webhooks.testing import WebhookTester

async def comprehensive_webhook_testing():
    """Run comprehensive webhook tests"""
    tester = WebhookTester()

    print("=" * 60)
    print("WEBHOOK TESTING SUITE")
    print("=" * 60)

    # Test 1: Connectivity
    print("\n1. Testing Connectivity...")
    connectivity = await tester.test_webhook_connectivity(
        "https://example.com/webhook"
    )
    print(f"   Reachable: {connectivity['reachable']}")
    print(f"   Status Code: {connectivity.get('status_code', 'N/A')}")
    print(f"   Duration: {connectivity['duration_ms']:.0f}ms")

    # Test 2: Signature Verification
    print("\n2. Testing Signature Verification...")
    sig_test = await tester.test_signature_verification("webhook-secret-xyz")
    print(f"   Signature Generated: {sig_test['signature_generated']}")
    print(f"   Valid with correct secret: {sig_test['verification_correct_secret']}")
    print(f"   Invalid with wrong secret: {sig_test['verification_incorrect_secret']}")
    print(f"   Test Passed: {sig_test['test_passed']}")

    # Test 3: Event Payload Generation
    print("\n3. Testing Event Payload Generation...")
    event_types = [
        "validation.completed",
        "validation.failed",
        "compliance.alert",
        "batch.completed"
    ]

    for event_type in event_types:
        result = await tester.test_event_payload_generation(event_type)
        if result['success']:
            print(f"   ✓ {event_type}: {result['payload_size_bytes']} bytes")
        else:
            print(f"   ✗ {event_type}: {result.get('error', 'Unknown error')}")

    # Test 4: Load Testing
    print("\n4. Load Testing (10 concurrent, 100 total requests)...")
    load_test = await tester.load_test_webhook(
        webhook_url="https://example.com/webhook",
        concurrent_requests=10,
        total_requests=100,
        secret="webhook-secret-xyz"
    )

    print(f"   Successful: {load_test['successful']}")
    print(f"   Failed: {load_test['failed']}")
    if load_test.get('statistics'):
        stats = load_test['statistics']
        print(f"   Success Rate: {stats['success_rate']:.1f}%")
        print(f"   Requests/sec: {stats['requests_per_second']:.1f}")
        print(f"   Avg Response: {stats['avg_response_time_ms']:.0f}ms")
        print(f"   P95 Response: {stats['p95_response_time_ms']:.0f}ms")
        print(f"   Total Time: {stats['total_duration_seconds']:.1f}s")

    print("\n" + "=" * 60)
```

---

## Example 5: Integration Health Monitoring

```python
from backend.integrations import IntegrationManager

async def monitor_integration_health():
    """Monitor health of all integrations"""
    manager = IntegrationManager()

    print("=" * 70)
    print("INTEGRATION HEALTH REPORT")
    print("=" * 70)

    # Get all integrations
    integrations = manager.list_integrations()

    print(f"\nTotal Integrations: {len(integrations)}")
    print("\nIntegration Status:")
    print("-" * 70)

    for integration in integrations:
        print(f"\n{integration['name']}:")
        print(f"  Type: {integration['type']}")
        print(f"  Status: {integration['status']}")
        print(f"  Created: {integration['created_at']}")
        if integration['last_event_at']:
            print(f"  Last Event: {integration['last_event_at']}")

    # Get manager metrics
    metrics = manager.get_metrics()

    print("\n" + "-" * 70)
    print("OVERALL METRICS:")
    print(f"  Total Integrations: {metrics['total_integrations']}")
    print(f"  Total Subscriptions: {metrics['total_subscriptions']}")
    print(f"  Events Routed: {metrics['total_events_routed']}")
    print(f"  Successful Deliveries: {metrics['successful_deliveries']}")
    print(f"  Failed Deliveries: {metrics['failed_deliveries']}")
    print(f"  Success Rate: {metrics['success_rate']:.1f}%")

    # Get subscriptions
    print("\n" + "-" * 70)
    print("EVENT SUBSCRIPTIONS:")
    subscriptions = manager.get_subscriptions()

    for event_type, subs in subscriptions.items():
        print(f"\n{event_type}:")
        for sub in subs:
            print(f"  → {sub}")

    print("\n" + "=" * 70)
```

---

## Example 6: Real-World Scenario

```python
import asyncio
from datetime import datetime
from backend.webhooks import WebhookManager
from backend.integrations import IntegrationManager
from backend.webhooks.event_types import (
    ValidationCompletedEvent,
    ComplianceAlertEvent,
    BatchCompletedEvent
)

async def production_workflow():
    """
    Production workflow:
    1. Validate batch of documents
    2. If compliance issues found, alert all channels
    3. Log results and send summary email
    """

    webhook_manager = WebhookManager()
    integration_manager = IntegrationManager()

    print("PRODUCTION WORKFLOW EXAMPLE")
    print("=" * 70)
    print(f"Start Time: {datetime.utcnow().isoformat()}\n")

    # STEP 1: Batch validation completes
    print("Step 1: Batch validation completed")
    validation_event = ValidationCompletedEvent(
        source_id="batch_daily_001",
        document_id="batch_daily_001",
        validation_status="pass_with_warnings",
        gates_passed=998,
        gates_failed=2,
        issues=[
            {"gate": "GDPR_COMPLIANCE", "severity": "high"},
            {"gate": "FCA_RULES", "severity": "medium"}
        ],
        processing_time_ms=45230.5
    )

    # Trigger validation event (goes to all subscribed webhooks)
    await webhook_manager.trigger_event(validation_event)
    print("  → Validation event triggered to all webhooks\n")

    # STEP 2: Compliance issues detected
    print("Step 2: Compliance violations detected")
    compliance_alert = ComplianceAlertEvent(
        source_id="batch_daily_001",
        alert_level="high",
        alert_type="gdpr_violation",
        message="GDPR compliance violation detected in 2 documents. "
                "Personal data found without proper consent notice.",
        affected_documents=[
            "batch_daily_001_doc_042",
            "batch_daily_001_doc_157"
        ],
        recommended_actions=[
            "Review GDPR Article 13 compliance requirements",
            "Add consent notice to documents",
            "Verify data processing documentation",
            "Notify data protection officer"
        ]
    )

    # Route alert to integrations (Slack, Teams, Email)
    result = await integration_manager.route_event(
        "compliance.alert",
        compliance_alert.to_dict()
    )
    print(f"  → Alert routed to {result['routed_to']} integrations")
    print(f"  → Slack: {'✓ Sent' if result['results'].get('Slack Compliance Channel', {}).get('success') else '✗ Failed'}")
    print(f"  → Teams: {'✓ Sent' if result['results'].get('Teams Risk Management', {}).get('success') else '✗ Failed'}")
    print(f"  → Email: {'✓ Sent' if result['results'].get('Email Alert Distribution', {}).get('success') else '✗ Failed'}\n")

    # STEP 3: Batch processing completes
    print("Step 3: Batch processing completed")
    batch_event = BatchCompletedEvent(
        source_id="batch_daily_001",
        batch_id="batch_daily_001",
        total_documents=1000,
        processed_documents=998,
        failed_documents=2,
        processing_time_ms=45230.5,
        results_summary={
            "compliance_issues": 2,
            "average_confidence": 0.96,
            "documents_passed": 998,
            "documents_with_warnings": 2
        }
    )

    # Trigger batch completion (triggers webhooks and integrations)
    webhook_result = await webhook_manager.trigger_event(batch_event)
    integration_result = await integration_manager.route_event(
        "batch.completed",
        batch_event.to_dict()
    )

    print(f"  → Webhooks triggered: {webhook_result['deliveries']}")
    print(f"  → Integrations triggered: {integration_result['routed_to']}\n")

    # STEP 4: Get analytics
    print("Step 4: Analytics and reporting")
    analytics = await webhook_manager.get_delivery_analytics(
        webhook_id=1,
        period_days=7
    )

    print(f"  → 7-day success rate: {analytics['success_rate']:.1f}%")
    print(f"  → Total events: {analytics['total_events']}")
    print(f"  → Avg response time: {analytics['avg_response_time_ms']:.0f}ms")

    manager_metrics = integration_manager.get_metrics()
    print(f"  → Total integrations: {manager_metrics['total_integrations']}")
    print(f"  → Integration success rate: {manager_metrics['success_rate']:.1f}%\n")

    print("=" * 70)
    print(f"End Time: {datetime.utcnow().isoformat()}")
    print("Workflow completed successfully!")


# Run the example
if __name__ == "__main__":
    asyncio.run(production_workflow())
```

---

## Example 7: Custom Integration Template

```python
from backend.integrations import BaseIntegration, IntegrationStatus
from typing import Dict, Any

class CustomIntegration(BaseIntegration):
    """
    Template for creating custom integrations
    """

    def __init__(
        self,
        name: str,
        api_endpoint: str,
        api_key: str,
        config: Dict[str, Any] = None
    ):
        credentials = {
            'api_endpoint': api_endpoint,
            'api_key': api_key
        }

        config = config or {}
        config.setdefault('timeout_seconds', 30)
        config.setdefault('retry_on_failure', True)

        super().__init__(
            name=name,
            integration_type='custom',
            credentials=credentials,
            config=config
        )

    async def connect(self) -> bool:
        """Connect to custom service"""
        try:
            is_valid = await self.validate_credentials()
            if is_valid:
                self.status = IntegrationStatus.CONNECTED
            return is_valid
        except Exception as e:
            self.status = IntegrationStatus.ERROR
            return False

    async def disconnect(self) -> bool:
        """Disconnect from custom service"""
        self.status = IntegrationStatus.DISCONNECTED
        return True

    async def validate_credentials(self) -> bool:
        """Validate API credentials"""
        # Implement custom validation logic
        return True

    async def send_message(self, message: Dict[str, Any]) -> bool:
        """Send message to custom service"""
        # Implement custom message sending logic
        import aiohttp

        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f"Bearer {self.credentials['api_key']}",
                    'Content-Type': 'application/json'
                }

                async with session.post(
                    self.credentials['api_endpoint'],
                    json=message,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(
                        total=self.config.get('timeout_seconds', 30)
                    )
                ) as response:
                    return response.status < 400

        except Exception as e:
            return False


# Usage
async def use_custom_integration():
    """Example of using custom integration"""

    custom = CustomIntegration(
        name="My Custom Service",
        api_endpoint="https://api.myservice.com/webhooks",
        api_key="sk_prod_1234567890",
        config={
            'timeout_seconds': 60,
            'retry_on_failure': True
        }
    )

    await custom.connect()

    message = {
        'event_type': 'compliance.alert',
        'payload': {
            'message': 'Custom service notification',
            'severity': 'high'
        }
    }

    success = await custom.send_message(message)
    print(f"Message sent: {success}")
```

---

## Running the Examples

```bash
# Run single example
python -m asyncio -c "
import asyncio
from examples import setup_webhooks
asyncio.run(setup_webhooks())
"

# Run comprehensive test
python -m asyncio -c "
import asyncio
from examples import comprehensive_webhook_testing
asyncio.run(comprehensive_webhook_testing())
"

# Run production workflow
python -m asyncio -c "
import asyncio
from examples import production_workflow
asyncio.run(production_workflow())
"
```

---

**Last Updated**: 2024-01-15
**Version**: 1.0.0
