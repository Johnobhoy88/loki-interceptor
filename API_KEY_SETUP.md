# LOKI Interceptor - API Key Setup Guide

**Last Updated**: October 2025

This guide shows you how to get **free API credits** for OpenAI and Gemini, and configure LOKI to use the cheapest available models.

---

## Quick Setup (5 Minutes)

### 1. Get OpenAI API Key (Free $5 Credits)

1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up with your email and verify your phone number
3. **Automatic**: $5 in free API credits added (valid 3 months, one-time per phone)
4. Navigate to [API Keys](https://platform.openai.com/api-keys)
5. Click "Create new secret key" → Copy the key (starts with `sk-proj-...`)
6. **No credit card required** - calls use free credits first automatically

**Note**: If you opt-in to share data for model improvement, you may get up to 11 million free tokens/day until April 2025.

### 2. Get Gemini API Key (Free Tier - 60 req/min)

1. Go to [Google AI Studio](https://ai.google.dev/gemini-api/)
2. Sign in with your Google account
3. Click "Get API Key" → Create a new key for your project
4. Copy the key (starts with `AIza...`)
5. **No payment info needed** - 60 requests/min and 120K-128K tokens/min on free tier

### 3. Configure LOKI

Create or update `configs/dev_api_keys.example`:

```bash
# LOKI Interceptor API Keys
ANTHROPIC=your_anthropic_key_here
OPENAI=sk-proj-YOUR_OPENAI_KEY_HERE
GEMINI=AIzaSy_YOUR_GEMINI_KEY_HERE
```

Then export to environment:

```bash
export ANTHROPIC_API_KEY="your_anthropic_key_here"
export OPENAI_API_KEY="sk-proj-YOUR_OPENAI_KEY_HERE"
export GEMINI_API_KEY="AIzaSy_YOUR_GEMINI_KEY_HERE"
```

Or add to your shell profile:

```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'export ANTHROPIC_API_KEY="your_key"' >> ~/.bashrc
echo 'export OPENAI_API_KEY="your_key"' >> ~/.bashrc
echo 'export GEMINI_API_KEY="your_key"' >> ~/.bashrc
source ~/.bashrc
```

---

## Cheapest Available Models (October 2025)

LOKI is configured to use the most cost-effective models by default:

### OpenAI Models

| Model | Use Case | Cost (per 1M tokens) | API Call |
|-------|----------|---------------------|----------|
| **gpt-5-nano** | Fastest, best for classification/summaries | $0.05 input, $0.40 output | `gpt-5-nano` |
| **gpt-5-mini** | More capable, still very cheap | $0.25 input, $2.00 output | `gpt-5-mini` |
| gpt-3.5-turbo | Legacy fallback | Variable | `gpt-3.5-turbo` |

**Default**: LOKI uses `gpt-5-mini` for compliance validation (balances cost and accuracy).

### Gemini Models

| Model | Use Case | Free Tier | API Call |
|-------|----------|-----------|----------|
| **gemini-1.5-flash** | Fast, recommended for most uses | 60 req/min, 128K tokens/min | `gemini-1.5-flash` |
| gemini-1.5-pro | More capable but slower | 60 req/min, 120K tokens/min | `gemini-1.5-pro` |
| gemini-1.0-pro | Legacy but stable | Same limits | `gemini-1.0-pro` |

**Default**: LOKI uses `gemini-1.5-flash` for optimal performance on free tier.

### Anthropic Models

| Model | Use Case | Cost (per 1M tokens) | API Call |
|-------|----------|---------------------|----------|
| claude-sonnet-4-20250514 | Best accuracy for compliance | $3 input, $15 output | `claude-sonnet-4-20250514` |
| claude-haiku-4-20250430 | Faster, cheaper | $1 input, $5 output | `claude-haiku-4-20250430` |

**Default**: LOKI uses `claude-sonnet-4-20250514` as primary validation engine (highest compliance detection accuracy).

---

## Update LOKI Model Defaults

### Backend Configuration

Edit `backend/core/aggregator.py` to use cheaper models:

**Current (Lines 82-110):**
```python
# OpenAI default
request_payload = {
    'model': spec.get('model') or 'gpt-4o-mini',  # OLD MODEL
    'messages': [{'role': 'user', 'content': prompt}]
}

# Gemini default
request_payload = {
    'model': spec.get('model') or 'gemini-1.5-flash',  # CORRECT
    'prompt': prompt
}
```

**Update OpenAI to use gpt-5-mini:**
```python
# Line 96
'model': spec.get('model') or 'gpt-5-mini',  # NEW: Cheapest capable model
```

### Frontend Configuration

Edit `frontend/app.js` to use updated models:

**Lines 320, 340, 347:**
```javascript
// OLD
model: 'gpt-4o-mini',
model: 'gemini-1.5-flash',

// NEW (already correct for Gemini, update OpenAI)
model: 'gpt-5-mini',         // Line 320, 340
model: 'gemini-1.5-flash',   // Line 347 (already correct)
```

---

## Testing Your Setup

### 1. Quick Health Check

```bash
curl http://127.0.0.1:5002/api/health
```

Expected:
```json
{
  "status": "healthy",
  "modules": ["hr_scottish", "gdpr_uk", "nda_uk", "tax_uk", "fca_uk"],
  "modules_loaded": 5
}
```

### 2. Test Provider Keys

**Anthropic:**
```bash
curl -X POST http://127.0.0.1:5002/api/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -d '{
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 100,
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

**OpenAI:**
```bash
curl -X POST http://127.0.0.1:5002/api/proxy \
  -H "Content-Type: application/json" \
  -H "x-api-key: $OPENAI_API_KEY" \
  -d '{
    "provider": "openai",
    "model": "gpt-5-mini",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

**Gemini:**
```bash
curl -X POST http://127.0.0.1:5002/api/proxy \
  -H "Content-Type: application/json" \
  -H "gemini-api-key: $GEMINI_API_KEY" \
  -d '{
    "provider": "gemini",
    "model": "gemini-1.5-flash",
    "prompt": "Hello"
  }'
```

### 3. Test Multi-Provider Aggregation

```bash
curl -X POST http://127.0.0.1:5002/api/aggregate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a privacy notice for data collection",
    "modules": ["gdpr_uk", "fca_uk"],
    "providers": [
      {"name": "anthropic", "api_key": "'"$ANTHROPIC_API_KEY"'"},
      {"name": "openai", "api_key": "'"$OPENAI_API_KEY"'"},
      {"name": "gemini", "api_key": "'"$GEMINI_API_KEY"'"}
    ]
  }'
```

---

## Troubleshooting

### "Quota Exceeded" Error (OpenAI)

**Cause**: You've used your $5 free credits or they expired (3 months)

**Solutions**:
1. Check usage: [platform.openai.com/usage](https://platform.openai.com/usage)
2. Add payment method for paid usage (optional)
3. Create new account with different phone number (not recommended)
4. Wait for renewal (if you opted into data sharing for free tier)

### "Model Not Found" Error (Gemini)

**Cause**: Using wrong API version or model name

**Solutions**:
1. Use `gemini-1.5-flash` instead of `gemini-flash-1.5`
2. Check available models: [ai.google.dev/gemini-api/docs/models/gemini](https://ai.google.dev/gemini-api/docs/models/gemini)
3. Ensure API key is from Google AI Studio, not Vertex AI (different auth)

### "Invalid API Key" Error

**Cause**: Key not set in environment or malformed

**Solutions**:
```bash
# Check if keys are set
echo $ANTHROPIC_API_KEY
echo $OPENAI_API_KEY
echo $GEMINI_API_KEY

# Re-export if missing
export ANTHROPIC_API_KEY="your_key"
export OPENAI_API_KEY="your_key"
export GEMINI_API_KEY="your_key"

# Restart backend after setting keys
python3 backend/server.py
```

### Rate Limit Errors

**OpenAI Free Tier**: 3 requests/min, 200 requests/day
**Gemini Free Tier**: 60 requests/min, 128K tokens/min

**Solutions**:
- Add delays between requests (LOKI has built-in rate limiting)
- Upgrade to paid tier for higher limits
- Distribute load across multiple providers

---

## Cost Estimates (Paid Usage)

### Example: 1,000 validation requests per month

**Scenario**: Each request generates ~500 tokens input, ~1000 tokens output

| Provider | Model | Monthly Cost |
|----------|-------|--------------|
| OpenAI | gpt-5-nano | $0.43 |
| OpenAI | gpt-5-mini | $2.13 |
| Gemini | gemini-1.5-flash | FREE (under quota) |
| Anthropic | claude-sonnet-4 | $19.50 |

**Recommendation**: Use Gemini for high-volume, OpenAI for medium accuracy, Anthropic for critical compliance checks.

---

## Security Best Practices

### ❌ DO NOT

- Commit API keys to Git
- Share keys in public forums
- Use production keys in demos
- Store keys in frontend JavaScript

### ✅ DO

- Use environment variables
- Rotate keys regularly
- Set usage limits in provider dashboards
- Use separate keys for dev/staging/prod
- Enable key restrictions (IP whitelist, HTTP referer)

### LOKI Security Features

- API keys never logged to disk
- Keys passed via headers, not URL params
- Rate limiting (10 req/min per client)
- Request size limits (10MB max)
- Key format validation before use

---

## Resources

- **OpenAI Pricing**: [openai.com/api/pricing/](https://openai.com/api/pricing/)
- **Gemini Pricing**: [ai.google.dev/gemini-api/docs/pricing](https://ai.google.dev/gemini-api/docs/pricing)
- **Anthropic Pricing**: [anthropic.com/pricing](https://anthropic.com/pricing)
- **OpenAI Platform**: [platform.openai.com](https://platform.openai.com)
- **Google AI Studio**: [ai.google.dev/gemini-api/](https://ai.google.dev/gemini-api/)

---

## Next Steps

1. ✓ Get API keys for all 3 providers
2. ✓ Update `backend/core/aggregator.py` with cheaper models
3. ✓ Export keys to environment
4. ✓ Test with `scripts/qa_deep_pass.py`
5. ✓ Monitor usage dashboards

For questions, see `QA_REPORT.md` or raise an issue.
