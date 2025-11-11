"""
Prompt Templates Library Module

Provides reusable prompt templates and patterns:
- Template definitions
- Template filling and validation
- Template versioning
- Template performance tracking
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import re


@dataclass
class PromptTemplate:
    """A reusable prompt template"""
    id: str
    name: str
    description: str
    template: str  # Template with {variable} placeholders
    required_variables: List[str] = field(default_factory=list)
    optional_variables: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    category: str = "general"
    version: str = "1.0"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    usage_count: int = 0
    average_quality_score: float = 0.0
    metadata: Dict = field(default_factory=dict)

    def fill(self, variables: Dict[str, str]) -> str:
        """
        Fill template with variables

        Args:
            variables: Dict of variable names to values

        Returns:
            Filled prompt string
        """
        # Validate required variables
        missing = [v for v in self.required_variables if v not in variables]
        if missing:
            raise ValueError(f"Missing required variables: {missing}")

        # Fill template
        filled = self.template
        for var_name, value in variables.items():
            placeholder = f"{{{var_name}}}"
            filled = filled.replace(placeholder, str(value))

        # Warn about unfilled optional variables
        remaining_placeholders = re.findall(r'\{(\w+)\}', filled)
        if remaining_placeholders:
            # Fill with empty strings
            for placeholder in remaining_placeholders:
                filled = filled.replace(f"{{{placeholder}}}", "")

        return filled.strip()

    def validate_variables(self, variables: Dict[str, str]) -> bool:
        """Check if variables are valid"""
        for req_var in self.required_variables:
            if req_var not in variables or not variables[req_var]:
                return False
        return True


class PromptTemplateLibrary:
    """
    Library of reusable prompt templates

    Features:
    - Template management
    - Template composition
    - Performance tracking
    - Template recommendations
    """

    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}
        self.usage_log: List[Dict] = []
        self._load_default_templates()

    def _load_default_templates(self):
        """Load default templates"""
        # Analysis template
        self.add_template(PromptTemplate(
            id="analyze_document",
            name="Document Analysis",
            description="Analyze a document for key information",
            template="""Analyze the following document and provide insights:

Document Type: {document_type}
Document Content: {content}

Please provide:
1. Key findings
2. Important patterns
3. Recommendations
4. Risk assessment

Format your response with clear sections.""",
            required_variables=["document_type", "content"],
            optional_variables=["focus_areas"],
            category="analysis",
            examples=[
                "analyze_document(document_type='contract', content='...')",
                "analyze_document(document_type='policy', content='...')"
            ]
        ))

        # Compliance check template
        self.add_template(PromptTemplate(
            id="check_compliance",
            name="Compliance Checker",
            description="Check content for compliance with regulations",
            template="""Check the following content for compliance with {regulation}:

Content: {content}

Provide:
1. Compliance status (PASS/FAIL/REVIEW)
2. Issues found
3. Recommended corrections
4. References to specific requirements""",
            required_variables=["regulation", "content"],
            category="compliance",
            examples=[
                "check_compliance(regulation='GDPR', content='...')",
                "check_compliance(regulation='HIPAA', content='...')"
            ]
        ))

        # Correction template
        self.add_template(PromptTemplate(
            id="correct_content",
            name="Content Corrector",
            description="Correct and improve content",
            template="""Correct and improve the following content:

Original Content: {content}

Focus areas: {focus_areas}

Provide:
1. Corrected version
2. Changes made
3. Explanations
4. Quality assessment""",
            required_variables=["content"],
            optional_variables=["focus_areas"],
            category="correction",
            examples=[
                "correct_content(content='...', focus_areas='grammar')",
                "correct_content(content='...')"
            ]
        ))

        # Summary template
        self.add_template(PromptTemplate(
            id="summarize_content",
            name="Content Summarizer",
            description="Create executive summary of content",
            template="""Create a {style} summary of the following content:

Content: {content}

Requirements:
- Length: {length}
- Style: {style}
- Include key points: {include_key_points}

Provide summary in the requested format.""",
            required_variables=["content"],
            optional_variables=["style", "length", "include_key_points"],
            category="summarization",
            examples=[
                "summarize_content(content='...', style='executive', length='brief')",
                "summarize_content(content='...')"
            ]
        ))

        # Extraction template
        self.add_template(PromptTemplate(
            id="extract_information",
            name="Information Extractor",
            description="Extract specific information from content",
            template="""Extract the following information from the content:

Content: {content}

Information to extract: {information_types}

Format: {format_preference}

