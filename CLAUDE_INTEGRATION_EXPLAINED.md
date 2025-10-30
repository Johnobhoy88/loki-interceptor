# Claude Integration in Loki Interceptor - Technical Explanation

## Summary

**Your question:** "Explain the Claude integration in the build, is that in the api interceptor?"

**Answer:** Yes! Claude is integrated through the **`AnthropicInterceptor` class** in `backend/core/interceptor.py`. It acts as a **middleware/proxy** that sits between your application and Claude's API, automatically validating all Claude responses against your compliance modules.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                     Loki Interceptor System                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User Request                                                    │
│       ↓                                                          │
│  ┌────────────────────────────────────────────────────┐         │
│  │         Backend Server (server.py)                 │         │
│  │  - Handles HTTP requests                           │         │
│  │  - Routes to appropriate interceptor               │         │
│  └────────────────────────────────────────────────────┘         │
│       ↓                                                          │
│  ┌────────────────────────────────────────────────────┐         │
│  │    AnthropicInterceptor (interceptor.py)           │◄─────   │
│  │                                                     │     │   │
│  │  1. Accepts request_data + API key                 │     │   │
│  │  2. Forwards to Claude API                         │     │   │
│  │  3. Gets response                                  │     │   │
│  │  4. Validates response with LOKI engine           │─────┘   │
│  │  5. Blocks if CRITICAL risk                        │         │
│  │  6. Returns enhanced response                      │         │
│  └────────────────────────────────────────────────────┘         │
│       ↓                                                          │
│  ┌────────────────────────────────────────────────────┐         │
│  │         LOKI Compliance Engine                     │         │
│  │  - Runs validation gates                           │         │
│  │  - Checks FCA, GDPR, Tax, NDA, HR rules           │         │
│  │  - Returns risk level + violations                 │         │
│  └────────────────────────────────────────────────────┘         │
│       ↓                                                          │
│  Enhanced Response with LOKI metadata                            │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## How Claude is Currently Integrated

### 1. **AnthropicInterceptor Class** (`backend/core/interceptor.py`)

This is the **main Claude integration point**. It has two key methods:

#### **Method 1: `intercept()`** - Basic interception with blocking

```python
def intercept(self, request_data, api_key, active_modules=None):
    """
    Forward request to Anthropic, validate response, return with LOKI metadata
    """
    # 1. Make HTTP request to Claude API
    url = 'https://api.anthropic.com/v1/messages'
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key,
        'anthropic-version': '2023-06-01',
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    response = resp.json()

    # 2. Extract text from Claude's response
    response_text = ''
    for block in response.get('content'):
        if block.get('type') == 'text':
            response_text += block.get('text')

    # 3. Validate with LOKI engine
    validation = self.engine.check_document(
        text=response_text,
        document_type='ai_generated',
        active_modules=modules_to_check
    )

    # 4. Block if CRITICAL risk
    if validation.get('overall_risk') == 'CRITICAL':
        return {
            'blocked': True,
            'error': 'LOKI_CRITICAL_ERROR',
            'message': 'AI response contains critical compliance errors',
            'validation': validation
        }

    # 5. Return enhanced response with LOKI metadata
    return {
        'blocked': False,
        'response': response,
        'loki': {
            'risk': validation.get('overall_risk'),
            'validation': validation,
            'timestamp': datetime.utcnow().isoformat()
        }
    }
```

**Key Features:**
- ✅ Direct HTTP calls to Claude API (no SDK dependency)
- ✅ Automatic validation of ALL Claude responses
- ✅ Blocks responses with CRITICAL compliance violations
- ✅ Adds LOKI metadata to every response
- ✅ Works with any Claude model (Sonnet, Opus, Haiku)

---

#### **Method 2: `intercept_and_validate()`** - Flag instead of block

```python
def intercept_and_validate(self, request_data, api_key, modules=None):
    """
    Intercept API call, validate response, flag instead of blocking
    """
    # Same process as above, but ALWAYS returns response
    # Sets 'flagged' metadata instead of blocking

    return {
        'blocked': False,
        'response': response,
        'validation': validation,
        'loki': {
            'risk': overall_risk,
            'flagged': overall_risk != 'LOW',
            'action': 'FLAGGED' if overall_risk != 'LOW' else 'ALLOWED',
            'gates_checked': list(validation.get('modules').keys())
        }
    }
```

**Difference:** Never blocks, always flags violations for review.

---

### 2. **ProviderRouter Class** (`backend/core/providers.py`)

