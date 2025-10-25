"""
Advanced deterministic synthesis engine leveraging universal sanitizer and snippet mapper.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .sanitizer import TextSanitizer
from .snippet_mapper import UniversalSnippetMapper, SnippetPlan
from .snippets import SnippetRegistry


@dataclass
class AppliedSnippet:
    gate_id: str
    module_id: str
    severity: str
    iteration: int
    order: int
    snippet_key: str
    text_added: str
    domain: str
    confidence: float


class SynthesisEngine:
    """Universal deterministic document assembly."""

    def __init__(
        self,
        validation_engine,
        snippet_registry: Optional[SnippetRegistry] = None,
        audit_logger=None,
    ) -> None:
        self.engine = validation_engine
        self.registry = snippet_registry or SnippetRegistry()
        self.sanitizer = TextSanitizer()
        self.mapper = UniversalSnippetMapper(self.registry)
        self.max_retries = 5
        self.audit_logger = audit_logger

    def synthesize(
        self,
        base_text: str,
        validation: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        modules: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        context = context or {}
        modules = modules or list(self.engine.modules.keys())

        start_time = time.time()
        original_text = base_text or ""
        initial_failures = self._extract_failures(validation)
        sanitization_result = self.sanitizer.sanitize(original_text, initial_failures)
        working_text = sanitization_result['sanitized_text']

        # Use original validation for first iteration, then re-validate after changes
        current_validation = validation

        applied_snippets: List[AppliedSnippet] = []
        attempted_keys = set()

        for iteration in range(1, self.max_retries + 1):
            failures = self._extract_failures(current_validation)
            if not failures:
                duration_ms = (time.time() - start_time) * 1000
                result = self._build_result(
                    success=True,
                    reason=f'All gates passed after {iteration - 1} iteration(s)',
                    iterations=iteration - 1,
                    working_text=working_text,
                    original_text=original_text,
                    applied_snippets=applied_snippets,
                    sanitization_actions=sanitization_result['actions'],
                    final_validation=current_validation,
                )
                self._log_synthesis('synthesize', result, modules, duration_ms)
                return result

            plans = self._build_snippet_plan(failures, attempted_keys)
            if not plans:
                duration_ms = (time.time() - start_time) * 1000
                result = self._needs_review_result(
                    reason='No suitable snippets available for remaining failures',
                    iterations=iteration - 1,
                    working_text=working_text,
                    original_text=original_text,
                    applied_snippets=applied_snippets,
                    sanitization_actions=sanitization_result['actions'],
                    validation=current_validation,
                    modules=modules,
                )
                self._log_synthesis('synthesize', result, modules, duration_ms)
                return result

            applied_this_iteration = []
            for order, plan in enumerate(plans, start=1):
                snippet_text = self.registry.format_snippet(plan.snippet, context)

                # Respect insertion points
                insertion_point = plan.snippet.insertion_point
                if insertion_point == 'start':
                    working_text = snippet_text + working_text
                elif insertion_point == 'end':
                    working_text = working_text + snippet_text
                else:  # 'section' or any other - append
                    working_text = working_text + snippet_text

                key = self._snippet_key(plan)
                attempted_keys.add(key)
                applied_this_iteration.append(
                    AppliedSnippet(
                        gate_id=plan.snippet.gate_id,
                        module_id=plan.snippet.module_id,
                        severity=plan.snippet.severity,
                        iteration=iteration,
                        order=order,
                        snippet_key=key,
                        text_added=snippet_text.strip(),
                        domain=plan.domain,
                        confidence=plan.confidence,
                    )
                )

            applied_snippets.extend(applied_this_iteration)

            current_validation = self.engine.check_document(
                text=working_text,
                document_type='synthesized',
                active_modules=modules,
            )

        duration_ms = (time.time() - start_time) * 1000
        result = self._needs_review_result(
            reason=f'Max retries ({self.max_retries}) reached',
            iterations=self.max_retries,
            working_text=working_text,
            original_text=original_text,
            applied_snippets=applied_snippets,
            sanitization_actions=sanitization_result['actions'],
            validation=current_validation,
            modules=modules,
        )
        self._log_synthesis('synthesize', result, modules, duration_ms)
        return result

    def synthesize_from_aggregator(
        self,
        aggregator_result: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        selected = aggregator_result.get('selected')
        if not selected:
            base_text = ''
            validation = {'modules': {}, 'overall_risk': 'CRITICAL'}
        else:
            base_text = selected.get('response_text', '')
            validation = selected.get('validation', {})
        modules = aggregator_result.get('modules', [])
        return self.synthesize(base_text, validation, context=context, modules=modules)

    def _build_snippet_plan(
        self,
        failures: List[Dict[str, Any]],
        attempted: set,
    ) -> List[SnippetPlan]:
        plans: List[SnippetPlan] = []
        for gate in failures:
            gate_key = f"{gate['module']}:{gate['gate']}"
            plan = self.mapper.map_gate_to_snippet(gate_key, gate)
            if not plan:
                continue
            key = self._snippet_key(plan)
            if key in attempted:
                continue
            plans.append(plan)
        plans.sort(key=lambda p: p.confidence, reverse=True)
        return plans

    def _extract_failures(self, validation: Dict[str, Any]) -> List[Dict[str, Any]]:
        failures: List[Dict[str, Any]] = []
        modules = validation.get('modules') or {}
        for module_id, module_payload in modules.items():
            gates = module_payload.get('gates') or {}
            for gate_id, gate_payload in gates.items():
                if (gate_payload or {}).get('status', '').upper() == 'FAIL':
                    failures.append(
                        {
                            'module': module_id,
                            'gate': gate_id,
                            'severity': gate_payload.get('severity', 'MEDIUM'),
                            'message': gate_payload.get('message', ''),
                            'suggestion': gate_payload.get('suggestion', ''),
                            'legal_source': gate_payload.get('legal_source', ''),
                            'details': gate_payload.get('details', []),
                            'excerpt': gate_payload.get('excerpt', ''),
                            'gate_id': f"{module_id}:{gate_id}",
                        }
                    )
        return failures

    def _needs_review_result(
        self,
        reason: str,
        iterations: int,
        working_text: str,
        original_text: str,
        applied_snippets: List[AppliedSnippet],
        sanitization_actions: List[Dict[str, Any]],
        validation: Dict[str, Any],
        modules: List[str],
    ) -> Dict[str, Any]:
        result = {
            'synthesized_text': working_text,
            'original_text': original_text,
            'iterations': iterations,
            'snippets_applied': [s.__dict__ for s in applied_snippets],
            'final_validation': validation,
            'success': False,
            'reason': reason,
            'sanitization': {'actions': sanitization_actions},
        }
        result.update(self._extract_needs_review_payload(validation, reason, modules))
        return result

    def _build_result(
        self,
        success: bool,
        reason: str,
        iterations: int,
        working_text: str,
        original_text: str,
        applied_snippets: List[AppliedSnippet],
        sanitization_actions: List[Dict[str, Any]],
        final_validation: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            'synthesized_text': working_text,
            'original_text': original_text,
            'iterations': iterations,
            'snippets_applied': [s.__dict__ for s in applied_snippets],
            'final_validation': final_validation,
            'success': success,
            'reason': reason,
            'sanitization': {'actions': sanitization_actions},
        }

    def _snippet_key(self, plan: SnippetPlan) -> str:
        return f"{plan.snippet.module_id}:{plan.snippet.gate_id}:{plan.domain}"

    def _extract_needs_review_payload(
        self,
        validation: Dict[str, Any],
        reason: str,
        modules: List[str],
    ) -> Dict[str, Any]:
        failing_gates = []
        suggested_actions = []
        for module_id, module_payload in (validation.get('modules') or {}).items():
            for gate_id, gate_payload in (module_payload.get('gates') or {}).items():
                if (gate_payload or {}).get('status', '').upper() == 'FAIL':
                    failing_gates.append(
                        {
                            'module_id': module_id,
                            'gate_id': gate_id,
                            'status': 'FAIL',
                            'severity': gate_payload.get('severity', 'unknown'),
                            'message': gate_payload.get('message', ''),
                            'suggestion': gate_payload.get('suggestion', ''),
                        }
                    )
                    suggestion = gate_payload.get('suggestion') or gate_payload.get('message')
                    if suggestion:
                        suggested_actions.append(f"{module_id}.{gate_id}: {suggestion}")
        return {
            'needs_review': True,
            'reason': reason,
            'failing_gates': failing_gates,
            'suggested_actions': suggested_actions[:10],
            'modules': modules,
        }

    def _log_synthesis(
        self,
        operation: str,
        result: Dict[str, Any],
        modules: List[str],
        duration_ms: float,
    ) -> None:
        if not self.audit_logger:
            return
        try:
            unresolved = [
                f"{gate['module_id']}:{gate['gate_id']}"
                for gate in result.get('failing_gates', [])
            ]
            self.audit_logger.log_synthesis(
                operation=operation,
                success=result.get('success', False),
                iterations=result.get('iterations', 0),
                snippets_applied=result.get('snippets_applied', []),
                unresolved_gates=unresolved,
                modules=modules,
                duration_ms=duration_ms,
                metadata={'reason': result.get('reason', '')},
            )
        except Exception:
            pass
