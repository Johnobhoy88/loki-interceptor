"""
Plugin Loader - Custom correction rules via plugin system

Allows users to define and load custom correction rules:
- Custom regex patterns
- Custom templates
- Custom validation logic
- Domain-specific corrections
"""
from __future__ import annotations

import os
import re
import json
import importlib.util
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CustomRule:
    """Represents a custom correction rule"""
    rule_id: str
    rule_type: str  # 'regex', 'template', 'function', 'composite'
    name: str
    description: str
    gate_pattern: str  # Pattern to match against gate IDs
    priority: int = 50  # Execution priority (higher = earlier)
    enabled: bool = True
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class RegexRule(CustomRule):
    """Custom regex-based correction rule"""
    pattern: str
    replacement: str
    flags: int = 0
    reason: str = ""


@dataclass
class TemplateRule(CustomRule):
    """Custom template insertion rule"""
    template: str
    position: str  # 'start', 'end', 'after_header', 'before_signature'
    condition: Optional[str] = None  # Optional regex condition


@dataclass
class FunctionRule(CustomRule):
    """Custom function-based correction rule"""
    function: Callable
    parameters: Dict[str, Any] = None

    def __post_init__(self):
        super().__post_init__()
        if self.parameters is None:
            self.parameters = {}


class PluginLoader:
    """
    Loads and manages custom correction rule plugins
    """

    def __init__(self, plugin_directories: Optional[List[str]] = None):
        """
        Initialize plugin loader

        Args:
            plugin_directories: List of directories to search for plugins
        """
        self.plugin_directories = plugin_directories or [
            './plugins/corrections',
            './backend/plugins/corrections',
            os.path.expanduser('~/.loki/plugins')
        ]

        self.loaded_rules: Dict[str, CustomRule] = {}
        self.regex_rules: List[RegexRule] = []
        self.template_rules: List[TemplateRule] = []
        self.function_rules: List[FunctionRule] = []

        self.rule_statistics: Dict[str, Dict[str, int]] = {}

    def load_plugins(self) -> Dict[str, Any]:
        """
        Load all plugins from configured directories

        Returns:
            Dictionary with loading results
        """
        results = {
            'loaded': 0,
            'failed': 0,
            'errors': [],
            'rules_by_type': {}
        }

        for directory in self.plugin_directories:
            if not os.path.exists(directory):
                continue

            # Load JSON rule files
            for file_path in Path(directory).glob('*.json'):
                try:
                    self._load_json_plugin(str(file_path))
                    results['loaded'] += 1
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append(f"Failed to load {file_path}: {str(e)}")

            # Load Python plugin modules
            for file_path in Path(directory).glob('*.py'):
                if file_path.stem.startswith('_'):
                    continue  # Skip private modules

                try:
                    self._load_python_plugin(str(file_path))
                    results['loaded'] += 1
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append(f"Failed to load {file_path}: {str(e)}")

        # Categorize rules
        results['rules_by_type'] = {
            'regex': len(self.regex_rules),
            'template': len(self.template_rules),
            'function': len(self.function_rules)
        }

        return results

    def _load_json_plugin(self, file_path: str):
        """Load correction rules from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Support both single rule and array of rules
        rules = data if isinstance(data, list) else [data]

        for rule_data in rules:
            rule_type = rule_data.get('rule_type', 'regex')
            rule_id = rule_data.get('rule_id', f"custom_{len(self.loaded_rules)}")

            if rule_type == 'regex':
                rule = RegexRule(
                    rule_id=rule_id,
                    rule_type='regex',
                    name=rule_data.get('name', ''),
                    description=rule_data.get('description', ''),
                    gate_pattern=rule_data.get('gate_pattern', ''),
                    priority=rule_data.get('priority', 50),
                    enabled=rule_data.get('enabled', True),
                    pattern=rule_data['pattern'],
                    replacement=rule_data['replacement'],
                    flags=self._parse_regex_flags(rule_data.get('flags', 'IGNORECASE')),
                    reason=rule_data.get('reason', '')
                )
                self.regex_rules.append(rule)
                self.loaded_rules[rule_id] = rule

            elif rule_type == 'template':
                rule = TemplateRule(
                    rule_id=rule_id,
                    rule_type='template',
                    name=rule_data.get('name', ''),
                    description=rule_data.get('description', ''),
                    gate_pattern=rule_data.get('gate_pattern', ''),
                    priority=rule_data.get('priority', 50),
                    enabled=rule_data.get('enabled', True),
                    template=rule_data['template'],
                    position=rule_data.get('position', 'end'),
                    condition=rule_data.get('condition')
                )
                self.template_rules.append(rule)
                self.loaded_rules[rule_id] = rule

    def _load_python_plugin(self, file_path: str):
        """Load correction rules from Python module"""
        # Import the module
        spec = importlib.util.spec_from_file_location("custom_plugin", file_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Look for rules defined in module
            if hasattr(module, 'CORRECTION_RULES'):
                rules = module.CORRECTION_RULES
                if isinstance(rules, list):
                    for rule_data in rules:
                        self._register_rule_from_dict(rule_data)

            # Look for correction functions
            if hasattr(module, 'register_rules'):
                custom_rules = module.register_rules()
                if isinstance(custom_rules, list):
                    for rule in custom_rules:
                        if isinstance(rule, CustomRule):
                            self._register_custom_rule(rule)

    def _register_rule_from_dict(self, rule_data: Dict[str, Any]):
        """Register a rule from dictionary specification"""
        rule_type = rule_data.get('rule_type', 'regex')
        rule_id = rule_data.get('rule_id', f"custom_{len(self.loaded_rules)}")

        if rule_type == 'regex':
            rule = RegexRule(
                rule_id=rule_id,
                rule_type='regex',
                name=rule_data.get('name', ''),
                description=rule_data.get('description', ''),
                gate_pattern=rule_data.get('gate_pattern', ''),
                priority=rule_data.get('priority', 50),
                pattern=rule_data['pattern'],
                replacement=rule_data['replacement'],
                flags=rule_data.get('flags', 0),
                reason=rule_data.get('reason', '')
            )
            self.regex_rules.append(rule)
            self.loaded_rules[rule_id] = rule

        elif rule_type == 'function' and 'function' in rule_data:
            rule = FunctionRule(
                rule_id=rule_id,
                rule_type='function',
                name=rule_data.get('name', ''),
                description=rule_data.get('description', ''),
                gate_pattern=rule_data.get('gate_pattern', ''),
                priority=rule_data.get('priority', 50),
                function=rule_data['function'],
                parameters=rule_data.get('parameters', {})
            )
            self.function_rules.append(rule)
            self.loaded_rules[rule_id] = rule

    def _register_custom_rule(self, rule: CustomRule):
        """Register a custom rule object"""
        self.loaded_rules[rule.rule_id] = rule

        if isinstance(rule, RegexRule):
            self.regex_rules.append(rule)
        elif isinstance(rule, TemplateRule):
            self.template_rules.append(rule)
        elif isinstance(rule, FunctionRule):
            self.function_rules.append(rule)

    def _parse_regex_flags(self, flags_str: str) -> int:
        """Parse regex flags from string"""
        flag_map = {
            'IGNORECASE': re.IGNORECASE,
            'MULTILINE': re.MULTILINE,
            'DOTALL': re.DOTALL,
            'UNICODE': re.UNICODE,
            'VERBOSE': re.VERBOSE
        }

        if isinstance(flags_str, int):
            return flags_str

        flags = 0
        for flag_name in flags_str.split('|'):
            flag_name = flag_name.strip()
            if flag_name in flag_map:
                flags |= flag_map[flag_name]

        return flags

    def get_rules_for_gate(
        self,
        gate_id: str,
        rule_type: Optional[str] = None
    ) -> List[CustomRule]:
        """
        Get all rules applicable to a specific gate

        Args:
            gate_id: Gate identifier
            rule_type: Optional filter by rule type

        Returns:
            List of applicable rules
        """
        applicable_rules = []

        for rule in self.loaded_rules.values():
            if not rule.enabled:
                continue

            # Check if gate pattern matches
            if rule.gate_pattern:
                if re.search(rule.gate_pattern, gate_id, re.IGNORECASE):
                    if rule_type is None or rule.rule_type == rule_type:
                        applicable_rules.append(rule)

        # Sort by priority (higher priority first)
        applicable_rules.sort(key=lambda r: r.priority, reverse=True)

        return applicable_rules

    def apply_regex_rules(
        self,
        text: str,
        gate_id: str
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Apply all applicable regex rules to text

        Args:
            text: Text to correct
            gate_id: Gate identifier

        Returns:
            Tuple of (corrected_text, changes_made)
        """
        corrected_text = text
        changes = []

        rules = self.get_rules_for_gate(gate_id, 'regex')

        for rule in rules:
            if not isinstance(rule, RegexRule):
                continue

            matches = re.findall(rule.pattern, corrected_text, rule.flags)
            if matches:
                corrected_text = re.sub(
                    rule.pattern,
                    rule.replacement,
                    corrected_text,
                    flags=rule.flags
                )

                changes.append({
                    'rule_id': rule.rule_id,
                    'rule_name': rule.name,
                    'matches': len(matches),
                    'pattern': rule.pattern,
                    'reason': rule.reason
                })

                # Track statistics
                self._record_rule_application(rule.rule_id, True)

        return corrected_text, changes

    def apply_template_rules(
        self,
        text: str,
        gate_id: str
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Apply all applicable template rules to text

        Args:
            text: Text to modify
            gate_id: Gate identifier

        Returns:
            Tuple of (modified_text, insertions_made)
        """
        modified_text = text
        insertions = []

        rules = self.get_rules_for_gate(gate_id, 'template')

        for rule in rules:
            if not isinstance(rule, TemplateRule):
                continue

            # Check condition if specified
            if rule.condition and not re.search(rule.condition, text, re.IGNORECASE):
                continue

            # Check if template already exists
            if rule.template.strip() in modified_text:
                continue

            # Insert template
            if rule.position == 'start':
                modified_text = rule.template + '\n\n' + modified_text
            elif rule.position == 'end':
                modified_text = modified_text + '\n\n' + rule.template
            elif rule.position == 'after_header':
                # Find first paragraph break
                match = re.search(r'\n\n', modified_text)
                if match:
                    insert_pos = match.end()
                    modified_text = (
                        modified_text[:insert_pos] +
                        rule.template + '\n\n' +
                        modified_text[insert_pos:]
                    )
            elif rule.position == 'before_signature':
                # Find signature
                sig_match = re.search(r'(?:Signed|Signature|Date:)', modified_text, re.IGNORECASE)
                if sig_match:
                    insert_pos = sig_match.start()
                    modified_text = (
                        modified_text[:insert_pos] +
                        rule.template + '\n\n' +
                        modified_text[insert_pos:]
                    )

            insertions.append({
                'rule_id': rule.rule_id,
                'rule_name': rule.name,
                'position': rule.position,
                'template_length': len(rule.template)
            })

            self._record_rule_application(rule.rule_id, True)

        return modified_text, insertions

    def apply_function_rules(
        self,
        text: str,
        gate_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Apply all applicable function-based rules

        Args:
            text: Text to process
            gate_id: Gate identifier
            context: Additional context for functions

        Returns:
            Tuple of (processed_text, results)
        """
        processed_text = text
        results = []
        context = context or {}

        rules = self.get_rules_for_gate(gate_id, 'function')

        for rule in rules:
            if not isinstance(rule, FunctionRule):
                continue

            try:
                # Call the custom function
                result = rule.function(
                    text=processed_text,
                    gate_id=gate_id,
                    context=context,
                    **rule.parameters
                )

                if result and isinstance(result, dict):
                    if 'text' in result:
                        processed_text = result['text']

                    results.append({
                        'rule_id': rule.rule_id,
                        'rule_name': rule.name,
                        'result': result
                    })

                    self._record_rule_application(rule.rule_id, True)

            except Exception as e:
                results.append({
                    'rule_id': rule.rule_id,
                    'rule_name': rule.name,
                    'error': str(e)
                })
                self._record_rule_application(rule.rule_id, False)

        return processed_text, results

    def _record_rule_application(self, rule_id: str, success: bool):
        """Record statistics about rule application"""
        if rule_id not in self.rule_statistics:
            self.rule_statistics[rule_id] = {
                'applications': 0,
                'successes': 0,
                'failures': 0
            }

        self.rule_statistics[rule_id]['applications'] += 1
        if success:
            self.rule_statistics[rule_id]['successes'] += 1
        else:
            self.rule_statistics[rule_id]['failures'] += 1

    def get_plugin_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about loaded plugins and their usage

        Returns:
            Dictionary with plugin statistics
        """
        return {
            'total_rules': len(self.loaded_rules),
            'regex_rules': len(self.regex_rules),
            'template_rules': len(self.template_rules),
            'function_rules': len(self.function_rules),
            'enabled_rules': sum(1 for r in self.loaded_rules.values() if r.enabled),
            'disabled_rules': sum(1 for r in self.loaded_rules.values() if not r.enabled),
            'rule_statistics': self.rule_statistics.copy()
        }

    def enable_rule(self, rule_id: str) -> bool:
        """Enable a specific rule"""
        if rule_id in self.loaded_rules:
            self.loaded_rules[rule_id].enabled = True
            return True
        return False

    def disable_rule(self, rule_id: str) -> bool:
        """Disable a specific rule"""
        if rule_id in self.loaded_rules:
            self.loaded_rules[rule_id].enabled = False
            return True
        return False

    def reload_plugins(self) -> Dict[str, Any]:
        """
        Reload all plugins from directories

        Returns:
            Dictionary with reload results
        """
        # Clear existing rules
        self.loaded_rules.clear()
        self.regex_rules.clear()
        self.template_rules.clear()
        self.function_rules.clear()

        # Reload
        return self.load_plugins()
