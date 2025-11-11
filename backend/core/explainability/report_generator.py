"""
Report Generator
Creates professional correction reports in multiple formats
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from dataclasses import asdict


class ReportGenerator:
    """
    Generates comprehensive correction reports

    Features:
    - Multiple output formats (JSON, HTML, PDF-ready, Markdown)
    - Professional styling and layout
    - Interactive visualizations
    - Export capabilities
    """

    def __init__(self):
        self.templates = self._load_templates()

    def generate_report(
        self,
        explanation_data: Dict[str, Any],
        impact_data: Dict[str, Any],
        reasoning_chain: Dict[str, Any],
        confidence_breakdown: Dict[str, Any],
        citations: List[Dict[str, Any]],
        format: str = 'html'
    ) -> str:
        """
        Generate comprehensive correction report

        Args:
            explanation_data: Explanation details
            impact_data: Impact analysis
            reasoning_chain: Reasoning steps
            confidence_breakdown: Confidence analysis
            citations: Legal citations
            format: Output format (html, json, markdown, pdf_ready)

        Returns:
            Formatted report string
        """
        if format == 'json':
            return self._generate_json_report(
                explanation_data, impact_data, reasoning_chain,
                confidence_breakdown, citations
            )
        elif format == 'html':
            return self._generate_html_report(
                explanation_data, impact_data, reasoning_chain,
                confidence_breakdown, citations
            )
        elif format == 'markdown':
            return self._generate_markdown_report(
                explanation_data, impact_data, reasoning_chain,
                confidence_breakdown, citations
            )
        elif format == 'pdf_ready':
            return self._generate_pdf_ready_html(
                explanation_data, impact_data, reasoning_chain,
                confidence_breakdown, citations
            )
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _generate_json_report(
        self,
        explanation: Dict[str, Any],
        impact: Dict[str, Any],
        reasoning: Dict[str, Any],
        confidence: Dict[str, Any],
        citations: List[Dict[str, Any]]
    ) -> str:
        """Generate JSON format report"""
        report = {
            'report_metadata': {
                'generated_at': datetime.utcnow().isoformat(),
                'version': '1.0',
                'report_type': 'correction_explanation'
            },
            'explanation': explanation,
            'impact_analysis': impact,
            'reasoning_chain': reasoning,
            'confidence_breakdown': confidence,
            'legal_citations': citations
        }
        return json.dumps(report, indent=2)

    def _generate_html_report(
        self,
        explanation: Dict[str, Any],
        impact: Dict[str, Any],
        reasoning: Dict[str, Any],
        confidence: Dict[str, Any],
        citations: List[Dict[str, Any]]
    ) -> str:
        """Generate interactive HTML report"""

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LOKI Correction Explainability Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f7fa;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 40px;
            border-radius: 8px 8px 0 0;
        }}

        .header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
        }}

        .header .subtitle {{
            font-size: 16px;
            opacity: 0.9;
        }}

        .content {{
            padding: 40px;
        }}

        .section {{
            margin-bottom: 40px;
        }}

        .section-title {{
            font-size: 24px;
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e0e7ff;
        }}

        .correction-box {{
            background: #f8fafc;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
        }}

        .correction-box .label {{
            font-weight: 600;
            color: #64748b;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}

        .correction-box .text {{
            font-size: 16px;
            line-height: 1.8;
        }}

        .original {{
            text-decoration: line-through;
            color: #ef4444;
            background: #fef2f2;
            padding: 2px 4px;
            border-radius: 3px;
        }}

        .corrected {{
            color: #10b981;
            background: #f0fdf4;
            padding: 2px 4px;
            border-radius: 3px;
            font-weight: 500;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}

        .stat-card {{
            background: #f8fafc;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }}

        .stat-card .value {{
            font-size: 32px;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 5px;
        }}

        .stat-card .label {{
            font-size: 14px;
            color: #64748b;
        }}

        .confidence-bar {{
            background: #e2e8f0;
            height: 30px;
            border-radius: 15px;
            overflow: hidden;
            margin: 10px 0;
        }}

        .confidence-fill {{
            background: linear-gradient(90deg, #10b981 0%, #059669 100%);
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            font-size: 14px;
            transition: width 0.3s ease;
        }}

        .reasoning-step {{
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
        }}

        .reasoning-step .step-header {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }}

        .step-number {{
            background: #667eea;
            color: white;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            margin-right: 15px;
        }}

        .step-question {{
            font-size: 18px;
            font-weight: 600;
            color: #1e293b;
        }}

        .step-content {{
            margin-left: 47px;
        }}

        .step-content p {{
            margin: 10px 0;
        }}

        .step-label {{
            font-weight: 600;
            color: #64748b;
            font-size: 13px;
            margin-top: 15px;
        }}

        .evidence-list {{
            list-style: none;
            margin: 10px 0;
        }}

        .evidence-list li {{
            padding: 8px 12px;
            background: #f8fafc;
            margin: 5px 0;
            border-left: 3px solid #667eea;
            border-radius: 3px;
        }}

        .citation {{
            background: #fffbeb;
            border: 1px solid #fde68a;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
        }}

        .citation-title {{
            font-weight: 700;
            color: #92400e;
            margin-bottom: 10px;
        }}

        .citation-ref {{
            color: #b45309;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            margin-bottom: 10px;
        }}

        .citation-url {{
            color: #2563eb;
            text-decoration: none;
            font-size: 14px;
        }}

        .citation-url:hover {{
            text-decoration: underline;
        }}

        .impact-item {{
            background: white;
            border-left: 4px solid #f59e0b;
            padding: 15px 20px;
            margin: 10px 0;
            border-radius: 4px;
        }}

        .impact-severity {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }}

        .severity-critical {{
            background: #fee2e2;
            color: #991b1b;
        }}

        .severity-high {{
            background: #fef3c7;
            color: #92400e;
        }}

        .severity-medium {{
            background: #dbeafe;
            color: #1e40af;
        }}

        .severity-low {{
            background: #d1fae5;
            color: #065f46;
        }}

        .action-list {{
            list-style: none;
        }}

        .action-list li {{
            padding: 12px 16px;
            margin: 8px 0;
            background: #f8fafc;
            border-left: 4px solid #667eea;
            border-radius: 4px;
        }}

        .action-timeline {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            margin-left: 10px;
        }}

        .footer {{
            background: #f8fafc;
            padding: 30px 40px;
            border-radius: 0 0 8px 8px;
            text-align: center;
            color: #64748b;
            font-size: 14px;
        }}

        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 Correction Explainability Report</h1>
            <div class="subtitle">Generated by LOKI Enterprise Compliance Platform • {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</div>
        </div>

        <div class="content">
            <!-- Correction Overview -->
            <div class="section">
                <h2 class="section-title">Correction Overview</h2>

                <div class="correction-box">
                    <div class="label">Original Text</div>
                    <div class="text">
                        <span class="original">{explanation.get('original_text', 'N/A')}</span>
                    </div>
                </div>

                <div class="correction-box">
                    <div class="label">Corrected Text</div>
                    <div class="text">
                        <span class="corrected">{explanation.get('corrected_text', 'N/A')}</span>
                    </div>
                </div>

                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="value">{explanation.get('confidence', {}).get('score', 0):.0%}</div>
                        <div class="label">Confidence</div>
                    </div>
                    <div class="stat-card">
                        <div class="value">{impact.get('risk_assessment', {}).get('reduction', '0%')}</div>
                        <div class="label">Risk Reduction</div>
                    </div>
                    <div class="stat-card">
                        <div class="value">{len(reasoning.get('steps', []))}</div>
                        <div class="label">Reasoning Steps</div>
                    </div>
                    <div class="stat-card">
                        <div class="value">{len(citations)}</div>
                        <div class="label">Legal Citations</div>
                    </div>
                </div>
            </div>

            <!-- Explanation -->
            <div class="section">
                <h2 class="section-title">Why This Correction?</h2>
                <p style="font-size: 16px; line-height: 1.8; color: #475569;">
                    {explanation.get('reason', 'N/A')}
                </p>

                <div style="margin-top: 20px;">
                    <strong style="color: #667eea;">Legal Basis:</strong><br>
                    {explanation.get('legal_basis', 'N/A')}
                </div>
            </div>

            <!-- Confidence Analysis -->
            <div class="section">
                <h2 class="section-title">Confidence Analysis</h2>

                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: {confidence.get('total_score', 0) * 100}%;">
                        {confidence.get('total_score', 0):.0%} Confidence
                    </div>
                </div>

                <p style="margin: 20px 0; font-size: 16px; line-height: 1.8;">
                    {confidence.get('reasoning', 'N/A')}
                </p>

                <div style="margin-top: 20px;">
                    <strong style="color: #667eea;">Recommendation:</strong><br>
                    {confidence.get('recommendation', 'N/A')}
                </div>
            </div>

            <!-- Reasoning Chain -->
            <div class="section">
                <h2 class="section-title">Reasoning Chain</h2>
                <p style="margin-bottom: 20px; color: #64748b;">
                    Step-by-step logical analysis of how this correction was determined:
                </p>

                {self._render_reasoning_steps(reasoning.get('steps', []))}
            </div>

            <!-- Legal Citations -->
            <div class="section">
                <h2 class="section-title">Legal Citations</h2>
                {self._render_citations(citations)}
            </div>

            <!-- Impact Analysis -->
            <div class="section">
                <h2 class="section-title">Impact Analysis</h2>

                <div style="margin-bottom: 30px;">
                    <h3 style="color: #1e293b; margin-bottom: 15px;">Risk Assessment</h3>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="value" style="color: #ef4444;">{impact.get('risk_assessment', {}).get('before', '0%')}</div>
                            <div class="label">Risk Before</div>
                        </div>
                        <div class="stat-card">
                            <div class="value" style="color: #10b981;">{impact.get('risk_assessment', {}).get('after', '0%')}</div>
                            <div class="label">Risk After</div>
                        </div>
                    </div>
                </div>

                <div style="margin-bottom: 30px;">
                    <h3 style="color: #1e293b; margin-bottom: 15px;">Affected Areas</h3>
                    {self._render_impact_areas(impact.get('downstream_effects', {}))}
                </div>

                <div>
                    <h3 style="color: #1e293b; margin-bottom: 15px;">Action Plan</h3>
                    {self._render_action_plan(impact.get('action_plan', {}))}
                </div>
            </div>
        </div>

        <div class="footer">
            <p><strong>LOKI Enterprise Compliance Platform</strong></p>
            <p>This report provides transparent explainability for all document corrections.</p>
            <p>For questions, contact your compliance team.</p>
        </div>
    </div>
</body>
</html>"""

        return html

    def _render_reasoning_steps(self, steps: List[Dict[str, Any]]) -> str:
        """Render reasoning steps as HTML"""
        if not steps:
            return "<p>No reasoning steps available.</p>"

        html_parts = []
        for step in steps:
            html_parts.append(f"""
                <div class="reasoning-step">
                    <div class="step-header">
                        <div class="step-number">{step.get('step_number', '?')}</div>
                        <div class="step-question">{step.get('question', 'N/A')}</div>
                    </div>
                    <div class="step-content">
                        <p><strong>Process:</strong> {step.get('process', 'N/A')}</p>
                        <p><strong>Result:</strong> {step.get('output', 'N/A')}</p>
                        <p><strong>Reasoning:</strong> {step.get('reasoning', 'N/A')}</p>

                        <div class="step-label">Evidence:</div>
                        <ul class="evidence-list">
                            {''.join(f'<li>{e}</li>' for e in step.get('evidence', []))}
                        </ul>

                        <p style="margin-top: 15px;">
                            <span class="step-label">Confidence:</span>
                            <strong style="color: #10b981;">{step.get('confidence', 0):.0%}</strong>
                        </p>
                    </div>
                </div>
            """)

        return ''.join(html_parts)

    def _render_citations(self, citations: List[Dict[str, Any]]) -> str:
        """Render legal citations as HTML"""
        if not citations:
            return "<p>No legal citations available.</p>"

        html_parts = []
        for citation in citations:
            html_parts.append(f"""
                <div class="citation">
                    <div class="citation-title">{citation.get('title', 'N/A')}</div>
                    <div class="citation-ref">{citation.get('reference', 'N/A')}</div>
                    <p style="margin: 10px 0; font-style: italic;">
                        "{citation.get('excerpt', 'N/A')}"
                    </p>
                    <p style="margin: 10px 0;">
                        <strong>Relevance:</strong> {citation.get('relevance', 'N/A')}
                    </p>
                    <a href="{citation.get('url', '#')}" class="citation-url" target="_blank">
                        View Full Text →
                    </a>
                </div>
            """)

        return ''.join(html_parts)

    def _render_impact_areas(self, downstream: Dict[str, Any]) -> str:
        """Render impact areas"""
        areas = []

        if downstream.get('document_sections'):
            areas.append(f"""
                <div style="margin: 15px 0;">
                    <strong>Document Sections:</strong>
                    <ul style="margin: 10px 0 0 20px;">
                        {''.join(f'<li>{s}</li>' for s in downstream.get('document_sections', []))}
                    </ul>
                </div>
            """)

        if downstream.get('related_documents'):
            areas.append(f"""
                <div style="margin: 15px 0;">
                    <strong>Related Documents:</strong>
                    <ul style="margin: 10px 0 0 20px;">
                        {''.join(f'<li>{d}</li>' for d in downstream.get('related_documents', []))}
                    </ul>
                </div>
            """)

        return ''.join(areas) if areas else "<p>No downstream impacts identified.</p>"

    def _render_action_plan(self, action_plan: Dict[str, Any]) -> str:
        """Render action plan"""
        html_parts = []

        if action_plan.get('immediate'):
            html_parts.append("""
                <h4 style="color: #ef4444; margin-top: 20px;">Immediate Actions</h4>
                <ul class="action-list">
            """)
            for action in action_plan.get('immediate', []):
                html_parts.append(f'<li>{action}<span class="action-timeline">NOW</span></li>')
            html_parts.append('</ul>')

        if action_plan.get('short_term'):
            html_parts.append("""
                <h4 style="color: #f59e0b; margin-top: 20px;">Short-term Actions (1 week)</h4>
                <ul class="action-list">
            """)
            for action in action_plan.get('short_term', []):
                html_parts.append(f'<li>{action}<span class="action-timeline">1 WEEK</span></li>')
            html_parts.append('</ul>')

        return ''.join(html_parts)

    def _generate_markdown_report(
        self,
        explanation: Dict[str, Any],
        impact: Dict[str, Any],
        reasoning: Dict[str, Any],
        confidence: Dict[str, Any],
        citations: List[Dict[str, Any]]
    ) -> str:
        """Generate Markdown format report"""

        md = f"""# Correction Explainability Report

**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

## Correction Overview

### Original Text
```
{explanation.get('original_text', 'N/A')}
```

### Corrected Text
```
{explanation.get('corrected_text', 'N/A')}
```

### Key Metrics
- **Confidence:** {explanation.get('confidence', {}).get('score', 0):.0%}
- **Risk Reduction:** {impact.get('risk_assessment', {}).get('reduction', '0%')}
- **Reasoning Steps:** {len(reasoning.get('steps', []))}
- **Legal Citations:** {len(citations)}

## Explanation

{explanation.get('reason', 'N/A')}

**Legal Basis:** {explanation.get('legal_basis', 'N/A')}

## Confidence Analysis

**Score:** {confidence.get('total_score', 0):.0%}

{confidence.get('reasoning', 'N/A')}

**Recommendation:** {confidence.get('recommendation', 'N/A')}

## Reasoning Chain

{self._render_reasoning_markdown(reasoning.get('steps', []))}

## Legal Citations

{self._render_citations_markdown(citations)}

## Impact Analysis

### Risk Assessment
- **Before:** {impact.get('risk_assessment', {}).get('before', '0%')}
- **After:** {impact.get('risk_assessment', {}).get('after', '0%')}
- **Reduction:** {impact.get('risk_assessment', {}).get('reduction', '0%')}

### Action Plan

{self._render_action_plan_markdown(impact.get('action_plan', {}))}

---

*Generated by LOKI Enterprise Compliance Platform*
"""

        return md

    def _render_reasoning_markdown(self, steps: List[Dict[str, Any]]) -> str:
        """Render reasoning steps as Markdown"""
        if not steps:
            return "No reasoning steps available."

        md_parts = []
        for step in steps:
            md_parts.append(f"""
### Step {step.get('step_number', '?')}: {step.get('question', 'N/A')}

**Process:** {step.get('process', 'N/A')}

**Result:** {step.get('output', 'N/A')}

**Reasoning:** {step.get('reasoning', 'N/A')}

**Evidence:**
{chr(10).join(f'- {e}' for e in step.get('evidence', []))}

**Confidence:** {step.get('confidence', 0):.0%}
""")

        return '\n'.join(md_parts)

    def _render_citations_markdown(self, citations: List[Dict[str, Any]]) -> str:
        """Render citations as Markdown"""
        if not citations:
            return "No legal citations available."

        md_parts = []
        for i, citation in enumerate(citations, 1):
            md_parts.append(f"""
### {i}. {citation.get('title', 'N/A')}

**Reference:** {citation.get('reference', 'N/A')}

> {citation.get('excerpt', 'N/A')}

**Relevance:** {citation.get('relevance', 'N/A')}

**Link:** [{citation.get('url', 'N/A')}]({citation.get('url', '#')})
""")

        return '\n'.join(md_parts)

    def _render_action_plan_markdown(self, action_plan: Dict[str, Any]) -> str:
        """Render action plan as Markdown"""
        md_parts = []

        if action_plan.get('immediate'):
            md_parts.append("#### Immediate Actions\n")
            for action in action_plan.get('immediate', []):
                md_parts.append(f"- [ ] {action}\n")

        if action_plan.get('short_term'):
            md_parts.append("\n#### Short-term Actions (1 week)\n")
            for action in action_plan.get('short_term', []):
                md_parts.append(f"- [ ] {action}\n")

        return ''.join(md_parts)

    def _generate_pdf_ready_html(
        self,
        explanation: Dict[str, Any],
        impact: Dict[str, Any],
        reasoning: Dict[str, Any],
        confidence: Dict[str, Any],
        citations: List[Dict[str, Any]]
    ) -> str:
        """Generate PDF-ready HTML (optimized for print)"""
        # Reuse HTML generation but add print-specific CSS
        return self._generate_html_report(
            explanation, impact, reasoning, confidence, citations
        )

    def _load_templates(self) -> Dict[str, str]:
        """Load report templates"""
        return {
            'html': 'html_template',
            'markdown': 'markdown_template',
            'json': 'json_template'
        }
