"""
Industry Benchmarking Engine
Compares compliance metrics against industry standards and best practices.
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class IndustryType(str, Enum):
    """Industry classifications"""
    FINANCIAL = "financial"
    HEALTHCARE = "healthcare"
    TECHNOLOGY = "technology"
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    UTILITIES = "utilities"
    INSURANCE = "insurance"
    TELECOMS = "telecoms"
    EDUCATION = "education"
    GOVERNMENT = "government"


class CompanySize(str, Enum):
    """Company size classifications"""
    STARTUP = "startup"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ENTERPRISE = "enterprise"


@dataclass
class BenchmarkData:
    """Industry benchmark statistics"""
    industry: IndustryType
    company_size: CompanySize
    metric_name: str
    percentile_10: float
    percentile_25: float
    percentile_50: float  # Median
    percentile_75: float
    percentile_90: float
    mean: float
    std_deviation: float
    sample_size: int


@dataclass
class BenchmarkComparison:
    """Comparison against industry benchmark"""
    metric_name: str
    your_score: float
    benchmark_median: float
    percentile: float  # 0-100, position in distribution
    position: str  # 'above', 'at', or 'below' benchmark
    gap: float  # Difference from median
    peers_above: int  # Number of peers above this score
    peers_below: int  # Number of peers below this score
    recommended_target: float


class IndustryBenchmarkingEngine:
    """
    Industry benchmarking and comparative analysis.

    Features:
    - Benchmark database by industry/size
    - Percentile ranking
    - Gap analysis
    - Best practice comparison
    - Peer group analysis
    - Target setting
    """

    def __init__(self):
        """Initialize benchmarking engine."""
        self.benchmarks = self._load_benchmarks()
        self.comparisons: Dict[str, BenchmarkComparison] = {}

    def _load_benchmarks(self) -> Dict[str, BenchmarkData]:
        """Load industry benchmark data."""
        # Sample benchmark data - in production, this would come from a database
        benchmarks = {}

        # GDPR Compliance benchmarks
        for industry in IndustryType:
            for size in CompanySize:
                key = f"gdpr_compliance_{industry.value}_{size.value}"
                # Create realistic benchmarks based on industry/size
                base_score = 70
                if industry in [IndustryType.FINANCIAL, IndustryType.HEALTHCARE]:
                    base_score = 82
                if size in [CompanySize.ENTERPRISE, CompanySize.LARGE]:
                    base_score += 5

                benchmarks[key] = BenchmarkData(
                    industry=industry,
                    company_size=size,
                    metric_name="gdpr_compliance",
                    percentile_10=base_score - 15,
                    percentile_25=base_score - 8,
                    percentile_50=base_score,
                    percentile_75=base_score + 8,
                    percentile_90=base_score + 15,
                    mean=base_score,
                    std_deviation=10,
                    sample_size=100
                )

        return benchmarks

    def compare_to_benchmark(
        self,
        metric_name: str,
        your_score: float,
        industry: IndustryType,
        company_size: CompanySize
    ) -> BenchmarkComparison:
        """
        Compare your score against industry benchmark.

        Args:
            metric_name: Name of the metric
            your_score: Your organization's score
            industry: Industry classification
            company_size: Company size classification

        Returns:
            BenchmarkComparison with detailed analysis
        """
        key = f"{metric_name}_{industry.value}_{company_size.value}"
        benchmark = self.benchmarks.get(key)

        if not benchmark:
            # Return default if not found
            return self._create_default_comparison(metric_name, your_score)

        # Calculate percentile
        percentile = self._calculate_percentile(your_score, benchmark)

        # Determine position
        gap = your_score - benchmark.percentile_50
        if gap > 5:
            position = "above"
        elif gap < -5:
            position = "below"
        else:
            position = "at"

        # Estimate peer distribution
        peers_below = int((percentile / 100) * benchmark.sample_size)
        peers_above = benchmark.sample_size - peers_below

        # Set recommended target
        if percentile < 50:
            recommended_target = benchmark.percentile_75
        elif percentile < 75:
            recommended_target = benchmark.percentile_90
        else:
            recommended_target = 95

        comparison = BenchmarkComparison(
            metric_name=metric_name,
            your_score=your_score,
            benchmark_median=benchmark.percentile_50,
            percentile=percentile,
            position=position,
            gap=gap,
            peers_above=peers_above,
            peers_below=peers_below,
            recommended_target=recommended_target
        )

        self.comparisons[metric_name] = comparison
        return comparison

    def _calculate_percentile(
        self,
        score: float,
        benchmark: BenchmarkData
    ) -> float:
        """Calculate percentile rank against benchmark distribution."""
        if benchmark.std_deviation == 0:
            return 50.0

        # Using normal distribution approximation
        z_score = (score - benchmark.mean) / benchmark.std_deviation

        # Simplified percentile calculation
        # In production, use standard normal CDF
        if z_score < -2:
            return 2.5
        elif z_score < -1.5:
            return 6.7
        elif z_score < -1:
            return 15.9
        elif z_score < -0.5:
            return 30.9
        elif z_score < 0:
            return 50.0
        elif z_score < 0.5:
            return 69.1
        elif z_score < 1:
            return 84.1
        elif z_score < 1.5:
            return 93.3
        elif z_score < 2:
            return 97.5
        else:
            return 99.5

    def get_peer_metrics(
        self,
        industry: IndustryType,
        company_size: CompanySize,
        metric_name: str
    ) -> Dict[str, float]:
        """Get peer group statistics."""
        key = f"{metric_name}_{industry.value}_{company_size.value}"
        benchmark = self.benchmarks.get(key)

        if not benchmark:
            return {}

        return {
            'minimum': benchmark.percentile_10,
            'q1': benchmark.percentile_25,
            'median': benchmark.percentile_50,
            'q3': benchmark.percentile_75,
            'maximum': benchmark.percentile_90,
            'mean': benchmark.mean,
            'std_deviation': benchmark.std_deviation,
            'sample_size': benchmark.sample_size,
        }

    def benchmark_multiple_metrics(
        self,
        scores: Dict[str, float],
        industry: IndustryType,
        company_size: CompanySize
    ) -> Dict[str, BenchmarkComparison]:
        """
        Benchmark multiple metrics at once.

        Args:
            scores: Dictionary of metric names to scores
            industry: Industry classification
            company_size: Company size classification

        Returns:
            Dictionary of BenchmarkComparison objects
        """
        results = {}

        for metric_name, score in scores.items():
            comparison = self.compare_to_benchmark(
                metric_name, score, industry, company_size
            )
            results[metric_name] = comparison

        return results

    def get_best_practices(
        self,
        industry: IndustryType,
        metric_name: str
    ) -> List[Dict[str, Any]]:
        """
        Get best practices for industry/metric combination.

        Args:
            industry: Industry classification
            metric_name: Metric to improve

        Returns:
            List of best practice recommendations
        """
        practices = {
            ('gdpr_compliance', IndustryType.FINANCIAL): [
                {
                    'practice': 'Data Protection Impact Assessments',
                    'description': 'Conduct DPIAs for all high-risk processing',
                    'expected_impact': '+15-20%',
                    'difficulty': 'medium',
                },
                {
                    'practice': 'Privacy by Design',
                    'description': 'Embed privacy in all systems from design phase',
                    'expected_impact': '+10-15%',
                    'difficulty': 'high',
                },
            ],
            ('gdpr_compliance', IndustryType.HEALTHCARE): [
                {
                    'practice': 'Consent Management System',
                    'description': 'Implement robust consent tracking system',
                    'expected_impact': '+20-25%',
                    'difficulty': 'medium',
                },
                {
                    'practice': 'Data Subject Rights Management',
                    'description': 'Automated system for handling subject access requests',
                    'expected_impact': '+15-20%',
                    'difficulty': 'medium',
                },
            ],
        }

        key = (metric_name, industry)
        return practices.get(key, self._get_default_practices())

    def _get_default_practices(self) -> List[Dict[str, Any]]:
        """Get default best practices."""
        return [
            {
                'practice': 'Regular Compliance Audits',
                'description': 'Conduct internal audits quarterly',
                'expected_impact': '+10%',
                'difficulty': 'easy',
            },
            {
                'practice': 'Staff Training',
                'description': 'Annual compliance training for all staff',
                'expected_impact': '+8%',
                'difficulty': 'easy',
            },
            {
                'practice': 'Documentation',
                'description': 'Maintain comprehensive compliance documentation',
                'expected_impact': '+12%',
                'difficulty': 'medium',
            },
        ]

    def _create_default_comparison(
        self,
        metric_name: str,
        your_score: float
    ) -> BenchmarkComparison:
        """Create default comparison for missing benchmark."""
        return BenchmarkComparison(
            metric_name=metric_name,
            your_score=your_score,
            benchmark_median=70,
            percentile=50,
            position="at",
            gap=your_score - 70,
            peers_above=50,
            peers_below=50,
            recommended_target=85
        )

    def get_industry_trends(
        self,
        industry: IndustryType
    ) -> Dict[str, float]:
        """Get industry trends for all metrics."""
        trends = {}

        for key, benchmark in self.benchmarks.items():
            if benchmark.industry == industry:
                trends[benchmark.metric_name] = benchmark.mean

        return trends

    def identify_competitive_advantages(
        self,
        scores: Dict[str, float],
        industry: IndustryType,
        company_size: CompanySize
    ) -> List[str]:
        """
        Identify areas where you exceed industry standards.

        Args:
            scores: Your metric scores
            industry: Industry classification
            company_size: Company size classification

        Returns:
            List of competitive advantages
        """
        advantages = []

        for metric_name, score in scores.items():
            comparison = self.compare_to_benchmark(
                metric_name, score, industry, company_size
            )

            if comparison.percentile > 75:
                advantages.append(
                    f"{metric_name}: Top 25% ({comparison.percentile:.0f}th percentile) - "
                    f"{comparison.gap:.1f} points above median"
                )

        return advantages

    def identify_improvement_opportunities(
        self,
        scores: Dict[str, float],
        industry: IndustryType,
        company_size: CompanySize
    ) -> List[Dict[str, Any]]:
        """
        Identify areas for improvement with benchmark gaps.

        Args:
            scores: Your metric scores
            industry: Industry classification
            company_size: Company size classification

        Returns:
            List of improvement opportunities
        """
        opportunities = []

        for metric_name, score in scores.items():
            comparison = self.compare_to_benchmark(
                metric_name, score, industry, company_size
            )

            if comparison.percentile < 50:
                opportunity = {
                    'metric': metric_name,
                    'your_score': comparison.your_score,
                    'benchmark_median': comparison.benchmark_median,
                    'gap': comparison.gap,
                    'percentile': comparison.percentile,
                    'improvement_needed': comparison.recommended_target - score,
                    'estimated_effort': self._estimate_effort(comparison.gap),
                    'best_practices': self.get_best_practices(industry, metric_name),
                }
                opportunities.append(opportunity)

        # Sort by improvement potential
        opportunities.sort(key=lambda x: x['improvement_needed'], reverse=True)
        return opportunities

    def _estimate_effort(self, gap: float) -> str:
        """Estimate effort to close gap."""
        if gap < -20:
            return "high"
        elif gap < -10:
            return "medium"
        else:
            return "low"
