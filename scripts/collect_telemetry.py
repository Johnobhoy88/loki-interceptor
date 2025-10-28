#!/usr/bin/env python3
"""
Telemetry Collection CLI
Aggregates synthesis telemetry from audit log and displays snippet success rates.
Run after gold suite to analyze performance.
"""
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT / 'backend'))

from core.audit_log import AuditLogger


def main():
    """Collect and display synthesis telemetry."""
    audit_logger = AuditLogger()

    # Get telemetry for different time windows
    windows = {
        'Last Hour': (datetime.utcnow() - timedelta(hours=1)).isoformat(),
        'Last 24 Hours': (datetime.utcnow() - timedelta(days=1)).isoformat(),
        'Last 7 Days': (datetime.utcnow() - timedelta(days=7)).isoformat(),
        'All Time': None
    }

    print("=" * 80)
    print("SYNTHESIS TELEMETRY REPORT")
    print("=" * 80)

    for window_name, since in windows.items():
        telemetry = audit_logger.get_synthesis_telemetry(since=since)

        if telemetry['total_operations'] == 0:
            continue

        print(f"\n## {window_name}")
        print(f"Total Operations:     {telemetry['total_operations']}")
        print(f"Success Rate:         {telemetry['success_rate']:.1%}")
        print(f"Avg Iterations:       {telemetry['avg_iterations']:.2f}")
        print(f"Avg Duration:         {telemetry['avg_duration_ms']:.1f}ms")
        print(f"Needs Review Count:   {telemetry['needs_review_count']}")

        # Top 10 most-applied snippets
        if telemetry['snippet_stats']:
            print(f"\n### Top 10 Most Applied Snippets:")
            for i, (snippet_id, stats) in enumerate(list(telemetry['snippet_stats'].items())[:10], 1):
                print(f"  {i}. {snippet_id}: {stats['applied']} applied, {stats['success_rate']:.1%} success")

        # Top 10 unresolved gates
        if telemetry['unresolved_gate_stats']:
            print(f"\n### Top 10 Unresolved Gates:")
            for i, (gate_id, count) in enumerate(list(telemetry['unresolved_gate_stats'].items())[:10], 1):
                print(f"  {i}. {gate_id}: {count} occurrences")

    # Export to JSON
    output_path = ROOT / 'data' / f"telemetry_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    export_data = {window_name: audit_logger.get_synthesis_telemetry(since=since) for window_name, since in windows.items()}

    with open(output_path, 'w') as f:
        json.dump(export_data, f, indent=2)

    print(f"\n📊 Full telemetry exported to: {output_path}")
    print("=" * 80)


if __name__ == '__main__':
    main()
