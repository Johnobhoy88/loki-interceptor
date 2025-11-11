#!/usr/bin/env python3
"""
Test Runner Script for LOKI Platform

This script provides a convenient way to run various test suites
with proper configuration and reporting.
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
import json
import argparse


class TestRunner:
    """Orchestrate test execution."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.tests_dir = project_root / "tests"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.report_dir = project_root / "test_reports" / self.timestamp
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def load_test_config(self):
        """Load test configuration from environment."""
        return {
            "backend_url": os.getenv("BACKEND_URL", "http://localhost:5002"),
            "frontend_url": os.getenv("FRONTEND_URL", "http://localhost:80"),
            "database_url": os.getenv(
                "TEST_DATABASE_URL",
                "postgresql://loki:testpass@localhost:5433/loki_test"
            ),
            "redis_url": os.getenv(
                "TEST_REDIS_URL",
                "redis://:testpass@localhost:6380/0"
            ),
            "timeout": int(os.getenv("API_TIMEOUT", "30")),
        }

    def run_smoke_tests(self, verbose=True):
        """Run smoke test suite."""
        print("\n" + "="*70)
        print("RUNNING SMOKE TESTS")
        print("="*70)

        cmd = [
            "pytest",
            str(self.tests_dir / "smoke"),
            "-v" if verbose else "",
            "--tb=short",
            "--timeout=30",
            f"--html={self.report_dir}/smoke_report.html",
            "--self-contained-html",
        ]

        return self._run_command(cmd, "smoke_tests.log")

    def run_e2e_tests(self, verbose=True):
        """Run E2E test suite."""
        print("\n" + "="*70)
        print("RUNNING E2E TESTS")
        print("="*70)

        cmd = [
            "pytest",
            str(self.tests_dir / "e2e"),
            "-v" if verbose else "",
            "--tb=short",
            "--timeout=60",
            f"--html={self.report_dir}/e2e_report.html",
            "--self-contained-html",
        ]

        return self._run_command(cmd, "e2e_tests.log")

    def run_integration_tests(self, verbose=True):
        """Run integration test suite."""
        print("\n" + "="*70)
        print("RUNNING INTEGRATION TESTS")
        print("="*70)

        cmd = [
            "pytest",
            str(self.tests_dir / "integration"),
            "-v" if verbose else "",
            "--tb=short",
            "--timeout=60",
            f"--html={self.report_dir}/integration_report.html",
            "--self-contained-html",
        ]

        return self._run_command(cmd, "integration_tests.log")

    def run_chaos_tests(self, verbose=True):
        """Run chaos engineering test suite."""
        print("\n" + "="*70)
        print("RUNNING CHAOS ENGINEERING TESTS")
        print("="*70)

        cmd = [
            "pytest",
            str(self.tests_dir / "chaos"),
            "-v" if verbose else "",
            "--tb=short",
            "--timeout=120",
            f"--html={self.report_dir}/chaos_report.html",
            "--self-contained-html",
        ]

        return self._run_command(cmd, "chaos_tests.log")

    def run_all_tests(self, verbose=True, coverage=True):
        """Run all test suites."""
        print("\n" + "="*70)
        print("RUNNING FULL TEST SUITE")
        print("="*70)

        cmd = [
            "pytest",
            str(self.tests_dir),
            "-v" if verbose else "",
            "--tb=short",
            "--timeout=300",
        ]

        if coverage:
            cmd.extend([
                "--cov=backend",
                f"--cov-report=html:{self.report_dir}/coverage",
                "--cov-report=term-missing",
                "--cov-report=xml",
            ])

        cmd.extend([
            f"--html={self.report_dir}/full_report.html",
            "--self-contained-html",
            f"--junit-xml={self.report_dir}/junit.xml",
        ])

        return self._run_command(cmd, "full_tests.log")

    def _run_command(self, cmd, log_file):
        """Execute command and capture output."""
        cmd = [arg for arg in cmd if arg]  # Remove empty strings

        log_path = self.report_dir / log_file
        print(f"\nCommand: {' '.join(cmd)}")
        print(f"Log file: {log_path}")

        with open(log_path, "w") as f:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            f.write(result.stdout)
            print(result.stdout)

        return result.returncode == 0

    def generate_summary(self, results):
        """Generate test execution summary."""
        summary = {
            "timestamp": self.timestamp,
            "results": results,
            "report_dir": str(self.report_dir),
        }

        summary_file = self.report_dir / "summary.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        print("\n" + "="*70)
        print("TEST EXECUTION SUMMARY")
        print("="*70)
        print(f"Timestamp: {self.timestamp}")
        for test_type, success in results.items():
            status = "PASSED" if success else "FAILED"
            print(f"{test_type:20s}: {status}")
        print(f"\nReport directory: {self.report_dir}")
        print(f"Summary: {summary_file}")

    def print_help(self):
        """Print available commands."""
        print("""
Usage: python scripts/run_tests.py [COMMAND] [OPTIONS]

Commands:
  smoke              Run smoke test suite (quick validation)
  e2e                Run E2E test suite (user workflows)
  integration        Run integration test suite (component interaction)
  chaos              Run chaos engineering tests (resilience)
  all                Run all test suites (default)
  deploy-check       Run smoke + critical integration tests (pre-deployment)

Options:
  --verbose, -v      Verbose output
  --coverage, -c     Include coverage report (requires coverage tools)
  --no-coverage      Skip coverage report
  --help, -h         Show this help message

Examples:
  python scripts/run_tests.py smoke
  python scripts/run_tests.py all --coverage
  python scripts/run_tests.py deploy-check
        """)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="LOKI Platform Test Runner",
        add_help=False
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="all",
        choices=["smoke", "e2e", "integration", "chaos", "all", "deploy-check"]
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        default=True,
        help="Include coverage report"
    )
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Skip coverage report"
    )
    parser.add_argument(
        "--help", "-h",
        action="store_true",
        help="Show help message"
    )

    args = parser.parse_args()

    if args.help:
        runner = TestRunner(Path.cwd())
        runner.print_help()
        return 0

    project_root = Path(__file__).parent.parent
    runner = TestRunner(project_root)

    results = {}

    try:
        if args.command == "smoke" or args.command == "deploy-check":
            results["smoke"] = runner.run_smoke_tests(args.verbose)
            if args.command == "deploy-check":
                # Also run critical integration tests
                results["integration_critical"] = runner.run_integration_tests(args.verbose)

        elif args.command == "e2e":
            results["e2e"] = runner.run_e2e_tests(args.verbose)

        elif args.command == "integration":
            results["integration"] = runner.run_integration_tests(args.verbose)

        elif args.command == "chaos":
            results["chaos"] = runner.run_chaos_tests(args.verbose)

        elif args.command == "all":
            results["smoke"] = runner.run_smoke_tests(args.verbose)
            results["e2e"] = runner.run_e2e_tests(args.verbose)
            results["integration"] = runner.run_integration_tests(args.verbose)
            results["chaos"] = runner.run_chaos_tests(args.verbose)

        runner.generate_summary(results)

        # Exit with failure if any test suite failed
        if not all(results.values()):
            return 1

        return 0

    except Exception as e:
        print(f"\nError running tests: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
