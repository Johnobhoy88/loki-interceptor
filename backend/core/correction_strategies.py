"""
Correction Strategies - Multi-Level Correction Approaches
Implements different correction strategies: regex, template, structural reorganization
"""
import re
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod


class CorrectionStrategy(ABC):
    """Base class for all correction strategies"""

    def __init__(self, strategy_type: str, priority: int = 50):
        self.strategy_type = strategy_type
        self.priority = priority  # Higher priority strategies execute first

    @abstractmethod
    def can_apply(self, text: str, gate_id: str, gate_result: Dict) -> bool:
        """Determine if this strategy can be applied to the given context"""
        pass

    @abstractmethod
    def apply(self, text: str, gate_id: str, gate_result: Dict, context: Dict) -> Optional[Dict]:
        """
        Apply the correction strategy

        Returns:
            {
                'text': str (corrected text),
                'metadata': {
                    'strategy': str,
                    'changes': int,
                    'locations': List[int],
                    'reason': str,
                    'examples': List[str]
                }
            }
        """
        pass


class RegexReplacementStrategy(CorrectionStrategy):
    """Strategy for simple regex-based find and replace"""

    def __init__(self):
        super().__init__("regex_replacement", priority=30)
        self.patterns = {}  # Will be populated by correction patterns

    def register_pattern(self, gate_pattern: str, regex_pattern: str, replacement: str,
                        reason: str, flags: int = 0):
        """Register a regex pattern for a specific gate pattern"""
        if gate_pattern not in self.patterns:
            self.patterns[gate_pattern] = []

        self.patterns[gate_pattern].append({
            'regex': regex_pattern,
            'replacement': replacement,
            'reason': reason,
            'flags': flags
        })

    def can_apply(self, text: str, gate_id: str, gate_result: Dict) -> bool:
        """Check if any registered patterns match this gate"""
        gate_id_lower = gate_id.lower()
        for gate_pattern in self.patterns.keys():
            # Check bidirectional matching: pattern in gate_id OR gate_id in pattern
            if (gate_pattern in gate_id_lower or gate_id_lower in gate_pattern or
                gate_pattern in str(gate_result.get('message', '')).lower()):
                return True
        return False

    def apply(self, text: str, gate_id: str, gate_result: Dict, context: Dict) -> Optional[Dict]:
        """Apply regex replacements"""
        corrected_text = text
        total_changes = 0
        all_examples = []
        reasons = []
        locations = []

        gate_id_lower = gate_id.lower()
        for gate_pattern, patterns in self.patterns.items():
            # Check bidirectional matching: pattern in gate_id OR gate_id in pattern
            if not (gate_pattern in gate_id_lower or gate_id_lower in gate_pattern or
                   gate_pattern in str(gate_result.get('message', '')).lower()):
                continue

            for pattern_config in patterns:
                regex = pattern_config['regex']
                replacement = pattern_config['replacement']
                flags = pattern_config.get('flags', 0)

                # Find all matches and their positions
                matches = list(re.finditer(regex, corrected_text, flags))
                if matches:
                    all_examples.extend([m.group() for m in matches[:3]])
                    locations.extend([m.start() for m in matches])
                    total_changes += len(matches)
                    reasons.append(pattern_config['reason'])

                    # Apply replacement
                    corrected_text = re.sub(regex, replacement, corrected_text, flags=flags)

        if total_changes > 0:
            return {
                'text': corrected_text,
                'metadata': {
                    'strategy': self.strategy_type,
                    'changes': total_changes,
                    'locations': locations[:10],  # Limit to first 10 locations
                    'reason': '; '.join(set(reasons)),
                    'examples': all_examples[:5]  # Limit to first 5 examples
                }
            }

        return None


