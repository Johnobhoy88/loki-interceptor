# Semantic Regression Harness - Architecture Upgrade

## Execute Upgrade

To implement the full architecture with baselines, diffs, and approval workflows:

```bash
python UPGRADE_HARNESS.py
```

This upgrades the existing harness (created by EXECUTE_SETUP_NOW.py) with advanced features.

## What's Added

### 1. Golden Baselines (`tests/semantic/baselines/`)
- One `.baseline.json` per fixture
- Stores gate statuses, semantic hits, review flags
- Versioned automatically
- Archived before updates

### 2. Enhanced Test Runner (`run_regression.py`)
- Loads engine output and diff-checks vs baseline
- If match → PASS
- If diff → Records delta (new/removed fails, risk changes, semantic deltas)
- Generates autopatch with smart hints

### 3. Autopatch System
- Creates `.patch.json` when diffs detected
- Annotates changes: "candidate improvement" vs "potential regression"
- Ready-to-apply after human approval

### 4. Approval Workflow CLI (`approve_baseline.py`)
- Review diffs interactively
- Approve → merges new expectations into baseline
- Reject → keeps current baseline
- View full patch or quit
- Command: `python tests/semantic/approve_baseline.py <fixture>`

### 5. Context Logging (`tests/semantic/history/`)
- Every run logged: git commit, timestamp, validation report
- Track semantic drift over time
- Rollback capability if auto-heal was wrong

### 6. Smart Hints
- Detects repeated misses (synonyms never matched)
- Suggests adding phrases to semantic rules
- Highlights patterns for human reviewers
- Identifies improvements vs regressions

### 7. Analysis Tools (`analyze_baselines.py`)
- Current status overview
- Trend analysis over time
- Export to JSON
- Commands: `make semantic-status`, `make semantic-trends`

## Workflow Changes

### Before (Manual)
1. Run tests → failures
2. Manually edit expected.json
3. Re-run tests
4. Commit changes

### After (Semi-Automated)
1. Run `make semantic-regression` → produces diff + patch
2. Review: `python tests/semantic/approve_baseline.py fca_fail.txt`
3. Approve/reject with one command
4. Commit updated baseline
5. Historical tracking automatic

## Example Session

```bash
$ make semantic-regression

⚠ DIFF DETECTED - Classification: CANDIDATE_IMPROVEMENT
   ➕ New failures: ['offshore_shell_company']
   📊 Semantic hits: 3 → 4 (Δ+1)
   
   💡 Smart Hints:
      🔵 Semantic hit count increased by 1
         → Likely improved synonym coverage
   
   📝 Autopatch generated: tax_scheme.patch.json
   ℹ Run 'python tests/semantic/approve_baseline.py tax_scheme.txt'

$ python tests/semantic/approve_baseline.py tax_scheme.txt

PATCH REVIEW: tax_scheme.txt
Classification: CANDIDATE_IMPROVEMENT

📋 Gate Failures:
   ➕ New: offshore_shell_company
   ✓ Unchanged: 3 gates

Options:
  [a] Approve - Update baseline
  [r] Reject - Keep current
  [v] View - Show full JSON
  [q] Quit

Your choice: a

✅ Patch approved for tax_scheme.txt
   📦 Archived to: tax_scheme_20251015_233000.baseline.json
   ✅ Baseline updated to v1.0.1

$ git add tests/semantic/baselines/
$ git commit -m "Approve tax scheme detection improvement"
```

## Key Benefits

- **Automated diff capture** - no manual JSON editing
- **Approval-based** - human stays in control
- **Historical tracking** - revert if needed
- **Smart guidance** - hints about what changed and why
- **Rollback safety** - baselines archived automatically

## Integration Points

- Works with existing fixtures and modules
- Compatible with CI/CD pipelines
- Exports to JSON for external analysis
- Logs everything for audit trails

## Next Steps

1. Run `python UPGRADE_HARNESS.py` to apply upgrades
2. Execute `make semantic-regression` to test
3. Review any patches generated
4. Commit approved baselines
5. Push to feature branch

This isn't fully self-repairing (human approval required), but automates the boring parts while keeping humans in control.
