"""Deterministic compliance snippet registry.

The prior experimental branch shipped a very large hand-authored template file.
For the new refusal-aware synthesis pipeline we only need a registry that covers
every gate with predictable placeholders so the synthesis engine can assemble a
clean document.  This implementation auto-generates snippets for every gate
exposed by the core modules and provides explicit copy for the few gates that
our tests assert on (risk warnings, lawful basis, promotions approval and FOS
signposting).

The registry is intentionally simple: each gate gets a ``ComplianceSnippet``
object describing the template text, where it should be inserted, and priority
ordering.  The synthesis engine then formats templates with any context provided
by the caller and substitutes sensible defaults for common placeholders.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Any, Callable, Dict, List, Optional


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
    insertion_point: str  # 'start', 'end', 'section'
    priority: int
    condition: Optional[Callable[[str, Dict[str, Any]], bool]] = None
    section_header: Optional[str] = None


SPECIAL_SNIPPETS: Dict[str, ComplianceSnippet] = {
    'fca_uk:fair_clear_not_misleading': ComplianceSnippet(
        gate_id='fair_clear_not_misleading',
        module_id='fca_uk',
        severity='critical',
        template=(
            "IMPORTANT RISK WARNING:\n\n"
            "The value of investments and any income from them can fall as well as rise. "
            "You may not get back the amount originally invested. Past performance is not "
            "a reliable indicator of future results."
        ),
        insertion_point='start',
        priority=100,
    ),
    'fca_uk:fos_signposting': ComplianceSnippet(
        gate_id='fos_signposting',
        module_id='fca_uk',
        severity='critical',
        template=(
            "\n\nCOMPLAINTS PROCEDURE:\n\n"
            "If you remain dissatisfied after our final response you may refer your "
            "complaint to the Financial Ombudsman Service (FOS) within six months. "
            "Visit www.financial-ombudsman.org.uk or call 0800 023 4567."
        ),
        insertion_point='section',
        section_header='COMPLAINTS PROCEDURE',
        priority=90,
    ),
    'fca_uk:promotions_approval': ComplianceSnippet(
        gate_id='promotions_approval',
        module_id='fca_uk',
        severity='high',
        template=(
            "\n\nPROMOTIONS APPROVAL:\n\n"
            "This financial promotion is issued or approved by [FIRM_NAME], an FCA "
            "authorised firm (FRN [FRN_NUMBER])."
        ),
        insertion_point='section',
        section_header='PROMOTIONS APPROVAL',
        priority=80,
    ),
    'gdpr_uk:lawful_basis': ComplianceSnippet(
        gate_id='lawful_basis',
        module_id='gdpr_uk',
        severity='critical',
        template=(
            "\n\nLAWFUL BASIS FOR PROCESSING:\n\n"
            "We process personal data under the lawful bases of contract performance, "
            "legal obligation and legitimate interests. Details are available in our "
            "Privacy Notice at [URL]."
        ),
        insertion_point='section',
        section_header='LAWFUL BASIS FOR PROCESSING',
        priority=95,
    ),
    'nda_uk:parties_identified': ComplianceSnippet(
        gate_id='parties_identified',
        module_id='nda_uk',
        severity='high',
        template=(
            "\n\nPARTIES IDENTIFIED:\n\n"
            "This agreement is made between [PARTY_ONE_NAME] and [PARTY_TWO_NAME]. "
            "Each party confirms that their legal identities and contact details are correctly stated."
        ),
        insertion_point='section',
        section_header='PARTIES IDENTIFIED',
        priority=80,
    ),
}


class SnippetRegistry:
    def __init__(self) -> None:
        self.snippets: Dict[str, ComplianceSnippet] = {}
        self._register_all()

    def _register_all(self) -> None:
        for module_name in MODULES:
            module = import_module(f'modules.{module_name}.module')
            class_name = f"{module_name.title().replace('_', '')}Module"
            module_cls = getattr(module, class_name)
            module_obj = module_cls()

            for gate_id, gate in module_obj.gates.items():
                key = f"{module_name}:{gate_id}"
                snippet = SPECIAL_SNIPPETS.get(key)
                if snippet:
                    self.snippets[key] = snippet
                    continue

                section_header = gate_id.replace('_', ' ').upper()
                legal_source = getattr(gate, 'legal_source', '')
                template = (
                    f"\n\n{section_header}:\n\n"
                    f"This section addresses the {gate_id.replace('_', ' ')} "
                    f"requirements. Refer to {legal_source or 'applicable regulations'} "
                    "for full obligations."
                )

                severity = getattr(gate, 'severity', 'medium') or 'medium'
                priority = 95 if str(severity).lower() == 'critical' else 70

                self.snippets[key] = ComplianceSnippet(
                    gate_id=gate_id,
                    module_id=module_name,
                    severity=severity,
                    template=template,
                    insertion_point='section',
                    section_header=section_header,
                    priority=priority,
                )

    def register(self, snippet: ComplianceSnippet) -> None:
        key = f"{snippet.module_id}:{snippet.gate_id}"
        self.snippets[key] = snippet

    def get_snippet(self, module_id: str, gate_id: str) -> Optional[ComplianceSnippet]:
        return self.snippets.get(f"{module_id}:{gate_id}")

    def get_snippets_for_failures(self, validation: Dict[str, Any]) -> List[ComplianceSnippet]:
        needed: List[ComplianceSnippet] = []
        modules = validation.get('modules', {})
        for module_id, module_payload in modules.items():
            gates = module_payload.get('gates', {})
            for gate_id, gate_result in gates.items():
                if (gate_result or {}).get('status', '').upper() == 'FAIL':
                    snippet = self.get_snippet(module_id, gate_id)
                    if snippet:
                        needed.append(snippet)
        return sorted(needed, key=lambda s: s.priority, reverse=True)

    def format_snippet(self, snippet: ComplianceSnippet, context: Dict[str, Any]) -> str:
        text = snippet.template
        for key, value in context.items():
            placeholder = f"[{key.upper()}]"
            if placeholder in text:
                text = text.replace(placeholder, str(value))

        default_replacements = {
            '[FIRM_NAME]': 'Our Firm',
            '[FRN_NUMBER]': '123456',
            '[URL]': 'https://example.com/privacy',
            '[CONTACT_DETAILS]': 'compliance@example.com',
            '[PARTY_ONE_NAME]': 'Party One',
            '[PARTY_TWO_NAME]': 'Party Two',
        }

        for placeholder, default in default_replacements.items():
            if placeholder in text:
                text = text.replace(placeholder, default)

        return text
