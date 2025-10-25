"""
Correction Synthesizer - Deterministic Synthesis Engine
Orchestrates multiple correction strategies in a repeatable, deterministic manner
Ensures consistent corrections across multiple runs with the same input
"""
import hashlib
import json
from typing import Dict, List, Optional, Tuple
from collections import OrderedDict


class CorrectionSynthesizer:
    """
    Deterministic synthesis engine that applies corrections in a consistent order
    to ensure repeatable results regardless of system state or timing
    """

    def __init__(self, strategies: List, document_type: str = None):
        """
        Initialize synthesizer with correction strategies

        Args:
            strategies: List of CorrectionStrategy instances
            document_type: Type of document being corrected (for context-aware decisions)
        """
        # Sort strategies by priority (higher priority first) then by name for determinism
        self.strategies = sorted(strategies, key=lambda s: (-s.priority, s.strategy_type))
        self.document_type = document_type

    def synthesize_corrections(self, text: str, gate_results: List[Tuple[str, Dict]],
                              context: Dict = None) -> Dict:
        """
        Apply corrections deterministically across all failing gates

        Args:
            text: Original document text
            gate_results: List of (gate_id, gate_result) tuples from validation
            context: Additional context (document_type, module_id, etc.)

        Returns:
            {
                'original': str,
                'corrected': str,
                'corrections': List[dict],
                'unchanged': bool,
                'determinism_hash': str,
                'correction_count': int,
                'strategies_applied': List[str]
            }
        """
        if context is None:
            context = {}

        # Add document type to context
        if self.document_type:
            context['document_type'] = self.document_type

        # Sort gate results deterministically by gate_id for consistent ordering
        sorted_gates = sorted(gate_results, key=lambda x: x[0])

        # Track corrections and current document state
        corrected_text = text
        all_corrections = []
        strategies_used = set()

        # Calculate initial hash for determinism verification
        initial_hash = self._calculate_input_hash(text, sorted_gates)

        # Apply corrections in deterministic order
        for gate_id, gate_result in sorted_gates:
            # Only process failures and warnings
            if gate_result.get('status') not in ['FAIL', 'WARNING']:
                continue

            # Try each strategy in priority order
            for strategy in self.strategies:
                # Check if strategy can apply
                if not strategy.can_apply(corrected_text, gate_id, gate_result):
                    continue

                # Apply strategy
                correction_result = strategy.apply(corrected_text, gate_id, gate_result, context)

                if correction_result and correction_result.get('text') != corrected_text:
                    # Update document state
                    old_text = corrected_text
                    corrected_text = correction_result['text']

                    # Record correction with metadata
                    correction_record = {
                        'gate_id': gate_id,
                        'gate_severity': gate_result.get('severity', 'unknown'),
                        'strategy': strategy.strategy_type,
                        'metadata': correction_result.get('metadata', {}),
                        'text_length_delta': len(corrected_text) - len(old_text)
                    }

                    all_corrections.append(correction_record)
                    strategies_used.add(strategy.strategy_type)

                    # Stop after first successful strategy for this gate (prevents over-correction)
                    break

        # Calculate final determinism hash
        final_hash = self._calculate_output_hash(corrected_text, all_corrections)

        return {
            'original': text,
            'corrected': corrected_text,
            'corrections': all_corrections,
            'unchanged': (text == corrected_text),
            'correction_count': len(all_corrections),
            'strategies_applied': sorted(list(strategies_used)),  # Sort for determinism
            'determinism': {
                'input_hash': initial_hash,
                'output_hash': final_hash,
                'repeatable': True  # This synthesis is deterministic
            }
        }

    def synthesize_with_context_awareness(self, text: str, gate_results: List[Tuple[str, Dict]],
                                          document_metadata: Dict) -> Dict:
        """
        Apply corrections with enhanced context awareness

        Args:
            text: Original document text
            gate_results: List of (gate_id, gate_result) tuples
            document_metadata: Rich metadata about the document
                {
                    'document_type': str,
                    'module_id': str,
                    'confidence': float,
                    'industry': str,
                    'jurisdiction': str
                }

        Returns:
            Same as synthesize_corrections but with context_aware flag
        """
        # Build enhanced context
        context = {
            'document_type': document_metadata.get('document_type', 'unknown'),
            'module_id': document_metadata.get('module_id'),
            'confidence': document_metadata.get('confidence', 1.0),
            'industry': document_metadata.get('industry'),
            'jurisdiction': document_metadata.get('jurisdiction', 'UK'),
            'context_aware': True
        }

        # Filter and prioritize corrections based on context
        filtered_gates = self._filter_gates_by_context(gate_results, context)

        # Apply corrections
        result = self.synthesize_corrections(text, filtered_gates, context)
        result['context_aware'] = True
        result['context'] = context

        return result

    def synthesize_multi_level(self, text: str, gate_results: List[Tuple[str, Dict]],
                               levels: List[str] = None) -> Dict:
        """
        Apply corrections in multiple levels/passes for complex documents

        Args:
            text: Original document text
            gate_results: List of (gate_id, gate_result) tuples
            levels: List of strategy types to apply in order
                   Default: ['suggestion_extraction', 'regex_replacement',
                            'template_insertion', 'structural_reorganization']

        Returns:
            Same as synthesize_corrections with level-by-level tracking
        """
        if levels is None:
            levels = [
                'suggestion_extraction',
                'regex_replacement',
                'template_insertion',
                'structural_reorganization'
            ]

        corrected_text = text
        all_corrections = []
        level_results = OrderedDict()

        # Apply each level in order
        for level in levels:
            # Filter strategies to only those matching this level
            level_strategies = [s for s in self.strategies if s.strategy_type == level]

            if not level_strategies:
                continue

            # Create temporary synthesizer for this level
            level_synthesizer = CorrectionSynthesizer(level_strategies, self.document_type)

            # Apply corrections at this level
            level_result = level_synthesizer.synthesize_corrections(
                corrected_text, gate_results, {'level': level}
            )

            # Update state
            corrected_text = level_result['corrected']
            all_corrections.extend(level_result['corrections'])

            # Record level results
            level_results[level] = {
                'corrections': level_result['correction_count'],
                'strategies': level_result['strategies_applied']
            }

        return {
            'original': text,
            'corrected': corrected_text,
            'corrections': all_corrections,
            'unchanged': (text == corrected_text),
            'correction_count': len(all_corrections),
            'multi_level': True,
            'levels': level_results,
            'determinism': {
                'input_hash': self._calculate_input_hash(text, gate_results),
                'output_hash': self._calculate_output_hash(corrected_text, all_corrections),
                'repeatable': True
            }
        }

    def _filter_gates_by_context(self, gate_results: List[Tuple[str, Dict]],
                                 context: Dict) -> List[Tuple[str, Dict]]:
        """
        Filter and prioritize gates based on document context

        Context-aware filtering rules:
        1. Critical failures always included
        2. Warnings filtered by relevance to document type
        3. Module-specific gates prioritized
        """
        filtered = []
        document_type = context.get('document_type', '').lower()
        module_id = context.get('module_id', '').lower()

        for gate_id, gate_result in gate_results:
            severity = gate_result.get('severity', 'low')
            status = gate_result.get('status')

            # Always include critical failures
            if severity == 'critical' and status == 'FAIL':
                filtered.append((gate_id, gate_result))
                continue

            # Include high severity failures
            if severity == 'high' and status == 'FAIL':
                filtered.append((gate_id, gate_result))
                continue

            # Context-aware warning filtering
            if status == 'WARNING':
                # Include if gate module matches document context
                if module_id and module_id in gate_id.lower():
                    filtered.append((gate_id, gate_result))
                    continue

                # Include if gate is relevant to document type
                if document_type:
                    if self._is_gate_relevant_to_doc_type(gate_id, document_type):
                        filtered.append((gate_id, gate_result))

        return filtered

    def _is_gate_relevant_to_doc_type(self, gate_id: str, document_type: str) -> bool:
        """Determine if a gate is relevant to a specific document type"""
        # Mapping of document types to relevant gate patterns
        relevance_map = {
            'financial': ['fca', 'risk', 'investment', 'promotion', 'client_money'],
            'privacy': ['gdpr', 'consent', 'data', 'retention', 'rights', 'processor'],
            'tax': ['vat', 'hmrc', 'tax', 'mtd', 'ir35'],
            'nda': ['whistleblowing', 'crime', 'harassment', 'duration', 'governing'],
            'employment': ['accompaniment', 'appeal', 'notice', 'suspension', 'dismissal'],
            'hr': ['disciplinary', 'grievance', 'accompaniment', 'evidence', 'appeal']
        }

        gate_lower = gate_id.lower()

        # Check if document type has relevant patterns
        for doc_type, patterns in relevance_map.items():
            if doc_type in document_type.lower():
                for pattern in patterns:
                    if pattern in gate_lower:
                        return True

        return False

    def _calculate_input_hash(self, text: str, gate_results: List[Tuple[str, Dict]]) -> str:
        """Calculate deterministic hash of input for verification"""
        # Create stable representation of input
        input_repr = {
            'text_hash': hashlib.sha256(text.encode('utf-8')).hexdigest(),
            'gates': sorted([
                (gate_id, gate_result.get('status'), gate_result.get('severity'))
                for gate_id, gate_result in gate_results
            ])
        }

        input_json = json.dumps(input_repr, sort_keys=True)
        return hashlib.sha256(input_json.encode('utf-8')).hexdigest()[:16]

    def _calculate_output_hash(self, text: str, corrections: List[Dict]) -> str:
        """Calculate deterministic hash of output for verification"""
        output_repr = {
            'text_hash': hashlib.sha256(text.encode('utf-8')).hexdigest(),
            'correction_count': len(corrections),
            'strategies': sorted(list(set(c['strategy'] for c in corrections)))
        }

        output_json = json.dumps(output_repr, sort_keys=True)
        return hashlib.sha256(output_json.encode('utf-8')).hexdigest()[:16]


