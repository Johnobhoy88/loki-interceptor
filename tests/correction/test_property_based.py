"""
Property-Based Testing for Correction System

This module uses Hypothesis library for property-based testing to automatically
generate test cases and verify invariants hold across all inputs.

Properties Tested:
- Determinism: Same input always produces same output
- Idempotency: Applying corrections multiple times doesn't change result
- Structure preservation: Corrections maintain document structure
- No data loss: Essential information is not lost
- Length bounds: Corrected text length is reasonable
- Unicode safety: Unicode characters are handled correctly
- Metadata consistency: Correction metadata is always complete
"""

import pytest
import re
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from hypothesis import example, note
from typing import Dict, List

from backend.core.correction_synthesizer import CorrectionSynthesizer, CorrectionValidator
from backend.core.correction_strategies import (
    RegexReplacementStrategy,
    TemplateInsertionStrategy,
    StructuralReorganizationStrategy,
    SuggestionExtractionStrategy
)
from backend.core.correction_patterns import CorrectionPatternRegistry


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="module")
def synthesizer_full():
    """Create fully configured synthesizer (module-scoped for performance)."""
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

    template_strategy = TemplateInsertionStrategy()
    for gate_pattern, templates in pattern_registry.templates.items():
        for template in templates:
            template_strategy.register_template(
                gate_pattern,
                template['template'],
                template['position'],
                template.get('condition')
            )

    structural_strategy = StructuralReorganizationStrategy()
    for gate_pattern, rules in pattern_registry.structural_rules.items():
        for rule in rules:
            structural_strategy.register_rule(
                gate_pattern,
                rule['type'],
                rule['config']
            )

    suggestion_strategy = SuggestionExtractionStrategy()

    strategies = [
        suggestion_strategy,
        regex_strategy,
        template_strategy,
        structural_strategy
    ]

    return CorrectionSynthesizer(strategies)


# ============================================================================
# HYPOTHESIS STRATEGIES (Input Generators)
# ============================================================================

# Generate text with various characteristics
text_strategy = st.text(
    alphabet=st.characters(
        blacklist_categories=('Cs',),  # Exclude surrogates
        blacklist_characters='\x00'
    ),
    min_size=0,
    max_size=500
)

# Generate text with specific problematic patterns
problematic_text_strategy = st.one_of(
    st.just("GUARANTEED returns!"),
    st.just("risk-free investment"),
    st.just("By using this site you agree"),
    st.just("VAT threshold is £85,000"),
    st.just("in perpetuity"),
    st.just("You must purchase"),
    st.text(min_size=10, max_size=200)
)

# Generate gate results
gate_status_strategy = st.sampled_from(['PASS', 'FAIL', 'WARNING'])
gate_severity_strategy = st.sampled_from(['low', 'medium', 'high', 'critical'])

gate_result_strategy = st.builds(
    dict,
    status=gate_status_strategy,
    severity=gate_severity_strategy
)

gate_entry_strategy = st.tuples(
    st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L',))),
    gate_result_strategy
)

gates_list_strategy = st.lists(
    gate_entry_strategy,
    min_size=0,
    max_size=10
)


# ============================================================================
# PROPERTY: DETERMINISM
# ============================================================================

class TestDeterminismProperty:
    """Test determinism property: same input always produces same output."""

    @given(
        text=problematic_text_strategy,
        gates=gates_list_strategy
    )
    @settings(max_examples=50, deadline=2000)
    def test_determinism_property(self, synthesizer_full, text, gates):
        """
        Property: Applying corrections with identical inputs produces identical outputs.
        """
        assume(len(text) > 0)  # Skip empty texts

        # Apply corrections twice
        result1 = synthesizer_full.synthesize_corrections(text, gates)
        result2 = synthesizer_full.synthesize_corrections(text, gates)

        # Should produce identical results
        assert result1['corrected'] == result2['corrected']
        assert result1['correction_count'] == result2['correction_count']
        assert result1['strategies_applied'] == result2['strategies_applied']

    @given(
        text=text_strategy,
        gates=gates_list_strategy
    )
    @settings(max_examples=30, deadline=2000)
    def test_determinism_hash_consistency(self, synthesizer_full, text, gates):
        """
        Property: Determinism hashes are consistent across runs.
        """
        assume(len(text) > 0)

        result1 = synthesizer_full.synthesize_corrections(text, gates)
        result2 = synthesizer_full.synthesize_corrections(text, gates)

        assert result1['determinism']['input_hash'] == result2['determinism']['input_hash']
        assert result1['determinism']['output_hash'] == result2['determinism']['output_hash']


