# IBM Granite Integration Module

Enterprise-grade integration of IBM Granite models with Loki Interceptor.

## Components

### 1. **DocumentConverter** - Granite-Docling 258M
Convert PDFs, images, and scans to structured text while preserving layout, tables, and figures.

### 2. **GuardianValidator** - Granite Guardian 3.0
Detect compliance risks, safety issues, and RAG hallucinations.

### 3. **GraniteInterceptor** - Model Validation
Intercept Granite model responses and validate against LOKI rules.

---

## Quick Start

### Installation

```bash
# Install Granite dependencies
pip install -r requirements-granite.txt

# For full functionality:
pip install docling transformers torch
```

### Basic Usage

#### 1. Convert PDF Documents

```python
from backend.granite import DocumentConverter

# Initialize converter
converter = DocumentConverter()

# Convert PDF to structured text
result = converter.convert_document("financial_promotion.pdf")

print(f"Extracted text: {result.text}")
print(f"Found {len(result.tables)} tables")
print(f"Found {len(result.figures)} figures")

# Format for validation
validation_input = converter.convert_to_validation_format(
    file_path="document.pdf",
    document_type="financial"
)
```

#### 2. Safety Validation with Guardian

```python
from backend.granite import GuardianValidator

# Initialize validator
guardian = GuardianValidator(model_size="2b")

# Validate text for safety risks
result = guardian.validate(
    text="Investment opportunity with guaranteed 15% returns",
    dimensions=["harm", "social_bias", "jailbreaking"]
)

print(f"Risk Level: {result.overall_risk.value}")
print(f"Passed: {result.passed}")
print(f"Recommendation: {result.recommendation}")

# RAG-specific validation
rag_result = guardian.validate_rag_response(
    question="What is FCA COBS 4.2.1?",
    answer="It requires fair, clear, not misleading communications",
    context="FCA Handbook: COBS 4.2.1 states..."
)
```

#### 3. Intercept Granite Model Calls

```python
from backend.granite import GraniteInterceptor
from backend.core.engine import ComplianceEngine

# Initialize
engine = ComplianceEngine()
guardian = GuardianValidator()
interceptor = GraniteInterceptor(engine, guardian)

# Intercept local Granite model
result = interceptor.intercept(
    request_data={
        'model': 'granite-3.2-8b-instruct',
        'messages': [{'role': 'user', 'content': 'Write financial advice'}],
        'max_tokens': 1024
    },
    endpoint='http://localhost:8000',  # Local vLLM/TGI server
    active_modules=['fca_uk', 'gdpr_uk']
)

if result['blocked']:
    print(f"BLOCKED: {result['message']}")
else:
    print(f"Risk: {result['loki']['risk']}")
    print(f"Response: {result['response']}")
```

---

## Integration Scenarios

### Scenario 1: Add PDF Support to Existing System

```python
from backend.granite import DocumentConverter
from backend.core.document_validator import DocumentValidator

# Convert PDF
converter = DocumentConverter()
doc_data = converter.convert_to_validation_format(
    file_path="vat_invoice.pdf",
    document_type="invoice"
)

# Validate with existing LOKI system
validator = DocumentValidator()
validation = validator.validate_document(
    text=doc_data['text'],
    document_type='invoice',
    modules=['tax_uk']
)
```

### Scenario 2: Add Guardian Safety Layer

```python
from backend.granite import GuardianValidator
from backend.core.document_corrector import DocumentCorrector

# Apply corrections
corrector = DocumentCorrector(advanced_mode=True)
result = corrector.correct_document(text, validation_results, doc_type)

# Validate corrections with Guardian
guardian = GuardianValidator()
safety_check = guardian.validate_correction(
    original=text,
    corrected=result['corrected'],
    correction_type='pattern_based'
)

if not safety_check.passed:
    print(f"WARNING: {safety_check.recommendation}")
```

### Scenario 3: Replace Claude with Granite

