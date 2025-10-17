from __future__ import annotations

import json
from dataclasses import dataclass
import re
from typing import Any, Dict, List, Optional, Tuple


RISK_PRIORITY = {
    'LOW': 0,
    'MEDIUM': 1,
    'HIGH': 2,
    'CRITICAL': 3,
    None: 4,
    'UNKNOWN': 4
}


@dataclass
class ProviderOutcome:
    provider: str
    risk: str
    failures: int
    warnings: int
    needs_review: int
    response_text: str
    validation: Dict[str, Any]
    raw: Dict[str, Any]
    blocked: bool
    error: Optional[str]
    is_refusal: bool = False
    content_score: float = 0.0
    refusal_reason: Optional[str] = None

    @property
    def score(self) -> tuple:
        return (
            RISK_PRIORITY.get(self.risk, 4),
            self.failures,
            self.warnings,
            self.needs_review
        )


class MultiModelAggregator:
    """Runs a prompt across multiple providers and returns comparison metadata."""

    def __init__(self, engine, anthropic_interceptor, openai_interceptor, gemini_interceptor):
        self.engine = engine
        self.anthropic = anthropic_interceptor
        self.openai = openai_interceptor
        self.gemini = gemini_interceptor

    def run(
        self,
        prompt: str,
        provider_specs: List[Dict[str, Any]],
        modules: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        modules_to_check = modules or list(self.engine.modules.keys())
        outcomes: List[ProviderOutcome] = []

        for spec in provider_specs:
            outcome = self._execute_provider(prompt, spec, modules_to_check)
            if outcome:
                outcomes.append(outcome)

        selected, selection_meta = self._select_best(outcomes)

        return {
            'prompt': prompt,
            'modules': modules_to_check,
            'selected': self._serialize_outcome(selected) if selected else None,
            'providers': [self._serialize_outcome(o) for o in outcomes],
            'selection': selection_meta or {},
            'all_refused': bool(selection_meta and selection_meta.get('all_refused'))
        }

    def _execute_provider(self, prompt: str, spec: Dict[str, Any], modules: List[str]) -> Optional[ProviderOutcome]:
        name = (spec.get('name') or '').strip().lower()
        api_key = spec.get('api_key')

        if not name or not api_key:
            return None

        try:
            if name == 'anthropic':
                request_payload = {
                    'model': spec.get('model') or 'claude-sonnet-4-20250514',
                    'max_tokens': spec.get('max_tokens') or 900,
                    'messages': [{'role': 'user', 'content': prompt}]
                }
                raw = self.anthropic.intercept_and_validate(request_payload, api_key, modules)
                validation = raw.get('validation') or raw.get('loki', {}).get('validation') or {}
                risk = (raw.get('loki') or {}).get('risk') or validation.get('overall_risk') or 'UNKNOWN'
                blocked = bool(raw.get('blocked'))
                response_text = self._extract_anthropic_text(raw)
                error = raw.get('error') if blocked else None

            elif name == 'openai':
                request_payload = {
                    'model': spec.get('model') or 'gpt-5-mini',
                    'messages': [{'role': 'user', 'content': prompt}]
                }
                project = spec.get('project')
                if project:
                    request_payload['project'] = project
                raw = self.openai.intercept(request_payload, api_key, modules)
                validation = raw.get('loki_validation') or {}
                if not validation and raw.get('validation'):
                    validation = raw['validation']
                risk = validation.get('overall_risk') or 'UNKNOWN'
                blocked = bool(raw.get('blocked'))
                response_text = self._extract_openai_text(raw)
                error = raw.get('message') if blocked else None

            elif name == 'gemini':
                request_payload = {
                    'model': spec.get('model') or 'gemini-2.5-flash',
                    'prompt': prompt
                }
                raw = self.gemini.intercept(request_payload, api_key, modules)
                validation = raw.get('loki_validation') or {}
                if not validation and raw.get('validation'):
                    validation = raw['validation']
                risk = validation.get('overall_risk') or 'UNKNOWN'
                blocked = bool(raw.get('blocked'))
                response_text = self._extract_gemini_text(raw)
                error = raw.get('message') if blocked else None

            else:
                return None

            clean_text = (response_text or '').strip()
            is_refusal, refusal_reason = self._detect_refusal(clean_text)
            content_score = float(len(re.findall(r'\w+', clean_text)))

            failures, warnings = self._count_gates(validation)
            needs_review = self._count_review_flags(validation)

            return ProviderOutcome(
                provider=name,
                risk=str(risk).upper(),
                failures=failures,
                warnings=warnings,
                needs_review=needs_review,
                response_text=response_text,
                validation=validation,
                raw=raw,
                blocked=blocked,
                error=error,
                is_refusal=is_refusal,
                content_score=content_score,
                refusal_reason=refusal_reason
            )

        except Exception as exc:
            return ProviderOutcome(
                provider=name,
                risk='UNKNOWN',
                failures=0,
                warnings=0,
                needs_review=0,
                response_text='',
                validation={},
                raw={},
                blocked=True,
                error=str(exc),
                is_refusal=True,
                content_score=0.0,
                refusal_reason='error'
            )

    def _select_best(self, outcomes: List[ProviderOutcome]) -> Tuple[Optional[ProviderOutcome], Dict[str, Any]]:
        if not outcomes:
            return None, {'reason': 'no_providers', 'all_refused': True}

        def sort_key(outcome: ProviderOutcome):
            return (
                outcome.blocked,
                outcome.score,
                -outcome.content_score
            )

        usable = [
            o for o in outcomes
            if not o.is_refusal and (o.response_text or '').strip()
        ]

        if usable:
            chosen = sorted(usable, key=sort_key)[0]
            metadata = {
                'reason': 'non_refusal_selected',
                'provider': chosen.provider,
                'used_blocked_provider': chosen.blocked,
                'fallback_from_refusal': any(out.is_refusal for out in outcomes if out != chosen)
            }
            return chosen, metadata

        # No usable responses (all refusals or empty)
        all_refused = all(o.is_refusal or not (o.response_text or '').strip() for o in outcomes)
        metadata = {
            'reason': 'all_providers_refused' if all_refused else 'no_content_available',
            'all_refused': all_refused
        }
        return None, metadata

    @staticmethod
    def _count_gates(validation: Dict[str, Any]) -> Tuple[int, int]:
        failures = 0
        warnings = 0
        modules = (validation or {}).get('modules') or {}
        for module_payload in modules.values():
            gates = (module_payload or {}).get('gates') or {}
            for gate in gates.values():
                status = (gate or {}).get('status')
                if status == 'FAIL':
                    failures += 1
                elif status == 'WARNING':
                    warnings += 1
        return failures, warnings

    @staticmethod
    def _count_review_flags(validation: Dict[str, Any]) -> int:
        semantic = (validation or {}).get('semantic') or {}
        return int(semantic.get('needs_review') or semantic.get('needs_review_count') or 0)

    @staticmethod
    def _refusal_patterns() -> List[Tuple[re.Pattern, str]]:
        patterns = [
            (r"\bi\s+can['’]?t\s+help\b", 'cant_help'),
            (r"\bi\s+can['’]?t\s+assist\b", 'cant_assist'),
            (r"\bi\s+can['’]?t\s+provide\b", 'cant_provide'),
            (r"\bi\s+cannot\s+help\b", 'cannot_help'),
            (r"\bi\s+cannot\s+assist\b", 'cannot_assist'),
            (r"\bi\s+must\s+refuse\b", 'must_refuse'),
            (r"\bi\s+am\s+unable\s+to\s+comply\b", 'unable_comply'),
            (r"\bagainst\s+(?:my\s+)?guidelines\b", 'against_guidelines'),
            (r"\bpolicy\s+prohibits\b", 'policy_prohibits'),
            (r"\bi\s+do\s+not\s+have\s+the\s+ability\b", 'no_ability'),
            (r"\bas\s+an\s+ai\s+language\s+model\b", 'ai_disclaimer')
        ]
        return [(re.compile(pattern, re.IGNORECASE), reason) for pattern, reason in patterns]

    def _detect_refusal(self, text: str) -> tuple[bool, Optional[str]]:
        if not text:
            return True, 'empty_response'

        normalized = text.strip()
        for pattern, reason in self._refusal_patterns():
            if pattern.search(normalized):
                return True, reason

        lowercase = normalized.lower()
        if lowercase.startswith("i'm sorry") or lowercase.startswith("i am sorry"):
            return True, 'apology_refusal'

        word_count = len(lowercase.split())
        if word_count < 40 and ('cannot help' in lowercase or 'unable to help' in lowercase or 'i cannot' in lowercase and 'comply' in lowercase):
            return True, 'short_refusal'

        return False, None

    @staticmethod
    def _extract_anthropic_text(raw: Dict[str, Any]) -> str:
        if raw.get('blocked') and raw.get('original_response'):
            return raw['original_response']
        response = raw.get('response') or {}
        content = response.get('content') or []
        text_blocks: List[str] = []
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get('type') != 'text':
                continue
            piece = block.get('text')
            if isinstance(piece, str):
                text_blocks.append(piece)
            elif isinstance(piece, list):
                text_blocks.append(''.join(str(p) for p in piece))
        if text_blocks:
            return ''.join(text_blocks)
        if isinstance(response.get('text'), str):
            return response['text']
        return ''

    @staticmethod
    def _extract_openai_text(raw: Dict[str, Any]) -> str:
        if not isinstance(raw, dict):
            return ''
        choices = raw.get('choices') or []
        parts = [choice.get('message', {}).get('content') for choice in choices if isinstance(choice, dict)]
        combined = '\n\n'.join([p for p in parts if isinstance(p, str) and p.strip()])
        if combined.strip():
            return combined
        if raw.get('original_response'):
            return str(raw['original_response'])
        return ''

    @staticmethod
    def _extract_gemini_text(raw: Dict[str, Any]) -> str:
        if not isinstance(raw, dict):
            return ''
        candidates = raw.get('candidates') or []
        for candidate in candidates:
            content = (candidate or {}).get('content') or {}
            parts = content.get('parts') or []
            for part in parts:
                if isinstance(part, dict) and part.get('text'):
                    return str(part['text'])
        if raw.get('original_response'):
            return str(raw['original_response'])
        return ''

    @staticmethod
    def _serialize_outcome(outcome: Optional[ProviderOutcome]) -> Optional[Dict[str, Any]]:
        if not outcome:
            return None
        return {
            'provider': outcome.provider,
            'risk': outcome.risk,
            'failures': outcome.failures,
            'warnings': outcome.warnings,
            'needs_review': outcome.needs_review,
            'response_text': outcome.response_text,
            'validation': outcome.validation,
            'blocked': outcome.blocked,
            'error': outcome.error,
            'is_refusal': outcome.is_refusal,
            'content_score': outcome.content_score,
            'refusal_reason': outcome.refusal_reason
        }
