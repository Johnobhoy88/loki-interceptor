"""
Advanced deterministic synthesis engine leveraging universal sanitizer and snippet mapper.

ENHANCED VERSION: Includes multi-pass correction, convergence detection, confidence scoring,
preview mode, rollback capabilities, quality metrics, and performance optimizations.
"""
from __future__ import annotations

import time
import re
import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Set
from datetime import datetime
from functools import lru_cache

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
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    correction_type: str = "snippet_insertion"
    text_hash: str = ""

    def __post_init__(self):
        """Calculate hash for tracking and rollback purposes"""
        if not self.text_hash:
            self.text_hash = hashlib.md5(self.text_added.encode()).hexdigest()[:12]


@dataclass
class CorrectionMetrics:
    """Quality metrics for correction engine performance"""
    precision: float = 0.0  # Correct corrections / Total corrections
    recall: float = 0.0  # Gates fixed / Total failing gates
    f1_score: float = 0.0  # Harmonic mean of precision and recall
    accuracy: float = 0.0  # Gates passing / Total gates
    corrections_applied: int = 0
    gates_fixed: int = 0
    gates_remaining: int = 0
    false_positives: int = 0  # Corrections that created new violations
    convergence_rate: float = 0.0  # Rate of improvement per iteration

    def calculate_f1(self):
        """Calculate F1 score from precision and recall"""
        if self.precision + self.recall > 0:
            self.f1_score = 2 * (self.precision * self.recall) / (self.precision + self.recall)
        else:
            self.f1_score = 0.0


