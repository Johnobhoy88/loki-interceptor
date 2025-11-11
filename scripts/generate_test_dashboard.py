#!/usr/bin/env python3
"""
Test Reporting Dashboard Generator

Generates an interactive HTML dashboard for test results and coverage reports.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import xml.etree.ElementTree as ET


class TestDashboardGenerator:
    """Generate test reporting dashboard."""

    def __init__(self, report_dir: Path):
        self.report_dir = Path(report_dir)
        self.test_results = self._load_test_results()
        self.coverage_data = self._load_coverage_data()

    def _load_test_results(self) -> Dict[str, Any]:
        """Load test results from JUnit XML."""
        junit_file = self.report_dir / "junit.xml"
        if not junit_file.exists():
            return {}

        try:
            tree = ET.parse(junit_file)
            root = tree.getroot()

            results = {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "duration": 0.0,
                "suites": [],
            }

            for testsuite in root.findall("testsuite"):
                suite_name = testsuite.get("name", "Unknown")
                tests = int(testsuite.get("tests", 0))
                failures = int(testsuite.get("failures", 0))
                skipped = int(testsuite.get("skipped", 0))
                duration = float(testsuite.get("time", 0))

                results["total"] += tests
                results["failed"] += failures
                results["skipped"] += skipped
                results["duration"] += duration
                results["passed"] += tests - failures - skipped

                results["suites"].append({
                    "name": suite_name,
                    "tests": tests,
                    "passed": tests - failures - skipped,
                    "failed": failures,
                    "skipped": skipped,
                    "duration": duration,
                })

            return results
        except Exception as e:
            print(f"Error loading test results: {str(e)}")
            return {}

    def _load_coverage_data(self) -> Dict[str, Any]:
        """Load coverage data."""
        coverage_file = self.report_dir / ".coverage"
        if not coverage_file.exists():
            return {"coverage": "N/A", "files": []}

        return {"coverage": "See coverage/index.html", "files": []}

    def generate_dashboard(self) -> str:
        """Generate HTML dashboard."""
        html = self._create_html_structure()
        return html

    def _create_html_structure(self) -> str:
        """Create HTML dashboard structure."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        results = self.test_results

        passed_pct = (
            (results.get("passed", 0) / results.get("total", 1) * 100)
            if results.get("total", 0) > 0
            else 0
        )

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LOKI Test Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        header {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}

        h1 {{
            color: #333;
            margin-bottom: 10px;
        }}

        .timestamp {{
            color: #666;
            font-size: 14px;
        }}

        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .metric-card {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        .metric-label {{
            color: #666;
            font-size: 14px;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .metric-value {{
            font-size: 32px;
            font-weight: bold;
            color: #333;
        }}

        .metric-value.pass {{
            color: #10b981;
        }}

        .metric-value.fail {{
            color: #ef4444;
        }}

        .metric-value.skip {{
            color: #f59e0b;
        }}

        .progress-bar {{
            background: #e5e7eb;
            height: 8px;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 15px;
        }}

        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #10b981 0%, #34d399 100%);
            width: {passed_pct}%;
            transition: width 0.3s ease;
        }}

        .progress-text {{
            font-size: 12px;
            color: #666;
            margin-top: 8px;
        }}

        .test-suites {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }}

        .suite-header {{
            padding: 20px;
            background: #f9fafb;
            border-bottom: 1px solid #e5e7eb;
            font-weight: 600;
            color: #333;
        }}

        .suite {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 20px;
            border-bottom: 1px solid #e5e7eb;
        }}

        .suite:last-child {{
            border-bottom: none;
        }}

        .suite-name {{
            color: #333;
            font-weight: 500;
        }}

        .suite-stats {{
            display: flex;
            gap: 20px;
            font-size: 14px;
        }}

        .stat {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}

        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }}

        .badge.pass {{
            background: #d1fae5;
            color: #065f46;
        }}

        .badge.fail {{
            background: #fee2e2;
            color: #7f1d1d;
        }}

        .badge.skip {{
            background: #fef3c7;
            color: #92400e;
        }}

        footer {{
            text-align: center;
            color: white;
            padding: 20px;
            margin-top: 40px;
            font-size: 14px;
        }}

        .links {{
            margin-top: 30px;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }}

        .link {{
            display: inline-block;
            padding: 10px 15px;
            background: white;
            color: #667eea;
            text-decoration: none;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.2s ease;
        }}

        .link:hover {{
            background: #f0f0f0;
            transform: translateY(-2px);
        }}

        @media (max-width: 768px) {{
            .metrics {{
                grid-template-columns: 1fr;
            }}

            .suite-stats {{
                flex-direction: column;
                gap: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>LOKI Compliance Platform - Test Dashboard</h1>
            <p class="timestamp">Generated: {timestamp}</p>
        </header>

        <div class="metrics">
            <div class="metric-card">
                <div class="metric-label">Total Tests</div>
                <div class="metric-value">{results.get("total", 0)}</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Passed</div>
                <div class="metric-value pass">{results.get("passed", 0)}</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {passed_pct}%"></div>
                </div>
                <div class="progress-text">{passed_pct:.1f}% success rate</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Failed</div>
                <div class="metric-value fail">{results.get("failed", 0)}</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Skipped</div>
                <div class="metric-value skip">{results.get("skipped", 0)}</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Duration</div>
                <div class="metric-value">{results.get("duration", 0):.1f}s</div>
            </div>
        </div>

        <div class="test-suites">
            <div class="suite-header">Test Suites</div>
            {self._render_suites(results.get("suites", []))}
        </div>

        <div class="links">
            <a href="full_report.html" class="link" target="_blank">Full Test Report</a>
            <a href="coverage/index.html" class="link" target="_blank">Coverage Report</a>
            <a href="junit.xml" class="link" target="_blank">JUnit XML</a>
            <a href="summary.json" class="link" target="_blank">Summary JSON</a>
        </div>

        <footer>
            <p>LOKI Compliance Platform - Automated Test Suite</p>
        </footer>
    </div>
</body>
</html>
        """
        return html

    def _render_suites(self, suites: List[Dict[str, Any]]) -> str:
        """Render test suite results."""
        html = ""
        for suite in suites:
            html += f"""
            <div class="suite">
                <div class="suite-name">{suite["name"]}</div>
                <div class="suite-stats">
                    <div class="stat">
                        <span class="badge pass">{suite["passed"]} passed</span>
                    </div>
                    <div class="stat">
                        <span class="badge fail">{suite["failed"]} failed</span>
                    </div>
                    <div class="stat">
                        <span class="badge skip">{suite["skipped"]} skipped</span>
                    </div>
                    <div class="stat">
                        <span>{suite["duration"]:.2f}s</span>
                    </div>
                </div>
            </div>
            """
        return html

    def save_dashboard(self, output_file: Path):
        """Save dashboard to HTML file."""
        html = self.generate_dashboard()
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            f.write(html)
        print(f"Dashboard saved to: {output_file}")


def main():
    """Main entry point."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python generate_test_dashboard.py <report_directory>")
        sys.exit(1)

    report_dir = Path(sys.argv[1])
    if not report_dir.exists():
        print(f"Error: Report directory not found: {report_dir}")
        sys.exit(1)

    generator = TestDashboardGenerator(report_dir)
    output_file = report_dir / "dashboard.html"
    generator.save_dashboard(output_file)

    print(f"\nDashboard generated successfully!")
    print(f"Open in browser: file://{output_file.absolute()}")


if __name__ == "__main__":
    main()
