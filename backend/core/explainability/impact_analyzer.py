"""
Impact Analyzer
Analyzes and explains the downstream impact of corrections
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum


class ImpactSeverity(Enum):
    """Severity of impact"""
    CRITICAL = "critical"  # Major compliance/legal impact
    HIGH = "high"  # Significant operational impact
    MEDIUM = "medium"  # Moderate impact
    LOW = "low"  # Minor impact
    MINIMAL = "minimal"  # Negligible impact


class ImpactCategory(Enum):
    """Categories of impact"""
    LEGAL = "legal"
    COMPLIANCE = "compliance"
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    REPUTATIONAL = "reputational"
    TECHNICAL = "technical"
    DOCUMENTATION = "documentation"


@dataclass
class Impact:
    """A single impact item"""
    category: ImpactCategory
    severity: ImpactSeverity
    description: str
    affected_area: str
    action_required: str
    timeline: str  # When this needs attention
    estimated_effort: str  # e.g., "1-2 hours", "1 day"


@dataclass
class ImpactAnalysis:
    """Complete impact analysis for a correction"""

    # Summary
    overall_severity: ImpactSeverity
    total_impacts: int
    categories_affected: List[str]

    # Detailed impacts
    impacts: List[Impact]
    critical_impacts: List[Impact]

    # Downstream effects
    document_sections: List[str]  # Other sections affected
    related_documents: List[str]  # Other documents to review
    processes: List[str]  # Processes that may need updates
    systems: List[str]  # Systems that may need updates

    # Risk assessment
    risk_before: float  # Risk level before correction (0-1)
    risk_after: float  # Risk level after correction (0-1)
    risk_reduction: float  # Percentage risk reduction
    residual_risks: List[str]  # Remaining risks

    # Benefits
    benefits: List[str]
    cost_savings: Optional[str]
    compliance_improvement: str

    # Action plan
    immediate_actions: List[str]
    short_term_actions: List[str]  # Within 1 week
    long_term_actions: List[str]  # Beyond 1 week


class ImpactAnalyzer:
    """
    Analyzes the downstream impact of document corrections

    Features:
    - Multi-dimensional impact analysis
    - Risk assessment (before/after)
    - Downstream dependency tracking
    - Action plan generation
    - Cost-benefit analysis
    """

    def __init__(self):
        self.impact_rules = self._load_impact_rules()

    def analyze_impact(
        self,
        correction_data: Dict[str, Any],
        document_context: Optional[Dict[str, Any]] = None
    ) -> ImpactAnalysis:
        """
        Perform comprehensive impact analysis

        Args:
            correction_data: The correction to analyze
            document_context: Optional document context

        Returns:
            Complete ImpactAnalysis
        """
        gate_id = correction_data.get('gate_id', '')
        severity = correction_data.get('severity', 'INFO')

        # Identify all impacts
        impacts = self._identify_impacts(correction_data, document_context)

        # Categorize impacts
        critical_impacts = [i for i in impacts if i.severity == ImpactSeverity.CRITICAL]

        # Determine overall severity
        if critical_impacts:
            overall_severity = ImpactSeverity.CRITICAL
        elif any(i.severity == ImpactSeverity.HIGH for i in impacts):
            overall_severity = ImpactSeverity.HIGH
        elif any(i.severity == ImpactSeverity.MEDIUM for i in impacts):
            overall_severity = ImpactSeverity.MEDIUM
        else:
            overall_severity = ImpactSeverity.LOW

        # Get affected categories
        categories = list(set(i.category.value for i in impacts))

        # Analyze downstream effects
        document_sections = self._identify_affected_sections(correction_data, document_context)
        related_documents = self._identify_related_documents(correction_data)
        processes = self._identify_affected_processes(correction_data)
        systems = self._identify_affected_systems(correction_data)

        # Risk assessment
        risk_before = self._calculate_risk_before(correction_data)
        risk_after = self._calculate_risk_after(correction_data)
        risk_reduction = ((risk_before - risk_after) / risk_before * 100) if risk_before > 0 else 0
        residual_risks = self._identify_residual_risks(correction_data)

        # Benefits
        benefits = self._identify_benefits(correction_data)
        cost_savings = self._estimate_cost_savings(correction_data)
        compliance_improvement = self._assess_compliance_improvement(correction_data)

        # Action plan
        immediate, short_term, long_term = self._generate_action_plan(impacts, correction_data)

        return ImpactAnalysis(
            overall_severity=overall_severity,
            total_impacts=len(impacts),
            categories_affected=categories,
            impacts=impacts,
            critical_impacts=critical_impacts,
            document_sections=document_sections,
            related_documents=related_documents,
            processes=processes,
            systems=systems,
            risk_before=risk_before,
            risk_after=risk_after,
            risk_reduction=risk_reduction,
            residual_risks=residual_risks,
            benefits=benefits,
            cost_savings=cost_savings,
            compliance_improvement=compliance_improvement,
            immediate_actions=immediate,
            short_term_actions=short_term,
            long_term_actions=long_term
        )

    def _identify_impacts(
        self,
        correction_data: Dict[str, Any],
        document_context: Optional[Dict[str, Any]]
    ) -> List[Impact]:
        """Identify all impacts of this correction"""
        impacts = []
        gate_id = correction_data.get('gate_id', '').lower()
        severity = correction_data.get('severity', 'INFO')

        # Legal impacts
        if 'legal' in gate_id or severity == 'ERROR':
            impacts.append(Impact(
                category=ImpactCategory.LEGAL,
                severity=ImpactSeverity.HIGH,
                description="Legal compliance requirement affected",
                affected_area="Legal risk exposure",
                action_required="Review with legal counsel",
                timeline="Immediate",
                estimated_effort="2-4 hours"
            ))

        # Compliance impacts
        if 'fca' in gate_id or 'gdpr' in gate_id or 'tax' in gate_id:
            impacts.append(Impact(
                category=ImpactCategory.COMPLIANCE,
                severity=ImpactSeverity.CRITICAL if severity == 'ERROR' else ImpactSeverity.HIGH,
                description=f"Regulatory compliance affected ({gate_id})",
                affected_area="Compliance posture",
                action_required="Update compliance documentation",
                timeline="Within 24 hours" if severity == 'ERROR' else "Within 1 week",
                estimated_effort="4-8 hours"
            ))

        # Operational impacts
        impacts.append(Impact(
            category=ImpactCategory.OPERATIONAL,
            severity=ImpactSeverity.MEDIUM,
            description="Document workflow affected",
            affected_area="Document approval process",
            action_required="Notify stakeholders",
            timeline="Within 1 week",
            estimated_effort="1-2 hours"
        ))

        # Financial impacts (for tax corrections)
        if 'tax' in gate_id:
            impacts.append(Impact(
                category=ImpactCategory.FINANCIAL,
                severity=ImpactSeverity.HIGH,
                description="Tax calculations and thresholds affected",
                affected_area="Financial planning and reporting",
                action_required="Review financial projections",
                timeline="Within 1 week",
                estimated_effort="4-6 hours"
            ))

        # Reputational impacts
        if severity == 'ERROR':
            impacts.append(Impact(
                category=ImpactCategory.REPUTATIONAL,
                severity=ImpactSeverity.MEDIUM,
                description="Regulatory standing improvement",
                affected_area="Organizational reputation",
                action_required="Communicate improvements to stakeholders",
                timeline="Within 2 weeks",
                estimated_effort="2-3 hours"
            ))

        # Documentation impacts
        impacts.append(Impact(
            category=ImpactCategory.DOCUMENTATION,
            severity=ImpactSeverity.LOW,
            description="Related documentation may need updates",
            affected_area="Document repository",
            action_required="Scan for similar issues in related documents",
            timeline="Within 1 month",
            estimated_effort="2-4 hours"
        ))

        return impacts

    def _identify_affected_sections(
        self,
        correction_data: Dict[str, Any],
        document_context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Identify document sections affected by this correction"""
        gate_id = correction_data.get('gate_id', '').lower()

        if 'gdpr' in gate_id:
            return [
                "Privacy Policy section",
                "Data Processing Terms",
                "Consent mechanisms",
                "Data Subject Rights section",
                "Third-party sharing disclosures"
            ]
        elif 'fca' in gate_id:
            return [
                "Risk Warnings",
                "Product Descriptions",
                "Fee Disclosures",
                "Performance Claims",
                "Client Communications"
            ]
        elif 'tax' in gate_id:
            return [
                "VAT Registration Information",
                "Tax Liability Disclosures",
                "Financial Thresholds",
                "Compliance Procedures"
            ]
        elif 'nda' in gate_id:
            return [
                "Confidentiality Obligations",
                "Third Party Rights",
                "Enforcement Provisions",
                "Termination Clauses"
            ]
        else:
            return ["Related compliance sections"]

    def _identify_related_documents(self, correction_data: Dict[str, Any]) -> List[str]:
        """Identify related documents that may need review"""
        gate_id = correction_data.get('gate_id', '').lower()

        if 'gdpr' in gate_id:
            return [
                "Privacy Policy",
                "Cookie Policy",
                "Data Processing Agreements",
                "Consent Forms",
                "Data Subject Access Request procedures"
            ]
        elif 'fca' in gate_id:
            return [
                "Client Agreements",
                "Marketing Materials",
                "Risk Disclosures",
                "Terms of Business",
                "Product Information Documents"
            ]
        elif 'tax' in gate_id:
            return [
                "Financial Statements",
                "Tax Returns",
                "VAT Registration Documents",
                "Business Plans",
                "Investor Communications"
            ]
        else:
            return ["Related compliance documents"]

    def _identify_affected_processes(self, correction_data: Dict[str, Any]) -> List[str]:
        """Identify business processes affected"""
        gate_id = correction_data.get('gate_id', '').lower()

        if 'gdpr' in gate_id:
            return [
                "Consent collection process",
                "Data processing procedures",
                "Privacy impact assessments",
                "Data subject request handling"
            ]
        elif 'fca' in gate_id:
            return [
                "Client onboarding",
                "Product sales process",
                "Marketing approval workflow",
                "Compliance review procedures"
            ]
        elif 'hr' in gate_id:
            return [
                "Employee onboarding",
                "Contract management",
                "HR records maintenance",
                "Employment law compliance"
            ]
        else:
            return ["Compliance review processes"]

    def _identify_affected_systems(self, correction_data: Dict[str, Any]) -> List[str]:
        """Identify technical systems affected"""
        gate_id = correction_data.get('gate_id', '').lower()

        if 'gdpr' in gate_id:
            return [
                "Consent management platform",
                "CRM system",
                "Marketing automation",
                "Cookie management"
            ]
        elif 'fca' in gate_id:
            return [
                "Client portal",
                "Document management system",
                "Compliance monitoring tools"
            ]
        else:
            return ["Document management system"]

    def _calculate_risk_before(self, correction_data: Dict[str, Any]) -> float:
        """Calculate risk level before correction"""
        severity = correction_data.get('severity', 'INFO')

        risk_map = {
            'ERROR': 0.9,
            'WARNING': 0.6,
            'INFO': 0.3
        }

        return risk_map.get(severity, 0.5)

    def _calculate_risk_after(self, correction_data: Dict[str, Any]) -> float:
        """Calculate risk level after correction"""
        confidence = correction_data.get('confidence', 0.8)
        before = self._calculate_risk_before(correction_data)

        # Risk after = before risk * (1 - confidence)
        # High confidence correction = low residual risk
        return before * (1 - confidence)

    def _identify_residual_risks(self, correction_data: Dict[str, Any]) -> List[str]:
        """Identify risks that remain after correction"""
        risks = []

        confidence = correction_data.get('confidence', 0.8)

        if confidence < 0.9:
            risks.append(
                f"Correction confidence is {confidence:.0%} - some uncertainty remains"
            )

        if not correction_data.get('expert_validated'):
            risks.append(
                "Correction has not been validated by legal experts"
            )

        risks.append(
            "Related documents may contain similar issues requiring correction"
        )

        return risks

    def _identify_benefits(self, correction_data: Dict[str, Any]) -> List[str]:
        """Identify benefits of making this correction"""
        benefits = []
        gate_id = correction_data.get('gate_id', '').lower()

        # Compliance benefits
        benefits.append("Improved regulatory compliance posture")
        benefits.append("Reduced risk of regulatory enforcement action")

        # Operational benefits
        benefits.append("Clearer documentation for stakeholders")
        benefits.append("More efficient compliance reviews")

        # Gate-specific benefits
        if 'gdpr' in gate_id:
            benefits.extend([
                "Stronger data protection compliance",
                "Reduced risk of ICO enforcement (fines up to 4% turnover)",
                "Enhanced customer trust through transparency"
            ])
        elif 'fca' in gate_id:
            benefits.extend([
                "Better FCA compliance standing",
                "Reduced risk of regulatory fines",
                "Improved client communications clarity"
            ])
        elif 'tax' in gate_id:
            benefits.extend([
                "Accurate tax compliance information",
                "Reduced risk of HMRC penalties",
                "Better financial planning"
            ])

        return benefits

    def _estimate_cost_savings(self, correction_data: Dict[str, Any]) -> Optional[str]:
        """Estimate potential cost savings"""
        severity = correction_data.get('severity', 'INFO')
        gate_id = correction_data.get('gate_id', '').lower()

        if severity == 'ERROR':
            if 'gdpr' in gate_id:
                return "Avoids potential ICO fine of up to £17.5M or 4% of turnover"
            elif 'fca' in gate_id:
                return "Avoids potential FCA fine (typically £100k-£10M for serious breaches)"
            elif 'tax' in gate_id:
                return "Avoids potential HMRC penalties (typically 15-100% of tax underpaid)"
        elif severity == 'WARNING':
            return "Reduces compliance audit costs (estimated £5k-£20k per audit finding)"

        return "Prevents future compliance issues and associated costs"

    def _assess_compliance_improvement(self, correction_data: Dict[str, Any]) -> str:
        """Assess overall compliance improvement"""
        severity = correction_data.get('severity', 'INFO')
        confidence = correction_data.get('confidence', 0.8)

        if severity == 'ERROR' and confidence > 0.8:
            return "SIGNIFICANT: Resolves critical compliance gap"
        elif severity == 'WARNING':
            return "MODERATE: Addresses important compliance concern"
        else:
            return "INCREMENTAL: Improves overall compliance posture"

    def _generate_action_plan(
        self,
        impacts: List[Impact],
        correction_data: Dict[str, Any]
    ) -> tuple[List[str], List[str], List[str]]:
        """Generate prioritized action plan"""

        immediate = []
        short_term = []
        long_term = []

        # Sort impacts by severity
        critical = [i for i in impacts if i.severity == ImpactSeverity.CRITICAL]
        high = [i for i in impacts if i.severity == ImpactSeverity.HIGH]
        medium = [i for i in impacts if i.severity == ImpactSeverity.MEDIUM]

        # Immediate actions (critical impacts)
        for impact in critical:
            immediate.append(f"{impact.action_required} ({impact.affected_area})")

        # Add correction application if high confidence
        if correction_data.get('confidence', 0) > 0.8:
            immediate.append("Apply this correction to the document")

        # Short-term actions (high impacts)
        for impact in high:
            short_term.append(f"{impact.action_required} ({impact.affected_area})")

        short_term.append("Review related documents for similar issues")
        short_term.append("Update compliance documentation")

        # Long-term actions (medium/low impacts)
        for impact in medium:
            long_term.append(f"{impact.action_required} ({impact.affected_area})")

        long_term.append("Conduct comprehensive document audit")
        long_term.append("Update compliance training materials")
        long_term.append("Review and update related processes")

        return immediate, short_term, long_term

    def _load_impact_rules(self) -> Dict[str, Any]:
        """Load impact analysis rules"""
        return {
            'critical_gates': ['fca_uk', 'gdpr_uk', 'tax_uk'],
            'high_severity_threshold': 0.7,
            'medium_severity_threshold': 0.4
        }

    def export_impact_report(self, analysis: ImpactAnalysis) -> Dict[str, Any]:
        """Export impact analysis as structured report"""
        return {
            'summary': {
                'overall_severity': analysis.overall_severity.value,
                'total_impacts': analysis.total_impacts,
                'categories_affected': analysis.categories_affected,
                'critical_count': len(analysis.critical_impacts)
            },
            'impacts': [
                {
                    'category': i.category.value,
                    'severity': i.severity.value,
                    'description': i.description,
                    'affected_area': i.affected_area,
                    'action_required': i.action_required,
                    'timeline': i.timeline,
                    'estimated_effort': i.estimated_effort
                }
                for i in analysis.impacts
            ],
            'downstream_effects': {
                'document_sections': analysis.document_sections,
                'related_documents': analysis.related_documents,
                'processes': analysis.processes,
                'systems': analysis.systems
            },
            'risk_assessment': {
                'before': f"{analysis.risk_before:.1%}",
                'after': f"{analysis.risk_after:.1%}",
                'reduction': f"{analysis.risk_reduction:.1f}%",
                'residual_risks': analysis.residual_risks
            },
            'benefits': {
                'list': analysis.benefits,
                'cost_savings': analysis.cost_savings,
                'compliance_improvement': analysis.compliance_improvement
            },
            'action_plan': {
                'immediate': analysis.immediate_actions,
                'short_term': analysis.short_term_actions,
                'long_term': analysis.long_term_actions
            }
        }