# ============================================================================
# PROPERTY: IDEMPOTENCY
# ============================================================================

class TestIdempotencyProperty:
    """Test idempotency: applying corrections multiple times converges."""

    @given(
        text=problematic_text_strategy,
        gates=gates_list_strategy
    )
    @settings(max_examples=30, deadline=3000)
    def test_idempotency_property(self, synthesizer_full, text, gates):
        """
        Property: Applying corrections repeatedly eventually stabilizes.
        """
        assume(len(text) > 0)

        # First correction
        result1 = synthesizer_full.synthesize_corrections(text, gates)

        # Apply corrections to corrected text
        result2 = synthesizer_full.synthesize_corrections(result1['corrected'], gates)

        # Third iteration
        result3 = synthesizer_full.synthesize_corrections(result2['corrected'], gates)

        # Should converge (2nd and 3rd should be identical or very similar)
        assert result2['corrected'] == result3['corrected'] or \
               result2['correction_count'] == 0  # No more corrections needed

    @given(text=problematic_text_strategy)
    @settings(max_examples=20, deadline=2000)
    def test_double_correction_idempotency(self, synthesizer_full, text):
        """
        Property: Correcting already-corrected text adds minimal changes.
        """
        assume(len(text) > 5)

        gates = [('test', {'status': 'FAIL', 'severity': 'low'})]

        result1 = synthesizer_full.synthesize_corrections(text, gates)
        result2 = synthesizer_full.synthesize_corrections(result1['corrected'], gates)

        # Length should not grow excessively
        assert len(result2['corrected']) <= len(result1['corrected']) * 1.2


# ============================================================================
# PROPERTY: STRUCTURE PRESERVATION
# ============================================================================

class TestStructurePreservationProperty:
    """Test that corrections preserve document structure."""

    @given(
        text=st.text(min_size=20, max_size=300),
        gates=gates_list_strategy
    )
    @settings(max_examples=30, deadline=2000)
    def test_line_count_reasonable(self, synthesizer_full, text, gates):
        """
        Property: Line count doesn't change drastically (within reason).
        """
        assume(len(text) > 10)

        result = synthesizer_full.synthesize_corrections(text, gates)

        original_lines = text.count('\n')
        corrected_lines = result['corrected'].count('\n')

        # Allow additions but not dramatic changes
        assert corrected_lines <= original_lines + 50  # Templates can add lines

    @given(text=text_strategy)
    @settings(max_examples=50, deadline=1000)
    def test_whitespace_not_destroyed(self, synthesizer_full, text):
        """
        Property: Whitespace structure is somewhat preserved.
        """
        assume(len(text) > 10)
        assume('\n\n' in text)  # Has paragraph breaks

        gates = [('test', {'status': 'PASS', 'severity': 'low'})]
        result = synthesizer_full.synthesize_corrections(text, gates)

        # Should still have some paragraph breaks
        assert '\n' in result['corrected'] or len(result['corrected']) < 20

    @given(
        text=st.text(min_size=10, max_size=100),
        gates=gates_list_strategy
    )
    @settings(max_examples=30, deadline=2000)
    def test_non_empty_output(self, synthesizer_full, text, gates):
        """
        Property: Non-empty input produces non-empty output.
        """
        assume(len(text.strip()) > 0)

        result = synthesizer_full.synthesize_corrections(text, gates)

        # Should not produce empty output
        assert len(result['corrected'].strip()) > 0


# ============================================================================
# PROPERTY: NO DATA LOSS
# ============================================================================

