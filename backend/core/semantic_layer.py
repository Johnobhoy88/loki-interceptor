import json
import os
import re
from copy import deepcopy
from typing import Dict, List, Optional


class SemanticLayer:
    """Deterministic semantic augmentation for rule-based gates."""

    _SEVERITY_ORDER = {
        'critical': 4,
        'high': 3,
        'medium': 2,
        'low': 1,
        'none': 0,
        None: -1,
    }

    def __init__(self, config_path: Optional[str] = None):
        base_dir = os.path.dirname(__file__)
        default_path = os.path.join(base_dir, 'semantic_rules.json')
        self.config_path = config_path or default_path
        self.rules = self._load_config(self.config_path)
        self._phrase_cache: Dict[str, Dict[str, List[re.Pattern]]] = {}
        self._header_cache: Dict[str, Dict[str, List[re.Pattern]]] = {}

    def _load_config(self, path: str) -> Dict:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Semantic configuration not found at {path}")
        with open(path, 'r', encoding='utf-8') as handle:
            data = json.load(handle)
        return data.get('modules', {})

    def post_process(self, module_name: str, gate_name: str, text: str, gate_result: Dict) -> Dict:
        module_rules = self.rules.get(module_name)
        if not module_rules:
            return gate_result

        gate_rules = (module_rules.get('gates') or {}).get(gate_name)
        if not gate_rules:
            return gate_result

        updated = deepcopy(gate_result) if gate_result is not None else {}
        status = (updated.get('status') or 'PASS').upper()
        severity = (updated.get('severity') or 'none').lower()
        notes: List[str] = list(updated.get('semantic_notes') or [])
        hits: List[Dict] = list(updated.get('semantic_hits') or [])

        text_casefold = text.casefold()

        # fail_if_present processing
        for canonical, metadata in (gate_rules.get('fail_if_present') or {}).items():
            if self._phrase_present(module_name, canonical, text_casefold):
                hit_detail = {
                    'type': 'fail_if_present',
                    'canonical': canonical,
                    'message': metadata.get('message'),
                }
                if metadata.get('human_review'):
                    hit_detail['human_review'] = True
                    updated['needs_human_review'] = True
                    notes.append('Flagged for human compliance review.')
                hits.append(hit_detail)
                notes.append(metadata.get('message', f"Semantic flag triggered: {canonical}"))
                status, severity = self._escalate(status, severity, 'FAIL', metadata.get('severity'))

        # require_one_of processing
        for requirement_key, requirement in (gate_rules.get('require_one_of') or {}).items():
            phrases = requirement.get('phrases') or []
            if not phrases:
                continue

            header_key = requirement.get('header')
            window = requirement.get('window', 240)
            present = False
            if header_key:
                present = self._phrases_near_header(module_name, phrases, header_key, text_casefold, window)
            if not present:
                present = self._any_phrase_present(module_name, phrases, text_casefold)

            if not present:
                miss_message = requirement.get('message') or f"Required semantic content missing: {requirement_key}"
                hit_detail = {
                    'type': 'require_one_of',
                    'canonical': requirement_key,
                    'message': miss_message,
                }
                if requirement.get('human_review'):
                    hit_detail['human_review'] = True
                    updated['needs_human_review'] = True
                    notes.append('Flagged for human compliance review.')
                hits.append(hit_detail)
                notes.append(miss_message)
                target_severity = requirement.get('severity', 'medium')
                target_status = 'FAIL' if target_severity in ('critical', 'high') else 'WARNING'
                status, severity = self._escalate(status, severity, target_status, target_severity)

        if notes:
            updated['semantic_notes'] = self._deduplicate(notes)
        if hits:
            updated['semantic_hits'] = hits
        updated['status'] = status
        updated['severity'] = severity
        return updated

    def _escalate(self, current_status: str, current_severity: str, target_status: str, target_severity: Optional[str]) -> (str, str):
        status_priority = {'FAIL': 3, 'WARNING': 2, 'PASS': 1, None: 0}
        chosen_status = current_status
        if status_priority.get(target_status, 0) > status_priority.get(current_status, 0):
            chosen_status = target_status

        current_rank = self._SEVERITY_ORDER.get(current_severity, -1)
        target_rank = self._SEVERITY_ORDER.get((target_severity or '').lower(), -1)
        chosen_severity = current_severity
        if target_rank > current_rank:
            chosen_severity = (target_severity or current_severity or 'none').lower()

        return chosen_status, chosen_severity

    def _phrase_present(self, module_name: str, canonical: str, text_casefold: str) -> bool:
        for pattern in self._get_phrase_patterns(module_name, canonical):
            if pattern.search(text_casefold):
                return True
        return False

    def _any_phrase_present(self, module_name: str, phrases: List[str], text_casefold: str) -> bool:
        for phrase in phrases:
            if self._phrase_present(module_name, phrase, text_casefold):
                return True
        return False

    def _phrases_near_header(self, module_name: str, phrases: List[str], header_key: Optional[str], text_casefold: str, window: int) -> bool:
        if not header_key:
            return False
        header_patterns = self._get_header_patterns(module_name, header_key)
        if not header_patterns:
            return False
        phrase_patterns: List[re.Pattern] = []
        for phrase in phrases:
            phrase_patterns.extend(self._get_phrase_patterns(module_name, phrase))
        if not phrase_patterns:
            return False

        for header_pattern in header_patterns:
            for match in header_pattern.finditer(text_casefold):
                start = match.end()
                end = min(len(text_casefold), start + max(window, 0))
                segment = text_casefold[start:end]
                for phrase_pattern in phrase_patterns:
                    if phrase_pattern.search(segment):
                        return True
        return False

    def _get_phrase_patterns(self, module_name: str, canonical: str) -> List[re.Pattern]:
        module_cache = self._phrase_cache.setdefault(module_name, {})
        if canonical in module_cache:
            return module_cache[canonical]

        module_rules = self.rules.get(module_name) or {}
        synonyms = (module_rules.get('synonyms') or {}).get(canonical, [])
        candidates = [canonical] + list(synonyms)
        patterns = []
        for phrase in candidates:
            phrase_casefold = phrase.casefold()
            escaped = re.escape(phrase_casefold)
            pattern = re.compile(rf"\b{escaped}\b")
            patterns.append(pattern)
        module_cache[canonical] = patterns
        return patterns

    def _get_header_patterns(self, module_name: str, header_key: str) -> List[re.Pattern]:
        module_cache = self._header_cache.setdefault(module_name, {})
        if header_key in module_cache:
            return module_cache[header_key]

        module_rules = self.rules.get(module_name) or {}
        header_terms = (module_rules.get('headers') or {}).get(header_key, [])
        patterns = []
        for header in header_terms:
            escaped = re.escape(header.casefold())
            patterns.append(re.compile(rf"\b{escaped}\b"))
        module_cache[header_key] = patterns
        return patterns

    @staticmethod
    def _deduplicate(values: List[str]) -> List[str]:
        seen = set()
        deduped = []
        for value in values:
            if not value:
                continue
            if value not in seen:
                seen.add(value)
                deduped.append(value)
        return deduped
