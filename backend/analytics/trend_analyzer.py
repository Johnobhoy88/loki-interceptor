"""
Trend Analysis Engine
Analyzes historical compliance data to identify patterns, trends, and insights.
"""

from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging
import statistics

logger = logging.getLogger(__name__)


class TrendDirection(str, Enum):
    """Trend direction indicators"""
    IMPROVING = "improving"
    DECLINING = "declining"
    STABLE = "stable"
    VOLATILE = "volatile"


class TrendSeverity(str, Enum):
    """Trend severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class TrendPoint:
    """Single data point in a trend"""
    timestamp: datetime
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrendAnalysis:
    """Complete trend analysis result"""
    name: str
    data_points: List[TrendPoint]
    direction: TrendDirection
    severity: TrendSeverity
    slope: float  # Rate of change
    r_squared: float  # Goodness of fit
    predictions: List[Tuple[datetime, float]]  # Future predictions
    volatility: float
    moving_average: List[float]
    insights: List[str]
    recommendations: List[str]


class TrendAnalyzer:
    """
    Advanced trend analysis engine for compliance data.

    Features:
    - Historical trend detection
    - Linear regression analysis
    - Moving average calculations
    - Volatility measurement
    - Predictive trend projections
    - Anomaly-based insights
    """

    def __init__(self, window_size: int = 30):
        """
        Initialize trend analyzer.

        Args:
            window_size: Default window size for analysis (days)
        """
        self.window_size = window_size
        self.trends_cache: Dict[str, TrendAnalysis] = {}

    def analyze_trend(
        self,
        name: str,
        data_points: List[Tuple[datetime, float]],
        window_days: Optional[int] = None
    ) -> TrendAnalysis:
        """
        Analyze trend for a given metric.

        Args:
            name: Metric name
            data_points: List of (timestamp, value) tuples
            window_days: Optional custom window size

        Returns:
            TrendAnalysis with detailed insights
        """
        window = window_days or self.window_size
        sorted_points = sorted(data_points, key=lambda x: x[0])

        if len(sorted_points) < 2:
            return self._create_empty_analysis(name)

        # Filter to window
        cutoff = datetime.now() - timedelta(days=window)
        filtered_points = [
            p for p in sorted_points if p[0] >= cutoff
        ]

        if not filtered_points:
            filtered_points = sorted_points[-30:]

        # Calculate trend metrics
        trend_points = [
            TrendPoint(timestamp=p[0], value=p[1])
            for p in filtered_points
        ]

        values = [p[1] for p in filtered_points]
        slope = self._calculate_slope(filtered_points)
        direction = self._determine_direction(slope, values)
        severity = self._assess_severity(values, direction)
        volatility = self._calculate_volatility(values)
        moving_avg = self._calculate_moving_average(values, window=7)
        r_squared = self._calculate_r_squared(filtered_points)

        predictions = self._generate_predictions(
            filtered_points, periods=7
        )

        insights = self._generate_insights(
            name, values, slope, direction, volatility
        )
        recommendations = self._generate_recommendations(
            direction, severity, insights
        )

        analysis = TrendAnalysis(
            name=name,
            data_points=trend_points,
            direction=direction,
            severity=severity,
            slope=slope,
            r_squared=r_squared,
            predictions=predictions,
            volatility=volatility,
            moving_average=moving_avg,
            insights=insights,
            recommendations=recommendations
        )

        self.trends_cache[name] = analysis
        return analysis

    def _calculate_slope(
        self,
        data_points: List[Tuple[datetime, float]]
    ) -> float:
        """Calculate linear regression slope."""
        if len(data_points) < 2:
            return 0.0

        n = len(data_points)
        x_values = list(range(n))
        y_values = [p[1] for p in data_points]

        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(y_values)

        numerator = sum(
            (x_values[i] - x_mean) * (y_values[i] - y_mean)
            for i in range(n)
        )
        denominator = sum(
            (x_values[i] - x_mean) ** 2
            for i in range(n)
        )

        if denominator == 0:
            return 0.0

        return numerator / denominator

    def _determine_direction(
        self,
        slope: float,
        values: List[float]
    ) -> TrendDirection:
        """Determine trend direction from slope."""
        # Calculate coefficient of variation for volatility check
        if len(values) < 2:
            return TrendDirection.STABLE

        cv = statistics.stdev(values) / statistics.mean(values) if statistics.mean(values) != 0 else 0

        if cv > 0.3:  # High volatility
            return TrendDirection.VOLATILE
        elif slope > 0.5:
            return TrendDirection.IMPROVING
        elif slope < -0.5:
            return TrendDirection.DECLINING
        else:
            return TrendDirection.STABLE

    def _assess_severity(
        self,
        values: List[float],
        direction: TrendDirection
    ) -> TrendSeverity:
        """Assess trend severity."""
        if direction == TrendDirection.IMPROVING:
            return TrendSeverity.LOW
        elif direction == TrendDirection.STABLE:
            return TrendSeverity.LOW
        elif direction == TrendDirection.VOLATILE:
            return TrendSeverity.HIGH
        else:  # Declining
            min_val = min(values)
            if min_val < 50:
                return TrendSeverity.CRITICAL
            elif min_val < 70:
                return TrendSeverity.HIGH
            else:
                return TrendSeverity.MEDIUM

    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate volatility (standard deviation)."""
        if len(values) < 2:
            return 0.0

        return statistics.stdev(values) if len(values) >= 2 else 0.0

    def _calculate_moving_average(
        self,
        values: List[float],
        window: int = 7
    ) -> List[float]:
        """Calculate moving average."""
        moving_avg = []
        for i in range(len(values)):
            start = max(0, i - window + 1)
            avg = statistics.mean(values[start:i + 1])
            moving_avg.append(avg)
        return moving_avg

    def _calculate_r_squared(
        self,
        data_points: List[Tuple[datetime, float]]
    ) -> float:
        """Calculate R-squared value for goodness of fit."""
        if len(data_points) < 2:
            return 0.0

        n = len(data_points)
        x_values = list(range(n))
        y_values = [p[1] for p in data_points]

        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(y_values)

        ss_tot = sum((y - y_mean) ** 2 for y in y_values)

        slope = self._calculate_slope(data_points)
        ss_res = sum(
            (y_values[i] - (y_mean + slope * (x_values[i] - x_mean))) ** 2
            for i in range(n)
        )

        if ss_tot == 0:
            return 0.0

        return 1 - (ss_res / ss_tot)

    def _generate_predictions(
        self,
        data_points: List[Tuple[datetime, float]],
        periods: int = 7
    ) -> List[Tuple[datetime, float]]:
        """Generate future predictions using linear regression."""
        if len(data_points) < 2:
            return []

        slope = self._calculate_slope(data_points)
        last_date = data_points[-1][0]
        last_value = data_points[-1][1]

        predictions = []
        for i in range(1, periods + 1):
            future_date = last_date + timedelta(days=i)
            predicted_value = last_value + (slope * i)
            # Bound predictions to 0-100 range
            predicted_value = max(0, min(100, predicted_value))
            predictions.append((future_date, predicted_value))

        return predictions

    def _generate_insights(
        self,
        name: str,
        values: List[float],
        slope: float,
        direction: TrendDirection,
        volatility: float
    ) -> List[str]:
        """Generate insights from trend analysis."""
        insights = []

        if direction == TrendDirection.IMPROVING:
            improvement_rate = abs(slope)
            insights.append(
                f"{name} is improving at a rate of {improvement_rate:.2f} "
                f"points per observation"
            )
        elif direction == TrendDirection.DECLINING:
            insights.append(
                f"{name} is declining at a rate of {abs(slope):.2f} "
                f"points per observation - immediate attention required"
            )
        elif direction == TrendDirection.VOLATILE:
            insights.append(
                f"{name} shows high volatility ({volatility:.2f}) with "
                f"unstable patterns"
            )

        # Percentile insights
        current_value = values[-1] if values else 0
        if current_value < 60:
            insights.append(f"Current {name} score ({current_value:.1f}) "
                          f"is below acceptable thresholds")
        elif current_value > 90:
            insights.append(f"{name} is performing at premium levels "
                          f"({current_value:.1f})")

        # Velocity insights
        if len(values) > 1:
            recent_change = values[-1] - values[0]
            insights.append(f"Overall change over period: {recent_change:.2f} "
                          f"points")

        return insights

    def _generate_recommendations(
        self,
        direction: TrendDirection,
        severity: TrendSeverity,
        insights: List[str]
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        if severity == TrendSeverity.CRITICAL:
            recommendations.append("URGENT: Implement immediate remediation "
                                 "measures")
            recommendations.append("Escalate to compliance leadership")
            recommendations.append("Develop emergency action plan")
        elif severity == TrendSeverity.HIGH:
            recommendations.append("Develop comprehensive improvement plan")
            recommendations.append("Increase monitoring frequency")
            recommendations.append("Schedule priority review meeting")
        elif severity == TrendSeverity.MEDIUM:
            recommendations.append("Monitor closely for further degradation")
            recommendations.append("Plan preventive measures")

        if direction == TrendDirection.DECLINING:
            recommendations.append("Identify root causes of decline")
            recommendations.append("Implement corrective actions")
        elif direction == TrendDirection.IMPROVING:
            recommendations.append("Maintain current improvement momentum")
            recommendations.append("Document successful practices")
        elif direction == TrendDirection.VOLATILE:
            recommendations.append("Investigate sources of volatility")
            recommendations.append("Stabilize processes and controls")

        return recommendations

    def _create_empty_analysis(self, name: str) -> TrendAnalysis:
        """Create empty analysis for insufficient data."""
        return TrendAnalysis(
            name=name,
            data_points=[],
            direction=TrendDirection.STABLE,
            severity=TrendSeverity.LOW,
            slope=0.0,
            r_squared=0.0,
            predictions=[],
            volatility=0.0,
            moving_average=[],
            insights=["Insufficient data for trend analysis"],
            recommendations=["Collect more historical data"]
        )

    def compare_trends(
        self,
        trends: Dict[str, List[Tuple[datetime, float]]]
    ) -> Dict[str, TrendAnalysis]:
        """
        Compare multiple trends simultaneously.

        Args:
            trends: Dictionary of metric names to data points

        Returns:
            Dictionary of TrendAnalysis objects
        """
        results = {}
        for name, data_points in trends.items():
            results[name] = self.analyze_trend(name, data_points)
        return results

    def get_cached_trend(self, name: str) -> Optional[TrendAnalysis]:
        """Retrieve cached trend analysis."""
        return self.trends_cache.get(name)

    def clear_cache(self) -> None:
        """Clear the trends cache."""
        self.trends_cache.clear()