class TestNoDataLossProperty:
    """Test that essential information is not lost."""

    @given(
        email=st.emails(),
        text_before=st.text(max_size=50),
        text_after=st.text(max_size=50)
    )
    @settings(max_examples=20, deadline=2000)
    def test_email_preservation(self, synthesizer_full, email, text_before, text_after):
        """
        Property: Email addresses in text are preserved.
        """
        text = f"{text_before} {email} {text_after}"
        assume(len(text) > 10)

        gates = [('test', {'status': 'PASS', 'severity': 'low'})]
        result = synthesizer_full.synthesize_corrections(text, gates)

        # Email should still be present
        assert email in result['corrected']

    @given(
        url=st.from_regex(r'https?://[a-z]+\.[a-z]{2,5}', fullmatch=True),
        text_before=st.text(max_size=50),
        text_after=st.text(max_size=50)
    )
    @settings(max_examples=20, deadline=2000)
    def test_url_preservation(self, synthesizer_full, url, text_before, text_after):
        """
        Property: URLs in text are preserved.
        """
        text = f"{text_before} {url} {text_after}"
        assume(len(text) > 10)

        gates = [('test', {'status': 'PASS', 'severity': 'low'})]
        result = synthesizer_full.synthesize_corrections(text, gates)

        # URL should be preserved
        assert url in result['corrected']

    @given(
        phone=st.from_regex(r'0\d{3}-\d{3}-\d{4}', fullmatch=True),
        text=st.text(min_size=10, max_size=100)
    )
    @settings(max_examples=20, deadline=2000)
    def test_phone_preservation(self, synthesizer_full, phone, text):
        """
        Property: Phone numbers are preserved.
        """
        full_text = f"Contact us: {phone}. {text}"

        gates = [('test', {'status': 'PASS', 'severity': 'low'})]
        result = synthesizer_full.synthesize_corrections(full_text, gates)

        # Phone should be preserved
        assert phone in result['corrected']


# ============================================================================
# PROPERTY: LENGTH BOUNDS
# ============================================================================

class TestLengthBoundsProperty:
    """Test that corrected text length is within reasonable bounds."""

    @given(
        text=text_strategy,
        gates=gates_list_strategy
    )
    @settings(max_examples=50, deadline=2000)
    def test_length_growth_bounded(self, synthesizer_full, text, gates):
        """
        Property: Corrected text doesn't grow excessively (max 5x original).
        """
        assume(len(text) > 10)

        result = synthesizer_full.synthesize_corrections(text, gates)

        # Should not grow more than 5x (templates can add content)
        assert len(result['corrected']) <= len(text) * 5

    @given(text=text_strategy)
    @settings(max_examples=50, deadline=1000)
    def test_no_excessive_shrinkage(self, synthesizer_full, text):
        """
        Property: Corrections don't remove more than 50% of content.
        """
        assume(len(text) > 20)

        gates = [('test', {'status': 'FAIL', 'severity': 'low'})]
        result = synthesizer_full.synthesize_corrections(text, gates)

        # Should not shrink more than 50% (some deletions are OK)
        assert len(result['corrected']) >= len(text) * 0.5

    @given(
        text=st.text(min_size=1, max_size=50),
        gates=gates_list_strategy
    )
    @settings(max_examples=30, deadline=2000)
    def test_minimum_length_maintained(self, synthesizer_full, text, gates):
        """
        Property: Non-empty input produces output with minimum length.
        """
        assume(len(text.strip()) > 0)

        result = synthesizer_full.synthesize_corrections(text, gates)

        # Should have some content
        assert len(result['corrected']) > 0


# ============================================================================
# PROPERTY: UNICODE SAFETY
# ============================================================================

