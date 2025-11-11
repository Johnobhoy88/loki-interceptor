"""
Correction API routes
"""

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from ..models.correction import (
    CorrectionRequest,
    CorrectionResponse,
    CorrectionIssue,
    CorrectionApplication
)
from ..dependencies import (
    get_corrector,
    check_rate_limit,
    get_request_timer,
    RequestTimer
)

router = APIRouter()


@router.post(
    "/correct",
    response_model=CorrectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Correct document",
    description="Apply rule-based corrections to compliance issues",
    response_description="Document with corrections applied"
)
async def correct_document(
    request: CorrectionRequest,
    timer: RequestTimer = Depends(get_request_timer),
    _: bool = Depends(check_rate_limit)
):
    """
    Apply rule-based corrections to document based on validation results

    This endpoint applies **deterministic, rule-based corrections** to compliance issues.
    No AI or ML models are used - all corrections are based on predefined rules.

    **Process:**
    1. Analyze validation results to identify correctable issues
    2. Generate correction suggestions with confidence scores
    3. Apply corrections (if auto_apply=true and confidence >= threshold)
    4. Return original and corrected text with detailed change log

    **Confidence Scores:**
    - 0.95-1.0: High confidence (safe to auto-apply)
    - 0.8-0.95: Medium-high confidence
    - 0.6-0.8: Medium confidence (review recommended)
    - <0.6: Low confidence (manual review required)

    **Example:**
    ```json
    {
      "text": "We may use your data for marketing purposes.",
      "validation_results": {...},
      "auto_apply": true,
      "confidence_threshold": 0.8
    }
    ```

    **Response:**
    ```json
    {
      "original_text": "We may use your data...",
      "corrected_text": "With your explicit consent, we will use your data...",
      "issues_found": 5,
      "issues_corrected": 4,
      "corrections": [...],
      "suggestions": [...]
    }
    ```
    """
    corrector = get_corrector()

    try:
        # Apply corrections
        correction_result = corrector.correct_document(
            request.text,
            request.validation_results
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Correction engine error: {str(e)}"
        )

    # Parse correction results
    issues_found = correction_result.get('issues_found', 0)
    issues_corrected = correction_result.get('issues_corrected', 0)
    corrected_text = correction_result.get('corrected_text', request.text)

    # Convert to API models
    corrections: List[CorrectionApplication] = []
    suggestions: List[CorrectionIssue] = []

    for idx, correction in enumerate(correction_result.get('corrections', [])):
        if isinstance(correction, dict):
            corrections.append(
                CorrectionApplication(
                    issue_id=correction.get('issue_id', f"ISSUE_{idx}"),
                    position=correction.get('position', 0),
                    length=correction.get('length', 0),
                    original=correction.get('original', ''),
                    corrected=correction.get('corrected', '')
                )
            )

    for idx, suggestion in enumerate(correction_result.get('suggestions', [])):
        if isinstance(suggestion, dict):
            suggestions.append(
                CorrectionIssue(
                    issue_id=suggestion.get('issue_id', f"SUGGEST_{idx}"),
                    gate_id=suggestion.get('gate_id', 'unknown'),
                    severity=suggestion.get('severity', 'WARNING'),
                    original_text=suggestion.get('original_text', ''),
                    suggested_text=suggestion.get('suggested_text', ''),
                    explanation=suggestion.get('explanation', ''),
                    confidence=suggestion.get('confidence', 0.5),
                    applied=suggestion.get('applied', False)
                )
            )

    # Calculate improvement score
    improvement_score = 0.0
    if issues_found > 0:
        improvement_score = min(1.0, issues_corrected / issues_found)

    return CorrectionResponse(
        original_text=request.text,
        corrected_text=corrected_text,
        issues_found=issues_found,
        issues_corrected=issues_corrected,
        corrections=corrections,
        suggestions=suggestions,
        improvement_score=improvement_score,
        metadata={
            'execution_time_ms': timer.elapsed_ms(),
            'auto_applied': request.auto_apply,
            'confidence_threshold': request.confidence_threshold
        }
    )


@router.post(
    "/synthesize",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Synthesize compliant document",
    description="Generate compliant document draft from validation results",
    response_description="Synthesized compliant document"
)
async def synthesize_document(
    base_text: str,
    validation: dict,
    context: dict = None,
    modules: List[str] = None,
    timer: RequestTimer = Depends(get_request_timer),
    _: bool = Depends(check_rate_limit)
):
    """
    Generate deterministic compliance draft using universal synthesis engine

    This endpoint uses **deterministic synthesis** to generate compliant document drafts.
    No AI models are used - synthesis is based on predefined templates and rules.

    **Process:**
    1. Analyze validation results
    2. Select appropriate compliance templates
    3. Generate compliant text sections
    4. Merge with original text
    5. Return synthesized document

    **Example:**
    ```json
    {
      "base_text": "This is an employment contract...",
      "validation": {...},
      "context": {"jurisdiction": "UK", "industry": "tech"},
      "modules": ["hr_scottish", "uk_employment"]
    }
    ```
    """
    from ..dependencies import get_synthesis_engine

    try:
        synthesis_engine = get_synthesis_engine()
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Synthesis engine not available"
        )

    try:
        result = synthesis_engine.synthesize(
            base_text=base_text,
            validation=validation,
            context=context or {},
            modules=modules
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Synthesis engine error: {str(e)}"
        )

    return {
        **result,
        'execution_time_ms': timer.elapsed_ms()
    }
