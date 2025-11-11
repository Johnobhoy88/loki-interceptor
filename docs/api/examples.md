# API Integration Examples

Complete examples showing how to use the LOKI Interceptor API in various languages and frameworks.

## Table of Contents
- [Python Examples](#python-examples)
- [JavaScript Examples](#javascript-examples)
- [cURL Examples](#curl-examples)
- [Postman Collections](#postman-collections)

---

## Python Examples

### Basic Validation (requests)

```python
import requests
import json

# Configuration
API_URL = "http://localhost:8000/api/v1"
DOCUMENT_TEXT = """
Investment Opportunity - Guaranteed 15% Returns!

Our fund has delivered consistent 15% annual returns for 3 years.
Zero risk investment suitable for everyone. Limited time offer!
"""

# Validate document
def validate_document():
    response = requests.post(
        f"{API_URL}/validate",
        json={
            "text": DOCUMENT_TEXT,
            "document_type": "financial_promotion",
            "modules": ["fca_uk"],
            "use_cache": False,
            "include_suggestions": True
        },
        timeout=30
    )

    if response.status_code == 200:
        result = response.json()
        print(f"Overall Risk: {result['risk']}")
        print(f"Validation Modules: {len(result['validation']['modules'])}")

        for module in result['validation']['modules']:
            print(f"\n{module['module_name']}:")
            print(f"  Gates Checked: {module['gates_checked']}")
            print(f"  Gates Failed: {module['gates_failed']}")

            for gate in module['gates']:
                if not gate['passed']:
                    print(f"  ❌ {gate['gate_name']}: {gate['message']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.json())

if __name__ == "__main__":
    validate_document()
```

### Async Validation (aiohttp)

```python
import asyncio
import aiohttp

API_URL = "http://localhost:8000/api/v1"

async def validate_async(text, document_type, modules):
    """Asynchronously validate a document"""
    async with aiohttp.ClientSession() as session:
        payload = {
            "text": text,
            "document_type": document_type,
            "modules": modules,
            "use_cache": True
        }

        async with session.post(
            f"{API_URL}/validate",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"API Error: {response.status}")

async def process_multiple_documents(documents):
    """Process multiple documents concurrently"""
    tasks = [
        validate_async(
            doc['text'],
            doc['document_type'],
            doc['modules']
        ) for doc in documents
    ]

    results = await asyncio.gather(*tasks)
    return results

# Usage
documents = [
    {
        "text": "Employment contract...",
        "document_type": "employment_contract",
        "modules": ["hr_scottish"]
    },
    {
        "text": "Privacy policy...",
        "document_type": "privacy_policy",
        "modules": ["gdpr_uk"]
    }
]

results = asyncio.run(process_multiple_documents(documents))
print(f"Processed {len(results)} documents")
```

### Validation with Automatic Correction

```python
import requests

def validate_and_correct(text, document_type, modules):
    """Validate and automatically correct a document"""

    api_url = "http://localhost:8000/api/v1"

    # Step 1: Validate
    print("Step 1: Validating document...")
    validation_response = requests.post(
        f"{api_url}/validate",
        json={
            "text": text,
            "document_type": document_type,
            "modules": modules,
            "use_cache": False
        }
    )

    if validation_response.status_code != 200:
        print(f"Validation failed: {validation_response.json()}")
        return None

    validation_result = validation_response.json()
    print(f"Overall Risk: {validation_result['risk']}")

    # Step 2: Correct
    print("Step 2: Applying corrections...")
    correction_response = requests.post(
        f"{api_url}/correct",
        json={
            "text": text,
            "validation_results": validation_result['validation'],
            "auto_apply": True,
            "confidence_threshold": 0.8
        }
    )

    if correction_response.status_code != 200:
        print(f"Correction failed: {correction_response.json()}")
        return None

    correction_result = correction_response.json()

    # Step 3: Display results
    print(f"\nIssues Found: {correction_result['issues_found']}")
    print(f"Issues Corrected: {correction_result['issues_corrected']}")

    if correction_result['corrections']:
        print("\nCorrections Applied:")
        for i, corr in enumerate(correction_result['corrections'], 1):
            print(f"{i}. {corr['reason']}")
            print(f"   Before: {corr['original']}")
            print(f"   After: {corr['corrected']}")
            print(f"   Confidence: {corr['confidence']:.0%}")

    return {
        "original": text,
        "corrected": correction_result['corrected_text'],
        "validation": validation_result,
        "correction": correction_result
    }

# Usage
text = """
We collect your data for marketing purposes.
By using our site you agree to all data collection.
We share your data with any third parties we choose.
"""

result = validate_and_correct(text, "privacy_policy", ["gdpr_uk"])

if result:
    print("\n" + "="*50)
    print("ORIGINAL:")
    print(result['original'])
    print("\n" + "="*50)
    print("CORRECTED:")
    print(result['corrected'])
```

### Batch Processing

```python
import requests
from pathlib import Path

def batch_validate_files(directory_path, document_type, modules):
    """Validate all text files in a directory"""

    api_url = "http://localhost:8000/api/v1"
    documents = []

    # Load documents
    for filepath in Path(directory_path).glob("*.txt"):
        with open(filepath, 'r') as f:
            documents.append({
                "text": f.read(),
                "document_type": document_type,
                "modules": modules,
                "metadata": {"filename": filepath.name}
            })

    # Batch validate (max 10 per request)
    results = []
    for i in range(0, len(documents), 10):
        batch = documents[i:i+10]

        print(f"Processing batch {i//10 + 1} ({len(batch)} documents)...")

        response = requests.post(
            f"{api_url}/validate/batch",
            json=batch
        )

        if response.status_code == 200:
            results.extend(response.json())
        else:
            print(f"Batch error: {response.json()}")

    # Summary
    print(f"\nProcessed {len(results)} documents")

    high_risk = sum(1 for r in results if r['risk'] in ['HIGH', 'CRITICAL'])
    print(f"High Risk: {high_risk}")

    return results

# Usage
results = batch_validate_files(
    "./documents",
    "financial_promotion",
    ["fca_uk", "gdpr_uk"]
)
```

### Error Handling

```python
import requests
from requests.exceptions import RequestException, Timeout

def safe_validate(text, document_type, modules, max_retries=3):
    """Validate with error handling and retries"""

    api_url = "http://localhost:8000/api/v1"

    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{api_url}/validate",
                json={
                    "text": text,
                    "document_type": document_type,
                    "modules": modules
                },
                timeout=30
            )

            # Handle HTTP errors
            response.raise_for_status()
            return response.json()

        except Timeout:
            print(f"Timeout on attempt {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                continue
            else:
                raise

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limit
                print("Rate limited. Waiting...")
                import time
                time.sleep(60)
            elif e.response.status_code >= 500:  # Server error
                print(f"Server error: {e.response.status_code}")
                if attempt < max_retries - 1:
                    continue
                else:
                    raise
            else:  # Client error (400, 403, etc.)
                print(f"Client error: {e.response.json()}")
                raise

        except RequestException as e:
            print(f"Request error: {e}")
            if attempt < max_retries - 1:
                continue
            else:
                raise

    raise Exception("Max retries exceeded")

# Usage
try:
    result = safe_validate(
        "Your document...",
        "contract",
        ["fca_uk", "gdpr_uk"]
    )
    print(f"Validation successful: {result['risk']}")
except Exception as e:
    print(f"Failed to validate: {e}")
```

---

## JavaScript Examples

### Fetch API

```javascript
// Configuration
const API_URL = 'http://localhost:8000/api/v1';

async function validateDocument(text, documentType, modules) {
  try {
    const response = await fetch(`${API_URL}/validate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: text,
        document_type: documentType,
        modules: modules,
        use_cache: false,
        include_suggestions: true
      })
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    const result = await response.json();

    console.log(`Overall Risk: ${result.risk}`);

    result.validation.modules.forEach(module => {
      console.log(`\n${module.module_name}:`);
      console.log(`  Gates Checked: ${module.gates_checked}`);
      console.log(`  Gates Failed: ${module.gates_failed}`);

      module.gates.forEach(gate => {
        if (!gate.passed) {
          console.log(`  ❌ ${gate.gate_name}: ${gate.message}`);
        }
      });
    });

    return result;
  } catch (error) {
    console.error('Validation error:', error);
    throw error;
  }
}

