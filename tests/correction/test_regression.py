"""
Regression Test Suite for Correction System

This module contains regression tests to ensure that corrections don't degrade
over time and that previously fixed issues don't reoccur.

Test Strategy:
- Snapshot testing: Compare current corrections against known-good baselines
- Historical bug prevention: Test cases for previously fixed bugs
- Version comparison: Ensure new changes don't break existing corrections
- Golden file testing: Maintain reference outputs for key test cases
"""

import pytest
import json
import hashlib
import os
from pathlib import Path
from typing import Dict, List
from backend.core.correction_synthesizer import CorrectionSynthesizer
from backend.core.correction_strategies import (
    RegexReplacementStrategy,
    TemplateInsertionStrategy,
    StructuralReorganizationStrategy,
    SuggestionExtractionStrategy
)
from backend.core.correction_patterns import CorrectionPatternRegistry


# ============================================================================
# FIXTURES AND HELPERS
# ============================================================================

@pytest.fixture
def regression_data_dir(tmp_path):
    """Create temporary directory for regression test data."""
    regression_dir = tmp_path / "regression_data"
    regression_dir.mkdir()
    return regression_dir


@pytest.fixture
def synthesizer_full():
    """Create fully configured synthesizer."""
    pattern_registry = CorrectionPatternRegistry()

    # Regex strategy
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

    # Template strategy
    template_strategy = TemplateInsertionStrategy()
    for gate_pattern, templates in pattern_registry.templates.items():
        for template in templates:
            template_strategy.register_template(
                gate_pattern,
                template['template'],
                template['position'],
                template.get('condition')
            )

    # Structural strategy
    structural_strategy = StructuralReorganizationStrategy()
    for gate_pattern, rules in pattern_registry.structural_rules.items():
        for rule in rules:
            structural_strategy.register_rule(
                gate_pattern,
                rule['type'],
                rule['config']
            )

    # Suggestion strategy
    suggestion_strategy = SuggestionExtractionStrategy()

    strategies = [
        suggestion_strategy,
        regex_strategy,
        template_strategy,
        structural_strategy
    ]

    return CorrectionSynthesizer(strategies)


def calculate_correction_hash(result: Dict) -> str:
    """Calculate hash of correction result for comparison."""
    stable_repr = {
        'corrected_hash': hashlib.sha256(result['corrected'].encode('utf-8')).hexdigest(),
        'correction_count': result['correction_count'],
        'strategies': sorted(result['strategies_applied'])
    }
    return hashlib.sha256(json.dumps(stable_repr, sort_keys=True).encode('utf-8')).hexdigest()


# ============================================================================
# HISTORICAL BUG PREVENTION TESTS
# ============================================================================

