# Multi-Model Aggregation (Experimental)

The `feature/multi-model-aggregation` branch introduces the first pass of a deterministic blending layer that can run the same prompt across multiple providers, validate each response with LOKI, and surface the safest option.

## How it works

1. **Frontend / Client** posts to `POST /api/aggregate` with:
   ```json
   {
     "prompt": "Explain the product to a retail customer.",
     "providers": [
       {"name": "anthropic", "api_key": "..."},
       {"name": "openai", "simulated_response": "Sample text without risk claims"}
     ],
     "modules": ["fca_uk", "gdpr_uk"],
     "max_tokens": 768
   }
   ```
2. For each provider:
   - If `simulated_response` is present, it is used (no API credits required).
   - Otherwise the provider router configures the SDK (if an API key is supplied) and calls the live model.
   - The response text is run through `AsyncLOKIEngine.check_document`, producing the standard gate output plus semantic hit totals.
3. The aggregator computes metrics (`overall_risk`, fail/warn counts, semantic hits, review flags) and picks the “least risky” answer. Tie-breakers favour fewer critical failures, then fewer total fails, warnings, and semantic hits.
4. The endpoint returns all responses, their metrics, and highlights the selected response for downstream use.

## Testing without credits

Run the manual smoke test:
```bash
python tests/manual/aggregate_demo.py
```
It simulates two providers (one non-compliant, one compliant) so you can verify selection logic locally.

## Limitations & next steps

- Live aggregation still depends on configuring provider API keys per request. Eventually we should support stored credentials / secrets.
- Auto-correction is not invoked yet; the selected response is returned verbatim with validation metadata.
- Tie-breaking is conservative but deterministic. We may revisit the scoring once more metrics (e.g., semantic coverage depth, human-review density) are captured.
- No frontend wiring yet; the existing UI can hit the new endpoint manually via `curl` or through a future dashboard control.

Use this branch to iterate safely before re-pointing any live deployments. When API credits are available, replace simulated responses with real provider calls to verify the behavior end-to-end.
