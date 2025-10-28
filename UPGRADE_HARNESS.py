#!/usr/bin/env python3
"""
Upgrade the semantic regression harness with:
- Golden baselines storage
- Diff-checking against baselines
- Autopatch generation
- Approval workflow CLI
- Context logging
- Smart hints for semantic drift
"""
import json
import subprocess
from pathlib import Path
from datetime import datetime

def git_command(cmd):
    """Execute a git command"""
    try:
        result = subprocess.run(
            f"git {cmd}",
            shell=True,
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent)
        )
        return result
    except Exception as e:
        print(f"Git command failed: {e}")
        return None

def main():
    print("="*70)
    print("UPGRADING SEMANTIC REGRESSION HARNESS")
    print("Advanced Features: Baselines, Diffs, Autopatches, Approval CLI")
    print("="*70)

    BASE_DIR = Path(__file__).parent
    TESTS_DIR = BASE_DIR / "tests" / "semantic"
    BASELINES_DIR = TESTS_DIR / "baselines"
    HISTORY_DIR = TESTS_DIR / "history"
    
    # Ensure we're on the right branch
    result = git_command("rev-parse --abbrev-ref HEAD")
    if result and "feature/semantic-regression" not in result.stdout:
        print("\n⚠ Not on feature/semantic-regression branch. Switching...")
        git_command("checkout feature/semantic-regression")
    
    print("\n[1/7] Creating enhanced directory structure...")
    BASELINES_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    print(f"      ✓ {BASELINES_DIR.relative_to(BASE_DIR)}")
    print(f"      ✓ {HISTORY_DIR.relative_to(BASE_DIR)}")
    
    # Create .gitkeep for history (logs shouldn't be committed)
    (HISTORY_DIR / ".gitkeep").write_text("", encoding='utf-8')
    (HISTORY_DIR / ".gitignore").write_text("*.log\n*.json\n", encoding='utf-8')
    
    print("\n[2/7] Creating golden baselines from expected.json...")
    expected_path = TESTS_DIR / "expected.json"
    if expected_path.exists():
        expected = json.loads(expected_path.read_text(encoding='utf-8'))
        
        for fixture_name, expectations in expected.items():
            baseline = {
                "fixture": fixture_name,
                "version": "1.0.0",
                "created_at": datetime.utcnow().isoformat() + "Z",
                "git_commit": git_command("rev-parse HEAD").stdout.strip() if git_command("rev-parse HEAD") else "unknown",
                "expected_gates": {
                    "failures": expectations.get("expected_failures", []),
                    "warnings": expectations.get("expected_warnings", [])
                },
                "expected_semantic_hits": {
                    "min": expectations.get("min_semantic_hits", 0),
                    "typical": expectations.get("min_semantic_hits", 0)
                },
                "expected_flags": {
                    "needs_review": expectations.get("needs_review", False),
                    "overall_risk": expectations.get("overall_risk", "LOW")
                },
                "modules": expectations.get("modules", []),
                "notes": f"Baseline for {fixture_name}"
            }
            
            baseline_file = BASELINES_DIR / f"{fixture_name.replace('.txt', '')}.baseline.json"
            baseline_file.write_text(json.dumps(baseline, indent=2), encoding='utf-8')
            print(f"      ✓ {baseline_file.name}")
    
    print("\n[3/7] Creating upgraded run_regression.py with diff checking...")
    
    upgraded_regression = '''#!/usr/bin/env python3
"""
Semantic Layer Regression Test Harness - Enhanced Edition

Features:
- Golden baseline comparison with detailed diffs
- Autopatch generation for semantic drift
- Context logging with git metadata
- Smart hints for recurring patterns
- Approval workflow support
"""
import json
import sys
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
from collections import defaultdict

# Determine paths relative to this script
SCRIPT_DIR = Path(__file__).parent
FIXTURES_DIR = SCRIPT_DIR / "fixtures"
BASELINES_DIR = SCRIPT_DIR / "baselines"
HISTORY_DIR = SCRIPT_DIR / "history"
BACKEND_DIR = SCRIPT_DIR.parent.parent / "backend"

# Add backend to path for imports
sys.path.insert(0, str(BACKEND_DIR))

try:
    from server import app
except ImportError as e:
    print(f"❌ Failed to import backend.server.app: {e}")
    print(f"   Make sure PYTHONPATH includes: {BACKEND_DIR}")
    sys.exit(1)


def get_git_commit() -> str:
    """Get current git commit hash"""
    try:
        import subprocess
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=str(SCRIPT_DIR)
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except:
        return "unknown"


def load_baseline(fixture_name: str) -> Dict[str, Any]:
    """Load golden baseline for a fixture"""
    baseline_file = BASELINES_DIR / f"{fixture_name.replace('.txt', '')}.baseline.json"
    if not baseline_file.exists():
        return None
    
    with open(baseline_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_fixture(filename: str) -> str:
    """Load fixture text content"""
    with open(FIXTURES_DIR / filename, 'r', encoding='utf-8') as f:
        return f.read()


def extract_gate_ids(validation_result: Dict[str, Any]) -> Dict[str, List[str]]:
    """Extract gate IDs by status from validation result"""
    failures = []
    warnings = []
    passes = []
    
    for gate in validation_result.get('gates', []):
        gate_id = gate.get('id', '')
        status = gate.get('status', '').upper()
        
        if status == 'FAIL':
            failures.append(gate_id)
        elif status == 'WARNING':
            warnings.append(gate_id)
        elif status == 'PASS':
            passes.append(gate_id)
    
    return {
        'failures': sorted(failures),
        'warnings': sorted(warnings),
        'passes': sorted(passes)
    }


def compute_diff(baseline: Dict[str, Any], actual: Dict[str, Any]) -> Dict[str, Any]:
    """Compute detailed diff between baseline and actual results"""
    diff = {
        "has_changes": False,
        "gate_changes": {},
        "semantic_changes": {},
        "flag_changes": {},
        "classification": "unchanged"
    }
    
    # Compare gate failures
    baseline_failures = set(baseline.get("expected_gates", {}).get("failures", []))
    actual_failures = set(actual.get("failures", []))
    
    new_failures = actual_failures - baseline_failures
    missing_failures = baseline_failures - actual_failures
    
    if new_failures or missing_failures:
        diff["has_changes"] = True
        diff["gate_changes"]["failures"] = {
            "new": sorted(list(new_failures)),
            "missing": sorted(list(missing_failures)),
            "unchanged": sorted(list(baseline_failures & actual_failures))
        }
    
    # Compare warnings
    baseline_warnings = set(baseline.get("expected_gates", {}).get("warnings", []))
    actual_warnings = set(actual.get("warnings", []))
    
    new_warnings = actual_warnings - baseline_warnings
    missing_warnings = baseline_warnings - actual_warnings
    
    if new_warnings or missing_warnings:
        diff["has_changes"] = True
        diff["gate_changes"]["warnings"] = {
            "new": sorted(list(new_warnings)),
            "missing": sorted(list(missing_warnings)),
            "unchanged": sorted(list(baseline_warnings & actual_warnings))
        }
    
    # Compare semantic hits
    baseline_hits = baseline.get("expected_semantic_hits", {}).get("typical", 0)
    actual_hits = actual.get("semantic_hits", 0)
    
    if actual_hits != baseline_hits:
        diff["has_changes"] = True
        diff["semantic_changes"] = {
            "baseline": baseline_hits,
            "actual": actual_hits,
            "delta": actual_hits - baseline_hits,
            "percentage_change": ((actual_hits - baseline_hits) / max(baseline_hits, 1)) * 100
        }
    
    # Compare flags
    baseline_review = baseline.get("expected_flags", {}).get("needs_review", False)
    actual_review = actual.get("needs_review", False)
    baseline_risk = baseline.get("expected_flags", {}).get("overall_risk", "LOW")
    actual_risk = actual.get("overall_risk", "UNKNOWN")
    
    if baseline_review != actual_review or baseline_risk != actual_risk:
        diff["has_changes"] = True
        diff["flag_changes"] = {
            "needs_review": {"baseline": baseline_review, "actual": actual_review},
            "overall_risk": {"baseline": baseline_risk, "actual": actual_risk}
        }
    
    # Classify the change
    if diff["has_changes"]:
        if new_failures:
            diff["classification"] = "potential_improvement"  # Catching more issues
        elif missing_failures:
            diff["classification"] = "potential_regression"  # Missing known issues
        elif new_warnings and not missing_warnings:
            diff["classification"] = "candidate_improvement"  # More cautious
        elif actual_hits > baseline_hits:
            diff["classification"] = "candidate_improvement"  # Better detection
        else:
            diff["classification"] = "needs_review"
    
    return diff


def generate_autopatch(fixture_name: str, baseline: Dict[str, Any], 
                       actual: Dict[str, Any], diff: Dict[str, Any]) -> Dict[str, Any]:
    """Generate an autopatch for updating the baseline"""
    patch = {
        "fixture": fixture_name,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "git_commit": get_git_commit(),
        "classification": diff["classification"],
        "changes": diff,
        "proposed_baseline": {
            "fixture": fixture_name,
            "version": baseline.get("version", "1.0.0"),
            "updated_at": datetime.utcnow().isoformat() + "Z",
            "git_commit": get_git_commit(),
            "expected_gates": {
                "failures": actual.get("failures", []),
                "warnings": actual.get("warnings", [])
            },
            "expected_semantic_hits": {
                "min": max(0, actual.get("semantic_hits", 0) - 1),
                "typical": actual.get("semantic_hits", 0)
            },
            "expected_flags": {
                "needs_review": actual.get("needs_review", False),
                "overall_risk": actual.get("overall_risk", "LOW")
            },
            "modules": baseline.get("modules", []),
            "notes": f"Updated from test run at {datetime.utcnow().isoformat()}"
        },
        "smart_hints": []
    }
    
    # Add smart hints
    if "gate_changes" in diff and "failures" in diff["gate_changes"]:
        new_failures = diff["gate_changes"]["failures"].get("new", [])
        if new_failures:
            patch["smart_hints"].append({
                "type": "new_detection",
                "message": f"New gate failures detected: {', '.join(new_failures)}",
                "suggestion": "Review if these are legitimate catches or false positives"
            })
        
        missing_failures = diff["gate_changes"]["failures"].get("missing", [])
        if missing_failures:
            patch["smart_hints"].append({
                "type": "missing_detection",
                "message": f"Previously caught failures no longer detected: {', '.join(missing_failures)}",
                "suggestion": "CRITICAL: Verify semantic rules haven't been weakened",
                "severity": "high"
            })
    
    if "semantic_changes" in diff and diff["semantic_changes"]:
        delta = diff["semantic_changes"]["delta"]
        if delta > 0:
            patch["smart_hints"].append({
                "type": "semantic_improvement",
                "message": f"Semantic hit count increased by {delta}",
                "suggestion": "Likely improved synonym coverage or pattern matching"
            })
        elif delta < 0:
            patch["smart_hints"].append({
                "type": "semantic_regression",
                "message": f"Semantic hit count decreased by {abs(delta)}",
                "suggestion": "Review if legitimate phrases are no longer matching",
                "severity": "medium"
            })
    
    return patch


def log_run_context(fixture_name: str, validation: Dict[str, Any], 
                    baseline: Dict[str, Any], diff: Dict[str, Any]):
    """Log full context of test run for historical tracking"""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    log_file = HISTORY_DIR / f"{fixture_name.replace('.txt', '')}_{timestamp}.log.json"
    
    context = {
        "fixture": fixture_name,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "git_commit": get_git_commit(),
        "baseline_version": baseline.get("version", "unknown") if baseline else None,
        "raw_validation": validation,
        "diff": diff,
        "result": "PASS" if not diff.get("has_changes", False) else "DIFF_DETECTED"
    }
    
    log_file.write_text(json.dumps(context, indent=2), encoding='utf-8')


def validate_fixture(client, fixture_name: str, baseline: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """Validate a single fixture against baseline with diff generation"""
    print(f"\\n{'='*60}")
    print(f"Testing: {fixture_name}")
    print('='*60)
    
    if not baseline:
        print("⚠ No baseline found - using legacy validation")
        return False, {"error": "no_baseline"}
    
    # Load fixture text
    text = load_fixture(fixture_name)
    modules = baseline.get("modules", [])
    
    # Make request to API
    response = client.post(
        '/api/validate-document',
        json={
            'text': text,
            'document_type': 'test',
            'modules': modules
        },
        content_type='application/json'
    )
    
    if response.status_code != 200:
        print(f"❌ API returned status {response.status_code}")
        return False, {"error": "api_error"}
    
    result = response.get_json()
    validation = result.get('validation', {})
    
    # Extract actual results
    gate_results = extract_gate_ids(validation)
    actual_results = {
        "failures": gate_results['failures'],
        "warnings": gate_results['warnings'],
        "semantic_hits": validation.get('semantic_hits', 0),
        "needs_review": validation.get('needs_review', False),
        "overall_risk": validation.get('overall_risk', 'UNKNOWN')
    }
    
    # Compute diff
    diff = compute_diff(baseline, actual_results)
    
    # Log context
    log_run_context(fixture_name, validation, baseline, diff)
    
    # Display results
    if not diff["has_changes"]:
        print("✅ BASELINE MATCH - No changes detected")
        print(f"   Failures: {len(actual_results['failures'])}")
        print(f"   Warnings: {len(actual_results['warnings'])}")
        print(f"   Semantic hits: {actual_results['semantic_hits']}")
        return True, {"diff": diff, "actual": actual_results}
    
    # Changes detected - show diff
    print(f"⚠ DIFF DETECTED - Classification: {diff['classification'].upper()}")
    
    if "gate_changes" in diff and "failures" in diff["gate_changes"]:
        fc = diff["gate_changes"]["failures"]
        if fc.get("new"):
            print(f"   ➕ New failures: {fc['new']}")
        if fc.get("missing"):
            print(f"   ➖ Missing failures: {fc['missing']}")
    
    if "gate_changes" in diff and "warnings" in diff["gate_changes"]:
        wc = diff["gate_changes"]["warnings"]
        if wc.get("new"):
            print(f"   ➕ New warnings: {wc['new']}")
        if wc.get("missing"):
            print(f"   ➖ Missing warnings: {wc['missing']}")
    
    if "semantic_changes" in diff and diff["semantic_changes"]:
        sc = diff["semantic_changes"]
        print(f"   📊 Semantic hits: {sc['baseline']} → {sc['actual']} (Δ{sc['delta']:+d})")
    
    if "flag_changes" in diff:
        fc = diff["flag_changes"]
        if "needs_review" in fc:
            print(f"   🚩 needs_review: {fc['needs_review']['baseline']} → {fc['needs_review']['actual']}")
        if "overall_risk" in fc:
            print(f"   ⚠ overall_risk: {fc['overall_risk']['baseline']} → {fc['overall_risk']['actual']}")
    
    # Generate autopatch
    patch = generate_autopatch(fixture_name, baseline, actual_results, diff)
    patch_file = SCRIPT_DIR / f"{fixture_name.replace('.txt', '')}.patch.json"
    patch_file.write_text(json.dumps(patch, indent=2), encoding='utf-8')
    print(f"\\n   📝 Autopatch generated: {patch_file.name}")
    
    # Show smart hints
    if patch.get("smart_hints"):
        print("\\n   💡 Smart Hints:")
        for hint in patch["smart_hints"]:
            severity = hint.get("severity", "info")
            icon = "🔴" if severity == "high" else "🟡" if severity == "medium" else "🔵"
            print(f"      {icon} {hint['message']}")
            print(f"         → {hint['suggestion']}")
    
    print(f"\\n   ℹ Run 'python tests/semantic/approve_baseline.py {fixture_name}' to review")
    
    return False, {"diff": diff, "actual": actual_results, "patch": patch}


def main():
    """Run all regression tests with baseline comparison"""
    print("="*60)
    print("SEMANTIC LAYER REGRESSION TESTS - Enhanced")
    print("="*60)
    
    # Get all fixtures
    fixtures = sorted([f.name for f in FIXTURES_DIR.glob("*.txt")])
    
    if not fixtures:
        print("❌ No fixtures found")
        return 1
    
    # Create test client
    with app.test_client() as client:
        results = {}
        all_patches = {}
        
        for fixture_name in fixtures:
            baseline = load_baseline(fixture_name)
            
            if not baseline:
                print(f"\\n⚠ No baseline for {fixture_name} - skipping")
                results[fixture_name] = "no_baseline"
                continue
            
            try:
                passed, data = validate_fixture(client, fixture_name, baseline)
                results[fixture_name] = "pass" if passed else "diff"
                
                if not passed and "patch" in data:
                    all_patches[fixture_name] = data["patch"]
                    
            except Exception as e:
                print(f"❌ Exception testing {fixture_name}: {e}")
                import traceback
                traceback.print_exc()
                results[fixture_name] = "error"
    
    # Summary
    print(f"\\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    
    passed = sum(1 for v in results.values() if v == "pass")
    diffs = sum(1 for v in results.values() if v == "diff")
    errors = sum(1 for v in results.values() if v == "error")
    total = len(results)
    
    for fixture_name, status in results.items():
        if status == "pass":
            print(f"✅ PASS: {fixture_name}")
        elif status == "diff":
            print(f"⚠ DIFF: {fixture_name} (autopatch available)")
        elif status == "error":
            print(f"❌ ERROR: {fixture_name}")
        else:
            print(f"⊘ SKIP: {fixture_name} ({status})")
    
    print(f"\\n{passed}/{total} baseline matches")
    
    if diffs > 0:
        print(f"\\n⚠ {diffs} fixture(s) have diffs - patches generated")
        print("\\nReview and approve changes:")
        for fixture_name in [k for k, v in results.items() if v == "diff"]:
            print(f"  python tests/semantic/approve_baseline.py {fixture_name}")
        print("\\nOr approve all at once:")
        print("  python tests/semantic/approve_baseline.py --all")
        return 1
    
    if errors > 0:
        print(f"\\n❌ {errors} test(s) failed with errors")
        return 1
    
    print("\\n🎉 All baselines match - semantic layer is stable!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
'''
    
    (TESTS_DIR / "run_regression.py").write_text(upgraded_regression, encoding='utf-8')
    print("      ✓ run_regression.py upgraded")
    
    print("\n[4/7] Creating approval workflow CLI...")
    
    approval_cli = '''#!/usr/bin/env python3
"""
Semantic Baseline Approval Tool

Allows human review and approval of semantic drift patches.

Usage:
    python approve_baseline.py <fixture_name>        # Review single fixture
    python approve_baseline.py --all                 # Review all pending patches
    python approve_baseline.py --rollback <fixture>  # Rollback to previous baseline
    python approve_baseline.py --history <fixture>   # Show change history
"""
import json
import sys
import shutil
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
BASELINES_DIR = SCRIPT_DIR / "baselines"
HISTORY_DIR = SCRIPT_DIR / "history"
ARCHIVE_DIR = BASELINES_DIR / "archive"


def load_patch(fixture_name: str):
    """Load autopatch for a fixture"""
    patch_file = SCRIPT_DIR / f"{fixture_name.replace('.txt', '')}.patch.json"
    if not patch_file.exists():
        return None
    
    with open(patch_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def archive_baseline(fixture_name: str):
    """Archive current baseline before updating"""
    ARCHIVE_DIR.mkdir(exist_ok=True)
    
    baseline_file = BASELINES_DIR / f"{fixture_name.replace('.txt', '')}.baseline.json"
    if not baseline_file.exists():
        return
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    archive_file = ARCHIVE_DIR / f"{fixture_name.replace('.txt', '')}_{timestamp}.baseline.json"
    
    shutil.copy2(baseline_file, archive_file)
    print(f"   📦 Archived to: {archive_file.name}")


def apply_patch(fixture_name: str, patch: dict):
    """Apply approved patch to baseline"""
    archive_baseline(fixture_name)
    
    baseline_file = BASELINES_DIR / f"{fixture_name.replace('.txt', '')}.baseline.json"
    proposed = patch["proposed_baseline"]
    
    # Update version
    if baseline_file.exists():
        current = json.loads(baseline_file.read_text(encoding='utf-8'))
        version_parts = current.get("version", "1.0.0").split(".")
        version_parts[-1] = str(int(version_parts[-1]) + 1)
        proposed["version"] = ".".join(version_parts)
    
    baseline_file.write_text(json.dumps(proposed, indent=2), encoding='utf-8')
    
    # Remove patch file
    patch_file = SCRIPT_DIR / f"{fixture_name.replace('.txt', '')}.patch.json"
    if patch_file.exists():
        patch_file.unlink()
    
    print(f"   ✅ Baseline updated to v{proposed['version']}")


def show_patch_review(fixture_name: str, patch: dict):
    """Display patch for human review"""
    print("\\n" + "="*70)
    print(f"PATCH REVIEW: {fixture_name}")
    print("="*70)
    
    print(f"\\nClassification: {patch['classification'].upper()}")
    print(f"Generated: {patch['generated_at']}")
    print(f"Commit: {patch['git_commit'][:8]}")
    
    changes = patch['changes']
    
    if "gate_changes" in changes and "failures" in changes["gate_changes"]:
        print("\\n📋 Gate Failures:")
        fc = changes["gate_changes"]["failures"]
        if fc.get("new"):
            print(f"   ➕ New: {', '.join(fc['new'])}")
        if fc.get("missing"):
            print(f"   ➖ Missing: {', '.join(fc['missing'])}")
        if fc.get("unchanged"):
            print(f"   ✓ Unchanged: {len(fc['unchanged'])} gates")
    
    if "gate_changes" in changes and "warnings" in changes["gate_changes"]:
        print("\\n⚠ Gate Warnings:")
        wc = changes["gate_changes"]["warnings"]
        if wc.get("new"):
            print(f"   ➕ New: {', '.join(wc['new'])}")
        if wc.get("missing"):
            print(f"   ➖ Missing: {', '.join(wc['missing'])}")
    
    if "semantic_changes" in changes and changes["semantic_changes"]:
        print("\\n📊 Semantic Hits:")
        sc = changes["semantic_changes"]
        print(f"   {sc['baseline']} → {sc['actual']} (Δ{sc['delta']:+d}, {sc['percentage_change']:+.1f}%)")
    
    if "flag_changes" in changes:
        print("\\n🚩 Flags:")
        fc = changes["flag_changes"]
        if "needs_review" in fc:
            nr = fc["needs_review"]
            print(f"   needs_review: {nr['baseline']} → {nr['actual']}")
        if "overall_risk" in fc:
            risk = fc["overall_risk"]
            print(f"   overall_risk: {risk['baseline']} → {risk['actual']}")
    
    if patch.get("smart_hints"):
        print("\\n💡 Smart Hints:")
        for hint in patch["smart_hints"]:
            severity = hint.get("severity", "info")
            icon = "🔴" if severity == "high" else "🟡" if severity == "medium" else "🔵"
            print(f"   {icon} {hint['message']}")
            print(f"      → {hint['suggestion']}")
    
    print("\\n" + "="*70)


def review_single(fixture_name: str):
    """Review and approve/reject a single patch"""
    patch = load_patch(fixture_name)
    
    if not patch:
        print(f"❌ No patch found for {fixture_name}")
        return 1
    
    show_patch_review(fixture_name, patch)
    
    print("\\nOptions:")
    print("  [a] Approve - Update baseline with these changes")
    print("  [r] Reject - Keep current baseline, discard patch")
    print("  [v] View - Show full patch JSON")
    print("  [q] Quit - Cancel without changes")
    
    choice = input("\\nYour choice: ").strip().lower()
    
    if choice == 'a':
        apply_patch(fixture_name, patch)
        print(f"\\n✅ Patch approved for {fixture_name}")
        return 0
    elif choice == 'r':
        patch_file = SCRIPT_DIR / f"{fixture_name.replace('.txt', '')}.patch.json"
        if patch_file.exists():
            patch_file.unlink()
        print(f"\\n❌ Patch rejected for {fixture_name}")
        return 0
    elif choice == 'v':
        print("\\n" + json.dumps(patch, indent=2))
        return review_single(fixture_name)
    else:
        print("\\n⊘ Cancelled")
        return 0


def review_all():
    """Review all pending patches"""
    patches = sorted(SCRIPT_DIR.glob("*.patch.json"))
    
    if not patches:
        print("✅ No pending patches")
        return 0
    
    print(f"\\nFound {len(patches)} pending patch(es):\\n")
    
    for patch_file in patches:
        fixture_name = patch_file.stem.replace(".patch", "") + ".txt"
        patch = json.loads(patch_file.read_text(encoding='utf-8'))
        
        print(f"  • {fixture_name} - {patch['classification']}")
    
    print("\\nReview each patch? [y/n]: ", end='')
    if input().strip().lower() != 'y':
        return 0
    
    for patch_file in patches:
        fixture_name = patch_file.stem.replace(".patch", "") + ".txt"
        result = review_single(fixture_name)
        if result != 0:
            return result
    
    print("\\n🎉 All patches reviewed!")
    return 0


def show_history(fixture_name: str):
    """Show change history for a fixture"""
    prefix = fixture_name.replace('.txt', '')
    history_files = sorted(HISTORY_DIR.glob(f"{prefix}_*.log.json"), reverse=True)
    
    if not history_files:
        print(f"No history found for {fixture_name}")
        return
    
    print(f"\\n{'='*70}")
    print(f"CHANGE HISTORY: {fixture_name}")
    print("="*70 + "\\n")
    
    for i, log_file in enumerate(history_files[:10]):  # Show last 10
        log = json.loads(log_file.read_text(encoding='utf-8'))
        
        timestamp = log.get("timestamp", "unknown")
        commit = log.get("git_commit", "unknown")[:8]
        result = log.get("result", "unknown")
        
        print(f"{i+1}. {timestamp}")
        print(f"   Commit: {commit}")
        print(f"   Result: {result}")
        
        if "diff" in log and log["diff"].get("has_changes"):
            diff = log["diff"]
            if "semantic_changes" in diff:
                sc = diff["semantic_changes"]
                print(f"   Semantic: {sc.get('baseline', 0)} → {sc.get('actual', 0)}")
        
        print()


def rollback_baseline(fixture_name: str):
    """Rollback to a previous baseline version"""
    prefix = fixture_name.replace('.txt', '')
    archives = sorted(ARCHIVE_DIR.glob(f"{prefix}_*.baseline.json"), reverse=True)
    
    if not archives:
        print(f"No archived baselines found for {fixture_name}")
        return 1
    
    print(f"\\nAvailable baselines for {fixture_name}:\\n")
    for i, archive in enumerate(archives[:5]):
        print(f"  {i+1}. {archive.stem}")
    
    print("\\nSelect version to restore (1-5) or 'q' to cancel: ", end='')
    choice = input().strip()
    
    if choice.lower() == 'q':
        return 0
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(archives):
            selected = archives[idx]
            baseline_file = BASELINES_DIR / f"{prefix}.baseline.json"
            
            # Archive current before rollback
            archive_baseline(fixture_name)
            
            # Restore
            shutil.copy2(selected, baseline_file)
            print(f"\\n✅ Rolled back to {selected.name}")
            return 0
    except ValueError:
        pass
    
    print("\\n❌ Invalid selection")
    return 1


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    
    command = sys.argv[1]
    
    if command == "--all":
        return review_all()
    elif command == "--history":
        if len(sys.argv) < 3:
            print("Usage: approve_baseline.py --history <fixture_name>")
            return 1
        show_history(sys.argv[2])
        return 0
    elif command == "--rollback":
        if len(sys.argv) < 3:
            print("Usage: approve_baseline.py --rollback <fixture_name>")
            return 1
        return rollback_baseline(sys.argv[2])
    else:
        # Assume it's a fixture name
        return review_single(command)


if __name__ == '__main__':
    sys.exit(main())
'''
    
    (TESTS_DIR / "approve_baseline.py").write_text(approval_cli, encoding='utf-8')
    print("      ✓ approve_baseline.py created")
    
    print("\n[5/7] Creating baseline analysis tool...")
    
    analysis_tool = '''#!/usr/bin/env python3
"""
Semantic Baseline Analysis Tool

Analyze semantic drift trends across all fixtures.

Usage:
    python analyze_baselines.py              # Show current status
    python analyze_baselines.py --trends     # Show drift trends over time
    python analyze_baselines.py --export     # Export analysis to JSON
"""
import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent
BASELINES_DIR = SCRIPT_DIR / "baselines"
HISTORY_DIR = SCRIPT_DIR / "history"


def analyze_current_baselines():
    """Analyze all current baselines"""
    baselines = sorted(BASELINES_DIR.glob("*.baseline.json"))
    
    if not baselines:
        print("No baselines found")
        return
    
    print("="*70)
    print("CURRENT BASELINE STATUS")
    print("="*70 + "\\n")
    
    for baseline_file in baselines:
        baseline = json.loads(baseline_file.read_text(encoding='utf-8'))
        fixture = baseline.get("fixture", baseline_file.stem)
        version = baseline.get("version", "unknown")
        
        gates = baseline.get("expected_gates", {})
        failures = len(gates.get("failures", []))
        warnings = len(gates.get("warnings", []))
        
        hits = baseline.get("expected_semantic_hits", {})
        typical_hits = hits.get("typical", 0)
        
        flags = baseline.get("expected_flags", {})
        risk = flags.get("overall_risk", "UNKNOWN")
        
        print(f"📋 {fixture}")
        print(f"   Version: {version}")
        print(f"   Gates: {failures} failures, {warnings} warnings")
        print(f"   Semantic hits: {typical_hits}")
        print(f"   Risk level: {risk}")
        print()


def analyze_trends():
    """Analyze semantic drift trends over time"""
    print("="*70)
    print("SEMANTIC DRIFT TRENDS")
    print("="*70 + "\\n")
    
    # Group history by fixture
    fixture_histories = defaultdict(list)
    
    for log_file in sorted(HISTORY_DIR.glob("*.log.json")):
        log = json.loads(log_file.read_text(encoding='utf-8'))
        fixture = log.get("fixture", "unknown")
        fixture_histories[fixture].append(log)
    
    if not fixture_histories:
        print("No historical data available")
        return
    
    for fixture, logs in sorted(fixture_histories.items()):
        print(f"📊 {fixture}")
        print(f"   Runs: {len(logs)}")
        
        diffs_detected = sum(1 for log in logs if log.get("result") == "DIFF_DETECTED")
        if diffs_detected > 0:
            print(f"   Diffs: {diffs_detected} ({diffs_detected/len(logs)*100:.1f}%)")
        
        # Analyze semantic hit trends
        semantic_values = []
        for log in logs:
            val = log.get("raw_validation", {}).get("semantic_hits")
            if val is not None:
                semantic_values.append(val)
        
        if semantic_values:
            avg = sum(semantic_values) / len(semantic_values)
            min_val = min(semantic_values)
            max_val = max(semantic_values)
            print(f"   Semantic hits: avg={avg:.1f}, range=[{min_val}-{max_val}]")
        
        print()


def export_analysis():
    """Export full analysis to JSON"""
    analysis = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "baselines": {},
        "trends": {},
        "summary": {}
    }
    
    # Export current baselines
    for baseline_file in BASELINES_DIR.glob("*.baseline.json"):
        baseline = json.loads(baseline_file.read_text(encoding='utf-8'))
        fixture = baseline.get("fixture", baseline_file.stem)
        analysis["baselines"][fixture] = baseline
    
    # Export trends
    fixture_histories = defaultdict(list)
    for log_file in HISTORY_DIR.glob("*.log.json"):
        log = json.loads(log_file.read_text(encoding='utf-8'))
        fixture = log.get("fixture", "unknown")
        fixture_histories[fixture].append({
            "timestamp": log.get("timestamp"),
            "result": log.get("result"),
            "had_diff": log.get("diff", {}).get("has_changes", False)
        })
    
    analysis["trends"] = dict(fixture_histories)
    
    # Summary statistics
    analysis["summary"] = {
        "total_baselines": len(analysis["baselines"]),
        "total_runs": sum(len(h) for h in fixture_histories.values()),
        "fixtures_with_history": len(fixture_histories)
    }
    
    output_file = SCRIPT_DIR / "baseline_analysis.json"
    output_file.write_text(json.dumps(analysis, indent=2), encoding='utf-8')
    
    print(f"✅ Analysis exported to {output_file.name}")


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--trends":
            analyze_trends()
        elif sys.argv[1] == "--export":
            export_analysis()
        else:
            print(__doc__)
    else:
        analyze_current_baselines()


if __name__ == '__main__':
    main()
'''
    
    (TESTS_DIR / "analyze_baselines.py").write_text(analysis_tool, encoding='utf-8')
    print("      ✓ analyze_baselines.py created")
    
    print("\n[6/7] Updating Makefile with new targets...")
    makefile_path = BASE_DIR / "Makefile"
    makefile_additions = """
# Enhanced semantic regression targets
.PHONY: semantic-regression-enhanced
semantic-regression-enhanced:
\t@echo "Running enhanced semantic regression with baseline comparison..."
\t@python tests/semantic/run_regression.py

.PHONY: semantic-approve-all
semantic-approve-all:
\t@echo "Reviewing all pending baseline patches..."
\t@python tests/semantic/approve_baseline.py --all

.PHONY: semantic-status
semantic-status:
\t@echo "Current baseline status:"
\t@python tests/semantic/analyze_baselines.py

.PHONY: semantic-trends
semantic-trends:
\t@echo "Semantic drift trends:"
\t@python tests/semantic/analyze_baselines.py --trends

# Update the main semantic-regression to use enhanced version
semantic-regression: semantic-regression-enhanced
"""
    
    if makefile_path.exists():
        content = makefile_path.read_text(encoding='utf-8')
        if 'semantic-regression-enhanced' not in content:
            makefile_path.write_text(content + "\n" + makefile_additions, encoding='utf-8')
            print("      ✓ Makefile updated with enhanced targets")
        else:
            print("      ✓ Makefile already has enhanced targets")
    else:
        makefile_path.write_text(makefile_additions, encoding='utf-8')
        print("      ✓ Makefile created with enhanced targets")
    
    print("\n[7/7] Creating documentation...")
    
    readme = '''# Semantic Regression Harness - Enhanced Edition

## Overview

The enhanced semantic regression harness provides automated baseline management, diff detection, and intelligent patching for semantic layer changes.

## Architecture

### Golden Baselines
- Stored in `tests/semantic/baselines/`
- Each fixture has a `.baseline.json` with expected gate statuses, semantic hits, and flags
- Versioned automatically on each update
- Archived before changes for rollback capability

### Test Runner
- Loads current engine output
- Diff-checks against stored baselines
- Generates autopatches when differences detected
- Classifies changes: improvement, regression, or needs-review

### Autopatch Generation
- Creates `.patch.json` files with proposed baseline updates
- Includes smart hints about what changed and why
- Suggests whether changes are improvements or regressions
- Ready to apply after human review

### Approval Workflow
- CLI tool for reviewing patches: `approve_baseline.py`
- Human reviews diffs before merging to baseline
- Approve, reject, or request more context
- Full audit trail of all changes

### Context Logging
- Every test run logged to `tests/semantic/history/`
- Includes git commit, timestamp, raw validation report
- Track semantic drift over time
- Rollback capability if auto-heal proved wrong

### Smart Hints
- Detects recurring misses (synonyms never matched)
- Suggests adding phrases to semantic rules
- Highlights patterns for human review
- Identifies critical regressions vs. improvements

## Usage

### Run Regression Tests
```bash
# Basic run with baseline comparison
make semantic-regression

# Or directly
python tests/semantic/run_regression.py
```

When differences are detected:
- Test exits with code 1
- Produces detailed diff output
- Generates autopatch files (`.patch.json`)
- Provides review commands

### Review Changes
```bash
# Review single fixture
python tests/semantic/approve_baseline.py fca_fail.txt

# Review all pending patches
python tests/semantic/approve_baseline.py --all
# Or: make semantic-approve-all
```

Interactive review options:
- **[a] Approve**: Update baseline with changes
- **[r] Reject**: Discard patch, keep current baseline
- **[v] View**: Show full patch JSON
- **[q] Quit**: Cancel without changes

### Analyze Status
```bash
# Show current baseline status
make semantic-status
# Or: python tests/semantic/analyze_baselines.py

# Show drift trends over time
make semantic-trends
# Or: python tests/semantic/analyze_baselines.py --trends

# Export full analysis
python tests/semantic/analyze_baselines.py --export
```

### Rollback Baseline
```bash
# Rollback to previous version
python tests/semantic/approve_baseline.py --rollback fca_fail.txt
```

### View History
```bash
# Show change history for a fixture
python tests/semantic/approve_baseline.py --history fca_fail.txt
```

## Workflow Example

1. **Make semantic rule changes** in backend/modules/

2. **Run regression tests**:
   ```bash
   make semantic-regression
   ```

3. **Review detected diffs**:
   ```
   ⚠ DIFF DETECTED - Classification: CANDIDATE_IMPROVEMENT
      ➕ New failures: ['new_synonym_matched']
      📊 Semantic hits: 3 → 4 (Δ+1)
      
      💡 Smart Hints:
         🔵 Semantic hit count increased by 1
            → Likely improved synonym coverage or pattern matching
      
      📝 Autopatch generated: fca_fail.patch.json
      ℹ Run 'python tests/semantic/approve_baseline.py fca_fail.txt' to review
   ```

4. **Review and approve**:
   ```bash
   python tests/semantic/approve_baseline.py fca_fail.txt
   ```

5. **Commit updated baseline**:
   ```bash
   git add tests/semantic/baselines/
   git commit -m "Approve semantic improvements for FCA module"
   ```

## Directory Structure

```
tests/semantic/
├── fixtures/              # Test documents
│   ├── fca_fail.txt
│   ├── gdpr_fail.txt
│   ├── hr_contract.txt
│   ├── tax_scheme.txt
│   └── nda_basic.txt
├── baselines/             # Golden baselines
│   ├── fca_fail.baseline.json
│   ├── gdpr_fail.baseline.json
│   ├── archive/          # Historical baselines
│   └── ...
├── history/               # Test run logs (gitignored)
│   ├── .gitkeep
│   ├── .gitignore
│   └── *.log.json
├── run_regression.py      # Enhanced test runner
├── approve_baseline.py    # Approval workflow CLI
├── analyze_baselines.py   # Analysis tool
└── *.patch.json          # Generated patches (temporary)
```

## Change Classifications

- **potential_improvement**: New gate failures detected (catching more issues)
- **potential_regression**: Missing gate failures (semantic rules weakened)
- **candidate_improvement**: New warnings or increased semantic hits
- **needs_review**: Other changes requiring human judgment

## Smart Hints

The system provides intelligent suggestions:

- **New Detection**: New gates triggered - verify legitimacy
- **Missing Detection** ⚠: Previously caught issues no longer detected - CRITICAL
- **Semantic Improvement**: Hit count increased - likely better coverage
- **Semantic Regression**: Hit count decreased - review for missing matches

## Best Practices

1. **Never approve patches blindly** - always review the diff
2. **Archive baselines** - automatic, but verify archives exist
3. **Check history** - understand why changes occurred
4. **Test before committing** - ensure semantic layer works as expected
5. **Document intent** - add notes to baseline JSON if needed

## Maintenance

- Baselines are auto-archived before updates
- History logs retained indefinitely (analyze trends)
- Patch files cleaned up after approval/rejection
- Run `make semantic-status` regularly to monitor drift

## Troubleshooting

**No baseline found**:
- Run initial setup to create baselines from expected.json
- Or manually create baseline from current output

**Patch won't apply**:
- Check for conflicts in baseline file
- Review patch JSON manually
- Use `--rollback` if needed

**Too many false positives**:
- Adjust semantic rules to be more precise
- Update baseline if legitimate behavior changed
- Review smart hints for guidance

## Future Enhancements

- Baseline comparison across git branches
- Automated regression detection in CI/CD
- Slack/email notifications for critical regressions
- Machine learning for smart hint improvement
- Visual diff viewer for complex changes
'''
    
    (TESTS_DIR / "README_ENHANCED.md").write_text(readme, encoding='utf-8')
    print("      ✓ README_ENHANCED.md created")
    
    print("\n[8/8] Staging and committing enhanced files...")
    
    files_to_stage = [
        "tests/semantic/baselines/",
        "tests/semantic/history/.gitkeep",
        "tests/semantic/history/.gitignore",
        "tests/semantic/run_regression.py",
        "tests/semantic/approve_baseline.py",
        "tests/semantic/analyze_baselines.py",
        "tests/semantic/README_ENHANCED.md",
        "Makefile"
    ]
    
    for file in files_to_stage:
        result = git_command(f"add {file}")
        if result and result.returncode == 0:
            print(f"      ✓ {file}")
    
    result = git_command('commit -m "Upgrade semantic harness: baselines, diffs, autopatches, approval CLI"')
    if result and result.returncode == 0:
        print("\n      ✓ Committed successfully")
    elif result and ("nothing to commit" in result.stdout + result.stderr):
        print("\n      ⚠ Nothing new to commit")
    
    print("\n" + "="*70)
    print("✅ SEMANTIC HARNESS UPGRADED!")
    print("="*70)
    
    print("\n🎯 New Features:")
    print("   ✓ Golden baselines with versioning")
    print("   ✓ Automated diff detection")
    print("   ✓ Autopatch generation")
    print("   ✓ Human approval workflow")
    print("   ✓ Context logging and history")
    print("   ✓ Smart hints for semantic drift")
    print("   ✓ Rollback capability")
    print("   ✓ Trend analysis tools")
    
    print("\n📘 New Commands:")
    print("   make semantic-regression       # Run with baseline comparison")
    print("   make semantic-approve-all      # Review all patches")
    print("   make semantic-status           # Show baseline status")
    print("   make semantic-trends           # Analyze drift trends")
    
    print("\n📝 Workflow:")
    print("   1. make semantic-regression    # Detect changes")
    print("   2. Review autopatch files")
    print("   3. python tests/semantic/approve_baseline.py <fixture>")
    print("   4. git commit updated baselines")
    
    print("\n⚠ Note: Stopped before pushing (as requested)")
    print("   Push when ready: git push origin feature/semantic-regression\n")
    
    # Clean up
    try:
        Path(__file__).unlink()
    except:
        pass

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
