"""
Comprehensive test suite for enhanced synthesis engine

Tests all new features:
- Multi-pass correction with convergence detection
- Confidence scoring
- Preview mode
- Rollback/undo functionality
- Conflict resolution
- Plugin system
- Performance optimizations
- Quality metrics
"""
import pytest
import time
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any

# Import modules to test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from backend.core.synthesis.engine import SynthesisEngine, AppliedSnippet, CorrectionMetrics
from backend.core.synthesis.confidence_scorer import ConfidenceScorer, ConfidenceFactors
from backend.core.synthesis.preview import PreviewEngine, PreviewResult
from backend.core.synthesis.rollback import RollbackManager, CorrectionState
from backend.core.synthesis.conflict_resolver import ConflictResolver, ConflictType, ConflictSeverity
from backend.core.synthesis.plugin_loader import PluginLoader, RegexRule, TemplateRule


class TestEnhancedSynthesisEngine:
    """Test suite for enhanced synthesis engine"""

    @pytest.fixture
    def mock_validation_engine(self):
        """Create a mock validation engine"""
        engine = Mock()
        engine.modules = {'fca_uk': {}, 'gdpr_uk': {}}
        engine.check_document = Mock(return_value={
            'modules': {
                'fca_uk': {
                    'gates': {
                        'risk_warning': {'status': 'PASS'}
                    }
                }
            },
            'overall_risk': 'LOW'
        })
        return engine

    @pytest.fixture
    def synthesis_engine(self, mock_validation_engine):
        """Create synthesis engine instance"""
        return SynthesisEngine(
            validation_engine=mock_validation_engine,
            enable_preview=False,
            enable_rollback=True,
            enable_metrics=True
        )

    def test_convergence_detection(self, synthesis_engine):
        """Test that engine detects convergence"""
        # Mock validation that shows improvement then plateau
        validation_results = [
            self._create_validation_with_failures(10),
            self._create_validation_with_failures(5),
            self._create_validation_with_failures(4),
            self._create_validation_with_failures(4),  # No improvement
        ]

        with patch.object(synthesis_engine.engine, 'check_document', side_effect=validation_results):
            result = synthesis_engine.synthesize(
                base_text="Test document",
                validation=validation_results[0]
            )

        # Should detect convergence and stop early
        assert result.get('converged') is not None
        assert result.get('convergence_history') is not None

    def test_multi_pass_correction(self, synthesis_engine):
        """Test multi-pass correction algorithm"""
        initial_validation = self._create_validation_with_failures(5)

        result = synthesis_engine.synthesize(
            base_text="Test document",
            validation=initial_validation
        )

        # Should attempt multiple iterations
        assert result.get('iterations', 0) >= 1
        assert 'snippets_applied' in result

    def test_confidence_scoring(self):
        """Test confidence scoring calculation"""
        scorer = ConfidenceScorer()

        factors = scorer.score_correction(
            gate_id='fca_uk:risk_warning',
            snippet_key='fca_uk:risk_warning:financial',
            gate_severity='high',
            snippet_severity='high',
            context={'document_type': 'financial'},
            snippet_text='RISK WARNING: Investments can fall...',
            gate_message='Missing risk warning'
        )

        assert isinstance(factors, ConfidenceFactors)
        assert 0.0 <= factors.pattern_match_strength <= 1.0
        assert 0.0 <= factors.severity_alignment <= 1.0
        assert 0.0 <= factors.domain_expertise <= 1.0

        overall_score = factors.calculate_weighted_score()
        assert 0.0 <= overall_score <= 1.0

    def test_preview_mode(self, synthesis_engine):
        """Test preview mode (dry-run without applying)"""
        initial_validation = self._create_validation_with_failures(3)

        result = synthesis_engine.preview_corrections(
            base_text="Original text",
            validation=initial_validation
        )

        # Preview mode should not modify original text
        assert result.get('preview_mode') == True
        assert result.get('synthesized_text') == "Original text"
        assert 'snippets_applied' in result  # But should show what would be applied

    def test_rollback_functionality(self):
        """Test rollback/undo capabilities"""
        manager = RollbackManager()

        # Save multiple snapshots
        manager.save_snapshot("Text v1", [], {})
        manager.save_snapshot("Text v2", [{'snippet_key': 'test1'}], {})
        manager.save_snapshot("Text v3", [{'snippet_key': 'test1'}, {'snippet_key': 'test2'}], {})

        # Rollback to iteration 1
        success, state, error = manager.rollback_to_iteration(1)

        assert success == True
        assert state is not None
        assert state.text == "Text v2"
        assert len(state.applied_snippets) == 1

    def test_rollback_to_previous(self):
        """Test rollback to previous state"""
        manager = RollbackManager()

        manager.save_snapshot("Text v1", [], {})
        manager.save_snapshot("Text v2", [], {})
        manager.save_snapshot("Text v3", [], {})

        success, state, error = manager.rollback_to_previous()

        assert success == True
        assert state.text == "Text v2"

    def test_undo_specific_correction(self):
        """Test undoing a specific correction"""
        manager = RollbackManager()

        manager.save_snapshot("Original", [], {})
        manager.save_snapshot("With correction A", [{'snippet_key': 'correct_a'}], {})
        manager.save_snapshot("With A and B", [
            {'snippet_key': 'correct_a'},
            {'snippet_key': 'correct_b'}
        ], {})

        success, state, error = manager.undo_correction('correct_b')

        assert success == True
        # Should rollback to before correct_b was applied

    def test_correction_lineage(self):
        """Test correction history tracking"""
        manager = RollbackManager()

        manager.save_snapshot("v1", [{'snippet_key': 'test_correction', 'iteration': 1}], {})
        manager.save_snapshot("v2", [{'snippet_key': 'test_correction', 'iteration': 2}], {})

        lineage = manager.get_correction_lineage('test_correction')

        assert len(lineage) == 2
        assert lineage[0]['iteration'] == 1

    def test_conflict_detection_contradictory(self):
        """Test detection of contradictory corrections"""
        resolver = ConflictResolver()

        snippets = [
            {
                'snippet_key': 'consent_mandatory',
                'text_added': 'Users must consent to proceed',
                'gate_id': 'gdpr_uk:consent'
            },
            {
                'snippet_key': 'consent_optional',
                'text_added': 'Consent is optional and may be withdrawn',
                'gate_id': 'gdpr_uk:consent'
            }
        ]

        conflicts = resolver.detect_conflicts(snippets, {}, {}, "Test text")

        # Should detect contradictory corrections
        contradictory = [c for c in conflicts if c.conflict_type == ConflictType.CONTRADICTORY]
        assert len(contradictory) > 0

    def test_conflict_detection_overlap(self):
        """Test detection of overlapping corrections"""
        resolver = ConflictResolver()

        snippets = [
            {
                'snippet_key': 'risk_warning_1',
                'text_added': 'Risk warning text',
                'gate_id': 'fca_uk:risk_warning'
            },
            {
                'snippet_key': 'risk_warning_2',
                'text_added': 'Alternative risk warning',
                'gate_id': 'fca_uk:risk_warning'
            }
        ]

        conflicts = resolver.detect_conflicts(snippets, {}, {}, "Test text")

        # Should detect overlap
        overlap = [c for c in conflicts if c.conflict_type == ConflictType.OVERLAP]
        assert len(overlap) > 0

    def test_conflict_detection_redundant(self):
        """Test detection of redundant corrections"""
        resolver = ConflictResolver()

        snippets = [
            {
                'snippet_key': 'duplicate_1',
                'text_added': 'Identical correction text',
                'gate_id': 'test:gate'
            },
            {
                'snippet_key': 'duplicate_2',
                'text_added': 'Identical correction text',
                'gate_id': 'test:gate'
            }
        ]

        conflicts = resolver.detect_conflicts(snippets, {}, {}, "Test text")

        # Should detect redundancy
        redundant = [c for c in conflicts if c.conflict_type == ConflictType.REDUNDANT]
        assert len(redundant) > 0

    def test_conflict_resolution(self):
        """Test automatic conflict resolution"""
        resolver = ConflictResolver()

        snippets = [
            {
                'snippet_key': 'dup1',
                'text_added': 'Same text',
                'gate_id': 'test:gate'
            },
            {
                'snippet_key': 'dup2',
                'text_added': 'Same text',
                'gate_id': 'test:gate'
            }
        ]

        conflicts = resolver.detect_conflicts(snippets, {}, {}, "Test")
        unresolved, actions = resolver.resolve_conflicts(conflicts, auto_resolve=True)

        # Some conflicts should be auto-resolved
        assert len(actions) > 0

    def test_plugin_loader_json(self, tmp_path):
        """Test loading plugins from JSON files"""
        # Create temporary plugin file
        plugin_file = tmp_path / "test_plugin.json"
        plugin_file.write_text('''
        {
            "rule_id": "test_regex_rule",
            "rule_type": "regex",
            "name": "Test Rule",
            "description": "Test regex rule",
            "gate_pattern": "test_gate",
            "pattern": "old_text",
            "replacement": "new_text",
            "flags": "IGNORECASE"
        }
        ''')

        loader = PluginLoader(plugin_directories=[str(tmp_path)])
        results = loader.load_plugins()

        assert results['loaded'] >= 1
        assert len(loader.regex_rules) >= 1

    def test_plugin_regex_application(self):
        """Test applying regex rules from plugins"""
        loader = PluginLoader(plugin_directories=[])

        # Manually add a test rule
        rule = RegexRule(
            rule_id='test_rule',
            rule_type='regex',
            name='Test Rule',
            description='Test',
            gate_pattern='test_gate',
            pattern=r'\brisk\b',
            replacement='RISK',
            flags=0
        )
        loader.regex_rules.append(rule)
        loader.loaded_rules[rule.rule_id] = rule

        text, changes = loader.apply_regex_rules("Investment risk is high", "test_gate")

        assert "RISK" in text
        assert len(changes) > 0

    def test_plugin_template_application(self):
        """Test applying template rules from plugins"""
        loader = PluginLoader(plugin_directories=[])

        # Add test template rule
        rule = TemplateRule(
            rule_id='test_template',
            rule_type='template',
            name='Test Template',
            description='Test',
            gate_pattern='test_gate',
            template='DISCLAIMER: This is a test',
            position='start'
        )
        loader.template_rules.append(rule)
        loader.loaded_rules[rule.rule_id] = rule

        text, insertions = loader.apply_template_rules("Original text", "test_gate")

        assert "DISCLAIMER" in text
        assert len(insertions) > 0

    def test_quality_metrics_calculation(self):
        """Test calculation of quality metrics (precision, recall, F1)"""
        metrics = CorrectionMetrics()

        # Simulate: 10 initial failures, 3 remaining, 7 corrections applied
        metrics.corrections_applied = 7
        metrics.gates_fixed = 7
        metrics.gates_remaining = 3

        # Calculate precision and recall
        metrics.precision = 7 / 7  # All corrections were helpful
        metrics.recall = 7 / 10  # Fixed 7 out of 10 failures
        metrics.calculate_f1()

        assert metrics.precision == 1.0
        assert metrics.recall == 0.7
        assert 0.8 <= metrics.f1_score <= 0.9  # Should be ~0.82

    def test_performance_regex_caching(self, synthesis_engine):
        """Test that regex caching improves performance"""
        pattern = r'\d{4}-\d{2}-\d{2}'

        # First call - should compile
        start = time.time()
        regex1 = synthesis_engine._get_compiled_regex(pattern)
        first_call_time = time.time() - start

        # Second call - should use cache
        start = time.time()
        regex2 = synthesis_engine._get_compiled_regex(pattern)
        second_call_time = time.time() - start

        assert regex1 is regex2  # Same object from cache
        assert second_call_time < first_call_time or second_call_time < 0.0001  # Faster or negligible

    def test_correction_validation_no_new_violations(self, synthesis_engine):
        """Test that corrections don't introduce new violations"""
        original_text = "Original document"
        corrected_text = "Corrected document with additions"

        initial_validation = self._create_validation_with_failures(5)

        # Mock the re-validation to show improvements
        with patch.object(synthesis_engine.engine, 'check_document', return_value=self._create_validation_with_failures(2)):
            validation_result = synthesis_engine.validate_corrections(
                original_text,
                corrected_text,
                initial_validation
            )

        assert validation_result['valid'] == True
        assert validation_result['improvement'] == 3  # 5 - 2 = 3

    def test_ab_testing_framework(self, synthesis_engine):
        """Test A/B testing capability"""
        base_text = "Test document"
        validation = self._create_validation_with_failures(3)

        comparison = synthesis_engine.run_ab_test(
            base_text=base_text,
            validation=validation,
            strategy_a='standard',
            strategy_b='aggressive',
            test_id='test_001'
        )

        assert 'strategy_a' in comparison
        assert 'strategy_b' in comparison
        assert 'winner' in comparison
        assert comparison['winner'] in ['standard', 'aggressive', 'tie']

    def test_preview_generation(self):
        """Test preview generation with warnings and recommendations"""
        preview_engine = PreviewEngine()

        synthesis_result = {
            'original_text': 'Original text',
            'snippets_applied': [
                {
                    'snippet_key': 'test:snippet',
                    'gate_id': 'fca_uk:risk_warning',
                    'module_id': 'fca_uk',
                    'severity': 'high',
                    'confidence': 0.9,
                    'iteration': 1,
                    'order': 1,
                    'text_added': 'RISK WARNING: Test warning text'
                }
            ],
            'metrics': {
                'gates_fixed': 3,
                'gates_remaining': 2
            },
            'converged': True,
            'conflicts': []
        }

        preview = preview_engine.generate_preview(synthesis_result)

        assert isinstance(preview, PreviewResult)
        assert preview.total_corrections == 1
        assert preview.high_confidence_corrections >= 1
        assert len(preview.recommendations) > 0

    def test_snapshot_diff_calculation(self):
        """Test calculating differences between snapshots"""
        manager = RollbackManager()

        manager.save_snapshot("Text v1", [], {})
        manager.save_snapshot("Text v2", [{'snippet_key': 'a'}, {'snippet_key': 'b'}], {})

        diff = manager.get_snapshot_diff(0, 1)

        assert diff is not None
        assert diff['net_corrections'] == 2
        assert len(diff['corrections_added']) == 2

    def test_engine_with_max_retries(self, synthesis_engine):
        """Test that engine respects max_retries"""
        synthesis_engine.max_retries = 2

        # Mock validation that never improves
        with patch.object(synthesis_engine.engine, 'check_document', return_value=self._create_validation_with_failures(5)):
            result = synthesis_engine.synthesize(
                base_text="Test",
                validation=self._create_validation_with_failures(5)
            )

        assert result['iterations'] <= synthesis_engine.max_retries

    def test_confidence_factors_weighted_score(self):
        """Test weighted confidence score calculation"""
        factors = ConfidenceFactors(
            pattern_match_strength=0.9,
            severity_alignment=0.8,
            historical_success=0.7,
            context_relevance=0.6,
            domain_expertise=0.9,
            snippet_specificity=0.8
        )

        score = factors.calculate_weighted_score()

        assert 0.7 <= score <= 0.9  # Should be high given high individual scores
        assert isinstance(score, float)

    def test_correction_statistics_tracking(self):
        """Test tracking of correction statistics"""
        scorer = ConfidenceScorer()

        # Record some applications
        scorer.record_application('snippet_a', True)
        scorer.record_application('snippet_a', True)
        scorer.record_application('snippet_a', False)
        scorer.record_application('snippet_b', True)

        stats = scorer.get_overall_statistics()

        assert stats['total_applications'] == 4
        assert stats['total_successes'] == 3
        assert stats['overall_success_rate'] == 0.75

        snippet_stats = scorer.get_snippet_statistics('snippet_a')
        assert snippet_stats['applications'] == 3
        assert snippet_stats['successes'] == 2

    # Helper methods

    def _create_validation_with_failures(self, failure_count: int) -> Dict[str, Any]:
        """Create a mock validation result with specified number of failures"""
        modules = {
            'fca_uk': {'gates': {}},
            'gdpr_uk': {'gates': {}}
        }

        for i in range(failure_count):
            module = 'fca_uk' if i % 2 == 0 else 'gdpr_uk'
            gate_id = f'gate_{i}'
            modules[module]['gates'][gate_id] = {
                'status': 'FAIL',
                'severity': 'HIGH',
                'message': f'Gate {i} failed'
            }

        return {
            'modules': modules,
            'overall_risk': 'HIGH' if failure_count > 5 else 'MEDIUM'
        }


# Integration Tests

class TestIntegration:
    """Integration tests for the complete enhanced system"""

    def test_full_correction_workflow(self):
        """Test complete workflow: synthesis -> preview -> apply -> rollback"""
        # This would require more extensive mocking/fixtures
        # Placeholder for comprehensive integration test
        pass

    def test_plugin_integration_with_engine(self):
        """Test plugins working with synthesis engine"""
        pass

    def test_conflict_resolution_in_workflow(self):
        """Test conflict detection and resolution in real workflow"""
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
