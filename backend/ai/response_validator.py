"""
Response Validation and Quality Checking Module

Provides comprehensive validation of AI responses including:
- Format validation
- Content quality checks
- Safety validation
- Completeness verification
- Consistency checking
"""

import re
import json
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class ValidationLevel(str, Enum):
    """Validation strictness level"""
    STRICT = "strict"  # All checks must pass
    MODERATE = "moderate"  # Most checks must pass
    LENIENT = "lenient"  # Core checks must pass


class RuleType(str, Enum):
    """Types of validation rules"""
    FORMAT = "format"  # Response structure validation
    CONTENT = "content"  # Content quality validation
    SAFETY = "safety"  # Safety checks
    COMPLETENESS = "completeness"  # Checks if response is complete
    CONSISTENCY = "consistency"  # Internal consistency checks
    CUSTOM = "custom"  # Custom validation logic


@dataclass
class ValidationRule:
    """A validation rule for response checking"""
    name: str
    rule_type: RuleType
    validator: Callable[[str], bool]  # Function that returns True if valid
    error_message: str
    severity: str = "error"  # "error" or "warning"
    enabled: bool = True


@dataclass
class ValidationResult:
    """Result of validation check"""
    is_valid: bool
    score: float  # 0-1, validation score
    passed_rules: List[str]
    failed_rules: List[str]
    errors: List[Dict[str, str]]
    warnings: List[Dict[str, str]]
    suggestions: List[str]
    validation_time_ms: float
    timestamp: str


