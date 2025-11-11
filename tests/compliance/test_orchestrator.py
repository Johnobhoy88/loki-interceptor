"""
Integration Tests for Compliance Orchestration System
Tests all components working together.
"""

import pytest
from datetime import datetime
from backend.compliance.orchestrator import ComplianceOrchestrator, ComplianceResult
from backend.compliance.module_recommender import ModuleRecommender
from backend.compliance.conflict_detector import ConflictDetector
from backend.compliance.scoring_engine import ScoringEngine
from backend.compliance.roadmap_generator import RoadmapGenerator
from backend.compliance.change_monitor import ChangeMonitor
from backend.compliance.benchmarking import BenchmarkingEngine
from backend.compliance.calendar import ObligationCalendar
from backend.compliance.cost_estimator import CostEstimator
from backend.compliance.risk_heatmap import RiskHeatmapGenerator
from backend.compliance.certification import CertificationGenerator


class TestComplianceOrchestrator:
    """Test suite for the complete orchestration system."""

    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = ComplianceOrchestrator()

    def test_orchestrator_initialization(self):
        """Test that orchestrator initializes correctly."""
        assert self.orchestrator is not None
        assert len(self.orchestrator.modules) > 0
        assert 'gdpr_uk' in self.orchestrator.modules
        assert 'fca_uk' in self.orchestrator.modules

    def test_module_recommender(self):
        """Test module recommendation system."""
        recommender = ModuleRecommender(self.orchestrator.modules)

        # Test GDPR detection
        gdpr_text = """
        Privacy Policy - We process personal data in accordance with GDPR.
        We collect user consent and ensure data subject rights are respected.
        """
        results = recommender.recommend(gdpr_text, 'privacy_policy')

        assert len(results) > 0
        assert any(r['module_id'] == 'gdpr_uk' for r in results)

        # Test financial services detection
        fca_text = """
        FCA Compliance Manual - This firm is authorized by the Financial Conduct Authority.
        We implement SMCR requirements and Treating Customers Fairly principles.
        """
        results = recommender.recommend(fca_text, 'compliance_manual')

        assert any(r['module_id'] == 'fca_uk' for r in results)
        assert all('confidence' in r for r in results)
        assert all('priority' in r for r in results)

    def test_conflict_detector(self):
        """Test cross-module conflict detection."""
        detector = ConflictDetector(self.orchestrator.modules)

        # Create sample results with known conflicts
        results = {
            'gdpr_uk': self._create_sample_result('gdpr_uk', 'PASS', 85),
            'hipaa_us': self._create_sample_result('hipaa_us', 'FAIL', 65)
        }

        conflicts = detector.detect(results)

        # Should detect GDPR-HIPAA conflict
        assert len(conflicts) > 0
        assert any(
            'gdpr_uk' in str(c) and 'hipaa_us' in str(c)
            for c in conflicts
        )

        # Test resolution roadmap
        roadmap = detector.get_resolution_roadmap(conflicts)
        assert 'total_conflicts' in roadmap
        assert 'phases' in roadmap

    def test_scoring_engine(self):
        """Test compliance scoring calculations."""
        engine = ScoringEngine()

        result = self._create_sample_result('gdpr_uk', 'PASS', 85)
        result.gates_passed = 13
        result.gates_failed = 1
        result.gates_warning = 1
        result.total_gates = 15

        scores = engine.calculate_scores({'gdpr_uk': result})

        assert 'module_scores' in scores
        assert 'aggregate' in scores
        assert scores['module_scores']['gdpr_uk']['score'] > 0
        assert 'grade' in scores['module_scores']['gdpr_uk']

    def test_roadmap_generator(self):
        """Test compliance roadmap generation."""
        generator = RoadmapGenerator(self.orchestrator.modules)

        results = {
            'gdpr_uk': self._create_sample_result('gdpr_uk', 'WARNING', 75),
            'fca_uk': self._create_sample_result('fca_uk', 'FAIL', 60)
        }

        roadmap = generator.generate(results, [], {'size': 'medium'})

        assert 'phases' in roadmap
        assert 'total_duration_days' in roadmap
        assert 'total_estimated_cost' in roadmap
        assert len(roadmap['phases']) > 0

        # Check that phases have required fields
        phase = roadmap['phases'][0]
        assert 'phase_number' in phase
        assert 'name' in phase
        assert 'tasks' in phase
        assert 'success_criteria' in phase

    def test_change_monitor(self):
        """Test regulatory change monitoring."""
        monitor = ChangeMonitor()

        updates = monitor.check_updates(['UK', 'EU'])

        assert 'total_changes' in updates
        assert 'all_changes' in updates
        assert 'monitoring_sources' in updates
        assert 'recommendations' in updates

    def test_benchmarking_engine(self):
        """Test benchmarking against industry standards."""
        engine = BenchmarkingEngine()

        scores = {
            'module_scores': {
                'gdpr_uk': {'score': 85.0, 'grade': 'B+'},
                'fca_uk': {'score': 78.0, 'grade': 'C+'}
            },
            'aggregate': {'overall_score': 81.5}
        }

        benchmarks = engine.benchmark(scores, {'industry': 'financial_services'})

        assert 'module_comparisons' in benchmarks
        assert 'aggregate_comparison' in benchmarks
        assert 'improvement_targets' in benchmarks

        # Check module comparison structure
        if 'gdpr_uk' in benchmarks['module_comparisons']:
            comparison = benchmarks['module_comparisons']['gdpr_uk']
            assert 'actual_score' in comparison
            assert 'industry_average' in comparison
            assert 'gap_to_average' in comparison

    def test_obligation_calendar(self):
        """Test compliance obligation calendar generation."""
        calendar = ObligationCalendar()

        results = {
            'gdpr_uk': self._create_sample_result('gdpr_uk', 'PASS', 85),
            'fca_uk': self._create_sample_result('fca_uk', 'PASS', 82)
        }

        cal_data = calendar.generate(results)

        assert 'total_obligations' in cal_data
        assert 'upcoming_30_days' in cal_data
        assert 'monthly_breakdown' in cal_data
        assert 'workload_analysis' in cal_data

    def test_cost_estimator(self):
        """Test compliance cost estimation."""
        estimator = CostEstimator(self.orchestrator.modules)

        results = {
            'gdpr_uk': self._create_sample_result('gdpr_uk', 'WARNING', 75),
            'fca_uk': self._create_sample_result('fca_uk', 'FAIL', 60)
        }

        roadmap = {
            'phases': [
                {'name': 'Phase 1', 'estimated_cost': 50000},
                {'name': 'Phase 2', 'estimated_cost': 100000}
            ]
        }

        costs = estimator.estimate(results, roadmap, {'size': 'medium', 'employee_count': 50})

        assert 'summary' in costs
        assert 'year_one_total' in costs['summary']
        assert 'cost_breakdown' in costs
        assert 'roi_analysis' in costs

    def test_risk_heatmap_generator(self):
        """Test risk heatmap generation."""
        generator = RiskHeatmapGenerator()

        results = {
            'gdpr_uk': self._create_sample_result('gdpr_uk', 'PASS', 85),
            'fca_uk': self._create_sample_result('fca_uk', 'FAIL', 55)
        }

        # Add issues to make it more realistic
        results['fca_uk'].critical_issues = [
            {'issue': 'Missing FCA authorization'},
            {'issue': 'No SMCR regime'}
        ]

        heatmap = generator.generate(results)

        assert 'module_risks' in heatmap
        assert 'heatmap_matrix' in heatmap
        assert 'quadrant_analysis' in heatmap
        assert 'risk_hotspots' in heatmap
        assert 'visualization_data' in heatmap

        # Check risk assessment structure
        assert len(heatmap['module_risks']) == 2
        for module_id, risk in heatmap['module_risks'].items():
            assert 'likelihood' in risk
            assert 'impact' in risk
            assert 'risk_score' in risk
            assert 'risk_level' in risk

    def test_certification_generator(self):
        """Test PDF certification report generation."""
        generator = CertificationGenerator()

        results = {
            'gdpr_uk': self._create_sample_result('gdpr_uk', 'PASS', 88),
            'fca_uk': self._create_sample_result('fca_uk', 'PASS', 84)
        }

        org_info = {
            'name': 'Test Organization Ltd',
            'address': '123 Test Street, London',
            'industry': 'financial_services'
        }

        # Test report generation (HTML fallback)
        output_path = '/tmp/test_compliance_report.html'
        result_path = generator.generate_report(results, org_info, output_path)

        assert result_path.endswith('.html')

    def test_full_orchestration_workflow(self):
        """Test complete orchestration workflow end-to-end."""
        # Sample document text
        document_text = """
        Privacy and Data Protection Policy

        We process personal data in accordance with UK GDPR and Data Protection Act 2018.
        This includes collecting explicit consent, ensuring data subject rights, maintaining
        secure data storage, and implementing appropriate technical and organizational measures.

        As an FCA-authorized firm, we also comply with financial services regulations and
        implement Treating Customers Fairly principles.

        All staff receive annual data protection training and we maintain comprehensive
        records of processing activities.
        """

        # Organization profile
        org_profile = {
            'name': 'Test Financial Services Ltd',
            'industry': 'financial_services',
            'size': 'medium',
            'employee_count': 75,
            'jurisdiction': 'UK'
        }

        # This would normally call analyze_document, but we'll test components
        # Since actual module execution requires the full LOKI infrastructure

        # Test module recommendation
        recommender = ModuleRecommender(self.orchestrator.modules)
        recommended = recommender.recommend(document_text, 'policy', org_profile)

        assert len(recommended) > 0
        assert any(r['module_id'] == 'gdpr_uk' for r in recommended)
        assert any(r['module_id'] == 'fca_uk' for r in recommended)

        # Create mock results for testing downstream components
        mock_results = {}
        for rec in recommended[:3]:  # Use top 3 recommendations
            mock_results[rec['module_id']] = self._create_sample_result(
                rec['module_id'],
                'WARNING' if rec['confidence'] < 0.7 else 'PASS',
                70 + (rec['confidence'] * 25)
            )

        # Test conflict detection
        detector = ConflictDetector(self.orchestrator.modules)
        conflicts = detector.detect(mock_results)

        # Test scoring
        scorer = ScoringEngine()
        scores = scorer.calculate_scores(mock_results)
        assert scores['aggregate']['overall_score'] > 0

        # Test roadmap generation
        roadmap_gen = RoadmapGenerator(self.orchestrator.modules)
        roadmap = roadmap_gen.generate(mock_results, conflicts, org_profile)
        assert len(roadmap['phases']) > 0

        # Test benchmarking
        benchmarker = BenchmarkingEngine()
        benchmarks = benchmarker.benchmark(scores, org_profile)
        assert 'module_comparisons' in benchmarks

        # Test calendar
        calendar = ObligationCalendar()
        cal_data = calendar.generate(mock_results)
        assert cal_data['total_obligations'] > 0

        # Test cost estimation
        cost_estimator = CostEstimator(self.orchestrator.modules)
        costs = cost_estimator.estimate(mock_results, roadmap, org_profile)
        assert costs['summary']['year_one_total'] > 0

        # Test risk heatmap
        risk_gen = RiskHeatmapGenerator()
        heatmap = risk_gen.generate(mock_results)
        assert 'overall_risk_level' in heatmap

        print("\n Full orchestration workflow test passed!")
        print(f"   - Recommended {len(recommended)} modules")
        print(f"   - Detected {len(conflicts)} conflicts")
        print(f"   - Overall score: {scores['aggregate']['overall_score']:.1f}")
        print(f"   - Roadmap phases: {len(roadmap['phases'])}")
        print(f"   - Year one cost: £{costs['summary']['year_one_total']:,.2f}")

    def _create_sample_result(
        self,
        module_id: str,
        status: str,
        score: float
    ) -> ComplianceResult:
        """Helper to create sample compliance results."""
        critical_issues = []
        high_issues = []
        medium_issues = []

        if status == 'FAIL':
            critical_issues = [
                {'issue': f'Critical compliance gap in {module_id}', 'severity': 'critical'}
            ]
            high_issues = [
                {'issue': f'High priority issue in {module_id}', 'severity': 'high'}
            ]
        elif status == 'WARNING':
            high_issues = [
                {'issue': f'Warning issue in {module_id}', 'severity': 'high'}
            ]
            medium_issues = [
                {'issue': f'Medium issue in {module_id}', 'severity': 'medium'}
            ]

        return ComplianceResult(
            module_id=module_id,
            module_name=self.orchestrator.modules.get(module_id, type('obj', (object,), {'name': module_id})).name,
            timestamp=datetime.now(),
            overall_status=status,
            score=score,
            gates_passed=int((score / 100) * 15),
            gates_failed=int(((100 - score) / 100) * 15),
            gates_warning=1 if status == 'WARNING' else 0,
            total_gates=15,
            critical_issues=critical_issues,
            high_issues=high_issues,
            medium_issues=medium_issues,
            recommendations=[],
            next_actions=[]
        )


