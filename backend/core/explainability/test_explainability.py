"""
Test script demonstrating the LOKI Explainability System

Run this to see example explainability reports for different correction types
"""

from explanation_engine import ExplanationEngine, ExplanationType, CorrectionCategory
from legal_citations import LegalCitationManager
from confidence_explainer import ConfidenceExplainer
from impact_analyzer import ImpactAnalyzer
from reasoning_chain import ReasoningChain
from report_generator import ReportGenerator
from feedback_manager import FeedbackManager, FeedbackType, RejectionReason
from dataclasses import asdict
import json


def test_gdpr_correction():
    """Test explainability for a GDPR correction"""
    print("\n" + "="*80)
    print("TEST 1: GDPR Data Consent Correction")
    print("="*80 + "\n")

    correction_data = {
        'correction_id': 'gdpr-001',
        'original_text': 'We may use your personal data for marketing purposes',
        'corrected_text': 'With your explicit consent, we will use your personal data for marketing purposes only',
        'position': 150,
        'length': 55,
        'gate_id': 'gdpr_uk',
        'severity': 'ERROR',
        'confidence': 0.95,
        'issue_type': 'compliance',
        'document_type': 'privacy_policy',
        'pattern_matched': 'gdpr_consent_pattern',
        'method': 'template_insertion',
        'strategy': 'TemplateInsertionStrategy'
    }

    # Initialize engines
    explanation_engine = ExplanationEngine()
    citation_manager = LegalCitationManager()
    confidence_explainer = ConfidenceExplainer()
    impact_analyzer = ImpactAnalyzer()
    reasoning_chain = ReasoningChain()

    # Generate components
    print("Generating explanation...")
    explanation = explanation_engine.generate_explanation(correction_data)

    print("\n--- EXPLANATION ---")
    print(f"Simple: {explanation.reason_simple}")
    print(f"\nDetailed: {explanation.reason_detailed}")
    print(f"\nLegal Basis: {explanation.legal_basis}")
    print(f"Category: {explanation.category.value}")

    print("\n--- LEGAL CITATIONS ---")
    citations = citation_manager.get_citations_by_gate('gdpr_uk')
    for i, citation in enumerate(citations, 1):
        print(f"\n{i}. {citation.title}")
        print(f"   Reference: {citation.reference}")
        print(f"   URL: {citation.url}")
        print(f"   Excerpt: \"{citation.excerpt}\"")

    print("\n--- CONFIDENCE ANALYSIS ---")
    confidence = confidence_explainer.explain_confidence(correction_data)
    print(f"Overall Confidence: {confidence.total_score:.0%}")
    print(f"Confidence Level: {confidence.confidence_level.value.upper()}")
    print(f"\nPrimary Factors:")
    for factor, score, explanation_text in confidence.primary_factors:
        print(f"  - {factor}: {score:.0%}")
        print(f"    {explanation_text[:100]}...")

    print(f"\nRecommendation: {confidence.recommendation}")

    print("\n--- IMPACT ANALYSIS ---")
    impact = impact_analyzer.analyze_impact(correction_data)
    print(f"Overall Severity: {impact.overall_severity.value.upper()}")
    print(f"Risk Before: {impact.risk_before:.0%}")
    print(f"Risk After: {impact.risk_after:.0%}")
    print(f"Risk Reduction: {impact.risk_reduction:.1f}%")

    print(f"\nAffected Documents ({len(impact.related_documents)}):")
    for doc in impact.related_documents[:3]:
        print(f"  - {doc}")

    print(f"\nImmediate Actions ({len(impact.immediate_actions)}):")
    for action in impact.immediate_actions:
        print(f"  - {action}")

    print("\n--- REASONING CHAIN ---")
    chain = reasoning_chain.build_chain(correction_data)
    print(f"Total Steps: {chain.total_steps}")
    print(f"Overall Confidence: {chain.overall_confidence:.0%}")
    print(f"\nKey Steps:")
    for step in chain.steps[:3]:  # Show first 3 steps
        print(f"\n  Step {step.step_number}: {step.question}")
        print(f"  Result: {step.output}")
        print(f"  Confidence: {step.confidence:.0%}")

    return {
        'explanation': explanation,
        'citations': citations,
        'confidence': confidence,
        'impact': impact,
        'reasoning': chain
    }


