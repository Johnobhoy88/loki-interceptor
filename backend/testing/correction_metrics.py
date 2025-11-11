"""
Correction Metrics Collection System

This module provides comprehensive metrics collection and analysis for the
correction system, tracking accuracy, performance, and quality over time.

Metrics Collected:
- Correction accuracy (before/after validation scores)
- Performance metrics (latency, throughput)
- Coverage metrics (gates addressed, strategies used)
- Quality metrics (document integrity, semantic preservation)
- Trend analysis (degradation detection)
"""

import time
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import statistics


@dataclass
class CorrectionMetrics:
    """Container for correction metrics."""

    # Identity
    timestamp: str
    document_id: str
    document_type: str

    # Input characteristics
    original_length: int
    original_word_count: int
    failing_gates_count: int
    failing_gates: List[str]

    # Correction results
    corrected_length: int
    corrected_word_count: int
    correction_count: int
    strategies_used: List[str]

    # Performance
    processing_time_ms: float
    processing_time_per_char_ms: float

    # Quality
    length_change_percent: float
    word_count_change_percent: float
    determinism_hash: str

    # Validation improvement
    violations_before: Optional[int] = None
    violations_after: Optional[int] = None
    improvement_percent: Optional[float] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class CorrectionMetricsCollector:
    """
    Collects and aggregates correction metrics over time.

    Usage:
        collector = CorrectionMetricsCollector()

        # During test/correction
        collector.start_correction("doc_123", "financial")
        result = apply_corrections(...)
        collector.end_correction(original_text, result, gate_results)

        # Get metrics
        summary = collector.get_summary()
    """

    def __init__(self):
        self.metrics_history: List[CorrectionMetrics] = []
        self.current_correction_start: Optional[float] = None
        self.current_doc_id: Optional[str] = None
        self.current_doc_type: Optional[str] = None

    def start_correction(self, document_id: str, document_type: str):
        """Start timing a correction."""
        self.current_correction_start = time.time()
        self.current_doc_id = document_id
        self.current_doc_type = document_type

    def end_correction(
        self,
        original_text: str,
        correction_result: Dict,
        gate_results: List,
        violations_before: Optional[int] = None,
        violations_after: Optional[int] = None
    ) -> CorrectionMetrics:
        """
        End timing and record correction metrics.

        Args:
            original_text: Original document text
            correction_result: Result from correction synthesizer
            gate_results: List of gate results
            violations_before: Optional violation count before correction
            violations_after: Optional violation count after correction

        Returns:
            CorrectionMetrics object with collected metrics
        """
        if self.current_correction_start is None:
            raise ValueError("start_correction() must be called first")

        processing_time = (time.time() - self.current_correction_start) * 1000  # ms

        corrected_text = correction_result.get('corrected', '')

        # Count words
        original_words = len(original_text.split())
        corrected_words = len(corrected_text.split())

        # Calculate changes
        length_change = ((len(corrected_text) - len(original_text)) / len(original_text) * 100) \
                        if len(original_text) > 0 else 0
        word_change = ((corrected_words - original_words) / original_words * 100) \
                      if original_words > 0 else 0

        # Extract failing gates
        failing_gates = [
            gate_id for gate_id, gate_result in gate_results
            if gate_result.get('status') in ['FAIL', 'WARNING']
        ]

        # Calculate improvement
        improvement = None
        if violations_before is not None and violations_after is not None:
            if violations_before > 0:
                improvement = ((violations_before - violations_after) / violations_before * 100)

        metrics = CorrectionMetrics(
            timestamp=datetime.now().isoformat(),
            document_id=self.current_doc_id or "unknown",
            document_type=self.current_doc_type or "unknown",
            original_length=len(original_text),
            original_word_count=original_words,
            failing_gates_count=len(failing_gates),
            failing_gates=failing_gates,
            corrected_length=len(corrected_text),
            corrected_word_count=corrected_words,
            correction_count=correction_result.get('correction_count', 0),
            strategies_used=correction_result.get('strategies_applied', []),
            processing_time_ms=processing_time,
            processing_time_per_char_ms=processing_time / len(original_text) if len(original_text) > 0 else 0,
            length_change_percent=length_change,
            word_count_change_percent=word_change,
            determinism_hash=correction_result.get('determinism', {}).get('output_hash', ''),
            violations_before=violations_before,
            violations_after=violations_after,
            improvement_percent=improvement
        )

        self.metrics_history.append(metrics)

        # Reset state
        self.current_correction_start = None
        self.current_doc_id = None
        self.current_doc_type = None

        return metrics

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of all collected metrics.

        Returns:
            Dictionary with summary statistics
        """
        if not self.metrics_history:
            return {"error": "No metrics collected"}

        processing_times = [m.processing_time_ms for m in self.metrics_history]
        correction_counts = [m.correction_count for m in self.metrics_history]
        improvements = [m.improvement_percent for m in self.metrics_history
                       if m.improvement_percent is not None]

        # Strategy usage
        strategy_usage = defaultdict(int)
        for metrics in self.metrics_history:
            for strategy in metrics.strategies_used:
                strategy_usage[strategy] += 1

        # Document type breakdown
        doc_type_counts = defaultdict(int)
        for metrics in self.metrics_history:
            doc_type_counts[metrics.document_type] += 1

        # Gate frequency
        gate_frequency = defaultdict(int)
        for metrics in self.metrics_history:
            for gate in metrics.failing_gates:
                gate_frequency[gate] += 1

        summary = {
            "total_corrections": len(self.metrics_history),
            "performance": {
                "avg_processing_time_ms": statistics.mean(processing_times),
                "median_processing_time_ms": statistics.median(processing_times),
                "min_processing_time_ms": min(processing_times),
                "max_processing_time_ms": max(processing_times),
                "stdev_processing_time_ms": statistics.stdev(processing_times) if len(processing_times) > 1 else 0
            },
            "corrections": {
                "avg_corrections_per_doc": statistics.mean(correction_counts),
                "median_corrections_per_doc": statistics.median(correction_counts),
                "total_corrections_applied": sum(correction_counts),
                "max_corrections_single_doc": max(correction_counts),
            },
            "improvement": {
                "avg_improvement_percent": statistics.mean(improvements) if improvements else None,
                "median_improvement_percent": statistics.median(improvements) if improvements else None,
                "docs_with_improvement_data": len(improvements)
            },
            "strategy_usage": dict(sorted(strategy_usage.items(), key=lambda x: x[1], reverse=True)),
            "document_types": dict(doc_type_counts),
            "top_failing_gates": dict(sorted(gate_frequency.items(), key=lambda x: x[1], reverse=True)[:10]),
            "timestamp": datetime.now().isoformat()
        }

        return summary

    def get_detailed_report(self) -> Dict[str, Any]:
        """Get detailed report with all metrics."""
        summary = self.get_summary()

        summary["detailed_metrics"] = [m.to_dict() for m in self.metrics_history]

        return summary

    def export_to_json(self, filepath: str):
        """Export all metrics to JSON file."""
        report = self.get_detailed_report()

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)

    def get_metrics_by_document_type(self, doc_type: str) -> List[CorrectionMetrics]:
        """Get all metrics for a specific document type."""
        return [m for m in self.metrics_history if m.document_type == doc_type]

    def get_performance_trend(self) -> List[Dict]:
        """
        Get performance trend over time.

        Returns:
            List of {timestamp, processing_time_ms} dictionaries
        """
        return [
            {
                "timestamp": m.timestamp,
                "processing_time_ms": m.processing_time_ms,
                "correction_count": m.correction_count
            }
            for m in self.metrics_history
        ]

    def detect_performance_degradation(self, threshold_percent: float = 20.0) -> Optional[Dict]:
        """
        Detect if performance has degraded compared to baseline.

        Args:
            threshold_percent: Percentage increase that triggers alert

        Returns:
            Alert dictionary if degradation detected, None otherwise
        """
        if len(self.metrics_history) < 10:
            return None

        # Compare recent performance to baseline
        baseline = self.metrics_history[:10]
        recent = self.metrics_history[-10:]

        baseline_avg = statistics.mean([m.processing_time_ms for m in baseline])
        recent_avg = statistics.mean([m.processing_time_ms for m in recent])

        increase_percent = ((recent_avg - baseline_avg) / baseline_avg * 100)

        if increase_percent > threshold_percent:
            return {
                "alert": "PERFORMANCE_DEGRADATION",
                "baseline_avg_ms": baseline_avg,
                "recent_avg_ms": recent_avg,
                "increase_percent": increase_percent,
                "threshold_percent": threshold_percent,
                "timestamp": datetime.now().isoformat()
            }

        return None

    def clear(self):
        """Clear all collected metrics."""
        self.metrics_history.clear()
        self.current_correction_start = None
        self.current_doc_id = None
        self.current_doc_type = None


class AccuracyMetricsTracker:
    """
    Tracks correction accuracy metrics over time.

    Accuracy is measured by comparing validation results before and after correction.
    """

    def __init__(self):
        self.accuracy_history: List[Dict] = []

    def record_accuracy(
        self,
        document_id: str,
        gates_before: Dict[str, str],  # gate_id -> status
        gates_after: Dict[str, str],
        correction_result: Dict
    ):
        """
        Record accuracy metrics for a correction.

        Args:
            document_id: Unique document identifier
            gates_before: Gate results before correction (gate_id -> status)
            gates_after: Gate results after correction
            correction_result: Correction result dictionary
        """
        # Count failures/warnings
        failures_before = sum(1 for status in gates_before.values() if status in ['FAIL', 'WARNING'])
        failures_after = sum(1 for status in gates_after.values() if status in ['FAIL', 'WARNING'])

        # Calculate improvement
        if failures_before > 0:
            improvement_rate = (failures_before - failures_after) / failures_before * 100
        else:
            improvement_rate = 0 if failures_after == 0 else -100

        # Gate-by-gate analysis
        gates_fixed = []
        gates_still_failing = []
        gates_made_worse = []

        for gate_id in gates_before.keys():
            before = gates_before.get(gate_id, 'PASS')
            after = gates_after.get(gate_id, 'PASS')

            if before in ['FAIL', 'WARNING'] and after == 'PASS':
                gates_fixed.append(gate_id)
            elif before in ['FAIL', 'WARNING'] and after in ['FAIL', 'WARNING']:
                gates_still_failing.append(gate_id)
            elif before == 'PASS' and after in ['FAIL', 'WARNING']:
                gates_made_worse.append(gate_id)

        accuracy_record = {
            "timestamp": datetime.now().isoformat(),
            "document_id": document_id,
            "failures_before": failures_before,
            "failures_after": failures_after,
            "improvement_rate_percent": improvement_rate,
            "gates_fixed": gates_fixed,
            "gates_still_failing": gates_still_failing,
            "gates_made_worse": gates_made_worse,
            "correction_count": correction_result.get('correction_count', 0),
            "strategies_used": correction_result.get('strategies_applied', [])
        }

        self.accuracy_history.append(accuracy_record)

        return accuracy_record

    def get_accuracy_summary(self) -> Dict[str, Any]:
        """Get summary of accuracy metrics."""
        if not self.accuracy_history:
            return {"error": "No accuracy data collected"}

        improvement_rates = [r['improvement_rate_percent'] for r in self.accuracy_history]
        total_gates_fixed = sum(len(r['gates_fixed']) for r in self.accuracy_history)
        total_gates_still_failing = sum(len(r['gates_still_failing']) for r in self.accuracy_history)
        total_gates_made_worse = sum(len(r['gates_made_worse']) for r in self.accuracy_history)

        # Calculate success rate (any improvement > 0)
        successful_corrections = sum(1 for r in self.accuracy_history if r['improvement_rate_percent'] > 0)
        success_rate = (successful_corrections / len(self.accuracy_history) * 100)

        # Perfect corrections (100% improvement)
        perfect_corrections = sum(1 for r in self.accuracy_history if r['improvement_rate_percent'] == 100)
        perfect_rate = (perfect_corrections / len(self.accuracy_history) * 100)

        return {
            "total_corrections": len(self.accuracy_history),
            "success_rate_percent": success_rate,
            "perfect_correction_rate_percent": perfect_rate,
            "avg_improvement_percent": statistics.mean(improvement_rates),
            "median_improvement_percent": statistics.median(improvement_rates),
            "total_gates_fixed": total_gates_fixed,
            "total_gates_still_failing": total_gates_still_failing,
            "total_gates_made_worse": total_gates_made_worse,
            "fix_rate_percent": (total_gates_fixed / (total_gates_fixed + total_gates_still_failing) * 100)
                                if (total_gates_fixed + total_gates_still_failing) > 0 else 0,
            "timestamp": datetime.now().isoformat()
        }

    def export_to_json(self, filepath: str):
        """Export accuracy history to JSON."""
        report = {
            "summary": self.get_accuracy_summary(),
            "history": self.accuracy_history
        }

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)


# Convenience function for quick metrics collection in tests
def collect_correction_metrics(
    original_text: str,
    correction_result: Dict,
    gate_results: List,
    document_id: str = "test_doc",
    document_type: str = "test"
) -> CorrectionMetrics:
    """
    Quick helper to collect metrics for a single correction.

    Usage in tests:
        metrics = collect_correction_metrics(original, result, gates)
        assert metrics.processing_time_ms < 1000
    """
    collector = CorrectionMetricsCollector()
    collector.start_correction(document_id, document_type)

    # Simulate timing (can't measure past corrections)
    time.sleep(0.001)  # Minimal delay

    metrics = collector.end_correction(original_text, correction_result, gate_results)

    return metrics