class ResponseValidator:
    """
    Validates and scores AI responses for quality

    Features:
    - Multiple validation strategies
    - Custom rule support
    - Quality scoring
    - Suggestion generation
    """

    def __init__(self, level: ValidationLevel = ValidationLevel.MODERATE):
        self.level = level
        self.rules: Dict[str, ValidationRule] = {}
        self.validation_history: List[ValidationResult] = []
        self._setup_default_rules()

    def _setup_default_rules(self):
        """Setup default validation rules"""
        # Format rules
        self.add_rule(ValidationRule(
            name="not_empty",
            rule_type=RuleType.FORMAT,
            validator=lambda r: len(r.strip()) > 0,
            error_message="Response is empty"
        ))

        self.add_rule(ValidationRule(
            name="reasonable_length",
            rule_type=RuleType.FORMAT,
            validator=lambda r: 10 < len(r) < 100000,
            error_message="Response length out of reasonable bounds",
            severity="warning"
        ))

        # Content rules
        self.add_rule(ValidationRule(
            name="contains_actionable_content",
            rule_type=RuleType.CONTENT,
            validator=self._has_actionable_content,
            error_message="Response lacks actionable content",
            severity="warning"
        ))

        self.add_rule(ValidationRule(
            name="professional_tone",
            rule_type=RuleType.CONTENT,
            validator=self._check_professional_tone,
            error_message="Response lacks professional tone",
            severity="warning"
        ))

        # Safety rules
        self.add_rule(ValidationRule(
            name="no_harmful_content",
            rule_type=RuleType.SAFETY,
            validator=self._check_safety,
            error_message="Response contains potentially harmful content"
        ))

        self.add_rule(ValidationRule(
            name="no_personal_data",
            rule_type=RuleType.SAFETY,
            validator=self._check_no_pii,
            error_message="Response contains potential PII"
        ))

        # Completeness rules
        self.add_rule(ValidationRule(
            name="has_clear_conclusion",
            rule_type=RuleType.COMPLETENESS,
            validator=self._has_conclusion,
            error_message="Response lacks clear conclusion",
            severity="warning"
        ))

        # Consistency rules
        self.add_rule(ValidationRule(
            name="no_contradictions",
            rule_type=RuleType.CONSISTENCY,
            validator=self._check_consistency,
            error_message="Response contains internal contradictions",
            severity="warning"
        ))

    def add_rule(self, rule: ValidationRule):
        """Add a validation rule"""
        self.rules[rule.name] = rule

    def remove_rule(self, rule_name: str):
        """Remove a validation rule"""
        if rule_name in self.rules:
            del self.rules[rule_name]

    def validate(self, response: str, custom_rules: Optional[List[ValidationRule]] = None) -> ValidationResult:
        """
        Validate an AI response

        Args:
            response: The response to validate
            custom_rules: Additional custom rules to apply

        Returns:
            ValidationResult with detailed validation information
        """
        import time
        start_time = time.time()

        passed_rules = []
        failed_rules = []
        errors = []
        warnings = []
        suggestions = []

        all_rules = list(self.rules.values())
        if custom_rules:
            all_rules.extend(custom_rules)

        # Apply all enabled rules
        for rule in all_rules:
            if not rule.enabled:
                continue

            try:
                if rule.validator(response):
                    passed_rules.append(rule.name)
                else:
                    failed_rules.append(rule.name)

                    issue = {
                        "rule": rule.name,
                        "message": rule.error_message,
                        "type": rule.rule_type.value
                    }

                    if rule.severity == "error":
                        errors.append(issue)
                    else:
                        warnings.append(issue)

                    suggestions.extend(self._get_suggestions_for_rule(rule, response))

            except Exception as e:
                warnings.append({
                    "rule": rule.name,
                    "message": f"Rule validation failed: {str(e)}"
                })

        # Calculate validation score
        passed = len(passed_rules)
        total = len(passed_rules) + len(failed_rules)
        score = passed / total if total > 0 else 0.0

        # Determine if valid based on level
        is_valid = self._is_valid_for_level(len(errors), len(warnings), self.level)

        validation_time_ms = (time.time() - start_time) * 1000

        result = ValidationResult(
            is_valid=is_valid,
            score=score,
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            validation_time_ms=validation_time_ms,
            timestamp=datetime.utcnow().isoformat()
        )

        self.validation_history.append(result)
        return result

    def _has_actionable_content(self, response: str) -> bool:
        """Check if response has actionable content"""
        action_words = ['do', 'use', 'implement', 'apply', 'follow', 'execute', 'perform', 'enable', 'disable']
        response_lower = response.lower()
        return any(word in response_lower for word in action_words)

    def _check_professional_tone(self, response: str) -> bool:
        """Check for professional tone"""
        # Should not have excessive exclamation marks or emojis
        exclamation_ratio = response.count('!') / max(1, len(response.split()))
        emoji_count = len(re.findall(r'[^\w\s\p{P}]', response, re.UNICODE))

        return exclamation_ratio < 0.1 and emoji_count < 3

    def _check_safety(self, response: str) -> bool:
        """Check for harmful content"""
        harmful_patterns = [
            r'\b(kill|harm|destroy|attack)\b',
            r'illegal\s+(activity|operation)',
            r'hack|malware|virus'
        ]

        response_lower = response.lower()
        for pattern in harmful_patterns:
            if re.search(pattern, response_lower):
                return False

        return True

    def _check_no_pii(self, response: str) -> bool:
        """Check for potential PII (simplified)"""
        # Simple patterns for common PII
        patterns = [
            r'\d{3}-\d{2}-\d{4}',  # SSN
            r'\b\d{16}\b',  # Credit card
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # Email
        ]

        # This is basic - in production use proper PII detection library
        return not any(re.search(p, response) for p in patterns)

    def _has_conclusion(self, response: str) -> bool:
        """Check if response has a clear conclusion"""
        conclusion_markers = [
            'conclusion', 'summary', 'in conclusion', 'therefore',
            'to summarize', 'ultimately', 'finally', 'in summary'
        ]

        response_lower = response.lower()
        return any(marker in response_lower for marker in conclusion_markers)

    def _check_consistency(self, response: str) -> bool:
        """Check for internal contradictions (simplified)"""
        # Check for common contradiction patterns
        contradictions = [
            (r'yes.*no', r'no.*yes'),
            (r'true.*false', r'false.*true'),
            (r'should.*must not', r'must not.*should'),
        ]

        response_lower = response.lower()

        for pattern1, pattern2 in contradictions:
            if re.search(pattern1, response_lower) and re.search(pattern2, response_lower):
                return False

        return True

    def _get_suggestions_for_rule(self, rule: ValidationRule, response: str) -> List[str]:
        """Generate suggestions for fixing validation failures"""
        suggestions = []

        if rule.name == "not_empty":
            suggestions.append("Provide a complete response")

        elif rule.name == "reasonable_length":
            if len(response) < 10:
                suggestions.append("Expand your response with more details")
            else:
                suggestions.append("Consider breaking response into sections")

        elif rule.name == "contains_actionable_content":
            suggestions.append("Add specific actions or recommendations")

        elif rule.name == "professional_tone":
            suggestions.append("Use formal language and remove excessive punctuation")

        elif rule.name == "has_clear_conclusion":
            suggestions.append("Add a clear conclusion or summary statement")

        return suggestions

    def _is_valid_for_level(self, error_count: int, warning_count: int, level: ValidationLevel) -> bool:
        """Determine if response is valid based on validation level"""
        if level == ValidationLevel.STRICT:
            return error_count == 0 and warning_count == 0

        elif level == ValidationLevel.MODERATE:
            return error_count == 0

        else:  # LENIENT
            return error_count <= 1

    def get_statistics(self) -> Dict:
        """Get validation statistics"""
        if not self.validation_history:
            return {}

        avg_score = sum(r.score for r in self.validation_history) / len(self.validation_history)
        valid_count = sum(1 for r in self.validation_history if r.is_valid)
        total_errors = sum(len(r.errors) for r in self.validation_history)
        total_warnings = sum(len(r.warnings) for r in self.validation_history)

        return {
            "total_validations": len(self.validation_history),
            "average_score": avg_score,
            "valid_count": valid_count,
            "invalid_count": len(self.validation_history) - valid_count,
            "validity_rate": valid_count / len(self.validation_history),
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "average_validation_time_ms": sum(r.validation_time_ms for r in self.validation_history) / len(self.validation_history)
        }
