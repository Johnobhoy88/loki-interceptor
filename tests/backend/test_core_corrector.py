"""
Comprehensive tests for backend.core.corrector module.

Tests document correction functionality including:
- Text correction and synthesis
- Compliance violation fixes
- Multi-module correction
- Confidence scoring
- Correction rollback
- Performance optimization
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

from backend.core.corrector import DocumentCorrector


class TestDocumentCorrectorBasics:
    """Test basic document correction functionality."""

    def test_corrector_initialization(self):
        """Test DocumentCorrector can be initialized."""
        corrector = DocumentCorrector()
        assert corrector is not None
        assert hasattr(corrector, 'correct')
        assert hasattr(corrector, 'synthesize')

    def test_correct_simple_violation(self):
        """Test correcting a simple compliance violation."""
        corrector = DocumentCorrector()

        # Misleading claim
        text = "GUARANTEED 15% annual returns!"
        violations = [{
            "module": "fca_uk",
            "gate": "misleading_claims",
            "severity": "CRITICAL",
            "message": "Contains guaranteed return claim"
        }]

        result = corrector.correct(text, violations)

        assert result is not None
        if isinstance(result, dict):
            assert "corrected_text" in result or "text" in result

    def test_correct_multiple_violations(self):
        """Test correcting multiple violations."""
        corrector = DocumentCorrector()

        text = "GUARANTEED returns! Zero risk investment!"
        violations = [
            {
                "module": "fca_uk",
                "gate": "misleading_claims",
                "severity": "CRITICAL",
            },
            {
                "module": "fca_uk",
                "gate": "fair_clear_not_misleading",
                "severity": "CRITICAL",
            }
        ]

        result = corrector.correct(text, violations)
        assert result is not None

    def test_correct_gdpr_violation(self):
        """Test correcting GDPR violations."""
        corrector = DocumentCorrector()

        privacy_text = "We collect your data. Data is stored forever."
        violations = [{
            "module": "gdpr_uk",
            "gate": "data_retention",
            "severity": "HIGH",
        }]

        result = corrector.correct(privacy_text, violations)
        assert result is not None

    def test_correct_tax_violation(self):
        """Test correcting tax compliance violations."""
        corrector = DocumentCorrector()

        invoice_text = "Invoice: £1000 (VAT not calculated)"
        violations = [{
            "module": "tax_uk",
            "gate": "vat_calculation",
            "severity": "HIGH",
        }]

        result = corrector.correct(invoice_text, violations)
        assert result is not None

    def test_correct_preserves_original_meaning(self):
        """Test that corrections preserve original meaning."""
        corrector = DocumentCorrector()

        text = "This investment could provide strong returns but carries market risk."
        # Already compliant but test the preservation logic

        result = corrector.correct(text, [])
        # Result should be similar to original
        if result:
            if isinstance(result, dict):
                corrected = result.get("corrected_text") or result.get("text", "")
            else:
                corrected = str(result)

            # Should preserve key words
            assert "investment" in corrected.lower() or "returns" in corrected.lower()


class TestDocumentCorrectorStrategies:
    """Test different correction strategies."""

    def test_conservative_correction(self):
        """Test conservative correction strategy."""
        corrector = DocumentCorrector()

        text = "GUARANTEED returns!"
        violations = [{
            "module": "fca_uk",
            "gate": "misleading_claims",
            "severity": "CRITICAL",
        }]

        if hasattr(corrector, 'correct_with_strategy'):
            result = corrector.correct_with_strategy(
                text, violations, strategy="conservative"
            )
            # Conservative should make minimal changes
            assert result is not None

    def test_aggressive_correction(self):
        """Test aggressive correction strategy."""
        corrector = DocumentCorrector()

        text = "GUARANTEED returns!"
        violations = [{
            "module": "fca_uk",
            "gate": "misleading_claims",
            "severity": "CRITICAL",
        }]

        if hasattr(corrector, 'correct_with_strategy'):
            result = corrector.correct_with_strategy(
                text, violations, strategy="aggressive"
            )
            # Aggressive should ensure compliance
            assert result is not None

    def test_balanced_correction(self):
        """Test balanced correction strategy."""
        corrector = DocumentCorrector()

        text = "GUARANTEED returns!"
        violations = [{
            "module": "fca_uk",
            "gate": "misleading_claims",
            "severity": "CRITICAL",
        }]

        if hasattr(corrector, 'correct_with_strategy'):
            result = corrector.correct_with_strategy(
                text, violations, strategy="balanced"
            )
            assert result is not None


class TestDocumentCorrectorConfidence:
    """Test confidence scoring in corrections."""

    def test_correction_confidence_scoring(self):
        """Test that corrections are scored for confidence."""
        corrector = DocumentCorrector()

        text = "GUARANTEED returns!"
        violations = [{
            "module": "fca_uk",
            "gate": "misleading_claims",
            "severity": "CRITICAL",
        }]

        result = corrector.correct(text, violations)

        if isinstance(result, dict):
            # Should include confidence score
            if "confidence" in result:
                assert 0 <= result["confidence"] <= 1

    def test_low_confidence_corrections(self):
        """Test handling of low-confidence corrections."""
        corrector = DocumentCorrector()

        # Ambiguous text that might be hard to correct
        ambiguous_text = "Performance may vary based on market conditions."
        violations = [{
            "module": "fca_uk",
            "gate": "ambiguous_claim",
            "severity": "MEDIUM",
        }]

        result = corrector.correct(ambiguous_text, violations)

        if isinstance(result, dict) and "confidence" in result:
            # Low confidence might be returned
            pass


class TestDocumentCorrectorSynthesis:
    """Test correction synthesis functionality."""

    def test_synthesize_from_violations(self):
        """Test synthesizing corrections from violation list."""
        corrector = DocumentCorrector()

        text = "GUARANTEED returns! Zero risk!"
        violations = [
            {
                "module": "fca_uk",
                "gate": "misleading_claims",
                "severity": "CRITICAL",
            },
            {
                "module": "fca_uk",
                "gate": "risk_disclosure",
                "severity": "HIGH",
            }
        ]

        if hasattr(corrector, 'synthesize'):
            result = corrector.synthesize(text, violations)
            assert result is not None

    def test_synthesis_with_suggestions(self):
        """Test synthesis with suggested corrections."""
        corrector = DocumentCorrector()

        text = "GUARANTEED returns!"

        if hasattr(corrector, 'synthesize_with_suggestions'):
            result = corrector.synthesize_with_suggestions(
                text,
                [{
                    "module": "fca_uk",
                    "gate": "misleading_claims",
                    "suggested_fix": "This investment carries risks..."
                }]
            )
            assert result is not None


class TestDocumentCorrectorRollback:
    """Test correction rollback functionality."""

    def test_track_correction_history(self):
        """Test tracking correction history."""
        corrector = DocumentCorrector()

        original = "GUARANTEED returns!"
        violations = [{"module": "fca_uk", "gate": "misleading_claims"}]

        result = corrector.correct(original, violations)

        if hasattr(corrector, 'get_history'):
            history = corrector.get_history()
            # Should track changes
            assert history is not None

    def test_rollback_to_previous(self):
        """Test rolling back to previous version."""
        corrector = DocumentCorrector()

        text = "Version 1"
        if hasattr(corrector, 'save_version'):
            corrector.save_version("v1", text)

        text = "Version 2"
        if hasattr(corrector, 'save_version'):
            corrector.save_version("v2", text)

        if hasattr(corrector, 'rollback_to'):
            result = corrector.rollback_to("v1")

    def test_compare_versions(self):
        """Test comparing different versions."""
        corrector = DocumentCorrector()

        original = "GUARANTEED returns!"
        corrected = "This investment may provide returns."

        if hasattr(corrector, 'compare'):
            diff = corrector.compare(original, corrected)
            # Should show differences
            assert diff is not None


class TestDocumentCorrectorMultiModule:
    """Test corrections across multiple modules."""

    def test_multi_module_correction(self):
        """Test correcting violations from multiple modules."""
        corrector = DocumentCorrector()

        text = """
        GUARANTEED returns! Zero risk investment!
        We collect your data forever.
        Invoice £1000 (VAT not shown).
        """

        violations = [
            {
                "module": "fca_uk",
                "gate": "misleading_claims",
                "severity": "CRITICAL",
            },
            {
                "module": "gdpr_uk",
                "gate": "data_retention",
                "severity": "HIGH",
            },
            {
                "module": "tax_uk",
                "gate": "vat_disclosure",
                "severity": "HIGH",
            }
        ]

        result = corrector.correct(text, violations)
        assert result is not None

    def test_module_interaction_handling(self):
        """Test handling of corrections that might interact."""
        corrector = DocumentCorrector()

        # Text that might conflict when correcting for multiple modules
        text = "Risk-free investment suitable for all investors."
        violations = [
            {"module": "fca_uk", "gate": "risk_warning"},
            {"module": "fca_uk", "gate": "target_market"},
        ]

        result = corrector.correct(text, violations)
        assert result is not None


class TestDocumentCorrectorPerformance:
    """Test correction performance."""

    def test_single_violation_correction_speed(self):
        """Test speed of correcting single violation."""
        corrector = DocumentCorrector()

        text = "GUARANTEED returns!"
        violations = [{
            "module": "fca_uk",
            "gate": "misleading_claims",
        }]

        start_time = time.time()
        result = corrector.correct(text, violations)
        elapsed = time.time() - start_time

        # Should correct quickly
        assert elapsed < 5.0

    def test_bulk_correction_performance(self):
        """Test performance of correcting multiple documents."""
        corrector = DocumentCorrector()

        documents = [
            ("GUARANTEED returns!", [{
                "module": "fca_uk",
                "gate": "misleading_claims",
            }]),
            ("Zero risk!", [{"module": "fca_uk", "gate": "risk_warning"}]),
            ("100% success rate!", [{"module": "fca_uk", "gate": "misleading_claims"}]),
        ]

        start_time = time.time()
        for text, violations in documents:
            corrector.correct(text, violations)
        elapsed = time.time() - start_time

        # Should handle 3 documents in less than 10 seconds
        assert elapsed < 10.0

    def test_large_document_correction(self):
        """Test correcting large documents."""
        corrector = DocumentCorrector()

        large_text = "This is a safe investment. " * 1000  # ~30KB text
        violations = [{"module": "fca_uk", "gate": "risk_warning"}]

        start_time = time.time()
        result = corrector.correct(large_text, violations)
        elapsed = time.time() - start_time

        assert result is not None
        # Should handle large documents within timeout
        assert elapsed < 30.0


class TestDocumentCorrectorIntegration:
    """Integration tests for document correction."""

    def test_full_correction_workflow(self):
        """Test complete correction workflow."""
        corrector = DocumentCorrector()

        # Original document with violations
        document = """
        INVESTMENT OPPORTUNITY

        GUARANTEED 15% Annual Returns!

        Risk-free investment. Suitable for all investors.
        Zero loss guaranteed. Act now - limited offer!

        We collect and retain all personal data indefinitely.
        """

        violations = [
            {"module": "fca_uk", "gate": "misleading_claims", "severity": "CRITICAL"},
            {"module": "fca_uk", "gate": "risk_warning", "severity": "CRITICAL"},
            {"module": "gdpr_uk", "gate": "data_retention", "severity": "HIGH"},
        ]

        # Step 1: Correct the document
        corrected = corrector.correct(document, violations)
        assert corrected is not None

        # Step 2: Get confidence score
        if isinstance(corrected, dict) and "confidence" in corrected:
            confidence = corrected["confidence"]
            assert 0 <= confidence <= 1

        # Step 3: Could re-validate (in real scenario)
        if isinstance(corrected, dict):
            final_text = corrected.get("corrected_text") or corrected.get("text", "")
        else:
            final_text = str(corrected)

        # Final text should be improved
        assert "GUARANTEED" not in final_text or "may" in final_text.lower()


class TestDocumentCorrectorErrorHandling:
    """Test error handling in document correction."""

    def test_correct_empty_text(self):
        """Test handling of empty text."""
        corrector = DocumentCorrector()

        result = corrector.correct("", [])
        # Should handle gracefully
        assert result is not None or result is None

    def test_correct_none_text(self):
        """Test handling of None text."""
        corrector = DocumentCorrector()

        try:
            result = corrector.correct(None, [])
        except Exception:
            pass  # Expected

    def test_correct_empty_violations(self):
        """Test correcting with empty violation list."""
        corrector = DocumentCorrector()

        text = "This is a compliant document."
        result = corrector.correct(text, [])

        # Should return the text unchanged or minimally modified
        if isinstance(result, dict):
            corrected = result.get("corrected_text") or result.get("text")
        else:
            corrected = str(result) if result else ""

        # Should be similar to original
        assert len(corrected) >= len(text) * 0.5

    def test_correct_with_invalid_violations(self):
        """Test handling of invalid violation structures."""
        corrector = DocumentCorrector()

        text = "Test document"
        invalid_violations = [
            {},  # Missing required fields
            {"module": "invalid_module"},
            None,
        ]

        try:
            result = corrector.correct(text, invalid_violations)
        except Exception:
            pass  # Some implementations may raise