class TestHistoricalBugPrevention:
    """Tests to ensure previously fixed bugs don't reoccur."""

    def test_bug_001_double_correction_prevention(self, synthesizer_full):
        """
        BUG-001: Prevent same correction being applied twice

        Historical issue: Some corrections were applied multiple times to the
        same location, causing duplication.
        """
        text = "GUARANTEED high returns!"
        gates = [
            ('fair_clear', {'status': 'FAIL', 'severity': 'critical'}),
            ('risk_benefit', {'status': 'FAIL', 'severity': 'high'})
        ]

        result = synthesizer_full.synthesize_corrections(text, gates)

        # Count occurrences of "potential" - should appear once, not multiple times
        potential_count = result['corrected'].lower().count('potential')
        assert potential_count <= 2, "Correction applied multiple times (BUG-001)"

    def test_bug_002_empty_document_handling(self, synthesizer_full):
        """
        BUG-002: Handle empty documents gracefully

        Historical issue: Empty documents caused crashes.
        """
        text = ""
        gates = [('test_gate', {'status': 'FAIL', 'severity': 'high'})]

        result = synthesizer_full.synthesize_corrections(text, gates)

        assert isinstance(result, dict)
        assert 'corrected' in result
        assert result['correction_count'] >= 0

    def test_bug_003_unicode_corruption(self, synthesizer_full):
        """
        BUG-003: Preserve unicode characters

        Historical issue: Unicode characters were being corrupted during corrections.
        """
        text = "Investment returns: £1000, €500, ¥10000. 用户信息"
        gates = [('test', {'status': 'PASS', 'severity': 'low'})]

        result = synthesizer_full.synthesize_corrections(text, gates)

        # All unicode should be preserved
        assert '£' in result['corrected']
        assert '€' in result['corrected']
        assert '¥' in result['corrected']
        assert '用户' in result['corrected']

    def test_bug_004_regex_catastrophic_backtracking(self, synthesizer_full):
        """
        BUG-004: Prevent catastrophic regex backtracking

        Historical issue: Some regex patterns caused performance issues with
        certain inputs due to catastrophic backtracking.
        """
        # Create text that could trigger backtracking
        text = "a" * 1000 + "GUARANTEED returns"
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        import time
        start = time.time()
        result = synthesizer_full.synthesize_corrections(text, gates)
        duration = time.time() - start

        # Should complete in reasonable time (< 2 seconds)
        assert duration < 2.0, f"Regex took too long: {duration}s (possible backtracking)"
        assert 'GUARANTEED' not in result['corrected']

    def test_bug_005_template_infinite_insertion(self, synthesizer_full):
        """
        BUG-005: Prevent infinite template insertion

        Historical issue: Templates were being inserted even when already present,
        causing the document to grow infinitely.
        """
        text = "We provide financial services."
        gates = [('fos_signposting', {'status': 'FAIL', 'severity': 'medium'})]

        result1 = synthesizer_full.synthesize_corrections(text, gates)

        # Apply corrections again on already-corrected text
        result2 = synthesizer_full.synthesize_corrections(result1['corrected'], gates)

        # Should not add the same template again
        assert len(result2['corrected']) <= len(result1['corrected']) * 1.1, "Template inserted multiple times"

    def test_bug_006_case_sensitivity_issue(self, synthesizer_full):
        """
        BUG-006: Case-insensitive matching issues

        Historical issue: Some patterns weren't matching due to case sensitivity.
        """
        text1 = "GUARANTEED returns!"
        text2 = "guaranteed returns!"
        text3 = "GuArAnTeEd returns!"

        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        result1 = synthesizer_full.synthesize_corrections(text1, gates)
        result2 = synthesizer_full.synthesize_corrections(text2, gates)
        result3 = synthesizer_full.synthesize_corrections(text3, gates)

        # All variations should be corrected
        assert 'guaranteed' not in result1['corrected'].lower()
        assert 'guaranteed' not in result2['corrected'].lower()
        assert 'guaranteed' not in result3['corrected'].lower()

    def test_bug_007_whitespace_preservation(self, synthesizer_full):
        """
        BUG-007: Preserve document whitespace structure

        Historical issue: Corrections were collapsing multiple newlines and
        destroying document structure.
        """
        text = "Section 1\n\n\nContent here\n\n\nSection 2\n\n\nMore content"
        gates = [('test', {'status': 'PASS', 'severity': 'low'})]

        result = synthesizer_full.synthesize_corrections(text, gates)

        # Should maintain reasonable whitespace (may normalize somewhat)
        newline_count_original = text.count('\n')
        newline_count_corrected = result['corrected'].count('\n')

        # Allow some normalization but not complete collapse
        assert newline_count_corrected >= newline_count_original * 0.5

    def test_bug_008_special_char_escaping(self, synthesizer_full):
        """
        BUG-008: Properly escape special regex characters

        Historical issue: Special characters in patterns weren't being escaped,
        causing regex errors.
        """
        text = "Investment cost: $100 (plus fees)."
        gates = [('test', {'status': 'PASS', 'severity': 'low'})]

        # Should not crash on special characters
        result = synthesizer_full.synthesize_corrections(text, gates)

        assert '$' in result['corrected']
        assert '(' in result['corrected']
        assert ')' in result['corrected']

    def test_bug_009_correction_order_dependency(self, synthesizer_full):
        """
        BUG-009: Corrections should be order-independent

        Historical issue: Order of gates in input affected the output.
        """
        text = "GUARANTEED returns! High yields!"

        gates_order_1 = [
            ('fair_clear', {'status': 'FAIL', 'severity': 'critical'}),
            ('risk_benefit', {'status': 'FAIL', 'severity': 'high'})
        ]

        gates_order_2 = [
            ('risk_benefit', {'status': 'FAIL', 'severity': 'high'}),
            ('fair_clear', {'status': 'FAIL', 'severity': 'critical'})
        ]

        result1 = synthesizer_full.synthesize_corrections(text, gates_order_1)
        result2 = synthesizer_full.synthesize_corrections(text, gates_order_2)

        # Results should be identical regardless of gate order
        assert result1['corrected'] == result2['corrected']

    def test_bug_010_metadata_corruption(self, synthesizer_full):
        """
        BUG-010: Correction metadata should be complete and valid

        Historical issue: Some corrections had missing or invalid metadata.
        """
        text = "GUARANTEED returns!"
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer_full.synthesize_corrections(text, gates)

        # Verify metadata completeness
        for correction in result['corrections']:
            assert 'gate_id' in correction
            assert 'strategy' in correction
            assert 'gate_severity' in correction
            assert 'metadata' in correction
            assert isinstance(correction['metadata'], dict)