```python
from backend.granite import GraniteInterceptor

# Before (Claude):
# from backend.core.interceptor import AnthropicInterceptor
# interceptor = AnthropicInterceptor(engine)
# result = interceptor.intercept(request, api_key='sk-ant-...')

# After (Granite):
from backend.granite import GraniteInterceptor
interceptor = GraniteInterceptor(engine, guardian)
result = interceptor.intercept(
    request_data=request,
    endpoint='http://localhost:8000',  # Self-hosted
    active_modules=['fca_uk']
)

# Same interface, different model!
```

---

## Deployment Options

### Option 1: Local Self-Hosted (Lowest Cost)

```bash
# Install vLLM
pip install vllm

# Start Granite 4.0 8B
python -m vllm.entrypoints.openai.api_server \
    --model ibm-granite/granite-4.0-8b-instruct \
    --port 8000 \
    --dtype auto
```

```python
# Connect to local endpoint
result = interceptor.intercept(
    request_data={'messages': [...]},
    endpoint='http://localhost:8000',
    active_modules=['fca_uk']
)
```

### Option 2: NVIDIA NIM (Managed)

```python
result = interceptor.intercept(
    request_data={'messages': [...]},
    endpoint='https://integrate.api.nvidia.com/v1',
    api_key='your-nvidia-api-key',
    active_modules=['fca_uk']
)
```

### Option 3: IBM watsonx.ai

```python
result = interceptor.intercept(
    request_data={'messages': [...]},
    endpoint='https://api.watsonx.ai/v1',
    api_key='your-watsonx-api-key',
    active_modules=['fca_uk']
)
```

---

## Advanced Usage

### Batch PDF Processing

```python
from pathlib import Path
from backend.granite import DocumentConverter
from backend.core.document_validator import DocumentValidator

converter = DocumentConverter()
validator = DocumentValidator()

# Process all PDFs in directory
pdf_files = list(Path("documents/").glob("*.pdf"))
results = []

for pdf_file in pdf_files:
    # Convert
    doc_data = converter.convert_to_validation_format(
        pdf_file,
        document_type="financial"
    )

    # Validate
    validation = validator.validate_document(
        text=doc_data['text'],
        document_type='financial',
        modules=['fca_uk', 'gdpr_uk']
    )

    results.append({
        'file': pdf_file.name,
        'status': validation['validation']['status'],
        'risk': validation['validation'].get('overall_risk')
    })

# Summary report
for result in results:
    print(f"{result['file']}: {result['status']} ({result['risk']})")
```

### Custom Risk Dimensions

```python
from backend.granite import GuardianValidator

guardian = GuardianValidator()

# Define custom risk criteria
custom_dimensions = [
    'harm',
    'social_bias',
    'financial_advice_without_license',  # Custom dimension
    'medical_advice_unauthorized'         # Custom dimension
]

result = guardian.validate(
    text="Consider investing in cryptocurrency",
    dimensions=custom_dimensions
)
```

### Cost Tracking

```python
from backend.granite import GraniteInterceptor

interceptor = GraniteInterceptor(engine)

# Get cost estimate
cost = interceptor.get_cost_estimate(
    tokens_input=2000,
    tokens_output=500,
    deployment_type='self_hosted'  # vs 'nvidia_nim', 'watsonx'
)

print(f"Cost per request: ${cost['total_cost']:.4f}")
print(f"Monthly at 10K requests: ${cost['total_cost'] * 10000:.2f}")
```

---

## Performance Benchmarks

### DocumentConverter (Granite-Docling 258M)

| Document Type | Pages | Time | Tables | Figures |
|--------------|-------|------|--------|---------|
| PDF Invoice | 1 | 2.3s | 3 | 0 |
| Financial Report | 10 | 18.5s | 12 | 8 |
| Scanned Contract | 5 | 12.1s | 0 | 0 |

**CPU:** Intel i7, 16GB RAM
**GPU:** N/A (CPU inference)

### GuardianValidator (Granite Guardian 2B)

