"""
Performance Benchmarking Suite for Correction System

This module contains performance benchmarks to ensure corrections remain fast
and to establish baseline performance metrics.

Benchmarks:
- Short document corrections (< 1KB)
- Medium document corrections (1-10KB)
- Long document corrections (10-50KB)
- Multiple gates processing
- Different correction strategies
- Concurrent correction requests
- Memory usage profiling
"""

import pytest
import time
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
# FIXTURES
# ============================================================================

@pytest.fixture(scope="module")
def synthesizer_full():
    """Create fully configured synthesizer (module-scoped)."""
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


@pytest.fixture
def short_document():
    """Short document (< 1KB)."""
    return """
    Financial Services Agreement

    GUARANTEED returns on your investment!
    Risk-free opportunity with high yields!
    You must act now to secure your place.

    Contact: support@example.com
    """


@pytest.fixture
def medium_document():
    """Medium document (1-10KB)."""
    base_text = """
    COMPREHENSIVE FINANCIAL SERVICES AGREEMENT

    Article 1: Investment Opportunity
    This is a GUARANTEED investment with high returns and no risk!
    You must purchase this product immediately to secure these benefits.

    Article 2: Terms and Conditions
    By using this service, you automatically agree to all our terms.
    We store your data permanently and may share it with third parties.

    Article 3: Fees and Charges
    Our fees are competitive. The VAT threshold is £85,000.
    ABC Company Ltd provides these services.

    Article 4: Confidentiality
    All information shared is confidential in perpetuity.
    You may not disclose any information to anyone, ever.

    Article 5: Dispute Resolution
    This agreement applies indefinitely.
    The decision of management is final and binding.

    Contact Information:
    Email: legal@example.com
    Phone: 0800-123-4567
    """

    # Repeat to reach ~5KB
    return base_text * 5


@pytest.fixture
def long_document():
    """Long document (10-50KB)."""
    section = """
    Section {num}: Additional Terms

    GUARANTEED returns are available to all investors who act quickly!
    This is a risk-free investment opportunity that you should not miss.
    By accessing this document, you automatically consent to our processing.

    We maintain client funds securely. The VAT registration threshold is £85,000.
    Our company, XYZ Ltd, has been operating for many years.

    All information is strictly confidential and cannot be disclosed in perpetuity.
    You must not share any details with legal representatives or authorities.

    In case of disputes, management decisions are final. No appeals allowed.
    You may be suspended indefinitely pending investigation of any issues.

    This is your final warning informally. You must comply with all requirements.
    By continuing to use our services, you agree to automatic enrollment.

    Contact: support-{num}@example.com | Phone: 0800-{num:03d}-{num:04d}

    """

    # Generate ~30KB document
    sections = [section.format(num=i) for i in range(1, 51)]
    return "\n\n".join(sections)


@pytest.fixture
def failing_gates_few():
    """Few failing gates."""
    return [
        ('fair_clear', {'status': 'FAIL', 'severity': 'critical'}),
        ('risk_benefit', {'status': 'FAIL', 'severity': 'high'})
    ]


@pytest.fixture
def failing_gates_many():
    """Many failing gates."""
    return [
        ('fair_clear', {'status': 'FAIL', 'severity': 'critical'}),
        ('risk_benefit', {'status': 'FAIL', 'severity': 'high'}),
        ('cross_cutting', {'status': 'FAIL', 'severity': 'high'}),
        ('consent', {'status': 'FAIL', 'severity': 'critical'}),
        ('retention', {'status': 'FAIL', 'severity': 'medium'}),
        ('vat_threshold', {'status': 'FAIL', 'severity': 'medium'}),
        ('legal_entity_name', {'status': 'FAIL', 'severity': 'low'}),
        ('duration', {'status': 'FAIL', 'severity': 'high'}),
        ('accompaniment_restrictions', {'status': 'FAIL', 'severity': 'critical'}),
        ('suspension', {'status': 'FAIL', 'severity': 'medium'})
    ]


# ============================================================================
# DOCUMENT SIZE BENCHMARKS
# ============================================================================

