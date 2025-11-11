"""
Cost Tracking and Optimization Module

Tracks AI API costs and provides optimization recommendations:
- Per-provider cost tracking
- Token usage monitoring
- Cost predictions
- Optimization suggestions
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum


class Provider(str, Enum):
    """AI Provider"""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GEMINI = "gemini"


@dataclass
class PricingConfig:
    """Pricing configuration for provider"""
    provider: Provider
    input_price_per_mtok: float  # Price per million input tokens
    output_price_per_mtok: float  # Price per million output tokens
    metadata: Dict = field(default_factory=dict)


@dataclass
class CostEntry:
    """Entry in cost tracking log"""
    timestamp: str
    provider: Provider
    input_tokens: int
    output_tokens: int
    cost: float
    metadata: Dict = field(default_factory=dict)


@dataclass
class CostMetrics:
    """Cost metrics summary"""
    total_cost: float
    total_input_tokens: int
    total_output_tokens: int
    average_cost_per_request: float
    requests_count: int
    cost_by_provider: Dict[str, float]
    cost_trend: List[Tuple[str, float]]  # (timestamp, cost) pairs
    projected_monthly_cost: float


class CostTracker:
    """
    Tracks and optimizes AI API costs

    Features:
    - Multi-provider cost tracking
    - Token usage monitoring
    - Cost prediction
    - Optimization recommendations
    """

    def __init__(self):
        self.pricing_config: Dict[Provider, PricingConfig] = {}
        self.cost_log: List[CostEntry] = []
        self._setup_default_pricing()

    def _setup_default_pricing(self):
        """Setup default pricing for major providers"""
        # Prices as of Nov 2024 (approximate)
        self.set_provider_pricing(Provider.ANTHROPIC, 0.80, 2.40)  # Claude 3.5 Sonnet
        self.set_provider_pricing(Provider.OPENAI, 2.50, 10.00)  # GPT-4
        self.set_provider_pricing(Provider.GEMINI, 0.075, 0.30)  # Gemini 1.5 Flash

    def set_provider_pricing(
        self,
        provider: Provider,
        input_price_per_mtok: float,
        output_price_per_mtok: float
    ):
        """Set pricing for provider"""
        self.pricing_config[provider] = PricingConfig(
            provider=provider,
            input_price_per_mtok=input_price_per_mtok,
            output_price_per_mtok=output_price_per_mtok
        )

    def record_usage(
        self,
        provider: Provider,
        input_tokens: int,
        output_tokens: int,
        metadata: Optional[Dict] = None
    ) -> CostEntry:
        """
        Record API usage

        Args:
            provider: Which provider
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            metadata: Additional metadata

        Returns:
            CostEntry that was recorded
        """
        cost = self._calculate_cost(provider, input_tokens, output_tokens)

        entry = CostEntry(
            timestamp=datetime.utcnow().isoformat(),
            provider=provider,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            metadata=metadata or {}
        )

        self.cost_log.append(entry)
        return entry

    def _calculate_cost(
        self,
        provider: Provider,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Calculate cost for usage"""
        if provider not in self.pricing_config:
            return 0.0

        config = self.pricing_config[provider]

        input_cost = (input_tokens / 1_000_000) * config.input_price_per_mtok
        output_cost = (output_tokens / 1_000_000) * config.output_price_per_mtok

        return input_cost + output_cost

    def get_metrics(self, days_back: Optional[int] = None) -> CostMetrics:
        """
        Get cost metrics

        Args:
            days_back: Include last N days (None = all time)

        Returns:
            CostMetrics with computed statistics
        """
        # Filter by time if specified
        entries = self.cost_log
        if days_back:
            cutoff = datetime.utcnow() - timedelta(days=days_back)
            entries = [
                e for e in self.cost_log
                if datetime.fromisoformat(e.timestamp) > cutoff
            ]

        if not entries:
            return CostMetrics(
                total_cost=0.0,
                total_input_tokens=0,
                total_output_tokens=0,
                average_cost_per_request=0.0,
                requests_count=0,
                cost_by_provider={},
                cost_trend=[],
                projected_monthly_cost=0.0
            )

        total_cost = sum(e.cost for e in entries)
        total_input = sum(e.input_tokens for e in entries)
        total_output = sum(e.output_tokens for e in entries)
        requests = len(entries)

        # Cost by provider
        cost_by_provider = {}
        for entry in entries:
            provider_name = entry.provider.value
            cost_by_provider[provider_name] = cost_by_provider.get(provider_name, 0.0) + entry.cost

        # Cost trend (daily)
        cost_trend = self._calculate_cost_trend(entries)

        # Project monthly cost
        if days_back and days_back > 0:
            daily_avg = total_cost / days_back
            projected_monthly = daily_avg * 30
        else:
            projected_monthly = 0.0

        return CostMetrics(
            total_cost=total_cost,
            total_input_tokens=total_input,
            total_output_tokens=total_output,
            average_cost_per_request=total_cost / requests if requests > 0 else 0.0,
            requests_count=requests,
            cost_by_provider=cost_by_provider,
            cost_trend=cost_trend,
            projected_monthly_cost=projected_monthly
        )

    def _calculate_cost_trend(self, entries: List[CostEntry]) -> List[Tuple[str, float]]:
        """Calculate daily cost trend"""
        daily_costs: Dict[str, float] = {}

        for entry in entries:
            date = entry.timestamp.split('T')[0]  # Extract date
            daily_costs[date] = daily_costs.get(date, 0.0) + entry.cost

        # Sort by date
        trend = sorted(daily_costs.items())
        return trend

    def get_provider_comparison(self) -> Dict:
        """Compare costs across providers"""
        metrics_by_provider = {}

        for provider in Provider:
            provider_entries = [e for e in self.cost_log if e.provider == provider]

            if not provider_entries:
                continue

            total_cost = sum(e.cost for e in provider_entries)
            total_tokens = sum(e.input_tokens + e.output_tokens for e in provider_entries)
            avg_cost_per_token = total_cost / total_tokens if total_tokens > 0 else 0

            metrics_by_provider[provider.value] = {
                "total_cost": total_cost,
                "total_tokens": total_tokens,
                "request_count": len(provider_entries),
                "average_cost_per_token": avg_cost_per_token,
                "cost_per_request": total_cost / len(provider_entries) if provider_entries else 0
            }

        return metrics_by_provider

    def get_optimization_recommendations(self, threshold: float = 0.0) -> List[Dict]:
        """
        Get cost optimization recommendations

        Args:
            threshold: Only recommend if savings > threshold

        Returns:
            List of recommendations
        """
        recommendations = []

        metrics = self.get_metrics(days_back=7)

        # Recommendation 1: Check for provider switch opportunities
        provider_comparison = self.get_provider_comparison()

        if len(provider_comparison) > 1:
            cheapest_provider = min(
                provider_comparison.items(),
                key=lambda x: x[1]['average_cost_per_token']
            )
            most_expensive = max(
                provider_comparison.items(),
                key=lambda x: x[1]['average_cost_per_token']
            )

            savings = most_expensive[1]['total_cost'] * 0.3  # 30% estimate

            if savings > threshold:
                recommendations.append({
                    "type": "provider_switch",
                    "message": f"Consider switching to {cheapest_provider[0]} for {savings:.2f} daily savings",
                    "current_provider": most_expensive[0],
                    "recommended_provider": cheapest_provider[0],
                    "estimated_savings": savings
                })

        # Recommendation 2: Suggest caching if many repeated queries
        repeated_queries = self._detect_repeated_queries()
        if repeated_queries:
            estimated_savings = repeated_queries['cost'] * 0.8  # 80% savings with caching
            recommendations.append({
                "type": "implement_caching",
                "message": f"Implement semantic caching to save {estimated_savings:.2f} daily",
                "repeated_query_count": repeated_queries['count'],
                "estimated_savings": estimated_savings
            })

        # Recommendation 3: Prompt optimization
        metrics = self.get_metrics(days_back=7)
        if metrics.total_input_tokens > 100000:
            recommendations.append({
                "type": "prompt_optimization",
                "message": "Optimize prompts to reduce token usage",
                "current_daily_tokens": metrics.total_input_tokens / 7,
                "potential_reduction_percent": 15
            })

        return recommendations

    def _detect_repeated_queries(self) -> Optional[Dict]:
        """Detect patterns of repeated queries"""
        # This is a simplified detection
        # In production, implement proper query deduplication

        if len(self.cost_log) < 2:
            return None

        # Group by day
        daily_entries: Dict[str, List[CostEntry]] = {}
        for entry in self.cost_log:
            date = entry.timestamp.split('T')[0]
            if date not in daily_entries:
                daily_entries[date] = []
            daily_entries[date].append(entry)

        # Check for similar requests (same token counts)
        repeated = 0
        repeated_cost = 0.0

        for entries in daily_entries.values():
            token_counts = {}
            for entry in entries:
                key = (entry.input_tokens, entry.output_tokens)
                if key not in token_counts:
                    token_counts[key] = []
                token_counts[key].append(entry)

            for token_key, matching_entries in token_counts.items():
                if len(matching_entries) > 1:
                    repeated += len(matching_entries) - 1
                    repeated_cost += sum(e.cost for e in matching_entries[1:])

        if repeated > 0:
            return {
                "count": repeated,
                "cost": repeated_cost
            }

        return None

    def export_report(self, filepath: str):
        """Export cost report to file"""
        metrics = self.get_metrics()

        report = f"""Cost Report
Generated: {datetime.utcnow().isoformat()}

Summary:
- Total Cost: ${metrics.total_cost:.2f}
- Total Input Tokens: {metrics.total_input_tokens:,}
- Total Output Tokens: {metrics.total_output_tokens:,}
- Total Requests: {metrics.requests_count}
- Average Cost per Request: ${metrics.average_cost_per_request:.4f}
- Projected Monthly Cost: ${metrics.projected_monthly_cost:.2f}

Cost by Provider:
"""

        for provider, cost in metrics.cost_by_provider.items():
            report += f"- {provider}: ${cost:.2f}\n"

        report += "\nRecommendations:\n"
        for rec in self.get_optimization_recommendations():
            report += f"- [{rec['type']}] {rec['message']}\n"

        with open(filepath, 'w') as f:
            f.write(report)
