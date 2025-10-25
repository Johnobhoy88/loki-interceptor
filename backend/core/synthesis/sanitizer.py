from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple


@dataclass
class SanitizationAction:
    pattern_type: str
    original: str
    replacement: str
    severity: str
    gate_triggered: Optional[str]
    count: int


class TextSanitizer:
    """
    Universal text sanitizer that neutralises toxic patterns before snippet insertion.
    The sanitizer works with pattern categories (absolute claims, superlatives, etc.)
    and adapts to gate failures so new modules can be supported without code changes.
    """

    def __init__(self) -> None:
        self.patterns = self._load_patterns()
        self.severity_map = {
            'absolute_claim': 'CRITICAL',
            'superlative': 'HIGH',
            'risk_minimization': 'CRITICAL',
            'urgency': 'MEDIUM',
            'overgeneralization': 'HIGH',
            'regulatory_bypass': 'CRITICAL',
            'disclosure': 'HIGH',
        }

    def sanitize(
        self,
        text: str,
        gate_failures: Optional[List[Dict]] = None,
    ) -> Dict[str, any]:
        """
        Perform sanitisation on the supplied text.  Gate failures influence which
        pattern categories are prioritised.
        """
        working_text = text or ""
        actions: List[SanitizationAction] = []

        categories = self._extract_patterns_from_gates(gate_failures)
        if not categories:
            categories = list(self.patterns.keys())

        for category in categories:
            pattern_group = self.patterns.get(category, [])
            for pattern_def in pattern_group:
                matcher = pattern_def['regex']
                replacement_func = pattern_def['replacer']
                matches = list(matcher.finditer(working_text))
                if not matches:
                    continue

                total_replaced = 0
                for match in matches:
                    original = match.group(0)
                    replacement = replacement_func(match)
                    if replacement == original:
                        continue
                    working_text = self._replacement_sub(
                        working_text, match.start(), match.end(), replacement
                    )
                    total_replaced += 1
                    actions.append(
                        SanitizationAction(
                            pattern_type=category,
                            original=original,
                            replacement=replacement,
                            severity=self.severity_map.get(category, 'MEDIUM'),
                            gate_triggered=pattern_def.get('gate_id'),
                            count=1,
                        )
                    )
                if total_replaced:
                    self._ensure_structural_spacing(category, pattern_def, working_text)

        confidence = self._confidence_score(text, working_text, actions)
        merged_actions = self._merge_actions(actions)

        return {
            'sanitized_text': working_text,
            'actions': [action.__dict__ for action in merged_actions],
            'confidence': confidence,
        }

    def _extract_patterns_from_gates(self, gate_failures: Optional[List[Dict]]) -> List[str]:
        """
        Analyse gate failures and return pattern categories that should be prioritised.
        The logic relies on common keywords instead of hard-coded gate IDs so new gates
        automatically influence sanitisation.
        """
        if not gate_failures:
            return []

        categories = set()
        for failure in gate_failures:
            gate_id = (failure.get('gate_id') or '').lower()
            message = (failure.get('message') or '').lower()
            details = ' '.join(str(d).lower() for d in failure.get('details', []))
            excerpt = (failure.get('excerpt') or '').lower()
            combined = ' '.join([gate_id, message, details, excerpt])

            if any(term in combined for term in ('misleading', 'guarantee', 'guaranteed', 'risk-free')):
                categories.add('absolute_claim')
                categories.add('risk_minimization')
            if any(term in combined for term in ('superlative', 'best', 'number one', '#1', 'unmatched', 'outperform')):
                categories.add('superlative')
            if any(term in combined for term in ('risk warning', 'no risk', 'safe', 'secure')):
                categories.add('risk_minimization')
            if any(term in combined for term in ('act now', 'limited time', 'spots filling', 'urgency')):
                categories.add('urgency')
            if any(term in combined for term in ('target market', 'everyone', 'anyone', 'all customers')):
                categories.add('overgeneralization')
            if any(term in combined for term in ('fca approval', 'section 21', 'not regulated', 'no approval needed')):
                categories.add('regulatory_bypass')
            if any(term in combined for term in ('consent', 'opt-out', 'withdraw')):
                categories.add('overgeneralization')
            if any(term in combined for term in ('disclosure', 'share', 'medical records', 'phi', 'personal data')):
                categories.add('disclosure')

        return list(categories)

    def _load_patterns(self) -> Dict[str, List[Dict]]:
        """
        Define regex patterns and replacement strategies for each category.
        """
        return {
            'absolute_claim': [
                {
                    'regex': re.compile(
                        r'\b(guaranteed|guarantee|certain|definite|assured)\s+((?:\d+%|\w+)\s+(?:return|returns|profit|profits|gain|gains|growth))',
                        re.IGNORECASE,
                    ),
                    'replacer': lambda match: self._soften_absolute(match),
                },
                {
                    'regex': re.compile(r'\b(100%\s+(?:success|guarantee|certainty))\b', re.IGNORECASE),
                    'replacer': lambda m: f"historically strong performance (no guarantee)",
                },
                {
                    'regex': re.compile(r'\b(balance|capital)\s+will\s+never\s+decrease\b', re.IGNORECASE),
                    'replacer': lambda m: "Capital is exposed to investment risk and may decrease in adverse market conditions",
                },
            ],
            'superlative': [
                {
                    'regex': re.compile(
                        r'\b(best|leading|number\s+one|#1|unmatched|unsurpassed|ultimate|revolutionary|exclusive)\b',
                        re.IGNORECASE,
                    ),
                    'replacer': lambda m: self._replace_superlative(m.group(0)),
                },
            ],
            'risk_minimization': [
                {
                    'regex': re.compile(r'\b(no\s+risk|risk-free|zero\s+risk|fully\s+safe|completely\s+secure)\b', re.IGNORECASE),
                    'replacer': lambda m: "Investments involve risk and are not guaranteed",
                },
                {
                    'regex': re.compile(r'\b(capital\s+is\s+(?:fully\s+)?protected)\b', re.IGNORECASE),
                    'replacer': lambda m: "Capital is exposed to market risk; safeguards are applied but losses remain possible",
                },
            ],
            'urgency': [
                {
                    'regex': re.compile(
                        r'\b(limited\s+time|act\s+now|don\'t\s+miss|spots\s+filling|only\s+\d+\s+left)\b',
                        re.IGNORECASE,
                    ),
                    'replacer': lambda m: "Currently available based on capacity",
                },
            ],
            'overgeneralization': [
                {
                    'regex': re.compile(r'\b(for|available\s+to)\s+(everyone|anyone|all\s+investors|every\s+saver)\b', re.IGNORECASE),
                    'replacer': lambda m: "for individuals who meet our suitability and eligibility criteria",
                },
            ],
            'disclosure': [
                {
                    'regex': re.compile(r'\bwe\s+share\s+your\s+(?:medical|health|financial)\s+(?:records|information|data)\s+with\s+partners\b', re.IGNORECASE),
                    'replacer': lambda m: "We share personal data with approved partners only where a lawful basis and appropriate safeguards exist, and we will inform you and obtain consent where required",
                },
            ],
            'regulatory_bypass': [
                {
                    'regex': re.compile(r'\b(no\s+need\s+for\s+(?:additional\s+)?fca\s+oversight|no\s+approval\s+required)\b', re.IGNORECASE),
                    'replacer': lambda m: "Financial promotions are issued or approved by an FCA-authorised firm where required",
                },
                {
                    'regex': re.compile(r'\b(pre-approved\s+by\s+our\s+team)\b', re.IGNORECASE),
                    'replacer': lambda m: "Reviewed by our compliance function and, where required, approved by an FCA-authorised person",
                },
            ],
        }

    def _soften_absolute(self, match: re.Match) -> str:
        prefix = match.group(1)
        suffix = match.group(2)
        if re.search(r'\d+%', suffix):
            return f"target {suffix} (not guaranteed)"
        return f"Potential {suffix} depending on market conditions"

    def _replace_superlative(self, word: str) -> str:
        replacements = {
            'best': 'leading',
            'number one': 'well-regarded',
            '#1': 'leading',
            'unmatched': 'high quality',
            'unsurpassed': 'high quality',
            'ultimate': 'comprehensive',
            'revolutionary': 'innovative',
            'exclusive': 'specialised',
        }
        return replacements.get(word.lower(), f"highly regarded")

    def _replacement_sub(self, text: str, start: int, end: int, replacement: str) -> str:
        return text[:start] + replacement + text[end:]

    def _ensure_structural_spacing(self, category: str, pattern_def: Dict, text: str) -> None:
        # Placeholder for future context-aware spacing adjustments
        return None

    def _merge_actions(self, actions: List[SanitizationAction]) -> List[SanitizationAction]:
        merged: Dict[Tuple[str, str, str], SanitizationAction] = {}
        for action in actions:
            key = (action.pattern_type, action.original, action.replacement)
            if key not in merged:
                merged[key] = action
            else:
                merged[key].count += 1
        return list(merged.values())

    def _confidence_score(self, original: str, sanitized: str, actions: List[SanitizationAction]) -> float:
        if not original:
            return 0.0
        ratio = 1.0 - (len(original) - len(sanitized)) / max(len(original), 1)
        adjustment = min(len(actions) / 10.0, 0.3)
        return max(0.0, min(1.0, 0.7 + adjustment - abs(1.0 - ratio)))