// Usage
validateDocument(
  'Investment returns guaranteed at 15% annually',
  'financial_promotion',
  ['fca_uk']
);
```

### Axios

```javascript
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Validate and Correct
async function validateAndCorrect(text, documentType, modules) {
  try {
    // Validate
    const validationRes = await apiClient.post('/validate', {
      text: text,
      document_type: documentType,
      modules: modules,
      use_cache: false
    });

    console.log(`Validation Risk: ${validationRes.data.risk}`);

    // Correct
    const correctionRes = await apiClient.post('/correct', {
      text: text,
      validation_results: validationRes.data.validation,
      auto_apply: true,
      confidence_threshold: 0.8
    });

    return {
      original: text,
      corrected: correctionRes.data.corrected_text,
      corrections: correctionRes.data.corrections
    };
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
    throw error;
  }
}

// Batch Validation
async function batchValidate(documents) {
  try {
    const response = await apiClient.post('/validate/batch', documents);
    return response.data;
  } catch (error) {
    console.error('Batch validation error:', error.response?.data);
    throw error;
  }
}

// Usage
const result = await validateAndCorrect(
  'Your document...',
  'privacy_policy',
  ['gdpr_uk']
);

console.log('Original:', result.original);
console.log('Corrected:', result.corrected);
console.log('Corrections:', result.corrections);
```

### WebSocket Real-time Validation

```javascript
function setupWebSocketValidation() {
  const ws = new WebSocket('ws://localhost:8000/api/v1/ws/validate');

  ws.onopen = () => {
    console.log('Connected to WebSocket');

    // Send validation request
    ws.send(JSON.stringify({
      text: 'Your document...',
      document_type: 'financial_promotion',
      modules: ['fca_uk', 'gdpr_uk']
    }));
  };

  ws.onmessage = (event) => {
    const message = JSON.parse(event.data);

    if (message.type === 'module_result') {
      console.log(`${message.module}: ${message.progress * 100}% complete`);
      console.log(`Gates Failed: ${message.result.gates_failed}`);
    } else if (message.type === 'complete') {
      console.log('Validation complete');
      console.log(`Overall Risk: ${message.overall_risk}`);
      ws.close();
    }
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };

  ws.onclose = () => {
    console.log('WebSocket closed');
  };
}