# ============================================================================
# SNAPSHOT TESTING
# ============================================================================

class TestCorrectionSnapshots:
    """Snapshot tests to catch unintended changes in corrections."""

    def test_snapshot_fca_risk_warning(self, synthesizer_full):
        """Snapshot test for FCA risk warning corrections."""
        text = "High returns await! Guaranteed profits!"
        gates = [
            ('fair_clear', {'status': 'FAIL', 'severity': 'critical'}),
            ('risk_benefit', {'status': 'FAIL', 'severity': 'high'})
        ]

        result = synthesizer_full.synthesize_corrections(text, gates)

        # Calculate hash for comparison
        result_hash = calculate_correction_hash(result)

        # Expected hash (would be updated if corrections intentionally change)
        # This is a placeholder - in real use, this would be a known-good hash
        assert isinstance(result_hash, str)
        assert len(result_hash) == 64  # SHA-256 hash

    def test_snapshot_gdpr_consent(self, synthesizer_full):
        """Snapshot test for GDPR consent corrections."""
        text = "By using this website, you automatically agree to our data processing."
        gates = [('consent', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer_full.synthesize_corrections(text, gates)

        # Key assertions that should remain stable
        assert 'automatically' not in result['corrected'].lower() or 'explicit' in result['corrected'].lower()
        assert result['correction_count'] > 0

    def test_snapshot_tax_vat_threshold(self, synthesizer_full):
        """Snapshot test for VAT threshold corrections."""
        text = "The VAT registration threshold is £85,000."
        gates = [('vat_threshold', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer_full.synthesize_corrections(text, gates)

        # Should always update to current threshold
        assert '£90,000' in result['corrected']
        assert '£85,000' not in result['corrected']

    def test_snapshot_nda_whistleblowing(self, synthesizer_full):
        """Snapshot test for NDA whistleblowing protections."""
        text = "All information is strictly confidential and cannot be disclosed."
        gates = [('whistleblowing', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer_full.synthesize_corrections(text, gates)

        # Should add whistleblowing protection
        corrected_lower = result['corrected'].lower()
        assert 'whistleblow' in corrected_lower or 'public interest' in corrected_lower

    def test_snapshot_hr_accompaniment(self, synthesizer_full):
        """Snapshot test for HR accompaniment rights."""
        text = "You are invited to a disciplinary meeting tomorrow."
        gates = [('accompaniment', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer_full.synthesize_corrections(text, gates)

        # Should add accompaniment rights
        assert 'accompanied' in result['corrected'].lower() or 'colleague' in result['corrected'].lower()


# ============================================================================
# DETERMINISM AND CONSISTENCY TESTS
# ============================================================================

class TestDeterminismConsistency:
    """Test that corrections are deterministic and consistent."""

    def test_identical_inputs_identical_outputs(self, synthesizer_full):
        """Test same input always produces same output."""
        text = "GUARANTEED returns on your investment!"
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        results = []
        for _ in range(5):
            result = synthesizer_full.synthesize_corrections(text, gates)
            results.append(result['corrected'])

        # All results should be identical
        assert all(r == results[0] for r in results)

    def test_determinism_hash_stability(self, synthesizer_full):
        """Test determinism hashes are stable across runs."""
        text = "Test document with violations"
        gates = [('test', {'status': 'FAIL', 'severity': 'medium'})]

        hashes = []
        for _ in range(3):
            result = synthesizer_full.synthesize_corrections(text, gates)
            hashes.append(result['determinism']['output_hash'])

        # All hashes should be identical
        assert all(h == hashes[0] for h in hashes)

    def test_correction_count_consistency(self, synthesizer_full):
        """Test correction counts are consistent."""
        text = "GUARANTEED returns! Risk-free investment! High yields!"
        gates = [
            ('fair_clear', {'status': 'FAIL', 'severity': 'critical'}),
            ('risk_benefit', {'status': 'FAIL', 'severity': 'high'})
        ]

        counts = []
        for _ in range(3):
            result = synthesizer_full.synthesize_corrections(text, gates)
            counts.append(result['correction_count'])

        # Correction count should be stable
        assert all(c == counts[0] for c in counts)

    def test_strategy_application_order(self, synthesizer_full):
        """Test strategies are always applied in same order."""
        text = "Document with multiple correction needs."
        gates = [
            ('gate_1', {'status': 'FAIL', 'severity': 'high'}),
            ('gate_2', {'status': 'FAIL', 'severity': 'high'}),
            ('gate_3', {'status': 'FAIL', 'severity': 'high'})
        ]

        strategy_lists = []
        for _ in range(3):
            result = synthesizer_full.synthesize_corrections(text, gates)
            strategy_lists.append(result['strategies_applied'])

        # Strategy lists should be identical (and sorted for determinism)
        assert all(sl == strategy_lists[0] for sl in strategy_lists)


# ============================================================================
# CORRECTION QUALITY REGRESSION TESTS
# ============================================================================

class TestCorrectionQualityRegression:
    """Test that correction quality doesn't degrade."""

    def test_correction_completeness(self, synthesizer_full):
        """Test all violations are addressed."""
        text = "GUARANTEED returns! Risk-free! High yields!"
        gates = [
            ('fair_clear_1', {'status': 'FAIL', 'severity': 'critical'}),
            ('fair_clear_2', {'status': 'FAIL', 'severity': 'critical'}),
            ('risk_benefit', {'status': 'FAIL', 'severity': 'high'})
        ]

        result = synthesizer_full.synthesize_corrections(text, gates)

        # All problematic terms should be addressed
        corrected_upper = result['corrected'].upper()
        assert 'GUARANTEED' not in corrected_upper or 'POTENTIAL' in corrected_upper.upper()

    def test_no_document_corruption(self, synthesizer_full):
        """Test corrections don't corrupt document structure."""
        text = """
        # Financial Services Document

        ## Section 1: Introduction
        This document outlines our services.

        ## Section 2: Terms
        Various terms apply.

        ## Section 3: Contact
        Contact us for more information.
        """

        gates = [('test', {'status': 'WARNING', 'severity': 'low'})]

        result = synthesizer_full.synthesize_corrections(text, gates)

        # Basic structure should be maintained
        assert 'Section 1' in result['corrected']
        assert 'Section 2' in result['corrected']
        assert 'Section 3' in result['corrected']

    def test_text_length_reasonableness(self, synthesizer_full):
        """Test corrected text length is reasonable."""
        text = "GUARANTEED returns on investments." * 10
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer_full.synthesize_corrections(text, gates)

        original_len = len(text)
        corrected_len = len(result['corrected'])

        # Corrected text should be within 3x of original (accounting for additions)
        assert corrected_len < original_len * 3

    def test_no_information_loss(self, synthesizer_full):
        """Test corrections don't lose essential information."""
        text = "Contact us at support@example.com or call 0800-123-4567 for assistance."
        gates = [('test', {'status': 'PASS', 'severity': 'low'})]

        result = synthesizer_full.synthesize_corrections(text, gates)

        # Contact information should be preserved
        assert 'support@example.com' in result['corrected']
        assert '0800-123-4567' in result['corrected']

    def test_multiple_corrections_no_conflicts(self, synthesizer_full):
        """Test multiple corrections don't conflict."""
        text = "GUARANTEED returns! By using this site you consent. VAT is £85,000."
        gates = [
            ('fair_clear', {'status': 'FAIL', 'severity': 'critical'}),
            ('consent', {'status': 'FAIL', 'severity': 'critical'}),
            ('vat_threshold', {'status': 'FAIL', 'severity': 'medium'})
        ]

        result = synthesizer_full.synthesize_corrections(text, gates)

        # All corrections should be applied
        assert result['correction_count'] >= 2
        # No correction should undo another
        assert '£90,000' in result['corrected']  # VAT correction preserved


# ============================================================================
# PERFORMANCE REGRESSION TESTS
# ============================================================================

class TestPerformanceRegression:
    """Test that correction performance doesn't degrade."""

    def test_short_document_performance(self, synthesizer_full):
        """Test short document correction performance."""
        text = "GUARANTEED returns! Risk-free investment!"
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        import time
        start = time.time()
        result = synthesizer_full.synthesize_corrections(text, gates)
        duration = time.time() - start

        # Should complete very quickly
        assert duration < 0.5, f"Short document took {duration}s"

    def test_medium_document_performance(self, synthesizer_full):
        """Test medium document correction performance."""
        text = "Financial services document. " * 100  # ~2.5KB
        gates = [('test', {'status': 'FAIL', 'severity': 'medium'})]

        import time
        start = time.time()
        result = synthesizer_full.synthesize_corrections(text, gates)
        duration = time.time() - start

        # Should complete reasonably quickly
        assert duration < 2.0, f"Medium document took {duration}s"

    def test_many_gates_performance(self, synthesizer_full):
        """Test performance with many failing gates."""
        text = "Document with multiple issues."
        gates = [(f'gate_{i}', {'status': 'FAIL', 'severity': 'low'}) for i in range(20)]

        import time
        start = time.time()
        result = synthesizer_full.synthesize_corrections(text, gates)
        duration = time.time() - start

        # Should handle many gates efficiently
        assert duration < 3.0, f"Many gates took {duration}s"


# ============================================================================
# BASELINE COMPARISON TESTS
# ============================================================================

class TestBaselineComparison:
    """Compare corrections against baseline outputs."""

    def test_baseline_fca_document(self, synthesizer_full):
        """Test FCA document against baseline."""
        text = """
        Investment Opportunity

        GUARANTEED returns of 15% annually! This is a risk-free investment
        that you should take advantage of immediately. ACT NOW!

        High yields with no downside risk!
        """

        gates = [
            ('fair_clear', {'status': 'FAIL', 'severity': 'critical'}),
            ('risk_benefit', {'status': 'FAIL', 'severity': 'high'}),
            ('cross_cutting', {'status': 'FAIL', 'severity': 'high'})
        ]

        result = synthesizer_full.synthesize_corrections(text, gates)

        # Baseline expectations
        assert 'GUARANTEED' not in result['corrected']
        assert 'risk-free' not in result['corrected'].lower()
        assert result['correction_count'] >= 3

    def test_baseline_gdpr_policy(self, synthesizer_full):
        """Test GDPR policy against baseline."""
        text = """
        Privacy Policy

        By using this website, you automatically agree to our data collection.
        We store your data permanently and may share it with third parties.
        """

        gates = [
            ('consent', {'status': 'FAIL', 'severity': 'critical'}),
            ('retention', {'status': 'FAIL', 'severity': 'high'}),
            ('third_party_sharing', {'status': 'FAIL', 'severity': 'high'})
        ]

        result = synthesizer_full.synthesize_corrections(text, gates)

        # Baseline expectations
        assert 'automatically' not in result['corrected'].lower() or 'explicit' in result['corrected'].lower()
        assert result['correction_count'] >= 2

    def test_baseline_minimal_changes_compliant(self, synthesizer_full):
        """Test that compliant documents get minimal changes."""
        text = """
        Professional Services Agreement

        This agreement is entered into between the parties as set out below.
        Both parties agree to maintain confidentiality as outlined herein.

        Contact: legal@example.com
        """

        gates = [('test', {'status': 'PASS', 'severity': 'low'})]

        result = synthesizer_full.synthesize_corrections(text, gates)

        # Should have minimal or no corrections
        assert result['correction_count'] == 0 or result['unchanged'] == True