def test_tax_correction():
    """Test explainability for a tax correction"""
    print("\n" + "="*80)
    print("TEST 2: Tax VAT Threshold Correction")
    print("="*80 + "\n")

    correction_data = {
        'correction_id': 'tax-001',
        'original_text': 'VAT registration threshold is £85,000',
        'corrected_text': 'VAT registration threshold is £90,000',
        'position': 450,
        'length': 37,
        'gate_id': 'tax_uk',
        'severity': 'ERROR',
        'confidence': 1.0,
        'issue_type': 'accuracy',
        'document_type': 'financial_document',
        'pattern_matched': 'vat_threshold_pattern',
        'method': 'regex_replacement',
        'strategy': 'RegexReplacementStrategy'
    }

    # Generate components
    explanation_engine = ExplanationEngine()
    confidence_explainer = ConfidenceExplainer()

    explanation = explanation_engine.generate_explanation(correction_data)
    confidence = confidence_explainer.explain_confidence(correction_data)

    print("--- EXPLANATION ---")
    print(f"Simple: {explanation.reason_simple}")
    print(f"Confidence: {explanation.confidence_score:.0%}")
    print(f"Risk Reduction: {explanation.risk_reduction:.0%}")

    print("\n--- CONFIDENCE BREAKDOWN ---")
    print(f"Overall: {confidence.total_score:.0%} ({confidence.confidence_level.value.upper()})")
    print(f"\nFactor Contributions:")
    for factor, contribution in sorted(
        confidence.weighted_contributions.items(),
        key=lambda x: x[1],
        reverse=True
    ):
        print(f"  {factor}: {contribution:.1%}")

    return {
        'explanation': explanation,
        'confidence': confidence
    }


def test_fca_correction():
    """Test explainability for an FCA correction"""
    print("\n" + "="*80)
    print("TEST 3: FCA Financial Communication Correction")
    print("="*80 + "\n")

    correction_data = {
        'correction_id': 'fca-001',
        'original_text': 'Our investment products may generate returns',
        'corrected_text': 'Our investment products may generate returns. Past performance is not a reliable indicator of future results. The value of investments can go down as well as up.',
        'position': 200,
        'length': 45,
        'gate_id': 'fca_uk',
        'severity': 'WARNING',
        'confidence': 0.85,
        'issue_type': 'compliance',
        'document_type': 'marketing_material',
        'pattern_matched': 'fca_risk_warning_pattern',
        'method': 'structural_reorganization',
        'strategy': 'StructuralReorganizationStrategy'
    }

    explanation_engine = ExplanationEngine()
    impact_analyzer = ImpactAnalyzer()
    citation_manager = LegalCitationManager()

    explanation = explanation_engine.generate_explanation(correction_data)
    impact = impact_analyzer.analyze_impact(correction_data)
    citations = citation_manager.get_citations_by_gate('fca_uk')

    print("--- EXPLANATION ---")
    print(explanation.reason_detailed)

    print("\n--- LEGAL BASIS ---")
    print(f"{explanation.legal_basis}")
    print(f"\nCitations:")
    for citation in citations:
        print(f"  - {citation.reference}: {citation.title}")

    print("\n--- IMPACT ---")
    print(f"Severity: {impact.overall_severity.value}")
    print(f"Total Impacts: {impact.total_impacts}")
    print(f"\nBenefits:")
    for benefit in impact.benefits[:3]:
        print(f"  - {benefit}")

    return {
        'explanation': explanation,
        'impact': impact,
        'citations': citations
    }


def test_feedback_system():
    """Test the feedback management system"""
    print("\n" + "="*80)
    print("TEST 4: Feedback Management System")
    print("="*80 + "\n")

    feedback_mgr = FeedbackManager()

    # Submit various feedback
    print("Submitting feedback...")

    # Acceptance
    feedback_mgr.submit_feedback(
        correction_id='gdpr-001',
        feedback_type=FeedbackType.ACCEPT,
        user_id='legal-001',
        user_role='legal_counsel',
        accuracy_rating=5,
        usefulness_rating=5,
        explanation_clarity_rating=4,
        gate_id='gdpr_uk',
        severity='ERROR'
    )

    # Rejection
    feedback_mgr.submit_feedback(
        correction_id='gdpr-002',
        feedback_type=FeedbackType.REJECT,
        user_id='compliance-001',
        user_role='compliance_officer',
        rejection_reason=RejectionReason.TOO_AGGRESSIVE,
        rejection_details='Changes document tone too drastically',
        accuracy_rating=3,
        gate_id='gdpr_uk',
        severity='WARNING'
    )

    # Modification
    feedback_mgr.submit_feedback(
        correction_id='tax-001',
        feedback_type=FeedbackType.MODIFY,
        user_id='finance-001',
        user_role='finance_director',
        modified_text='Current VAT threshold is £90,000 (as of April 2024)',
        modification_reason='Added effective date for clarity',
        accuracy_rating=4,
        usefulness_rating=5,
        gate_id='tax_uk',
        severity='ERROR'
    )

    # Analyze feedback
    print("\n--- FEEDBACK ANALYTICS ---")
    analytics = feedback_mgr.analyze_feedback()

    print(f"Total Feedback: {analytics.total_feedback}")
    print(f"Acceptance Rate: {analytics.acceptance_rate:.0%}")
    print(f"Rejection Rate: {analytics.rejection_rate:.0%}")
    print(f"Modification Rate: {analytics.modification_rate:.0%}")

    print(f"\nAverage Ratings:")
    print(f"  Accuracy: {analytics.average_accuracy_rating:.1f}/5")
    print(f"  Usefulness: {analytics.average_usefulness_rating:.1f}/5")
    print(f"  Clarity: {analytics.average_clarity_rating:.1f}/5")

    print(f"\nImprovement Trend: {analytics.improvement_trend.upper()}")

    if analytics.areas_for_improvement:
        print(f"\nAreas for Improvement:")
        for area in analytics.areas_for_improvement:
            print(f"  - {area}")

    # Learning recommendations
    recommendations = feedback_mgr.get_learning_recommendations(analytics)
    if recommendations:
        print(f"\nLearning Recommendations:")
        for rec in recommendations:
            print(f"  - {rec}")

    return analytics


