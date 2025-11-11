"""
Risk Heatmap Generator - Creates visual risk assessments across compliance modules
Generates heatmaps showing risk levels, priorities, and areas requiring attention.
"""

from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class RiskHeatmapGenerator:
    """
    Compliance risk heatmap visualization system.
    
    Features:
    - Risk level assessment
    - Multi-dimensional risk analysis
    - Visual heatmap data generation
    - Priority quadrant analysis
    - Risk trend tracking
    """
    
    def __init__(self):
        self._initialize_risk_matrix()
    
    def _initialize_risk_matrix(self):
        """Initialize risk assessment matrix."""
        # Risk levels: (likelihood, impact) -> risk_score
        self.risk_matrix = {
            (5, 5): 25, (5, 4): 20, (5, 3): 15, (5, 2): 10, (5, 1): 5,
            (4, 5): 20, (4, 4): 16, (4, 3): 12, (4, 2): 8,  (4, 1): 4,
            (3, 5): 15, (3, 4): 12, (3, 3): 9,  (3, 2): 6,  (3, 1): 3,
            (2, 5): 10, (2, 4): 8,  (2, 3): 6,  (2, 2): 4,  (2, 1): 2,
            (1, 5): 5,  (1, 4): 4,  (1, 3): 3,  (1, 2): 2,  (1, 1): 1
        }
        
        # Risk categories
        self.risk_categories = {
            'critical': (20, 25),
            'high': (12, 19),
            'medium': (6, 11),
            'low': (1, 5)
        }
    
    def generate(self, module_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive risk heatmap.
        
        Args:
            module_results: Compliance results for all modules
        
        Returns:
            Heatmap data with risk assessments and visualizations
        """
        logger.info("Generating compliance risk heatmap")
        
        # Calculate risk scores for each module
        module_risks = {}
        for module_id, result in module_results.items():
            risk_assessment = self._assess_module_risk(module_id, result)
            module_risks[module_id] = risk_assessment
        
        # Generate heatmap matrix
        heatmap_matrix = self._generate_heatmap_matrix(module_risks)
        
        # Generate quadrant analysis
        quadrants = self._analyze_quadrants(module_risks)
        
        # Identify hotspots
        hotspots = self._identify_hotspots(module_risks)
        
        # Generate risk trends
        trends = self._analyze_risk_trends(module_risks)
        
        # Create visualization data
        visualization_data = self._create_visualization_data(module_risks)
        
        return {
            'timestamp': module_results.get('timestamp', 'unknown'),
            'module_risks': module_risks,
            'heatmap_matrix': heatmap_matrix,
            'quadrant_analysis': quadrants,
            'risk_hotspots': hotspots,
            'risk_trends': trends,
            'visualization_data': visualization_data,
            'overall_risk_level': self._calculate_overall_risk(module_risks),
            'recommendations': self._generate_risk_recommendations(module_risks)
        }
    
    def _assess_module_risk(self, module_id: str, result: Any) -> Dict[str, Any]:
        """Assess risk for a single module."""
        # Calculate likelihood (1-5) based on current failures
        if not hasattr(result, 'gates_failed') or result.total_gates == 0:
            likelihood = 1
        else:
            failure_rate = result.gates_failed / result.total_gates
            if failure_rate >= 0.5:
                likelihood = 5  # Very likely
            elif failure_rate >= 0.3:
                likelihood = 4  # Likely
            elif failure_rate >= 0.15:
                likelihood = 3  # Possible
            elif failure_rate >= 0.05:
                likelihood = 2  # Unlikely
            else:
                likelihood = 1  # Very unlikely
        
        # Calculate impact (1-5) based on severity of issues
        if not hasattr(result, 'critical_issues'):
            impact = 1
        else:
            if len(result.critical_issues) > 3:
                impact = 5  # Catastrophic
            elif len(result.critical_issues) > 0:
                impact = 4  # Major
            elif len(result.high_issues) > 3:
                impact = 3  # Moderate
            elif len(result.high_issues) > 0:
                impact = 2  # Minor
            else:
                impact = 1  # Negligible
        
        # Calculate risk score
        risk_score = self.risk_matrix.get((likelihood, impact), 9)
        
        # Determine risk level
        risk_level = self._get_risk_level(risk_score)
        
        # Calculate residual risk (after current controls)
        residual_likelihood = max(1, likelihood - 1)
        residual_impact = max(1, impact - 1)
        residual_score = self.risk_matrix.get((residual_likelihood, residual_impact), 4)
        
        return {
            'module_id': module_id,
            'module_name': result.module_name if hasattr(result, 'module_name') else module_id,
            'likelihood': likelihood,
            'impact': impact,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'residual_risk_score': residual_score,
            'compliance_score': result.score if hasattr(result, 'score') else 0,
            'critical_issues': len(result.critical_issues) if hasattr(result, 'critical_issues') else 0,
            'high_issues': len(result.high_issues) if hasattr(result, 'high_issues') else 0,
            'gates_failed': result.gates_failed if hasattr(result, 'gates_failed') else 0,
            'coordinates': {
                'x': impact,
                'y': likelihood
            }
        }
    
    def _get_risk_level(self, risk_score: int) -> str:
        """Get risk level from score."""
        for level, (min_score, max_score) in self.risk_categories.items():
            if min_score <= risk_score <= max_score:
                return level
        return 'low'
    
    def _generate_heatmap_matrix(self, module_risks: Dict[str, Any]) -> List[List[Any]]:
        """Generate 5x5 heatmap matrix."""
        # Initialize 5x5 matrix
        matrix = [[[] for _ in range(5)] for _ in range(5)]
        
        # Place modules in matrix
        for module_id, risk in module_risks.items():
            x = risk['impact'] - 1  # Convert to 0-indexed
            y = risk['likelihood'] - 1
            
            matrix[y][x].append({
                'module_id': module_id,
                'module_name': risk['module_name'],
                'risk_score': risk['risk_score'],
                'risk_level': risk['risk_level']
            })
        
        return matrix
    
    def _analyze_quadrants(self, module_risks: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze risk distribution across quadrants."""
        quadrants = {
            'high_likelihood_high_impact': [],  # Top-right: Critical
            'high_likelihood_low_impact': [],   # Top-left: Monitor
            'low_likelihood_high_impact': [],   # Bottom-right: Mitigate
            'low_likelihood_low_impact': []     # Bottom-left: Accept
        }
        
        for module_id, risk in module_risks.items():
            likelihood = risk['likelihood']
            impact = risk['impact']
            
            if likelihood >= 4 and impact >= 4:
                quadrants['high_likelihood_high_impact'].append({
                    'module_id': module_id,
                    'module_name': risk['module_name'],
                    'risk_score': risk['risk_score']
                })
            elif likelihood >= 4 and impact < 4:
                quadrants['high_likelihood_low_impact'].append({
                    'module_id': module_id,
                    'module_name': risk['module_name'],
                    'risk_score': risk['risk_score']
                })
            elif likelihood < 4 and impact >= 4:
                quadrants['low_likelihood_high_impact'].append({
                    'module_id': module_id,
                    'module_name': risk['module_name'],
                    'risk_score': risk['risk_score']
                })
            else:
                quadrants['low_likelihood_low_impact'].append({
                    'module_id': module_id,
                    'module_name': risk['module_name'],
                    'risk_score': risk['risk_score']
                })
        
        return {
            'critical_action_required': quadrants['high_likelihood_high_impact'],
            'monitor_closely': quadrants['high_likelihood_low_impact'],
            'mitigate_impact': quadrants['low_likelihood_high_impact'],
            'acceptable_risk': quadrants['low_likelihood_low_impact'],
            'summary': {
                'critical': len(quadrants['high_likelihood_high_impact']),
                'monitor': len(quadrants['high_likelihood_low_impact']),
                'mitigate': len(quadrants['low_likelihood_high_impact']),
                'acceptable': len(quadrants['low_likelihood_low_impact'])
            }
        }
    
    def _identify_hotspots(self, module_risks: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify risk hotspots requiring immediate attention."""
        hotspots = []
        
        for module_id, risk in module_risks.items():
            if risk['risk_level'] in ['critical', 'high']:
                hotspot = {
                    'module_id': module_id,
                    'module_name': risk['module_name'],
                    'risk_level': risk['risk_level'],
                    'risk_score': risk['risk_score'],
                    'likelihood': risk['likelihood'],
                    'impact': risk['impact'],
                    'critical_issues': risk['critical_issues'],
                    'urgency': 'immediate' if risk['risk_level'] == 'critical' else 'high',
                    'recommended_action': self._get_hotspot_action(risk)
                }
                hotspots.append(hotspot)
        
        # Sort by risk score (highest first)
        hotspots.sort(key=lambda x: x['risk_score'], reverse=True)
        
        return hotspots
    
    def _get_hotspot_action(self, risk: Dict[str, Any]) -> str:
        """Get recommended action for a hotspot."""
        if risk['risk_level'] == 'critical':
            return f"URGENT: Address {risk['critical_issues']} critical issues immediately. Allocate dedicated resources."
        elif risk['likelihood'] >= 4:
            return f"HIGH: Implement controls to reduce likelihood. Review {risk['gates_failed']} failed gates."
        elif risk['impact'] >= 4:
            return "HIGH: Implement safeguards to reduce potential impact. Enhance monitoring."
        else:
            return "MEDIUM: Schedule remediation in next sprint. Monitor closely."
    
    def _analyze_risk_trends(self, module_risks: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze risk trends (simplified - would need historical data)."""
        # In a real implementation, this would compare against historical data
        # For now, provide current state analysis
        
        risk_distribution = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        }
        
        for risk in module_risks.values():
            risk_distribution[risk['risk_level']] += 1
        
        return {
            'current_distribution': risk_distribution,
            'total_modules': len(module_risks),
            'high_risk_percentage': round(
                (risk_distribution['critical'] + risk_distribution['high']) / len(module_risks) * 100, 1
            ) if module_risks else 0,
            'trend': 'stable',  # Would be calculated from historical data
            'recommendation': self._get_trend_recommendation(risk_distribution, len(module_risks))
        }
    
    def _get_trend_recommendation(self, distribution: Dict[str, int], total: int) -> str:
        """Get recommendation based on risk distribution."""
        high_risk_count = distribution['critical'] + distribution['high']
        high_risk_pct = (high_risk_count / total * 100) if total > 0 else 0
        
        if high_risk_pct > 50:
            return "CRITICAL: Over 50% of modules in high-risk category. Immediate intervention required."
        elif high_risk_pct > 30:
            return "CONCERN: Significant high-risk exposure. Accelerate remediation efforts."
        elif high_risk_pct > 15:
            return "ATTENTION: Moderate risk levels. Continue systematic remediation."
        else:
            return "GOOD: Most risks under control. Maintain current approach."
    
    def _create_visualization_data(self, module_risks: Dict[str, Any]) -> Dict[str, Any]:
        """Create data formatted for visualization tools."""
        # Data for scatter plot
        scatter_data = []
        for module_id, risk in module_risks.items():
            scatter_data.append({
                'id': module_id,
                'name': risk['module_name'],
                'x': risk['impact'],
                'y': risk['likelihood'],
                'z': risk['risk_score'],
                'size': risk['risk_score'] * 2,
                'color': self._get_color_for_risk_level(risk['risk_level']),
                'label': f"{risk['module_name']} ({risk['risk_score']})"
            })
        
        # Data for bar chart (risk by module)
        bar_data = [
            {
                'module': risk['module_name'],
                'risk_score': risk['risk_score'],
                'color': self._get_color_for_risk_level(risk['risk_level'])
            }
            for risk in sorted(module_risks.values(), key=lambda x: x['risk_score'], reverse=True)
        ]
        
        # Data for pie chart (risk distribution)
        risk_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for risk in module_risks.values():
            risk_counts[risk['risk_level']] += 1
        
        pie_data = [
            {'category': level, 'count': count, 'color': self._get_color_for_risk_level(level)}
            for level, count in risk_counts.items()
            if count > 0
        ]
        
        return {
            'scatter_plot': scatter_data,
            'bar_chart': bar_data,
            'pie_chart': pie_data,
            'heatmap_config': {
                'x_axis': {'label': 'Impact', 'range': [1, 5]},
                'y_axis': {'label': 'Likelihood', 'range': [1, 5]},
                'color_scale': {
                    'critical': '#DC2626',
                    'high': '#F59E0B',
                    'medium': '#FCD34D',
                    'low': '#10B981'
                }
            }
        }
    
    def _get_color_for_risk_level(self, risk_level: str) -> str:
        """Get color code for risk level."""
        colors = {
            'critical': '#DC2626',  # Red
            'high': '#F59E0B',      # Amber
            'medium': '#FCD34D',    # Yellow
            'low': '#10B981'        # Green
        }
        return colors.get(risk_level, '#6B7280')
    
    def _calculate_overall_risk(self, module_risks: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall organizational risk level."""
        if not module_risks:
            return {'level': 'low', 'score': 0}
        
        avg_risk_score = sum(r['risk_score'] for r in module_risks.values()) / len(module_risks)
        max_risk_score = max(r['risk_score'] for r in module_risks.values())
        
        overall_level = self._get_risk_level(int(avg_risk_score))
        
        return {
            'level': overall_level,
            'average_risk_score': round(avg_risk_score, 2),
            'maximum_risk_score': max_risk_score,
            'risk_exposure': 'high' if max_risk_score >= 20 else 'medium' if max_risk_score >= 12 else 'low',
            'status': self._get_overall_status(overall_level, max_risk_score)
        }
    
    def _get_overall_status(self, avg_level: str, max_score: int) -> str:
        """Get overall risk status message."""
        if avg_level == 'critical' or max_score >= 20:
            return "CRITICAL: Immediate executive attention required"
        elif avg_level == 'high' or max_score >= 15:
            return "HIGH: Accelerated remediation program needed"
        elif avg_level == 'medium':
            return "MODERATE: Continue systematic risk reduction"
        else:
            return "LOW: Maintain current controls and monitoring"
    
    def _generate_risk_recommendations(self, module_risks: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on risk heatmap."""
        recommendations = []
        
        # Count by risk level
        critical_count = sum(1 for r in module_risks.values() if r['risk_level'] == 'critical')
        high_count = sum(1 for r in module_risks.values() if r['risk_level'] == 'high')
        
        if critical_count > 0:
            recommendations.append(
                f"CRITICAL: {critical_count} modules at critical risk level. Establish incident response team."
            )
        
        if high_count > 2:
            recommendations.append(
                f"HIGH: {high_count} modules at high risk. Prioritize remediation in next 30 days."
            )
        
        # Identify concentration risks
        high_impact_modules = [r for r in module_risks.values() if r['impact'] >= 4]
        if len(high_impact_modules) > 3:
            recommendations.append(
                "CONCENTRATION: Multiple high-impact modules. Consider enterprise risk assessment."
            )
        
        recommendations.extend([
            "Establish monthly risk review cadence",
            "Implement automated risk monitoring and alerting",
            "Document risk appetite and tolerance levels",
            "Regular testing of controls effectiveness"
        ])
        
        return recommendations
