"""
Roadmap Generator - Creates prioritized compliance action plans
Generates implementation roadmaps with phases, timelines, and resource estimates.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class RoadmapPhase:
    """Represents a phase in the compliance roadmap."""
    phase_number: int
    name: str
    duration_days: int
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    tasks: List[Dict[str, Any]] = field(default_factory=list)
    dependencies: List[int] = field(default_factory=list)  # Phase numbers
    resources_required: List[str] = field(default_factory=list)
    estimated_cost: float = 0.0
    priority: str = 'medium'  # 'critical', 'high', 'medium', 'low'
    success_criteria: List[str] = field(default_factory=list)


class RoadmapGenerator:
    """
    Intelligent compliance roadmap generator.

    Features:
    - Phased implementation plans
    - Priority-based scheduling
    - Resource allocation recommendations
    - Dependency management
    - Timeline estimation
    - Success criteria definition
    """

    def __init__(self, modules: Dict[str, Any]):
        self.modules = modules

    def generate(
        self,
        module_results: Dict[str, Any],
        conflicts: List[Dict[str, Any]],
        organization_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive compliance roadmap.

        Args:
            module_results: Compliance results for all modules
            conflicts: Detected cross-module conflicts
            organization_profile: Organization profile for customization

        Returns:
            Detailed roadmap with phases, tasks, and timelines
        """
        logger.info("Generating compliance roadmap")

        # Determine organization context
        org_size = organization_profile.get('size', 'medium') if organization_profile else 'medium'
        org_resources = organization_profile.get('resources', 'limited') if organization_profile else 'limited'
        start_date = organization_profile.get('start_date') if organization_profile else datetime.now()

        # Analyze current state
        current_state = self._analyze_current_state(module_results)

        # Generate phases
        phases = self._generate_phases(
            module_results,
            conflicts,
            current_state,
            org_size,
            org_resources
        )

        # Calculate timelines
        phases_with_dates = self._calculate_timelines(phases, start_date)

        # Identify critical path
        critical_path = self._identify_critical_path(phases_with_dates)

        # Generate quick wins
        quick_wins = self._identify_quick_wins(module_results)

        # Generate long-term improvements
        long_term = self._identify_long_term_improvements(module_results)

        # Calculate total estimates
        total_estimates = self._calculate_total_estimates(phases_with_dates)

        return {
            'generated_at': datetime.now().isoformat(),
            'current_state': current_state,
            'phases': [self._serialize_phase(p) for p in phases_with_dates],
            'total_phases': len(phases_with_dates),
            'total_duration_days': total_estimates['duration'],
            'total_estimated_cost': total_estimates['cost'],
            'critical_path': critical_path,
            'quick_wins': quick_wins,
            'long_term_improvements': long_term,
            'milestones': self._generate_milestones(phases_with_dates),
            'resource_plan': self._generate_resource_plan(phases_with_dates),
            'risk_factors': self._identify_risk_factors(module_results, conflicts),
            'success_metrics': self._define_success_metrics(module_results)
        }

    def _analyze_current_state(self, module_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current compliance state."""
        total_modules = len(module_results)
        critical_gaps = sum(
            len(r.critical_issues) for r in module_results.values()
            if hasattr(r, 'critical_issues')
        )
        high_gaps = sum(
            len(r.high_issues) for r in module_results.values()
            if hasattr(r, 'high_issues')
        )

        # Calculate maturity level
        avg_score = sum(r.score for r in module_results.values()) / total_modules if total_modules > 0 else 0

        if avg_score >= 90:
            maturity = 'Optimized'
        elif avg_score >= 75:
            maturity = 'Managed'
        elif avg_score >= 60:
            maturity = 'Defined'
        elif avg_score >= 40:
            maturity = 'Initial'
        else:
            maturity = 'Ad-hoc'

        return {
            'maturity_level': maturity,
            'average_score': round(avg_score, 2),
            'total_modules': total_modules,
            'modules_passing': sum(1 for r in module_results.values() if r.overall_status == 'PASS'),
            'modules_failing': sum(1 for r in module_results.values() if r.overall_status == 'FAIL'),
            'critical_gaps': critical_gaps,
            'high_priority_gaps': high_gaps,
            'readiness': self._assess_readiness(critical_gaps, high_gaps, avg_score)
        }

    def _assess_readiness(self, critical_gaps: int, high_gaps: int, avg_score: float) -> str:
        """Assess overall readiness for compliance."""
        if critical_gaps > 0:
            return 'Not Ready - Critical gaps must be addressed'
        elif high_gaps > 5:
            return 'Needs Improvement - Multiple high-priority gaps'
        elif avg_score < 70:
            return 'Below Standard - Significant work required'
        elif avg_score < 85:
            return 'Approaching Ready - Minor improvements needed'
        else:
            return 'Ready - Strong compliance posture'

    def _generate_phases(
        self,
        module_results: Dict[str, Any],
        conflicts: List[Dict[str, Any]],
        current_state: Dict[str, Any],
        org_size: str,
        org_resources: str
    ) -> List[RoadmapPhase]:
        """Generate implementation phases."""
        phases = []

        # Phase 1: Foundation & Critical Issues (Weeks 1-4)
        phase1 = self._create_foundation_phase(module_results, conflicts, org_size)
        phases.append(phase1)

        # Phase 2: Core Compliance Implementation (Weeks 5-12)
        phase2 = self._create_core_implementation_phase(module_results, org_size)
        phases.append(phase2)

        # Phase 3: Integration & Testing (Weeks 13-16)
        phase3 = self._create_integration_phase(module_results)
        phases.append(phase3)

        # Phase 4: Optimization & Continuous Improvement (Weeks 17+)
        phase4 = self._create_optimization_phase(module_results)
        phases.append(phase4)

        # Adjust phases based on organization resources
        if org_resources == 'extensive':
            # Can parallelize more, reduce timelines
            for phase in phases:
                phase.duration_days = int(phase.duration_days * 0.7)
        elif org_resources == 'limited':
            # Need more time, sequential approach
            for phase in phases:
                phase.duration_days = int(phase.duration_days * 1.3)

        return phases

    def _create_foundation_phase(
        self,
        module_results: Dict[str, Any],
        conflicts: List[Dict[str, Any]],
        org_size: str
    ) -> RoadmapPhase:
        """Create Phase 1: Foundation & Critical Issues."""
        tasks = []

        # Task 1: Address critical issues
        critical_modules = [
            (mid, r) for mid, r in module_results.items()
            if hasattr(r, 'critical_issues') and len(r.critical_issues) > 0
        ]

        if critical_modules:
            for module_id, result in critical_modules:
                tasks.append({
                    'task_id': f'critical_{module_id}',
                    'name': f'Resolve critical issues in {module_id}',
                    'description': f'Address {len(result.critical_issues)} critical compliance gaps',
                    'priority': 'critical',
                    'estimated_hours': len(result.critical_issues) * 8,
                    'assigned_to': 'Compliance Team',
                    'deliverables': [f'Remediation plan for {module_id}', 'Documentation', 'Testing']
                })

        # Task 2: Resolve conflicts
        critical_conflicts = [c for c in conflicts if c['severity'] in ['critical', 'high']]
        if critical_conflicts:
            tasks.append({
                'task_id': 'resolve_conflicts',
                'name': 'Resolve cross-module conflicts',
                'description': f'Address {len(critical_conflicts)} critical/high conflicts',
                'priority': 'critical',
                'estimated_hours': len(critical_conflicts) * 12,
                'assigned_to': 'Legal & Compliance',
                'deliverables': ['Conflict resolution plan', 'Policy decisions', 'Documentation']
            })

        # Task 3: Establish governance
        tasks.append({
            'task_id': 'establish_governance',
            'name': 'Establish compliance governance framework',
            'description': 'Set up compliance team, processes, and tools',
            'priority': 'high',
            'estimated_hours': 40,
            'assigned_to': 'Leadership Team',
            'deliverables': ['Governance structure', 'Roles & responsibilities', 'Meeting schedule']
        })

        return RoadmapPhase(
            phase_number=1,
            name='Foundation & Critical Issues',
            duration_days=28,
            start_date=None,
            end_date=None,
            tasks=tasks,
            dependencies=[],
            resources_required=['Compliance Team', 'Legal Counsel', 'IT Security'],
            estimated_cost=50000.0 if org_size == 'enterprise' else 20000.0,
            priority='critical',
            success_criteria=[
                'All critical issues resolved',
                'Major conflicts addressed',
                'Governance framework established',
                'Compliance team activated'
            ]
        )

    def _create_core_implementation_phase(
        self,
        module_results: Dict[str, Any],
        org_size: str
    ) -> RoadmapPhase:
        """Create Phase 2: Core Compliance Implementation."""
        tasks = []

        # Implement each module
        for module_id, result in module_results.items():
            if result.overall_status in ['FAIL', 'WARNING']:
                module_name = self.modules[module_id].name if module_id in self.modules else module_id

                tasks.append({
                    'task_id': f'implement_{module_id}',
                    'name': f'Implement {module_name}',
                    'description': f'Full implementation of {module_name} requirements',
                    'priority': 'high',
                    'estimated_hours': self.modules[module_id].implementation_time_days * 6 if module_id in self.modules else 80,
                    'assigned_to': f'{module_name} Team',
                    'deliverables': [
                        f'{module_name} policies',
                        'Technical controls',
                        'Training materials',
                        'Documentation'
                    ]
                })

        # Add training tasks
        tasks.append({
            'task_id': 'compliance_training',
            'name': 'Conduct compliance training',
            'description': 'Train all staff on compliance requirements',
            'priority': 'high',
            'estimated_hours': 80,
            'assigned_to': 'Training Team',
            'deliverables': ['Training program', 'Attendance records', 'Assessment results']
        })

        return RoadmapPhase(
            phase_number=2,
            name='Core Compliance Implementation',
            duration_days=56,
            start_date=None,
            end_date=None,
            tasks=tasks,
            dependencies=[1],
            resources_required=['Implementation Teams', 'Technical Resources', 'Training'],
            estimated_cost=150000.0 if org_size == 'enterprise' else 60000.0,
            priority='high',
            success_criteria=[
                'All modules implemented',
                'Policies documented',
                'Technical controls deployed',
                'Staff trained',
                'Scores improved to >70'
            ]
        )

    def _create_integration_phase(self, module_results: Dict[str, Any]) -> RoadmapPhase:
        """Create Phase 3: Integration & Testing."""
        tasks = [
            {
                'task_id': 'integration_testing',
                'name': 'Integration testing',
                'description': 'Test all compliance modules together',
                'priority': 'high',
                'estimated_hours': 80,
                'assigned_to': 'QA Team',
                'deliverables': ['Test plans', 'Test results', 'Issue log']
            },
            {
                'task_id': 'process_integration',
                'name': 'Integrate compliance into business processes',
                'description': 'Embed compliance checks into daily operations',
                'priority': 'high',
                'estimated_hours': 120,
                'assigned_to': 'Process Improvement Team',
                'deliverables': ['Updated processes', 'Workflow documentation', 'Training']
            },
            {
                'task_id': 'monitoring_setup',
                'name': 'Set up continuous monitoring',
                'description': 'Implement automated compliance monitoring',
                'priority': 'medium',
                'estimated_hours': 60,
                'assigned_to': 'IT Team',
                'deliverables': ['Monitoring dashboard', 'Alerts configured', 'Reports automated']
            }
        ]

        return RoadmapPhase(
            phase_number=3,
            name='Integration & Testing',
            duration_days=28,
            start_date=None,
            end_date=None,
            tasks=tasks,
            dependencies=[2],
            resources_required=['QA Team', 'IT Team', 'Process Team'],
            estimated_cost=40000.0,
            priority='medium',
            success_criteria=[
                'All integration tests passed',
                'Compliance embedded in processes',
                'Monitoring operational',
                'No critical findings'
            ]
        )

    def _create_optimization_phase(self, module_results: Dict[str, Any]) -> RoadmapPhase:
        """Create Phase 4: Optimization & Continuous Improvement."""
        tasks = [
            {
                'task_id': 'optimization',
                'name': 'Optimize compliance processes',
                'description': 'Streamline and automate compliance activities',
                'priority': 'medium',
                'estimated_hours': 80,
                'assigned_to': 'Continuous Improvement Team',
                'deliverables': ['Optimization report', 'Process improvements', 'Automation']
            },
            {
                'task_id': 'certification_prep',
                'name': 'Prepare for external certification',
                'description': 'Prepare documentation and evidence for audit',
                'priority': 'medium',
                'estimated_hours': 120,
                'assigned_to': 'Compliance Team',
                'deliverables': ['Audit readiness assessment', 'Evidence packages', 'Gap analysis']
            },
            {
                'task_id': 'continuous_improvement',
                'name': 'Establish continuous improvement program',
                'description': 'Set up ongoing compliance improvement process',
                'priority': 'low',
                'estimated_hours': 40,
                'assigned_to': 'Compliance Team',
                'deliverables': ['Improvement framework', 'KPIs', 'Review schedule']
            }
        ]

        return RoadmapPhase(
            phase_number=4,
            name='Optimization & Continuous Improvement',
            duration_days=42,
            start_date=None,
            end_date=None,
            tasks=tasks,
            dependencies=[3],
            resources_required=['Compliance Team', 'External Auditors'],
            estimated_cost=30000.0,
            priority='low',
            success_criteria=[
                'Processes optimized',
                'Certification ready',
                'Continuous improvement established',
                'Scores >85'
            ]
        )

    def _calculate_timelines(
        self,
        phases: List[RoadmapPhase],
        start_date: datetime
    ) -> List[RoadmapPhase]:
        """Calculate start and end dates for each phase."""
        current_date = start_date

        for phase in phases:
            # Check dependencies
            if phase.dependencies:
                # Start after all dependent phases complete
                max_dependency_end = start_date
                for dep_phase_num in phase.dependencies:
                    dep_phase = next((p for p in phases if p.phase_number == dep_phase_num), None)
                    if dep_phase and dep_phase.end_date:
                        if dep_phase.end_date > max_dependency_end:
                            max_dependency_end = dep_phase.end_date
                current_date = max_dependency_end

            phase.start_date = current_date
            phase.end_date = current_date + timedelta(days=phase.duration_days)
            current_date = phase.end_date

        return phases

    def _identify_critical_path(self, phases: List[RoadmapPhase]) -> List[Dict[str, Any]]:
        """Identify the critical path through the roadmap."""
        critical_path = []

        for phase in phases:
            if phase.priority in ['critical', 'high']:
                critical_path.append({
                    'phase': phase.phase_number,
                    'name': phase.name,
                    'start': phase.start_date.isoformat() if phase.start_date else None,
                    'end': phase.end_date.isoformat() if phase.end_date else None,
                    'duration_days': phase.duration_days,
                    'critical_tasks': [
                        t for t in phase.tasks
                        if t['priority'] in ['critical', 'high']
                    ]
                })

        return critical_path

    def _identify_quick_wins(self, module_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify quick win opportunities."""
        quick_wins = []

        for module_id, result in module_results.items():
            # Look for easy fixes (medium issues with simple solutions)
            if hasattr(result, 'medium_issues'):
                for issue in result.medium_issues[:3]:  # Top 3
                    quick_wins.append({
                        'module': module_id,
                        'issue': issue.get('issue', str(issue)),
                        'estimated_effort': '1-2 days',
                        'impact': 'Quick score improvement',
                        'priority': 'medium'
                    })

        return quick_wins[:5]  # Return top 5

    def _identify_long_term_improvements(self, module_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify long-term improvement opportunities."""
        improvements = [
            {
                'area': 'Automation',
                'description': 'Implement automated compliance monitoring and reporting',
                'timeframe': '6-12 months',
                'benefit': 'Reduced manual effort, improved accuracy'
            },
            {
                'area': 'Integration',
                'description': 'Integrate compliance checks into development pipeline',
                'timeframe': '3-6 months',
                'benefit': 'Shift-left compliance, early issue detection'
            },
            {
                'area': 'Training',
                'description': 'Establish ongoing compliance training program',
                'timeframe': '3-6 months',
                'benefit': 'Improved compliance culture, reduced violations'
            },
            {
                'area': 'Metrics',
                'description': 'Develop comprehensive compliance metrics dashboard',
                'timeframe': '2-4 months',
                'benefit': 'Better visibility, data-driven decisions'
            }
        ]

        return improvements

    def _calculate_total_estimates(self, phases: List[RoadmapPhase]) -> Dict[str, Any]:
        """Calculate total duration and cost estimates."""
        total_duration = sum(p.duration_days for p in phases)
        total_cost = sum(p.estimated_cost for p in phases)
        total_tasks = sum(len(p.tasks) for p in phases)

        return {
            'duration': total_duration,
            'cost': total_cost,
            'tasks': total_tasks,
            'end_date': phases[-1].end_date.isoformat() if phases and phases[-1].end_date else None
        }

    def _generate_milestones(self, phases: List[RoadmapPhase]) -> List[Dict[str, Any]]:
        """Generate key milestones."""
        milestones = []

        for phase in phases:
            milestones.append({
                'milestone': f'{phase.name} Complete',
                'date': phase.end_date.isoformat() if phase.end_date else None,
                'criteria': phase.success_criteria,
                'phase': phase.phase_number
            })

        return milestones

    def _generate_resource_plan(self, phases: List[RoadmapPhase]) -> Dict[str, Any]:
        """Generate resource allocation plan."""
        all_resources = set()
        for phase in phases:
            all_resources.update(phase.resources_required)

        resource_timeline = []
        for phase in phases:
            resource_timeline.append({
                'phase': phase.phase_number,
                'phase_name': phase.name,
                'period': f"{phase.start_date.strftime('%Y-%m-%d') if phase.start_date else 'TBD'} to {phase.end_date.strftime('%Y-%m-%d') if phase.end_date else 'TBD'}",
                'resources': phase.resources_required,
                'estimated_cost': phase.estimated_cost
            })

        return {
            'total_resources_needed': list(all_resources),
            'timeline': resource_timeline,
            'peak_resource_phase': max(phases, key=lambda p: len(p.resources_required)).phase_number
        }

    def _identify_risk_factors(
        self,
        module_results: Dict[str, Any],
        conflicts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify risks to roadmap execution."""
        risks = []

        # Risk from conflicts
        if conflicts:
            high_severity_conflicts = [c for c in conflicts if c['severity'] in ['critical', 'high']]
            if high_severity_conflicts:
                risks.append({
                    'risk': 'Cross-module conflicts',
                    'severity': 'high',
                    'description': f'{len(high_severity_conflicts)} high-severity conflicts may delay implementation',
                    'mitigation': 'Prioritize conflict resolution in Phase 1'
                })

        # Risk from critical issues
        total_critical = sum(
            len(r.critical_issues) for r in module_results.values()
            if hasattr(r, 'critical_issues')
        )
        if total_critical > 10:
            risks.append({
                'risk': 'High number of critical issues',
                'severity': 'high',
                'description': f'{total_critical} critical issues may require extended timeline',
                'mitigation': 'Consider external consulting support'
            })

        # Risk from multiple modules
        if len(module_results) > 5:
            risks.append({
                'risk': 'Complex multi-framework compliance',
                'severity': 'medium',
                'description': 'Managing multiple compliance frameworks increases complexity',
                'mitigation': 'Use unified compliance management platform'
            })

        return risks

    def _define_success_metrics(self, module_results: Dict[str, Any]) -> Dict[str, Any]:
        """Define success metrics for roadmap."""
        current_avg = sum(r.score for r in module_results.values()) / len(module_results) if module_results else 0

        return {
            'current_average_score': round(current_avg, 2),
            'target_average_score': 85.0,
            'improvement_needed': round(85.0 - current_avg, 2),
            'kpis': [
                {
                    'metric': 'Average Compliance Score',
                    'current': round(current_avg, 2),
                    'target': 85.0,
                    'unit': 'score'
                },
                {
                    'metric': 'Critical Issues',
                    'current': sum(len(r.critical_issues) for r in module_results.values() if hasattr(r, 'critical_issues')),
                    'target': 0,
                    'unit': 'count'
                },
                {
                    'metric': 'Modules Passing',
                    'current': sum(1 for r in module_results.values() if r.overall_status == 'PASS'),
                    'target': len(module_results),
                    'unit': 'count'
                },
                {
                    'metric': 'Time to Compliance',
                    'current': 'N/A',
                    'target': '4-6 months',
                    'unit': 'months'
                }
            ]
        }

    def _serialize_phase(self, phase: RoadmapPhase) -> Dict[str, Any]:
        """Serialize roadmap phase to dictionary."""
        return {
            'phase_number': phase.phase_number,
            'name': phase.name,
            'duration_days': phase.duration_days,
            'start_date': phase.start_date.isoformat() if phase.start_date else None,
            'end_date': phase.end_date.isoformat() if phase.end_date else None,
            'tasks': phase.tasks,
            'task_count': len(phase.tasks),
            'dependencies': phase.dependencies,
            'resources_required': phase.resources_required,
            'estimated_cost': phase.estimated_cost,
            'priority': phase.priority,
            'success_criteria': phase.success_criteria
        }
