"""
Conflict Resolver - Detects and resolves correction conflicts

Handles situations where corrections:
- Contradict each other
- Introduce new violations
- Overlap in their effects
- Have incompatible requirements
"""
from __future__ import annotations

from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum


class ConflictType(Enum):
    """Types of conflicts that can occur"""
    CONTRADICTORY = "contradictory"  # Corrections that contradict each other
    OVERLAP = "overlap"  # Corrections affecting same text region
    NEW_VIOLATION = "new_violation"  # Correction introduces new failure
    INCOMPATIBLE = "incompatible"  # Corrections have incompatible requirements
    REDUNDANT = "redundant"  # Correction is redundant with another


class ConflictSeverity(Enum):
    """Severity levels for conflicts"""
    CRITICAL = "critical"  # Must be resolved
    HIGH = "high"  # Should be resolved
    MEDIUM = "medium"  # Can be resolved
    LOW = "low"  # Minor issue


@dataclass
class Conflict:
    """Represents a conflict between corrections"""
    conflict_id: str
    conflict_type: ConflictType
    severity: ConflictSeverity
    corrections_involved: List[str]  # Snippet keys
    description: str
    suggested_resolution: Optional[str] = None
    auto_resolvable: bool = False


class ConflictResolver:
    """
    Detects and resolves conflicts between corrections
    """

    def __init__(self):
        self.detected_conflicts: List[Conflict] = []
        self.resolution_strategies = {
            ConflictType.CONTRADICTORY: self._resolve_contradictory,
            ConflictType.OVERLAP: self._resolve_overlap,
            ConflictType.NEW_VIOLATION: self._resolve_new_violation,
            ConflictType.INCOMPATIBLE: self._resolve_incompatible,
            ConflictType.REDUNDANT: self._resolve_redundant
        }

    def detect_conflicts(
        self,
        applied_snippets: List[Dict[str, Any]],
        initial_validation: Dict[str, Any],
        current_validation: Dict[str, Any],
        text: str
    ) -> List[Conflict]:
        """
        Detect all types of conflicts in the corrections

        Args:
            applied_snippets: List of snippets that have been applied
            initial_validation: Initial validation results
            current_validation: Current validation results after corrections
            text: Current document text

        Returns:
            List of detected conflicts
        """
        self.detected_conflicts.clear()

        # Detect each type of conflict
        self._detect_contradictory_corrections(applied_snippets)
        self._detect_overlap_conflicts(applied_snippets, text)
        self._detect_new_violations(initial_validation, current_validation, applied_snippets)
        self._detect_incompatible_corrections(applied_snippets)
        self._detect_redundant_corrections(applied_snippets)

        return self.detected_conflicts

    def _detect_contradictory_corrections(self, snippets: List[Dict[str, Any]]):
        """Detect corrections that contradict each other"""
        # Check for opposing patterns
        contradictory_pairs = [
            (['consent', 'agree'], ['withdraw', 'revoke']),
            (['mandatory', 'must'], ['optional', 'may']),
            (['always', 'all'], ['never', 'none']),
            (['guaranteed', 'certain'], ['not guaranteed', 'uncertain']),
        ]

        for i, snippet_a in enumerate(snippets):
            text_a = snippet_a.get('text_added', '').lower()
            key_a = snippet_a.get('snippet_key', '')

            for j, snippet_b in enumerate(snippets[i+1:], start=i+1):
                text_b = snippet_b.get('text_added', '').lower()
                key_b = snippet_b.get('snippet_key', '')

                for positive_terms, negative_terms in contradictory_pairs:
                    has_positive_a = any(term in text_a for term in positive_terms)
                    has_negative_b = any(term in text_b for term in negative_terms)

                    if has_positive_a and has_negative_b:
                        conflict = Conflict(
                            conflict_id=f"CONTRA_{i}_{j}",
                            conflict_type=ConflictType.CONTRADICTORY,
                            severity=ConflictSeverity.HIGH,
                            corrections_involved=[key_a, key_b],
                            description=f"Corrections {key_a} and {key_b} contain contradictory statements",
                            suggested_resolution="Review both corrections and keep the one with higher confidence",
                            auto_resolvable=True
                        )
                        self.detected_conflicts.append(conflict)

    def _detect_overlap_conflicts(self, snippets: List[Dict[str, Any]], text: str):
        """Detect corrections that overlap in their effects"""
        # Check for similar gate IDs (indicating they address same issue)
        gate_groups: Dict[str, List[Dict[str, Any]]] = {}

        for snippet in snippets:
            gate_id = snippet.get('gate_id', '').split(':')[-1]  # Get gate name without module
            if gate_id not in gate_groups:
                gate_groups[gate_id] = []
            gate_groups[gate_id].append(snippet)

        # Find groups with multiple corrections
        for gate_id, group in gate_groups.items():
            if len(group) > 1:
                conflict = Conflict(
                    conflict_id=f"OVERLAP_{gate_id}",
                    conflict_type=ConflictType.OVERLAP,
                    severity=ConflictSeverity.MEDIUM,
                    corrections_involved=[s.get('snippet_key', '') for s in group],
                    description=f"Multiple corrections ({len(group)}) targeting same gate: {gate_id}",
                    suggested_resolution="Keep the correction with highest confidence, remove others",
                    auto_resolvable=True
                )
                self.detected_conflicts.append(conflict)

    def _detect_new_violations(
        self,
        initial_validation: Dict[str, Any],
        current_validation: Dict[str, Any],
        snippets: List[Dict[str, Any]]
    ):
        """Detect if corrections introduced new violations"""
        initial_passing = self._get_passing_gates(initial_validation)
        current_passing = self._get_passing_gates(current_validation)

        newly_failing = initial_passing - current_passing

        if newly_failing:
            # Try to identify which correction caused the new failure
            for gate_id in newly_failing:
                conflict = Conflict(
                    conflict_id=f"NEWVIOL_{gate_id.replace(':', '_')}",
                    conflict_type=ConflictType.NEW_VIOLATION,
                    severity=ConflictSeverity.CRITICAL,
                    corrections_involved=[s.get('snippet_key', '') for s in snippets],
                    description=f"Corrections introduced new violation in {gate_id}",
                    suggested_resolution="Rollback and apply corrections individually to identify culprit",
                    auto_resolvable=False
                )
                self.detected_conflicts.append(conflict)

    def _detect_incompatible_corrections(self, snippets: List[Dict[str, Any]]):
        """Detect corrections with incompatible requirements"""
        # Check for module incompatibilities
        module_incompatibilities = {
            ('fca_uk', 'promotions'): ('gdpr_uk', 'consent'),  # Example: FCA promotions vs GDPR consent
        }

        for snippet_a in snippets:
            module_a = snippet_a.get('module_id', '').lower()
            gate_a = snippet_a.get('gate_id', '').lower()

            for snippet_b in snippets:
                if snippet_a == snippet_b:
                    continue

                module_b = snippet_b.get('module_id', '').lower()
                gate_b = snippet_b.get('gate_id', '').lower()

                # Check for known incompatibilities
                for (mod1, gate1), (mod2, gate2) in module_incompatibilities.items():
                    if (mod1 in module_a and gate1 in gate_a and
                        mod2 in module_b and gate2 in gate_b):
                        conflict = Conflict(
                            conflict_id=f"INCOMPAT_{snippet_a.get('snippet_key', '')}_{snippet_b.get('snippet_key', '')}",
                            conflict_type=ConflictType.INCOMPATIBLE,
                            severity=ConflictSeverity.HIGH,
                            corrections_involved=[
                                snippet_a.get('snippet_key', ''),
                                snippet_b.get('snippet_key', '')
                            ],
                            description=f"Corrections may have incompatible requirements: {module_a}.{gate_a} vs {module_b}.{gate_b}",
                            suggested_resolution="Review both corrections for compatibility",
                            auto_resolvable=False
                        )
                        self.detected_conflicts.append(conflict)

    def _detect_redundant_corrections(self, snippets: List[Dict[str, Any]]):
        """Detect redundant corrections (duplicates or subsets)"""
        for i, snippet_a in enumerate(snippets):
            text_a = snippet_a.get('text_added', '').strip().lower()
            key_a = snippet_a.get('snippet_key', '')

            for j, snippet_b in enumerate(snippets[i+1:], start=i+1):
                text_b = snippet_b.get('text_added', '').strip().lower()
                key_b = snippet_b.get('snippet_key', '')

                # Check for exact duplicates
                if text_a == text_b:
                    conflict = Conflict(
                        conflict_id=f"REDUND_{i}_{j}",
                        conflict_type=ConflictType.REDUNDANT,
                        severity=ConflictSeverity.LOW,
                        corrections_involved=[key_a, key_b],
                        description=f"Corrections {key_a} and {key_b} are identical",
                        suggested_resolution="Remove duplicate correction",
                        auto_resolvable=True
                    )
                    self.detected_conflicts.append(conflict)

                # Check for substring (one contains the other)
                elif text_a in text_b or text_b in text_a:
                    conflict = Conflict(
                        conflict_id=f"REDUND_SUB_{i}_{j}",
                        conflict_type=ConflictType.REDUNDANT,
                        severity=ConflictSeverity.LOW,
                        corrections_involved=[key_a, key_b],
                        description=f"Correction {key_a if len(text_a) < len(text_b) else key_b} is redundant (contained in the other)",
                        suggested_resolution="Keep longer, more comprehensive correction",
                        auto_resolvable=True
                    )
                    self.detected_conflicts.append(conflict)

    def resolve_conflicts(
        self,
        conflicts: Optional[List[Conflict]] = None,
        auto_resolve: bool = True
    ) -> Tuple[List[Conflict], List[str]]:
        """
        Attempt to resolve detected conflicts

        Args:
            conflicts: List of conflicts to resolve (uses detected conflicts if None)
            auto_resolve: Whether to automatically resolve conflicts marked as auto_resolvable

        Returns:
            Tuple of (unresolved_conflicts, resolution_actions)
        """
        conflicts_to_resolve = conflicts or self.detected_conflicts
        unresolved = []
        actions = []

        for conflict in conflicts_to_resolve:
            if auto_resolve and conflict.auto_resolvable:
                # Attempt automatic resolution
                resolution_func = self.resolution_strategies.get(conflict.conflict_type)
                if resolution_func:
                    resolved, action = resolution_func(conflict)
                    if resolved:
                        actions.append(action)
                    else:
                        unresolved.append(conflict)
                else:
                    unresolved.append(conflict)
            else:
                unresolved.append(conflict)

        return unresolved, actions

    def _resolve_contradictory(self, conflict: Conflict) -> Tuple[bool, str]:
        """Resolve contradictory corrections"""
        # Strategy: Keep correction with higher confidence
        action = f"Recommend manual review of corrections: {', '.join(conflict.corrections_involved)}"
        return True, action

    def _resolve_overlap(self, conflict: Conflict) -> Tuple[bool, str]:
        """Resolve overlapping corrections"""
        action = f"Remove redundant corrections for gate: {conflict.corrections_involved[0].split(':')[0]}"
        return True, action

    def _resolve_new_violation(self, conflict: Conflict) -> Tuple[bool, str]:
        """Resolve new violations (not auto-resolvable)"""
        return False, "Manual intervention required"

    def _resolve_incompatible(self, conflict: Conflict) -> Tuple[bool, str]:
        """Resolve incompatible corrections (not auto-resolvable)"""
        return False, "Manual review of requirements needed"

    def _resolve_redundant(self, conflict: Conflict) -> Tuple[bool, str]:
        """Resolve redundant corrections"""
        action = f"Remove redundant correction: {conflict.corrections_involved[-1]}"
        return True, action

    def _get_passing_gates(self, validation: Dict[str, Any]) -> Set[str]:
        """Extract set of passing gate IDs from validation"""
        passing = set()
        modules = validation.get('modules', {})

        for module_id, module_data in modules.items():
            gates = module_data.get('gates', {})
            for gate_id, gate_data in gates.items():
                if gate_data.get('status', '').upper() == 'PASS':
                    passing.add(f"{module_id}:{gate_id}")

        return passing

    def get_conflict_summary(self) -> Dict[str, Any]:
        """
        Get a summary of detected conflicts

        Returns:
            Dictionary with conflict statistics
        """
        return {
            'total_conflicts': len(self.detected_conflicts),
            'by_type': {
                conflict_type.value: sum(
                    1 for c in self.detected_conflicts if c.conflict_type == conflict_type
                )
                for conflict_type in ConflictType
            },
            'by_severity': {
                severity.value: sum(
                    1 for c in self.detected_conflicts if c.severity == severity
                )
                for severity in ConflictSeverity
            },
            'auto_resolvable': sum(1 for c in self.detected_conflicts if c.auto_resolvable),
            'requires_manual_review': sum(1 for c in self.detected_conflicts if not c.auto_resolvable)
        }

    def export_conflicts(self) -> List[Dict[str, Any]]:
        """
        Export conflicts as JSON-serializable dictionaries

        Returns:
            List of conflict dictionaries
        """
        return [
            {
                'conflict_id': c.conflict_id,
                'type': c.conflict_type.value,
                'severity': c.severity.value,
                'corrections_involved': c.corrections_involved,
                'description': c.description,
                'suggested_resolution': c.suggested_resolution,
                'auto_resolvable': c.auto_resolvable
            }
            for c in self.detected_conflicts
        ]