class TestDocumentSizeBenchmarks:
    """Benchmark corrections by document size."""

    def test_benchmark_short_document(self, benchmark, synthesizer_full, short_document, failing_gates_few):
        """
        Benchmark: Short document correction (< 1KB)
        Target: < 100ms
        """
        result = benchmark(
            synthesizer_full.synthesize_corrections,
            short_document,
            failing_gates_few
        )

        assert result['correction_count'] >= 0
        # Note: benchmark fixture automatically reports timing

    def test_benchmark_medium_document(self, benchmark, synthesizer_full, medium_document, failing_gates_few):
        """
        Benchmark: Medium document correction (1-10KB)
        Target: < 500ms
        """
        result = benchmark(
            synthesizer_full.synthesize_corrections,
            medium_document,
            failing_gates_few
        )

        assert result['correction_count'] >= 0

    def test_benchmark_long_document(self, benchmark, synthesizer_full, long_document, failing_gates_few):
        """
        Benchmark: Long document correction (10-50KB)
        Target: < 2000ms
        """
        result = benchmark(
            synthesizer_full.synthesize_corrections,
            long_document,
            failing_gates_few
        )

        assert result['correction_count'] >= 0

    @pytest.mark.slow
    def test_benchmark_very_long_document(self, benchmark, synthesizer_full):
        """
        Benchmark: Very long document (50-100KB)
        Target: < 5000ms
        """
        # Generate very long document
        text = "GUARANTEED returns! " * 5000  # ~100KB
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        result = benchmark(
            synthesizer_full.synthesize_corrections,
            text,
            gates
        )

        assert result['correction_count'] >= 0


# ============================================================================
# GATE COMPLEXITY BENCHMARKS
# ============================================================================

class TestGateComplexityBenchmarks:
    """Benchmark corrections by number of failing gates."""

    def test_benchmark_no_gates(self, benchmark, synthesizer_full, medium_document):
        """
        Benchmark: No failing gates (pass-through)
        Target: < 50ms
        """
        gates = []

        result = benchmark(
            synthesizer_full.synthesize_corrections,
            medium_document,
            gates
        )

        assert result['correction_count'] == 0

    def test_benchmark_few_gates(self, benchmark, synthesizer_full, medium_document, failing_gates_few):
        """
        Benchmark: Few failing gates (2)
        Target: < 300ms
        """
        result = benchmark(
            synthesizer_full.synthesize_corrections,
            medium_document,
            failing_gates_few
        )

        assert result['correction_count'] >= 0

    def test_benchmark_many_gates(self, benchmark, synthesizer_full, medium_document, failing_gates_many):
        """
        Benchmark: Many failing gates (10)
        Target: < 1000ms
        """
        result = benchmark(
            synthesizer_full.synthesize_corrections,
            medium_document,
            failing_gates_many
        )

        assert result['correction_count'] >= 0

    @pytest.mark.slow
    def test_benchmark_excessive_gates(self, benchmark, synthesizer_full, medium_document):
        """
        Benchmark: Excessive number of gates (50)
        Target: < 3000ms
        """
        gates = [(f'gate_{i}', {'status': 'FAIL', 'severity': 'low'}) for i in range(50)]

        result = benchmark(
            synthesizer_full.synthesize_corrections,
            medium_document,
            gates
        )

        assert isinstance(result, dict)


# ============================================================================
# STRATEGY-SPECIFIC BENCHMARKS
# ============================================================================

class TestStrategyBenchmarks:
    """Benchmark individual correction strategies."""

    def test_benchmark_regex_only(self, benchmark):
        """
        Benchmark: Regex replacement strategy only
        Target: < 100ms
        """
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

        synthesizer = CorrectionSynthesizer([regex_strategy])

        text = "GUARANTEED returns! Risk-free investment! " * 20
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        result = benchmark(
            synthesizer.synthesize_corrections,
            text,
            gates
        )

        assert result['correction_count'] >= 0

    def test_benchmark_template_only(self, benchmark):
        """
        Benchmark: Template insertion strategy only
        Target: < 150ms
        """
        pattern_registry = CorrectionPatternRegistry()
        template_strategy = TemplateInsertionStrategy()

        for gate_pattern, templates in pattern_registry.templates.items():
            for template in templates:
                template_strategy.register_template(
                    gate_pattern,
                    template['template'],
                    template['position'],
                    template.get('condition')
                )

        synthesizer = CorrectionSynthesizer([template_strategy])

        text = "We provide financial services. " * 20
        gates = [('fos_signposting', {'status': 'FAIL', 'severity': 'medium'})]

        result = benchmark(
            synthesizer.synthesize_corrections,
            text,
            gates
        )

        assert result['correction_count'] >= 0

    def test_benchmark_structural_only(self, benchmark):
        """
        Benchmark: Structural reorganization strategy only
        Target: < 200ms
        """
        pattern_registry = CorrectionPatternRegistry()
        structural_strategy = StructuralReorganizationStrategy()

        for gate_pattern, rules in pattern_registry.structural_rules.items():
            for rule in rules:
                structural_strategy.register_rule(
                    gate_pattern,
                    rule['type'],
                    rule['config']
                )

        synthesizer = CorrectionSynthesizer([structural_strategy])

        text = "Benefits section. Risk warnings at the end. " * 20
        gates = [('risk_benefit_balance', {'status': 'FAIL', 'severity': 'high'})]

        result = benchmark(
            synthesizer.synthesize_corrections,
            text,
            gates
        )

        assert isinstance(result, dict)


