"""
Custom Report Builder
Generates compliance reports with flexible customization.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ReportType(str, Enum):
    """Report type classifications"""
    COMPLIANCE_OVERVIEW = "compliance_overview"
    AUDIT_FINDINGS = "audit_findings"
    RISK_ASSESSMENT = "risk_assessment"
    TREND_ANALYSIS = "trend_analysis"
    EXECUTIVE_SUMMARY = "executive_summary"
    DETAILED_ASSESSMENT = "detailed_assessment"
    GAP_ANALYSIS = "gap_analysis"
    CERTIFICATION_STATUS = "certification_status"


class ReportFormat(str, Enum):
    """Report output formats"""
    PDF = "pdf"
    EXCEL = "excel"
    WORD = "word"
    HTML = "html"
    JSON = "json"
    CSV = "csv"


class ReportFrequency(str, Enum):
    """Report generation frequency"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"
    ON_DEMAND = "on_demand"


@dataclass
class ReportSection:
    """Report section configuration"""
    section_id: str
    title: str
    section_type: str  # 'summary', 'metrics', 'trends', 'risks', 'recommendations'
    content_template: str
    filters: Dict[str, Any] = field(default_factory=dict)
    order: int = 0


@dataclass
class ReportTemplate:
    """Report template configuration"""
    template_id: str
    name: str
    description: str
    report_type: ReportType
    sections: List[ReportSection]
    branding: Dict[str, Any] = field(default_factory=dict)  # Logo, colors, fonts


@dataclass
class GeneratedReport:
    """Generated report instance"""
    report_id: str
    template: ReportTemplate
    generated_date: datetime
    period_start: datetime
    period_end: datetime
    organization: str
    content: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


