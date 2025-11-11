# LOKI Correction Explainability System

## Overview

The **LOKI Correction Explainability System** provides complete transparency for every document correction made by the platform. This system ensures that compliance officers, legal teams, and stakeholders understand exactly why each correction was made, the legal basis, confidence level, and downstream impacts.

## Key Features

### 1. Transparent Explanations
- **Simple and Detailed Modes**: From one-line summaries to comprehensive multi-paragraph explanations
- **Legal Context**: Every correction linked to specific UK regulations and legal requirements
- **Clear Reasoning**: Step-by-step explanation of the correction logic

### 2. Legal Citation Management
- **Comprehensive Database**: Full citations for FCA, GDPR, HMRC, and other UK regulations
- **Deep Linking**: Direct links to official legislation and guidance
- **Regular Updates**: Citations verified and updated regularly
- **Multiple Jurisdictions**: Support for UK, Scotland, England & Wales, Northern Ireland

### 3. Confidence Scoring
- **Multi-Factor Analysis**: 8 different factors contribute to confidence scores
- **Transparent Breakdown**: See exactly what contributes to each score
- **Clear Thresholds**: Defined confidence levels (Very High, High, Medium, Low)
- **Actionable Recommendations**: Know when to auto-apply vs. manual review

### 4. Impact Analysis
- **Downstream Effects**: Identify all affected documents, sections, and processes
- **Risk Assessment**: Before/after risk levels with reduction percentages
- **Cost-Benefit**: Estimated cost savings from regulatory compliance
- **Action Plans**: Prioritized immediate, short-term, and long-term actions

### 5. Reasoning Chains
- **Step-by-Step Logic**: 10-step reasoning process for every correction
- **Evidence Tracking**: All evidence sources documented
- **Validation Checkpoints**: Multiple validation stages
- **Audit Trail**: Complete history of decision-making

### 6. Visual Reports
- **Interactive HTML Reports**: Beautiful, professional reports with charts
- **PDF Export**: Print-ready reports for stakeholders
- **Multiple Formats**: JSON, HTML, Markdown, PDF-ready
- **Customizable**: Tailor reports to your needs

### 7. Feedback Loop
- **User Feedback**: Accept, reject, or modify corrections with reasons
- **Learning System**: Continuously improves from user feedback
- **Analytics Dashboard**: Track acceptance rates and performance
- **Quality Monitoring**: Identify areas needing improvement

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Explainability System                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Explanation  │  │   Legal      │  │ Confidence   │      │
│  │   Engine     │  │  Citations   │  │  Explainer   │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                  │              │
│         └─────────────────┼──────────────────┘              │
│                           │                                 │
│  ┌──────────────┐  ┌──────┴───────┐  ┌──────────────┐      │
│  │   Impact     │  │  Reasoning   │  │   Report     │      │
│  │  Analyzer    │  │    Chain     │  │  Generator   │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                  │              │
│         └─────────────────┼──────────────────┘              │
│                           │                                 │
│                  ┌────────┴────────┐                        │
│                  │    Feedback     │                        │
│                  │    Manager      │                        │
│                  └─────────────────┘                        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Explanation Engine (`explanation_engine.py`)

The core engine that generates comprehensive explanations for corrections.

**Key Features:**
- Multi-level explanations (simple, detailed, legal, technical, impact, full)
- Category classification (compliance, legal, best practice, etc.)
- Alternative correction suggestions
- Risk reduction calculations
- Audit trail generation

**Example Usage:**
```python
from backend.core.explainability import ExplanationEngine

engine = ExplanationEngine()

correction_data = {
    'original_text': 'We may use your data',
    'corrected_text': 'With your explicit consent, we will use your data',
    'gate_id': 'gdpr_uk',
    'severity': 'ERROR',
    'confidence': 0.95
}

explanation = engine.generate_explanation(correction_data)

print(f"Reason: {explanation.reason_simple}")
print(f"Legal Basis: {explanation.legal_basis}")
print(f"Risk Reduction: {explanation.risk_reduction:.0%}")
```

