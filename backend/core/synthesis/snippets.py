"""Deterministic compliance snippet registry built on domain templates."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .domain_templates import DOMAIN_TEMPLATES, MODULE_TAXONOMY

MODULES = [
    'fca_uk',
    'gdpr_uk',
    'hr_scottish',
    'nda_uk',
    'tax_uk',
]


@dataclass
class ComplianceSnippet:
    gate_id: str
    module_id: str
    severity: str
    template: str
    insertion_point: str
    priority: int
    section_header: Optional[str] = None


SPECIAL_SNIPPETS = {
    'fca_uk:fair_clear_not_misleading': ComplianceSnippet(
        gate_id='fair_clear_not_misleading',
        module_id='fca_uk',
        severity='critical',
        template="""IMPORTANT RISK WARNING:

The value of investments and any income from them can fall as well as rise. You may not get back the amount originally invested. Past performance is not a reliable indicator of future results.""",
        insertion_point='start',
        priority=100,
        section_header='IMPORTANT RISK WARNING',
    ),
    'fca_uk:fos_signposting': ComplianceSnippet(
        gate_id='fos_signposting',
        module_id='fca_uk',
        severity='critical',
        template="""

FINANCIAL OMBUDSMAN SERVICE:

If you remain dissatisfied after our final response you may refer your complaint to the Financial Ombudsman Service (FOS) within six months. Visit financial-ombudsman.org.uk or call 0800 023 4567.""",
        insertion_point='section',
        priority=90,
        section_header='FINANCIAL OMBUDSMAN SERVICE',
    ),
    'fca_uk:promotions_approval': ComplianceSnippet(
        gate_id='promotions_approval',
        module_id='fca_uk',
        severity='critical',
        template="""

REGULATORY APPROVAL:

This financial promotion has been approved by [FIRM_NAME] (FRN: [FRN_NUMBER]), which is authorised and regulated by the Financial Conduct Authority.""",
        insertion_point='end',
        priority=95,
        section_header='REGULATORY APPROVAL',
    ),
    'gdpr_uk:lawful_basis': ComplianceSnippet(
        gate_id='lawful_basis',
        module_id='gdpr_uk',
        severity='critical',
        template="""

DATA PROCESSING:

