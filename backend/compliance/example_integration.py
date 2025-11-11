"""
Complete Integration Example - LOKI Compliance Orchestration System
Demonstrates end-to-end usage of all orchestration components.
"""

from backend.compliance import (
    ComplianceOrchestrator,
    ModuleRecommender,
    ConflictDetector,
    ScoringEngine,
    RoadmapGenerator,
    ChangeMonitor,
    BenchmarkingEngine,
    CertificationGenerator,
    ObligationCalendar,
    CostEstimator,
    RiskHeatmapGenerator
)
from datetime import datetime


def main():
    """Demonstrate complete orchestration workflow."""
    
    print("="*70)
    print("LOKI COMPLIANCE ORCHESTRATION SYSTEM - INTEGRATION EXAMPLE")
    print("="*70)
    print()
    
    # Sample document
    document_text = """
    Privacy and Financial Services Compliance Policy
    
    We process personal data in accordance with UK GDPR and Data Protection Act 2018.
    As an FCA-authorized firm, we implement Treating Customers Fairly principles.
    
    Key Requirements:
    - Obtain explicit consent for data processing
    - Ensure data subject rights (access, rectification, erasure, portability)
    - Implement appropriate technical and organizational measures
    - Maintain records of processing activities
    - Conduct Data Protection Impact Assessments for high-risk processing
    - Apply SMCR requirements for Senior Managers
    - Ensure fair value assessments for all products
    - Maintain client assets protection
    
    All staff receive annual compliance training covering GDPR, FCA regulations,
    and our internal policies. We maintain comprehensive audit trails and 
    regularly review our compliance posture.
    """
    
    organization_profile = {
        'name': 'Example Financial Services Ltd',
        'industry': 'financial_services',
        'size': 'medium',
        'employee_count': 75,
        'jurisdiction': 'UK',
        'resources': 'standard'
    }
    
    print(f"Organization: {organization_profile['name']}")
    print(f"Industry: {organization_profile['industry']}")
    print(f"Size: {organization_profile['size']} ({organization_profile['employee_count']} employees)")
    print()
    
    # Step 1: Module Recommendation
    print("\n" + "="*70)
    print("STEP 1: MODULE RECOMMENDATION")
    print("="*70)
    
    orchestrator = ComplianceOrchestrator()
    recommender = ModuleRecommender(orchestrator.modules)
    
    recommendations = recommender.recommend(
        document_text,
        'policy',
        organization_profile
    )
    
    print(f"\nRecommended {len(recommendations)} compliance modules:")
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['module_name']}")
        print(f"   Confidence: {rec['confidence']:.2f}")
        print(f"   Priority: {rec['priority']}")
        print(f"   Implementation: {rec['implementation_time']} days")
        print(f"   Reason: {rec['reason'][:100]}...")
    
    # Step 2: Conflict Detection (using mock results)
    print("\n" + "="*70)
    print("STEP 2: CROSS-MODULE CONFLICT DETECTION")
    print("="*70)
    
    # Create mock results for demonstration
    from backend.compliance.orchestrator import ComplianceResult
    
    mock_results = {
        'gdpr_uk': ComplianceResult(
            module_id='gdpr_uk',
            module_name='GDPR UK',
            timestamp=datetime.now(),
            overall_status='WARNING',
            score=75,
            gates_passed=11,
            gates_failed=2,
            gates_warning=2,
            total_gates=15,
            critical_issues=[],
            high_issues=[
                {'issue': 'DPIA not documented for high-risk processing'}
            ],
            medium_issues=[
                {'issue': 'Consent withdrawal mechanism could be clearer'}
            ],
            recommendations=[],
            next_actions=[]
        ),
        'fca_uk': ComplianceResult(
            module_id='fca_uk',
            module_name='FCA UK',
            timestamp=datetime.now(),
            overall_status='PASS',
            score=82,
            gates_passed=9,
            gates_failed=0,
            gates_warning=1,
            total_gates=10,
            critical_issues=[],
            high_issues=[],
            medium_issues=[
                {'issue': 'Consumer Duty implementation documentation incomplete'}
            ],
            recommendations=[],
            next_actions=[]
        )
    }
    
    detector = ConflictDetector(orchestrator.modules)
    conflicts = detector.detect(mock_results)
    
    print(f"\nDetected {len(conflicts)} potential conflicts")
    if conflicts:
        for conflict in conflicts[:3]:
            print(f"\n- {conflict['description']}")
            print(f"  Severity: {conflict['severity']}")
            print(f"  Resolution: {conflict.get('resolution_strategies', ['N/A'])[0]}")
    else:
        print("✅ No significant conflicts detected")
    
    # Step 3: Compliance Scoring
    print("\n" + "="*70)
    print("STEP 3: COMPLIANCE SCORING")
    print("="*70)
    
    scoring_engine = ScoringEngine()
    scores = scoring_engine.calculate_scores(mock_results)
    
    print(f"\n📊 Overall Compliance Score: {scores['aggregate']['overall_score']:.1f}%")
    print(f"   Grade: {scores['aggregate']['overall_grade']}")
    print(f"   Status: {scores['summary']['status']}")
    print(f"\n   Module Scores:")
    for module_id, score_data in scores['module_scores'].items():
        status_icon = "✅" if score_data['score'] >= 80 else "⚠️" if score_data['score'] >= 70 else "❌"
        print(f"   {status_icon} {module_id}: {score_data['score']:.1f}% ({score_data['grade']})")
    
    # Step 4: Roadmap Generation
    print("\n" + "="*70)
    print("STEP 4: IMPLEMENTATION ROADMAP")
    print("="*70)
    
    roadmap_gen = RoadmapGenerator(orchestrator.modules)
    roadmap = roadmap_gen.generate(mock_results, conflicts, organization_profile)
    
    print(f"\n📅 Implementation Plan: {roadmap['total_duration_days']} days")
    print(f"💰 Estimated Cost: £{roadmap['total_estimated_cost']:,.2f}")
    print(f"\nPhases ({len(roadmap['phases'])}):")
    
    for phase in roadmap['phases']:
        print(f"\n Phase {phase['phase_number']}: {phase['name']}")
        print(f"   Duration: {phase['duration_days']} days")
        print(f"   Cost: £{phase['estimated_cost']:,.2f}")
        print(f"   Tasks: {phase['task_count']}")
        print(f"   Priority: {phase['priority']}")
    
    # Step 5: Cost Estimation
    print("\n" + "="*70)
    print("STEP 5: COST ESTIMATION & ROI")
    print("="*70)
    
    cost_estimator = CostEstimator(orchestrator.modules)
    costs = cost_estimator.estimate(mock_results, roadmap, organization_profile)
    
    print(f"\n💷 Financial Analysis:")
    print(f"   Year 1 Total: £{costs['summary']['year_one_total']:,.2f}")
    print(f"   Year 2+ Annual: £{costs['summary']['year_two_plus_annual']:,.2f}")
    print(f"   3-Year Total: £{costs['summary']['three_year_total']:,.2f}")
    print(f"\n   ROI Analysis:")
    print(f"   ROI: {costs['roi_analysis']['roi_percentage']:.1f}%")
    print(f"   Payback Period: {costs['roi_analysis']['payback_period_months']:.1f} months")
    print(f"   Annual Benefits: £{costs['roi_analysis']['annual_benefits']:,.2f}")
    
    # Step 6: Risk Heatmap
    print("\n" + "="*70)
    print("STEP 6: RISK ASSESSMENT")
    print("="*70)
    
    risk_gen = RiskHeatmapGenerator()
    heatmap = risk_gen.generate(mock_results)
    
    print(f"\n🎯 Risk Analysis:")
    print(f"   Overall Risk Level: {heatmap['overall_risk_level']['level'].upper()}")
    print(f"   Average Risk Score: {heatmap['overall_risk_level']['average_risk_score']:.1f}/25")
    print(f"   Risk Exposure: {heatmap['overall_risk_level']['risk_exposure'].upper()}")
    print(f"   Status: {heatmap['overall_risk_level']['status']}")
    print(f"\n   Risk Hotspots: {len(heatmap['risk_hotspots'])}")
    
    for hotspot in heatmap['risk_hotspots'][:3]:
        print(f"   ⚠️  {hotspot['module_name']}: {hotspot['risk_level']} risk")
    
    # Step 7: Benchmarking
    print("\n" + "="*70)
    print("STEP 7: INDUSTRY BENCHMARKING")
    print("="*70)
    
    benchmarker = BenchmarkingEngine()
    benchmarks = benchmarker.benchmark(scores, organization_profile)
    
    print(f"\n📈 Industry Comparison:")
    print(f"   Industry: {benchmarks['industry']}")
    print(f"   Overall Ranking: {benchmarks['ranking']['rank']}")
    print(f"   Percentile: {benchmarks['ranking']['percentile']:.0f}th")
    print(f"   Description: {benchmarks['ranking']['description']}")
    print(f"\n   Module Comparisons:")
    
    for module_id, comp in list(benchmarks['module_comparisons'].items())[:3]:
        gap_icon = "✅" if comp['gap_to_average'] >= 0 else "📉"
        print(f"   {gap_icon} {module_id}:")
        print(f"      Your Score: {comp['actual_score']:.1f}%")
        print(f"      Industry Avg: {comp['industry_average']:.1f}%")
        print(f"      Gap: {comp['gap_to_average']:+.1f}% ({comp['status']})")
    
    # Step 8: Obligation Calendar
    print("\n" + "="*70)
    print("STEP 8: COMPLIANCE CALENDAR")
    print("="*70)
    
    calendar = ObligationCalendar()
    cal_data = calendar.generate(mock_results)
    
    print(f"\n📅 Obligations Overview:")
    print(f"   Total Obligations: {cal_data['total_obligations']}")
    print(f"   Upcoming (30 days): {len(cal_data['upcoming_30_days'])}")
    print(f"   Upcoming (90 days): {len(cal_data['upcoming_90_days'])}")
    print(f"   Overdue: {len(cal_data['overdue'])}")
    print(f"\n   Critical Deadlines: {len(cal_data['critical_deadlines'])}")
    
    for obligation in cal_data['critical_deadlines'][:3]:
        print(f"   📌 {obligation['title']} - {obligation['responsible_party']}")
    
    # Step 9: Regulatory Monitoring
    print("\n" + "="*70)
    print("STEP 9: REGULATORY CHANGE MONITORING")
    print("="*70)
    
    monitor = ChangeMonitor()
    updates = monitor.check_updates(['UK', 'EU'])
    
    print(f"\n🔔 Regulatory Updates:")
    print(f"   Total Changes: {updates['total_changes']}")
    print(f"   High Impact: {updates['changes_by_impact']['high']}")
    print(f"   Medium Impact: {updates['changes_by_impact']['medium']}")
    print(f"   Urgent (< 30 days): {len(updates['urgent_changes'])}")
    
    if updates['urgent_changes']:
        print(f"\n   Urgent Actions Required:")
        for change in updates['urgent_changes']:
            print(f"   ⚡ {change['title']}")
            print(f"      Authority: {change['authority']}")
            print(f"      Deadline: {change['deadline'][:10]}")
    
    # Summary
    print("\n" + "="*70)
    print("ORCHESTRATION COMPLETE - SUMMARY")
    print("="*70)
    
    print(f"""
✅ Compliance Analysis Completed Successfully!

Key Findings:
- Overall Score: {scores['aggregate']['overall_score']:.1f}% ({scores['aggregate']['overall_grade']})
- Risk Level: {heatmap['overall_risk_level']['level'].upper()}
- Industry Ranking: {benchmarks['ranking']['rank']}
- Implementation: {roadmap['total_duration_days']} days, £{roadmap['total_estimated_cost']:,.2f}
- ROI: {costs['roi_analysis']['roi_percentage']:.1f}%

Next Steps:
1. Review {len(heatmap['risk_hotspots'])} risk hotspots
2. Address {len(cal_data['critical_deadlines'])} critical obligations
3. Monitor {updates['total_changes']} regulatory changes
4. Execute {len(roadmap['phases'])}-phase implementation plan

💡 Generate certification report: CertificationGenerator().generate_report()
    """)
    
    print("\n" + "="*70)
    print("For detailed documentation, see: COMPLIANCE_ORCHESTRATION.md")
    print("="*70)


if __name__ == "__main__":
    main()