**Output Example:**
```
Reason: Mandated by GDPR for data protection and privacy compliance (ERROR severity)
Legal Basis: UK GDPR Article 6 (Lawfulness of processing)
Risk Reduction: 76%
```

### 2. Legal Citation Manager (`legal_citations.py`)

Manages comprehensive legal citations for all UK regulations.

**Supported Regulations:**
- FCA Handbook (Financial Conduct Authority)
- UK GDPR (Data Protection)
- HMRC Tax Regulations
- UK Contract Law
- Employment Rights Act (Scotland)

**Key Features:**
- 15+ pre-loaded legal citations
- Deep linking to official sources
- Citation formatting (Bluebook, OSCOLA, Simple)
- Verification tracking
- Multi-jurisdiction support

**Example Usage:**
```python
from backend.core.explainability import LegalCitationManager

citation_manager = LegalCitationManager()

# Get citations for GDPR corrections
citations = citation_manager.get_citations_by_gate('gdpr_uk')

for citation in citations:
    print(f"{citation.title}")
    print(f"Reference: {citation.reference}")
    print(f"URL: {citation.url}")
    print(f"Excerpt: {citation.excerpt}")
    print()
```

**Citation Database:**
- `fca_prin_2_1_1r` - FCA Principles for Businesses
- `fca_prin_7` - Communications with clients
- `uk_gdpr_article_6` - Lawfulness of processing
- `uk_gdpr_article_7` - Conditions for consent
- `vat_act_1994_s4` - VAT scope
- `vat_threshold_2024` - Current VAT thresholds
- `contracts_third_parties_act_1999` - Third-party rights
- `employment_rights_act_1996_s1` - Employment particulars

### 3. Confidence Explainer (`confidence_explainer.py`)

Provides transparent breakdowns of confidence scores.

**Confidence Factors:**
1. **Pattern Match** (25%): How well it matches known patterns
2. **Regulatory Clarity** (20%): How clear the regulatory requirement is
3. **Context Fit** (15%): How appropriate for the document
4. **Historical Accuracy** (15%): Success rate in similar cases
5. **Expert Validation** (10%): Human expert review status
6. **Similarity Score** (5%): Similarity to known good corrections
7. **Legal Precedent** (5%): Strength of legal backing
8. **Consistency Check** (5%): Consistency with other corrections

**Confidence Levels:**
- **Very High** (90-100%): Auto-apply recommended
- **High** (75-89%): Safe to apply, minimal review
- **Medium** (50-74%): Review before applying
- **Low** (30-49%): Manual expert review required
- **Very Low** (0-29%): Do not auto-apply

**Example Usage:**
```python
from backend.core.explainability import ConfidenceExplainer

explainer = ConfidenceExplainer()

breakdown = explainer.explain_confidence(correction_data)

print(f"Overall Confidence: {breakdown.total_score:.0%}")
print(f"Level: {breakdown.confidence_level.value}")
print(f"\nTop Factors:")
for factor, score, explanation in breakdown.primary_factors:
    print(f"  - {factor}: {score:.0%}")
    print(f"    {explanation}")

print(f"\nRecommendation: {breakdown.recommendation}")
```

### 4. Impact Analyzer (`impact_analyzer.py`)

Analyzes downstream impacts of corrections.

**Impact Categories:**
- **Legal**: Compliance and legal risk impacts
- **Compliance**: Regulatory standing
- **Operational**: Business process impacts
- **Financial**: Cost and savings
- **Reputational**: Brand and trust impacts
- **Technical**: System and tool impacts
- **Documentation**: Other documents affected

**Impact Severity:**
- **Critical**: Major compliance/legal impact
- **High**: Significant operational impact
- **Medium**: Moderate impact
- **Low**: Minor impact
- **Minimal**: Negligible impact