class ReportBuilder:
    """
    Custom compliance report builder.

    Features:
    - Customizable report templates
    - Multi-section reports
    - Flexible data aggregation
    - Professional formatting
    - Branding support
    - Multi-format export
    """

    def __init__(self):
        """Initialize report builder."""
        self.templates: Dict[str, ReportTemplate] = {}
        self.generated_reports: Dict[str, GeneratedReport] = {}
        self._initialize_default_templates()

    def _initialize_default_templates(self) -> None:
        """Initialize default report templates."""
        # Compliance Overview Template
        compliance_sections = [
            ReportSection(
                section_id="executive_summary",
                title="Executive Summary",
                section_type="summary",
                content_template="templates/executive_summary.html",
                order=1
            ),
            ReportSection(
                section_id="compliance_metrics",
                title="Current Compliance Metrics",
                section_type="metrics",
                content_template="templates/metrics.html",
                order=2
            ),
            ReportSection(
                section_id="module_scores",
                title="Module Compliance Scores",
                section_type="metrics",
                content_template="templates/module_scores.html",
                order=3
            ),
            ReportSection(
                section_id="trends",
                title="Compliance Trends",
                section_type="trends",
                content_template="templates/trends.html",
                order=4
            ),
            ReportSection(
                section_id="recommendations",
                title="Recommendations",
                section_type="recommendations",
                content_template="templates/recommendations.html",
                order=5
            ),
        ]

        compliance_template = ReportTemplate(
            template_id="compliance_overview",
            name="Compliance Overview Report",
            description="Comprehensive overview of compliance status",
            report_type=ReportType.COMPLIANCE_OVERVIEW,
            sections=compliance_sections
        )

        self.templates["compliance_overview"] = compliance_template

        # Risk Assessment Template
        risk_sections = [
            ReportSection(
                section_id="risk_summary",
                title="Risk Summary",
                section_type="summary",
                content_template="templates/risk_summary.html",
                order=1
            ),
            ReportSection(
                section_id="risk_heatmap",
                title="Risk Heatmap",
                section_type="risks",
                content_template="templates/risk_heatmap.html",
                order=2
            ),
            ReportSection(
                section_id="risk_details",
                title="Risk Detailed Analysis",
                section_type="risks",
                content_template="templates/risk_details.html",
                order=3
            ),
            ReportSection(
                section_id="mitigation",
                title="Risk Mitigation Strategies",
                section_type="recommendations",
                content_template="templates/mitigation.html",
                order=4
            ),
        ]

        risk_template = ReportTemplate(
            template_id="risk_assessment",
            name="Risk Assessment Report",
            description="Detailed risk assessment and mitigation plan",
            report_type=ReportType.RISK_ASSESSMENT,
            sections=risk_sections
        )

        self.templates["risk_assessment"] = risk_template

    def create_custom_template(
        self,
        template_id: str,
        name: str,
        description: str,
        report_type: ReportType,
        sections: List[ReportSection],
        branding: Optional[Dict[str, Any]] = None
    ) -> ReportTemplate:
        """
        Create a custom report template.

        Args:
            template_id: Unique template identifier
            name: Template name
            description: Template description
            report_type: Type of report
            sections: List of report sections
            branding: Optional branding configuration

        Returns:
            ReportTemplate
        """
        template = ReportTemplate(
            template_id=template_id,
            name=name,
            description=description,
            report_type=report_type,
            sections=sorted(sections, key=lambda x: x.order),
            branding=branding or self._get_default_branding()
        )

        self.templates[template_id] = template
        return template

    def _get_default_branding(self) -> Dict[str, Any]:
        """Get default branding configuration."""
        return {
            'logo_url': '',
            'primary_color': '#1976d2',
            'secondary_color': '#424242',
            'font_family': 'Arial, sans-serif',
            'organization_name': 'LOKI Enterprise',
        }

    def generate_report(
        self,
        template_id: str,
        data: Dict[str, Any],
        organization: str,
        period_start: datetime,
        period_end: datetime,
        report_id: Optional[str] = None
    ) -> GeneratedReport:
        """
        Generate a report from template with data.

        Args:
            template_id: Template to use
            data: Report data
            organization: Organization name
            period_start: Report period start
            period_end: Report period end
            report_id: Optional custom report ID

        Returns:
            GeneratedReport
        """
        if template_id not in self.templates:
            raise ValueError(f"Template {template_id} not found")

        template = self.templates[template_id]

        if not report_id:
            report_id = f"report_{datetime.now().timestamp()}"

        # Aggregate section content
        content = {}
        for section in template.sections:
            section_content = self._render_section(section, data)
            content[section.section_id] = section_content

        report = GeneratedReport(
            report_id=report_id,
            template=template,
            generated_date=datetime.now(),
            period_start=period_start,
            period_end=period_end,
            organization=organization,
            content=content,
            metadata={
                'data_sources': list(data.keys()),
                'total_sections': len(template.sections),
            }
        )

        self.generated_reports[report_id] = report
        return report

    def _render_section(
        self,
        section: ReportSection,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Render individual report section."""
        section_data = data.get(section.section_id, {})

        return {
            'title': section.title,
            'type': section.section_type,
            'content': section_data,
            'generated_at': datetime.now().isoformat(),
        }

    def add_section_to_template(
        self,
        template_id: str,
        section: ReportSection
    ) -> bool:
        """Add section to existing template."""
        if template_id not in self.templates:
            return False

        template = self.templates[template_id]
        # Update order to be after last section
        section.order = len(template.sections) + 1
        template.sections.append(section)
        template.sections.sort(key=lambda x: x.order)
        return True

    def remove_section_from_template(
        self,
        template_id: str,
        section_id: str
    ) -> bool:
        """Remove section from template."""
        if template_id not in self.templates:
            return False

        template = self.templates[template_id]
        original_count = len(template.sections)
        template.sections = [s for s in template.sections if s.section_id != section_id]

        return len(template.sections) < original_count

    def get_report(self, report_id: str) -> Optional[GeneratedReport]:
        """Retrieve generated report."""
        return self.generated_reports.get(report_id)

    def list_templates(self) -> List[Dict[str, str]]:
        """List all available templates."""
        return [
            {
                'id': t.template_id,
                'name': t.name,
                'type': t.report_type.value,
                'sections': len(t.sections),
            }
            for t in self.templates.values()
        ]

    def list_generated_reports(
        self,
        organization: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List generated reports."""
        reports = list(self.generated_reports.values())

        if organization:
            reports = [r for r in reports if r.organization == organization]

        return [
            {
                'id': r.report_id,
                'template': r.template.name,
                'organization': r.organization,
                'generated': r.generated_date.isoformat(),
                'period': f"{r.period_start.date()} to {r.period_end.date()}",
            }
            for r in sorted(reports, key=lambda x: x.generated_date, reverse=True)
        ]

    def clone_template(
        self,
        source_template_id: str,
        new_template_id: str,
        new_name: str
    ) -> Optional[ReportTemplate]:
        """Clone existing template with new ID."""
        if source_template_id not in self.templates:
            return None

        source = self.templates[source_template_id]

        # Deep copy sections
        new_sections = [
            ReportSection(
                section_id=f"{new_template_id}_{s.section_id}",
                title=s.title,
                section_type=s.section_type,
                content_template=s.content_template,
                filters=s.filters.copy(),
                order=s.order
            )
            for s in source.sections
        ]

        new_template = ReportTemplate(
            template_id=new_template_id,
            name=new_name,
            description=source.description,
            report_type=source.report_type,
            sections=new_sections,
            branding=source.branding.copy()
        )

        self.templates[new_template_id] = new_template
        return new_template

    def bulk_generate_reports(
        self,
        template_id: str,
        organizations: List[Dict[str, Any]],
        period_start: datetime,
        period_end: datetime
    ) -> List[GeneratedReport]:
        """
        Generate reports for multiple organizations.

        Args:
            template_id: Template to use
            organizations: List of org data dicts
            period_start: Period start
            period_end: Period end

        Returns:
            List of GeneratedReport
        """
        reports = []

        for org_data in organizations:
            org_name = org_data.get('name', 'Unknown')
            report = self.generate_report(
                template_id=template_id,
                data=org_data.get('data', {}),
                organization=org_name,
                period_start=period_start,
                period_end=period_end,
            )
            reports.append(report)

        return reports
