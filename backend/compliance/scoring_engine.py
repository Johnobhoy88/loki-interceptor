"""
Scoring Engine - Calculates compliance scores (0-100) for each module
Provides detailed scoring breakdowns, trends, and improvement metrics.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class ScoreBreakdown:
    """Detailed breakdown of a compliance score."""
    total_score: float  # 0-100
    component_scores: Dict[str, float] = field(default_factory=dict)
    gate_scores: Dict[str, float] = field(default_factory=dict)
    penalties: List[Dict[str, Any]] = field(default_factory=list)
    bonuses: List[Dict[str, Any]] = field(default_factory=list)
    grade: str = ''  # A+, A, B+, B, C, D, F
    percentile: Optional[float] = None


@dataclass
class ScoreTrend:
    """Historical trend of compliance scores."""
    current_score: float
    previous_score: Optional[float]
    change: float
    trend: str  # 'improving', 'declining', 'stable'
    velocity: float  # Rate of change


class ScoringEngine:
    """
    Advanced compliance scoring system.

    Features:
    - 0-100 scoring scale
    - Multi-factor scoring algorithm
    - Severity-weighted calculations
    - Historical trend analysis
    - Grade assignment (A+ to F)
    - Percentile ranking
    """

    def __init__(self):
        self.score_history: Dict[str, List[tuple]] = {}  # (timestamp, score)
        self._initialize_scoring_weights()

    def _initialize_scoring_weights(self):
        """Initialize scoring weights for different factors."""
        self.weights = {
            'gate_pass_rate': 0.40,  # 40% - Basic gate pass/fail
            'severity_adjusted': 0.30,  # 30% - Weighted by issue severity
            'completeness': 0.15,  # 15% - Coverage of requirements
            'best_practices': 0.15,  # 15% - Beyond minimum compliance
        }

        self.severity_weights = {
            'critical': 1.0,
            'high': 0.7,
            'medium': 0.4,
            'low': 0.2
        }

        self.grade_thresholds = {
            'A+': 97,
            'A': 93,
            'A-': 90,
            'B+': 87,
            'B': 83,
            'B-': 80,
            'C+': 77,
            'C': 73,
            'C-': 70,
            'D': 60,
            'F': 0
        }

    def calculate_scores(self, module_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive compliance scores for all modules.

        Args:
            module_results: Dictionary of compliance results by module_id

        Returns:
            Detailed scoring report with breakdowns and trends
        """
        logger.info(f"Calculating scores for {len(module_results)} modules")

        scores = {}
        for module_id, result in module_results.items():
            score_breakdown = self._calculate_module_score(module_id, result)
            scores[module_id] = {
                'score': score_breakdown.total_score,
                'grade': score_breakdown.grade,
                'breakdown': self._serialize_breakdown(score_breakdown),
                'trend': self._calculate_trend(module_id, score_breakdown.total_score),
                'recommendations': self._generate_score_recommendations(score_breakdown, result)
            }

        # Calculate aggregate scores
        aggregate = self._calculate_aggregate_scores(scores)

        return {
            'timestamp': datetime.now().isoformat(),
            'module_scores': scores,
            'aggregate': aggregate,
            'summary': self._generate_score_summary(scores, aggregate)
        }

    def _calculate_module_score(self, module_id: str, result: Any) -> ScoreBreakdown:
        """Calculate detailed score for a single module."""
        breakdown = ScoreBreakdown(total_score=0.0)

        # Component 1: Gate pass rate (40%)
        if result.total_gates > 0:
            gate_pass_rate = result.gates_passed / result.total_gates
            breakdown.component_scores['gate_pass_rate'] = gate_pass_rate * 100
        else:
            breakdown.component_scores['gate_pass_rate'] = 0.0

        # Component 2: Severity-adjusted score (30%)
        severity_score = self._calculate_severity_adjusted_score(result)
        breakdown.component_scores['severity_adjusted'] = severity_score

        # Component 3: Completeness score (15%)
        completeness_score = self._calculate_completeness_score(result)
        breakdown.component_scores['completeness'] = completeness_score

        # Component 4: Best practices score (15%)
        best_practices_score = self._calculate_best_practices_score(result)
        breakdown.component_scores['best_practices'] = best_practices_score

        # Calculate weighted total
        total_score = (
            breakdown.component_scores['gate_pass_rate'] * self.weights['gate_pass_rate'] +
            breakdown.component_scores['severity_adjusted'] * self.weights['severity_adjusted'] +
            breakdown.component_scores['completeness'] * self.weights['completeness'] +
            breakdown.component_scores['best_practices'] * self.weights['best_practices']
        )

        # Apply penalties
        penalties = self._calculate_penalties(result)
        for penalty in penalties:
            total_score -= penalty['amount']
        breakdown.penalties = penalties

        # Apply bonuses
        bonuses = self._calculate_bonuses(result)
        for bonus in bonuses:
            total_score += bonus['amount']
        breakdown.bonuses = bonuses

        # Ensure score is between 0 and 100
        breakdown.total_score = max(0.0, min(100.0, total_score))

        # Assign grade
        breakdown.grade = self._assign_grade(breakdown.total_score)

        # Calculate individual gate scores
        breakdown.gate_scores = self._calculate_gate_scores(result)

        return breakdown

    def _calculate_severity_adjusted_score(self, result: Any) -> float:
        """Calculate score adjusted for issue severity."""
        if result.total_gates == 0:
            return 0.0

        # Start with perfect score
        score = 100.0

        # Deduct based on severity-weighted issues
        critical_deduction = len(result.critical_issues) * self.severity_weights['critical'] * 10
        high_deduction = len(result.high_issues) * self.severity_weights['high'] * 7
        medium_deduction = len(result.medium_issues) * self.severity_weights['medium'] * 4

        total_deduction = critical_deduction + high_deduction + medium_deduction

        # Normalize by number of gates
        normalized_deduction = (total_deduction / result.total_gates) * 10

        score -= normalized_deduction

        return max(0.0, min(100.0, score))

    def _calculate_completeness_score(self, result: Any) -> float:
        """Calculate completeness score based on requirement coverage."""
        if result.total_gates == 0:
            return 0.0

        # Completeness is based on:
        # 1. All gates executed (not N/A)
        # 2. Minimal warnings
        # 3. Full documentation

        base_score = 100.0

        # Deduct for warnings (incomplete implementation)
        warning_penalty = (result.gates_warning / result.total_gates) * 20
        base_score -= warning_penalty

        # Deduct for N/A gates (not applicable = incomplete coverage)
        # This would need to be added to result structure if tracked

        return max(0.0, min(100.0, base_score))

    def _calculate_best_practices_score(self, result: Any) -> float:
        """Calculate score for going beyond minimum compliance."""
        score = 50.0  # Base score for meeting minimums

        # Bonus points for:
        # - No critical issues: +20
        # - No high issues: +15
        # - Detailed documentation: +10
        # - Proactive measures: +5

        if len(result.critical_issues) == 0:
            score += 20

        if len(result.high_issues) == 0:
            score += 15

        if len(result.medium_issues) == 0:
            score += 10

        if result.gates_warning == 0:
            score += 5

        return min(100.0, score)

    def _calculate_penalties(self, result: Any) -> List[Dict[str, Any]]:
        """Calculate penalties to be applied to score."""
        penalties = []

        # Critical issue penalty
        if result.critical_issues:
            penalties.append({
                'reason': f'{len(result.critical_issues)} critical issues',
                'amount': len(result.critical_issues) * 5,
                'severity': 'critical'
            })

        # Failed gates penalty (if many failures)
        if result.gates_failed > result.total_gates * 0.5:
            penalties.append({
                'reason': 'More than 50% of gates failed',
                'amount': 10,
                'severity': 'high'
            })

        return penalties

    def _calculate_bonuses(self, result: Any) -> List[Dict[str, Any]]:
        """Calculate bonuses to be applied to score."""
        bonuses = []

        # Perfect score bonus
        if result.gates_failed == 0 and result.gates_warning == 0:
            bonuses.append({
                'reason': 'Perfect compliance - all gates passed',
                'amount': 5,
                'type': 'excellence'
            })

        # Zero critical issues bonus (if high total gates)
        if result.total_gates >= 10 and len(result.critical_issues) == 0:
            bonuses.append({
                'reason': 'No critical issues in comprehensive check',
                'amount': 3,
                'type': 'quality'
            })

        return bonuses

    def _calculate_gate_scores(self, result: Any) -> Dict[str, float]:
        """Calculate individual scores for each gate."""
        # This would require gate-level details from result
        # For now, return simplified version
        return {
            'passed_gates': result.gates_passed,
            'failed_gates': result.gates_failed,
            'warning_gates': result.gates_warning,
        }

    def _assign_grade(self, score: float) -> str:
        """Assign letter grade based on score."""
        for grade, threshold in self.grade_thresholds.items():
            if score >= threshold:
                return grade
        return 'F'

    def _calculate_trend(self, module_id: str, current_score: float) -> Dict[str, Any]:
        """Calculate score trend over time."""
        if module_id not in self.score_history:
            self.score_history[module_id] = []

        # Add current score to history
        self.score_history[module_id].append((datetime.now(), current_score))

        # Keep only last 30 days
        cutoff = datetime.now() - timedelta(days=30)
        self.score_history[module_id] = [
            (ts, score) for ts, score in self.score_history[module_id]
            if ts >= cutoff
        ]

        # Calculate trend
        history = self.score_history[module_id]
        if len(history) < 2:
            return {
                'trend': 'new',
                'change': 0.0,
                'velocity': 0.0,
                'previous_score': None
            }

        previous_score = history[-2][1]
        change = current_score - previous_score

        # Calculate velocity (change per day)
        time_diff = (history[-1][0] - history[-2][0]).days
        velocity = change / time_diff if time_diff > 0 else 0.0

        trend = 'stable'
        if change > 5:
            trend = 'improving'
        elif change < -5:
            trend = 'declining'

        return {
            'trend': trend,
            'change': round(change, 2),
            'velocity': round(velocity, 2),
            'previous_score': round(previous_score, 2),
            'data_points': len(history)
        }

    def _calculate_aggregate_scores(self, module_scores: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate aggregate scores across all modules."""
        if not module_scores:
            return {
                'overall_score': 0.0,
                'overall_grade': 'F',
                'average_score': 0.0,
                'median_score': 0.0,
                'best_module': None,
                'worst_module': None
            }

        scores = [s['score'] for s in module_scores.values()]
        average_score = sum(scores) / len(scores)

        sorted_scores = sorted(scores)
        median_score = sorted_scores[len(sorted_scores) // 2]

        # Overall score is weighted average (can be customized)
        overall_score = average_score

        # Find best and worst modules
        best_module = max(module_scores.items(), key=lambda x: x[1]['score'])
        worst_module = min(module_scores.items(), key=lambda x: x[1]['score'])

        return {
            'overall_score': round(overall_score, 2),
            'overall_grade': self._assign_grade(overall_score),
            'average_score': round(average_score, 2),
            'median_score': round(median_score, 2),
            'min_score': round(min(scores), 2),
            'max_score': round(max(scores), 2),
            'score_range': round(max(scores) - min(scores), 2),
            'best_module': {
                'module_id': best_module[0],
                'score': best_module[1]['score'],
                'grade': best_module[1]['grade']
            },
            'worst_module': {
                'module_id': worst_module[0],
                'score': worst_module[1]['score'],
                'grade': worst_module[1]['grade']
            }
        }

    def _generate_score_summary(
        self,
        module_scores: Dict[str, Any],
        aggregate: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate human-readable summary of scores."""
        # Count modules by grade
        grade_counts = {}
        for module_score in module_scores.values():
            grade = module_score['grade']
            grade_counts[grade] = grade_counts.get(grade, 0) + 1

        # Determine overall status
        overall_score = aggregate['overall_score']
        if overall_score >= 90:
            status = 'Excellent'
            message = 'Strong compliance posture across all modules'
        elif overall_score >= 80:
            status = 'Good'
            message = 'Solid compliance with room for improvement'
        elif overall_score >= 70:
            status = 'Fair'
            message = 'Meets minimum requirements but needs enhancement'
        elif overall_score >= 60:
            status = 'Poor'
            message = 'Significant compliance gaps requiring immediate attention'
        else:
            status = 'Critical'
            message = 'Urgent remediation required'

        return {
            'status': status,
            'message': message,
            'grade_distribution': grade_counts,
            'modules_above_90': sum(1 for s in module_scores.values() if s['score'] >= 90),
            'modules_below_70': sum(1 for s in module_scores.values() if s['score'] < 70),
            'improvement_priority': aggregate['worst_module']['module_id'] if aggregate['worst_module'] else None
        }

    def _generate_score_recommendations(
        self,
        breakdown: ScoreBreakdown,
        result: Any
    ) -> List[str]:
        """Generate recommendations based on score breakdown."""
        recommendations = []

        # Low gate pass rate
        if breakdown.component_scores['gate_pass_rate'] < 70:
            recommendations.append(
                f"Improve gate pass rate (currently {breakdown.component_scores['gate_pass_rate']:.1f}%). "
                f"Focus on fixing {result.gates_failed} failed gates."
            )

        # High severity issues
        if breakdown.component_scores['severity_adjusted'] < 70:
            recommendations.append(
                f"Address {len(result.critical_issues)} critical and {len(result.high_issues)} high severity issues."
            )

        # Low completeness
        if breakdown.component_scores['completeness'] < 80:
            recommendations.append(
                f"Improve completeness score. Review {result.gates_warning} warnings and ensure full implementation."
            )

        # Low best practices
        if breakdown.component_scores['best_practices'] < 70:
            recommendations.append(
                "Enhance compliance beyond minimum requirements. Consider additional safeguards and documentation."
            )

        # Grade-based recommendations
        if breakdown.total_score < 60:
            recommendations.append(
                "URGENT: Score is below 60%. This represents a critical compliance gap requiring immediate remediation."
            )
        elif breakdown.total_score < 80:
            recommendations.append(
                "Score below 80%. Prioritize addressing failed gates and high-severity issues to reach good standing."
            )

        return recommendations

    def _serialize_breakdown(self, breakdown: ScoreBreakdown) -> Dict[str, Any]:
        """Serialize score breakdown to dictionary."""
        return {
            'total_score': round(breakdown.total_score, 2),
            'grade': breakdown.grade,
            'components': {k: round(v, 2) for k, v in breakdown.component_scores.items()},
            'gate_scores': breakdown.gate_scores,
            'penalties': breakdown.penalties,
            'bonuses': breakdown.bonuses,
            'weights_used': self.weights
        }

    def get_score_comparison(
        self,
        module_scores: Dict[str, Any],
        benchmark_scores: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Compare scores against benchmarks."""
        if not benchmark_scores:
            # Use default industry benchmarks
            benchmark_scores = {
                'gdpr_uk': 85.0,
                'fca_uk': 82.0,
                'hipaa_us': 88.0,
                'pci_dss': 90.0,
                'sox_us': 87.0
            }

        comparisons = {}
        for module_id, score_data in module_scores.items():
            benchmark = benchmark_scores.get(module_id, 80.0)
            current = score_data['score']
            gap = current - benchmark

            comparisons[module_id] = {
                'current_score': current,
                'benchmark': benchmark,
                'gap': round(gap, 2),
                'status': 'above' if gap >= 0 else 'below',
                'percentage_of_benchmark': round((current / benchmark) * 100, 1)
            }

        return comparisons


# Testing
def test_scoring_engine():
    """Test scoring engine with sample results."""
    from backend.compliance.orchestrator import ComplianceResult
    from datetime import datetime

    engine = ScoringEngine()

    # Test case 1: High-performing module
    result1 = ComplianceResult(
        module_id='gdpr_uk',
        module_name='GDPR UK',
        timestamp=datetime.now(),
        overall_status='PASS',
        score=92,
        gates_passed=13,
        gates_failed=0,
        gates_warning=1,
        total_gates=14,
        critical_issues=[],
        high_issues=[],
        medium_issues=[{'issue': 'Minor documentation gap'}],
        recommendations=[],
        next_actions=[]
    )

    scores1 = engine.calculate_scores({'gdpr_uk': result1})
    assert scores1['module_scores']['gdpr_uk']['score'] >= 85
    assert scores1['module_scores']['gdpr_uk']['grade'] in ['A', 'A-', 'B+']
    print(" High-performing module test passed")

    # Test case 2: Poor-performing module
    result2 = ComplianceResult(
        module_id='fca_uk',
        module_name='FCA UK',
        timestamp=datetime.now(),
        overall_status='FAIL',
        score=45,
        gates_passed=4,
        gates_failed=6,
        gates_warning=2,
        total_gates=12,
        critical_issues=[
            {'issue': 'Missing FCA authorization'},
            {'issue': 'No SMCR regime'}
        ],
        high_issues=[{'issue': 'TCF not implemented'}],
        medium_issues=[],
        recommendations=[],
        next_actions=[]
    )

    scores2 = engine.calculate_scores({'fca_uk': result2})
    assert scores2['module_scores']['fca_uk']['score'] < 70
    assert scores2['module_scores']['fca_uk']['grade'] in ['D', 'F']
    print(" Poor-performing module test passed")

    # Test aggregate scores
    all_results = {'gdpr_uk': result1, 'fca_uk': result2}
    all_scores = engine.calculate_scores(all_results)
    assert 'aggregate' in all_scores
    assert 'overall_score' in all_scores['aggregate']
    print(" Aggregate scores test passed")

    print("\nAll scoring engine tests passed!")
    return True


if __name__ == "__main__":
    test_scoring_engine()
