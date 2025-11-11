"""
Executive Summary Report Generator
Creates concise executive-level compliance summaries.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExecutiveSummary:
    """Executive summary report"""
    title: str
    generated_date: datetime
    organization: str
    period: Dict[str, str]  # start, end dates

    # Key sections
    overall_score: float
    risk_level: str  # critical, high, medium, low
    compliance_status: str  # passing, warning, failing

    # Highlights
    key_metrics: Dict[str, float]
    top_risks: List[str]
    top_opportunities: List[str]
    critical_actions: List[str]

    # Details
    module_status: Dict[str, Dict[str, Any]]
    trend_summary: str
    forecast_summary: str

    # Recommendations
    priority_recommendations: List[Dict[str, str]]
    next_steps: List[str]

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


class ExecutiveSummaryGenerator:
    """
    Executive summary report generator.

    Features:
    - One-page executive overview
    - Key metrics highlighted
    - Risk assessment summary
    - Critical actions identified
    - Trend and forecast summaries
    - Actionable recommendations
    """

    def __init__(self):
        """Initialize executive summary generator."""
        self.summaries: Dict[str, ExecutiveSummary] = {}

    def generate_summary(
        self,
        organization: str,
        compliance_data: Dict[str, Any],
        period_start: datetime,
        period_end: datetime,
        analytics_data: Optional[Dict[str, Any]] = None
    ) -> ExecutiveSummary:
        """
        Generate executive summary from compliance data.

        Args:
            organization: Organization name
            compliance_data: Full compliance data
            period_start: Report period start
            period_end: Report period end
            analytics_data: Optional analytics/trend data

        Returns:
            ExecutiveSummary
        """
        analytics_data = analytics_data or {}

        # Extract key metrics
        overall_score = self._extract_overall_score(compliance_data)
        module_scores = self._extract_module_scores(compliance_data)

        # Determine status
        risk_level = self._assess_risk_level(overall_score)
        compliance_status = self._determine_compliance_status(overall_score)

        # Identify risks and opportunities
        top_risks = self._identify_top_risks(compliance_data, analytics_data)
        top_opportunities = self._identify_opportunities(
            compliance_data, analytics_data
        )

        # Determine critical actions
        critical_actions = self._identify_critical_actions(
            top_risks, module_scores
        )

        # Generate summaries
        trend_summary = self._generate_trend_summary(analytics_data)
        forecast_summary = self._generate_forecast_summary(analytics_data)

        # Generate recommendations
        priority_recommendations = self._generate_recommendations(
            overall_score, top_risks, module_scores
        )
        next_steps = self._generate_next_steps(priority_recommendations)

        summary = ExecutiveSummary(
            title=f"{organization} - Compliance Executive Summary",
            generated_date=datetime.now(),
            organization=organization,
            period={
                'start': period_start.strftime('%Y-%m-%d'),
                'end': period_end.strftime('%Y-%m-%d'),
            },
            overall_score=overall_score,
            risk_level=risk_level,
            compliance_status=compliance_status,
            key_metrics={
                'overall_compliance_score': overall_score,
                'modules_compliant': len([s for s in module_scores.values() if s >= 70]),
                'modules_total': len(module_scores),
                'critical_findings': len([r for r in top_risks if 'critical' in r.lower()]),
            },
            top_risks=top_risks[:5],  # Top 5 risks
            top_opportunities=top_opportunities[:3],  # Top 3 opportunities
            critical_actions=critical_actions[:3],  # Top 3 critical actions
            module_status={
                name: {
                    'score': score,
                    'status': 'Compliant' if score >= 70 else 'At Risk',
                    'trend': self._get_module_trend(name, analytics_data),
                }
                for name, score in module_scores.items()
            },
            trend_summary=trend_summary,
            forecast_summary=forecast_summary,
            priority_recommendations=priority_recommendations[:5],
            next_steps=next_steps,
            metadata={
                'data_sources': list(compliance_data.keys()),
                'summary_type': 'executive',
            }
        )

        summary_id = f"summary_{organization}_{datetime.now().timestamp()}"
        self.summaries[summary_id] = summary

        return summary

    def _extract_overall_score(self, compliance_data: Dict[str, Any]) -> float:
        """Extract overall compliance score."""
        if 'overall_score' in compliance_data:
            return compliance_data['overall_score']

        # Calculate from module scores
        module_scores = self._extract_module_scores(compliance_data)
        if module_scores:
            return sum(module_scores.values()) / len(module_scores)

        return 0.0

    def _extract_module_scores(self, compliance_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract module-level compliance scores."""
        scores = {}

        if 'modules' in compliance_data:
            for module_name, module_data in compliance_data['modules'].items():
                if isinstance(module_data, dict) and 'score' in module_data:
                    scores[module_name] = module_data['score']
                elif isinstance(module_data, (int, float)):
                    scores[module_name] = module_data

        return scores

    def _assess_risk_level(self, overall_score: float) -> str:
        """Assess overall risk level from score."""
        if overall_score < 50:
            return "critical"
        elif overall_score < 70:
            return "high"
        elif overall_score < 85:
            return "medium"
        else:
            return "low"

    def _determine_compliance_status(self, overall_score: float) -> str:
        """Determine compliance status."""
        if overall_score >= 85:
            return "Compliant"
        elif overall_score >= 70:
            return "Substantially Compliant"
        elif overall_score >= 50:
            return "Non-Compliant with Remediation Plans"
        else:
            return "Critical Non-Compliance"

    def _identify_top_risks(
        self,
        compliance_data: Dict[str, Any],
        analytics_data: Dict[str, Any]
    ) -> List[str]:
        """Identify top compliance risks."""
        risks = []

        # Extract from compliance data
        if 'findings' in compliance_data:
            findings = compliance_data['findings']
            if isinstance(findings, list):
                for finding in findings[:5]:
                    if isinstance(finding, dict) and 'description' in finding:
                        severity = finding.get('severity', 'medium').lower()
                        if severity in ['critical', 'high']:
                            risks.append(finding['description'])

        # Extract from anomalies
        if 'anomalies' in analytics_data:
            anomalies = analytics_data['anomalies']
            if isinstance(anomalies, list):
                for anomaly in anomalies[:3]:
                    if isinstance(anomaly, dict):
                        risks.append(f"Anomaly detected: {anomaly.get('description', 'Unknown')}")

        return risks

    def _identify_opportunities(
        self,
        compliance_data: Dict[str, Any],
        analytics_data: Dict[str, Any]
    ) -> List[str]:
        """Identify improvement opportunities."""
        opportunities = []

        # From improvements in trend
        if 'trends' in analytics_data:
            trends = analytics_data['trends']
            if isinstance(trends, dict):
                for metric, trend_data in trends.items():
                    if trend_data.get('direction') == 'improving':
                        opportunities.append(
                            f"Capitalize on improving {metric} trend"
                        )

        # From benchmarking
        if 'benchmarks' in analytics_data:
            benchmarks = analytics_data['benchmarks']
            if isinstance(benchmarks, dict):
                for metric, bench_data in benchmarks.items():
                    if bench_data.get('percentile', 0) > 75:
                        opportunities.append(
                            f"Leverage {metric} excellence as competitive advantage"
                        )

        return opportunities

    def _identify_critical_actions(
        self,
        top_risks: List[str],
        module_scores: Dict[str, float]
    ) -> List[str]:
        """Identify critical actions needed."""
        actions = []

        # From low-scoring modules
        for module, score in module_scores.items():
            if score < 50:
                actions.append(f"Urgent: Remediate {module} compliance issues ({score:.0f}%)")
            elif score < 70:
                actions.append(f"Priority: Improve {module} to minimum threshold (Current: {score:.0f}%)")

        # From risks
        for risk in top_risks[:2]:
            if 'data' in risk.lower() or 'breach' in risk.lower():
                actions.append(f"CRITICAL: Address - {risk}")
            else:
                actions.append(f"Important: {risk}")

        return actions

    def _generate_trend_summary(self, analytics_data: Dict[str, Any]) -> str:
        """Generate trend summary text."""
        if 'trends' not in analytics_data:
            return "Insufficient trend data for analysis."

        trends = analytics_data['trends']
        improving_count = 0
        declining_count = 0

        if isinstance(trends, dict):
            for metric, trend_data in trends.items():
                if trend_data.get('direction') == 'improving':
                    improving_count += 1
                elif trend_data.get('direction') == 'declining':
                    declining_count += 1

        if improving_count > declining_count:
            return (f"Positive trend: {improving_count} metrics improving. "
                   f"Maintain current initiatives.")
        elif declining_count > improving_count:
            return (f"Concerning trend: {declining_count} metrics declining. "
                   f"Immediate action required.")
        else:
            return "Trends are stable. Continue monitoring."

    def _generate_forecast_summary(self, analytics_data: Dict[str, Any]) -> str:
        """Generate forecast summary text."""
        if 'forecasts' not in analytics_data:
            return "Insufficient data for forecasting."

        forecasts = analytics_data['forecasts']
        if isinstance(forecasts, dict):
            most_likely = forecasts.get('most_likely_scenario', 'unknown')
            if most_likely == 'optimistic':
                return "30-day forecast predicts improvement. Maintain current trajectory."
            elif most_likely == 'pessimistic':
                return "30-day forecast predicts decline. Urgent remediation needed."
            else:
                return "30-day forecast indicates stable trend with normal variation."

        return "Forecast data unavailable."

    def _get_module_trend(
        self,
        module_name: str,
        analytics_data: Dict[str, Any]
    ) -> str:
        """Get trend for specific module."""
        if 'trends' not in analytics_data:
            return "unknown"

        trends = analytics_data.get('trends', {})
        if module_name in trends:
            return trends[module_name].get('direction', 'unknown')

        return "unknown"

    def _generate_recommendations(
        self,
        overall_score: float,
        top_risks: List[str],
        module_scores: Dict[str, float]
    ) -> List[Dict[str, str]]:
        """Generate priority recommendations."""
        recommendations = []

        # High-level recommendations
        if overall_score < 70:
            recommendations.append({
                'priority': 'Critical',
                'action': 'Establish comprehensive compliance improvement program',
                'expected_impact': 'Improve overall score by 15-20%',
            })

        # Module-specific recommendations
        for module, score in module_scores.items():
            if score < 70:
                recommendations.append({
                    'priority': 'High',
                    'action': f'Implement {module} remediation plan',
                    'expected_impact': f'Improve {module} score to 80+%',
                })

        # Risk-based recommendations
        if top_risks:
            recommendations.append({
                'priority': 'High',
                'action': 'Address identified compliance risks',
                'expected_impact': 'Reduce risk level and audit findings',
            })

        return recommendations

    def _generate_next_steps(
        self,
        recommendations: List[Dict[str, str]]
    ) -> List[str]:
        """Generate next steps based on recommendations."""
        steps = []

        if recommendations:
            for idx, rec in enumerate(recommendations[:3], 1):
                steps.append(
                    f"{idx}. {rec['action']}"
                )

        steps.append("4. Schedule follow-up review in 30 days")
        steps.append("5. Establish compliance metrics dashboard")

        return steps

    def get_summary(self, summary_id: str) -> Optional[ExecutiveSummary]:
        """Retrieve summary."""
        return self.summaries.get(summary_id)

    def export_summary_text(self, summary: ExecutiveSummary) -> str:
        """Export summary as formatted text."""
        text_parts = []

        text_parts.append(f"{'='*60}")
        text_parts.append(f"{summary.title}")
        text_parts.append(f"{'='*60}")
        text_parts.append("")

        text_parts.append(f"Period: {summary.period['start']} to {summary.period['end']}")
        text_parts.append(f"Generated: {summary.generated_date.strftime('%Y-%m-%d %H:%M:%S')}")
        text_parts.append("")

        text_parts.append("EXECUTIVE OVERVIEW")
        text_parts.append(f"  Overall Compliance Score: {summary.overall_score:.1f}%")
        text_parts.append(f"  Risk Level: {summary.risk_level.upper()}")
        text_parts.append(f"  Status: {summary.compliance_status}")
        text_parts.append("")

        text_parts.append("KEY METRICS")
        for metric, value in summary.key_metrics.items():
            text_parts.append(f"  {metric.replace('_', ' ').title()}: {value}")
        text_parts.append("")

        text_parts.append("TOP RISKS")
        for idx, risk in enumerate(summary.top_risks, 1):
            text_parts.append(f"  {idx}. {risk}")
        text_parts.append("")

        text_parts.append("PRIORITY RECOMMENDATIONS")
        for idx, rec in enumerate(summary.priority_recommendations, 1):
            text_parts.append(f"  {idx}. {rec['action']}")
        text_parts.append("")

        text_parts.append("NEXT STEPS")
        for step in summary.next_steps:
            text_parts.append(f"  • {step}")

        return "\n".join(text_parts)