Return only the extracted information in the specified format.""",
            required_variables=["content", "information_types"],
            optional_variables=["format_preference"],
            category="extraction",
            examples=[
                "extract_information(content='...', information_types='names,dates,amounts')"
            ]
        ))

    def add_template(self, template: PromptTemplate) -> PromptTemplate:
        """Add template to library"""
        self.templates[template.id] = template
        return template

    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """Get template by ID"""
        return self.templates.get(template_id)

    def list_templates(
        self,
        category: Optional[str] = None
    ) -> List[PromptTemplate]:
        """List available templates"""
        templates = list(self.templates.values())

        if category:
            templates = [t for t in templates if t.category == category]

        return sorted(templates, key=lambda t: t.usage_count, reverse=True)

    def use_template(
        self,
        template_id: str,
        variables: Dict[str, str]
    ) -> str:
        """
        Use a template to generate prompt

        Args:
            template_id: ID of template
            variables: Variables to fill

        Returns:
            Generated prompt
        """
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")

        if not template.validate_variables(variables):
            raise ValueError(f"Invalid variables for template {template_id}")

        # Generate prompt
        prompt = template.fill(variables)

        # Log usage
        self._log_usage(template_id, variables)

        return prompt

    def get_recommended_template(
        self,
        task_description: str
    ) -> Optional[PromptTemplate]:
        """
        Get recommended template for task

        Args:
            task_description: Description of task

        Returns:
            Recommended template or None
        """
        task_lower = task_description.lower()

        # Simple keyword matching
        recommendations = {
            ("analyze", "document"): "analyze_document",
            ("compliance", "check"): "check_compliance",
            ("correct", "fix"): "correct_content",
            ("summary", "summarize"): "summarize_content",
            ("extract", "extraction"): "extract_information"
        }

        for keywords, template_id in recommendations.items():
            if any(kw in task_lower for kw in keywords):
                return self.get_template(template_id)

        return None

    def create_composite_template(
        self,
        name: str,
        sub_templates: List[str],
        instructions: str
    ) -> PromptTemplate:
        """
        Create composite template from multiple templates

        Args:
            name: Name of composite template
            sub_templates: List of template IDs to compose
            instructions: Instructions for composition

        Returns:
            New composite template
        """
        parts = []
        variables = set()

        for template_id in sub_templates:
            template = self.get_template(template_id)
            if template:
                parts.append(f"[{template.name}]\n{template.template}")
                variables.update(template.required_variables)
                variables.update(template.optional_variables)

        composite_template = f"""{instructions}

{chr(10).join(parts)}

Please follow the above instructions and templates."""

        composite = PromptTemplate(
            id=f"composite_{len(self.templates)}",
            name=name,
            description=f"Composite of: {', '.join(sub_templates)}",
            template=composite_template,
            required_variables=list(variables),
            category="composite",
            version="1.0",
            metadata={"sub_templates": sub_templates}
        )

        self.add_template(composite)
        return composite

    def update_template_score(
        self,
        template_id: str,
        quality_score: float
    ):
        """Update quality score for template"""
        template = self.get_template(template_id)
        if template:
            # Update weighted average
            total_uses = template.usage_count
            current_avg = template.average_quality_score

            new_avg = (
                (current_avg * total_uses + quality_score) /
                (total_uses + 1)
            )

            template.average_quality_score = new_avg

    def _log_usage(self, template_id: str, variables: Dict[str, str]):
        """Log template usage"""
        template = self.get_template(template_id)
        if template:
            template.usage_count += 1

        self.usage_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "template_id": template_id,
            "variables_count": len(variables)
        })

        # Keep log bounded
        if len(self.usage_log) > 10000:
            self.usage_log = self.usage_log[-5000:]

    def get_statistics(self) -> Dict:
        """Get template library statistics"""
        total_templates = len(self.templates)
        total_uses = sum(t.usage_count for t in self.templates.values())

        avg_quality = (
            sum(t.average_quality_score for t in self.templates.values()) / total_templates
            if total_templates > 0 else 0
        )

        by_category = {}
        for template in self.templates.values():
            cat = template.category
            if cat not in by_category:
                by_category[cat] = 0
            by_category[cat] += 1

        return {
            "total_templates": total_templates,
            "total_uses": total_uses,
            "average_quality_score": avg_quality,
            "by_category": by_category,
            "most_used": max(
                ((t.id, t.usage_count) for t in self.templates.values()),
                key=lambda x: x[1],
                default=(None, 0)
            )[0]
        }

    def export_templates(self, filepath: str):
        """Export templates to file"""
        import json

        templates_data = [
            {
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "template": t.template,
                "category": t.category,
                "version": t.version,
                "usage_count": t.usage_count,
                "average_quality_score": t.average_quality_score
            }
            for t in self.templates.values()
        ]

        with open(filepath, 'w') as f:
            json.dump(templates_data, f, indent=2)

    def import_templates(self, filepath: str):
        """Import templates from file"""
        import json

        with open(filepath, 'r') as f:
            templates_data = json.load(f)

        for data in templates_data:
            template = PromptTemplate(
                id=data["id"],
                name=data["name"],
                description=data["description"],
                template=data["template"],
                category=data.get("category", "imported"),
                version=data.get("version", "1.0"),
                usage_count=data.get("usage_count", 0),
                average_quality_score=data.get("average_quality_score", 0.0)
            )
            self.add_template(template)