def test_report_generation():
    """Test report generation in multiple formats"""
    print("\n" + "="*80)
    print("TEST 5: Report Generation")
    print("="*80 + "\n")

    # Generate sample data
    correction_data = {
        'correction_id': 'report-test-001',
        'original_text': 'Sample original text',
        'corrected_text': 'Sample corrected text',
        'gate_id': 'gdpr_uk',
        'severity': 'ERROR',
        'confidence': 0.95
    }

    # Initialize engines
    explanation_engine = ExplanationEngine()
    citation_manager = LegalCitationManager()
    confidence_explainer = ConfidenceExplainer()
    impact_analyzer = ImpactAnalyzer()
    reasoning_chain = ReasoningChain()
    report_generator = ReportGenerator()

    # Generate all components
    explanation = explanation_engine.generate_explanation(correction_data)
    citations = citation_manager.get_citations_by_gate('gdpr_uk')
    confidence = confidence_explainer.explain_confidence(correction_data)
    impact = impact_analyzer.analyze_impact(correction_data)
    chain = reasoning_chain.build_chain(correction_data)

    # Generate JSON report
    print("Generating JSON report...")
    json_report = report_generator.generate_report(
        explanation_data=explanation.__dict__,
        impact_data=impact.__dict__,
        reasoning_chain=chain.__dict__,
        confidence_breakdown=asdict(confidence),
        citations=[c.__dict__ for c in citations],
        format='json'
    )

    report_data = json.loads(json_report)
    print(f"JSON Report generated with {len(report_data)} sections")

    # Generate Markdown report
    print("\nGenerating Markdown report...")
    md_report = report_generator.generate_report(
        explanation_data=explanation.__dict__,
        impact_data=impact.__dict__,
        reasoning_chain=chain.__dict__,
        confidence_breakdown=asdict(confidence),
        citations=[c.__dict__ for c in citations],
        format='markdown'
    )
    print(f"Markdown Report generated ({len(md_report)} characters)")

    # Generate HTML report
    print("\nGenerating HTML report...")
    html_report = report_generator.generate_report(
        explanation_data=explanation.__dict__,
        impact_data=impact.__dict__,
        reasoning_chain=chain.__dict__,
        confidence_breakdown=asdict(confidence),
        citations=[c.__dict__ for c in citations],
        format='html'
    )
    print(f"HTML Report generated ({len(html_report)} characters)")

    # Save HTML report
    print("\nSaving HTML report to 'sample_explainability_report.html'...")
    with open('/home/user/loki-interceptor/sample_explainability_report.html', 'w') as f:
        f.write(html_report)

    print("Report saved successfully!")

    return {
        'json': json_report,
        'markdown': md_report,
        'html': html_report
    }


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("LOKI EXPLAINABILITY SYSTEM - COMPREHENSIVE TEST SUITE")
    print("="*80)

    # Run all tests
    test_gdpr_correction()
    test_tax_correction()
    test_fca_correction()
    test_feedback_system()
    test_report_generation()

    print("\n" + "="*80)
    print("ALL TESTS COMPLETED SUCCESSFULLY")
    print("="*80 + "\n")

    print("Summary:")
    print("✓ GDPR correction explainability tested")
    print("✓ Tax correction explainability tested")
    print("✓ FCA correction explainability tested")
    print("✓ Feedback management system tested")
    print("✓ Report generation tested (JSON, Markdown, HTML)")
    print("\nCheck 'sample_explainability_report.html' for a visual example!")


if __name__ == '__main__':
    main()
