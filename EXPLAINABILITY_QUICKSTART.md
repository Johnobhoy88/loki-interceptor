# LOKI Explainability System - Quick Start Guide

## What is the Explainability System?

The LOKI Explainability System makes every document correction **transparent, traceable, and trustworthy**. It answers:
- **WHY** was this correction made?
- **WHAT** legal basis supports it?
- **HOW** confident are we?
- **WHAT** is the impact?
- **HOW** was the decision made?

## 5-Minute Quick Start

### 1. Basic Usage

```python
from backend.core.explainability import ExplanationEngine

# Create engine
engine = ExplanationEngine()

# Explain a correction
correction = {
    'original_text': 'We may use your data',
    'corrected_text': 'With your explicit consent, we will use your data',
    'gate_id': 'gdpr_uk',
    'severity': 'ERROR',
    'confidence': 0.95
}

explanation = engine.generate_explanation(correction)

# Get results
print(f"Why: {explanation.reason_simple}")
print(f"Legal: {explanation.legal_basis}")
print(f"Confidence: {explanation.confidence_score:.0%}")
print(f"Risk Reduced: {explanation.risk_reduction:.0%}")
```

### 2. Get Legal Citations

```python
from backend.core.explainability import LegalCitationManager

citations = LegalCitationManager()

# Get citations for GDPR
for citation in citations.get_citations_by_gate('gdpr_uk'):
    print(f"{citation.title}")
    print(f"  {citation.url}")
```

### 3. Explain Confidence

```python
from backend.core.explainability import ConfidenceExplainer

explainer = ConfidenceExplainer()
breakdown = explainer.explain_confidence(correction)

print(f"Confidence: {breakdown.total_score:.0%}")
print(f"Level: {breakdown.confidence_level.value}")
print(f"Recommendation: {breakdown.recommendation}")
```

### 4. Analyze Impact

```python
from backend.core.explainability import ImpactAnalyzer

analyzer = ImpactAnalyzer()
impact = analyzer.analyze_impact(correction)

print(f"Risk Reduction: {impact.risk_reduction:.0%}")
print(f"Affected Documents: {len(impact.related_documents)}")
print(f"Immediate Actions: {len(impact.immediate_actions)}")
```

### 5. Generate Report

```python
from backend.core.explainability import ReportGenerator

generator = ReportGenerator()

# Generate HTML report
report = generator.generate_report(
    explanation_data=explanation.__dict__,
    impact_data=impact.__dict__,
    reasoning_chain={},
    confidence_breakdown={},
    citations=[],
    format='html'
)

# Save
with open('report.html', 'w') as f:
    f.write(report)
```

## Key Components

| Component | Purpose | Key Output |
|-----------|---------|------------|
| **Explanation Engine** | Core explanations | Why correction was made |
| **Legal Citations** | Legal basis | Official regulations & links |
| **Confidence Explainer** | Confidence breakdown | Score + factors |
| **Impact Analyzer** | Downstream effects | Risk + action plan |
| **Reasoning Chain** | Step-by-step logic | Decision process |
| **Report Generator** | Visual reports | HTML/PDF/Markdown |
| **Feedback Manager** | User feedback | Analytics + learning |

## Common Use Cases

### Use Case 1: Auto-Apply Decision
```python
# Should we auto-apply this correction?
confidence = explainer.explain_confidence(correction)

if confidence.total_score >= 0.85:
    print("✓ Safe to auto-apply")
    apply_correction(correction)
else:
    print("✗ Requires manual review")
    send_for_review(correction)
```

### Use Case 2: Stakeholder Report
```python
# Generate report for legal team
report = generator.generate_report(
    explanation_data=explanation,
    impact_data=impact,
    reasoning_chain=chain,
    confidence_breakdown=confidence,
    citations=citations,
    format='pdf_ready'
)

send_to_legal(report)
```

### Use Case 3: Audit Trail
```python
# Create audit trail for compliance
trail = {
    'correction_id': correction['correction_id'],
    'timestamp': datetime.utcnow(),
    'explanation': explanation.reason_detailed,
    'legal_basis': explanation.legal_basis,
    'confidence': explanation.confidence_score,
    'citations': [c.reference for c in citations],
    'approved_by': user_id
}

save_audit_trail(trail)
```

### Use Case 4: Feedback Collection
```python
from backend.core.explainability import FeedbackManager, FeedbackType

feedback_mgr = FeedbackManager()

# User accepts correction
feedback_mgr.submit_feedback(
    correction_id='corr-001',
    feedback_type=FeedbackType.ACCEPT,
    user_id='legal-001',
    user_role='legal_counsel',
    accuracy_rating=5,
    usefulness_rating=5
)

# Analyze performance
analytics = feedback_mgr.analyze_feedback()
print(f"Acceptance Rate: {analytics.acceptance_rate:.0%}")
```

## Confidence Levels Guide

