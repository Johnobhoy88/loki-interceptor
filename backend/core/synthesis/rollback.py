"""
Rollback Manager - Undo functionality for corrections

Provides comprehensive rollback and undo capabilities:
- Rollback to specific iterations
- Undo individual corrections
- Restore previous states
- Track correction history and lineage
"""
from __future__ import annotations

import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CorrectionState:
    """Snapshot of document state at a specific point"""
    iteration: int
    timestamp: str
    text: str
    text_hash: str
    applied_snippets: List[Dict[str, Any]]
    validation: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Calculate text hash if not provided"""
        if not self.text_hash:
            self.text_hash = hashlib.sha256(self.text.encode()).hexdigest()[:16]


@dataclass
class RollbackOperation:
    """Record of a rollback operation"""
    operation_id: str
    timestamp: str
    from_iteration: int
    to_iteration: int
    reason: str
    corrections_undone: int
    success: bool
    error_message: Optional[str] = None


class RollbackManager:
    """
    Manages document state snapshots and rollback operations
    """

    def __init__(self, max_history: int = 50):
        """
        Initialize rollback manager

        Args:
            max_history: Maximum number of snapshots to keep (default 50)
        """
        self.max_history = max_history
        self.snapshots: List[CorrectionState] = []
        self.rollback_history: List[RollbackOperation] = []
        self.current_iteration = 0

    def save_snapshot(
        self,
        text: str,
        applied_snippets: List[Dict[str, Any]],
        validation: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> CorrectionState:
        """
        Save a snapshot of the current document state

        Args:
            text: Current document text
            applied_snippets: List of snippets applied so far
            validation: Current validation results
            metadata: Optional additional metadata

        Returns:
            CorrectionState object representing the snapshot
        """
        snapshot = CorrectionState(
            iteration=self.current_iteration,
            timestamp=datetime.utcnow().isoformat(),
            text=text,
            text_hash="",  # Will be calculated in __post_init__
            applied_snippets=[s.copy() if isinstance(s, dict) else s.__dict__ for s in applied_snippets],
            validation=validation.copy(),
            metadata=metadata or {}
        )

        self.snapshots.append(snapshot)
        self.current_iteration += 1

        # Trim history if exceeds max
        if len(self.snapshots) > self.max_history:
            self.snapshots = self.snapshots[-self.max_history:]

        return snapshot

    def rollback_to_iteration(
        self,
        target_iteration: int,
        reason: str = "User requested rollback"
    ) -> Tuple[bool, Optional[CorrectionState], Optional[str]]:
        """
        Rollback to a specific iteration

        Args:
            target_iteration: Iteration number to rollback to
            reason: Reason for the rollback

        Returns:
            Tuple of (success, state, error_message)
        """
        # Find the target snapshot
        target_snapshot = None
        for snapshot in self.snapshots:
            if snapshot.iteration == target_iteration:
                target_snapshot = snapshot
                break

        if target_snapshot is None:
            return False, None, f"Iteration {target_iteration} not found in history"

        # Calculate corrections undone
        current_corrections = self.snapshots[-1].applied_snippets if self.snapshots else []
        target_corrections = target_snapshot.applied_snippets
        corrections_undone = len(current_corrections) - len(target_corrections)

        # Record rollback operation
        operation = RollbackOperation(
            operation_id=hashlib.md5(f"{datetime.utcnow().isoformat()}".encode()).hexdigest()[:12],
            timestamp=datetime.utcnow().isoformat(),
            from_iteration=self.current_iteration - 1,
            to_iteration=target_iteration,
            reason=reason,
            corrections_undone=corrections_undone,
            success=True,
            error_message=None
        )

        self.rollback_history.append(operation)

        # Reset current iteration
        self.current_iteration = target_iteration + 1

        return True, target_snapshot, None

    def rollback_to_previous(
        self,
        reason: str = "Rollback to previous state"
    ) -> Tuple[bool, Optional[CorrectionState], Optional[str]]:
        """
        Rollback to the immediately previous state

        Args:
            reason: Reason for the rollback

        Returns:
            Tuple of (success, state, error_message)
        """
        if len(self.snapshots) < 2:
            return False, None, "No previous state available"

        previous_iteration = self.snapshots[-2].iteration
        return self.rollback_to_iteration(previous_iteration, reason)

    def rollback_to_original(
        self,
        reason: str = "Reset to original state"
    ) -> Tuple[bool, Optional[CorrectionState], Optional[str]]:
        """
        Rollback to the original state (iteration 0)

        Args:
            reason: Reason for the rollback

        Returns:
            Tuple of (success, state, error_message)
        """
        if not self.snapshots:
            return False, None, "No snapshots available"

        return self.rollback_to_iteration(0, reason)

    def undo_correction(
        self,
        snippet_key: str,
        reason: str = "Undo specific correction"
    ) -> Tuple[bool, Optional[CorrectionState], Optional[str]]:
        """
        Undo a specific correction by snippet key

        This finds the last iteration before this correction was applied

        Args:
            snippet_key: Key of the snippet to undo
            reason: Reason for undoing

        Returns:
            Tuple of (success, state, error_message)
        """
        # Find the iteration where this correction was first applied
        target_iteration = None

        for snapshot in self.snapshots:
            has_correction = any(
                s.get('snippet_key') == snippet_key for s in snapshot.applied_snippets
            )

            if has_correction:
                # Found first application - rollback to previous iteration
                target_iteration = snapshot.iteration - 1
                break

        if target_iteration is None:
            return False, None, f"Correction with key {snippet_key} not found in history"

        if target_iteration < 0:
            target_iteration = 0

        return self.rollback_to_iteration(target_iteration, f"{reason}: {snippet_key}")

    def undo_last_n_corrections(
        self,
        n: int,
        reason: str = "Undo last N corrections"
    ) -> Tuple[bool, Optional[CorrectionState], Optional[str]]:
        """
        Undo the last N corrections

        Args:
            n: Number of corrections to undo
            reason: Reason for undoing

        Returns:
            Tuple of (success, state, error_message)
        """
        if not self.snapshots:
            return False, None, "No snapshots available"

        current_snapshot = self.snapshots[-1]
        current_corrections = len(current_snapshot.applied_snippets)

        if n > current_corrections:
            return False, None, f"Cannot undo {n} corrections - only {current_corrections} applied"

        # Find the iteration with (current - n) corrections
        target_corrections = current_corrections - n
        target_iteration = None

        for snapshot in reversed(self.snapshots):
            if len(snapshot.applied_snippets) <= target_corrections:
                target_iteration = snapshot.iteration
                break

        if target_iteration is None:
            return False, None, "Could not find appropriate rollback point"

        return self.rollback_to_iteration(target_iteration, f"{reason}: {n} corrections")

    def get_snapshot(self, iteration: int) -> Optional[CorrectionState]:
        """
        Get a specific snapshot by iteration number

        Args:
            iteration: Iteration number to retrieve

        Returns:
            CorrectionState if found, None otherwise
        """
        for snapshot in self.snapshots:
            if snapshot.iteration == iteration:
                return snapshot
        return None

    def get_current_snapshot(self) -> Optional[CorrectionState]:
        """
        Get the most recent snapshot

        Returns:
            Latest CorrectionState or None if no snapshots
        """
        return self.snapshots[-1] if self.snapshots else None

    def get_snapshot_diff(
        self,
        from_iteration: int,
        to_iteration: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get the difference between two snapshots

        Args:
            from_iteration: Starting iteration
            to_iteration: Ending iteration

        Returns:
            Dictionary describing the differences
        """
        from_snapshot = self.get_snapshot(from_iteration)
        to_snapshot = self.get_snapshot(to_iteration)

        if not from_snapshot or not to_snapshot:
            return None

        # Calculate corrections added/removed
        from_keys = {s.get('snippet_key') for s in from_snapshot.applied_snippets}
        to_keys = {s.get('snippet_key') for s in to_snapshot.applied_snippets}

        added = to_keys - from_keys
        removed = from_keys - to_keys

        # Text differences
        text_length_diff = len(to_snapshot.text) - len(from_snapshot.text)

        return {
            'from_iteration': from_iteration,
            'to_iteration': to_iteration,
            'corrections_added': list(added),
            'corrections_removed': list(removed),
            'net_corrections': len(to_snapshot.applied_snippets) - len(from_snapshot.applied_snippets),
            'text_length_change': text_length_diff,
            'text_changed': from_snapshot.text_hash != to_snapshot.text_hash
        }

    def get_correction_lineage(self, snippet_key: str) -> List[Dict[str, Any]]:
        """
        Get the history of a specific correction across iterations

        Args:
            snippet_key: Snippet key to track

        Returns:
            List of dictionaries describing when this correction appeared
        """
        lineage = []

        for snapshot in self.snapshots:
            for snippet in snapshot.applied_snippets:
                if snippet.get('snippet_key') == snippet_key:
                    lineage.append({
                        'iteration': snapshot.iteration,
                        'timestamp': snapshot.timestamp,
                        'gate_id': snippet.get('gate_id'),
                        'module_id': snippet.get('module_id'),
                        'confidence': snippet.get('confidence'),
                        'text_hash': snippet.get('text_hash', '')
                    })
                    break  # Only first occurrence per iteration

        return lineage

    def get_rollback_history(self) -> List[RollbackOperation]:
        """
        Get the history of all rollback operations

        Returns:
            List of RollbackOperation objects
        """
        return self.rollback_history.copy()

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about rollback manager state

        Returns:
            Dictionary with statistics
        """
        return {
            'total_snapshots': len(self.snapshots),
            'current_iteration': self.current_iteration,
            'max_history': self.max_history,
            'total_rollbacks': len(self.rollback_history),
            'successful_rollbacks': sum(1 for r in self.rollback_history if r.success),
            'failed_rollbacks': sum(1 for r in self.rollback_history if not r.success),
            'oldest_snapshot_iteration': self.snapshots[0].iteration if self.snapshots else None,
            'newest_snapshot_iteration': self.snapshots[-1].iteration if self.snapshots else None,
            'total_corrections_current': len(self.snapshots[-1].applied_snippets) if self.snapshots else 0
        }

    def clear_history(self):
        """Clear all snapshots and rollback history"""
        self.snapshots.clear()
        self.rollback_history.clear()
        self.current_iteration = 0

    def export_snapshot(self, iteration: int) -> Optional[Dict[str, Any]]:
        """
        Export a snapshot as a dictionary for serialization

        Args:
            iteration: Iteration to export

        Returns:
            Dictionary representation of the snapshot
        """
        snapshot = self.get_snapshot(iteration)
        if not snapshot:
            return None

        return {
            'iteration': snapshot.iteration,
            'timestamp': snapshot.timestamp,
            'text': snapshot.text,
            'text_hash': snapshot.text_hash,
            'applied_snippets': snapshot.applied_snippets,
            'validation': snapshot.validation,
            'metadata': snapshot.metadata
        }

    def import_snapshot(self, snapshot_data: Dict[str, Any]) -> bool:
        """
        Import a snapshot from dictionary

        Args:
            snapshot_data: Dictionary with snapshot data

        Returns:
            True if successful, False otherwise
        """
        try:
            snapshot = CorrectionState(
                iteration=snapshot_data['iteration'],
                timestamp=snapshot_data['timestamp'],
                text=snapshot_data['text'],
                text_hash=snapshot_data['text_hash'],
                applied_snippets=snapshot_data['applied_snippets'],
                validation=snapshot_data['validation'],
                metadata=snapshot_data.get('metadata', {})
            )

            self.snapshots.append(snapshot)
            return True
        except (KeyError, TypeError):
            return False
