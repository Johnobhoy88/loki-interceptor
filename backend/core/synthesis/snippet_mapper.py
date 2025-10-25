from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from .domain_templates import DOMAIN_TEMPLATES, MODULE_TAXONOMY
from .snippets import ComplianceSnippet, SnippetRegistry


@dataclass
class SnippetPlan:
    snippet: ComplianceSnippet
    confidence: float
    domain: str
    gate_id: str


class UniversalSnippetMapper:
    """
    Convert gate metadata into snippet plans.  Uses domain taxonomy so new gates
    automatically pick up reusable templates.
    """

    def __init__(self, snippet_registry: SnippetRegistry) -> None:
        self.registry = snippet_registry
        self.domain_templates = DOMAIN_TEMPLATES
        self.module_taxonomy = MODULE_TAXONOMY
        self.taxonomy = self._build_gate_taxonomy()

    def _build_gate_taxonomy(self) -> Dict[str, Dict[str, str]]:
        taxonomy: Dict[str, Dict[str, str]] = {}
        for module_name, module_map in self.module_taxonomy.items():
            for gate_id, meta in module_map.items():
                taxonomy[f"{module_name}:{gate_id}"] = dict(meta)
        return taxonomy

    def map_gate_to_snippet(self, gate_id: str, gate_metadata: Dict) -> Optional[SnippetPlan]:
        # First, check if there's a special snippet (takes precedence)
        module_id, gate_name = gate_id.split(':') if ':' in gate_id else (None, gate_id)
        if module_id and gate_name:
            special_snippet = self.registry.get_snippet(module_id, gate_name)
            if special_snippet:
                # Use the inferred domain for the plan, but use the special snippet
                metadata = self.taxonomy.get(gate_id)
                if metadata:
                    domain = metadata.get('domain')
                else:
                    domain = self._infer_domain_from_gate(gate_metadata).get('domain', 'disclosure')
                confidence = self._confidence(domain, gate_metadata)
                return SnippetPlan(snippet=special_snippet, confidence=0.99, domain=domain, gate_id=gate_id)

        # Otherwise, build from template
        key = gate_id
        metadata = dict(self.taxonomy.get(key, {}))
        domain = None
        variant = None
        context = {}
        if metadata:
            domain = metadata.get('domain')
            variant = metadata.get('variant')
            context = dict(metadata.get('context', {}))
        else:
            inferred = self._infer_domain_from_gate(gate_metadata)
            domain = inferred.get('domain')
            variant = inferred.get('variant')
            context = inferred.get('context', {})

        if not domain:
            return None

        snippet = self.registry.build_snippet(domain, variant, context, gate_metadata)
        if not snippet:
            return None

        confidence = self._confidence(domain, gate_metadata)
        return SnippetPlan(snippet=snippet, confidence=confidence, domain=domain, gate_id=gate_id)

    def get_confidence(self, snippet_plan: SnippetPlan) -> float:
        return snippet_plan.confidence

    def _confidence(self, domain: str, gate_metadata: Dict) -> float:
        severity = (gate_metadata.get('severity') or 'MEDIUM').upper()
        base = {
            'CRITICAL': 0.9,
            'HIGH': 0.8,
            'MEDIUM': 0.6,
            'LOW': 0.5,
        }.get(severity, 0.6)
        if domain in ('risk_warning', 'consent', 'limitation'):
            base += 0.05
        return min(base, 0.95)

    def _infer_domain_from_gate(self, gate_metadata: Dict) -> Dict[str, any]:
        gate_id = (gate_metadata.get('gate_id') or '').lower()
        message = (gate_metadata.get('message') or '').lower()
        suggestion = (gate_metadata.get('suggestion') or '').lower()
        legal_source = (gate_metadata.get('legal_source') or '').lower()
        combined = ' '.join([gate_id, message, suggestion, legal_source])

        mapping = [
            ('disclosure', ['signpost', 'contact', 'disclosure', 'inform', 'provide contact', 'process describe']),
            ('risk_warning', ['risk', 'warning', 'loss', 'fall as well as rise']),
            ('consent', ['consent', 'withdraw', 'opt-out', 'permission']),
            ('limitation', ['scope', 'limitation', 'eligibility', 'target market', 'definition']),
            ('procedure', ['complaint', 'process', 'breach notification', 'time limit']),
            ('definition', ['purpose', 'definition', 'clarify', 'description']),
        ]
        for domain, keywords in mapping:
            if any(keyword in combined for keyword in keywords):
                return {
                    'domain': domain,
                    'variant': None,
                    'context': {},
                }
        return {
            'domain': 'disclosure',
            'variant': None,
            'context': {},
        }
