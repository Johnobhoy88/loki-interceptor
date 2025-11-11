"""
Validation API routes
"""

from datetime import datetime
from typing import List, Optional
import hashlib

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from ..models.validation import (
    ValidationRequest,
    ValidationResponse,
    ValidationResult,
    ModuleResult,
    GateResult,
    RiskLevel,
    SeverityLevel,
    UniversalAnalyzerResult
)
from ..dependencies import (
    get_engine,
    get_cache,
    get_audit_logger,
    check_rate_limit,
    get_request_timer,
    RequestTimer
)

router = APIRouter()


def _hash_text(text: str) -> str:
    """Generate SHA-256 hash of text"""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def _convert_gate_result(gate_data: dict) -> GateResult:
    """Convert engine gate result to API model"""
    return GateResult(
        gate_id=gate_data.get('gate_id', 'unknown'),
        gate_name=gate_data.get('gate_name', gate_data.get('gate_id', 'Unknown')),
        passed=gate_data.get('passed', True),
        severity=SeverityLevel(gate_data.get('severity', 'INFO')),
        message=gate_data.get('message', ''),
        legal_source=gate_data.get('legal_source'),
        snippets=gate_data.get('snippets', []),
        suggestions=gate_data.get('suggestions', []),
        metadata=gate_data.get('metadata', {})
    )


def _convert_module_result(module_id: str, module_data: dict) -> ModuleResult:
    """Convert engine module result to API model"""
    gates = []
    gates_checked = 0
    gates_passed = 0
    gates_failed = 0

    # Parse gates from module data
    if 'gates' in module_data:
        for gate_data in module_data['gates']:
            if isinstance(gate_data, dict):
                gates.append(_convert_gate_result(gate_data))
                gates_checked += 1
                if gate_data.get('passed', True):
                    gates_passed += 1
                else:
                    gates_failed += 1

    # Determine risk level
    if gates_failed == 0:
        risk_level = RiskLevel.LOW
    elif gates_failed < gates_checked * 0.3:
        risk_level = RiskLevel.MEDIUM
    elif gates_failed < gates_checked * 0.6:
        risk_level = RiskLevel.HIGH
    else:
        risk_level = RiskLevel.CRITICAL

    return ModuleResult(
        module_id=module_id,
        module_name=module_data.get('name', module_id.replace('_', ' ').title()),
        gates_checked=gates_checked,
        gates_passed=gates_passed,
        gates_failed=gates_failed,
        risk_level=risk_level,
        gates=gates,
        execution_time_ms=module_data.get('execution_time_ms', 0.0)
    )


def _convert_validation_result(
    engine_result: dict,
    timer: RequestTimer,
    cached: bool = False
) -> ValidationResult:
    """Convert engine validation result to API model"""

    # Convert modules
    modules = []
    total_gates_checked = 0
    total_gates_failed = 0

    if 'modules' in engine_result and isinstance(engine_result['modules'], dict):
        for module_id, module_data in engine_result['modules'].items():
            if isinstance(module_data, dict) and not module_data.get('error'):
                module_result = _convert_module_result(module_id, module_data)
                modules.append(module_result)
                total_gates_checked += module_result.gates_checked
                total_gates_failed += module_result.gates_failed

    # Convert universal analyzers
    universal_analyzers = []
    if 'universal' in engine_result:
        universal_data = engine_result['universal']
        if isinstance(universal_data, dict):
            for analyzer_name, analyzer_data in universal_data.items():
                if isinstance(analyzer_data, dict):
                    universal_analyzers.append(
                        UniversalAnalyzerResult(
                            name=analyzer_name,
                            detected=analyzer_data.get('detected', False),
                            count=analyzer_data.get('count', 0),
                            details=analyzer_data
                        )
                    )

    # Determine overall risk
    overall_risk = RiskLevel(engine_result.get('overall_risk', 'LOW'))

    return ValidationResult(
        document_hash=engine_result.get('document_hash', ''),
        timestamp=engine_result.get('timestamp', datetime.utcnow().isoformat()),
        overall_risk=overall_risk,
        modules=modules,
        universal_analyzers=universal_analyzers,
        total_gates_checked=total_gates_checked,
        total_gates_failed=total_gates_failed,
        execution_time_ms=timer.elapsed_ms(),
        cached=cached
    )


@router.post(
    "/validate",
    response_model=ValidationResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate document",
    description="Validate a document against compliance modules",
    response_description="Validation results with risk assessment"
)
async def validate_document(
    request: ValidationRequest,
    timer: RequestTimer = Depends(get_request_timer),
    _: bool = Depends(check_rate_limit)
):
    """
    Validate a document against compliance modules

    This endpoint performs comprehensive compliance validation on the provided text.

    **Process:**
    1. Check cache for existing results (if use_cache=true)
    2. Run validation against specified modules (or all if not specified)
    3. Analyze with universal analyzers (PII, contradictions, etc.)
    4. Calculate overall risk score
    5. Return detailed results

    **Risk Levels:**
    - LOW: No significant issues found
    - MEDIUM: Some non-critical issues found
    - HIGH: Multiple issues or critical issues found
    - CRITICAL: Severe compliance violations found

    **Example:**
    ```json
    {
      "text": "This employment contract is subject to Scottish law...",
      "document_type": "employment_contract",
      "modules": ["hr_scottish", "uk_employment"],
      "use_cache": true,
      "include_suggestions": true
    }
    ```
    """
    engine = get_engine()
    cache = get_cache()
    audit_logger = get_audit_logger()

    # Determine modules to check
    modules = request.modules or list(engine.modules.keys())

    # Check cache if enabled
    if request.use_cache:
        cached_result = cache.get(request.text, request.document_type, modules)
        if cached_result:
            validation = _convert_validation_result(cached_result, timer, cached=True)
            return ValidationResponse(
                validation=validation,
                risk=validation.overall_risk,
                suggestions_available=request.include_suggestions
            )

    # Run validation
    try:
        engine_result = engine.check_document(
            text=request.text,
            document_type=request.document_type,
            active_modules=modules
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation engine error: {str(e)}"
        )

    # Cache result
    if request.use_cache:
        cache.set(request.text, request.document_type, modules, engine_result)

    # Log to audit
    try:
        audit_logger.log_validation(
            request.text,
            request.document_type,
            modules,
            engine_result,
            request.metadata.get('client_id', 'unknown')
        )
    except Exception:
        # Don't fail request if audit logging fails
        pass

    # Convert to API model
    validation = _convert_validation_result(engine_result, timer, cached=False)

    return ValidationResponse(
        validation=validation,
        risk=validation.overall_risk,
        suggestions_available=request.include_suggestions
    )


@router.post(
    "/validate/batch",
    response_model=List[ValidationResponse],
    status_code=status.HTTP_200_OK,
    summary="Batch validate documents",
    description="Validate multiple documents in a single request",
    response_description="List of validation results"
)
async def validate_documents_batch(
    requests: List[ValidationRequest],
    timer: RequestTimer = Depends(get_request_timer),
    _: bool = Depends(check_rate_limit)
):
    """
    Validate multiple documents in a single request

    This endpoint allows batch validation of up to 10 documents.

    **Limitations:**
    - Maximum 10 documents per batch
    - Each document is validated independently
    - Results returned in the same order as requests

    **Example:**
    ```json
    [
      {
        "text": "Document 1...",
        "document_type": "contract"
      },
      {
        "text": "Document 2...",
        "document_type": "policy"
      }
    ]
    ```
    """
    if len(requests) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 documents per batch request"
        )

    results = []
    for req in requests:
        result = await validate_document(req, timer, True)
        results.append(result)

    return results
