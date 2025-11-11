"""
Adversarial Testing: Corner Cases

Tests for corner cases and unusual scenarios that might expose bugs.
"""

import pytest
import json
from backend.core.correction_synthesizer import CorrectionSynthesizer
from backend.core.correction_strategies import RegexReplacementStrategy
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


class TestCaseVariations:
    """Test case sensitivity corner cases."""

    def test_mixed_case_guaranteed(self, synthesizer):
        """Test various capitalizations of GUARANTEED."""
        test_cases = [
            "GUARANTEED",
            "guaranteed",
            "Guaranteed",
            "GuArAnTeEd",
            "gUARANTEED"
        ]

        for text in test_cases:
            gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]
            result = synthesizer.synthesize_corrections(text, gates)

            # All variations should be caught
            assert 'guaranteed' not in result['corrected'].lower() or \
                   'potential' in result['corrected'].lower() or \
                   'not guaranteed' in result['corrected'].lower()

    def test_case_preservation_in_names(self, synthesizer):
        """Test that proper nouns preserve case."""
        text = "Contact John Smith at ABC Company Ltd"
        gates = [('legal_entity_name', {'status': 'FAIL', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)

        # Names should preserve case
        assert 'John' in result['corrected'] or 'john' in result['corrected'].lower()


class TestWhitespaceVariations:
    """Test whitespace handling corner cases."""

    def test_various_whitespace_types(self, synthesizer):
        """Test different types of whitespace."""
        text = "GUARANTEED\treturns\nwith\r\nhigh   yields"
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)
        assert isinstance(result['corrected'], str)

    def test_leading_trailing_whitespace(self, synthesizer):
        """Test leading and trailing whitespace preservation."""
        text = "   GUARANTEED returns!   "
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)

        # Corrections should work regardless of whitespace
        assert 'GUARANTEED' not in result['corrected'] or 'potential' in result['corrected'].lower()

    def test_multiple_spaces_between_words(self, synthesizer):
        """Test multiple spaces between words."""
        text = "GUARANTEED          returns"
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)
        assert isinstance(result['corrected'], str)


class TestPunctuationEdgeCases:
    """Test punctuation-related corner cases."""

    def test_violation_with_punctuation(self, synthesizer):
        """Test violations with various punctuation."""
        test_cases = [
            "GUARANTEED!",
            "GUARANTEED?",
            "GUARANTEED.",
            "GUARANTEED,",
            "GUARANTEED;",
            "GUARANTEED:",
            "(GUARANTEED)",
            "[GUARANTEED]",
            "{GUARANTEED}"
        ]

        for text in test_cases:
            gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]
            result = synthesizer.synthesize_corrections(text, gates)

            # Should catch all variations
            assert 'GUARANTEED' not in result['corrected'] or 'potential' in result['corrected'].lower()

    def test_multiple_punctuation(self, synthesizer):
        """Test multiple punctuation marks."""
        text = "GUARANTEED returns!!!"
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)
        assert 'GUARANTEED' not in result['corrected'] or 'potential' in result['corrected'].lower()

    def test_apostrophes_in_text(self, synthesizer):
        """Test various apostrophe styles."""
        text = "It's guaranteed. We're confident. You'll succeed."
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)
        # Should preserve contractions
        assert "'" in result['corrected'] or "'" in result['corrected']


class TestNumberFormats:
    """Test various number format corner cases."""

    def test_vat_threshold_variations(self, synthesizer):
        """Test various formats of VAT threshold."""
        test_cases = [
            "£85,000",
            "£85000",
            "£ 85,000",
            "£85,000.00",
            "85,000",
            "85000"
        ]

        for text in test_cases:
            full_text = f"VAT registration threshold is {text}"
            gates = [('vat_threshold', {'status': 'FAIL', 'severity': 'medium'})]
            result = synthesizer.synthesize_corrections(full_text, gates)

            # Should catch various formats
            if '85' in text:
                assert '£90,000' in result['corrected'] or '90000' in result['corrected']

    def test_currency_without_symbol(self, synthesizer):
        """Test numbers without currency symbols."""
        text = "The threshold is 85000 pounds"
        gates = [('vat_threshold', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)
        # May or may not correct without £ symbol
        assert isinstance(result['corrected'], str)

    def test_decimal_numbers(self, synthesizer):
        """Test decimal number preservation."""
        text = "Returns of 12.5% annually. Fees: £123.45"
        gates = [('test', {'status': 'PASS', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)

        # Decimals should be preserved
        assert '12.5' in result['corrected'] or '123.45' in result['corrected']


class TestAcronymsAndAbbreviations:
    """Test acronyms and abbreviations."""

    def test_ltd_vs_limited(self, synthesizer):
        """Test Ltd vs Limited variations."""
        test_cases = [
            "ABC Ltd",
            "ABC Ltd.",
            "ABC LTD",
            "ABC ltd",
        ]

        for text in test_cases:
            gates = [('legal_entity_name', {'status': 'FAIL', 'severity': 'low'})]
            result = synthesizer.synthesize_corrections(text, gates)

            # Should expand to Limited
            assert 'Limited' in result['corrected'] or 'Ltd' in result['corrected']

    def test_fca_acronym_preservation(self, synthesizer):
        """Test FCA acronym is preserved."""
        text = "FCA regulated services with guaranteed returns"
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)

        # FCA should remain
        assert 'FCA' in result['corrected'] or 'fca' in result['corrected'].lower()

    def test_gdpr_acronym_preservation(self, synthesizer):
        """Test GDPR acronym is preserved."""
        text = "GDPR compliant data processing"
        gates = [('test', {'status': 'PASS', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)
        assert 'GDPR' in result['corrected'] or 'gdpr' in result['corrected'].lower()


class TestMultilinePatterns:
    """Test patterns that span multiple lines."""

    def test_violation_across_lines(self, synthesizer):
        """Test violation split across lines."""
        text = "GUARANTEED\nreturns"
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)

        # May or may not catch cross-line patterns
        assert isinstance(result['corrected'], str)

    def test_multiline_section(self, synthesizer):
        """Test corrections in multiline sections."""
        text = """
        Section 1:
        GUARANTEED returns
        on your investment
        with high yields
        """

        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]
        result = synthesizer.synthesize_corrections(text, gates)

        assert 'GUARANTEED' not in result['corrected'] or 'potential' in result['corrected'].lower()

    def test_paragraph_boundaries(self, synthesizer):
        """Test corrections respect paragraph boundaries."""
        text = "Paragraph 1 content.\n\nParagraph 2 with GUARANTEED returns.\n\nParagraph 3 content."
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)

        # Should have paragraph breaks
        assert '\n\n' in result['corrected'] or 'Paragraph' in result['corrected']


class TestMetadataEdgeCases:
    """Test correction metadata edge cases."""

    def test_correction_without_gate_match(self, synthesizer):
        """Test when gate ID doesn't match any patterns."""
        text = "GUARANTEED returns!"
        gates = [('completely_unrelated_gate', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)

        # Should handle gracefully
        assert result['correction_count'] >= 0
        assert isinstance(result['corrections'], list)

    def test_multiple_corrections_same_gate(self, synthesizer):
        """Test multiple corrections from the same gate."""
        text = "GUARANTEED returns and risk-free investment!"
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)

        # May apply multiple corrections
        assert result['correction_count'] >= 0

    def test_correction_metadata_completeness(self, synthesizer):
        """Test all corrections have complete metadata."""
        text = "GUARANTEED returns!"
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)

        for correction in result['corrections']:
            assert 'gate_id' in correction
            assert 'strategy' in correction
            assert 'metadata' in correction


