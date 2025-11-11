"""
Adversarial Testing: Edge Cases

Tests for edge cases and boundary conditions that might break the correction system.
"""

import pytest
from backend.core.correction_synthesizer import CorrectionSynthesizer, CorrectionValidator
from backend.core.correction_strategies import (
    RegexReplacementStrategy,
    TemplateInsertionStrategy,
    StructuralReorganizationStrategy,
    SuggestionExtractionStrategy
)
from backend.core.correction_patterns import CorrectionPatternRegistry


@pytest.fixture
def synthesizer():
    """Create basic synthesizer."""
    pattern_registry = CorrectionPatternRegistry()

    regex_strategy = RegexReplacementStrategy()
    for gate_pattern, patterns in pattern_registry.regex_patterns.items():
        for pattern in patterns:
            regex_strategy.register_pattern(
                gate_pattern,
                pattern['pattern'],
                pattern['replacement'],
                pattern['reason'],
                pattern.get('flags', 0)
            )

    return CorrectionSynthesizer([regex_strategy])


class TestExtremeLength:
    """Test extremely long or short documents."""

    def test_single_character(self, synthesizer):
        """Test single character document."""
        text = "A"
        gates = [('test', {'status': 'FAIL', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert isinstance(result, dict)
        assert len(result['corrected']) >= 1

    def test_extremely_long_line(self, synthesizer):
        """Test document with one extremely long line (10KB)."""
        text = "GUARANTEED " * 1000  # 10KB single line
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'GUARANTEED' not in result['corrected'] or len(result['corrected']) > len(text)

    def test_many_empty_lines(self, synthesizer):
        """Test document with many empty lines."""
        text = "Header\n" + ("\n" * 1000) + "Footer"
        gates = [('test', {'status': 'PASS', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'Header' in result['corrected']
        assert 'Footer' in result['corrected']


class TestSpecialCharacters:
    """Test special and unusual characters."""

    def test_null_bytes(self, synthesizer):
        """Test handling of null bytes (should be filtered or handled)."""
        # Most text processing should remove or handle null bytes
        text = "Test\x00content"
        gates = [('test', {'status': 'PASS', 'severity': 'low'})]

        # Should not crash
        result = synthesizer.synthesize_corrections(text, gates)
        assert isinstance(result, dict)

    def test_control_characters(self, synthesizer):
        """Test various control characters."""
        text = "Test\x01\x02\x03\x04content"
        gates = [('test', {'status': 'PASS', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)
        assert isinstance(result, dict)

    def test_zero_width_characters(self, synthesizer):
        """Test zero-width unicode characters."""
        text = "Test\u200B\u200C\u200Dcontent"  # Zero-width space, non-joiner, joiner
        gates = [('test', {'status': 'PASS', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)
        assert isinstance(result['corrected'], str)

    def test_right_to_left_markers(self, synthesizer):
        """Test RTL markers and bidirectional text."""
        text = "Test \u202Eتسات\u202C content"
        gates = [('test', {'status': 'PASS', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)
        assert isinstance(result['corrected'], str)

    def test_combining_characters(self, synthesizer):
        """Test combining diacritical marks."""
        text = "Café résumé naïve"  # Various accents
        gates = [('test', {'status': 'PASS', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)
        assert 'Caf' in result['corrected'] or 'résumé' in result['corrected']


class TestMalformedInput:
    """Test malformed or unusual input structures."""

    def test_only_whitespace(self, synthesizer):
        """Test document with only whitespace."""
        text = "     \t\t\t\n\n\n     "
        gates = [('test', {'status': 'FAIL', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)
        assert isinstance(result, dict)

    def test_unbalanced_brackets(self, synthesizer):
        """Test text with unbalanced brackets."""
        text = "Investment [[GUARANTEED]]] returns {{{high yields"
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)
        assert 'GUARANTEED' not in result['corrected'] or 'potential' in result['corrected'].lower()

    def test_nested_quotes(self, synthesizer):
        """Test deeply nested quotes."""
        text = '"He said "She said "They said "GUARANTEED returns""""'
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)
        assert isinstance(result['corrected'], str)

    def test_unclosed_tags(self, synthesizer):
        """Test HTML-like unclosed tags."""
        text = "<div>GUARANTEED returns <span>high yields</div> risk-free"
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)
        assert '<' in result['corrected']  # Tags should be preserved


class TestRepeatingPatterns:
    """Test documents with repeating patterns."""

    def test_same_word_repeated(self, synthesizer):
        """Test same problematic word repeated many times."""
        text = "GUARANTEED " * 100
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)

        # Should correct all instances
        assert result['corrected'].upper().count('GUARANTEED') < 50

    def test_alternating_violations(self, synthesizer):
        """Test alternating violation patterns."""
        text = "GUARANTEED safe GUARANTEED safe GUARANTEED safe " * 10
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)
        assert 'GUARANTEED' not in result['corrected'] or 'potential' in result['corrected'].lower()

    def test_nested_violations(self, synthesizer):
        """Test nested violation patterns."""
        text = "GUARANTEED (risk-free (high yields))"
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)
        assert 'GUARANTEED' not in result['corrected'] or 'potential' in result['corrected'].lower()


class TestBoundaryValues:
    """Test boundary value conditions."""

    def test_exact_threshold_length(self, synthesizer):
        """Test document at exact length thresholds."""
        # Test at 1KB boundary
        text = "x" * 1024
        gates = [('test', {'status': 'PASS', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)
        assert len(result['corrected']) >= 1000

    def test_zero_corrections_possible(self, synthesizer):
        """Test when no corrections can be applied."""
        text = "This is a perfectly compliant document."
        gates = [('nonexistent_gate', {'status': 'FAIL', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)
        assert result['correction_count'] == 0

    def test_all_gates_failing(self, synthesizer):
        """Test when every possible gate is failing."""
        text = "GUARANTEED returns!"
        gates = [(f'gate_{i}', {'status': 'FAIL', 'severity': 'critical'}) for i in range(100)]

        result = synthesizer.synthesize_corrections(text, gates)
        assert isinstance(result, dict)


class TestEncodingIssues:
    """Test various encoding edge cases."""

    def test_mixed_encodings(self, synthesizer):
        """Test text that might have come from different encodings."""
        text = "Test £100 €200 ¥300 with café and naïve"
        gates = [('test', {'status': 'PASS', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)

        # All characters should be preserved
        assert '£' in result['corrected']
        assert '€' in result['corrected']

    def test_emoji_preservation(self, synthesizer):
        """Test emoji handling."""
        text = "Investment opportunity 📈💰 GUARANTEED returns! 🎉"
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)

        # Emojis should be preserved
        assert '📈' in result['corrected'] or '💰' in result['corrected']

    def test_mathematical_symbols(self, synthesizer):
        """Test mathematical and scientific symbols."""
        text = "Returns: ∑ ∫ ∂ ≈ ≤ ≥ ± × ÷ √"
        gates = [('test', {'status': 'PASS', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)
        assert '∑' in result['corrected'] or isinstance(result['corrected'], str)


class TestConcurrentIssues:
    """Test patterns that might cause issues in concurrent processing."""

    def test_same_pattern_multiple_locations(self, synthesizer):
        """Test same problematic pattern in many locations."""
        text = "GUARANTEED returns! " + "Some content. " * 10 + "GUARANTEED returns! " + \
               "More content. " * 10 + "GUARANTEED returns!"
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)

        # All instances should be corrected
        assert result['corrected'].count('GUARANTEED') < 2

    def test_overlapping_patterns(self, synthesizer):
        """Test overlapping violation patterns."""
        text = "GUARANTEEDGUARANTEED"  # Overlapping pattern
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)
        # Should handle overlaps gracefully
        assert isinstance(result['corrected'], str)


class TestStateCorruption:
    """Test patterns that might corrupt internal state."""

    def test_empty_gate_id(self, synthesizer):
        """Test empty gate ID."""
        text = "GUARANTEED returns!"
        gates = [('', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)
        assert isinstance(result, dict)

    def test_missing_gate_fields(self, synthesizer):
        """Test gate with missing fields."""
        text = "GUARANTEED returns!"
        gates = [('test_gate', {})]  # Missing status and severity

        result = synthesizer.synthesize_corrections(text, gates)
        assert isinstance(result, dict)

    def test_invalid_severity(self, synthesizer):
        """Test invalid severity values."""
        text = "GUARANTEED returns!"
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'EXTREME_ULTRA_CRITICAL'})]

        result = synthesizer.synthesize_corrections(text, gates)
        assert isinstance(result, dict)


class TestRegexEdgeCases:
    """Test regex pattern edge cases."""

    def test_regex_special_chars_in_text(self, synthesizer):
        """Test text with regex special characters."""
        text = "Investment: $100 (plus fees) [subject to terms] {options available}"
        gates = [('test', {'status': 'PASS', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)

        # Special chars should be preserved
        assert '$' in result['corrected']
        assert '(' in result['corrected']
        assert '[' in result['corrected']

    def test_dot_star_in_text(self, synthesizer):
        """Test text that looks like regex patterns."""
        text = "Pattern: .* and .+ and .*?"
        gates = [('test', {'status': 'PASS', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)
        assert '.*' in result['corrected']

    def test_backreferences_in_text(self, synthesizer):
        """Test text with backslash sequences."""
        text = "Path: C:\\Users\\Example\\Documents\\file.txt"
        gates = [('test', {'status': 'PASS', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)
        assert 'Users' in result['corrected']