We process your personal data in accordance with the UK GDPR and Data Protection Act 2018. Our lawful basis for processing is set out in our privacy policy available at [URL]. For more information, contact [CONTACT_DETAILS].""",
        insertion_point='section',
        priority=95,
        section_header='DATA PROCESSING',
    ),
}

class SnippetRegistry:
    def __init__(self) -> None:
        self.domain_templates = self._load_domain_templates()
        self.module_catalog = self._load_module_catalog()
        self._snippets_cache = None  # Lazy-loaded compatibility layer

    @property
    def snippets(self) -> Dict[str, ComplianceSnippet]:
        """Legacy API compatibility: Return dict of all snippets keyed by 'module:gate'"""
        if self._snippets_cache is None:
            self._snippets_cache = self._build_snippets_cache()
        return self._snippets_cache

    def _build_snippets_cache(self) -> Dict[str, ComplianceSnippet]:
        """Build complete snippet cache for all gates"""
        cache = {}

        # Add special snippets first
        for key, snippet in SPECIAL_SNIPPETS.items():
            cache[key] = snippet

        # Add all module catalog snippets
        for module_id, gates in self.module_catalog.items():
            for gate_id, meta in gates.items():
                key = f"{module_id}:{gate_id}"
                if key not in cache:  # Don't overwrite special snippets
                    snippet = self.build_snippet(
                        meta['domain'],
                        meta.get('variant'),
                        meta.get('context', {}),
                        meta
                    )
                    if snippet:
                        cache[key] = snippet

        return cache

    def _load_domain_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load comprehensive domain templates from domain_templates.py"""
        return DOMAIN_TEMPLATES

    def _load_module_catalog(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Load comprehensive module taxonomy from domain_templates.py"""
        return MODULE_TAXONOMY

    def build_snippet(
        self,
        domain: str,
        variant: Optional[str],
        context: Dict[str, Any],
        gate_metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[ComplianceSnippet]:
        """Build snippet from Codex's DOMAIN_TEMPLATES structure"""
        domain_conf = self.domain_templates.get(domain)
        if not domain_conf:
            return None

        # Get variant template or fall back to first available
        variant_conf = None
        if variant and variant in domain_conf:
            variant_conf = domain_conf[variant]
        else:
            # Fall back to first variant in domain
            variant_conf = next(iter(domain_conf.values())) if domain_conf else None

        if not variant_conf:
            return None

        # Merge default_context with provided context
        base_context = dict(variant_conf.get('default_context', {}))
        base_context.update(context)

        # Format template with merged context
        template_text = variant_conf['template']
        try:
            formatted_template = template_text.format(**base_context)
        except KeyError:
            # If formatting fails, use template as-is
            formatted_template = template_text

        # Extract metadata
        meta = gate_metadata or {}
        gate_id = meta.get('gate_id', context.get('gate_id', 'generic_gate'))
        module_id = meta.get('module_id', context.get('module_id', 'generic_module'))
        severity = (meta.get('severity') or context.get('severity') or 'MEDIUM').lower()
        insertion_point = meta.get('insertion_point', context.get('insertion_point', 'section'))
        priority = meta.get('priority', 95 if severity == 'critical' else 75)

        return ComplianceSnippet(
            gate_id=gate_id,
            module_id=module_id,
            severity=severity,
            template=formatted_template,
            insertion_point=insertion_point,
            priority=priority,
            section_header=base_context.get('section_header', self._default_section_header(domain)),
        )

    def get_snippet(self, module_id: str, gate_id: str) -> Optional[ComplianceSnippet]:
        override = SPECIAL_SNIPPETS.get(f"{module_id}:{gate_id}")
        if override:
            return override
        meta = self.module_catalog.get(module_id, {}).get(gate_id)
        if not meta:
            return None
        return self.build_snippet(meta['domain'], meta.get('variant'), meta.get('context', {}), meta)

    def get_snippets_for_failures(self, validation: Dict[str, Any]) -> List[ComplianceSnippet]:
        needed: List[ComplianceSnippet] = []
        for module_id, module_payload in (validation.get('modules') or {}).items():
            for gate_id, gate_result in (module_payload.get('gates') or {}).items():
                if (gate_result or {}).get('status', '').upper() == 'FAIL':
                    snippet = self.get_snippet(module_id, gate_id)
                    if snippet:
                        needed.append(snippet)
        return sorted(needed, key=lambda s: s.priority, reverse=True)

    def format_snippet(self, snippet: ComplianceSnippet, context: Dict[str, Any]) -> str:
        text = snippet.template
        replacements = {
            '[FIRM_NAME]': context.get('firm_name', 'Our Firm'),
            '[FRN_NUMBER]': context.get('frn_number', '123456'),
            '[URL]': context.get('url', 'https://example.com'),
            '[CONTACT_DETAILS]': context.get('contact_details', 'support@example.com'),
            '[PARTY_ONE_NAME]': context.get('party_one_name', 'Party One'),
            '[PARTY_TWO_NAME]': context.get('party_two_name', 'Party Two'),
        }
        for placeholder, value in replacements.items():
            text = text.replace(placeholder, value)
        return text

    def _default_section_header(self, domain: str) -> str:
        return {
            'disclosure': 'DISCLOSURE',
            'risk_warning': 'RISK WARNING',
            'consent': 'CONSENT & PREFERENCES',
            'procedure': 'PROCEDURE',
            'definition': 'DEFINITIONS',
            'limitation': 'LIMITATIONS',
        }.get(domain, 'INFORMATION')