**Example Usage:**
```python
from backend.core.explainability import ImpactAnalyzer

analyzer = ImpactAnalyzer()

impact = analyzer.analyze_impact(correction_data)

print(f"Overall Severity: {impact.overall_severity.value}")
print(f"Risk Before: {impact.risk_before:.0%}")
print(f"Risk After: {impact.risk_after:.0%}")
print(f"Risk Reduction: {impact.risk_reduction:.1f}%")

print("\nAffected Documents:")
for doc in impact.related_documents:
    print(f"  - {doc}")

print("\nImmediate Actions:")
for action in impact.immediate_actions:
    print(f"  - {action}")
```

### 5. Reasoning Chain (`reasoning_chain.py`)

Builds transparent step-by-step reasoning for every correction.

**Reasoning Steps:**
1. **Detection**: What issue was detected?
2. **Pattern Analysis**: Does it match known patterns?
3. **Regulatory Assessment**: What regulations apply?
4. **Context Evaluation**: Is it appropriate for this document?
5. **Solution Generation**: What correction should be applied?
6. **Alternative Evaluation**: Are there alternatives?
7. **Confidence Assessment**: How confident are we?
8. **Impact Analysis**: What are the impacts?
9. **Validation**: Does it pass all checks?
10. **Final Decision**: What's the recommendation?

**Example Usage:**
```python
from backend.core.explainability import ReasoningChain

chain_builder = ReasoningChain()

chain = chain_builder.build_chain(correction_data)

print(f"Total Steps: {chain.total_steps}")
print(f"Overall Confidence: {chain.overall_confidence:.0%}")

for step in chain.steps:
    print(f"\nStep {step.step_number}: {step.question}")
    print(f"Process: {step.process}")
    print(f"Result: {step.output}")
    print(f"Confidence: {step.confidence:.0%}")
```

### 6. Report Generator (`report_generator.py`)

Creates professional reports in multiple formats.

**Supported Formats:**
- **HTML**: Interactive web-based reports
- **Markdown**: Documentation-friendly format
- **JSON**: Machine-readable format
- **PDF-Ready**: Optimized for print/PDF export

**Report Sections:**
- Correction overview
- Detailed explanation
- Confidence analysis
- Reasoning chain
- Legal citations
- Impact analysis
- Action plan

**Example Usage:**
```python
from backend.core.explainability import ReportGenerator

generator = ReportGenerator()

# Generate HTML report
html_report = generator.generate_report(
    explanation_data=explanation.export_explanation('corr-001', 'json'),
    impact_data=impact.export_impact_report(impact_analysis),
    reasoning_chain=chain.export_chain('corr-001', 'detailed'),
    confidence_breakdown=asdict(breakdown),
    citations=citation_manager.export_citations('gdpr_uk')['citations'],
    format='html'
)

# Save report
with open('correction_report.html', 'w') as f:
    f.write(html_report)
```

### 7. Feedback Manager (`feedback_manager.py`)

Collects and analyzes user feedback for continuous improvement.

**Feedback Types:**
- **Accept**: Correction accepted as-is
- **Reject**: Correction rejected (with reason)
- **Modify**: Correction modified by user
- **Defer**: Correction deferred for review

**Rejection Reasons:**
- Inaccurate
- Inappropriate for context
- Too aggressive
- Too conservative
- Wrong regulatory interpretation
- Style mismatch
- Other (with details)

**Example Usage:**
```python
from backend.core.explainability import FeedbackManager, FeedbackType, RejectionReason

feedback_mgr = FeedbackManager()

# Submit feedback
feedback = feedback_mgr.submit_feedback(
    correction_id='corr-001',
    feedback_type=FeedbackType.ACCEPT,
    user_id='legal-001',
    user_role='legal_counsel',
    accuracy_rating=5,
    usefulness_rating=5,
    explanation_clarity_rating=4,
    comments='Excellent correction, clearly explained'
)

# Analyze feedback
analytics = feedback_mgr.analyze_feedback(gate_id='gdpr_uk')

print(f"Acceptance Rate: {analytics.acceptance_rate:.0%}")
print(f"Top Rejection Reasons:")
for reason, count in analytics.top_rejection_reasons:
    print(f"  - {reason}: {count}")

print(f"\nAreas for Improvement:")
for area in analytics.areas_for_improvement:
    print(f"  - {area}")
```

