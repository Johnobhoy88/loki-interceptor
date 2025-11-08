# API Integration Master

Expert in LOKI API integration patterns, authentication, and optimization.

## LOKI API Architecture

### API Endpoints

**Document Validation:**
```http
POST /validate-document
Content-Type: application/json

{
  "text": "Document text to validate",
  "document_type": "financial|privacy_policy|invoice|disciplinary_notice",
  "modules": ["fca_uk", "gdpr_uk", "tax_uk", "nda_uk", "hr_scottish"]
}
```

**Response:**
```json
{
  "validation": {
    "status": "PASS|FAIL",
    "modules": {
      "fca_uk": {
        "status": "FAIL",
        "gates": {
          "fair_clear_not_misleading": {
            "status": "FAIL",
            "severity": "critical",
            "message": "Guaranteed returns claim detected",
            "legal_source": "FCA COBS 4.2.1R",
            "suggestion": "Remove guarantee language..."
          }
        }
      }
    }
  }
}
```

**Anthropic Interceptor:**
```http
POST /v1/messages
X-API-Key: YOUR_ANTHROPIC_KEY
Content-Type: application/json

{
  "model": "claude-sonnet-4-20250514",
  "max_tokens": 1024,
  "messages": [{"role": "user", "content": "Generate investment advice"}],
  "modules": ["fca_uk", "gdpr_uk"]
}
```

## Integration Patterns

### Pattern 1: Real-Time Validation

```python
import requests

class LOKIClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url

    def validate_document(self, text, document_type, modules=None):
        """
        Validate document against compliance modules

        Args:
            text: Document text
            document_type: Type of document
            modules: List of compliance modules to check

        Returns:
            dict: Validation results
        """
        if modules is None:
            modules = ["fca_uk", "gdpr_uk", "tax_uk", "nda_uk", "hr_scottish"]

        response = requests.post(
            f"{self.base_url}/validate-document",
            json={
                "text": text,
                "document_type": document_type,
                "modules": modules
            },
            timeout=30
        )

        response.raise_for_status()
        return response.json()

# Usage
client = LOKIClient()
results = client.validate_document(
    text="Investment opportunity with guaranteed returns!",
    document_type="financial",
    modules=["fca_uk"]
)

if results['validation']['status'] == 'FAIL':
    print("Compliance violations detected:")
    for module, module_results in results['validation']['modules'].items():
        for gate, gate_result in module_results['gates'].items():
            if gate_result['status'] == 'FAIL':
                print(f"- {gate}: {gate_result['message']}")
```

### Pattern 2: Batch Processing

```python
class LOKIBatchProcessor:
    def __init__(self, client):
        self.client = client

    def validate_batch(self, documents, max_workers=5):
        """
        Validate multiple documents concurrently

        Args:
            documents: List of (text, document_type, modules) tuples
            max_workers: Max concurrent requests

        Returns:
            list: Results for each document
        """
        from concurrent.futures import ThreadPoolExecutor

        def validate_one(doc):
            text, doc_type, modules = doc
            try:
                return self.client.validate_document(text, doc_type, modules)
            except Exception as e:
                return {'error': str(e)}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(validate_one, documents))

        return results

# Usage
documents = [
    ("Financial promotion text", "financial", ["fca_uk"]),
    ("Privacy policy text", "privacy_policy", ["gdpr_uk"]),
    ("Invoice text", "invoice", ["tax_uk"]),
]

processor = LOKIBatchProcessor(client)
results = processor.validate_batch(documents)
```

### Pattern 3: Claude Interceptor Integration

```python
class ClaudeWithLOKI:
    def __init__(self, anthropic_api_key, loki_url="http://localhost:5000"):
        self.anthropic_key = anthropic_api_key
        self.loki_url = loki_url

    def generate_with_compliance(self, prompt, modules=None, max_tokens=1024):
        """
        Generate text with automatic compliance validation

        Args:
            prompt: User prompt for Claude
            modules: LOKI compliance modules to check
            max_tokens: Max tokens to generate

        Returns:
            dict: Generated text + validation results
        """
        # Call LOKI's Anthropic interceptor endpoint
        response = requests.post(
            f"{self.loki_url}/v1/messages",
            headers={
                "X-API-Key": self.anthropic_key,
                "Content-Type": "application/json"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}],
                "modules": modules or ["fca_uk", "gdpr_uk"]
            }
        )

        response.raise_for_status()
        return response.json()

# Usage
claude_loki = ClaudeWithLOKI(anthropic_api_key="sk-ant-...")

result = claude_loki.generate_with_compliance(
    prompt="Write financial advice about investing in stocks",
    modules=["fca_uk"]
)

print("Generated:", result['content'][0]['text'])
print("Compliance:", result.get('validation', {}))
```

## Error Handling

### Graceful Degradation

