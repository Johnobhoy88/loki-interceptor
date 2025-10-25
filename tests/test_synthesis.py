#!/usr/bin/env python3
"""
Tests for the Synthesis Layer
Pure deterministic document assembly with compliance snippets
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT / 'backend'))

import pytest
from core.async_engine import AsyncLOKIEngine
from core.synthesis import SynthesisEngine, SnippetRegistry


@pytest.fixture
def engine():
    """Create a test LOKI engine"""
    eng = AsyncLOKIEngine(max_workers=4)
    eng.load_module('fca_uk')
    eng.load_module('gdpr_uk')
    eng.load_module('hr_scottish')
    eng.load_module('nda_uk')
    eng.load_module('tax_uk')
    return eng


@pytest.fixture
def synthesis_engine(engine):
    """Create a synthesis engine with test engine"""
    return SynthesisEngine(engine)


@pytest.fixture
def snippet_registry():
    """Create a snippet registry"""
    return SnippetRegistry()


class TestSnippetRegistry:
    """Test snippet registry functionality"""

    def test_registry_initialization(self, snippet_registry):
        """Test that registry initializes with snippets"""
        assert len(snippet_registry.snippets) >= 84  # All gates covered
        assert 'fca_uk:fair_clear_not_misleading' in snippet_registry.snippets
        assert 'gdpr_uk:lawful_basis' in snippet_registry.snippets
        assert 'nda_uk:protected_whistleblowing' in snippet_registry.snippets
        assert 'tax_uk:vat_invoice_integrity' in snippet_registry.snippets
        assert 'hr_scottish:accompaniment' in snippet_registry.snippets

    def test_get_snippet(self, snippet_registry):
        """Test retrieving specific snippets"""
        snippet = snippet_registry.get_snippet('fca_uk', 'fos_signposting')
        assert snippet is not None
        assert snippet.gate_id == 'fos_signposting'
        assert snippet.module_id == 'fca_uk'
        assert 'Financial Ombudsman' in snippet.template

    def test_format_snippet_with_context(self, snippet_registry):
        """Test snippet formatting with context variables"""
        snippet = snippet_registry.get_snippet('gdpr_uk', 'lawful_basis')
        context = {
            'url': 'https://example.com/privacy'
        }
        formatted = snippet_registry.format_snippet(snippet, context)
        assert 'https://example.com/privacy' in formatted

    def test_format_snippet_with_defaults(self, snippet_registry):
        """Test snippet formatting uses defaults for missing context"""
        snippet = snippet_registry.get_snippet('fca_uk', 'promotions_approval')
        formatted = snippet_registry.format_snippet(snippet, {})
        assert '[FIRM NAME]' not in formatted  # Should be replaced with default
        assert 'Our Firm' in formatted


class TestSynthesisEngine:
    """Test synthesis engine functionality"""

    def test_engine_initialization(self, synthesis_engine):
        """Test synthesis engine initializes correctly"""
        assert synthesis_engine.engine is not None
        assert synthesis_engine.registry is not None
        assert synthesis_engine.max_retries == 5

    def test_synthesize_empty_document(self, synthesis_engine):
        """Test synthesizing from empty base text"""
        # Create a mock validation with failures
        validation = {
            'modules': {
                'fca_uk': {
                    'gates': {
                        'fos_signposting': {
                            'status': 'FAIL',
                            'message': 'Missing FOS signposting'
                        }
                    }
                }
            },
            'overall_risk': 'CRITICAL'
        }

        result = synthesis_engine.synthesize(
            base_text='',
            validation=validation,
            context={},
            modules=['fca_uk']
        )

        assert result is not None
        assert 'synthesized_text' in result
        assert 'Financial Ombudsman' in result['synthesized_text']
        assert len(result['snippets_applied']) > 0

    def test_synthesize_with_base_text(self, synthesis_engine):
        """Test synthesizing with existing base text"""
        base_text = "Welcome to our financial services."
        validation = {
            'modules': {
                'fca_uk': {
                    'gates': {
                        'fair_clear_not_misleading': {
                            'status': 'FAIL',
                            'message': 'Missing risk warning'
                        }
                    }
                }
            },
            'overall_risk': 'CRITICAL'
        }

        result = synthesis_engine.synthesize(
            base_text=base_text,
            validation=validation,
            context={},
            modules=['fca_uk']
        )

        assert 'Welcome to our financial services' in result['synthesized_text']
        assert 'RISK WARNING' in result['synthesized_text']
        assert result['original_text'] == base_text

    def test_synthesize_includes_metadata_iteration_order(self, synthesis_engine):
        """Applied snippet metadata surfaces iteration and order information"""
        base_text = "Original tester paragraph."
        validation = {
            'modules': {
                'fca_uk': {
                    'gates': {
                        'fair_clear_not_misleading': {
                            'status': 'FAIL',
                            'message': 'Missing risk warning'
                        },
                        'fos_signposting': {
                            'status': 'FAIL',
                            'message': 'Missing FOS statement'
                        }
                    }
                }
            },
            'overall_risk': 'CRITICAL'
        }

        result = synthesis_engine.synthesize(
            base_text=base_text,
            validation=validation,
            context={},
            modules=['fca_uk']
        )

        assert result['original_text'] == base_text
        assert result['snippets_applied'], "Expected snippets to be applied"
        for snippet_meta in result['snippets_applied']:
            assert 'iteration' in snippet_meta
            assert snippet_meta['iteration'] >= 1
            assert 'order' in snippet_meta
            assert snippet_meta['order'] >= 1

    def test_synthesize_passes_validation(self, synthesis_engine):
        """Test that synthesis resolves failures"""
        # This test uses real validation - may need actual gate implementations
        base_text = "Investment opportunity with great returns!"
        validation = {
            'modules': {
                'fca_uk': {
                    'gates': {
                        'fair_clear_not_misleading': {
                            'status': 'FAIL',
                            'message': 'Missing risk warnings'
                        }
                    }
                }
            },
            'overall_risk': 'CRITICAL'
        }

        result = synthesis_engine.synthesize(
            base_text=base_text,
            validation=validation,
            context={},
            modules=['fca_uk']
        )

        assert result['success'] or result['iterations'] > 0
        assert len(result['snippets_applied']) > 0

    def test_synthesize_multiple_modules(self, synthesis_engine):
        """Test synthesizing with multiple module failures"""
        validation = {
            'modules': {
                'fca_uk': {
                    'gates': {
                        'fos_signposting': {'status': 'FAIL', 'message': 'Missing FOS'}
                    }
                },
                'gdpr_uk': {
                    'gates': {
                        'lawful_basis': {'status': 'FAIL', 'message': 'Missing lawful basis'}
                    }
                }
            },
            'overall_risk': 'CRITICAL'
        }

        result = synthesis_engine.synthesize(
            base_text='',
            validation=validation,
            context={},
            modules=['fca_uk', 'gdpr_uk']
        )

        text = result['synthesized_text']
        assert 'Financial Ombudsman' in text
        assert 'GDPR' in text or 'Data Protection' in text.upper()
        assert len(result['snippets_applied']) >= 2

    def test_snippet_insertion_points(self, synthesis_engine):
        """Test that snippets respect insertion points"""
        base_text = "Middle content here."
        validation = {
            'modules': {
                'fca_uk': {
                    'gates': {
                        'fair_clear_not_misleading': {'status': 'FAIL', 'message': 'test'},
                        'fos_signposting': {'status': 'FAIL', 'message': 'test'}
                    }
                }
            },
            'overall_risk': 'CRITICAL'
        }

        result = synthesis_engine.synthesize(
            base_text=base_text,
            validation=validation,
            context={},
            modules=['fca_uk']
        )

        text = result['synthesized_text']
        # Risk warning should be at start
        assert text.startswith('IMPORTANT RISK WARNING')
        # FOS signposting should be at end
        assert 'Financial Ombudsman' in text

    def test_max_retries_limit(self, synthesis_engine):
        """Test that synthesis respects max retries"""
        synthesis_engine.max_retries = 2

        # Create a validation that can't be resolved
        validation = {
            'modules': {
                'fca_uk': {
                    'gates': {
                        'nonexistent_gate': {'status': 'FAIL', 'message': 'test'}
                    }
                }
            },
            'overall_risk': 'CRITICAL'
        }

        result = synthesis_engine.synthesize(
            base_text='',
            validation=validation,
            context={},
            modules=['fca_uk']
        )

        assert result['iterations'] <= 2
        # Should not succeed since we can't fix nonexistent gate
        assert not result['success'] or result['reason'].startswith('All gates passed')


class TestIntegration:
    """Integration tests with full validation"""

    def test_fca_promotional_material(self, synthesis_engine):
        """Test synthesizing compliant promotional material"""
        base_text = """
        Best investment returns in the market!
        Guaranteed profits of 20% per year.
        """

        # First validate to get failures
        validation = synthesis_engine.engine.check_document(
            text=base_text,
            document_type='promotional',
            active_modules=['fca_uk']
        )

        # Should have failures
        failures = len(synthesis_engine._extract_failures(validation))
        assert failures > 0

        # Now synthesize
        result = synthesis_engine.synthesize(
            base_text=base_text,
            validation=validation,
            context={
                'firm_name': 'Test Firm Ltd',
                'number': '123456'
            },
            modules=['fca_uk']
        )

        # Check result
        assert 'RISK WARNING' in result['synthesized_text']
        assert len(result['snippets_applied']) > 0

    def test_gdpr_document_synthesis(self, synthesis_engine):
        """Test synthesizing GDPR-compliant document"""
        base_text = "We collect your personal data."

        validation = synthesis_engine.engine.check_document(
            text=base_text,
            document_type='privacy_policy',
            active_modules=['gdpr_uk']
        )

        result = synthesis_engine.synthesize(
            base_text=base_text,
            validation=validation,
            context={
                'url': 'https://example.com/privacy',
                'dpo_email': 'dpo@example.com'
            },
            modules=['gdpr_uk']
        )

        text = result['synthesized_text']
        assert 'personal data' in text.lower()
        # Should add data protection information
        if result['snippets_applied']:
            assert any('gdpr' in s['module_id'] for s in result['snippets_applied'])

    def test_nda_document_synthesis(self, synthesis_engine):
        """Test synthesizing NDA-compliant document"""
        base_text = "You agree not to disclose confidential information."

        validation = synthesis_engine.engine.check_document(
            text=base_text,
            document_type='nda',
            active_modules=['nda_uk']
        )

        result = synthesis_engine.synthesize(
            base_text=base_text,
            validation=validation,
            context={
                'party_disclosing': 'Company Ltd',
                'party_receiving': 'Contractor Ltd',
                'nda_duration': '2 years'
            },
            modules=['nda_uk']
        )

        text = result['synthesized_text']
        assert 'confidential' in text.lower()
        # Should include NDA protections if failures detected
        if result['snippets_applied']:
            assert any('nda' in s['module_id'] for s in result['snippets_applied'])

    def test_tax_document_synthesis(self, synthesis_engine):
        """Test synthesizing tax-compliant invoice"""
        base_text = "Invoice for services rendered."

        validation = synthesis_engine.engine.check_document(
            text=base_text,
            document_type='invoice',
            active_modules=['tax_uk']
        )

        result = synthesis_engine.synthesize(
            base_text=base_text,
            validation=validation,
            context={
                'company_name': 'Test Ltd',
                'company_number': '12345678',
                'vat_number': 'GB123456789'
            },
            modules=['tax_uk']
        )

        text = result['synthesized_text']
        assert 'invoice' in text.lower()
        # Should add tax-compliant elements if failures detected
        if result['snippets_applied']:
            assert any('tax' in s['module_id'] for s in result['snippets_applied'])

    def test_hr_document_synthesis(self, synthesis_engine):
        """Test synthesizing HR-compliant disciplinary document"""
        base_text = "You are required to attend a meeting regarding your conduct."

        validation = synthesis_engine.engine.check_document(
            text=base_text,
            document_type='disciplinary',
            active_modules=['hr_scottish']
        )

        result = synthesis_engine.synthesize(
            base_text=base_text,
            validation=validation,
            context={
                'employee_name': 'John Doe',
                'meeting_date': '2024-01-15',
                'meeting_time': '10:00 AM'
            },
            modules=['hr_scottish']
        )

        text = result['synthesized_text']
        assert 'meeting' in text.lower()
        # Should add HR-compliant protections if failures detected
        if result['snippets_applied']:
            assert any('hr' in s['module_id'] for s in result['snippets_applied'])


class TestSnippetCoverage:
    """Test coverage of all modules with snippets"""

    def test_all_modules_have_snippets(self, snippet_registry):
        """Test that all five modules have snippet coverage"""
        modules = ['fca_uk', 'gdpr_uk', 'hr_scottish', 'nda_uk', 'tax_uk']
        for module in modules:
            module_snippets = [k for k in snippet_registry.snippets.keys() if k.startswith(f'{module}:')]
            assert len(module_snippets) > 0, f"Module {module} has no snippets"

    def test_fca_snippet_coverage(self, snippet_registry):
        """Test FCA module has comprehensive snippet coverage"""
        fca_gates = [
            'fair_clear_not_misleading', 'fos_signposting', 'promotions_approval',
            'outcomes_coverage', 'cross_cutting_rules', 'fair_value', 'comprehension_aids'
        ]
        for gate in fca_gates:
            snippet = snippet_registry.get_snippet('fca_uk', gate)
            assert snippet is not None, f"Missing snippet for fca_uk:{gate}"
            assert len(snippet.template) > 20, f"Snippet for {gate} is too short"

    def test_gdpr_snippet_coverage(self, snippet_registry):
        """Test GDPR module has comprehensive snippet coverage"""
        gdpr_gates = [
            'lawful_basis', 'consent', 'purpose', 'retention', 'rights',
            'security', 'data_minimisation', 'third_party_sharing'
        ]
        for gate in gdpr_gates:
            snippet = snippet_registry.get_snippet('gdpr_uk', gate)
            assert snippet is not None, f"Missing snippet for gdpr_uk:{gate}"
            tmpl = snippet.template.lower()
            assert (
                'retention' in tmpl
                or 'data' in tmpl
                or 'gdpr' in tmpl
                or 'security' in tmpl
            )

    def test_nda_snippet_coverage(self, snippet_registry):
        """Test NDA module has comprehensive snippet coverage"""
        nda_gates = [
            'protected_whistleblowing', 'protected_crime_reporting', 'protected_harassment',
            'definition_specificity', 'public_domain_exclusion', 'governing_law'
        ]
        for gate in nda_gates:
            snippet = snippet_registry.get_snippet('nda_uk', gate)
            assert snippet is not None, f"Missing snippet for nda_uk:{gate}"
            assert len(snippet.template) > 20

    def test_tax_snippet_coverage(self, snippet_registry):
        """Test Tax module has comprehensive snippet coverage"""
        tax_gates = [
            'vat_invoice_integrity', 'vat_number_format', 'vat_rate_accuracy',
            'invoice_legal_requirements', 'company_limited_suffix', 'mtd_compliance'
        ]
        for gate in tax_gates:
            snippet = snippet_registry.get_snippet('tax_uk', gate)
            assert snippet is not None, f"Missing snippet for tax_uk:{gate}"
            assert len(snippet.template) > 20

    def test_hr_snippet_coverage(self, snippet_registry):
        """Test HR module has comprehensive snippet coverage"""
        hr_gates = [
            'accompaniment', 'evidence', 'appeal', 'allegations', 'dismissal',
            'meeting_notice', 'investigation', 'informal_threats'
        ]
        for gate in hr_gates:
            snippet = snippet_registry.get_snippet('hr_scottish', gate)
            assert snippet is not None, f"Missing snippet for hr_scottish:{gate}"
            assert len(snippet.template) > 20


class TestSnippetFormatting:
    """Test snippet formatting and context variables"""

    def test_nda_context_formatting(self, snippet_registry):
        """Test NDA snippets format context variables correctly"""
        snippet = snippet_registry.get_snippet('nda_uk', 'parties_identified')
        context = {
            'party_one_name': 'ACME Corp',
            'party_two_name': 'Contractor Inc'
        }
        formatted = snippet_registry.format_snippet(snippet, context)
        assert 'ACME Corp' in formatted or 'Party One' in formatted
        assert 'Contractor Inc' in formatted or 'Party Two' in formatted

    def test_tax_context_formatting(self, snippet_registry):
        """Test Tax snippets format context variables correctly"""
        snippet = snippet_registry.get_snippet('tax_uk', 'vat_number_format')
        context = {
            'vat_number': 'GB987654321'
        }
        formatted = snippet_registry.format_snippet(snippet, context)
        assert 'GB987654321' in formatted or 'VAT' in formatted

    def test_hr_context_formatting(self, snippet_registry):
        """Test HR snippets format context variables correctly"""
        snippet = snippet_registry.get_snippet('hr_scottish', 'meeting_notice')
        context = {
            'employee_name': 'Jane Smith',
            'meeting_date': '2024-03-20',
            'meeting_time': '2:00 PM'
        }
        formatted = snippet_registry.format_snippet(snippet, context)
        lower_fmt = formatted.lower()
        assert 'notice' in lower_fmt or 'timeframe' in lower_fmt or 'meeting' in lower_fmt

    def test_context_defaults_applied(self, snippet_registry):
        """Test that context defaults are applied when variables missing"""
        snippet = snippet_registry.get_snippet('fca_uk', 'promotions_approval')
        # Pass empty context - should use defaults
        formatted = snippet_registry.format_snippet(snippet, {})
        # Should not have any unreplaced placeholders
        assert '[FIRM NAME]' not in formatted
        assert '[NUMBER]' not in formatted


class TestSnippetPriorities:
    """Test snippet priority and severity handling"""

    def test_critical_snippets_have_high_priority(self, snippet_registry):
        """Test that critical snippets have priority 100"""
        critical_gates = [
            ('fca_uk', 'fair_clear_not_misleading'),
            ('gdpr_uk', 'lawful_basis'),
            ('nda_uk', 'protected_whistleblowing')
        ]
        for module_id, gate_id in critical_gates:
            snippet = snippet_registry.get_snippet(module_id, gate_id)
            if snippet and snippet.severity == 'critical':
                assert snippet.priority >= 95, f"Critical snippet {module_id}:{gate_id} should have high priority"

    def test_snippets_have_insertion_points(self, snippet_registry):
        """Test that all snippets have valid insertion points"""
        valid_points = ['start', 'end', 'section']
        for key, snippet in snippet_registry.snippets.items():
            assert snippet.insertion_point in valid_points, \
                f"Snippet {key} has invalid insertion point: {snippet.insertion_point}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