setupWebSocketValidation();
```

### React Hook

```javascript
import { useState, useCallback } from 'react';

export function useApiValidation() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const validate = useCallback(async (text, documentType, modules) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text,
          document_type: documentType,
          modules,
          use_cache: false
        })
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { validate, loading, error, result };
}

// Usage in component
function ValidationForm() {
  const { validate, loading, error, result } = useApiValidation();
  const [text, setText] = useState('');

  const handleValidate = async () => {
    try {
      await validate(text, 'financial_promotion', ['fca_uk']);
    } catch (err) {
      console.error('Validation failed:', err);
    }
  };

  return (
    <div>
      <textarea value={text} onChange={(e) => setText(e.target.value)} />
      <button onClick={handleValidate} disabled={loading}>
        {loading ? 'Validating...' : 'Validate'}
      </button>

      {error && <div className="error">{error}</div>}
      {result && <div className="result">Risk: {result.risk}</div>}
    </div>
  );
}
```

---

## cURL Examples

### Basic Validation

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

### Pretty Print Response

```bash
curl -X POST http://localhost:8000/api/v1/validate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your document...",
    "document_type": "contract",
    "modules": ["fca_uk", "gdpr_uk"]
  }' | jq '.'
```

### Save Response to File

```bash
curl -X POST http://localhost:8000/api/v1/validate \
  -H "Content-Type: application/json" \
  -d @payload.json \
  -o response.json
```

### With Authentication (Future)

```bash
curl -X POST http://localhost:8000/api/v1/validate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{...}'
```

### Check Rate Limit Headers

```bash
curl -i -X POST http://localhost:8000/api/v1/validate \
  -H "Content-Type: application/json" \
  -d '{...}'
```

---

## Postman Collections

### Import Collection

1. Open Postman
2. Click "Import"
3. Paste the following JSON or download from GitHub

### Sample Collection

```json
{
  "info": {
    "name": "LOKI Interceptor API",
    "description": "Collection for LOKI Interceptor API endpoints",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/health"
      }
    },
    {
      "name": "Validate Document",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/v1/validate",
        "body": {
          "mode": "raw",
          "raw": "{\"text\": \"Your document...\", \"document_type\": \"financial_promotion\", \"modules\": [\"fca_uk\"]}"
        }
      }
    },
    {
      "name": "Correct Document",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/v1/correct",
        "body": {
          "mode": "raw",
          "raw": "{\"text\": \"Your document...\", \"validation_results\": {}, \"auto_apply\": true}"
        }
      }
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000/api",
      "type": "string"
    }
  ]
}
```

### Environment Variables

Set up Postman environments with:

```json
{
  "base_url": "http://localhost:8000/api",
  "api_key": "your_api_key",
  "document_type": "financial_promotion",
  "modules": ["fca_uk", "gdpr_uk"]
}
```

---

## Performance Tips

1. **Use caching** for repeated validations
2. **Batch operations** for multiple documents
3. **Set appropriate timeouts** (default 30s)
4. **Handle rate limits** gracefully
5. **Use async operations** for concurrent processing

---

**See also**: [API Reference](README.md) | [Full Documentation](../INDEX.md)