| Text Length | Dimensions | Time (CPU) | Time (GPU) |
|-------------|-----------|------------|-----------|
| 100 tokens | 4 | 0.8s | 0.2s |
| 500 tokens | 4 | 1.5s | 0.4s |
| 2000 tokens | 4 | 3.2s | 0.8s |

**CPU:** Intel i7, 16GB RAM
**GPU:** NVIDIA RTX 3090

### GraniteInterceptor (Granite 4.0 8B)

| Request Type | Time (CPU) | Time (GPU) | Tokens/sec |
|-------------|-----------|-----------|-----------|
| Short (100 tokens) | N/A | 1.2s | 83 |
| Medium (500 tokens) | N/A | 3.5s | 143 |
| Long (2000 tokens) | N/A | 12.8s | 156 |

**GPU:** NVIDIA A100 40GB

---

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│                 Loki Interceptor + Granite                 │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Document Input                                            │
│       ↓                                                    │
│  ┌──────────────────────────────────────┐                │
│  │  DocumentConverter (Docling 258M)    │                │
│  │  • PDF → Structured Text             │                │
│  │  • Table Extraction                  │                │
│  │  • Layout Preservation               │                │
│  └──────────────────────────────────────┘                │
│       ↓                                                    │
│  ┌──────────────────────────────────────┐                │
│  │  LOKI Pattern Validation             │                │
│  │  • 141 Detection Rules               │                │
│  │  • 5 Compliance Modules              │                │
│  └──────────────────────────────────────┘                │
│       ↓                                                    │
│  ┌──────────────────────────────────────┐                │
│  │  GuardianValidator (Guardian 2B)     │                │
│  │  • Safety Risk Detection             │                │
│  │  • RAG Groundedness                  │                │
│  │  • Bias Detection                    │                │
│  └──────────────────────────────────────┘                │
│       ↓                                                    │
│  Enhanced Validated Output                                 │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## Comparison: Claude vs Granite

| Feature | Claude (Existing) | Granite (New) |
|---------|------------------|---------------|
| **Document Support** | Text only | ✅ PDF, images, scans |
| **Safety Validation** | Pattern-based | ✅ Guardian AI model |
| **Deployment** | API only | ✅ Self-hosted or cloud |
| **Cost (10K docs)** | $169/mo | $20-50/mo |
| **Data Privacy** | Third-party | ✅ On-premises option |
| **ISO 42001** | ❌ No | ✅ Yes |
| **RAG Checks** | ❌ No | ✅ Groundedness, relevance |

---

## Troubleshooting

### Docling Not Working

```python
# Check if installed
from backend.granite import DocumentConverter
converter = DocumentConverter()

# If error: "Docling not installed"
# Install: pip install docling
```

### Guardian Model Download Issues

```python
# Check transformers installation
import transformers
print(transformers.__version__)  # Should be >= 4.35.0

# Download model manually
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("ibm-granite/granite-guardian-3.0-2b")
```

### GPU Memory Issues

```python
# Use smaller model
guardian = GuardianValidator(model_size="2b")  # Not "8b"

# Or force CPU
guardian = GuardianValidator(device="cpu")
```

---

## Next Steps

1. **Start with DocumentConverter** - Add PDF support (low risk)
2. **Add GuardianValidator** - Enhance safety checks (optional)
3. **Test GraniteInterceptor** - A/B test vs Claude (pilot phase)
4. **Benchmark Performance** - Measure accuracy vs cost
5. **Gradual Migration** - Shift traffic based on results

---

## Support & Resources

- **IBM Granite Docs:** https://www.ibm.com/granite/docs
- **Granite GitHub:** https://github.com/ibm-granite
- **Guardian Models:** https://huggingface.co/ibm-granite/granite-guardian-3.0-8b
- **Docling Docs:** https://github.com/DS4SD/docling

---

**Version:** 1.0.0
**Last Updated:** January 2025
**Author:** Highland AI