```python
class RobustLOKIClient:
    def __init__(self, base_url, retries=3, timeout=30):
        self.base_url = base_url
        self.retries = retries
        self.timeout = timeout

    def validate_with_retry(self, text, document_type, modules):
        """
        Validate with automatic retries and error handling

        Returns:
            dict: Validation results or error info
        """
        import time

        for attempt in range(self.retries):
            try:
                response = requests.post(
                    f"{self.base_url}/validate-document",
                    json={"text": text, "document_type": document_type, "modules": modules},
                    timeout=self.timeout
                )

                response.raise_for_status()
                return {
                    'success': True,
                    'data': response.json()
                }

            except requests.exceptions.Timeout:
                if attempt < self.retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                return {
                    'success': False,
                    'error': 'timeout',
                    'message': 'LOKI validation timed out'
                }

            except requests.exceptions.ConnectionError:
                return {
                    'success': False,
                    'error': 'connection_error',
                    'message': 'Cannot connect to LOKI service'
                }

            except requests.exceptions.HTTPError as e:
                return {
                    'success': False,
                    'error': 'http_error',
                    'status_code': e.response.status_code,
                    'message': e.response.text
                }

        return {
            'success': False,
            'error': 'max_retries_exceeded'
        }
```

## Performance Optimization

### Caching Strategy

```python
from functools import lru_cache
import hashlib

class CachedLOKIClient:
    def __init__(self, client):
        self.client = client
        self._cache = {}

    def _cache_key(self, text, document_type, modules):
        """Generate cache key from inputs"""
        modules_str = ','.join(sorted(modules))
        content = f"{text}|{document_type}|{modules_str}"
        return hashlib.sha256(content.encode()).hexdigest()

    def validate_cached(self, text, document_type, modules, ttl=3600):
        """
        Validate with caching

        Args:
            ttl: Cache TTL in seconds

        Returns:
            dict: Validation results (may be cached)
        """
        import time

        cache_key = self._cache_key(text, document_type, modules)

        # Check cache
        if cache_key in self._cache:
            cached_result, cached_time = self._cache[cache_key]
            if time.time() - cached_time < ttl:
                return {
                    **cached_result,
                    'cached': True,
                    'cache_age': time.time() - cached_time
                }

        # Call API
        result = self.client.validate_document(text, document_type, modules)

        # Store in cache
        self._cache[cache_key] = (result, time.time())

        return {
            **result,
            'cached': False
        }
```

### Request Batching

```python
class BatchingLOKIClient:
    def __init__(self, client, batch_size=10, flush_interval=1.0):
        self.client = client
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self._batch = []
        self._results = []
        self._lock = threading.Lock()

    def queue_validation(self, text, document_type, modules):
        """
        Add validation to batch queue

        Returns:
            Future: Will contain results when batch is processed
        """
        import threading
        from concurrent.futures import Future

        future = Future()

        with self._lock:
            self._batch.append((text, document_type, modules, future))

            if len(self._batch) >= self.batch_size:
                self._flush_batch()

        return future

    def _flush_batch(self):
        """Process queued validations"""
        if not self._batch:
            return

        batch = self._batch[:]
        self._batch = []

        # Process batch
        processor = LOKIBatchProcessor(self.client)
        documents = [(text, dt, mods) for text, dt, mods, _ in batch]
        results = processor.validate_batch(documents)

        # Fulfill futures
        for (_, _, _, future), result in zip(batch, results):
            future.set_result(result)
```

## Webhook Integration

### Event-Driven Validation

```python
from flask import Flask, request, jsonify

app = Flask(__name__)
loki_client = LOKIClient()

@app.route('/webhook/document-uploaded', methods=['POST'])
def handle_document_upload():
    """
    Webhook endpoint for document upload events

    Expected payload:
    {
        "document_id": "123",
        "text": "document text",
        "document_type": "financial",
        "callback_url": "https://your-app.com/validation-complete"
    }
    """
    data = request.json

    # Validate document
    results = loki_client.validate_document(
        text=data['text'],
        document_type=data['document_type'],
        modules=data.get('modules', ['fca_uk', 'gdpr_uk'])
    )

    # Send results back
    callback_response = requests.post(
        data['callback_url'],
        json={
            'document_id': data['document_id'],
            'validation_results': results
        }
    )

    return jsonify({'status': 'processed'})
```

## Authentication Patterns

### API Key Authentication

```python
class AuthenticatedLOKIClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def validate_document(self, text, document_type, modules):
        response = requests.post(
            f"{self.base_url}/validate-document",
            headers=self._headers(),
            json={"text": text, "document_type": document_type, "modules": modules}
        )
        response.raise_for_status()
        return response.json()
```

## Best Practices

1. **Always handle errors gracefully** - LOKI service may be unavailable
2. **Implement timeouts** - Prevent hanging requests
3. **Cache results** - Same document doesn't need re-validation
4. **Batch when possible** - More efficient than individual requests
5. **Use appropriate modules** - Don't validate everything against everything
6. **Monitor performance** - Track response times and failures
7. **Implement retries** - With exponential backoff
8. **Validate inputs** - Before sending to LOKI
9. **Handle rate limits** - If implemented
10. **Log requests** - For debugging and auditing

## Resources

- LOKI API server: `backend/server.py`
- Example integrations: `examples/api_client.py`
- Performance tests: `backend/tests/performance/`

## See Also

- `authentication.md` - OAuth2/JWT implementation
- `error-handling.md` - Comprehensive error handling
- `performance.md` - Optimization strategies
- `webhooks.md` - Event-driven integration