class TemplateInsertionStrategy(CorrectionStrategy):
    """Strategy for inserting template text (compliance clauses, warnings, etc.)"""

    def __init__(self):
        super().__init__("template_insertion", priority=40)
        self.templates = {}

    def register_template(self, gate_pattern: str, template: str, position: str,
                         condition: Optional[str] = None):
        """
        Register a template for insertion

        Args:
            gate_pattern: Pattern to match against gate_id
            template: The text to insert
            position: 'start', 'end', 'after_header', 'before_signature'
            condition: Optional regex condition that must match for insertion
        """
        if gate_pattern not in self.templates:
            self.templates[gate_pattern] = []

        self.templates[gate_pattern].append({
            'template': template,
            'position': position,
            'condition': condition
        })

    def can_apply(self, text: str, gate_id: str, gate_result: Dict) -> bool:
        """Check if we have a template for this gate"""
        gate_id_lower = gate_id.lower()
        for gate_pattern in self.templates.keys():
            # Check bidirectional matching: pattern in gate_id OR gate_id in pattern
            if gate_pattern in gate_id_lower or gate_id_lower in gate_pattern:
                return True
        return False

    def _find_insertion_point(self, text: str, position: str) -> int:
        """Find the appropriate insertion point in the document"""
        if position == 'start':
            # After any header/title if present
            header_match = re.search(r'^#.*?\n|^[A-Z\s]{5,}\n', text, re.MULTILINE)
            return header_match.end() if header_match else 0

        elif position == 'end':
            return len(text)

        elif position == 'after_header':
            # After the first major section break
            section_match = re.search(r'\n\n+', text)
            return section_match.end() if section_match else len(text) // 10

        elif position == 'before_signature':
            # Before signature block
            sig_match = re.search(r'(?:Signed|Signature|Date:).*?$', text, re.IGNORECASE | re.MULTILINE)
            return sig_match.start() if sig_match else len(text)

        return len(text)

    def apply(self, text: str, gate_id: str, gate_result: Dict, context: Dict) -> Optional[Dict]:
        """Insert templates at appropriate locations"""
        corrected_text = text
        insertions = []

        gate_id_lower = gate_id.lower()
        for gate_pattern, template_configs in self.templates.items():
            # Check bidirectional matching: pattern in gate_id OR gate_id in pattern
            if not (gate_pattern in gate_id_lower or gate_id_lower in gate_pattern):
                continue

            for template_config in template_configs:
                template = template_config['template']
                position = template_config['position']
                condition = template_config.get('condition')

                # Check condition if specified
                if condition and not re.search(condition, text, re.IGNORECASE):
                    continue

                # Check if template already exists in document
                if template.strip() in corrected_text:
                    continue

                # Find insertion point
                insertion_point = self._find_insertion_point(corrected_text, position)

                # Insert template with proper formatting
                formatted_template = f"\n\n{template.strip()}\n\n"
                corrected_text = (
                    corrected_text[:insertion_point] +
                    formatted_template +
                    corrected_text[insertion_point:]
                )

                insertions.append({
                    'template': template[:100] + '...' if len(template) > 100 else template,
                    'position': position,
                    'location': insertion_point
                })

        if insertions:
            return {
                'text': corrected_text,
                'metadata': {
                    'strategy': self.strategy_type,
                    'changes': len(insertions),
                    'locations': [ins['location'] for ins in insertions],
                    'reason': f"Inserted {len(insertions)} compliance template(s)",
                    'examples': [ins['template'] for ins in insertions]
                }
            }

        return None