class CorrectionValidator:
    """Validates corrections maintain document integrity and comply with rules"""

    @staticmethod
    def validate_correction(original: str, corrected: str, corrections: List[Dict]) -> Dict:
        """
        Validate that corrections are safe and maintain document structure

        Returns:
            {
                'valid': bool,
                'warnings': List[str],
                'errors': List[str]
            }
        """
        warnings = []
        errors = []

        # Check 1: Document not empty
        if not corrected or len(corrected.strip()) < 10:
            errors.append("Corrected document is empty or too short")

        # Check 2: Major deletions (>50% of content removed)
        original_len = len(original)
        corrected_len = len(corrected)
        if corrected_len < original_len * 0.5:
            warnings.append(f"Document reduced by {100 - (corrected_len/original_len*100):.1f}% - verify deletions are intentional")

        # Check 3: Excessive additions (>200% growth)
        if corrected_len > original_len * 2.0:
            warnings.append(f"Document grew by {(corrected_len/original_len - 1)*100:.1f}% - verify additions are necessary")

        # Check 4: Verify all corrections have metadata
        for correction in corrections:
            if 'strategy' not in correction:
                errors.append("Correction missing strategy information")
            if 'gate_id' not in correction:
                errors.append("Correction missing gate_id")

        # Check 5: No infinite loops (same correction applied multiple times)
        correction_fingerprints = [
            f"{c.get('gate_id')}:{c.get('strategy')}"
            for c in corrections
        ]
        if len(correction_fingerprints) != len(set(correction_fingerprints)):
            warnings.append("Same correction applied multiple times - check for loops")

        return {
            'valid': len(errors) == 0,
            'warnings': warnings,
            'errors': errors
        }
