"""
Webhook Testing Interface

Comprehensive testing utilities for webhook development and debugging.
"""

import asyncio
import json
import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import aiohttp

from .manager import WebhookManager
from .event_types import (
    WebhookEvent,
    ValidationCompletedEvent,
    ValidationFailedEvent,
    CorrectionAppliedEvent,
    DocumentProcessedEvent,
    ComplianceAlertEvent,
    BatchCompletedEvent,
)
from .retry_handler import WebhookSignatureVerifier


logger = logging.getLogger(__name__)


class WebhookTester:
    """
    Comprehensive webhook testing interface

    Features:
    - Test webhook connectivity
    - Send test events with various payloads
    - Verify signature generation and validation
    - Load testing with concurrent deliveries
    - Latency and performance profiling
    - Response validation
    """

    def __init__(self, manager: Optional[WebhookManager] = None):
        """
        Initialize webhook tester

        Args:
            manager: WebhookManager instance
        """
        self.manager = manager or WebhookManager()
        self.test_results: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, Any] = {}

    async def test_webhook_connectivity(self, webhook_url: str) -> Dict[str, Any]:
        """
        Test basic webhook connectivity

        Args:
            webhook_url: URL to test

        Returns:
            Connectivity test results
        """
        start_time = time.time()
        test_payload = {
            'event_type': 'test',
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'Webhook connectivity test',
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook_url,
                    json=test_payload,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    duration_ms = (time.time() - start_time) * 1000

                    result = {
                        'success': response.status < 400,
                        'status_code': response.status,
                        'duration_ms': duration_ms,
                        'reachable': True,
                    }

                    # Try to read response body
                    try:
                        response_text = await response.text()
                        result['response_length'] = len(response_text)
                    except:
                        pass

                    return result

        except asyncio.TimeoutError:
            return {
                'success': False,
                'reachable': False,
                'error': 'Request timeout (>10s)',
                'duration_ms': (time.time() - start_time) * 1000,
            }
        except aiohttp.ClientConnectorError as e:
            return {
                'success': False,
                'reachable': False,
                'error': f'Connection failed: {str(e)}',
            }
        except Exception as e:
            return {
                'success': False,
                'reachable': False,
                'error': f'Unexpected error: {str(e)}',
            }

    async def test_signature_verification(self, secret: str) -> Dict[str, Any]:
        """
        Test HMAC-SHA256 signature generation and verification

        Args:
            secret: Webhook secret

        Returns:
            Signature test results
        """
        payload = {'test': 'payload', 'timestamp': datetime.utcnow().isoformat()}
        payload_json = json.dumps(payload, default=str)
        payload_bytes = payload_json.encode('utf-8')

        # Generate signature
        signature = WebhookSignatureVerifier.generate_signature(secret, payload_bytes)

        # Verify with correct secret
        verified_correct = WebhookSignatureVerifier.verify_signature(
            secret, payload_bytes, signature
        )

        # Verify with incorrect secret
        verified_incorrect = WebhookSignatureVerifier.verify_signature(
            secret + 'wrong', payload_bytes, signature
        )

        return {
            'signature_generated': True,
            'signature': signature,
            'verification_correct_secret': verified_correct,
            'verification_incorrect_secret': verified_incorrect,
            'test_passed': verified_correct and not verified_incorrect,
        }

    async def test_event_payload_generation(self, event_type: str) -> Dict[str, Any]:
        """
        Test event payload generation

        Args:
            event_type: Type of event to generate

        Returns:
            Event payload test results
        """
        try:
            if event_type == 'validation.completed':
                event = ValidationCompletedEvent(
                    source_id='test_validation_001',
                    document_id='doc_001',
                    validation_status='pass',
                    gates_passed=8,
                    gates_failed=0,
                    issues=[],
                    processing_time_ms=523.45,
                )
            elif event_type == 'validation.failed':
                event = ValidationFailedEvent(
                    source_id='test_validation_002',
                    document_id='doc_002',
                    error_message='Validation engine timeout',
                    error_code='VALIDATION_TIMEOUT',
                )
            elif event_type == 'correction.applied':
                event = CorrectionAppliedEvent(
                    source_id='test_correction_001',
                    document_id='doc_001',
                    corrections_count=3,
                    changes=[
                        {'rule': 'GDPR_REDACTION', 'text': 'personal email'},
                        {'rule': 'WHITESPACE_NORMALIZATION', 'text': '  '},
                        {'rule': 'MARKUP_REMOVAL', 'text': '<script>'},
                    ],
                    before_text='Original text with personal data...',
                    after_text='Corrected text with redactions...',
                    confidence_score=0.95,
                )
            elif event_type == 'document.processed':
                event = DocumentProcessedEvent(
                    source_id='test_document_001',
                    document_id='doc_001',
                    document_type='contract',
                    file_size_bytes=24576,
                    processing_time_ms=1234.56,
                    validation_results={
                        'status': 'pass',
                        'gates_passed': 8,
                        'gates_failed': 0,
                    },
                    corrections_applied=True,
                )
            elif event_type == 'compliance.alert':
                event = ComplianceAlertEvent(
                    source_id='test_alert_001',
                    alert_level='high',
                    alert_type='fca_violation',
                    message='Potential FCA rule 2.1.1 violation',
                    affected_documents=['doc_001', 'doc_002'],
                    recommended_actions=[
                        'Review FCA rules 2.1.1',
                        'Check document content for breaches',
                    ],
                )
            elif event_type == 'batch.completed':
                event = BatchCompletedEvent(
                    source_id='test_batch_001',
                    batch_id='batch_001',
                    total_documents=500,
                    processed_documents=498,
                    failed_documents=2,
                    processing_time_ms=45230.5,
                    results_summary={
                        'average_confidence': 0.94,
                        'compliance_issues': 12,
                    },
                )
            else:
                return {'success': False, 'error': f'Unknown event type: {event_type}'}

            payload = event.to_dict()
            payload_size = len(json.dumps(payload, default=str))

            return {
                'success': True,
                'event_type': event_type,
                'payload': payload,
                'payload_size_bytes': payload_size,
                'event_id': event.event_id,
            }

        except Exception as e:
            return {
                'success': False,
                'event_type': event_type,
                'error': str(e),
            }

    async def load_test_webhook(
        self,
        webhook_url: str,
        concurrent_requests: int = 10,
        total_requests: int = 100,
        secret: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Load test a webhook with concurrent deliveries

        Args:
            webhook_url: Webhook URL to test
            concurrent_requests: Number of concurrent requests
            total_requests: Total number of requests
            secret: Optional secret for signature verification

        Returns:
            Load test results
        """
        results = {
            'total_requests': total_requests,
            'concurrent_requests': concurrent_requests,
            'successful': 0,
            'failed': 0,
            'response_times': [],
            'status_codes': [],
            'errors': [],
            'start_time': datetime.utcnow().isoformat(),
        }

        async def make_request(session, request_num):
            payload = {
                'request_number': request_num,
                'timestamp': datetime.utcnow().isoformat(),
                'test': True,
            }
            payload_json = json.dumps(payload, default=str)
            payload_bytes = payload_json.encode('utf-8')

            headers = {'Content-Type': 'application/json'}

            if secret:
                signature = WebhookSignatureVerifier.generate_signature(secret, payload_bytes)
                headers['X-Webhook-Signature'] = f"sha256={signature}"

            start = time.time()

            try:
                async with session.post(
                    webhook_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    duration = (time.time() - start) * 1000
                    return {
                        'success': response.status < 400,
                        'status_code': response.status,
                        'duration_ms': duration,
                    }
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'duration_ms': (time.time() - start) * 1000,
                }

        start_time = time.time()

        async with aiohttp.ClientSession() as session:
            semaphore = asyncio.Semaphore(concurrent_requests)

            async def bounded_request(request_num):
                async with semaphore:
                    return await make_request(session, request_num)

            tasks = [bounded_request(i) for i in range(total_requests)]
            responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for response in responses:
            if isinstance(response, Exception):
                results['failed'] += 1
                results['errors'].append(str(response))
            elif response.get('success'):
                results['successful'] += 1
                results['response_times'].append(response['duration_ms'])
                results['status_codes'].append(response['status_code'])
            else:
                results['failed'] += 1
                results['response_times'].append(response.get('duration_ms', 0))
                if 'error' in response:
                    results['errors'].append(response['error'])

        total_duration = (time.time() - start_time)

        # Calculate statistics
        if results['response_times']:
            response_times = sorted(results['response_times'])
            results['statistics'] = {
                'total_duration_seconds': total_duration,
                'requests_per_second': total_requests / total_duration,
                'avg_response_time_ms': sum(response_times) / len(response_times),
                'min_response_time_ms': response_times[0],
                'max_response_time_ms': response_times[-1],
                'p50_response_time_ms': response_times[len(response_times) // 2],
                'p95_response_time_ms': response_times[int(len(response_times) * 0.95)],
                'p99_response_time_ms': response_times[int(len(response_times) * 0.99)],
                'success_rate': (results['successful'] / total_requests) * 100,
            }

        results['end_time'] = datetime.utcnow().isoformat()

        return results

    async def test_all_event_types(self) -> Dict[str, Any]:
        """
        Test payload generation for all event types

        Returns:
            Results for all event types
        """
        event_types = [
            'validation.completed',
            'validation.failed',
            'correction.applied',
            'document.processed',
            'compliance.alert',
            'batch.completed',
        ]

        results = {
            'total_events': len(event_types),
            'tested': 0,
            'passed': 0,
            'failed': 0,
            'events': {},
        }

        for event_type in event_types:
            result = await self.test_event_payload_generation(event_type)
            results['events'][event_type] = result
            results['tested'] += 1

            if result.get('success'):
                results['passed'] += 1
            else:
                results['failed'] += 1

        return results

    async def test_retry_logic(
        self,
        webhook_id: int,
        failure_rate: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Test retry logic with simulated failures

        Args:
            webhook_id: Webhook ID to test
            failure_rate: Rate of failures to simulate (0-1)

        Returns:
            Retry test results
        """
        results = {
            'webhook_id': webhook_id,
            'failure_rate': failure_rate,
            'retries_triggered': 0,
            'retries_successful': 0,
            'retries_failed': 0,
        }

        # This would be implemented with actual webhook delivery simulation
        logger.info(f"Testing retry logic for webhook {webhook_id}")

        return results

    def generate_test_report(self) -> str:
        """
        Generate a comprehensive test report

        Returns:
            Formatted test report
        """
        report = [
            "=" * 80,
            "WEBHOOK TESTING REPORT",
            "=" * 80,
            f"Generated: {datetime.utcnow().isoformat()}",
            "",
            "TEST RESULTS SUMMARY",
            "-" * 80,
            f"Total Tests: {len(self.test_results)}",
            "",
        ]

        if self.performance_metrics:
            report.append("PERFORMANCE METRICS")
            report.append("-" * 80,)
            for metric, value in self.performance_metrics.items():
                if isinstance(value, float):
                    report.append(f"{metric}: {value:.2f}")
                else:
                    report.append(f"{metric}: {value}")
            report.append("")

        return "\n".join(report)


class WebhookSimulator:
    """
    Simulates webhook server for testing

    Useful for testing webhook clients without external infrastructure.
    """

    def __init__(self, port: int = 8765):
        """
        Initialize webhook simulator

        Args:
            port: Port to listen on
        """
        self.port = port
        self.received_events: List[Dict[str, Any]] = []
        self.should_fail = False
        self.response_delay_ms = 0

    async def receive_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Receive and store webhook

        Args:
            payload: Webhook payload

        Returns:
            Response dictionary
        """
        event = {
            'received_at': datetime.utcnow().isoformat(),
            'payload': payload,
        }

        self.received_events.append(event)

        if self.response_delay_ms > 0:
            await asyncio.sleep(self.response_delay_ms / 1000)

        if self.should_fail:
            return {'success': False, 'error': 'Simulated failure'}

        return {'success': True, 'event_id': payload.get('event_id')}

    def get_received_events(self) -> List[Dict[str, Any]]:
        """Get all received events"""
        return self.received_events

    def clear_events(self):
        """Clear received events"""
        self.received_events = []

    def get_event_count(self) -> int:
        """Get count of received events"""
        return len(self.received_events)
