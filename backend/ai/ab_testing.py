"""
A/B Testing Framework for AI Prompts

Enables structured testing of different prompt variations:
- Variant management
- Performance tracking
- Statistical analysis
- Recommendation engine
"""

import random
import statistics
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, asdict, field
from datetime import datetime


class MetricType(str, Enum):
    """Types of metrics to track"""
    QUALITY_SCORE = "quality_score"
    RESPONSE_TIME = "response_time"
    TOKEN_USAGE = "token_usage"
    USER_SATISFACTION = "user_satisfaction"
    CONVERSION = "conversion"


@dataclass
class TestVariant:
    """A variant in A/B test"""
    id: str
    name: str
    prompt_template: str
    description: str = ""
    weight: float = 0.5  # Traffic allocation weight
    metadata: Dict = field(default_factory=dict)


@dataclass
class TestResult:
    """Result of A/B test"""
    variant_id: str
    metric_type: MetricType
    value: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict = field(default_factory=dict)


@dataclass
class VariantStats:
    """Statistics for a variant"""
    variant_id: str
    total_tests: int
    average_value: float
    median_value: float
    std_dev: float
    min_value: float
    max_value: float
    confidence_interval: tuple = (0.0, 0.0)  # 95% CI


class ABTestingFramework:
    """
    A/B Testing framework for AI prompts

    Features:
    - Multiple variant management
    - Weighted variant selection
    - Performance tracking
    - Statistical analysis
    - Winner detection
    """

    def __init__(self, test_id: str):
        self.test_id = test_id
        self.variants: Dict[str, TestVariant] = {}
        self.results: List[TestResult] = []
        self.created_at = datetime.utcnow().isoformat()
        self.metadata: Dict = {}

    def add_variant(self, variant: TestVariant):
        """Add variant to test"""
        self.variants[variant.id] = variant

    def remove_variant(self, variant_id: str) -> bool:
        """Remove variant from test"""
        if variant_id in self.variants:
            del self.variants[variant_id]
            return True
        return False

    def select_variant(self, randomized: bool = True) -> Optional[TestVariant]:
        """
        Select a variant based on weights

        Args:
            randomized: Use weighted random selection

        Returns:
            Selected variant or None if no variants
        """
        if not self.variants:
            return None

        if not randomized:
            # Return first variant
            return list(self.variants.values())[0]

        # Weighted random selection
        variants_list = list(self.variants.values())
        weights = [v.weight for v in variants_list]

        # Normalize weights
        total_weight = sum(weights)
        if total_weight == 0:
            return random.choice(variants_list)

        normalized_weights = [w / total_weight for w in weights]

        return random.choices(variants_list, weights=normalized_weights, k=1)[0]

    def record_result(
        self,
        variant_id: str,
        metric_type: MetricType,
        value: float,
        metadata: Optional[Dict] = None
    ) -> TestResult:
        """
        Record test result

        Args:
            variant_id: Which variant this result is for
            metric_type: Type of metric
            value: Metric value
            metadata: Additional metadata

        Returns:
            Recorded TestResult
        """
        result = TestResult(
            variant_id=variant_id,
            metric_type=metric_type,
            value=value,
            timestamp=datetime.utcnow().isoformat(),
            metadata=metadata or {}
        )

        self.results.append(result)
        return result

    def get_variant_stats(
        self,
        variant_id: str,
        metric_type: Optional[MetricType] = None
    ) -> VariantStats:
        """
        Get statistics for a variant

        Args:
            variant_id: Which variant
            metric_type: Filter by metric type (None = all)

        Returns:
            VariantStats with computed statistics
        """
        # Filter results
        filtered = [
            r for r in self.results
            if r.variant_id == variant_id and
            (metric_type is None or r.metric_type == metric_type)
        ]

        if not filtered:
            return VariantStats(
                variant_id=variant_id,
                total_tests=0,
                average_value=0.0,
                median_value=0.0,
                std_dev=0.0,
                min_value=0.0,
                max_value=0.0
            )

        values = [r.value for r in filtered]

        avg = statistics.mean(values)
        median = statistics.median(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0.0
        min_val = min(values)
        max_val = max(values)

        # Simple 95% confidence interval
        ci_margin = 1.96 * std_dev / (len(values) ** 0.5) if std_dev > 0 else 0
        ci = (avg - ci_margin, avg + ci_margin)

        return VariantStats(
            variant_id=variant_id,
            total_tests=len(filtered),
            average_value=avg,
            median_value=median,
            std_dev=std_dev,
            min_value=min_val,
            max_value=max_val,
            confidence_interval=ci
        )

    def get_winner(
        self,
        metric_type: MetricType,
        higher_is_better: bool = True
    ) -> Optional[str]:
        """
        Determine winning variant for metric

        Args:
            metric_type: Which metric to compare
            higher_is_better: Whether higher values are better

        Returns:
            ID of winning variant or None
        """
        stats_dict = {}

        for variant_id in self.variants.keys():
            stats = self.get_variant_stats(variant_id, metric_type)
            if stats.total_tests > 0:
                stats_dict[variant_id] = stats.average_value

        if not stats_dict:
            return None

        if higher_is_better:
            return max(stats_dict.items(), key=lambda x: x[1])[0]
        else:
            return min(stats_dict.items(), key=lambda x: x[1])[0]

    def is_significant(
        self,
        variant_id_a: str,
        variant_id_b: str,
        metric_type: MetricType,
        confidence: float = 0.95
    ) -> bool:
        """
        Test if difference between variants is statistically significant

        Args:
            variant_id_a: First variant
            variant_id_b: Second variant
            metric_type: Which metric to compare
            confidence: Confidence level (0-1)

        Returns:
            True if difference is significant
        """
        stats_a = self.get_variant_stats(variant_id_a, metric_type)
        stats_b = self.get_variant_stats(variant_id_b, metric_type)

        if stats_a.total_tests == 0 or stats_b.total_tests == 0:
            return False

        # Simple significance test: non-overlapping confidence intervals
        # For more rigor, use proper statistical tests
        ci_a = stats_a.confidence_interval
        ci_b = stats_b.confidence_interval

        # No overlap = significant
        return ci_a[1] < ci_b[0] or ci_b[1] < ci_a[0]

    def get_comparison(self, metric_type: MetricType) -> Dict:
        """
        Get comparison of all variants for a metric

        Args:
            metric_type: Which metric to compare

        Returns:
            Dict with variant comparisons
        """
        comparison = {}

        for variant_id in self.variants.keys():
            stats = self.get_variant_stats(variant_id, metric_type)
            comparison[variant_id] = {
                "average": stats.average_value,
                "median": stats.median_value,
                "std_dev": stats.std_dev,
                "total_tests": stats.total_tests,
                "confidence_interval": stats.confidence_interval
            }

        return comparison

    def recommend_variant(
        self,
        metric_type: MetricType,
        higher_is_better: bool = True
    ) -> Optional[str]:
        """
        Recommend best performing variant

        Args:
            metric_type: Which metric to optimize
            higher_is_better: Whether higher values are better

        Returns:
            ID of recommended variant
        """
        return self.get_winner(metric_type, higher_is_better)

    def get_summary(self) -> Dict:
        """Get test summary"""
        return {
            "test_id": self.test_id,
            "created_at": self.created_at,
            "variants": len(self.variants),
            "total_results": len(self.results),
            "variant_ids": list(self.variants.keys()),
            "metric_types": list(set(r.metric_type.value for r in self.results))
        }
