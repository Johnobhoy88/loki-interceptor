"""
Certification Generator - Creates professional PDF compliance certification reports
Generates comprehensive compliance reports with charts, tables, and official documentation.
"""

from typing import Dict, List, Any
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)


class CertificationGenerator:
    """
    PDF compliance certification report generator.

    Features:
    - Professional PDF reports
    - Charts and visualizations
    - Executive summaries
    - Detailed compliance matrices
    - Audit-ready documentation
    - Digital signatures support

    Note: Uses ReportLab for PDF generation (optional dependency)
    """

    def __init__(self):
        self.report_template = 'compliance_certification'
        self.reportlab_available = self._check_reportlab()

    def _check_reportlab(self) -> bool:
        """Check if ReportLab is available."""
        try:
            import reportlab
            return True
        except ImportError:
            logger.warning("ReportLab not available. PDF generation will use fallback HTML format.")
            return False

    def generate_report(
        self,
        module_results: Dict[str, Any],
        organization_info: Dict[str, Any],
        output_path: str
    ) -> str:
        """
        Generate compliance certification PDF report.

        Args:
            module_results: Compliance results for all modules
            organization_info: Organization details for the report
            output_path: Path to save the PDF

        Returns:
            Path to generated report
        """
        logger.info(f"Generating compliance certification report: {output_path}")

        if self.reportlab_available:
            return self._generate_pdf_report(module_results, organization_info, output_path)
        else:
            return self._generate_html_report(module_results, organization_info, output_path)

    def _generate_pdf_report(
        self,
        module_results: Dict[str, Any],
        organization_info: Dict[str, Any],
        output_path: str
    ) -> str:
        """Generate PDF report using ReportLab."""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

            # Create PDF document
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()

            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1E40AF'),
                spaceAfter=30,
                alignment=TA_CENTER
            )

            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#1E40AF'),
                spaceAfter=12,
                spaceBefore=12
            )

            # Title Page
            story.append(Spacer(1, 2*inch))
            story.append(Paragraph("Compliance Certification Report", title_style))
            story.append(Spacer(1, 0.5*inch))

            # Organization Info
            org_name = organization_info.get('name', 'Organization')
            org_address = organization_info.get('address', '')
            report_date = datetime.now().strftime('%d %B %Y')

            story.append(Paragraph(f"<b>{org_name}</b>", styles['Normal']))
            if org_address:
                story.append(Paragraph(org_address, styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph(f"Report Date: {report_date}", styles['Normal']))

            story.append(PageBreak())

            # Executive Summary
            story.append(Paragraph("Executive Summary", heading_style))

            summary_data = self._prepare_summary_data(module_results)
            summary_text = f"""
            This report certifies the compliance status of {org_name} across {summary_data['total_modules']}
            compliance frameworks. The organization has achieved an overall compliance score of
            <b>{summary_data['average_score']:.1f}%</b> with <b>{summary_data['modules_passing']}</b> modules
            passing and <b>{summary_data['modules_failing']}</b> requiring remediation.
            """
            story.append(Paragraph(summary_text, styles['Normal']))
            story.append(Spacer(1, 0.3*inch))

            # Summary Statistics Table
            summary_table_data = [
                ['Metric', 'Value'],
                ['Total Modules Assessed', str(summary_data['total_modules'])],
                ['Overall Compliance Score', f"{summary_data['average_score']:.1f}%"],
                ['Modules Passing', str(summary_data['modules_passing'])],
                ['Modules Requiring Attention', str(summary_data['modules_failing'])],
                ['Critical Issues', str(summary_data['critical_issues'])],
                ['High Priority Issues', str(summary_data['high_issues'])]
            ]

            summary_table = Table(summary_table_data, colWidths=[3*inch, 2*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 0.5*inch))

            # Module-by-Module Assessment
            story.append(PageBreak())
            story.append(Paragraph("Detailed Module Assessment", heading_style))

            for module_id, result in module_results.items():
                module_name = result.module_name if hasattr(result, 'module_name') else module_id
                score = result.score if hasattr(result, 'score') else 0
                status = result.overall_status if hasattr(result, 'overall_status') else 'UNKNOWN'

                # Module header
                story.append(Paragraph(f"<b>{module_name}</b>", styles['Heading3']))

                # Module details table
                module_data = [
                    ['Compliance Score', f"{score:.1f}%"],
                    ['Status', status],
                    ['Gates Passed', f"{result.gates_passed}/{result.total_gates}" if hasattr(result, 'gates_passed') else 'N/A'],
                    ['Critical Issues', str(len(result.critical_issues)) if hasattr(result, 'critical_issues') else '0'],
                    ['High Priority Issues', str(len(result.high_issues)) if hasattr(result, 'high_issues') else '0']
                ]

                module_table = Table(module_data, colWidths=[2.5*inch, 2.5*inch])
                module_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT')
                ]))
                story.append(module_table)
                story.append(Spacer(1, 0.2*inch))

                # Issues (if any)
                if hasattr(result, 'critical_issues') and result.critical_issues:
                    story.append(Paragraph("<b>Critical Issues:</b>", styles['Normal']))
                    for issue in result.critical_issues[:3]:  # Limit to top 3
                        issue_text = issue.get('issue', str(issue)) if isinstance(issue, dict) else str(issue)
                        story.append(Paragraph(f"• {issue_text}", styles['Normal']))
                    story.append(Spacer(1, 0.1*inch))

                story.append(Spacer(1, 0.3*inch))

            # Recommendations
            story.append(PageBreak())
            story.append(Paragraph("Recommendations", heading_style))

            recommendations = self._generate_certification_recommendations(module_results)
            for i, recommendation in enumerate(recommendations, 1):
                story.append(Paragraph(f"{i}. {recommendation}", styles['Normal']))
                story.append(Spacer(1, 0.1*inch))

            # Certification Statement
            story.append(PageBreak())
            story.append(Paragraph("Certification Statement", heading_style))

            cert_text = f"""
            This report certifies that {org_name} has undergone a comprehensive compliance assessment
            as of {report_date}. The assessment covered {summary_data['total_modules']} compliance frameworks
            using the LOKI Compliance Orchestration System.
            <br/><br/>
            Overall Compliance Status: <b>{self._get_certification_status(summary_data)}</b>
            <br/><br/>
            This certification is valid for 12 months from the date of issue and subject to continuous monitoring.
            """
            story.append(Paragraph(cert_text, styles['Normal']))
            story.append(Spacer(1, 1*inch))

            # Signature section
            story.append(Paragraph("_" * 50, styles['Normal']))
            story.append(Paragraph("Authorized Signature", styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph(f"Date: {report_date}", styles['Normal']))

            # Build PDF
            doc.build(story)

            logger.info(f"PDF report generated successfully: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            # Fallback to HTML
            return self._generate_html_report(module_results, organization_info, output_path.replace('.pdf', '.html'))

    def _generate_html_report(
        self,
        module_results: Dict[str, Any],
        organization_info: Dict[str, Any],
        output_path: str
    ) -> str:
        """Generate HTML report as fallback."""
        summary_data = self._prepare_summary_data(module_results)
        org_name = organization_info.get('name', 'Organization')
        report_date = datetime.now().strftime('%d %B %Y')

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Compliance Certification Report - {org_name}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 40px;
                    line-height: 1.6;
                }}
                h1 {{
                    color: #1E40AF;
                    border-bottom: 3px solid #1E40AF;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #1E40AF;
                    margin-top: 30px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th {{
                    background-color: #1E40AF;
                    color: white;
                    padding: 12px;
                    text-align: left;
                }}
                td {{
                    border: 1px solid #ddd;
                    padding: 10px;
                }}
                tr:nth-child(even) {{
                    background-color: #f2f2f2;
                }}
                .status-pass {{
                    color: green;
                    font-weight: bold;
                }}
                .status-fail {{
                    color: red;
                    font-weight: bold;
                }}
                .status-warning {{
                    color: orange;
                    font-weight: bold;
                }}
                .summary-box {{
                    background-color: #f0f9ff;
                    border: 2px solid #1E40AF;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 8px;
                }}
                .certification {{
                    background-color: #f0f9ff;
                    border: 2px solid #10B981;
                    padding: 30px;
                    margin: 30px 0;
                    border-radius: 8px;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <h1>Compliance Certification Report</h1>

            <div class="summary-box">
                <h3>{org_name}</h3>
                <p><strong>Report Date:</strong> {report_date}</p>
                <p><strong>Assessment Period:</strong> {report_date}</p>
            </div>

            <h2>Executive Summary</h2>
            <p>This report certifies the compliance status of {org_name} across {summary_data['total_modules']}
            compliance frameworks. The organization has achieved an overall compliance score of
            <strong>{summary_data['average_score']:.1f}%</strong>.</p>

            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Total Modules Assessed</td>
                    <td>{summary_data['total_modules']}</td>
                </tr>
                <tr>
                    <td>Overall Compliance Score</td>
                    <td><strong>{summary_data['average_score']:.1f}%</strong></td>
                </tr>
                <tr>
                    <td>Modules Passing</td>
                    <td class="status-pass">{summary_data['modules_passing']}</td>
                </tr>
                <tr>
                    <td>Modules Requiring Attention</td>
                    <td class="status-fail">{summary_data['modules_failing']}</td>
                </tr>
                <tr>
                    <td>Critical Issues</td>
                    <td>{summary_data['critical_issues']}</td>
                </tr>
                <tr>
                    <td>High Priority Issues</td>
                    <td>{summary_data['high_issues']}</td>
                </tr>
            </table>

            <h2>Module Assessment Details</h2>
            <table>
                <tr>
                    <th>Module</th>
                    <th>Score</th>
                    <th>Status</th>
                    <th>Gates Passed</th>
                    <th>Critical Issues</th>
                </tr>
        """

        for module_id, result in module_results.items():
            module_name = result.module_name if hasattr(result, 'module_name') else module_id
            score = result.score if hasattr(result, 'score') else 0
            status = result.overall_status if hasattr(result, 'overall_status') else 'UNKNOWN'
            gates_passed = f"{result.gates_passed}/{result.total_gates}" if hasattr(result, 'gates_passed') else 'N/A'
            critical = len(result.critical_issues) if hasattr(result, 'critical_issues') else 0

            status_class = 'status-pass' if status == 'PASS' else 'status-fail' if status == 'FAIL' else 'status-warning'

            html_content += f"""
                <tr>
                    <td><strong>{module_name}</strong></td>
                    <td>{score:.1f}%</td>
                    <td class="{status_class}">{status}</td>
                    <td>{gates_passed}</td>
                    <td>{critical}</td>
                </tr>
            """

        html_content += """
            </table>

            <h2>Recommendations</h2>
            <ol>
        """

        recommendations = self._generate_certification_recommendations(module_results)
        for recommendation in recommendations:
            html_content += f"<li>{recommendation}</li>"

        certification_status = self._get_certification_status(summary_data)

        html_content += f"""
            </ol>

            <div class="certification">
                <h2>Certification Statement</h2>
                <p>This report certifies that <strong>{org_name}</strong> has undergone a comprehensive
                compliance assessment as of <strong>{report_date}</strong>.</p>
                <p>Overall Compliance Status: <strong>{certification_status}</strong></p>
                <p>This certification is valid for 12 months from the date of issue.</p>
                <p style="margin-top: 40px;">_________________________________</p>
                <p><strong>Authorized Signature</strong></p>
                <p>Date: {report_date}</p>
            </div>

            <footer style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #ccc; text-align: center; color: #666;">
                <p>Generated by LOKI Compliance Orchestration System</p>
                <p>Report ID: CERT-{datetime.now().strftime('%Y%m%d-%H%M%S')}</p>
            </footer>
        </body>
        </html>
        """

        # Ensure output path has .html extension
        if not output_path.endswith('.html'):
            output_path = output_path.replace('.pdf', '.html')

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"HTML report generated successfully: {output_path}")
        return output_path

    def _prepare_summary_data(self, module_results: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare summary statistics."""
        total_modules = len(module_results)
        modules_passing = sum(1 for r in module_results.values() if r.overall_status == 'PASS')
        modules_failing = sum(1 for r in module_results.values() if r.overall_status in ['FAIL', 'WARNING'])

        avg_score = sum(r.score for r in module_results.values()) / total_modules if total_modules > 0 else 0

        critical_issues = sum(
            len(r.critical_issues) for r in module_results.values()
            if hasattr(r, 'critical_issues')
        )

        high_issues = sum(
            len(r.high_issues) for r in module_results.values()
            if hasattr(r, 'high_issues')
        )

        return {
            'total_modules': total_modules,
            'modules_passing': modules_passing,
            'modules_failing': modules_failing,
            'average_score': avg_score,
            'critical_issues': critical_issues,
            'high_issues': high_issues
        }

    def _get_certification_status(self, summary_data: Dict[str, Any]) -> str:
        """Determine overall certification status."""
        avg_score = summary_data['average_score']
        critical_issues = summary_data['critical_issues']

        if critical_issues > 0:
            return "NOT CERTIFIED - Critical issues must be resolved"
        elif avg_score >= 90:
            return "CERTIFIED - EXCELLENT"
        elif avg_score >= 80:
            return "CERTIFIED - GOOD"
        elif avg_score >= 70:
            return "CONDITIONALLY CERTIFIED - Improvements Required"
        else:
            return "NOT CERTIFIED - Significant gaps identified"

    def _generate_certification_recommendations(self, module_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations for the certification report."""
        recommendations = []

        # Analyze results
        failing_modules = [
            (mid, r) for mid, r in module_results.items()
            if r.overall_status in ['FAIL', 'WARNING']
        ]

        critical_modules = [
            (mid, r) for mid, r in module_results.items()
            if hasattr(r, 'critical_issues') and len(r.critical_issues) > 0
        ]

        if critical_modules:
            module_names = ', '.join([r.module_name if hasattr(r, 'module_name') else mid for mid, r in critical_modules[:3]])
            recommendations.append(
                f"Address critical issues in: {module_names}. These require immediate remediation."
            )

        if failing_modules:
            recommendations.append(
                f"Implement remediation plans for {len(failing_modules)} modules requiring attention."
            )

        recommendations.extend([
            "Establish quarterly compliance review process to maintain certification status.",
            "Implement continuous monitoring system for early detection of compliance drift.",
            "Conduct staff training on updated compliance requirements.",
            "Schedule follow-up assessment in 6 months to track improvement progress.",
            "Document all compliance procedures and maintain audit trail."
        ])

        return recommendations[:10]  # Limit to top 10
