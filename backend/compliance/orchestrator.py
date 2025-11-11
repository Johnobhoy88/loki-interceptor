"""
Compliance Orchestrator - Main coordination system for all compliance modules
Intelligent orchestration across GDPR, HIPAA, SOX, PCI-DSS, and FCA compliance modules.
"""

from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from dataclasses import dataclass, field
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class ComplianceModule:
    """Represents a compliance module with its metadata."""
    name: str
    module_id: str
    category: str  # 'data_protection', 'financial', 'healthcare', 'security', 'industry'
    jurisdiction: str  # 'UK', 'EU', 'US', 'Global'
    required_by: List[str] = field(default_factory=list)
    conflicts_with: List[str] = field(default_factory=list)
    complements: List[str] = field(default_factory=list)
    complexity_score: int = 5  # 1-10
    implementation_time_days: int = 30


@dataclass
class ComplianceResult:
    """Results from a compliance check."""
    module_id: str
    module_name: str
    timestamp: datetime
    overall_status: str  # 'PASS', 'FAIL', 'WARNING', 'N/A'
    score: float  # 0-100
    gates_passed: int
    gates_failed: int
    gates_warning: int
    total_gates: int
    critical_issues: List[Dict[str, Any]]
    high_issues: List[Dict[str, Any]]
    medium_issues: List[Dict[str, Any]]
    recommendations: List[str]
    next_actions: List[Dict[str, Any]]