This provides **direct Claude SDK integration** (alternative to interceptor):

```python
class ProviderRouter:
    def configure_provider(self, provider_name: str, api_key: str):
        if provider_name == 'anthropic':
            import anthropic
            self.providers['anthropic'] = anthropic.Anthropic(api_key=api_key)

    def call_provider(self, provider_name: str, prompt: str, max_tokens: int = 1024):
        if provider_name == 'anthropic':
            client = self.providers['anthropic']
            resp = client.messages.create(
                model='claude-sonnet-4-20250514',
                max_tokens=max_tokens,
                messages=[{'role': 'user', 'content': prompt}],
            )
            return resp.content[0].text
```

**Key Features:**
- ✅ Uses official Anthropic SDK
- ✅ Supports multiple AI providers (Claude, GPT, Gemini)
- ✅ Simpler for direct model calls
- ⚠️ **Does NOT include automatic validation** (you must validate separately)

---

### 3. **MultiModelAggregator** (`backend/core/aggregator.py`)

This enables **multi-model comparison** with Claude:

```python
class MultiModelAggregator:
    """Runs a prompt across multiple providers and returns comparison metadata."""

    def run(self, prompt: str, provider_specs: List[Dict[str, Any]], modules: Optional[List[str]] = None):
        # Calls Claude, GPT, and Gemini in parallel
        # Validates ALL responses with LOKI
        # Selects "best" response based on:
        #   - Lowest risk level
        #   - Fewest compliance failures
        #   - Content quality score

        outcomes: List[ProviderOutcome] = []

        for spec in provider_specs:
            # For Claude:
            if spec['name'] == 'anthropic':
                request_payload = {
                    'model': 'claude-sonnet-4-20250514',
                    'max_tokens': 900,
                    'messages': [{'role': 'user', 'content': prompt}]
                }
                raw = self.anthropic.intercept_and_validate(request_payload, api_key, modules)
                validation = raw.get('validation')
                risk = raw.get('loki', {}).get('risk')

                outcomes.append(ProviderOutcome(
                    provider='anthropic',
                    risk=risk,
                    failures=count_failures(validation),
                    validation=validation,
                    response_text=extract_text(raw)
                ))

        # Select best response
        selected = self._select_best(outcomes)

        return {
            'selected': selected,
            'providers': outcomes,
            'selection': selection_metadata
        }
```

**Key Features:**
- ✅ Run same prompt through Claude + GPT + Gemini
- ✅ Compare compliance across models
- ✅ Auto-select safest response
- ✅ Useful for high-risk content generation

---

## Where Claude is NOT Used

**Important:** The current Loki Interceptor **does NOT use Claude for document validation**.

The validation system is **pattern-based**, using:
- ✅ 141 regex detection rules
- ✅ Template insertions
- ✅ Structural corrections
- ✅ No AI/LLM required for validation

**Claude is only used for:**
1. ✅ Validating Claude's own responses (interceptor)
2. ✅ Multi-model comparison (aggregator)
3. ✅ Optional: Could be used for semantic analysis (not currently implemented)

---

## How This Differs from the Gold Standard Enhancement

### What We Just Built (No Claude Required)

The **gold standard enhancement** we completed earlier works **without Claude**:

```
Document → Pattern Registry (141 rules) → Validation → Corrections
```

- ✅ 79 pattern groups across 5 modules
- ✅ Pure regex + template-based
- ✅ Fast, deterministic, no API costs
- ✅ Works offline

### Where Claude COULD Be Added (Future Enhancement)

You could add Claude for **semantic analysis** before pattern matching:

```
Document → Claude Semantic Analysis → Pattern Validation → Corrections
         (understand context)       (apply rules)
```

**Benefits of adding Claude here:**
- Understand document context and intent
- Better categorization (is this a financial promotion or privacy policy?)
- Detect subtle compliance issues regex can't catch
- Natural language understanding

**This is what IBM Granite could replace/supplement!**

---

## IBM Granite vs Current Claude Integration

### Current State: Claude Used As

| Purpose | Current Implementation | File |
|---------|----------------------|------|
| **API Response Validation** | `AnthropicInterceptor` validates Claude's outputs | `interceptor.py` |
| **Multi-Model Comparison** | `MultiModelAggregator` compares Claude vs GPT vs Gemini | `aggregator.py` |
| **Direct LLM Calls** | `ProviderRouter` for simple Claude API calls | `providers.py` |

### Where Granite Could Fit