| Score | Level | Meaning | Action |
|-------|-------|---------|--------|
| 90-100% | Very High | Explicit requirement | Auto-apply |
| 75-89% | High | Strong guidance | Apply with minimal review |
| 50-74% | Medium | Best practice | Review before apply |
| 30-49% | Low | Interpretation | Expert review required |
| 0-29% | Very Low | Uncertain | Do not auto-apply |

## Visual Dashboard

Open `frontend/correction_visualizer.html` in a browser to see:
- Interactive document view with highlighted corrections
- Correction list with confidence indicators
- Detailed explainability tabs
- Visual reasoning chains
- Legal citations with links
- Impact analysis charts

## Integration with Existing Code

### With Document Corrector
```python
from backend.core.corrector import DocumentCorrector
from backend.core.explainability import ExplanationEngine

# Apply corrections
corrector = DocumentCorrector(advanced_mode=True)
result = corrector.correct(document, validation_results)

# Explain corrections
explainer = ExplanationEngine()
for correction in result['corrections']:
    explanation = explainer.generate_explanation(correction)
    print(f"Applied: {correction['corrected_text']}")
    print(f"Reason: {explanation.reason_simple}")
```

### With API Endpoints
```python
from fastapi import APIRouter
from backend.core.explainability import ExplanationEngine

router = APIRouter()

@router.post("/api/v1/corrections/explain")
async def explain_correction(correction_data: dict):
    engine = ExplanationEngine()
    explanation = engine.generate_explanation(correction_data)

    return {
        'reason': explanation.reason_detailed,
        'legal_basis': explanation.legal_basis,
        'confidence': explanation.confidence_score,
        'citations': explanation.legal_citations
    }
```

## Best Practices

### ✅ DO
- Always generate explanations for corrections
- Include legal citations for regulatory corrections
- Set confidence thresholds (≥85% for auto-apply)
- Collect user feedback systematically
- Generate reports for audit trails
- Store explainability data with corrections

### ❌ DON'T
- Auto-apply low confidence corrections (<75%)
- Skip explanation generation for any correction
- Ignore user feedback
- Use outdated legal citations
- Apply corrections without legal basis

## Troubleshooting

### Problem: Low Confidence Scores
**Solution:**
- Review pattern accuracy
- Validate regulatory interpretations
- Improve context detection
- Seek expert validation

### Problem: High Rejection Rates
**Solution:**
- Analyze rejection reasons
- Update correction patterns
- Improve style matching
- Reduce correction aggressiveness

### Problem: Missing Legal Citations
**Solution:**
```python
# Add new citation
citation_manager = LegalCitationManager()
citation_manager._add_citation(LegalCitation(
    citation_id='new_citation',
    title='New Regulation',
    reference='REG 2024/1',
    citation_type=CitationType.REGULATION,
    jurisdiction=Jurisdiction.UK,
    url='https://example.com',
    excerpt='Regulation text...',
    relevance='Applies to...',
    status='in_force'
))
```

## Example Output

### Simple Explanation
```
"Mandated by GDPR for data protection and privacy compliance (ERROR severity)"
```

### Detailed Explanation
```
This correction addresses a compliance issue identified in your document.
Under GDPR Article 6, all data processing must have a lawful basis. The
original text did not clearly establish explicit consent, which could result
in regulatory violations and fines up to 4% of annual turnover. This
correction updates the text to meet current requirements, ensuring compliance
and reducing risk.
```

### Confidence Breakdown
```
Overall Confidence: 95%
Level: VERY HIGH

Primary Factors:
  - Pattern Match: 95% (Exact pattern match from library)
  - Regulatory Clarity: 90% (Explicit requirement)
  - Context Fit: 85% (Appropriate for document type)

Recommendation: Apply this correction automatically. Safe for production use.
```

### Impact Summary
```
Risk Reduction: 76%
Severity: CRITICAL

Affected Areas:
  - Legal Compliance
  - Privacy Policy
  - Data Processing Agreements

Immediate Actions:
  - Apply this correction to the document
  - Update compliance documentation
  - Review with legal counsel
```

## Testing

Run the test suite:
```bash
cd /home/user/loki-interceptor/backend/core/explainability
python test_explainability.py
```

This will:
- Test GDPR correction explanations
- Test Tax correction explanations
- Test FCA correction explanations
- Test feedback management
- Generate sample reports

## Support

For more information:
- **Full Documentation**: See `CORRECTION_EXPLAINABILITY.md`
- **API Reference**: See inline code documentation
- **Examples**: See `test_explainability.py`
- **Frontend**: See `frontend/correction_visualizer.html`

## Next Steps

1. **Integrate**: Add explainability to your correction workflow
2. **Customize**: Adjust confidence thresholds for your needs
3. **Monitor**: Track acceptance rates and feedback
4. **Improve**: Use feedback to refine patterns
5. **Report**: Generate reports for stakeholders

---

**LOKI Enterprise Compliance Platform**
*Every correction is explainable. Every decision is transparent.*
