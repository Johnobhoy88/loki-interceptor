"""
Document Corrector - Rule-Based Correction Engine
Applies fixes to documents based on gate suggestions WITHOUT using AI
"""
import re
from typing import Dict, List, Tuple, Optional


class DocumentCorrector:
    """
    Applies corrections to documents based on validation results.
    Uses regex patterns and string replacements - NO AI involved.
    """

    def __init__(self):
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

    def correct_document(self, text: str, validation_results: Dict) -> Dict:
        """
        Apply corrections to document based on validation results.

        Args:
            text: Original document text
            validation_results: Validation response from engine

        Returns:
            {
                'original': str,
                'corrected': str,
                'corrections_applied': List[dict],
                'unchanged': bool
            }
        """
        corrected_text = text
        corrections_applied = []

        # Extract all gates from all modules
        all_gates = self._extract_gates(validation_results)

        # Apply corrections based on gate failures
        for gate_id, gate_result in all_gates:
            if gate_result.get('status') in ['FAIL', 'WARNING']:
                correction = self._apply_gate_correction(
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
            'correction_count': len(corrections_applied)
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

    def _apply_gate_correction(self, text: str, gate_id: str, gate_result: Dict) -> Optional[Dict]:
        """
        Apply correction for a specific gate failure.

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
        """Add a custom correction rule."""
        self.correction_rules[rule_id] = {
            'pattern': pattern,
            'replacement': replacement,
            'reason': reason,
            'flags': flags
        }