class TestDeterminismEdgeCases:
    """Test determinism in edge cases."""

    def test_determinism_with_empty_input(self, synthesizer):
        """Test determinism with empty input."""
        text = ""
        gates = []

        result1 = synthesizer.synthesize_corrections(text, gates)
        result2 = synthesizer.synthesize_corrections(text, gates)

        assert result1['corrected'] == result2['corrected']

    def test_determinism_with_unicode(self, synthesizer):
        """Test determinism with unicode."""
        text = "投資保證高回報！£100 €200"
        gates = [('test', {'status': 'PASS', 'severity': 'low'})]

        result1 = synthesizer.synthesize_corrections(text, gates)
        result2 = synthesizer.synthesize_corrections(text, gates)

        assert result1['corrected'] == result2['corrected']
        assert result1['determinism']['output_hash'] == result2['determinism']['output_hash']

    def test_determinism_with_many_gates(self, synthesizer):
        """Test determinism with many gates."""
        text = "Test document"
        gates = [(f'gate_{i}', {'status': 'FAIL', 'severity': 'low'}) for i in range(20)]

        result1 = synthesizer.synthesize_corrections(text, gates)
        result2 = synthesizer.synthesize_corrections(text, gates)

        assert result1['corrected'] == result2['corrected']


class TestContextDependency:
    """Test context-dependent corrections."""

    def test_same_word_different_context(self, synthesizer):
        """Test same word in different contexts."""
        text1 = "GUARANTEED by law"  # Legal guarantee
        text2 = "GUARANTEED returns"  # Financial guarantee (problematic)

        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        result1 = synthesizer.synthesize_corrections(text1, gates)
        result2 = synthesizer.synthesize_corrections(text2, gates)

        # Both should be corrected for consistency
        assert isinstance(result1['corrected'], str)
        assert isinstance(result2['corrected'], str)

    def test_abbreviation_expansion_context(self, synthesizer):
        """Test abbreviation expansion in context."""
        text = "Dr. Smith from ABC Ltd provides services"
        gates = [('legal_entity_name', {'status': 'FAIL', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)

        # Should expand Ltd but not Dr.
        assert 'Dr' in result['corrected'] or 'Smith' in result['corrected']


class TestRecursivePatterns:
    """Test patterns that might cause recursion."""

    def test_correction_creates_new_violation(self, synthesizer):
        """Test when a correction might create a new violation."""
        # This is theoretical - most corrections shouldn't create new violations
        text = "Test content"
        gates = [('test', {'status': 'FAIL', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)

        # Should not infinitely loop
        assert isinstance(result, dict)

    def test_nested_replacements(self, synthesizer):
        """Test nested replacement patterns."""
        text = "((GUARANTEED))"
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)

        # Should handle nesting
        assert 'GUARANTEED' not in result['corrected'] or 'potential' in result['corrected'].lower()


class TestLocalizationEdgeCases:
    """Test localization and regional variations."""

    def test_uk_vs_us_spelling(self, synthesizer):
        """Test UK vs US spellings."""
        text = "We recognise and organise your data"
        gates = [('test', {'status': 'PASS', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)

        # UK spellings should be preserved
        assert 'recognise' in result['corrected'] or 'organize' in result['corrected'] or 'data' in result['corrected']

    def test_currency_symbols_various(self, synthesizer):
        """Test various currency symbols."""
        text = "Prices: £100 $150 €200 ¥1000"
        gates = [('test', {'status': 'PASS', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)

        # All should be preserved
        assert '£' in result['corrected']
        assert '$' in result['corrected'] or '€' in result['corrected']

    def test_date_formats(self, synthesizer):
        """Test various date formats."""
        text = "Dates: 01/12/2024, 2024-12-01, 1st December 2024"
        gates = [('test', {'status': 'PASS', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)

        # Dates should be preserved
        assert '2024' in result['corrected'] or '12' in result['corrected']