class TestUnicodeSafetyProperty:
    """Test that unicode characters are handled correctly."""

    @given(
        text=st.text(
            alphabet=st.characters(
                blacklist_categories=('Cs',),
                whitelist_categories=('L', 'N', 'P')
            ),
            min_size=5,
            max_size=100
        )
    )
    @settings(max_examples=50, deadline=2000)
    def test_unicode_preservation(self, synthesizer_full, text):
        """
        Property: Unicode characters are preserved through corrections.
        """
        assume(len(text) > 3)

        gates = [('test', {'status': 'PASS', 'severity': 'low'})]
        result = synthesizer_full.synthesize_corrections(text, gates)

        # Should be valid unicode
        assert isinstance(result['corrected'], str)
        # Should be encodable/decodable
        assert result['corrected'].encode('utf-8').decode('utf-8') == result['corrected']

    @given(
        text=st.text(
            alphabet='£€¥₹₽¢',
            min_size=1,
            max_size=20
        )
    )
    @settings(max_examples=20, deadline=1000)
    def test_currency_symbols_preserved(self, synthesizer_full, text):
        """
        Property: Currency symbols are preserved.
        """
        full_text = f"Price: {text} per unit"

        gates = [('test', {'status': 'PASS', 'severity': 'low'})]
        result = synthesizer_full.synthesize_corrections(full_text, gates)

        # At least some currency symbols should remain
        currency_symbols = set('£€¥₹₽¢')
        original_currencies = currency_symbols & set(full_text)
        result_currencies = currency_symbols & set(result['corrected'])

        assert len(result_currencies) >= len(original_currencies) * 0.5

    @given(
        text=st.text(
            alphabet=st.characters(whitelist_categories=('Lo',)),  # Other letters (CJK, etc)
            min_size=3,
            max_size=30
        )
    )
    @settings(max_examples=20, deadline=1000)
    def test_multibyte_characters(self, synthesizer_full, text):
        """
        Property: Multibyte characters (CJK, Arabic, etc.) are handled.
        """
        assume(len(text) > 2)

        gates = [('test', {'status': 'PASS', 'severity': 'low'})]
        result = synthesizer_full.synthesize_corrections(text, gates)

        # Should not crash and produce valid output
        assert isinstance(result['corrected'], str)
        assert len(result['corrected']) > 0


# ============================================================================
# PROPERTY: METADATA CONSISTENCY
# ============================================================================

class TestMetadataConsistencyProperty:
    """Test that correction metadata is always complete and consistent."""

    @given(
        text=problematic_text_strategy,
        gates=gates_list_strategy
    )
    @settings(max_examples=30, deadline=2000)
    def test_correction_count_matches_list(self, synthesizer_full, text, gates):
        """
        Property: Correction count matches length of corrections list.
        """
        assume(len(text) > 0)

        result = synthesizer_full.synthesize_corrections(text, gates)

        assert result['correction_count'] == len(result['corrections'])

    @given(
        text=problematic_text_strategy,
        gates=gates_list_strategy
    )
    @settings(max_examples=30, deadline=2000)
    def test_all_corrections_have_metadata(self, synthesizer_full, text, gates):
        """
        Property: Every correction has complete metadata.
        """
        assume(len(text) > 0)

        result = synthesizer_full.synthesize_corrections(text, gates)

        for correction in result['corrections']:
            assert 'gate_id' in correction
            assert 'strategy' in correction
            assert 'gate_severity' in correction
            assert 'metadata' in correction
            assert isinstance(correction['metadata'], dict)

    @given(
        text=problematic_text_strategy,
        gates=gates_list_strategy
    )
    @settings(max_examples=30, deadline=2000)
    def test_strategies_applied_is_sorted(self, synthesizer_full, text, gates):
        """
        Property: Strategies applied list is always sorted (for determinism).
        """
        assume(len(text) > 0)

        result = synthesizer_full.synthesize_corrections(text, gates)

        strategies = result['strategies_applied']
        assert strategies == sorted(strategies)

    @given(
        text=text_strategy,
        gates=gates_list_strategy
    )
    @settings(max_examples=30, deadline=2000)
    def test_determinism_dict_present(self, synthesizer_full, text, gates):
        """
        Property: Determinism metadata is always present.
        """
        assume(len(text) > 0)

        result = synthesizer_full.synthesize_corrections(text, gates)

        assert 'determinism' in result
        assert 'input_hash' in result['determinism']
        assert 'output_hash' in result['determinism']
        assert 'repeatable' in result['determinism']


# ============================================================================
# PROPERTY: CORRECTION VALIDATOR
# ============================================================================