| Purpose | Granite Model | Benefit |
|---------|---------------|---------|
| **Document Preprocessing** | Granite-Docling 258M | Add PDF/image support |
| **Response Safety Validation** | Granite Guardian 3.0 2B | Enhanced compliance checks |
| **Replace Claude API Calls** | Granite 3.2 8B VLM | Cost reduction, data privacy |
| **Pre-Validation Risk Screening** | Granite Guardian 3.0 8B | Detect high-risk before processing |

---

## Example: Current Claude Integration in Action

### Scenario: User generates financial advice with Claude

```python
# 1. User makes request through Loki
request = {
    'model': 'claude-sonnet-4-20250514',
    'max_tokens': 1024,
    'messages': [{
        'role': 'user',
        'content': 'Write a financial promotion for our 15% guaranteed returns fund'
    }]
}

# 2. Goes through AnthropicInterceptor
interceptor = AnthropicInterceptor(engine)
result = interceptor.intercept(request, api_key='sk-ant-...', active_modules=['fca_uk'])

# 3. Claude generates response:
claude_response = "Invest in our fund with guaranteed 15% annual returns..."

# 4. LOKI validates against FCA UK rules
validation = {
    'overall_risk': 'CRITICAL',
    'modules': {
        'fca_uk': {
            'gates': {
                'fair_clear_not_misleading': {
                    'status': 'FAIL',
                    'severity': 'critical',
                    'reason': 'Guaranteed returns are misleading per FCA COBS 4.2.1'
                }
            }
        }
    }
}

# 5. Interceptor BLOCKS response
return {
    'blocked': True,
    'error': 'LOKI_CRITICAL_ERROR',
    'message': 'AI response contains critical compliance errors',
    'validation': validation,
    'original_response': claude_response
}
```

**Result:** User never receives the non-compliant content from Claude.

---

## Summary: Where is Claude?

**YES, Claude is in the API interceptor!** Specifically:

| Component | File | Purpose | Uses Claude? |
|-----------|------|---------|--------------|
| ✅ **AnthropicInterceptor** | `interceptor.py` | Proxy/middleware for Claude API calls | **YES** |
| ✅ **ProviderRouter** | `providers.py` | Direct Claude SDK integration | **YES** |
| ✅ **MultiModelAggregator** | `aggregator.py` | Multi-model comparison | **YES** |
| ❌ **Pattern Registry** | `correction_patterns.py` | 141 detection rules | **NO** |
| ❌ **Correction Synthesizer** | `correction_synthesizer.py` | Apply corrections | **NO** |
| ❌ **Document Validator** | (would be in engine.py) | Validate documents | **NO** |

---

## How Granite Would Change This

### Option 1: Keep Claude, Add Granite (Hybrid)

```
Current:
  Claude API → AnthropicInterceptor → LOKI Validation → Response

Enhanced:
  Document → Granite-Docling (PDF parsing)
          → Claude API → AnthropicInterceptor → LOKI Validation
          → Granite Guardian (final safety check) → Response
```

### Option 2: Replace Claude with Granite

```
Current:
  Claude API → AnthropicInterceptor → LOKI Validation → Response

Enhanced:
  Granite 4.0 API → GraniteInterceptor → LOKI Validation
                                       → Granite Guardian → Response
```

**Cost:**
- Claude: $3-15 per 1M tokens (API)
- Granite: $0.10 per 1M tokens (self-hosted compute)

**Privacy:**
- Claude: Data sent to Anthropic
- Granite: 100% on-premises

**Compliance:**
- Claude: No specific certifications
- Granite: ISO 42001 certified

---

## Next Steps

Now that you understand the current Claude integration, here's what we can do:

### **Conservative Path (Low Risk)**
1. Keep all existing Claude integration as-is
2. Add Granite-Docling for PDF preprocessing
3. Add Granite Guardian for output safety checks
4. No changes to core validation logic

### **Aggressive Path (Cost Optimization)**
1. Create `GraniteInterceptor` (mirror of `AnthropicInterceptor`)
2. Add Granite models to `ProviderRouter`
3. Update `MultiModelAggregator` to include Granite
4. A/B test Claude vs Granite for accuracy
5. Gradually shift traffic to Granite

### **Questions for You**
1. Do you want to **keep Claude** for AI response validation?
2. Do you want to **add Granite** as an additional provider?
3. Do you want to **replace Claude** with Granite entirely?
4. What's your priority: **accuracy** or **cost**?

Let me know what direction makes sense for your use case!

---

**Document Created:** January 2025
**Author:** Highland AI / Claude Code