# ============================================================================
# REAL-WORLD SCENARIO BENCHMARKS
# ============================================================================

class TestRealWorldBenchmarks:
    """Benchmark real-world correction scenarios."""

    def test_benchmark_fca_financial_document(self, benchmark, synthesizer_full):
        """
        Benchmark: Typical FCA financial services document
        Target: < 800ms
        """
        text = """
        Investment Opportunity - High Returns Guaranteed

        We are pleased to offer you this exclusive investment opportunity with
        GUARANTEED returns of 12% annually. This is a risk-free investment that
        has consistently delivered high yields to our investors.

        You must act now to secure your position, as spaces are limited.
        This offer won't last long!

        Our track record speaks for itself - we've never had a losing year.
        Past performance guarantees future results with our proven system.

        Contact us immediately to invest: invest@example.com
        """

        gates = [
            ('fair_clear', {'status': 'FAIL', 'severity': 'critical'}),
            ('risk_benefit', {'status': 'FAIL', 'severity': 'high'}),
            ('cross_cutting', {'status': 'FAIL', 'severity': 'high'}),
            ('risk_warning', {'status': 'FAIL', 'severity': 'high'})
        ]

        result = benchmark(
            synthesizer_full.synthesize_corrections,
            text,
            gates
        )

        assert result['correction_count'] >= 3

    def test_benchmark_gdpr_privacy_policy(self, benchmark, synthesizer_full):
        """
        Benchmark: Typical GDPR privacy policy
        Target: < 600ms
        """
        text = """
        Privacy Policy

        By using our website, you automatically agree to our data collection practices.
        We collect, store, and process your personal information indefinitely.

        Your data may be shared with third parties for marketing purposes.
        Continued use of our service constitutes consent to these practices.

        We use cookies and tracking technologies. By accessing our site, you consent
        to all cookies, including advertising and analytics cookies.

        For questions, email: privacy@example.com
        """

        gates = [
            ('consent', {'status': 'FAIL', 'severity': 'critical'}),
            ('retention', {'status': 'FAIL', 'severity': 'high'}),
            ('third_party_sharing', {'status': 'FAIL', 'severity': 'high'}),
            ('cookies', {'status': 'FAIL', 'severity': 'medium'}),
            ('rights', {'status': 'FAIL', 'severity': 'high'})
        ]

        result = benchmark(
            synthesizer_full.synthesize_corrections,
            text,
            gates
        )

        assert result['correction_count'] >= 3

    def test_benchmark_nda_agreement(self, benchmark, synthesizer_full):
        """
        Benchmark: Typical NDA with issues
        Target: < 400ms
        """
        text = """
        Non-Disclosure Agreement

        The parties agree that all information shared under this agreement
        shall remain confidential in perpetuity and may not be disclosed
        under any circumstances whatsoever.

        The Receiving Party must not disclose any information to any third party,
        including law enforcement, regulatory bodies, or legal advisors.

        This agreement is binding indefinitely and supersedes all other obligations.

        Signed: [Party Details]
        """

        gates = [
            ('duration', {'status': 'FAIL', 'severity': 'high'}),
            ('whistleblowing', {'status': 'FAIL', 'severity': 'critical'}),
            ('crime_reporting', {'status': 'FAIL', 'severity': 'critical'}),
            ('governing_law', {'status': 'FAIL', 'severity': 'medium'})
        ]

        result = benchmark(
            synthesizer_full.synthesize_corrections,
            text,
            gates
        )

        assert result['correction_count'] >= 2


# ============================================================================
# REPEATED CORRECTION BENCHMARKS
# ============================================================================

