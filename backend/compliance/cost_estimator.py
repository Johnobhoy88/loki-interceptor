"""
Cost Estimator - Estimates compliance implementation and maintenance costs
Provides cost analysis, ROI calculations, and budget planning.
"""

from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class CostEstimator:
    """
    Compliance cost estimation and analysis system.
    
    Features:
    - Implementation cost estimation
    - Ongoing maintenance costs
    - Resource cost calculations
    - ROI analysis
    - Budget planning
    """
    
    def __init__(self, modules: Dict[str, Any]):
        self.modules = modules
        self._initialize_cost_factors()
    
    def _initialize_cost_factors(self):
        """Initialize cost factors and rates."""
        # Daily rates by role (in GBP)
        self.daily_rates = {
            'Compliance Officer': 600,
            'Legal Counsel': 1200,
            'IT Security Specialist': 700,
            'DPO (Data Protection Officer)': 800,
            'External Auditor': 1000,
            'External Consultant': 1500,
            'Technical Developer': 650,
            'Training Specialist': 500,
            'Project Manager': 700
        }
        
        # Module-specific cost factors
        self.module_costs = {
            'gdpr_uk': {
                'software_tools': 5000,
                'training_per_employee': 150,
                'annual_maintenance': 12000
            },
            'gdpr_advanced': {
                'software_tools': 15000,
                'training_per_employee': 300,
                'annual_maintenance': 20000
            },
            'fca_uk': {
                'software_tools': 25000,
                'training_per_employee': 500,
                'annual_maintenance': 40000
            },
            'fca_advanced': {
                'software_tools': 40000,
                'training_per_employee': 750,
                'annual_maintenance': 60000
            },
            'pci_dss': {
                'software_tools': 20000,
                'training_per_employee': 400,
                'annual_maintenance': 30000
            },
            'sox_us': {
                'software_tools': 50000,
                'training_per_employee': 600,
                'annual_maintenance': 75000
            },
            'hipaa_us': {
                'software_tools': 30000,
                'training_per_employee': 500,
                'annual_maintenance': 45000
            }
        }
    
    def estimate(
        self,
        module_results: Dict[str, Any],
        roadmap: Dict[str, Any],
        organization_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Estimate total compliance costs.
        
        Args:
            module_results: Compliance results for all modules
            roadmap: Implementation roadmap
            organization_profile: Organization profile with size, employee count, etc.
        
        Returns:
            Comprehensive cost estimate with breakdown
        """
        logger.info("Estimating compliance costs")
        
        # Extract organization details
        org_size = organization_profile.get('size', 'medium') if organization_profile else 'medium'
        employee_count = organization_profile.get('employee_count', 50) if organization_profile else 50
        
        # Calculate implementation costs
        implementation_costs = self._calculate_implementation_costs(
            module_results,
            roadmap,
            org_size
        )
        
        # Calculate ongoing costs
        ongoing_costs = self._calculate_ongoing_costs(
            module_results,
            employee_count
        )
        
        # Calculate remediation costs
        remediation_costs = self._calculate_remediation_costs(module_results)
        
        # Calculate training costs
        training_costs = self._calculate_training_costs(
            module_results,
            employee_count
        )
        
        # Calculate tooling costs
        tooling_costs = self._calculate_tooling_costs(module_results)
        
        # Calculate external costs
        external_costs = self._calculate_external_costs(
            module_results,
            org_size
        )
        
        # Total costs
        year_one_total = (
            implementation_costs['total'] +
            remediation_costs['total'] +
            training_costs['total'] +
            tooling_costs['one_time'] +
            external_costs['year_one'] +
            ongoing_costs['annual'] / 2  # Half year of ongoing costs
        )
        
        year_two_plus_annual = (
            ongoing_costs['annual'] +
            tooling_costs['annual'] +
            external_costs['annual']
        )
        
        # Calculate ROI
        roi = self._calculate_roi(year_one_total, module_results)
        
        return {
            'currency': 'GBP',
            'organization_size': org_size,
            'employee_count': employee_count,
            'cost_breakdown': {
                'implementation': implementation_costs,
                'remediation': remediation_costs,
                'training': training_costs,
                'tooling': tooling_costs,
                'external_services': external_costs,
                'ongoing_operations': ongoing_costs
            },
            'summary': {
                'year_one_total': round(year_one_total, 2),
                'year_two_plus_annual': round(year_two_plus_annual, 2),
                'three_year_total': round(year_one_total + (year_two_plus_annual * 2), 2),
                'five_year_total': round(year_one_total + (year_two_plus_annual * 4), 2)
            },
            'roi_analysis': roi,
            'cost_per_module': self._calculate_per_module_costs(module_results, employee_count),
            'recommendations': self._generate_cost_recommendations(
                year_one_total,
                org_size,
                module_results
            )
        }
    
    def _calculate_implementation_costs(
        self,
        module_results: Dict[str, Any],
        roadmap: Dict[str, Any],
        org_size: str
    ) -> Dict[str, Any]:
        """Calculate implementation costs from roadmap."""
        if not roadmap.get('phases'):
            return {'total': 0, 'details': []}
        
        phase_costs = []
        total = 0
        
        for phase in roadmap['phases']:
            phase_cost = phase.get('estimated_cost', 0)
            phase_costs.append({
                'phase': phase['name'],
                'cost': phase_cost
            })
            total += phase_cost
        
        # Adjust for organization size
        size_multiplier = {'small': 0.7, 'medium': 1.0, 'large': 1.3, 'enterprise': 1.8}.get(org_size, 1.0)
        adjusted_total = total * size_multiplier
        
        return {
            'total': adjusted_total,
            'by_phase': phase_costs,
            'size_adjustment': size_multiplier
        }
    
    def _calculate_ongoing_costs(
        self,
        module_results: Dict[str, Any],
        employee_count: int
    ) -> Dict[str, Any]:
        """Calculate ongoing operational costs."""
        annual_costs = []
        total = 0
        
        for module_id in module_results.keys():
            module_cost = self.module_costs.get(module_id, {}).get('annual_maintenance', 5000)
            annual_costs.append({
                'module': module_id,
                'cost': module_cost
            })
            total += module_cost
        
        # Add staffing costs (0.1 FTE per module)
        compliance_officer_days = len(module_results) * 25  # 25 days per module per year
        staffing_cost = compliance_officer_days * self.daily_rates['Compliance Officer']
        
        total += staffing_cost
        
        return {
            'annual': round(total, 2),
            'monthly': round(total / 12, 2),
            'by_module': annual_costs,
            'staffing_cost': round(staffing_cost, 2),
            'staffing_days': compliance_officer_days
        }
    
    def _calculate_remediation_costs(self, module_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate costs to remediate current issues."""
        remediation_costs = []
        total = 0
        
        for module_id, result in module_results.items():
            if not hasattr(result, 'critical_issues'):
                continue
            
            # Estimate hours based on issues
            critical_hours = len(result.critical_issues) * 16  # 2 days per critical issue
            high_hours = len(result.high_issues) * 8  # 1 day per high issue
            medium_hours = len(result.medium_issues) * 4  # 0.5 days per medium issue
            
            total_hours = critical_hours + high_hours + medium_hours
            
            # Calculate cost (mix of internal and external)
            internal_cost = (total_hours / 8) * self.daily_rates['Compliance Officer']
            external_cost = (total_hours / 8) * 0.3 * self.daily_rates['External Consultant']  # 30% external
            
            module_cost = internal_cost + external_cost
            
            remediation_costs.append({
                'module': module_id,
                'critical_issues': len(result.critical_issues),
                'high_issues': len(result.high_issues),
                'medium_issues': len(result.medium_issues),
                'estimated_hours': total_hours,
                'cost': round(module_cost, 2)
            })
            
            total += module_cost
        
        return {
            'total': round(total, 2),
            'by_module': remediation_costs
        }
    
    def _calculate_training_costs(
        self,
        module_results: Dict[str, Any],
        employee_count: int
    ) -> Dict[str, Any]:
        """Calculate training costs."""
        training_costs = []
        total = 0
        
        for module_id in module_results.keys():
            cost_per_employee = self.module_costs.get(module_id, {}).get('training_per_employee', 100)
            module_total = cost_per_employee * employee_count
            
            training_costs.append({
                'module': module_id,
                'cost_per_employee': cost_per_employee,
                'total_cost': module_total
            })
            
            total += module_total
        
        # Add training development costs
        development_cost = len(module_results) * 5000  # £5k per module to develop training
        
        return {
            'total': round(total + development_cost, 2),
            'employee_training': round(total, 2),
            'development': development_cost,
            'by_module': training_costs,
            'employees_trained': employee_count
        }
    
    def _calculate_tooling_costs(self, module_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate software and tooling costs."""
        one_time = 0
        annual = 0
        
        tools = []
        
        for module_id in module_results.keys():
            tool_cost = self.module_costs.get(module_id, {}).get('software_tools', 3000)
            one_time += tool_cost
            
            # Annual license/maintenance (typically 20% of initial cost)
            annual_cost = tool_cost * 0.2
            annual += annual_cost
            
            tools.append({
                'module': module_id,
                'one_time': tool_cost,
                'annual': annual_cost
            })
        
        return {
            'one_time': round(one_time, 2),
            'annual': round(annual, 2),
            'by_module': tools
        }
    
    def _calculate_external_costs(
        self,
        module_results: Dict[str, Any],
        org_size: str
    ) -> Dict[str, Any]:
        """Calculate external consultant and auditor costs."""
        # Year one: Heavy external support
        consultant_days = len(module_results) * 10  # 10 days per module
        auditor_days = 5  # Initial assessment
        
        year_one = (
            consultant_days * self.daily_rates['External Consultant'] +
            auditor_days * self.daily_rates['External Auditor']
        )
        
        # Ongoing: Annual audits only
        annual = 3 * self.daily_rates['External Auditor']  # 3 days annual audit
        
        return {
            'year_one': round(year_one, 2),
            'annual': round(annual, 2),
            'consultant_days_year_one': consultant_days,
            'annual_audit_days': 3
        }
    
    def _calculate_per_module_costs(
        self,
        module_results: Dict[str, Any],
        employee_count: int
    ) -> Dict[str, Any]:
        """Calculate costs per module."""
        per_module = {}
        
        for module_id in module_results.keys():
            module_info = self.module_costs.get(module_id, {})
            
            implementation = self.modules[module_id].implementation_time_days * self.daily_rates['Compliance Officer'] if module_id in self.modules else 10000
            training = module_info.get('training_per_employee', 100) * employee_count
            tooling = module_info.get('software_tools', 3000)
            annual_maintenance = module_info.get('annual_maintenance', 5000)
            
            total_year_one = implementation + training + tooling + annual_maintenance
            
            per_module[module_id] = {
                'implementation': round(implementation, 2),
                'training': round(training, 2),
                'tooling': round(tooling, 2),
                'annual_maintenance': round(annual_maintenance, 2),
                'total_year_one': round(total_year_one, 2)
            }
        
        return per_module
    
    def _calculate_roi(self, total_cost: float, module_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate return on investment."""
        # Estimated benefits
        # 1. Avoided fines
        avg_fine_risk = 100000  # Average potential fine
        fine_probability_without = 0.3  # 30% chance without compliance
        fine_probability_with = 0.05  # 5% chance with compliance
        avoided_fine_value = avg_fine_risk * (fine_probability_without - fine_probability_with)
        
        # 2. Efficiency gains
        efficiency_value = len(module_results) * 20000  # £20k per module in efficiency
        
        # 3. Reputation/brand value
        reputation_value = 50000
        
        total_benefits = avoided_fine_value + efficiency_value + reputation_value
        
        roi_percentage = ((total_benefits - total_cost) / total_cost) * 100
        payback_period = total_cost / (total_benefits / 12)  # months
        
        return {
            'total_investment': round(total_cost, 2),
            'annual_benefits': round(total_benefits, 2),
            'roi_percentage': round(roi_percentage, 1),
            'payback_period_months': round(payback_period, 1),
            'benefit_breakdown': {
                'avoided_fines': round(avoided_fine_value, 2),
                'efficiency_gains': round(efficiency_value, 2),
                'reputation_protection': round(reputation_value, 2)
            },
            'break_even_date': f"{int(payback_period)} months"
        }
    
    def _generate_cost_recommendations(
        self,
        year_one_total: float,
        org_size: str,
        module_results: Dict[str, Any]
    ) -> List[str]:
        """Generate cost optimization recommendations."""
        recommendations = []
        
        if year_one_total > 500000:
            recommendations.append(
                "Consider phased implementation to spread costs over multiple years"
            )
        
        if org_size in ['small', 'medium']:
            recommendations.append(
                "Consider shared compliance services or consortium approach to reduce costs"
            )
        
        if len(module_results) > 5:
            recommendations.append(
                "Invest in unified compliance platform to reduce per-module costs"
            )
        
        recommendations.extend([
            "Negotiate multi-year contracts with vendors for better rates",
            "Consider internal hiring vs. external consultants for ongoing support",
            "Leverage open-source compliance tools where appropriate",
            "Explore government grants or subsidies for compliance initiatives"
        ])
        
        return recommendations
