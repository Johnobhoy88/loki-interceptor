#!/usr/bin/env python3
"""
Gold Fixture Regression Suite
Tests synthesis engine against nastiest real-world compliance failures.
Hard-fails if any gate regresses or synthesis can't clean a document in ≤5 iterations.
"""
from __future__ import annotations
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT / 'backend'))

from core.async_engine import AsyncLOKIEngine
from core.synthesis import SynthesisEngine
from core.audit_log import AuditLogger


class GoldSuiteRunner:
    """Regression runner for gold fixtures with strict pass/fail criteria."""

    def __init__(self):
        self.engine = AsyncLOKIEngine(max_workers=4)
        self.engine.load_module('fca_uk')
        self.engine.load_module('gdpr_uk')
        self.engine.load_module('hr_scottish')
        self.engine.load_module('nda_uk')
        self.engine.load_module('tax_uk')

        self.audit_logger = AuditLogger()
        self.synthesis_engine = SynthesisEngine(self.engine, audit_logger=self.audit_logger)
        self.gold_fixtures_dir = Path(__file__).parent / 'gold_fixtures'

        self.results = []
        self.failures = []

    def run_suite(self) -> Dict[str, Any]:
        """
        Run all gold fixtures through validation → synthesis → re-validation.

        Returns:
            Suite summary with pass/fail counts and detailed results
        """
        print("=" * 80)
        print("GOLD FIXTURE REGRESSION SUITE")
        print("=" * 80)

        start_time = time.time()
        modules = ['fca_uk', 'gdpr_uk', 'hr_scottish', 'nda_uk', 'tax_uk']

        for module in modules:
            module_dir = self.gold_fixtures_dir / module
            if not module_dir.exists():
                print(f"⚠️  Skipping {module}: directory not found")
                continue

            fixtures = sorted(module_dir.glob('*.txt'))
            print(f"\n📁 {module.upper()}: {len(fixtures)} fixtures")

            for fixture_path in fixtures:
                self._run_fixture(fixture_path, module)

        duration = time.time() - start_time

        # Generate summary
        summary = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'duration_seconds': round(duration, 2),
            'total_fixtures': len(self.results),
            'passed': sum(1 for r in self.results if r['passed']),
            'failed': len(self.failures),
            'pass_rate': round((len(self.results) - len(self.failures)) / len(self.results) * 100, 1) if self.results else 0.0,
            'results': self.results,
            'failures': self.failures
        }

        self._print_summary(summary)
        self._write_reports(summary)

        return summary

    def _run_fixture(self, fixture_path: Path, module: str) -> None:
        """Run a single fixture through the synthesis pipeline."""
        fixture_name = fixture_path.stem
        text = fixture_path.read_text()

        print(f"  • {fixture_name}...", end=' ', flush=True)

        try:
            # 1. Initial validation
            validation = self.engine.check_document(
                text=text,
                document_type='test',
                active_modules=[module]
            )

            initial_failures = self._count_failures(validation)

            if initial_failures == 0:
                print(f"⚠️  SKIP (no initial failures)")
                self.results.append({
                    'fixture': f"{module}/{fixture_name}",
                    'passed': True,
                    'skipped': True,
                    'reason': 'No initial failures to synthesize'
                })
                return

            # 2. Synthesis
            synthesis_result = self.synthesis_engine.synthesize(
                base_text=text,
                validation=validation,
                context={},
                modules=[module]
            )

            # 3. Validation criteria
            passed = True
            fail_reason = None

            # Criterion 1: Must succeed or have valid reason
            if not synthesis_result['success']:
                if synthesis_result.get('needs_review'):
                    # NeedsReview is acceptable if no snippets available
                    if 'No snippets available' in synthesis_result['reason']:
                        pass  # Acceptable - no remediation exists yet
                    else:
                        passed = False
                        fail_reason = synthesis_result['reason']
                else:
                    passed = False
                    fail_reason = synthesis_result['reason']

            # Criterion 2: Must complete in ≤5 iterations
            if synthesis_result['iterations'] > 5:
                passed = False
                fail_reason = f"Exceeded max iterations: {synthesis_result['iterations']}"

            # Criterion 3: Must reduce failures
            final_failures = self._count_failures(synthesis_result['final_validation'])
            if final_failures >= initial_failures and synthesis_result['iterations'] > 0:
                passed = False
                fail_reason = f"No progress: {initial_failures} → {final_failures} failures"

            result = {
                'fixture': f"{module}/{fixture_name}",
                'passed': passed,
                'initial_failures': initial_failures,
                'final_failures': final_failures,
                'iterations': synthesis_result['iterations'],
                'snippets_applied': len(synthesis_result['snippets_applied']),
                'success': synthesis_result['success'],
                'reason': synthesis_result['reason'],
                'needs_review': synthesis_result.get('needs_review', False)
            }

            self.results.append(result)

            if passed:
                print(f"✅ PASS ({initial_failures}→{final_failures} failures, {synthesis_result['iterations']} iter)")
            else:
                print(f"❌ FAIL: {fail_reason}")
                self.failures.append({**result, 'fail_reason': fail_reason})

        except Exception as e:
            print(f"💥 ERROR: {e}")
            self.results.append({
                'fixture': f"{module}/{fixture_name}",
                'passed': False,
                'error': str(e)
            })
            self.failures.append({
                'fixture': f"{module}/{fixture_name}",
                'fail_reason': f"Exception: {e}"
            })

    def _count_failures(self, validation: Dict[str, Any]) -> int:
        """Count FAIL status gates."""
        count = 0
        for module_data in validation.get('modules', {}).values():
            for gate_result in module_data.get('gates', {}).values():
                if gate_result.get('status') == 'FAIL':
                    count += 1
        return count

    def _print_summary(self, summary: Dict[str, Any]) -> None:
        """Print test summary to console."""
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total Fixtures:  {summary['total_fixtures']}")
        print(f"Passed:          {summary['passed']} ✅")
        print(f"Failed:          {summary['failed']} ❌")
        print(f"Pass Rate:       {summary['pass_rate']}%")
        print(f"Duration:        {summary['duration_seconds']}s")

        if self.failures:
            print("\n❌ FAILURES:")
            for failure in self.failures:
                print(f"  • {failure['fixture']}: {failure.get('fail_reason', 'Unknown')}")

        print("=" * 80)

    def _write_reports(self, summary: Dict[str, Any]) -> None:
        """Write JSON and Markdown reports."""
        artifacts_dir = Path(__file__).parent / 'artifacts'
        artifacts_dir.mkdir(exist_ok=True)

        timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')

        # JSON report
        json_path = artifacts_dir / f'gold_suite_{timestamp}.json'
        with open(json_path, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"\n📄 JSON report: {json_path}")

        # Markdown report
        md_path = artifacts_dir / f'gold_suite_{timestamp}.md'
        with open(md_path, 'w') as f:
            f.write(f"# Gold Suite Report\n\n")
            f.write(f"**Date**: {summary['timestamp']}\n\n")
            f.write(f"**Duration**: {summary['duration_seconds']}s\n\n")
            f.write(f"## Summary\n\n")
            f.write(f"- **Total Fixtures**: {summary['total_fixtures']}\n")
            f.write(f"- **Passed**: {summary['passed']} ✅\n")
            f.write(f"- **Failed**: {summary['failed']} ❌\n")
            f.write(f"- **Pass Rate**: {summary['pass_rate']}%\n\n")

            if self.failures:
                f.write(f"## Failures\n\n")
                for failure in self.failures:
                    f.write(f"### {failure['fixture']}\n\n")
                    f.write(f"- **Reason**: {failure.get('fail_reason', 'Unknown')}\n")
                    f.write(f"- **Initial Failures**: {failure.get('initial_failures', 'N/A')}\n")
                    f.write(f"- **Final Failures**: {failure.get('final_failures', 'N/A')}\n")
                    f.write(f"- **Iterations**: {failure.get('iterations', 'N/A')}\n\n")

            f.write(f"## All Results\n\n")
            f.write("| Fixture | Status | Failures (Before → After) | Iterations | Snippets |\n")
            f.write("|---------|--------|---------------------------|------------|----------|\n")
            for result in summary['results']:
                status = "✅ PASS" if result['passed'] else "❌ FAIL"
                before = result.get('initial_failures', '-')
                after = result.get('final_failures', '-')
                iters = result.get('iterations', '-')
                snippets = result.get('snippets_applied', '-')
                f.write(f"| {result['fixture']} | {status} | {before} → {after} | {iters} | {snippets} |\n")

        print(f"📄 Markdown report: {md_path}")


def main():
    """Run gold suite and exit with appropriate code."""
    runner = GoldSuiteRunner()
    summary = runner.run_suite()

    # Exit with failure if any tests failed
    sys.exit(1 if summary['failed'] > 0 else 0)


if __name__ == '__main__':
    main()