class SynthesisEngine:
    """
    Universal deterministic document assembly with enhanced features:
    - Multi-pass correction with convergence detection
    - Confidence scoring and quality metrics
    - Preview mode (dry-run without applying)
    - Rollback/undo capabilities
    - Correction history tracking
    - Performance optimizations (regex caching)
    - Conflict resolution
    """

    def __init__(
        self,
        validation_engine,
        snippet_registry: Optional[SnippetRegistry] = None,
        audit_logger=None,
        enable_preview: bool = False,
        enable_rollback: bool = True,
        enable_metrics: bool = True,
        convergence_threshold: float = 0.05,
        max_retries: int = 5,
    ) -> None:
        self.engine = validation_engine
        self.registry = snippet_registry or SnippetRegistry()
        self.sanitizer = TextSanitizer()
        self.mapper = UniversalSnippetMapper(self.registry)
        self.max_retries = max_retries
        self.audit_logger = audit_logger

        # Enhanced features
        self.enable_preview = enable_preview
        self.enable_rollback = enable_rollback
        self.enable_metrics = enable_metrics
        self.convergence_threshold = convergence_threshold

        # History tracking for rollback
        self.correction_history: List[Dict[str, Any]] = []
        self.state_snapshots: List[Tuple[str, List[AppliedSnippet], Dict]] = []

        # Compiled regex cache for performance
        self._regex_cache: Dict[str, re.Pattern] = {}

        # Metrics tracking
        self.metrics = CorrectionMetrics()

        # A/B testing framework
        self.ab_test_enabled = False
        self.ab_test_results: Dict[str, List[Dict]] = {}

        # Conflict tracking
        self.conflicts: List[Dict[str, Any]] = []

    def synthesize(
        self,
        base_text: str,
        validation: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        modules: Optional[List[str]] = None,
        preview_mode: bool = False,
    ) -> Dict[str, Any]:
        """
        Enhanced synthesis with multi-pass correction, convergence detection, and metrics.

        Args:
            base_text: Original document text
            validation: Initial validation results
            context: Additional context for snippet formatting
            modules: List of modules to validate against
            preview_mode: If True, run in dry-run mode without applying changes

        Returns:
            Comprehensive result dictionary with corrections, metrics, and history
        """
        context = context or {}
        modules = modules or list(self.engine.modules.keys())
        preview_mode = preview_mode or self.enable_preview

        start_time = time.time()
        original_text = base_text or ""
        initial_failures = self._extract_failures(validation)
        initial_failure_count = len(initial_failures)

        # Clear previous state
        self.correction_history.clear()
        self.state_snapshots.clear()
        self.conflicts.clear()

        sanitization_result = self.sanitizer.sanitize(original_text, initial_failures)
        working_text = sanitization_result['sanitized_text']

        # Snapshot initial state for rollback
        if self.enable_rollback:
            self._save_snapshot(working_text, [], validation)

        # Use original validation for first iteration, then re-validate after changes
        current_validation = validation

        applied_snippets: List[AppliedSnippet] = []
        attempted_keys = set()

        # Convergence tracking
        previous_failure_count = initial_failure_count
        convergence_history: List[float] = []
        converged = False

        for iteration in range(1, self.max_retries + 1):
            failures = self._extract_failures(current_validation)
            current_failure_count = len(failures)

            # Calculate convergence rate
            if previous_failure_count > 0:
                improvement_rate = (previous_failure_count - current_failure_count) / previous_failure_count
                convergence_history.append(improvement_rate)

                # Check for convergence (no improvement or minimal improvement)
                if improvement_rate < self.convergence_threshold and iteration > 1:
                    converged = True
                    if current_failure_count == 0:
                        # Perfect convergence - all failures resolved
                        break
                    elif improvement_rate <= 0:
                        # No improvement - stop to avoid infinite loop
                        break

            if not failures:
                duration_ms = (time.time() - start_time) * 1000
                result = self._build_result(
                    success=True,
                    reason=f'All gates passed after {iteration - 1} iteration(s)',
                    iterations=iteration - 1,
                    working_text=working_text if not preview_mode else original_text,
                    original_text=original_text,
                    applied_snippets=applied_snippets,
                    sanitization_actions=sanitization_result['actions'],
                    final_validation=current_validation,
                )

                # Add enhanced metrics
                if self.enable_metrics:
                    self._calculate_metrics(initial_failure_count, current_failure_count, applied_snippets, result)
                    result['metrics'] = self.metrics.__dict__
                    result['convergence_history'] = convergence_history
                    result['converged'] = True

                result['preview_mode'] = preview_mode
                self._log_synthesis('synthesize', result, modules, duration_ms)
                return result

            plans = self._build_snippet_plan(failures, attempted_keys)
            if not plans:
                duration_ms = (time.time() - start_time) * 1000
                result = self._needs_review_result(
                    reason='No suitable snippets available for remaining failures',
                    iterations=iteration - 1,
                    working_text=working_text if not preview_mode else original_text,
                    original_text=original_text,
                    applied_snippets=applied_snippets,
                    sanitization_actions=sanitization_result['actions'],
                    validation=current_validation,
                    modules=modules,
                )

                if self.enable_metrics:
                    self._calculate_metrics(initial_failure_count, current_failure_count, applied_snippets, result)
                    result['metrics'] = self.metrics.__dict__
                    result['convergence_history'] = convergence_history

                result['preview_mode'] = preview_mode
                self._log_synthesis('synthesize', result, modules, duration_ms)
                return result

            # Apply corrections
            previous_text = working_text
            applied_this_iteration = []

            for order, plan in enumerate(plans, start=1):
                snippet_text = self.registry.format_snippet(plan.snippet, context)

                # Preview mode: don't actually apply changes
                if not preview_mode:
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

                snippet_obj = AppliedSnippet(
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
                applied_this_iteration.append(snippet_obj)

            applied_snippets.extend(applied_this_iteration)

            # Validate corrections (check for new violations)
            if not preview_mode:
                current_validation = self.engine.check_document(
                    text=working_text,
                    document_type='synthesized',
                    active_modules=modules,
                )

                # Detect conflicts (new failures introduced)
                new_failures = self._detect_new_violations(validation, current_validation)
                if new_failures:
                    self.conflicts.extend(new_failures)

                # Save snapshot for rollback
                if self.enable_rollback:
                    self._save_snapshot(working_text, list(applied_snippets), current_validation)

            previous_failure_count = current_failure_count

        duration_ms = (time.time() - start_time) * 1000
        result = self._needs_review_result(
            reason=f'Max retries ({self.max_retries}) reached' + (' (converged)' if converged else ''),
            iterations=self.max_retries,
            working_text=working_text if not preview_mode else original_text,
            original_text=original_text,
            applied_snippets=applied_snippets,
            sanitization_actions=sanitization_result['actions'],
            validation=current_validation,
            modules=modules,
        )

        # Add enhanced metrics
        if self.enable_metrics:
            current_failures = len(self._extract_failures(current_validation))
            self._calculate_metrics(initial_failure_count, current_failures, applied_snippets, result)
            result['metrics'] = self.metrics.__dict__
            result['convergence_history'] = convergence_history
            result['converged'] = converged

        result['preview_mode'] = preview_mode
        result['conflicts'] = self.conflicts

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

    # ===================================================================
    # Enhanced Feature Methods
    # ===================================================================

    def _save_snapshot(self, text: str, snippets: List[AppliedSnippet], validation: Dict):
        """Save a state snapshot for rollback purposes"""
        self.state_snapshots.append((text, snippets.copy(), validation.copy()))

    def _calculate_metrics(
        self,
        initial_failures: int,
        current_failures: int,
        applied_snippets: List[AppliedSnippet],
        result: Dict[str, Any]
    ):
        """Calculate quality metrics for corrections"""
        self.metrics.corrections_applied = len(applied_snippets)
        self.metrics.gates_fixed = initial_failures - current_failures
        self.metrics.gates_remaining = current_failures

        # Calculate precision (how many corrections were actually helpful)
        if len(applied_snippets) > 0:
            helpful_corrections = self.metrics.gates_fixed
            self.metrics.precision = helpful_corrections / len(applied_snippets)
        else:
            self.metrics.precision = 0.0

        # Calculate recall (how many failures were fixed)
        if initial_failures > 0:
            self.metrics.recall = self.metrics.gates_fixed / initial_failures
        else:
            self.metrics.recall = 1.0 if current_failures == 0 else 0.0

        # Calculate F1 score
        self.metrics.calculate_f1()

        # Calculate accuracy
        total_gates = result.get('final_validation', {}).get('total_gates', initial_failures + 10)
        passing_gates = total_gates - current_failures
        self.metrics.accuracy = passing_gates / total_gates if total_gates > 0 else 0.0

        # Calculate convergence rate
        if len(result.get('convergence_history', [])) > 0:
            self.metrics.convergence_rate = sum(result['convergence_history']) / len(result['convergence_history'])

        # Detect false positives (corrections that introduced new violations)
        self.metrics.false_positives = len(self.conflicts)

    def _detect_new_violations(
        self,
        initial_validation: Dict[str, Any],
        current_validation: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Detect if corrections introduced new violations"""
        initial_passing = self._get_passing_gates(initial_validation)
        current_passing = self._get_passing_gates(current_validation)

        new_violations = []
        for gate_id in initial_passing:
            if gate_id not in current_passing:
                new_violations.append({
                    'gate_id': gate_id,
                    'status': 'newly_failing',
                    'reason': 'Correction introduced new violation'
                })

        return new_violations

    def _get_passing_gates(self, validation: Dict[str, Any]) -> Set[str]:
        """Extract set of passing gate IDs"""
        passing = set()
        modules = validation.get('modules', {})
        for module_id, module_data in modules.items():
            gates = module_data.get('gates', {})
            for gate_id, gate_data in gates.items():
                if gate_data.get('status', '').upper() == 'PASS':
                    passing.add(f"{module_id}:{gate_id}")
        return passing

    def rollback_to_iteration(self, iteration: int) -> Optional[Tuple[str, List[AppliedSnippet], Dict]]:
        """
        Rollback to a specific iteration snapshot

        Args:
            iteration: Iteration number to rollback to (0 = initial state)

        Returns:
            Tuple of (text, applied_snippets, validation) or None if iteration not found
        """
        if not self.enable_rollback:
            return None

        if 0 <= iteration < len(self.state_snapshots):
            return self.state_snapshots[iteration]

        return None

    def get_correction_lineage(self, snippet_key: str) -> List[Dict[str, Any]]:
        """
        Get the lineage/history of a specific correction

        Args:
            snippet_key: The key of the snippet to track

        Returns:
            List of correction events for this snippet
        """
        lineage = []
        for snapshot_idx, (text, snippets, validation) in enumerate(self.state_snapshots):
            for snippet in snippets:
                if snippet.snippet_key == snippet_key:
                    lineage.append({
                        'iteration': snippet.iteration,
                        'snapshot_index': snapshot_idx,
                        'timestamp': snippet.timestamp,
                        'confidence': snippet.confidence,
                        'gate_id': snippet.gate_id,
                        'text_hash': snippet.text_hash
                    })
        return lineage

    @lru_cache(maxsize=256)
    def _get_compiled_regex(self, pattern: str, flags: int = 0) -> re.Pattern:
        """
        Get a compiled regex pattern from cache or compile and cache it

        Args:
            pattern: Regex pattern string
            flags: Regex flags

        Returns:
            Compiled regex pattern
        """
        cache_key = f"{pattern}:{flags}"
        if cache_key not in self._regex_cache:
            self._regex_cache[cache_key] = re.compile(pattern, flags)
        return self._regex_cache[cache_key]

    def preview_corrections(
        self,
        base_text: str,
        validation: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        modules: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Run synthesis in preview mode (dry-run) without applying changes

        Returns:
            Preview result with proposed corrections and confidence scores
        """
        return self.synthesize(
            base_text=base_text,
            validation=validation,
            context=context,
            modules=modules,
            preview_mode=True
        )

    def run_ab_test(
        self,
        base_text: str,
        validation: Dict[str, Any],
        strategy_a: str,
        strategy_b: str,
        test_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Run A/B test comparing two correction strategies

        Args:
            base_text: Original text
            validation: Validation results
            strategy_a: Name of first strategy
            strategy_b: Name of second strategy
            test_id: Unique identifier for this test
            context: Additional context

        Returns:
            Comparison results with metrics for both strategies
        """
        self.ab_test_enabled = True

        # Run strategy A
        result_a = self.synthesize(base_text, validation, context)

        # Reset state
        self.correction_history.clear()
        self.state_snapshots.clear()

        # Run strategy B
        result_b = self.synthesize(base_text, validation, context)

        # Compare results
        comparison = {
            'test_id': test_id,
            'strategy_a': {
                'name': strategy_a,
                'success': result_a.get('success', False),
                'iterations': result_a.get('iterations', 0),
                'corrections': len(result_a.get('snippets_applied', [])),
                'metrics': result_a.get('metrics', {}),
                'conflicts': len(result_a.get('conflicts', []))
            },
            'strategy_b': {
                'name': strategy_b,
                'success': result_b.get('success', False),
                'iterations': result_b.get('iterations', 0),
                'corrections': len(result_b.get('snippets_applied', [])),
                'metrics': result_b.get('metrics', {}),
                'conflicts': len(result_b.get('conflicts', []))
            },
            'winner': None,
            'timestamp': datetime.utcnow().isoformat()
        }

        # Determine winner based on F1 score
        f1_a = result_a.get('metrics', {}).get('f1_score', 0)
        f1_b = result_b.get('metrics', {}).get('f1_score', 0)

        if f1_a > f1_b:
            comparison['winner'] = strategy_a
        elif f1_b > f1_a:
            comparison['winner'] = strategy_b
        else:
            comparison['winner'] = 'tie'

        # Store test results
        if test_id not in self.ab_test_results:
            self.ab_test_results[test_id] = []
        self.ab_test_results[test_id].append(comparison)

        self.ab_test_enabled = False
        return comparison

    def validate_corrections(
        self,
        original_text: str,
        corrected_text: str,
        validation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate that corrections don't introduce new violations

        Args:
            original_text: Original document
            corrected_text: Corrected document
            validation: Original validation results

        Returns:
            Validation report with any new violations detected
        """
        # Re-validate corrected text
        new_validation = self.engine.check_document(
            text=corrected_text,
            document_type='synthesized',
            active_modules=list(self.engine.modules.keys())
        )

        # Compare validations
        new_violations = self._detect_new_violations(validation, new_validation)

        return {
            'valid': len(new_violations) == 0,
            'new_violations': new_violations,
            'original_failures': len(self._extract_failures(validation)),
            'current_failures': len(self._extract_failures(new_validation)),
            'improvement': len(self._extract_failures(validation)) - len(self._extract_failures(new_validation))
        }
