"""
Document Corrector - Enterprise-Grade Multi-Level Correction Engine
Applies fixes to documents based on gate suggestions WITHOUT using AI

Features:
- Gate-specific correction patterns (FCA, GDPR, Tax UK, NDA UK, HR Scottish)
- Context-aware correction logic that understands document type
- Deterministic synthesis ensuring repeatable corrections
- Multi-level strategies: regex replacements, template insertions, structural reorganization
"""
import re
from typing import Dict, List, Tuple, Optional

# Handle both relative and absolute imports
try:
    from .correction_strategies import (
        RegexReplacementStrategy,
        TemplateInsertionStrategy,
        StructuralReorganizationStrategy,
        SuggestionExtractionStrategy
    )
    from .correction_patterns import CorrectionPatternRegistry
    from .correction_synthesizer import CorrectionSynthesizer, CorrectionValidator
except ImportError:
    from correction_strategies import (
        RegexReplacementStrategy,
        TemplateInsertionStrategy,
        StructuralReorganizationStrategy,
        SuggestionExtractionStrategy
    )
    from correction_patterns import CorrectionPatternRegistry
    from correction_synthesizer import CorrectionSynthesizer, CorrectionValidator


class DocumentCorrector:
    """
    Advanced multi-level document correction system.

    Architecture:
    1. Multiple correction strategies (regex, template, structural, suggestion)
    2. Gate-specific patterns organized by regulatory module
    3. Deterministic synthesis engine for repeatable corrections
    4. Context-aware logic based on document type
    5. Validation layer to ensure correction integrity
    """

    def __init__(self, advanced_mode: bool = True):
        """
        Initialize corrector with advanced or legacy mode

        Args:
            advanced_mode: Use advanced multi-level correction system (default: True)
        """
        self.advanced_mode = advanced_mode

        if advanced_mode:
            # Initialize advanced correction system
            self._init_advanced_system()
        else:
            # Legacy simple correction rules
            self._init_legacy_rules()

    def _init_advanced_system(self):
        """Initialize advanced multi-level correction system"""
        # Initialize pattern registry
        self.pattern_registry = CorrectionPatternRegistry()

        # Initialize correction strategies
        self.regex_strategy = RegexReplacementStrategy()
        self.template_strategy = TemplateInsertionStrategy()
        self.structural_strategy = StructuralReorganizationStrategy()
        self.suggestion_strategy = SuggestionExtractionStrategy()

        # Register patterns with strategies
        self._register_patterns()

        # List of all strategies
        self.strategies = [
            self.suggestion_strategy,
            self.regex_strategy,
            self.template_strategy,
            self.structural_strategy
        ]

        # Validator
        self.validator = CorrectionValidator()

    def _init_legacy_rules(self):
        """Initialize legacy simple correction rules"""
        self.correction_rules = {
            # Tax UK corrections
            'vat_threshold': {
                'pattern': r'£85,?000',
                'replacement': '£90,000',
                'reason': 'Updated VAT threshold (April 2024)'
            },
            'old_vat_threshold': {
                'pattern': r'£83,?000',
                'replacement': '£90,000',
                'reason': 'Updated VAT threshold (April 2024)'
            },
            # FCA UK corrections
            'generic_risk_warning': {
                'pattern': r'investments can go down as well as up',
                'replacement': 'The value of investments can fall as well as rise and you may get back less than you invest',
                'reason': 'FCA-compliant risk warning',
                'flags': re.IGNORECASE
            },
            # GDPR corrections
            'bundled_consent': {
                'pattern': r'by using (?:this|our) (?:website|service|app),? you (?:automatically )?(?:agree|consent) to',
                'replacement': 'We request your explicit consent to',
                'reason': 'Remove forced consent',
                'flags': re.IGNORECASE
            },
        }

    def _register_patterns(self):
        """Register all patterns from registry with strategies"""
        # Register regex patterns
        for gate_pattern, patterns in self.pattern_registry.get_regex_patterns().items():
            for pattern_config in patterns:
                self.regex_strategy.register_pattern(
                    gate_pattern,
                    pattern_config['pattern'],
                    pattern_config['replacement'],
                    pattern_config['reason'],
                    pattern_config.get('flags', 0)
                )

        # Register templates
        for gate_pattern, templates in self.pattern_registry.get_templates().items():
            for template_config in templates:
                self.template_strategy.register_template(
                    gate_pattern,
                    template_config['template'],
                    template_config['position'],
                    template_config.get('condition')
                )

        # Register structural rules
        for gate_pattern, rules in self.pattern_registry.get_structural_rules().items():
            for rule in rules:
                self.structural_strategy.register_rule(
                    gate_pattern,
                    rule['type'],
                    rule['config']
                )

    def correct_document(self, text: str, validation_results: Dict,
                        document_type: str = None, advanced_options: Dict = None) -> Dict:
        """
        Apply corrections to document based on validation results.

        Args:
            text: Original document text
            validation_results: Validation response from engine
            document_type: Type of document (for context-aware corrections)
            advanced_options: Options for advanced mode
                {
                    'multi_level': bool - Use multi-level correction
                    'context_aware': bool - Use context-aware filtering
                    'document_metadata': Dict - Rich document metadata
                }

        Returns:
            {
                'original': str,
                'corrected': str,
                'corrections_applied': List[dict],
                'unchanged': bool,
                'correction_count': int,
                'validation': Dict (optional) - Validation results
                'determinism': Dict (optional) - Determinism information
            }
        """
        if advanced_options is None:
            advanced_options = {}

        if self.advanced_mode:
            return self._correct_document_advanced(text, validation_results, document_type, advanced_options)
        else:
            return self._correct_document_legacy(text, validation_results)

    def _correct_document_advanced(self, text: str, validation_results: Dict,
                                   document_type: str = None, options: Dict = None) -> Dict:
        """Advanced multi-level correction with deterministic synthesis"""
        # Extract all gates from validation results
        all_gates = self._extract_gates(validation_results)

        # Filter to only failures and warnings
        failing_gates = [
            (gate_id, gate_result)
            for gate_id, gate_result in all_gates
            if gate_result.get('status') in ['FAIL', 'WARNING']
        ]

        if not failing_gates:
            return {
                'original': text,
                'corrected': text,
                'corrections_applied': [],
                'unchanged': True,
                'correction_count': 0,
                'mode': 'advanced'
            }

        # Choose correction mode
        use_multi_level = options.get('multi_level', False)
        use_context_aware = options.get('context_aware', False)
        document_metadata = options.get('document_metadata', {})

        # Initialize synthesizer
        synthesizer = CorrectionSynthesizer(self.strategies, document_type)

        # Apply corrections
        if use_context_aware and document_metadata:
            result = synthesizer.synthesize_with_context_awareness(
                text, failing_gates, document_metadata
            )
        elif use_multi_level:
            result = synthesizer.synthesize_multi_level(text, failing_gates)
        else:
            result = synthesizer.synthesize_corrections(text, failing_gates)

        # Validate corrections
        validation = self.validator.validate_correction(
            result['original'],
            result['corrected'],
            result['corrections']
        )

        # Format response
        return {
            'original': result['original'],
            'corrected': result['corrected'],
            'corrections_applied': result['corrections'],
            'unchanged': result['unchanged'],
            'correction_count': result['correction_count'],
            'strategies_applied': result.get('strategies_applied', []),
            'determinism': result.get('determinism', {}),
            'validation': validation,
            'mode': 'advanced',
            'multi_level': result.get('multi_level', False),
            'context_aware': result.get('context_aware', False)
        }

    def _correct_document_legacy(self, text: str, validation_results: Dict) -> Dict:
        """Legacy simple correction for backwards compatibility"""
        corrected_text = text
        corrections_applied = []

        # Extract all gates from all modules
        all_gates = self._extract_gates(validation_results)

        # Apply corrections based on gate failures
        for gate_id, gate_result in all_gates:
            if gate_result.get('status') in ['FAIL', 'WARNING']:
                correction = self._apply_gate_correction_legacy(
                    corrected_text,
                    gate_id,
                    gate_result
                )
                if correction:
                    corrected_text = correction['text']
                    corrections_applied.append(correction['details'])

        return {
            'original': text,
            'corrected': corrected_text,
            'corrections_applied': corrections_applied,
            'unchanged': (text == corrected_text),
            'correction_count': len(corrections_applied),
            'mode': 'legacy'
        }

    def _extract_gates(self, validation_results: Dict) -> List[Tuple[str, Dict]]:
        """Extract all gate results from validation response."""
        gates = []

        validation = validation_results.get('validation', {})
        modules = validation.get('modules', {})

        for module_id, module_data in modules.items():
            module_gates = module_data.get('gates', {})
            for gate_id, gate_result in module_gates.items():
                gates.append((gate_id, gate_result))

        return gates

    def _apply_gate_correction_legacy(self, text: str, gate_id: str, gate_result: Dict) -> Optional[Dict]:
        """
        Apply correction for a specific gate failure (legacy method).

        Returns:
            {
                'text': str (corrected text),
                'details': {
                    'gate': str,
                    'rule': str,
                    'changes': int,
                    'reason': str
                }
            }
        """
        # Check if we have a predefined correction rule for this gate
        for rule_id, rule in self.correction_rules.items():
            if self._gate_matches_rule(gate_id, gate_result, rule_id):
                pattern = rule['pattern']
                replacement = rule['replacement']
                flags = rule.get('flags', 0)

                # Count matches before replacing
                matches = re.findall(pattern, text, flags)
                if not matches:
                    continue

                # Apply replacement
                corrected = re.sub(pattern, replacement, text, flags=flags)

                return {
                    'text': corrected,
                    'details': {
                        'gate': gate_id,
                        'rule': rule_id,
                        'changes': len(matches),
                        'reason': rule['reason'],
                        'examples': matches[:3]  # Show first 3 matches
                    }
                }

        # Try using gate suggestion if available
        suggestion = gate_result.get('suggestion', '')
        if suggestion and 'Add:' in suggestion:
            # Extract suggested text
            match = re.search(r'Add: ["\'](.+?)["\']', suggestion)
            if match:
                suggested_text = match.group(1)
                # Append to end of document
                corrected = text.strip() + '\n\n' + suggested_text
                return {
                    'text': corrected,
                    'details': {
                        'gate': gate_id,
                        'rule': 'append_suggestion',
                        'changes': 1,
                        'reason': f'Added missing content from {gate_id}',
                        'examples': [suggested_text[:100] + '...']
                    }
                }

        return None

    def _gate_matches_rule(self, gate_id: str, gate_result: Dict, rule_id: str) -> bool:
        """Check if a gate failure matches a correction rule."""
        # Map gates to rules
        gate_rule_mapping = {
            'vat_threshold': ['vat_threshold', 'old_vat_threshold'],
            'risk_warning': ['generic_risk_warning'],
            'consent': ['bundled_consent'],
        }

        for key, rules in gate_rule_mapping.items():
            if key in gate_id.lower() and rule_id in rules:
                return True

        return False

    def add_correction_rule(self, rule_id: str, pattern: str, replacement: str, reason: str, flags: int = 0):
        """Add a custom correction rule (legacy mode only)."""
        if not self.advanced_mode:
            self.correction_rules[rule_id] = {
                'pattern': pattern,
                'replacement': replacement,
                'reason': reason,
                'flags': flags
            }

    # ========================================
    # Advanced Mode Utility Methods
    # ========================================

    def get_available_corrections(self, text: str, validation_results: Dict) -> Dict:
        """
        Preview available corrections without applying them

        Returns:
            {
                'total_gates': int,
                'failing_gates': int,
                'available_corrections': List[dict],
                'estimated_changes': int
            }
        """
        if not self.advanced_mode:
            return {'error': 'Only available in advanced mode'}

        all_gates = self._extract_gates(validation_results)
        failing_gates = [
            (gate_id, gate_result)
            for gate_id, gate_result in all_gates
            if gate_result.get('status') in ['FAIL', 'WARNING']
        ]

        available_corrections = []
        for gate_id, gate_result in failing_gates:
            for strategy in self.strategies:
                if strategy.can_apply(text, gate_id, gate_result):
                    available_corrections.append({
                        'gate_id': gate_id,
                        'severity': gate_result.get('severity'),
                        'strategy': strategy.strategy_type,
                        'priority': strategy.priority
                    })

        return {
            'total_gates': len(all_gates),
            'failing_gates': len(failing_gates),
            'available_corrections': available_corrections,
            'estimated_changes': len(available_corrections)
        }

    def get_correction_statistics(self) -> Dict:
        """
        Get statistics about registered correction patterns

        Returns:
            {
                'regex_patterns': int,
                'templates': int,
                'structural_rules': int,
                'total_patterns': int,
                'modules': List[str]
            }
        """
        if not self.advanced_mode:
            return {'error': 'Only available in advanced mode'}

        patterns = self.pattern_registry.get_all_patterns()

        regex_count = sum(len(p) for p in patterns['regex'].values())
        template_count = sum(len(t) for t in patterns['templates'].values())
        structural_count = sum(len(r) for r in patterns['structural'].values())

        # Extract module names from patterns
        modules = set()
        for pattern_key in patterns['regex'].keys():
            if any(m in pattern_key for m in ['fca', 'gdpr', 'tax', 'nda', 'hr']):
                if 'fca' in pattern_key:
                    modules.add('FCA UK')
                if 'gdpr' in pattern_key or 'consent' in pattern_key or 'data' in pattern_key:
                    modules.add('GDPR UK')
                if 'vat' in pattern_key or 'tax' in pattern_key or 'hmrc' in pattern_key:
                    modules.add('Tax UK')
                if 'nda' in pattern_key or 'whistleblow' in pattern_key:
                    modules.add('NDA UK')
                if 'accompan' in pattern_key or 'appeal' in pattern_key or 'disciplinary' in pattern_key:
                    modules.add('HR Scottish')

        return {
            'regex_patterns': regex_count,
            'templates': template_count,
            'structural_rules': structural_count,
            'total_patterns': regex_count + template_count + structural_count,
            'modules': sorted(list(modules)),
            'strategies': [s.strategy_type for s in self.strategies]
        }

    def test_pattern_match(self, text: str, gate_pattern: str) -> Dict:
        """
        Test if patterns for a specific gate would match the given text

        Args:
            text: Text to test
            gate_pattern: Gate pattern to test (e.g., 'vat_threshold', 'consent')

        Returns:
            {
                'matches': List[dict],
                'would_correct': bool
            }
        """
        if not self.advanced_mode:
            return {'error': 'Only available in advanced mode'}

        matches = []

        # Test regex patterns
        regex_patterns = self.pattern_registry.get_regex_patterns(gate_pattern)
        for pattern_key, patterns in regex_patterns.items():
            for pattern_config in patterns:
                pattern_matches = re.findall(
                    pattern_config['pattern'],
                    text,
                    pattern_config.get('flags', 0)
                )
                if pattern_matches:
                    matches.append({
                        'type': 'regex',
                        'pattern_key': pattern_key,
                        'matches': pattern_matches[:5],
                        'count': len(pattern_matches)
                    })

        # Test templates
        templates = self.pattern_registry.get_templates(gate_pattern)
        for template_key, template_configs in templates.items():
            for template_config in template_configs:
                condition = template_config.get('condition')
                if condition:
                    if re.search(condition, text, re.IGNORECASE):
                        matches.append({
                            'type': 'template',
                            'template_key': template_key,
                            'position': template_config['position']
                        })
                else:
                    matches.append({
                        'type': 'template',
                        'template_key': template_key,
                        'position': template_config['position']
                    })

        return {
            'matches': matches,
            'would_correct': len(matches) > 0
        }
