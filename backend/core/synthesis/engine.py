"""
Synthesis Engine - Deterministic Compliance Document Assembly
Pure Python - no AI, deterministic text operations with retry validation
"""
from __future__ import annotations
import re
import time
from typing import Dict, List, Any, Optional, Tuple
from .snippets import SnippetRegistry, ComplianceSnippet


class SynthesisEngine:
    """
    Assembles compliant documents by applying deterministic snippet templates
    to satisfy gate failures. Retries validation until all gates pass or limit reached.
    """

    def __init__(self, validation_engine, snippet_registry: Optional[SnippetRegistry] = None, audit_logger=None):
        """
        Args:
            validation_engine: LOKI engine instance for re-validation
            snippet_registry: SnippetRegistry instance (or creates new one)
            audit_logger: Optional AuditLogger instance for telemetry
        """
        self.engine = validation_engine
        self.registry = snippet_registry or SnippetRegistry()
        self.max_retries = 5
        self.audit_logger = audit_logger  # Will be injected by server.py

    def synthesize(
        self,
        base_text: str,
        validation: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        modules: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a compliant document by applying snippets to satisfy gate failures.

        Args:
            base_text: Original document text (may be empty or from best provider)
            validation: Initial validation results with gate failures
            context: Template variables (firm_name, contact_details, etc.)
            modules: List of modules to validate against

        Returns:
            {
                'synthesized_text': str,
                'iterations': int,
                'snippets_applied': List[Dict],
                'final_validation': Dict,
                'success': bool,
                'reason': str
            }
        """
        context = context or {}
        modules = modules or list(self.engine.modules.keys())

        # Track synthesis metadata and timing
        start_time = time.time()
        applied_snippets: List[Dict[str, Any]] = []
        iteration = 0
        original_text = base_text or ""
        current_text, sanitization_actions = self._sanitize_text(original_text)
        current_validation = validation
        applied_keys = set()
        previous_failure_count = None

        for iteration in range(1, self.max_retries + 1):
            failure_count = self._count_failures(current_validation)

            if failure_count == 0:
                duration_ms = (time.time() - start_time) * 1000
                result = {
                    'synthesized_text': current_text,
                    'original_text': original_text,
                    'iterations': iteration - 1,
                    'snippets_applied': applied_snippets,
                    'final_validation': current_validation,
                    'success': True,
                    'reason': 'All gates passed',
                    'sanitization': {'actions': sanitization_actions}
                }
                self._log_synthesis_telemetry('synthesize', result, modules, duration_ms)
                return result

            # Get snippets needed for current failures
            needed_snippets = [
                snippet for snippet in self.registry.get_snippets_for_failures(current_validation)
                if self._snippet_key(snippet) not in applied_keys
            ]

            if not needed_snippets:
                duration_ms = (time.time() - start_time) * 1000
                result = {
                    'synthesized_text': current_text,
                    'original_text': original_text,
                    'iterations': iteration - 1,
                    'snippets_applied': applied_snippets,
                    'final_validation': current_validation,
                    'success': False,
                    'reason': f'No snippets available for {failure_count} remaining failures.',
                    'sanitization': {'actions': sanitization_actions}
                }
                # Add NeedsReview payload
                result.update(self._extract_needs_review_payload(current_validation, result['reason'], modules))
                self._log_synthesis_telemetry('synthesize', result, modules, duration_ms)

                # Also log to needs_review tracking
                if self.audit_logger:
                    try:
                        self.audit_logger.log_needs_review(
                            failing_gates=result['failing_gates'],
                            reason=result['reason'],
                            modules=modules
                        )
                    except Exception:
                        pass

                return result

            # Apply snippets to document
            modified_text, applied_in_iteration = self._apply_snippets(
                current_text,
                needed_snippets,
                context
            )

            # Annotate snippet metadata with iteration/order for audit clarity
            start_index = len(applied_snippets)
            for offset, metadata in enumerate(applied_in_iteration):
                metadata['iteration'] = iteration
                metadata['order'] = start_index + offset + 1
                if metadata.get('snippet_key'):
                    applied_keys.add(metadata['snippet_key'])

            # Track applied snippets
            applied_snippets.extend(applied_in_iteration)
            current_text = modified_text

            # Re-validate the synthesized text
            current_validation = self.engine.check_document(
                text=current_text,
                document_type='synthesized',
                active_modules=modules
            )

            # Check if we've resolved all failures
            if self._count_failures(current_validation) == 0:
                duration_ms = (time.time() - start_time) * 1000
                result = {
                    'synthesized_text': current_text,
                    'original_text': original_text,
                    'iterations': iteration,
                    'snippets_applied': applied_snippets,
                    'final_validation': current_validation,
                    'success': True,
                    'reason': f'All gates passed after {iteration} iteration(s)',
                    'sanitization': {'actions': sanitization_actions}
                }
                self._log_synthesis_telemetry('synthesize', result, modules, duration_ms)
                return result

            new_failure_count = self._count_failures(current_validation)
            if previous_failure_count is not None and new_failure_count >= previous_failure_count and not applied_in_iteration:
                break
            previous_failure_count = new_failure_count

        # Max retries reached - NeedsReview
        duration_ms = (time.time() - start_time) * 1000
        result = {
            'synthesized_text': current_text,
            'original_text': original_text,
            'iterations': self.max_retries,
            'snippets_applied': applied_snippets,
            'final_validation': current_validation,
            'success': False,
            'reason': f'Max retries ({self.max_retries}) reached, {self._count_failures(current_validation)} failures remain',
            'sanitization': {'actions': sanitization_actions}
        }
        # Add NeedsReview payload
        result.update(self._extract_needs_review_payload(current_validation, result['reason'], modules))
        self._log_synthesis_telemetry('synthesize', result, modules, duration_ms)

        # Also log to needs_review tracking
        if self.audit_logger:
            try:
                self.audit_logger.log_needs_review(
                    failing_gates=result['failing_gates'],
                    reason=result['reason'],
                    modules=modules
                )
            except Exception:
                pass

        return result

    def _apply_snippets(
        self,
        text: str,
        snippets: List[ComplianceSnippet],
        context: Dict[str, Any]
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Apply a list of snippets to the text.

        Returns:
            (modified_text, applied_snippet_metadata)
        """
        modified_text = text
        applied_metadata = []

        # Group snippets by insertion point
        start_snippets = [s for s in snippets if s.insertion_point == 'start']
        end_snippets = [s for s in snippets if s.insertion_point == 'end']
        section_snippets = [s for s in snippets if s.insertion_point == 'section']

        # Apply start snippets (prepend)
        for snippet in start_snippets:
            formatted = self.registry.format_snippet(snippet, context)
            modified_text = formatted + modified_text
            applied_metadata.append({
                'gate_id': snippet.gate_id,
                'module_id': snippet.module_id,
                'severity': snippet.severity,
                'insertion_point': snippet.insertion_point,
                'text_added': formatted.strip(),
                'snippet_key': self._snippet_key(snippet)
            })

        # Apply section snippets (insert at section or append)
        for snippet in section_snippets:
            formatted = self.registry.format_snippet(snippet, context)
            modified_text = self._insert_section(modified_text, formatted, snippet.section_header)
            applied_metadata.append({
                'gate_id': snippet.gate_id,
                'module_id': snippet.module_id,
                'severity': snippet.severity,
                'insertion_point': snippet.insertion_point,
                'section_header': snippet.section_header,
                'text_added': formatted.strip(),
                'snippet_key': self._snippet_key(snippet)
            })

        # Apply end snippets (append)
        for snippet in end_snippets:
            formatted = self.registry.format_snippet(snippet, context)
            modified_text = modified_text + formatted
            applied_metadata.append({
                'gate_id': snippet.gate_id,
                'module_id': snippet.module_id,
                'severity': snippet.severity,
                'insertion_point': snippet.insertion_point,
                'text_added': formatted.strip(),
                'snippet_key': self._snippet_key(snippet)
            })

        return modified_text, applied_metadata

    def _insert_section(self, text: str, section_content: str, section_header: Optional[str]) -> str:
        """
        Insert a section into the document. If section header exists, replace it.
        Otherwise, append to end.
        """
        if not section_header:
            return text + section_content

        # Try to find existing section header
        # Look for patterns like "SECTION HEADER:" or "## Section Header"
        header_patterns = [
            rf"^{re.escape(section_header)}:\s*$",
            rf"^#+\s*{re.escape(section_header)}\s*$",
        ]

        for pattern in header_patterns:
            match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
            if match:
                # Section exists - replace it
                # Find next section or end
                section_start = match.end()
                next_section = re.search(r'\n\n[A-Z\s]+:', text[section_start:])
                if next_section:
                    section_end = section_start + next_section.start()
                    text = text[:section_start] + section_content + text[section_end:]
                else:
                    text = text[:section_start] + section_content
                return text

        # Section doesn't exist - append to end
        return text + section_content

    def _count_failures(self, validation: Dict[str, Any]) -> int:
        """Count total FAIL gates across all modules"""
        count = 0
        modules = validation.get('modules', {})
        for module_payload in modules.values():
            gates = module_payload.get('gates', {})
            for gate_result in gates.values():
                if gate_result.get('status') == 'FAIL':
                    count += 1
        return count

    @staticmethod
    def _snippet_key(snippet: ComplianceSnippet) -> str:
        return f"{snippet.module_id}:{snippet.gate_id}:{snippet.insertion_point}"

    def _sanitize_text(self, text: str) -> Tuple[str, List[Dict[str, Any]]]:
        actions: List[Dict[str, Any]] = []
        updated = text or ''

        replacements = [
            (re.compile(r"\b\d+%\s+guaranteed\s+returns?\b", re.IGNORECASE), "Target returns vary according to market conditions and are not guaranteed."),
            (re.compile(r"\bguaranteed\s+returns?\b", re.IGNORECASE), "Returns depend on market performance and are not guaranteed."),
            (re.compile(r"\bzero\s+downside\b", re.IGNORECASE), "All investments carry risk, including possible loss of capital."),
            (re.compile(r"\bno\s+fca\s+approval\s+required\b", re.IGNORECASE), "Financial promotions must be issued or approved by an FCA-authorised firm."),
            (re.compile(r"\bevery\s+saver\s+qualifies\s+immediately\b", re.IGNORECASE), "Eligibility is subject to our target-market criteria and suitability checks."),
            (re.compile(r"\bcapital\s+is\s+always\s+safe\b", re.IGNORECASE), "Capital is exposed to investment risk and may fall in value."),
            (re.compile(r"\brisk[-\s]*free\b", re.IGNORECASE), "Investments involve risk and capital is not guaranteed."),
            (re.compile(r"\bguaranteed\s+liquidity\b", re.IGNORECASE), "Liquidity is subject to notice periods and market conditions."),
            (re.compile(r"\binstant\s+withdrawals?\s+guaranteed\b", re.IGNORECASE), "Withdrawal requests are processed in line with contractual terms and may be subject to notice periods.")
        ]

        removal_patterns = [
            re.compile(r"^.*referral program.*$", re.IGNORECASE | re.MULTILINE),
            re.compile(r"^.*double\s+your\s+returns?.*$", re.IGNORECASE | re.MULTILINE)
        ]

        for pattern, replacement in replacements:
            if pattern.search(updated):
                updated, count = pattern.subn(replacement, updated)
                if count:
                    actions.append({'pattern': pattern.pattern, 'replacement': replacement, 'count': count})

        for pattern in removal_patterns:
            if pattern.search(updated):
                updated, count = pattern.subn('', updated)
                if count:
                    actions.append({'pattern': pattern.pattern, 'replacement': '[removed]', 'count': count})

        updated = re.sub(r'\n{3,}', '\n\n', updated)

        return updated, actions

    def synthesize_from_aggregator(
        self,
        aggregator_result: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Synthesize a compliant document from aggregator results.

        Args:
            aggregator_result: Output from MultiModelAggregator.run()
            context: Template variables for snippet formatting

        Returns:
            Synthesis result with synthesized text and metadata
        """
        # Extract the selected provider's text and validation
        selected = aggregator_result.get('selected')
        if not selected:
            # No viable provider - start with empty text
            base_text = ""
            validation = {'modules': {}, 'overall_risk': 'CRITICAL'}
        else:
            base_text = selected.get('response_text', '')
            validation = selected.get('validation', {})

        modules = aggregator_result.get('modules', [])

        return self.synthesize(
            base_text=base_text,
            validation=validation,
            context=context,
            modules=modules
        )

    def _log_synthesis_telemetry(
        self,
        operation: str,
        result: Dict[str, Any],
        modules: List[str],
        duration_ms: float
    ) -> None:
        """Log synthesis telemetry if audit logger is configured."""
        if not self.audit_logger:
            return

        try:
            # Extract unresolved gates
            unresolved_gates = []
            final_validation = result.get('final_validation', {})
            for module_id, module_data in final_validation.get('modules', {}).items():
                for gate_id, gate_result in module_data.get('gates', {}).items():
                    if gate_result.get('status') == 'FAIL':
                        unresolved_gates.append(f"{module_id}:{gate_id}")

            self.audit_logger.log_synthesis(
                operation=operation,
                success=result.get('success', False),
                iterations=result.get('iterations', 0),
                snippets_applied=result.get('snippets_applied', []),
                unresolved_gates=unresolved_gates,
                modules=modules,
                duration_ms=duration_ms,
                metadata={'reason': result.get('reason', '')}
            )
        except Exception as e:
            # Don't let telemetry failures break synthesis
            print(f"Warning: Failed to log synthesis telemetry: {e}")

    def _extract_needs_review_payload(
        self,
        validation: Dict[str, Any],
        reason: str,
        modules: List[str]
    ) -> Dict[str, Any]:
        """
        Extract NeedsReview payload from validation failures.

        Returns structured data for manual review including:
        - failing_gates: List of gate details with excerpts
        - suggested_actions: Manual remediation steps
        - reason: Why synthesis couldn't complete
        """
        failing_gates = []
        suggested_actions = []

        for module_id, module_data in validation.get('modules', {}).items():
            for gate_id, gate_result in module_data.get('gates', {}).items():
                if gate_result.get('status') == 'FAIL':
                    failing_gate = {
                        'module_id': module_id,
                        'gate_id': gate_id,
                        'status': 'FAIL',
                        'severity': gate_result.get('severity', 'unknown'),
                        'message': gate_result.get('message', ''),
                        'suggestion': gate_result.get('suggestion', ''),
                        'excerpt': ''  # Could extract from document if needed
                    }
                    failing_gates.append(failing_gate)

                    # Build suggested action
                    action = f"{module_id}.{gate_id}: {gate_result.get('suggestion', gate_result.get('message', 'Review manually'))}"
                    if action not in suggested_actions:
                        suggested_actions.append(action)

        return {
            'needs_review': True,
            'reason': reason,
            'failing_gates': failing_gates,
            'offending_excerpts': [g['excerpt'] for g in failing_gates if g.get('excerpt')],
            'suggested_actions': suggested_actions[:10],  # Limit to top 10
            'modules': modules
        }