class ComplianceOrchestrator:
    """
    Central orchestrator for all compliance modules.

    Features:
    - Auto-detection of required compliance modules
    - Cross-module conflict detection
    - Compliance scoring (0-100 per module)
    - Roadmap generation with prioritized actions
    - Multi-jurisdiction support
    - Integration with all sub-systems
    """

    def __init__(self):
        self.modules = self._initialize_modules()
        self.active_modules: Set[str] = set()
        self.results_cache: Dict[str, ComplianceResult] = {}

        # Initialize sub-systems (will be imported dynamically to avoid circular deps)
        self.recommender = None
        self.conflict_detector = None
        self.scoring_engine = None
        self.roadmap_generator = None
        self.change_monitor = None
        self.benchmarking = None
        self.certification = None
        self.calendar = None
        self.cost_estimator = None
        self.risk_heatmap = None

    def _initialize_modules(self) -> Dict[str, ComplianceModule]:
        """Initialize all available compliance modules with metadata."""
        return {
            'gdpr_uk': ComplianceModule(
                name='GDPR UK Compliance',
                module_id='gdpr_uk',
                category='data_protection',
                jurisdiction='UK',
                required_by=['data_processing', 'personal_data', 'eu_business'],
                complements=['gdpr_advanced', 'privacy_uk'],
                complexity_score=8,
                implementation_time_days=60
            ),
            'gdpr_advanced': ComplianceModule(
                name='GDPR Advanced',
                module_id='gdpr_advanced',
                category='data_protection',
                jurisdiction='EU',
                required_by=['high_risk_processing', 'automated_decisions'],
                complements=['gdpr_uk'],
                complexity_score=9,
                implementation_time_days=90
            ),
            'fca_uk': ComplianceModule(
                name='FCA Financial Conduct',
                module_id='fca_uk',
                category='financial',
                jurisdiction='UK',
                required_by=['financial_services', 'uk_banking'],
                conflicts_with=['sec_us'],  # Different regulatory approaches
                complements=['fca_advanced'],
                complexity_score=9,
                implementation_time_days=120
            ),
            'fca_advanced': ComplianceModule(
                name='FCA Advanced',
                module_id='fca_advanced',
                category='financial',
                jurisdiction='UK',
                required_by=['investment_services', 'crypto_assets'],
                complements=['fca_uk'],
                complexity_score=10,
                implementation_time_days=150
            ),
            'hipaa_us': ComplianceModule(
                name='HIPAA Healthcare Privacy',
                module_id='hipaa_us',
                category='healthcare',
                jurisdiction='US',
                required_by=['healthcare', 'medical_records', 'phi_processing'],
                conflicts_with=['gdpr_uk'],  # Different consent models
                complexity_score=9,
                implementation_time_days=90
            ),
            'sox_us': ComplianceModule(
                name='Sarbanes-Oxley (SOX)',
                module_id='sox_us',
                category='financial',
                jurisdiction='US',
                required_by=['public_company', 'financial_reporting'],
                complements=['audit_controls'],
                complexity_score=10,
                implementation_time_days=180
            ),
            'pci_dss': ComplianceModule(
                name='PCI-DSS Payment Card',
                module_id='pci_dss',
                category='security',
                jurisdiction='Global',
                required_by=['payment_processing', 'card_data'],
                complements=['security_uk'],
                complexity_score=8,
                implementation_time_days=90
            ),
            'nda_uk': ComplianceModule(
                name='UK NDA Confidentiality',
                module_id='nda_uk',
                category='legal',
                jurisdiction='UK',
                required_by=['confidential_info', 'trade_secrets'],
                complements=['gdpr_uk'],
                complexity_score=5,
                implementation_time_days=30
            ),
            'tax_uk': ComplianceModule(
                name='UK Tax Compliance (MTD)',
                module_id='tax_uk',
                category='financial',
                jurisdiction='UK',
                required_by=['uk_business', 'tax_reporting'],
                complexity_score=6,
                implementation_time_days=45
            ),
            'hr_scottish': ComplianceModule(
                name='Scottish HR Employment Law',
                module_id='hr_scottish',
                category='employment',
                jurisdiction='Scotland',
                required_by=['scottish_employer', 'employment_contracts'],
                complements=['uk_employment'],
                complexity_score=6,
                implementation_time_days=40
            ),
            'uk_employment': ComplianceModule(
                name='UK Employment Law',
                module_id='uk_employment',
                category='employment',
                jurisdiction='UK',
                required_by=['uk_employer', 'employee_contracts'],
                complements=['hr_scottish'],
                complexity_score=7,
                implementation_time_days=50
            ),
            'scottish_law': ComplianceModule(
                name='Scottish Legal System',
                module_id='scottish_law',
                category='legal',
                jurisdiction='Scotland',
                required_by=['scottish_contracts', 'scots_law'],
                complexity_score=7,
                implementation_time_days=60
            ),
            'healthcare_uk': ComplianceModule(
                name='UK Healthcare (NHS/CQC)',
                module_id='healthcare_uk',
                category='healthcare',
                jurisdiction='UK',
                required_by=['nhs_services', 'healthcare_provider'],
                complements=['gdpr_uk'],
                complexity_score=8,
                implementation_time_days=75
            ),
            'finance_industry': ComplianceModule(
                name='Finance Industry Standards',
                module_id='finance_industry',
                category='industry',
                jurisdiction='UK',
                required_by=['financial_services'],
                complements=['fca_uk'],
                complexity_score=7,
                implementation_time_days=60
            ),
            'education_uk': ComplianceModule(
                name='UK Education Compliance',
                module_id='education_uk',
                category='industry',
                jurisdiction='UK',
                required_by=['education_provider', 'student_data'],
                complements=['gdpr_uk'],
                complexity_score=6,
                implementation_time_days=50
            ),
        }

    def analyze_document(
        self,
        text: str,
        document_type: str,
        organization_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive compliance analysis across all relevant modules.

        Args:
            text: Document text to analyze
            document_type: Type of document (e.g., 'contract', 'policy', 'agreement')
            organization_profile: Optional organization profile for better recommendations

        Returns:
            Complete compliance analysis with scores, conflicts, and recommendations
        """
        logger.info(f"Starting compliance orchestration for document type: {document_type}")

        # Step 1: Recommend relevant modules
        recommended_modules = self._recommend_modules(text, document_type, organization_profile)
        logger.info(f"Recommended modules: {[m['module_id'] for m in recommended_modules]}")

        # Step 2: Run compliance checks on all recommended modules
        module_results = self._run_compliance_checks(text, document_type, recommended_modules)

        # Step 3: Detect cross-module conflicts
        conflicts = self._detect_conflicts(module_results)

        # Step 4: Calculate compliance scores
        scores = self._calculate_scores(module_results)

        # Step 5: Generate compliance roadmap
        roadmap = self._generate_roadmap(module_results, conflicts, organization_profile)

        # Step 6: Generate risk heatmap
        risk_heatmap = self._generate_risk_heatmap(module_results)

        # Step 7: Calculate cost estimates
        cost_estimate = self._estimate_costs(module_results, roadmap)

        # Step 8: Generate obligation calendar
        calendar = self._generate_calendar(module_results)

        # Step 9: Benchmark against industry standards
        benchmarks = self._benchmark_results(scores, organization_profile)

        # Aggregate results
        return {
            'timestamp': datetime.now().isoformat(),
            'document_type': document_type,
            'orchestration_summary': {
                'total_modules_analyzed': len(module_results),
                'modules_passed': sum(1 for r in module_results.values() if r.overall_status == 'PASS'),
                'modules_failed': sum(1 for r in module_results.values() if r.overall_status == 'FAIL'),
                'modules_warning': sum(1 for r in module_results.values() if r.overall_status == 'WARNING'),
                'average_score': sum(r.score for r in module_results.values()) / len(module_results) if module_results else 0,
                'critical_issues_count': sum(len(r.critical_issues) for r in module_results.values()),
                'high_issues_count': sum(len(r.high_issues) for r in module_results.values()),
            },
            'recommended_modules': recommended_modules,
            'module_results': {k: self._serialize_result(v) for k, v in module_results.items()},
            'compliance_scores': scores,
            'cross_module_conflicts': conflicts,
            'compliance_roadmap': roadmap,
            'risk_heatmap': risk_heatmap,
            'cost_estimate': cost_estimate,
            'obligation_calendar': calendar,
            'industry_benchmarks': benchmarks,
            'certification_ready': self._check_certification_readiness(module_results),
            'next_steps': self._prioritize_next_steps(module_results, conflicts, roadmap),
        }

    def _recommend_modules(
        self,
        text: str,
        document_type: str,
        organization_profile: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Recommend relevant compliance modules based on document content."""
        # Import dynamically to avoid circular dependencies
        from .module_recommender import ModuleRecommender

        if not self.recommender:
            self.recommender = ModuleRecommender(self.modules)

        return self.recommender.recommend(text, document_type, organization_profile)

    def _run_compliance_checks(
        self,
        text: str,
        document_type: str,
        recommended_modules: List[Dict[str, Any]]
    ) -> Dict[str, ComplianceResult]:
        """Run compliance checks on all recommended modules."""
        results = {}

        # Import actual module implementations
        available_modules = self._load_available_modules()

        for rec_module in recommended_modules:
            module_id = rec_module['module_id']

            if module_id in available_modules:
                try:
                    module_instance = available_modules[module_id]
                    check_result = module_instance.execute(text, document_type)

                    # Convert to ComplianceResult
                    compliance_result = self._convert_to_compliance_result(
                        module_id,
                        self.modules[module_id].name,
                        check_result
                    )
                    results[module_id] = compliance_result

                except Exception as e:
                    logger.error(f"Error running compliance check for {module_id}: {e}")
                    results[module_id] = self._create_error_result(module_id, str(e))
            else:
                logger.warning(f"Module {module_id} not available for execution")

        return results

    def _load_available_modules(self) -> Dict[str, Any]:
        """Load actual module implementations."""
        available = {}

        try:
            from backend.modules.gdpr_uk.module import GdprUkModule
            available['gdpr_uk'] = GdprUkModule()
        except ImportError:
            logger.warning("GDPR UK module not available")

        try:
            from backend.modules.gdpr_advanced.module import GdprAdvancedModule
            available['gdpr_advanced'] = GdprAdvancedModule()
        except ImportError:
            logger.warning("GDPR Advanced module not available")

        try:
            from backend.modules.fca_uk.module import FcaUkModule
            available['fca_uk'] = FcaUkModule()
        except ImportError:
            logger.warning("FCA UK module not available")

        try:
            from backend.modules.fca_advanced.module import FcaAdvancedModule
            available['fca_advanced'] = FcaAdvancedModule()
        except ImportError:
            logger.warning("FCA Advanced module not available")

        try:
            from backend.modules.nda_uk.module import NdaUkModule
            available['nda_uk'] = NdaUkModule()
        except ImportError:
            logger.warning("NDA UK module not available")

        try:
            from backend.modules.tax_uk.module import TaxUkModule
            available['tax_uk'] = TaxUkModule()
        except ImportError:
            logger.warning("Tax UK module not available")

        try:
            from backend.modules.hr_scottish.module import HrScottishModule
            available['hr_scottish'] = HrScottishModule()
        except ImportError:
            logger.warning("HR Scottish module not available")

        try:
            from backend.modules.uk_employment.module import UkEmploymentModule
            available['uk_employment'] = UkEmploymentModule()
        except ImportError:
            logger.warning("UK Employment module not available")

        try:
            from backend.modules.scottish_law.module import ScottishLawModule
            available['scottish_law'] = ScottishLawModule()
        except ImportError:
            logger.warning("Scottish Law module not available")

        return available

    def _convert_to_compliance_result(
        self,
        module_id: str,
        module_name: str,
        check_result: Dict[str, Any]
    ) -> ComplianceResult:
        """Convert module check result to standardized ComplianceResult."""
        gates = check_result.get('gates', {})

        gates_passed = sum(1 for g in gates.values() if g.get('status') == 'PASS')
        gates_failed = sum(1 for g in gates.values() if g.get('status') == 'FAIL')
        gates_warning = sum(1 for g in gates.values() if g.get('status') == 'WARNING')
        total_gates = len(gates)

        # Calculate score (0-100)
        score = (gates_passed / total_gates * 100) if total_gates > 0 else 0

        # Categorize issues by severity
        critical_issues = []
        high_issues = []
        medium_issues = []

        for gate_name, gate_result in gates.items():
            if gate_result.get('status') in ['FAIL', 'WARNING']:
                issue = {
                    'gate': gate_name,
                    'status': gate_result.get('status'),
                    'severity': gate_result.get('severity', 'medium'),
                    'message': gate_result.get('message', ''),
                    'suggestions': gate_result.get('suggestions', [])
                }

                severity = gate_result.get('severity', 'medium')
                if severity == 'critical':
                    critical_issues.append(issue)
                elif severity == 'high':
                    high_issues.append(issue)
                else:
                    medium_issues.append(issue)

        # Determine overall status
        if critical_issues:
            overall_status = 'FAIL'
        elif gates_failed > 0:
            overall_status = 'FAIL'
        elif gates_warning > 0:
            overall_status = 'WARNING'
        else:
            overall_status = 'PASS'

        return ComplianceResult(
            module_id=module_id,
            module_name=module_name,
            timestamp=datetime.now(),
            overall_status=overall_status,
            score=score,
            gates_passed=gates_passed,
            gates_failed=gates_failed,
            gates_warning=gates_warning,
            total_gates=total_gates,
            critical_issues=critical_issues,
            high_issues=high_issues,
            medium_issues=medium_issues,
            recommendations=[],
            next_actions=[]
        )

    def _create_error_result(self, module_id: str, error_msg: str) -> ComplianceResult:
        """Create an error result for a failed module check."""
        return ComplianceResult(
            module_id=module_id,
            module_name=self.modules.get(module_id, ComplianceModule('Unknown', module_id, 'unknown', 'unknown')).name,
            timestamp=datetime.now(),
            overall_status='ERROR',
            score=0,
            gates_passed=0,
            gates_failed=0,
            gates_warning=0,
            total_gates=0,
            critical_issues=[{'error': error_msg}],
            high_issues=[],
            medium_issues=[],
            recommendations=[f"Fix module error: {error_msg}"],
            next_actions=[]
        )

    def _detect_conflicts(self, module_results: Dict[str, ComplianceResult]) -> List[Dict[str, Any]]:
        """Detect conflicts between compliance modules."""
        from .conflict_detector import ConflictDetector

        if not self.conflict_detector:
            self.conflict_detector = ConflictDetector(self.modules)

        return self.conflict_detector.detect(module_results)

    def _calculate_scores(self, module_results: Dict[str, ComplianceResult]) -> Dict[str, Any]:
        """Calculate compliance scores for all modules."""
        from .scoring_engine import ScoringEngine

        if not self.scoring_engine:
            self.scoring_engine = ScoringEngine()

        return self.scoring_engine.calculate_scores(module_results)

    def _generate_roadmap(
        self,
        module_results: Dict[str, ComplianceResult],
        conflicts: List[Dict[str, Any]],
        organization_profile: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate compliance roadmap with prioritized actions."""
        from .roadmap_generator import RoadmapGenerator

        if not self.roadmap_generator:
            self.roadmap_generator = RoadmapGenerator(self.modules)

        return self.roadmap_generator.generate(module_results, conflicts, organization_profile)

    def _generate_risk_heatmap(self, module_results: Dict[str, ComplianceResult]) -> Dict[str, Any]:
        """Generate risk heatmap visualization data."""
        from .risk_heatmap import RiskHeatmapGenerator

        if not self.risk_heatmap:
            self.risk_heatmap = RiskHeatmapGenerator()

        return self.risk_heatmap.generate(module_results)

    def _estimate_costs(
        self,
        module_results: Dict[str, ComplianceResult],
        roadmap: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Estimate compliance implementation costs."""
        from .cost_estimator import CostEstimator

        if not self.cost_estimator:
            self.cost_estimator = CostEstimator(self.modules)

        return self.cost_estimator.estimate(module_results, roadmap)

    def _generate_calendar(self, module_results: Dict[str, ComplianceResult]) -> Dict[str, Any]:
        """Generate obligation calendar."""
        from .calendar import ObligationCalendar

        if not self.calendar:
            self.calendar = ObligationCalendar()

        return self.calendar.generate(module_results)

    def _benchmark_results(
        self,
        scores: Dict[str, Any],
        organization_profile: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Benchmark results against industry standards."""
        from .benchmarking import BenchmarkingEngine

        if not self.benchmarking:
            self.benchmarking = BenchmarkingEngine()

        return self.benchmarking.benchmark(scores, organization_profile)

    def _check_certification_readiness(self, module_results: Dict[str, ComplianceResult]) -> Dict[str, Any]:
        """Check if organization is ready for compliance certification."""
        certification_status = {}

        for module_id, result in module_results.items():
            # Ready if score >= 90 and no critical issues
            is_ready = result.score >= 90 and len(result.critical_issues) == 0

            certification_status[module_id] = {
                'ready': is_ready,
                'score': result.score,
                'required_score': 90,
                'blocking_issues': len(result.critical_issues),
                'gap_to_certification': max(0, 90 - result.score)
            }

        return certification_status

    def _prioritize_next_steps(
        self,
        module_results: Dict[str, ComplianceResult],
        conflicts: List[Dict[str, Any]],
        roadmap: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Prioritize next steps based on all analysis."""
        next_steps = []

        # Priority 1: Resolve conflicts
        if conflicts:
            next_steps.append({
                'priority': 1,
                'category': 'conflict_resolution',
                'action': f"Resolve {len(conflicts)} cross-module conflicts",
                'urgency': 'critical',
                'estimated_time': '1-2 weeks',
                'details': conflicts
            })

        # Priority 2: Fix critical issues
        critical_count = sum(len(r.critical_issues) for r in module_results.values())
        if critical_count > 0:
            next_steps.append({
                'priority': 2,
                'category': 'critical_issues',
                'action': f"Address {critical_count} critical compliance issues",
                'urgency': 'critical',
                'estimated_time': '2-4 weeks',
                'modules_affected': [m for m, r in module_results.items() if r.critical_issues]
            })

        # Priority 3: Implement roadmap phases
        if roadmap.get('phases'):
            phase_1 = roadmap['phases'][0] if roadmap['phases'] else None
            if phase_1:
                next_steps.append({
                    'priority': 3,
                    'category': 'roadmap_execution',
                    'action': f"Execute Phase 1: {phase_1.get('name', 'Foundation')}",
                    'urgency': 'high',
                    'estimated_time': phase_1.get('duration', 'Unknown'),
                    'tasks': phase_1.get('tasks', [])
                })

        # Priority 4: Improve scores below 80
        low_scoring_modules = {m: r.score for m, r in module_results.items() if r.score < 80}
        if low_scoring_modules:
            next_steps.append({
                'priority': 4,
                'category': 'score_improvement',
                'action': f"Improve compliance scores for {len(low_scoring_modules)} modules",
                'urgency': 'medium',
                'estimated_time': '4-8 weeks',
                'modules': low_scoring_modules
            })

        return sorted(next_steps, key=lambda x: x['priority'])

    def _serialize_result(self, result: ComplianceResult) -> Dict[str, Any]:
        """Serialize ComplianceResult to dictionary."""
        return {
            'module_id': result.module_id,
            'module_name': result.module_name,
            'timestamp': result.timestamp.isoformat(),
            'overall_status': result.overall_status,
            'score': result.score,
            'gates_passed': result.gates_passed,
            'gates_failed': result.gates_failed,
            'gates_warning': result.gates_warning,
            'total_gates': result.total_gates,
            'critical_issues': result.critical_issues,
            'high_issues': result.high_issues,
            'medium_issues': result.medium_issues,
            'recommendations': result.recommendations,
            'next_actions': result.next_actions
        }

    def generate_certification_report(
        self,
        module_results: Dict[str, ComplianceResult],
        organization_info: Dict[str, Any],
        output_path: str
    ) -> str:
        """Generate professional PDF certification report."""
        from .certification import CertificationGenerator

        if not self.certification:
            self.certification = CertificationGenerator()

        return self.certification.generate_report(module_results, organization_info, output_path)

    def monitor_regulatory_changes(self, jurisdictions: List[str]) -> Dict[str, Any]:
        """Monitor regulatory changes for specified jurisdictions."""
        from .change_monitor import ChangeMonitor

        if not self.change_monitor:
            self.change_monitor = ChangeMonitor()

        return self.change_monitor.check_updates(jurisdictions)