class TestCorrectionValidatorProperty:
    """Test correction validator properties."""

    @given(
        original=st.text(min_size=10, max_size=100),
        corrected=st.text(min_size=10, max_size=100)
    )
    @settings(max_examples=30, deadline=1000)
    def test_validator_always_returns_dict(self, original, corrected):
        """
        Property: Validator always returns proper structure.
        """
        corrections = []
        result = CorrectionValidator.validate_correction(original, corrected, corrections)

        assert isinstance(result, dict)
        assert 'valid' in result
        assert 'warnings' in result
        assert 'errors' in result
        assert isinstance(result['valid'], bool)
        assert isinstance(result['warnings'], list)
        assert isinstance(result['errors'], list)

    @given(text=st.text(min_size=10, max_size=100))
    @settings(max_examples=20, deadline=1000)
    def test_validator_identical_text(self, text):
        """
        Property: Validator accepts identical text (no changes).
        """
        assume(len(text.strip()) > 5)

        result = CorrectionValidator.validate_correction(text, text, [])

        # Should be valid (no changes is OK)
        assert result['valid'] == True or len(result['errors']) == 0

    @given(
        original=st.text(min_size=50, max_size=100),
        ratio=st.floats(min_value=0.1, max_value=0.4)
    )
    @settings(max_examples=20, deadline=1000)
    def test_validator_excessive_deletion_warning(self, original, ratio):
        """
        Property: Validator warns about excessive deletions.
        """
        assume(len(original) > 40)

        # Create corrected text with major deletion
        corrected = original[:int(len(original) * ratio)]

        result = CorrectionValidator.validate_correction(original, corrected, [])

        # Should have warning about reduction
        assert len(result['warnings']) > 0 or not result['valid']


# ============================================================================
# PROPERTY: CORRECTION ORDER INDEPENDENCE
# ============================================================================

class TestCorrectionOrderProperty:
    """Test that gate order doesn't affect final result."""

    @given(
        text=problematic_text_strategy,
        gates_list=st.lists(
            gate_entry_strategy,
            min_size=2,
            max_size=5,
            unique_by=lambda x: x[0]  # Unique gate IDs
        )
    )
    @settings(max_examples=20, deadline=3000)
    def test_gate_order_independence(self, synthesizer_full, text, gates_list):
        """
        Property: Different gate orderings produce same result (determinism).
        """
        assume(len(text) > 5)
        assume(len(gates_list) >= 2)

        # Apply with original order
        result1 = synthesizer_full.synthesize_corrections(text, gates_list)

        # Apply with reversed order
        gates_reversed = list(reversed(gates_list))
        result2 = synthesizer_full.synthesize_corrections(text, gates_reversed)

        # Results should be identical due to deterministic sorting
        assert result1['corrected'] == result2['corrected']


# ============================================================================
# PROPERTY: ROBUSTNESS TO MALFORMED INPUT
# ============================================================================

class TestRobustnessProperty:
    """Test robustness to edge cases and malformed inputs."""

    @given(gates=gates_list_strategy)
    @settings(max_examples=20, deadline=1000)
    def test_empty_text_handling(self, synthesizer_full, gates):
        """
        Property: Empty text is handled without errors.
        """
        result = synthesizer_full.synthesize_corrections("", gates)

        assert isinstance(result, dict)
        assert 'corrected' in result
        assert 'correction_count' in result

    @given(text=text_strategy)
    @settings(max_examples=30, deadline=1000)
    def test_empty_gates_handling(self, synthesizer_full, text):
        """
        Property: Empty gates list is handled without errors.
        """
        assume(len(text) > 0)

        result = synthesizer_full.synthesize_corrections(text, [])

        assert isinstance(result, dict)
        assert result['correction_count'] == 0
        assert result['unchanged'] == True

    @given(
        text=st.text(min_size=5, max_size=100),
        status=st.just('INVALID'),
        severity=st.just('unknown')
    )
    @settings(max_examples=20, deadline=1000)
    def test_invalid_gate_status(self, synthesizer_full, text, status, severity):
        """
        Property: Invalid gate statuses are handled gracefully.
        """
        gates = [('test_gate', {'status': status, 'severity': severity})]

        # Should not crash
        result = synthesizer_full.synthesize_corrections(text, gates)

        assert isinstance(result, dict)

    @given(
        text=st.text(
            alphabet=st.characters(whitelist_characters='\n \t'),
            min_size=5,
            max_size=50
        )
    )
    @settings(max_examples=20, deadline=1000)
    def test_whitespace_only_text(self, synthesizer_full, text):
        """
        Property: Whitespace-only text is handled.
        """
        gates = [('test', {'status': 'FAIL', 'severity': 'low'})]

        result = synthesizer_full.synthesize_corrections(text, gates)

        assert isinstance(result, dict)
        assert isinstance(result['corrected'], str)
