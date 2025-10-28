# Gold Fixture Regression Suite

## Overview

The Gold Suite is a comprehensive regression harness for the LOKI synthesis engine. It validates deterministic document assembly against 70+ real-world compliance failures across all five modules (FCA, GDPR, HR, NDA, Tax).

## Running the Suite

```bash
# From project root
python3 tests/semantic/gold_suite.py
```

### Pass Criteria

Each fixture must meet **all** of the following:

1. **Success or valid NeedsReview**: Synthesis must either resolve all gates OR return NeedsReview with legitimate reason (e.g., "No snippets available")
2. **Max 5 iterations**: Must complete within 5 synthesis/validation cycles
3. **Reduce failures**: Final failure count must be < initial count (progress required)

### Output

The suite generates two reports in `tests/semantic/artifacts/`:

- **JSON**: `gold_suite_YYYYMMDDTHHMMSSZ.json` - Machine-readable results
- **Markdown**: `gold_suite_YYYYMMDDTHHMMSSZ.md` - Human-readable report with failure details

## Understanding Results

### Exit Codes
- `0`: All fixtures passed
- `1`: One or more fixtures failed

### Result Status
- ✅ **PASS**: All criteria met, gates resolved
- ❌ **FAIL**: Criteria violated (max retries, no progress, etc.)
- ⚠️  **SKIP**: No initial failures to test

### Common Failure Reasons

1. **"Max retries (5) reached, N failures remain"**
   - Synthesis couldn't resolve all gates in 5 iterations
   - Action: Review unresolved gates, add/improve snippets

2. **"No progress: X → Y failures"**
   - Applied snippets didn't reduce failure count
   - Possible causes: Wrong snippets applied, new gates triggered
   - Action: Review snippet logic and gate interactions

3. **"No snippets available for N remaining failures"**
   - Missing snippet coverage for specific gates
   - Action: Add snippets to `backend/core/synthesis/snippets.py`

## Telemetry Collection

After running the suite, collect telemetry to analyze snippet performance:

```bash
python3 scripts/collect_telemetry.py
```

### Telemetry Insights

- **Snippet Success Rates**: Which snippets reliably resolve gates?
- **Unresolved Gate Frequency**: Which gates need better snippets?
- **Avg Iterations**: How many cycles typically needed?
- **Duration Stats**: Performance benchmarking

### Example Output

```
## Last 24 Hours
Total Operations:     74
Success Rate:         31.1%
Avg Iterations:       2.45
Avg Duration:         90.3ms
Needs Review Count:   51

### Top 10 Most Applied Snippets:
  1. fca_uk:fair_clear_not_misleading: 15 applied, 93.3% success
  2. hr_scottish:accompaniment: 12 applied, 100.0% success
  ...

### Top 10 Unresolved Gates:
  1. nda_uk:protected_whistleblowing: 14 occurrences
  2. tax_uk:vat_invoice_integrity: 10 occurrences
  ...
```

## Gold Fixture Organization

```
tests/semantic/gold_fixtures/
├── fca_uk/          # 15 FCA UK fixtures
├── gdpr_uk/         # 15 GDPR UK fixtures
├── hr_scottish/     # 15 HR Scottish fixtures
├── nda_uk/          # 14 NDA UK fixtures
└── tax_uk/          # 15 Tax UK fixtures
```

Each fixture is a single `.txt` file containing deliberately non-compliant text designed to trigger specific gate failures.

## Adding New Fixtures

1. Create `.txt` file in appropriate module directory
2. Name descriptively (e.g., `16_new_violation_pattern.txt`)
3. Write text that triggers 1-5 gate failures
4. Run suite to validate behavior

## Integration with CI/CD

The suite is designed for automated testing:

```yaml
# Example GitHub Actions workflow
- name: Run Gold Suite
  run: python3 tests/semantic/gold_suite.py

- name: Upload Reports
  uses: actions/upload-artifact@v2
  with:
    name: gold-suite-reports
    path: tests/semantic/artifacts/gold_suite_*.{json,md}
```

## Debugging Failures

### Step 1: Review the Markdown Report

```bash
cat tests/semantic/artifacts/gold_suite_*.md
```

Look for:
- Which fixtures failed?
- What was the fail reason?
- Initial vs final failure counts

### Step 2: Run Single Fixture

```python
# In Python shell
from core.async_engine import AsyncLOKIEngine
from core.synthesis import SynthesisEngine

engine = AsyncLOKIEngine(max_workers=4)
engine.load_module('fca_uk')  # Your module

text = open('tests/semantic/gold_fixtures/fca_uk/01_misleading_returns.txt').read()
validation = engine.check_document(text, 'test', ['fca_uk'])

synthesis_engine = SynthesisEngine(engine)
result = synthesis_engine.synthesize(text, validation, {}, ['fca_uk'])

print(f"Success: {result['success']}")
print(f"Iterations: {result['iterations']}")
print(f"Reason: {result['reason']}")
```

### Step 3: Check Snippet Coverage

```python
from core.synthesis import SnippetRegistry

registry = SnippetRegistry()
snippet = registry.get_snippet('fca_uk', 'problematic_gate')

if not snippet:
    print("❌ Missing snippet for this gate")
else:
    print(f"✓ Snippet found: {snippet.template[:100]}...")
```

### Step 4: Review Audit Log

```bash
# Check synthesis operations logged
python3 scripts/collect_telemetry.py
```

## Performance Benchmarks

| Metric | Target | Typical |
|--------|--------|---------|
| Avg Duration | <200ms | ~90ms |
| Avg Iterations | ≤3 | ~2.5 |
| Success Rate | >80% | 31% (initial) |
| Max Iteration Limit | 5 | 5 |

**Note**: Initial success rate of 31% is expected for first run - indicates which snippets need development.

## Known Limitations

1. **Complex Multi-Gate Failures**: Some fixtures trigger 5+ gates simultaneously. May need multi-pass strategy.
2. **Gate Interactions**: Applying snippets can trigger new gates (e.g., adding data collection language triggers GDPR gates).
3. **Context Requirements**: Some snippets need rich context variables to be effective.

## Future Enhancements

- [ ] Parallel fixture execution
- [ ] Fixture difficulty scoring
- [ ] Automated snippet suggestion from failures
- [ ] Historical trend analysis
- [ ] Performance regression detection

## Support

For questions or issues:
- Review `SYNTHESIS_DOCUMENTATION.md` for synthesis architecture
- Check audit logs with `scripts/collect_telemetry.py`
- Examine specific fixtures in `tests/semantic/gold_fixtures/`
- Run unit tests: `python3 -m pytest tests/test_synthesis.py -v`