## Frontend Visualizer

The **Correction Visualizer** (`frontend/correction_visualizer.html`) provides an interactive web interface for exploring corrections.

**Features:**
- **Document View**: See corrections highlighted in context
- **Correction List**: Browse all identified corrections
- **Tabbed Details**: Explore explanations, confidence, reasoning, citations, and impact
- **Visual Indicators**: Color-coded severity and confidence levels
- **Action Buttons**: Accept, reject, modify, or export corrections
- **Responsive Design**: Works on desktop and tablet devices

**How to Use:**
1. Open `frontend/correction_visualizer.html` in a web browser
2. View the sample corrections loaded automatically
3. Click on any correction to see full details
4. Use tabs to explore different aspects of the correction
5. Use action buttons to provide feedback

## Integration Guide

### Basic Integration

```python
from backend.core.explainability import (
    ExplanationEngine,
    LegalCitationManager,
    ConfidenceExplainer,
    ImpactAnalyzer,
    ReasoningChain,
    ReportGenerator,
    FeedbackManager
)

# Initialize all components
explanation_engine = ExplanationEngine()
citation_manager = LegalCitationManager()
confidence_explainer = ConfidenceExplainer()
impact_analyzer = ImpactAnalyzer()
reasoning_chain = ReasoningChain()
report_generator = ReportGenerator()
feedback_manager = FeedbackManager()

# Process a correction
correction_data = {
    'correction_id': 'corr-001',
    'original_text': 'Original text here',
    'corrected_text': 'Corrected text here',
    'gate_id': 'gdpr_uk',
    'severity': 'ERROR',
    'confidence': 0.95,
    'document_type': 'privacy_policy'
}

# Generate explanation
explanation = explanation_engine.generate_explanation(correction_data)

# Get legal citations
citations = citation_manager.get_citations_by_gate(correction_data['gate_id'])

# Analyze confidence
confidence = confidence_explainer.explain_confidence(correction_data)

# Analyze impact
impact = impact_analyzer.analyze_impact(correction_data)

# Build reasoning chain
reasoning = reasoning_chain.build_chain(correction_data)

# Generate report
report = report_generator.generate_report(
    explanation_data=explanation.export_explanation(correction_data['correction_id'], 'json'),
    impact_data=impact.export_impact_report(impact),
    reasoning_chain=reasoning.export_chain(correction_data['correction_id'], 'detailed'),
    confidence_breakdown=asdict(confidence),
    citations=[asdict(c) for c in citations],
    format='html'
)

# Save report
with open(f"reports/{correction_data['correction_id']}.html", 'w') as f:
    f.write(report)

print(f"Report generated for {correction_data['correction_id']}")
```

### API Integration

```python
from fastapi import APIRouter, HTTPException
from backend.core.explainability import ExplanationEngine

router = APIRouter(prefix="/api/v1/explainability")

@router.post("/explain")
async def explain_correction(correction_data: dict):
    """Generate explanation for a correction"""
    try:
        engine = ExplanationEngine()
        explanation = engine.generate_explanation(correction_data)

        return {
            'correction_id': explanation.correction_id,
            'reason': explanation.reason_detailed,
            'legal_basis': explanation.legal_basis,
            'confidence': explanation.confidence_score,
            'citations': explanation.legal_citations,
            'impact': {
                'scope': explanation.impact_scope,
                'risk_reduction': explanation.risk_reduction
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/report/{correction_id}")
async def get_report(correction_id: str, format: str = 'html'):
    """Get full explainability report"""
    # Implementation here
    pass
```

