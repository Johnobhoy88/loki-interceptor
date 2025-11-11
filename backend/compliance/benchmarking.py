"""
Benchmarking Engine - Compares compliance scores against industry standards
Provides industry benchmarks, peer comparisons, and best-in-class targets.
"""

from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BenchmarkingEngine:
    """
    Compliance benchmarking and comparison system.
    
    Features:
    - Industry standard benchmarks
    - Peer group comparisons
    - Best-in-class targets
    - Gap analysis
    - Percentile rankings
    """
    
    def __init__(self):
        self._initialize_benchmarks()
    
    def _initialize_benchmarks(self):
        """Initialize industry benchmark data."""
        # Industry average scores by module
        self.industry_benchmarks = {
            'gdpr_uk': {
                'average': 78.5,
                'best_in_class': 95.0,
                'minimum_acceptable': 70.0,
                'median': 80.0
            },
            'gdpr_advanced': {
                'average': 72.0,
                'best_in_class': 92.0,
                'minimum_acceptable': 65.0,
                'median': 75.0
            },
            'fca_uk': {
                'average': 81.0,
                'best_in_class': 96.0,
                'minimum_acceptable': 75.0,
                'median': 82.0
            },
            'fca_advanced': {
                'average': 76.5,
                'best_in_class': 94.0,
                'minimum_acceptable': 70.0,
                'median': 78.0
            },
            'hipaa_us': {
                'average': 83.0,
                'best_in_class': 97.0,
                'minimum_acceptable': 80.0,
                'median': 85.0
            },
            'sox_us': {
                'average': 85.0,
                'best_in_class': 98.0,
                'minimum_acceptable': 82.0,
                'median': 86.0
            },
            'pci_dss': {
                'average': 88.0,
                'best_in_class': 99.0,
                'minimum_acceptable': 85.0,
                'median': 89.0
            },
            'nda_uk': {
                'average': 82.0,
                'best_in_class': 95.0,
                'minimum_acceptable': 75.0,
                'median': 83.0
            },
            'tax_uk': {
                'average': 79.0,
                'best_in_class': 94.0,
                'minimum_acceptable': 72.0,
                'median': 80.0
            },
            'uk_employment': {
                'average': 77.0,
                'best_in_class': 93.0,
                'minimum_acceptable': 70.0,
                'median': 78.0
            }
        }
        
        # Industry-specific adjustments
        self.industry_adjustments = {
            'financial_services': 1.05,  # Higher expectations
            'healthcare': 1.08,  # Very high expectations
            'technology': 1.0,  # Standard
            'retail': 0.95,  # Slightly lower
            'manufacturing': 0.93,  # Lower
            'education': 0.98  # Slightly lower
        }
    
    def benchmark(
        self,
        scores: Dict[str, Any],
        organization_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Benchmark compliance scores against industry standards.
        
        Args:
            scores: Compliance scores from scoring engine
            organization_profile: Optional organization profile
        
        Returns:
            Benchmark comparison report
        """
        logger.info("Benchmarking compliance scores")
        
        industry = organization_profile.get('industry', 'technology') if organization_profile else 'technology'
        org_size = organization_profile.get('size', 'medium') if organization_profile else 'medium'
        
        # Get industry adjustment factor
        adjustment = self.industry_adjustments.get(industry, 1.0)
        
        module_comparisons = {}
        for module_id, score_data in scores.get('module_scores', {}).items():
            comparison = self._compare_module(
                module_id,
                score_data['score'],
                adjustment
            )
            module_comparisons[module_id] = comparison
        
        # Calculate aggregate comparison
        aggregate_comparison = self._calculate_aggregate_comparison(
            module_comparisons,
            scores.get('aggregate', {})
        )
        
        # Generate improvement targets
        targets = self._generate_targets(module_comparisons, adjustment)
        
        return {
            'timestamp': scores.get('timestamp'),
            'industry': industry,
            'industry_adjustment': adjustment,
            'organization_size': org_size,
            'module_comparisons': module_comparisons,
            'aggregate_comparison': aggregate_comparison,
            'improvement_targets': targets,
            'ranking': self._calculate_ranking(aggregate_comparison),
            'recommendations': self._generate_benchmark_recommendations(
                module_comparisons,
                industry
            )
        }
    
    def _compare_module(
        self,
        module_id: str,
        actual_score: float,
        industry_adjustment: float
    ) -> Dict[str, Any]:
        """Compare module score against benchmarks."""
        benchmarks = self.industry_benchmarks.get(module_id, {
            'average': 75.0,
            'best_in_class': 90.0,
            'minimum_acceptable': 65.0,
            'median': 77.0
        })
        
        # Apply industry adjustment to benchmarks
        adjusted_avg = benchmarks['average'] * industry_adjustment
        adjusted_bic = benchmarks['best_in_class'] * industry_adjustment
        adjusted_min = benchmarks['minimum_acceptable'] * industry_adjustment
        
        # Calculate gaps
        gap_to_avg = actual_score - adjusted_avg
        gap_to_bic = actual_score - adjusted_bic
        gap_to_min = actual_score - adjusted_min
        
        # Determine percentile (simplified)
        if actual_score >= adjusted_bic:
            percentile = 95
        elif actual_score >= adjusted_avg + 10:
            percentile = 80
        elif actual_score >= adjusted_avg:
            percentile = 60
        elif actual_score >= adjusted_min:
            percentile = 40
        else:
            percentile = 20
        
        # Determine status
        if actual_score >= adjusted_bic:
            status = 'Best-in-Class'
        elif actual_score >= adjusted_avg:
            status = 'Above Average'
        elif actual_score >= adjusted_min:
            status = 'Below Average'
        else:
            status = 'Below Minimum'
        
        return {
            'actual_score': round(actual_score, 2),
            'industry_average': round(adjusted_avg, 2),
            'best_in_class': round(adjusted_bic, 2),
            'minimum_acceptable': round(adjusted_min, 2),
            'median': round(benchmarks['median'] * industry_adjustment, 2),
            'gap_to_average': round(gap_to_avg, 2),
            'gap_to_best_in_class': round(gap_to_bic, 2),
            'gap_to_minimum': round(gap_to_min, 2),
            'percentile': percentile,
            'status': status,
            'meets_minimum': actual_score >= adjusted_min
        }
    
    def _calculate_aggregate_comparison(
        self,
        module_comparisons: Dict[str, Any],
        aggregate_scores: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate aggregate benchmark comparison."""
        if not module_comparisons:
            return {}
        
        avg_percentile = sum(c['percentile'] for c in module_comparisons.values()) / len(module_comparisons)
        modules_above_avg = sum(1 for c in module_comparisons.values() if c['status'] == 'Above Average' or c['status'] == 'Best-in-Class')
        modules_bic = sum(1 for c in module_comparisons.values() if c['status'] == 'Best-in-Class')
        modules_below_min = sum(1 for c in module_comparisons.values() if not c['meets_minimum'])
        
        overall_status = 'Average'
        if avg_percentile >= 80:
            overall_status = 'Excellent - Above Industry Average'
        elif avg_percentile >= 60:
            overall_status = 'Good - Meeting Industry Standards'
        elif avg_percentile >= 40:
            overall_status = 'Fair - Below Industry Average'
        else:
            overall_status = 'Poor - Significant Gaps'
        
        return {
            'average_percentile': round(avg_percentile, 1),
            'overall_status': overall_status,
            'modules_above_average': modules_above_avg,
            'modules_best_in_class': modules_bic,
            'modules_below_minimum': modules_below_min,
            'total_modules': len(module_comparisons)
        }
    
    def _generate_targets(
        self,
        module_comparisons: Dict[str, Any],
        industry_adjustment: float
    ) -> Dict[str, Any]:
        """Generate improvement targets."""
        targets = {}
        
        for module_id, comparison in module_comparisons.items():
            if comparison['gap_to_average'] < 0:
                # Below average - target is industry average
                target = comparison['industry_average']
                target_type = 'Reach Industry Average'
                priority = 'high'
            elif comparison['gap_to_best_in_class'] < 0:
                # Above average but not best-in-class - target is BIC
                target = comparison['best_in_class']
                target_type = 'Reach Best-in-Class'
                priority = 'medium'
            else:
                # Already best-in-class - maintain
                target = comparison['actual_score']
                target_type = 'Maintain Excellence'
                priority = 'low'
            
            targets[module_id] = {
                'current_score': comparison['actual_score'],
                'target_score': target,
                'improvement_needed': round(target - comparison['actual_score'], 2),
                'target_type': target_type,
                'priority': priority,
                'estimated_effort': self._estimate_effort(target - comparison['actual_score'])
            }
        
        return targets
    
    def _estimate_effort(self, score_gap: float) -> str:
        """Estimate effort required to close score gap."""
        if score_gap <= 0:
            return 'Maintenance only'
        elif score_gap < 5:
            return '1-2 weeks'
        elif score_gap < 10:
            return '1-2 months'
        elif score_gap < 20:
            return '3-4 months'
        else:
            return '6+ months'
    
    def _calculate_ranking(self, aggregate_comparison: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall ranking."""
        percentile = aggregate_comparison.get('average_percentile', 50)
        
        if percentile >= 95:
            rank = 'Top 5%'
            description = 'Excellence - Industry Leader'
        elif percentile >= 80:
            rank = 'Top 20%'
            description = 'Strong Performance'
        elif percentile >= 60:
            rank = 'Top 40%'
            description = 'Above Average'
        elif percentile >= 40:
            rank = 'Middle 40%'
            description = 'Average Performance'
        else:
            rank = 'Bottom 40%'
            description = 'Needs Improvement'
        
        return {
            'rank': rank,
            'description': description,
            'percentile': percentile
        }
    
    def _generate_benchmark_recommendations(
        self,
        module_comparisons: Dict[str, Any],
        industry: str
    ) -> List[str]:
        """Generate recommendations based on benchmark comparison."""
        recommendations = []
        
        # Find modules below minimum
        below_min = [m for m, c in module_comparisons.items() if not c['meets_minimum']]
        if below_min:
            recommendations.append(
                f"CRITICAL: {len(below_min)} modules below industry minimum. Immediate action required: {', '.join(below_min)}"
            )
        
        # Find modules significantly below average
        below_avg = [m for m, c in module_comparisons.items() if c['gap_to_average'] < -10]
        if below_avg:
            recommendations.append(
                f"HIGH PRIORITY: {len(below_avg)} modules significantly below industry average: {', '.join(below_avg)}"
            )
        
        # Industry-specific recommendations
        if industry == 'financial_services':
            recommendations.append(
                "Financial services: Maintain scores above 85 for regulatory modules (FCA, GDPR)"
            )
        elif industry == 'healthcare':
            recommendations.append(
                "Healthcare: Prioritize data protection and patient safety modules (GDPR, Healthcare)"
            )
        
        # Best practices
        recommendations.append(
            "Benchmark against industry leaders quarterly to maintain competitive compliance posture"
        )
        
        return recommendations