class StructuralReorganizationStrategy(CorrectionStrategy):
    """Strategy for reorganizing document structure (sections, ordering, etc.)"""

    def __init__(self):
        super().__init__("structural_reorganization", priority=60)
        self.reorganization_rules = {}

    def register_rule(self, gate_pattern: str, rule_type: str, config: Dict):
        """
        Register a structural reorganization rule

        Args:
            gate_pattern: Pattern to match against gate_id
            rule_type: 'move_section', 'reorder_items', 'add_section_header', 'split_paragraph'
            config: Rule-specific configuration
        """
        if gate_pattern not in self.reorganization_rules:
            self.reorganization_rules[gate_pattern] = []

        self.reorganization_rules[gate_pattern].append({
            'type': rule_type,
            'config': config
        })

    def can_apply(self, text: str, gate_id: str, gate_result: Dict) -> bool:
        """Check if reorganization rules apply"""
        for gate_pattern in self.reorganization_rules.keys():
            if gate_pattern in gate_id.lower():
                return True
        return False

    def _move_section(self, text: str, section_pattern: str, target_position: str) -> str:
        """Move a section to a different position"""
        section_match = re.search(section_pattern, text, re.IGNORECASE | re.DOTALL)
        if not section_match:
            return text

        section_text = section_match.group()
        text_without_section = text[:section_match.start()] + text[section_match.end():]

        if target_position == 'start':
            return section_text + '\n\n' + text_without_section
        elif target_position == 'end':
            return text_without_section + '\n\n' + section_text

        return text

    def _add_section_header(self, text: str, header: str, after_pattern: str) -> str:
        """Add a section header after a specific pattern"""
        match = re.search(after_pattern, text, re.IGNORECASE)
        if match:
            insertion_point = match.end()
            return text[:insertion_point] + f"\n\n## {header}\n\n" + text[insertion_point:]
        return text

    def _reorder_risk_warnings(self, text: str) -> str:
        """Move risk warnings to appear before benefit statements"""
        # Find risk warning section
        risk_pattern = r'((?:Risk|Warning|Important|Caution).*?(?:\n\n|\Z))'
        risk_match = re.search(risk_pattern, text, re.IGNORECASE | re.DOTALL)

        # Find benefit section
        benefit_pattern = r'((?:Benefit|Return|Profit|Advantage).*?(?:\n\n|\Z))'
        benefit_match = re.search(benefit_pattern, text, re.IGNORECASE | re.DOTALL)

        if risk_match and benefit_match and risk_match.start() > benefit_match.start():
            # Risk appears after benefits - reorder
            risk_text = risk_match.group()
            benefit_text = benefit_match.group()

            # Remove both sections
            text = text[:benefit_match.start()] + text[benefit_match.end():]
            risk_match = re.search(risk_pattern, text, re.IGNORECASE | re.DOTALL)
            if risk_match:
                text = text[:risk_match.start()] + text[risk_match.end():]

            # Insert in correct order: risk first, then benefits
            insertion_point = min(risk_match.start() if risk_match else 0, benefit_match.start())
            text = text[:insertion_point] + risk_text + '\n\n' + benefit_text + '\n\n' + text[insertion_point:]

        return text

    def apply(self, text: str, gate_id: str, gate_result: Dict, context: Dict) -> Optional[Dict]:
        """Apply structural reorganization"""
        corrected_text = text
        changes = []

        for gate_pattern, rules in self.reorganization_rules.items():
            if gate_pattern not in gate_id.lower():
                continue

            for rule in rules:
                rule_type = rule['type']
                config = rule['config']
                original_text = corrected_text

                if rule_type == 'move_section':
                    corrected_text = self._move_section(
                        corrected_text,
                        config['section_pattern'],
                        config['target_position']
                    )

                elif rule_type == 'add_section_header':
                    corrected_text = self._add_section_header(
                        corrected_text,
                        config['header'],
                        config['after_pattern']
                    )

                elif rule_type == 'reorder_risk_warnings':
                    corrected_text = self._reorder_risk_warnings(corrected_text)

                if corrected_text != original_text:
                    changes.append(rule_type)

        if changes:
            return {
                'text': corrected_text,
                'metadata': {
                    'strategy': self.strategy_type,
                    'changes': len(changes),
                    'locations': [],
                    'reason': f"Applied structural changes: {', '.join(changes)}",
                    'examples': changes
                }
            }

        return None


class SuggestionExtractionStrategy(CorrectionStrategy):
    """Strategy for extracting and applying suggestions from gate results"""

    def __init__(self):
        super().__init__("suggestion_extraction", priority=20)

    def can_apply(self, text: str, gate_id: str, gate_result: Dict) -> bool:
        """Check if gate has actionable suggestions"""
        suggestion = gate_result.get('suggestion', '')
        return bool(suggestion and ('Add:' in suggestion or 'Include:' in suggestion))

    def apply(self, text: str, gate_id: str, gate_result: Dict, context: Dict) -> Optional[Dict]:
        """Extract and apply suggestions from gate results"""
        suggestion = gate_result.get('suggestion', '')

        # Extract suggested text using various patterns
        patterns = [
            r'Add:\s*["\'](.+?)["\']',
            r'Add:\s*"([^"]+)"',
            r'Include:\s*["\'](.+?)["\']',
            r'Add:\s*([^.]+\.)(?:\s|$)'
        ]

        for pattern in patterns:
            match = re.search(pattern, suggestion, re.DOTALL)
            if match:
                suggested_text = match.group(1).strip()

                # Check if suggestion already exists in document
                if suggested_text.lower() in text.lower():
                    return None

                # Append to end of document with proper formatting
                corrected_text = text.rstrip() + '\n\n' + suggested_text

                return {
                    'text': corrected_text,
                    'metadata': {
                        'strategy': self.strategy_type,
                        'changes': 1,
                        'locations': [len(text)],
                        'reason': f'Applied suggestion from {gate_id}',
                        'examples': [suggested_text[:200] + '...' if len(suggested_text) > 200 else suggested_text]
                    }
                }

        return None
