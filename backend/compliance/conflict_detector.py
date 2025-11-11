"""
Conflict Detector - Identifies and resolves cross-module compliance conflicts
Detects contradictions, overlaps, and incompatibilities between compliance frameworks.
"""

from typing import Dict, List, Any, Set, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ComplianceConflict:
    """Represents a conflict between compliance modules."""
    conflict_id: str
    conflict_type: str  # 'contradiction', 'overlap', 'gap', 'incompatibility'
    severity: str  # 'critical', 'high', 'medium', 'low'
    module_a: str
    module_b: str
    description: str
    affected_requirements: List[str]
    resolution_strategies: List[str]
    priority: int  # 1-10


class ConflictDetector:
    """
    Cross-module conflict detection and resolution system.

    Features:
    - Detect regulatory contradictions
    - Identify requirement overlaps
    - Find compliance gaps
    - Suggest resolution strategies
    - Prioritize conflict resolution
    """

    def __init__(self, modules: Dict[str, Any]):
        self.modules = modules
        self._initialize_conflict_rules()

    def _initialize_conflict_rules(self):
        """Initialize known conflict patterns between modules."""
        self.conflict_rules = {
            ('gdpr_uk', 'hipaa_us'): {
                'type': 'contradiction',
                'severity': 'high',
                'description': 'Different consent models and data subject rights',
                'details': [
                    'GDPR requires explicit consent withdrawal at any time',
                    'HIPAA allows consent to be condition of treatment',
                    'GDPR has broader data subject rights (right to erasure)',
                    'HIPAA retention requirements may conflict with erasure rights'
                ],
                'resolution': [
                    'Implement jurisdictional data segregation',
                    'Apply GDPR standards to EU data, HIPAA to US data',
                    'Document legal basis for processing separately',
                    'Implement region-specific consent mechanisms'
                ]
            },
            ('fca_uk', 'sec_us'): {
                'type': 'incompatibility',
                'severity': 'critical',
                'description': 'Different regulatory reporting and governance requirements',
                'details': [
                    'FCA SMCR vs SEC officer certification requirements differ',
                    'Different market abuse definitions and reporting',
                    'Conflicting disclosure requirements',
                    'Different approach to client classification'
                ],
                'resolution': [
                    'Maintain separate compliance programs per jurisdiction',
                    'Implement dual reporting frameworks',
                    'Consult legal counsel for cross-border operations',
                    'Consider regulatory equivalence agreements'
                ]
            },
            ('gdpr_uk', 'sox_us'): {
                'type': 'overlap',
                'severity': 'medium',
                'description': 'Overlapping data retention and audit trail requirements',
                'details': [
                    'Both require audit trails but with different retention periods',
                    'SOX requires 7 years, GDPR requires minimum necessary',
                    'Both require access controls but different standards',
                    'Overlap in data protection impact assessments'
                ],
                'resolution': [
                    'Implement longest retention period (7 years for SOX)',
                    'Document GDPR legal basis for extended retention',
                    'Use combined audit trail system',
                    'Implement unified access control framework'
                ]
            },
            ('pci_dss', 'gdpr_uk'): {
                'type': 'overlap',
                'severity': 'medium',
                'description': 'Overlapping security and data protection requirements',
                'details': [
                    'PCI-DSS has specific cardholder data encryption requirements',
                    'GDPR requires appropriate security measures',
                    'Both require breach notification but different timelines',
                    'PCI-DSS 72 hours, GDPR 72 hours (aligned)'
                ],
                'resolution': [
                    'PCI-DSS standards typically exceed GDPR minimums',
                    'Use PCI-DSS security controls for payment data',
                    'Extend PCI-DSS controls to all personal data',
                    'Implement unified breach response procedure'
                ]
            },
            ('hipaa_us', 'sox_us'): {
                'type': 'overlap',
                'severity': 'low',
                'description': 'Overlapping audit and control requirements',
                'details': [
                    'Both require internal controls and audit trails',
                    'HIPAA focuses on PHI, SOX on financial data',
                    'Different scoping but similar control objectives',
                    'Can share control framework'
                ],
                'resolution': [
                    'Implement unified control framework',
                    'Extend SOX controls to PHI systems',
                    'Use same audit trail infrastructure',
                    'Coordinate compliance testing'
                ]
            },
            ('fca_uk', 'gdpr_uk'): {
                'type': 'overlap',
                'severity': 'low',
                'description': 'Complementary requirements with some overlap',
                'details': [
                    'FCA client communication requirements align with GDPR',
                    'Both require appropriate security measures',
                    'GDPR covers FCA client data',
                    'FCA conduct rules extend GDPR principles'
                ],
                'resolution': [
                    'Implement GDPR as baseline for all personal data',
                    'Apply FCA-specific rules to financial services',
                    'Use combined privacy notice',
                    'Coordinate regulatory reporting'
                ]
            }
        }

    def detect(self, module_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect conflicts between active compliance modules.

        Args:
            module_results: Dictionary of compliance results by module_id

        Returns:
            List of detected conflicts with resolution strategies
        """
        logger.info(f"Detecting conflicts between {len(module_results)} modules")

        conflicts = []
        active_modules = list(module_results.keys())

        # Check for known conflict patterns
        for i, module_a in enumerate(active_modules):
            for module_b in active_modules[i + 1:]:
                conflict = self._check_module_pair(module_a, module_b, module_results)
                if conflict:
                    conflicts.append(conflict)

        # Check for requirement contradictions
        requirement_conflicts = self._detect_requirement_conflicts(module_results)
        conflicts.extend(requirement_conflicts)

        # Check for compliance gaps
        gaps = self._detect_compliance_gaps(module_results)
        conflicts.extend(gaps)

        # Check for timing conflicts
        timing_conflicts = self._detect_timing_conflicts(module_results)
        conflicts.extend(timing_conflicts)

        # Sort by severity and priority
        conflicts.sort(key=lambda x: (
            {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}[x['severity']],
            x.get('priority', 5)
        ), reverse=True)

        logger.info(f"Detected {len(conflicts)} conflicts")
        return conflicts

    def _check_module_pair(
        self,
        module_a: str,
        module_b: str,
        module_results: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Check for conflicts between a specific pair of modules."""

        # Check known conflict rules
        rule_key = (module_a, module_b)
        reverse_key = (module_b, module_a)

        rule = self.conflict_rules.get(rule_key) or self.conflict_rules.get(reverse_key)

        if rule:
            conflict_id = f"{module_a}_{module_b}_conflict"
            return {
                'conflict_id': conflict_id,
                'conflict_type': rule['type'],
                'severity': rule['severity'],
                'module_a': module_a,
                'module_b': module_b,
                'module_a_name': self.modules[module_a].name if module_a in self.modules else module_a,
                'module_b_name': self.modules[module_b].name if module_b in self.modules else module_b,
                'description': rule['description'],
                'details': rule['details'],
                'resolution_strategies': rule['resolution'],
                'priority': {'critical': 10, 'high': 7, 'medium': 4, 'low': 2}[rule['severity']],
                'impact': self._assess_conflict_impact(module_a, module_b, module_results)
            }

        # Check for jurisdiction conflicts
        if module_a in self.modules and module_b in self.modules:
            jurisdiction_conflict = self._check_jurisdiction_conflict(module_a, module_b)
            if jurisdiction_conflict:
                return jurisdiction_conflict

        return None

    def _check_jurisdiction_conflict(self, module_a: str, module_b: str) -> Optional[Dict[str, Any]]:
        """Check if modules have jurisdiction conflicts."""
        module_a_obj = self.modules[module_a]
        module_b_obj = self.modules[module_b]

        # Check if same category but different jurisdictions
        if (module_a_obj.category == module_b_obj.category and
            module_a_obj.jurisdiction != module_b_obj.jurisdiction and
            module_b_obj.jurisdiction != 'Global' and
            module_a_obj.jurisdiction != 'Global'):

            return {
                'conflict_id': f"{module_a}_{module_b}_jurisdiction",
                'conflict_type': 'incompatibility',
                'severity': 'high',
                'module_a': module_a,
                'module_b': module_b,
                'module_a_name': module_a_obj.name,
                'module_b_name': module_b_obj.name,
                'description': f"Different jurisdictions for {module_a_obj.category} compliance",
                'details': [
                    f"{module_a_obj.name}: {module_a_obj.jurisdiction}",
                    f"{module_b_obj.name}: {module_b_obj.jurisdiction}",
                    "May have conflicting requirements",
                    "Requires jurisdiction-specific implementation"
                ],
                'resolution_strategies': [
                    "Implement jurisdiction-based processing logic",
                    "Separate data handling by geography",
                    "Consult legal counsel for cross-border operations",
                    "Document territorial scope of each regulation"
                ],
                'priority': 8,
                'impact': "May require significant architectural changes"
            }

        return None

    def _detect_requirement_conflicts(self, module_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect conflicts in specific requirements across modules."""
        conflicts = []

        # Example: Data retention conflicts
        retention_requirements = {}
        for module_id, result in module_results.items():
            # Extract retention-related issues from results
            if hasattr(result, 'high_issues'):
                for issue in result.high_issues + result.medium_issues:
                    if 'retention' in str(issue).lower():
                        retention_requirements[module_id] = issue

        if len(retention_requirements) > 1:
            conflicts.append({
                'conflict_id': 'retention_conflict',
                'conflict_type': 'contradiction',
                'severity': 'medium',
                'description': 'Multiple modules have different data retention requirements',
                'details': [f"{k}: {v}" for k, v in retention_requirements.items()],
                'resolution_strategies': [
                    'Implement longest retention period',
                    'Document legal basis for extended retention',
                    'Consider regional variation in retention',
                    'Implement automated deletion after retention expires'
                ],
                'priority': 5,
                'affected_modules': list(retention_requirements.keys())
            })

        return conflicts

    def _detect_compliance_gaps(self, module_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect gaps in compliance coverage."""
        gaps = []

        # Check for complementary modules that should be used together
        active_modules = set(module_results.keys())

        # GDPR modules should be used together for comprehensive coverage
        if 'gdpr_uk' in active_modules and 'gdpr_advanced' not in active_modules:
            # Check if advanced features are mentioned
            has_advanced_features = False
            for result in module_results.values():
                if hasattr(result, 'critical_issues'):
                    for issue in result.critical_issues:
                        if any(keyword in str(issue).lower()
                               for keyword in ['automated decision', 'profiling', 'high risk']):
                            has_advanced_features = True
                            break

            if has_advanced_features:
                gaps.append({
                    'conflict_id': 'gdpr_advanced_gap',
                    'conflict_type': 'gap',
                    'severity': 'high',
                    'description': 'Advanced GDPR features detected but GDPR Advanced module not active',
                    'details': [
                        'Document mentions automated decisions or profiling',
                        'GDPR Advanced module provides specialized checks',
                        'May be missing critical compliance requirements'
                    ],
                    'resolution_strategies': [
                        'Activate GDPR Advanced module',
                        'Conduct Data Protection Impact Assessment (DPIA)',
                        'Review automated decision-making processes',
                        'Implement additional safeguards'
                    ],
                    'priority': 8,
                    'recommended_module': 'gdpr_advanced'
                })

        # FCA modules should be used together
        if 'fca_uk' in active_modules and 'fca_advanced' not in active_modules:
            for result in module_results.values():
                if hasattr(result, 'high_issues'):
                    for issue in result.high_issues:
                        if any(keyword in str(issue).lower()
                               for keyword in ['investment', 'crypto', 'algorithm', 'trading']):
                            gaps.append({
                                'conflict_id': 'fca_advanced_gap',
                                'conflict_type': 'gap',
                                'severity': 'high',
                                'description': 'Advanced financial services detected but FCA Advanced module not active',
                                'resolution_strategies': [
                                    'Activate FCA Advanced module',
                                    'Review investment services compliance',
                                    'Consider MiFID II requirements'
                                ],
                                'priority': 8,
                                'recommended_module': 'fca_advanced'
                            })
                            break

        return gaps

    def _detect_timing_conflicts(self, module_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect conflicts in timing requirements (deadlines, retention periods, etc.)."""
        conflicts = []

        # Example: Different breach notification timelines
        notification_requirements = {
            'gdpr_uk': {'timeline': '72 hours', 'requirement': 'Notify supervisory authority'},
            'hipaa_us': {'timeline': '60 days', 'requirement': 'Notify affected individuals'},
            'pci_dss': {'timeline': 'Immediate', 'requirement': 'Notify payment brands'},
        }

        active_notifications = {
            k: v for k, v in notification_requirements.items()
            if k in module_results
        }

        if len(active_notifications) > 1:
            conflicts.append({
                'conflict_id': 'breach_notification_timing',
                'conflict_type': 'overlap',
                'severity': 'high',
                'description': 'Multiple breach notification requirements with different timelines',
                'details': [
                    f"{module}: {info['timeline']} - {info['requirement']}"
                    for module, info in active_notifications.items()
                ],
                'resolution_strategies': [
                    'Implement unified breach response procedure',
                    'Use shortest timeline as standard (most restrictive)',
                    'Create breach notification checklist covering all requirements',
                    'Automate notification processes where possible'
                ],
                'priority': 9,
                'affected_modules': list(active_notifications.keys())
            })

        return conflicts

    def _assess_conflict_impact(
        self,
        module_a: str,
        module_b: str,
        module_results: Dict[str, Any]
    ) -> str:
        """Assess the potential impact of a conflict."""
        result_a = module_results.get(module_a)
        result_b = module_results.get(module_b)

        if not result_a or not result_b:
            return "Unknown impact"

        critical_count = 0
        if hasattr(result_a, 'critical_issues'):
            critical_count += len(result_a.critical_issues)
        if hasattr(result_b, 'critical_issues'):
            critical_count += len(result_b.critical_issues)

        if critical_count > 5:
            return "Very High - May require significant remediation effort"
        elif critical_count > 2:
            return "High - Requires prompt attention and resources"
        elif critical_count > 0:
            return "Medium - Should be addressed in near term"
        else:
            return "Low - Can be managed through documentation"

    def get_resolution_roadmap(self, conflicts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a roadmap for resolving detected conflicts."""
        if not conflicts:
            return {
                'total_conflicts': 0,
                'message': 'No conflicts detected',
                'phases': []
            }

        # Group conflicts by severity
        critical = [c for c in conflicts if c['severity'] == 'critical']
        high = [c for c in conflicts if c['severity'] == 'high']
        medium = [c for c in conflicts if c['severity'] == 'medium']
        low = [c for c in conflicts if c['severity'] == 'low']

        phases = []

        # Phase 1: Critical conflicts
        if critical:
            phases.append({
                'phase': 1,
                'name': 'Critical Conflict Resolution',
                'duration': '1-2 weeks',
                'conflicts': critical,
                'priority': 'Immediate action required',
                'resources': 'Legal counsel, compliance team, technical team'
            })

        # Phase 2: High severity conflicts
        if high:
            phases.append({
                'phase': 2,
                'name': 'High Priority Conflicts',
                'duration': '2-4 weeks',
                'conflicts': high,
                'priority': 'High priority',
                'resources': 'Compliance team, technical implementation'
            })

        # Phase 3: Medium and low severity
        if medium or low:
            phases.append({
                'phase': 3,
                'name': 'Optimization and Documentation',
                'duration': '4-8 weeks',
                'conflicts': medium + low,
                'priority': 'Standard priority',
                'resources': 'Documentation team, ongoing monitoring'
            })

        return {
            'total_conflicts': len(conflicts),
            'by_severity': {
                'critical': len(critical),
                'high': len(high),
                'medium': len(medium),
                'low': len(low)
            },
            'phases': phases,
            'estimated_total_duration': self._calculate_duration(phases),
            'recommendations': self._generate_recommendations(conflicts)
        }

    def _calculate_duration(self, phases: List[Dict[str, Any]]) -> str:
        """Calculate total estimated duration."""
        if not phases:
            return '0 weeks'

        # Simple duration estimation
        phase_count = len(phases)
        if phase_count == 1:
            return phases[0]['duration']
        elif phase_count == 2:
            return '3-6 weeks'
        else:
            return '7-14 weeks'

    def _generate_recommendations(self, conflicts: List[Dict[str, Any]]) -> List[str]:
        """Generate general recommendations for conflict resolution."""
        recommendations = [
            "Prioritize conflicts by severity and business impact",
            "Engage legal counsel for jurisdictional conflicts",
            "Document resolution decisions for audit trail",
            "Implement unified compliance framework where possible",
            "Regular monitoring for new conflicts as regulations evolve"
        ]

        # Add specific recommendations based on conflict types
        conflict_types = set(c['conflict_type'] for c in conflicts)

        if 'contradiction' in conflict_types:
            recommendations.append("Create clear policies for contradictory requirements")

        if 'gap' in conflict_types:
            recommendations.append("Activate recommended modules to close compliance gaps")

        if 'incompatibility' in conflict_types:
            recommendations.append("Consider jurisdiction-specific implementations")

        return recommendations


# Testing
def test_conflict_detector():
    """Test conflict detection with sample results."""
    from backend.compliance.orchestrator import ComplianceOrchestrator, ComplianceResult
    from datetime import datetime

    orchestrator = ComplianceOrchestrator()
    detector = ConflictDetector(orchestrator.modules)

    # Create sample results
    results = {
        'gdpr_uk': ComplianceResult(
            module_id='gdpr_uk',
            module_name='GDPR UK',
            timestamp=datetime.now(),
            overall_status='PASS',
            score=85,
            gates_passed=12,
            gates_failed=1,
            gates_warning=2,
            total_gates=15,
            critical_issues=[],
            high_issues=[],
            medium_issues=[],
            recommendations=[],
            next_actions=[]
        ),
        'hipaa_us': ComplianceResult(
            module_id='hipaa_us',
            module_name='HIPAA',
            timestamp=datetime.now(),
            overall_status='FAIL',
            score=65,
            gates_passed=8,
            gates_failed=3,
            gates_warning=1,
            total_gates=12,
            critical_issues=[{'issue': 'PHI not properly secured'}],
            high_issues=[],
            medium_issues=[],
            recommendations=[],
            next_actions=[]
        )
    }

    conflicts = detector.detect(results)
    assert len(conflicts) > 0, "Should detect GDPR-HIPAA conflict"
    assert any(c['conflict_type'] == 'contradiction' for c in conflicts), "Should detect contradiction"

    print(" Conflict detection test passed")
    print(f"  Detected {len(conflicts)} conflicts")

    # Test resolution roadmap
    roadmap = detector.get_resolution_roadmap(conflicts)
    assert roadmap['total_conflicts'] == len(conflicts)
    assert len(roadmap['phases']) > 0

    print(" Resolution roadmap test passed")
    print(f"  Generated {len(roadmap['phases'])} resolution phases")

    return True


if __name__ == "__main__":
    test_conflict_detector()