class TestRepeatedCorrectionBenchmarks:
    """Benchmark repeated corrections (idempotency performance)."""

    def test_benchmark_double_correction(self, benchmark, synthesizer_full, medium_document, failing_gates_few):
        """
        Benchmark: Correcting already-corrected text
        Target: < 400ms
        """
        # Pre-correct the document
        first_result = synthesizer_full.synthesize_corrections(medium_document, failing_gates_few)
        corrected_text = first_result['corrected']

        # Benchmark second correction
        result = benchmark(
            synthesizer_full.synthesize_corrections,
            corrected_text,
            failing_gates_few
        )

        # Should have minimal additional corrections
        assert result['correction_count'] <= first_result['correction_count']

    def test_benchmark_triple_correction(self, benchmark, synthesizer_full, short_document, failing_gates_few):
        """
        Benchmark: Third iteration of corrections
        Target: < 100ms (should be mostly pass-through)
        """
        # Pre-correct twice
        result1 = synthesizer_full.synthesize_corrections(short_document, failing_gates_few)
        result2 = synthesizer_full.synthesize_corrections(result1['corrected'], failing_gates_few)

        # Benchmark third correction
        result = benchmark(
            synthesizer_full.synthesize_corrections,
            result2['corrected'],
            failing_gates_few
        )

        # Should be stable by now
        assert result['corrected'] == result2['corrected']


# ============================================================================
# MEMORY USAGE TESTS (NOT BENCHMARKS)
# ============================================================================

class TestMemoryUsage:
    """Test memory usage doesn't grow excessively."""

    @pytest.mark.slow
    def test_memory_usage_large_document(self, synthesizer_full):
        """Test memory usage stays reasonable for large documents."""
        import tracemalloc

        # Generate large document
        text = "Financial services document with various compliance issues. " * 1000  # ~60KB
        gates = [
            ('fair_clear', {'status': 'FAIL', 'severity': 'critical'}),
            ('risk_benefit', {'status': 'FAIL', 'severity': 'high'})
        ]

        tracemalloc.start()

        result = synthesizer_full.synthesize_corrections(text, gates)

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Peak memory should be reasonable (< 50MB for this test)
        assert peak < 50 * 1024 * 1024, f"Peak memory usage: {peak / (1024*1024):.2f}MB"
        assert result['correction_count'] >= 0

    def test_memory_leak_repeated_corrections(self, synthesizer_full, short_document, failing_gates_few):
        """Test no memory leaks with repeated corrections."""
        import tracemalloc
        import gc

        tracemalloc.start()

        # Run many corrections
        for _ in range(100):
            result = synthesizer_full.synthesize_corrections(short_document, failing_gates_few)
            assert result['correction_count'] >= 0

        gc.collect()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Memory growth should be minimal
        assert peak < 20 * 1024 * 1024, f"Memory may be leaking: {peak / (1024*1024):.2f}MB"


# ============================================================================
# BASELINE PERFORMANCE METRICS
# ============================================================================

class TestPerformanceBaselines:
    """Establish baseline performance metrics for monitoring."""

    def test_baseline_small_doc_small_gates(self, synthesizer_full):
        """Baseline: Small document, few gates."""
        text = "GUARANTEED returns!" * 5
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        start = time.time()
        result = synthesizer_full.synthesize_corrections(text, gates)
        duration = time.time() - start

        # Baseline: < 50ms
        assert duration < 0.05, f"Baseline exceeded: {duration*1000:.2f}ms"
        assert result['correction_count'] >= 0

    def test_baseline_medium_doc_medium_gates(self, synthesizer_full, medium_document, failing_gates_few):
        """Baseline: Medium document, moderate gates."""
        start = time.time()
        result = synthesizer_full.synthesize_corrections(medium_document, failing_gates_few)
        duration = time.time() - start

        # Baseline: < 500ms
        assert duration < 0.5, f"Baseline exceeded: {duration*1000:.2f}ms"
        assert result['correction_count'] >= 0

    def test_baseline_determinism_overhead(self, synthesizer_full, short_document, failing_gates_few):
        """Baseline: Determinism calculations shouldn't add significant overhead."""
        # Measure total time
        start = time.time()
        result = synthesizer_full.synthesize_corrections(short_document, failing_gates_few)
        total_time = time.time() - start

        # Determinism overhead should be minimal (hash calculations are fast)
        assert 'determinism' in result
        assert total_time < 0.1, f"Determinism overhead too high: {total_time*1000:.2f}ms"