## Best Practices

### 1. Always Provide Explanations
- Every correction should have at least a simple explanation
- Higher severity corrections require detailed explanations
- Include legal citations for all regulatory corrections

### 2. Maintain Citation Accuracy
- Verify legal citations every 6 months
- Update thresholds and values when regulations change
- Link to official government sources

### 3. Set Appropriate Confidence Thresholds
- Use ≥85% confidence for auto-apply
- Require manual review for <75% confidence
- Never auto-apply <50% confidence corrections

### 4. Collect Feedback Systematically
- Require feedback on all rejected corrections
- Track acceptance rates by gate and severity
- Use feedback to improve patterns

### 5. Generate Comprehensive Reports
- Include all explainability components
- Export reports for audit trails
- Store reports for compliance documentation

### 6. Monitor Performance
- Track acceptance rates weekly
- Review rejection reasons monthly
- Update patterns based on feedback

## Performance Metrics

The explainability system tracks:

- **Acceptance Rate**: Percentage of corrections accepted
- **Rejection Rate**: Percentage of corrections rejected
- **Modification Rate**: Percentage requiring user modification
- **Average Confidence**: Mean confidence across all corrections
- **Average Ratings**: User ratings for accuracy, usefulness, clarity
- **Processing Time**: Time to generate explanations and reports

**Target Metrics:**
- Acceptance Rate: >85%
- Average Confidence: >0.80
- Average User Rating: >4.0/5
- Report Generation: <500ms

## Compliance Benefits

### Regulatory Audit Support
- Complete audit trail for all corrections
- Legal citations ready for regulator review
- Clear documentation of compliance improvements

### Risk Reduction
- Transparent risk assessment before/after
- Quantified risk reduction percentages
- Clear action plans for remediation

### Stakeholder Communication
- Professional reports for board/executives
- Clear explanations for legal counsel
- Technical details for compliance officers

### Continuous Improvement
- Systematic feedback collection
- Performance analytics
- Learning from rejections

## Troubleshooting

### Low Confidence Scores
- Review pattern accuracy
- Validate regulatory interpretations
- Improve context detection
- Seek expert validation

### High Rejection Rates
- Analyze rejection reasons
- Update correction patterns
- Improve style matching
- Reduce correction aggressiveness

### Missing Citations
- Add citations to citation database
- Verify citation URLs
- Update citation excerpts
- Check jurisdiction mapping

### Slow Report Generation
- Optimize template rendering
- Cache citation data
- Pre-compute confidence factors
- Use async processing

## Future Enhancements

### Planned Features
- **Machine Learning**: Learn from feedback to improve confidence
- **Multi-Language**: Support for multiple languages
- **Advanced Visualizations**: Interactive charts and graphs
- **Comparison Tool**: Compare multiple correction strategies
- **Knowledge Base**: Searchable database of correction examples
- **API Expansion**: More granular API endpoints

### Roadmap
- Q1 2025: ML-based confidence tuning
- Q2 2025: Multi-language support
- Q3 2025: Advanced visualizations
- Q4 2025: Knowledge base integration

## Support

For questions or issues with the explainability system:

- **Documentation**: See this file and inline code documentation
- **Examples**: Check `backend/core/explainability/` for usage examples
- **Tests**: Review test files for integration patterns
- **Frontend**: See `frontend/correction_visualizer.html` for UI reference

## Conclusion

The LOKI Correction Explainability System provides complete transparency for document corrections, ensuring compliance officers and legal teams understand exactly why each correction was made, the legal basis, and the downstream impacts. By combining legal citations, confidence analysis, reasoning chains, and user feedback, the system enables informed decision-making and continuous improvement.

**Every correction is explainable. Every decision is transparent. Every change is traceable.**

---

**LOKI Enterprise Compliance Platform**
*Making compliance transparent, traceable, and trustworthy*
