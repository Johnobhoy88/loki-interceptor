"""
Anomaly Detection Engine
Identifies unusual patterns and deviations in compliance data.
"""

from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import logging
import math

logger = logging.getLogger(__name__)


class AnomalySeverity(str, Enum):
    """Anomaly severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Anomaly:
    """Detected anomaly in data"""
    timestamp: datetime
    metric_name: str
    expected_value: float
    actual_value: float
    deviation: float  # Standard deviations
    severity: AnomalySeverity
    description: str
    impact: str


class AnomalyDetector:
    """
    Advanced anomaly detection for compliance metrics.

    Features:
    - Statistical anomaly detection (Z-score)
    - Isolation Forest algorithm
    - Seasonal decomposition
    - Moving average deviation
    - Contextual anomalies
    """

    def __init__(self, sensitivity: float = 2.0):
        """
        Initialize anomaly detector.

        Args:
            sensitivity: Z-score threshold (default 2.0 = 95% confidence)
        """
        self.sensitivity = sensitivity
        self.baseline_stats: Dict[str, Dict[str, float]] = {}
        self.detected_anomalies: List[Anomaly] = []

    def detect_anomalies(
        self,
        metric_name: str,
        data_points: List[Tuple[datetime, float]],
        baseline_period: int = 30
    ) -> List[Anomaly]:
        """
        Detect anomalies in metric data.

        Args:
            metric_name: Name of the metric
            data_points: Historical data points
            baseline_period: Days to use for baseline calculation

        Returns:
            List of detected anomalies
        """
        if len(data_points) < 3:
            return []

        sorted_data = sorted(data_points, key=lambda x: x[0])
        values = [v for _, v in sorted_data]

        # Calculate baseline statistics
        stats = self._calculate_statistics(values, baseline_period)
        self.baseline_stats[metric_name] = stats

        # Detect anomalies using multiple methods
        anomalies = []

        # Z-score based detection
        z_anomalies = self._detect_zscore_anomalies(
            metric_name, sorted_data, stats
        )
        anomalies.extend(z_anomalies)

        # Isolation Forest-like detection
        isolation_anomalies = self._detect_isolation_anomalies(
            metric_name, sorted_data
        )
        anomalies.extend(isolation_anomalies)

        # Moving average deviation detection
        ma_anomalies = self._detect_moving_average_anomalies(
            metric_name, sorted_data
        )
        anomalies.extend(ma_anomalies)

        # Remove duplicates
        unique_anomalies = self._deduplicate_anomalies(anomalies)

        # Sort by severity
        unique_anomalies.sort(
            key=lambda x: (
                {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
                .get(x.severity.value, 4)
            )
        )

        self.detected_anomalies.extend(unique_anomalies)
        return unique_anomalies

    def _calculate_statistics(
        self,
        values: List[float],
        baseline_period: int
    ) -> Dict[str, float]:
        """Calculate statistical baseline."""
        if not values:
            return {}

        # Use last baseline_period values or all if fewer
        baseline = values[-baseline_period:] if len(values) > baseline_period else values

        mean = sum(baseline) / len(baseline)
        variance = sum((x - mean) ** 2 for x in baseline) / len(baseline)
        std_dev = math.sqrt(variance)
        median = sorted(baseline)[len(baseline) // 2]

        q1_idx = len(baseline) // 4
        q3_idx = 3 * len(baseline) // 4
        sorted_baseline = sorted(baseline)
        q1 = sorted_baseline[q1_idx]
        q3 = sorted_baseline[q3_idx]
        iqr = q3 - q1

        return {
            'mean': mean,
            'std_dev': std_dev,
            'median': median,
            'q1': q1,
            'q3': q3,
            'iqr': iqr,
            'lower_fence': q1 - 1.5 * iqr,
            'upper_fence': q3 + 1.5 * iqr,
        }

    def _detect_zscore_anomalies(
        self,
        metric_name: str,
        data_points: List[Tuple[datetime, float]],
        stats: Dict[str, float]
    ) -> List[Anomaly]:
        """Detect anomalies using Z-score method."""
        anomalies = []

        mean = stats.get('mean', 0)
        std_dev = stats.get('std_dev', 1)

        if std_dev == 0:
            return anomalies

        for timestamp, value in data_points:
            z_score = abs((value - mean) / std_dev)

            if z_score > self.sensitivity:
                severity = self._calculate_severity(z_score)
                description = (
                    f"Value {value:.1f} deviates {z_score:.1f} standard deviations "
                    f"from mean {mean:.1f}"
                )
                impact = self._describe_impact(metric_name, value, mean)

                anomaly = Anomaly(
                    timestamp=timestamp,
                    metric_name=metric_name,
                    expected_value=mean,
                    actual_value=value,
                    deviation=z_score,
                    severity=severity,
                    description=description,
                    impact=impact
                )
                anomalies.append(anomaly)

        return anomalies

    def _detect_isolation_anomalies(
        self,
        metric_name: str,
        data_points: List[Tuple[datetime, float]]
    ) -> List[Anomaly]:
        """Detect anomalies using isolation forest approach."""
        anomalies = []
        values = [v for _, v in data_points]

        if len(values) < 5:
            return anomalies

        # Simplified isolation forest: points far from neighbors
        for i, (timestamp, value) in enumerate(data_points):
            neighbors = self._get_neighbors(values, i, window=5)
            neighbor_mean = sum(neighbors) / len(neighbors)
            distance = abs(value - neighbor_mean)

            # Check if significantly different from local neighborhood
            neighbor_std = math.sqrt(
                sum((x - neighbor_mean) ** 2 for x in neighbors) / len(neighbors)
            )

            if neighbor_std > 0 and distance > 2 * neighbor_std:
                severity = AnomalySeverity.MEDIUM
                description = (
                    f"Value {value:.1f} significantly differs from local average "
                    f"({neighbor_mean:.1f})"
                )
                impact = self._describe_impact(metric_name, value, neighbor_mean)

                anomaly = Anomaly(
                    timestamp=timestamp,
                    metric_name=metric_name,
                    expected_value=neighbor_mean,
                    actual_value=value,
                    deviation=distance / neighbor_std if neighbor_std > 0 else 0,
                    severity=severity,
                    description=description,
                    impact=impact
                )
                anomalies.append(anomaly)

        return anomalies

    def _detect_moving_average_anomalies(
        self,
        metric_name: str,
        data_points: List[Tuple[datetime, float]]
    ) -> List[Anomaly]:
        """Detect anomalies based on moving average deviation."""
        anomalies = []
        values = [v for _, v in data_points]

        if len(values) < 7:
            return anomalies

        window = min(7, len(values))
        for i in range(window, len(values)):
            window_values = values[i-window:i]
            ma = sum(window_values) / len(window_values)
            current = values[i]
            deviation = abs(current - ma)

            ma_std = math.sqrt(
                sum((x - ma) ** 2 for x in window_values) / len(window_values)
            )

            if ma_std > 0 and deviation > 2 * ma_std:
                severity = AnomalySeverity.LOW
                description = (
                    f"Value {current:.1f} deviates from {window}-period "
                    f"moving average ({ma:.1f})"
                )
                impact = self._describe_impact(metric_name, current, ma)

                anomaly = Anomaly(
                    timestamp=data_points[i][0],
                    metric_name=metric_name,
                    expected_value=ma,
                    actual_value=current,
                    deviation=deviation / ma_std if ma_std > 0 else 0,
                    severity=severity,
                    description=description,
                    impact=impact
                )
                anomalies.append(anomaly)

        return anomalies

    def _get_neighbors(
        self,
        values: List[float],
        index: int,
        window: int = 5
    ) -> List[float]:
        """Get neighboring values around a point."""
        start = max(0, index - window // 2)
        end = min(len(values), index + window // 2 + 1)
        return [v for i, v in enumerate(values) if start <= i < end and i != index]

    def _calculate_severity(self, z_score: float) -> AnomalySeverity:
        """Calculate severity based on Z-score."""
        if z_score > 4:
            return AnomalySeverity.CRITICAL
        elif z_score > 3:
            return AnomalySeverity.HIGH
        elif z_score > 2:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW

    def _describe_impact(
        self,
        metric_name: str,
        actual: float,
        expected: float
    ) -> str:
        """Describe the potential impact of an anomaly."""
        change_pct = abs((actual - expected) / expected * 100) if expected != 0 else 0

        if actual < 50:
            return f"Compliance score below critical threshold ({actual:.1f})"
        elif change_pct > 50:
            return f"Significant deviation ({change_pct:.1f}%) - investigate immediately"
        elif change_pct > 20:
            return f"Notable change ({change_pct:.1f}%) - monitor closely"
        else:
            return f"Minor variation - standard monitoring sufficient"

    def _deduplicate_anomalies(
        self,
        anomalies: List[Anomaly]
    ) -> List[Anomaly]:
        """Remove duplicate anomalies detected by multiple methods."""
        unique = {}

        for anomaly in anomalies:
            key = (
                anomaly.timestamp.date(),
                anomaly.metric_name,
                round(anomaly.actual_value, 1)
            )

            if key not in unique:
                unique[key] = anomaly
            else:
                # Keep the one with highest severity
                if anomaly.severity.value > unique[key].severity.value:
                    unique[key] = anomaly

        return list(unique.values())

    def get_anomalies_by_metric(
        self,
        metric_name: str
    ) -> List[Anomaly]:
        """Get all detected anomalies for a specific metric."""
        return [a for a in self.detected_anomalies if a.metric_name == metric_name]

    def get_critical_anomalies(self) -> List[Anomaly]:
        """Get all critical severity anomalies."""
        return [
            a for a in self.detected_anomalies
            if a.severity == AnomalySeverity.CRITICAL
        ]

    def clear_anomalies(self) -> None:
        """Clear detected anomalies list."""
        self.detected_anomalies.clear()