def test_integration_suite():
    """Run complete integration test suite."""
    test_class = TestComplianceOrchestrator()
    test_class.setup_method()

    print("\n" + "="*70)
    print("COMPLIANCE ORCHESTRATION SYSTEM - INTEGRATION TESTS")
    print("="*70)

    tests = [
        ("Orchestrator Initialization", test_class.test_orchestrator_initialization),
        ("Module Recommender", test_class.test_module_recommender),
        ("Conflict Detector", test_class.test_conflict_detector),
        ("Scoring Engine", test_class.test_scoring_engine),
        ("Roadmap Generator", test_class.test_roadmap_generator),
        ("Change Monitor", test_class.test_change_monitor),
        ("Benchmarking Engine", test_class.test_benchmarking_engine),
        ("Obligation Calendar", test_class.test_obligation_calendar),
        ("Cost Estimator", test_class.test_cost_estimator),
        ("Risk Heatmap Generator", test_class.test_risk_heatmap_generator),
        ("Certification Generator", test_class.test_certification_generator),
        ("Full Orchestration Workflow", test_class.test_full_orchestration_workflow),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            print(f"\n¶ Running: {test_name}")
            test_func()
            print(f"   PASSED")
            passed += 1
        except Exception as e:
            print(f"  L FAILED: {str(e)}")
            failed += 1

    print("\n" + "="*70)
    print(f"TEST SUMMARY: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("="*70 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = test_integration_suite()
    exit(0 if success else 1)
