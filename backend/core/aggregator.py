from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple

from core.providers import ProviderRouter, ProviderError, ProviderCallError


RISK_PRIORITY = {
    'LOW': 0,
    'MEDIUM': 1,
    'HIGH': 2,
    'CRITICAL': 3,
    None: 4,
    'UNKNOWN': 4
}


@dataclass
class ModelMetrics:
    overall_risk: str
    failures: int
    warnings: int
    critical_failures: int
    semantic_hits: int
    needs_review: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ModelOutcome:
    provider: str
    prompt: str
    response_text: str
    metrics: ModelMetrics
    validation: Dict[str, Any]
    error: Optional[str] = None

    def risk_weight(self) -> int:
        return RISK_PRIORITY.get(self.metrics.overall_risk, 4)


class MultiModelAggregator:
    """
    Orchestrates multi-provider prompts, validates each response, and selects
    the safest output based on deterministic scoring.
    """

    def __init__(self, engine, provider_router: ProviderRouter):
        self.engine = engine
        self.provider_router = provider_router

    def aggregate(
        self,
        prompt: str,
        provider_specs: List[Dict[str, Any]],
        modules: Optional[List[str]] = None,
        max_tokens: int = 1024
    ) -> Dict[str, Any]:
        outcomes: List[ModelOutcome] = []

        modules_to_check = modules or list(self.engine.modules.keys())

        for spec in provider_specs:
            provider_name = (spec.get('name') or '').strip().lower()
            if not provider_name:
                continue

            simulated_text = spec.get('simulated_response')
            api_key = spec.get('api_key')
            per_model_tokens = spec.get('max_tokens') or max_tokens

            response_text: str = ''
            error: Optional[str] = None

            if simulated_text:
                response_text = simulated_text
            else:
                try:
                    if api_key:
                        self.provider_router.configure_provider(provider_name, api_key)
                    response_text = self.provider_router.call_provider(
                        provider_name,
                        prompt,
                        max_tokens=per_model_tokens
                    )
                except (ProviderError, ProviderCallError, Exception) as exc:  # noqa: B902
                    error = str(exc)

            if not response_text:
                outcome = ModelOutcome(
                    provider=provider_name,
                    prompt=prompt,
                    response_text='',
                    metrics=ModelMetrics(
                        overall_risk='UNKNOWN',
                        failures=0,
                        warnings=0,
                        critical_failures=0,
                        semantic_hits=0,
                        needs_review=0
                    ),
                    validation={},
                    error=error or 'No response text available'
                )
                outcomes.append(outcome)
                continue

            validation = self.engine.check_document(
                text=response_text,
                document_type='ai_generated',
                active_modules=modules_to_check
            )

            metrics = self._extract_metrics(validation)

            outcome = ModelOutcome(
                provider=provider_name,
                prompt=prompt,
                response_text=response_text,
                metrics=metrics,
                validation=validation,
                error=error
            )
            outcomes.append(outcome)

        selected = self._select_best(outcomes)

        return {
            'prompt': prompt,
            'modules': modules_to_check,
            'responses': [self._outcome_to_dict(o) for o in outcomes],
            'selected': self._outcome_to_dict(selected) if selected else None
        }

    def _extract_metrics(self, validation: Dict[str, Any]) -> ModelMetrics:
        overall_risk = (validation or {}).get('overall_risk') or 'UNKNOWN'
        failures = 0
        warnings = 0
        critical = 0

        modules = (validation or {}).get('modules') or {}
        for module_payload in modules.values():
            gates = (module_payload or {}).get('gates') or {}
            for gate in gates.values():
                status = (gate or {}).get('status')
                severity = (gate or {}).get('severity', '').lower()
                if status == 'FAIL':
                    failures += 1
                    if severity == 'critical':
                        critical += 1
                elif status == 'WARNING':
                    warnings += 1

        semantic_summary = (validation or {}).get('semantic') or {}
        semantic_hits = int(semantic_summary.get('total_hits') or 0)
        needs_review = int(semantic_summary.get('needs_review') or 0)

        return ModelMetrics(
            overall_risk=overall_risk,
            failures=failures,
            warnings=warnings,
            critical_failures=critical,
            semantic_hits=semantic_hits,
            needs_review=needs_review
        )

    def _select_best(self, outcomes: List[ModelOutcome]) -> Optional[ModelOutcome]:
        viable = [o for o in outcomes if not o.error and o.response_text]
        if not viable:
            return outcomes[0] if outcomes else None

        def sort_key(outcome: ModelOutcome) -> Tuple[int, int, int, int, int]:
            metrics = outcome.metrics
            return (
                outcome.risk_weight(),
                metrics.critical_failures,
                metrics.failures,
                metrics.warnings,
                metrics.semantic_hits
            )

        viable.sort(key=sort_key)
        return viable[0]

    def _outcome_to_dict(self, outcome: Optional[ModelOutcome]) -> Optional[Dict[str, Any]]:
        if not outcome:
            return None
        return {
            'provider': outcome.provider,
            'response_text': outcome.response_text,
            'metrics': outcome.metrics.to_dict(),
            'validation': outcome.validation,
            'error': outcome.error
        }

