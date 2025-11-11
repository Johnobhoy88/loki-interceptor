"""
Enhanced Correction API v2 - Production-Ready Correction System

Features:
- Advanced correction orchestration
- Batch processing
- Real-time streaming
- Async scheduling
- Multi-format export
- Webhooks
- Rate limiting
- Versioning
"""

import asyncio
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field, validator

from ..dependencies import (
    get_corrector,
    check_rate_limit,
    get_request_timer,
    RequestTimer,
    get_cache
)


# ==================== Models ====================

class CorrectionFormat(str, Enum):
    """Supported export formats"""
    JSON = "json"
    XML = "xml"
    DOCX = "docx"
    HTML = "html"
    MARKDOWN = "markdown"


class CorrectionPriority(str, Enum):
    """Job priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class CorrectionStage(str, Enum):
    """Pipeline stages"""
    VALIDATE = "validate"
    ANALYZE = "analyze"
    CORRECT = "correct"
    VERIFY = "verify"
    EXPORT = "export"


class CorrectionRequest(BaseModel):
    """Enhanced correction request"""
    text: str = Field(..., min_length=1, max_length=10485760, description="Document text (max 10MB)")
    validation_results: Optional[Dict] = Field(None, description="Validation results from engine")
    document_type: Optional[str] = Field(None, description="Document type for context-aware corrections")
    auto_apply: bool = Field(True, description="Auto-apply high-confidence corrections")
    confidence_threshold: float = Field(0.8, ge=0.0, le=1.0, description="Confidence threshold for auto-apply")
    pipeline_stages: List[CorrectionStage] = Field(
        default_factory=lambda: [CorrectionStage.VALIDATE, CorrectionStage.ANALYZE, CorrectionStage.CORRECT, CorrectionStage.VERIFY],
        description="Pipeline stages to execute"
    )
    export_format: CorrectionFormat = Field(CorrectionFormat.JSON, description="Export format")
    enable_caching: bool = Field(True, description="Enable result caching")
    algorithm_version: Optional[str] = Field(None, description="Specific correction algorithm version")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

    @validator('text')
    def validate_text_size(cls, v):
        """Validate text size"""
        if len(v.encode('utf-8')) > 10485760:  # 10MB
            raise ValueError("Document size exceeds 10MB limit")
        return v


class BatchCorrectionRequest(BaseModel):
    """Batch correction request"""
    documents: List[Dict[str, Any]] = Field(..., min_items=1, max_items=1000, description="Documents to correct (max 1000)")
    parallel: bool = Field(True, description="Process documents in parallel")
    priority: CorrectionPriority = Field(CorrectionPriority.NORMAL, description="Batch job priority")
    webhook_url: Optional[str] = Field(None, description="Webhook URL for completion notification")
    export_format: CorrectionFormat = Field(CorrectionFormat.JSON, description="Export format for all documents")

    @validator('documents')
    def validate_documents(cls, v):
        """Validate documents list"""
        total_size = sum(len(str(doc).encode('utf-8')) for doc in v)
        if total_size > 104857600:  # 100MB total
            raise ValueError("Total batch size exceeds 100MB limit")
        return v


class CorrectionJobRequest(BaseModel):
    """Async correction job request"""
    text: str = Field(..., min_length=1)
    validation_results: Optional[Dict] = None
    priority: CorrectionPriority = Field(CorrectionPriority.NORMAL)
    webhook_url: Optional[str] = None
    callback_data: Optional[Dict] = None


class CorrectionResponse(BaseModel):
    """Enhanced correction response"""
    job_id: str = Field(..., description="Unique job identifier")
    original_text: str
    corrected_text: str
    issues_found: int
    issues_corrected: int
    corrections: List[Dict[str, Any]]
    suggestions: List[Dict[str, Any]]
    improvement_score: float = Field(..., ge=0.0, le=1.0)
    algorithm_version: str = Field(default="2.0.0")
    pipeline_execution: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BatchCorrectionResponse(BaseModel):
    """Batch correction response"""
    batch_id: str
    status: str
    total_documents: int
    completed: int
    failed: int
    results: List[Dict[str, Any]] = Field(default_factory=list)
    started_at: datetime
    completed_at: Optional[datetime] = None
    execution_time_ms: Optional[float] = None


class JobStatusResponse(BaseModel):
    """Job status response"""
    job_id: str
    status: str  # queued, processing, completed, failed
    progress: float = Field(..., ge=0.0, le=100.0)
    stage: Optional[CorrectionStage] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    estimated_completion: Optional[datetime] = None


class QuotaInfo(BaseModel):
    """Quota information"""
    user_id: str
    requests_used: int
    requests_limit: int
    requests_remaining: int
    reset_at: datetime
    rate_limit_per_minute: int


# ==================== Router ====================

router = APIRouter()


# ==================== Correction Endpoints ====================

@router.post(
    "/correct/advanced",
    response_model=CorrectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Advanced document correction",
    description="Apply corrections with full pipeline control and advanced options"
)
async def correct_document_advanced(
    request: CorrectionRequest,
    background_tasks: BackgroundTasks,
    timer: RequestTimer = Depends(get_request_timer),
    _: bool = Depends(check_rate_limit)
):
    """
    Advanced document correction with pipeline control

    **Features:**
    - Multi-stage pipeline execution
    - Algorithm versioning
    - Result caching
    - Multiple export formats
    - Detailed execution tracking

    **Pipeline Stages:**
    1. **VALIDATE**: Validate document and inputs
    2. **ANALYZE**: Analyze issues and determine corrections
    3. **CORRECT**: Apply corrections
    4. **VERIFY**: Verify correction quality
    5. **EXPORT**: Export in requested format

    **Example:**
    ```json
    {
      "text": "Your document text...",
      "pipeline_stages": ["validate", "analyze", "correct", "verify"],
      "export_format": "json",
      "algorithm_version": "2.0.0"
    }
    ```
    """
    from ...core.correction_pipeline import CorrectionPipeline

    job_id = str(uuid.uuid4())

    try:
        # Initialize pipeline
        pipeline = CorrectionPipeline(
            algorithm_version=request.algorithm_version or "2.0.0",
            enable_caching=request.enable_caching
        )

        # Execute pipeline
        result = await pipeline.execute(
            text=request.text,
            validation_results=request.validation_results,
            document_type=request.document_type,
            stages=request.pipeline_stages,
            auto_apply=request.auto_apply,
            confidence_threshold=request.confidence_threshold
        )

        # Export in requested format
        if request.export_format != CorrectionFormat.JSON:
            from ...core.correction_exporter import CorrectionExporter
            exporter = CorrectionExporter()
            result['export'] = await exporter.export(result, request.export_format)

        # Cache result if enabled
        if request.enable_caching:
            cache = get_cache()
            cache_key = f"correction:{job_id}"
            cache.set(cache_key, result, expire=3600)  # Cache for 1 hour

        return CorrectionResponse(
            job_id=job_id,
            original_text=result['original_text'],
            corrected_text=result['corrected_text'],
            issues_found=result['issues_found'],
            issues_corrected=result['issues_corrected'],
            corrections=result['corrections'],
            suggestions=result.get('suggestions', []),
            improvement_score=result['improvement_score'],
            algorithm_version=result['algorithm_version'],
            pipeline_execution=result['pipeline_execution'],
            metadata={
                **request.metadata,
                'execution_time_ms': timer.elapsed_ms(),
                'export_format': request.export_format.value,
                'stages_executed': [s.value for s in request.pipeline_stages]
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Correction pipeline error: {str(e)}"
        )


@router.post(
    "/correct/batch",
    response_model=BatchCorrectionResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Batch document correction",
    description="Process multiple documents in batch (async)"
)
async def correct_batch(
    request: BatchCorrectionRequest,
    background_tasks: BackgroundTasks,
    _: bool = Depends(check_rate_limit)
):
    """
    Process multiple documents in batch

    **Features:**
    - Process up to 1000 documents per batch
    - Parallel or sequential processing
    - Priority queuing
    - Webhook notifications
    - Progress tracking

    **Example:**
    ```json
    {
      "documents": [
        {"text": "Document 1...", "validation_results": {...}},
        {"text": "Document 2...", "validation_results": {...}}
      ],
      "parallel": true,
      "priority": "high",
      "webhook_url": "https://example.com/webhook"
    }
    ```
    """
    from ...core.batch_corrector import BatchCorrector

    batch_id = str(uuid.uuid4())

    try:
        # Initialize batch corrector
        batch_corrector = BatchCorrector(
            batch_id=batch_id,
            priority=request.priority,
            webhook_url=request.webhook_url
        )

        # Start batch processing in background
        background_tasks.add_task(
            batch_corrector.process_batch,
            documents=request.documents,
            parallel=request.parallel,
            export_format=request.export_format
        )

        return BatchCorrectionResponse(
            batch_id=batch_id,
            status="queued",
            total_documents=len(request.documents),
            completed=0,
            failed=0,
            started_at=datetime.utcnow()
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch processing error: {str(e)}"
        )


@router.get(
    "/correct/batch/{batch_id}",
    response_model=BatchCorrectionResponse,
    summary="Get batch status",
    description="Get status and results of batch correction job"
)
async def get_batch_status(batch_id: str):
    """Get batch correction status and results"""
    from ...core.batch_corrector import BatchCorrector

    try:
        status_info = await BatchCorrector.get_batch_status(batch_id)
        if not status_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Batch {batch_id} not found"
            )
        return status_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching batch status: {str(e)}"
        )


@router.post(
    "/correct/schedule",
    response_model=JobStatusResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Schedule async correction",
    description="Schedule correction job for async processing"
)
async def schedule_correction(
    request: CorrectionJobRequest,
    _: bool = Depends(check_rate_limit)
):
    """
    Schedule correction for async processing

    **Features:**
    - Queue-based async processing
    - Priority scheduling
    - Webhook notifications
    - Job status tracking

    **Example:**
    ```json
    {
      "text": "Document text...",
      "priority": "high",
      "webhook_url": "https://example.com/webhook",
      "callback_data": {"user_id": "123"}
    }
    ```
    """
    from ...core.correction_scheduler import CorrectionScheduler

    job_id = str(uuid.uuid4())

    try:
        scheduler = CorrectionScheduler()

        # Schedule job
        job_info = await scheduler.schedule_job(
            job_id=job_id,
            text=request.text,
            validation_results=request.validation_results,
            priority=request.priority,
            webhook_url=request.webhook_url,
            callback_data=request.callback_data
        )

        return JobStatusResponse(
            job_id=job_id,
            status="queued",
            progress=0.0,
            created_at=job_info['created_at'],
            updated_at=job_info['updated_at'],
            estimated_completion=job_info.get('estimated_completion')
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Job scheduling error: {str(e)}"
        )


@router.get(
    "/correct/jobs/{job_id}",
    response_model=JobStatusResponse,
    summary="Get job status",
    description="Get status and result of scheduled correction job"
)
async def get_job_status(job_id: str):
    """Get correction job status"""
    from ...core.correction_scheduler import CorrectionScheduler

    try:
        scheduler = CorrectionScheduler()
        job_info = await scheduler.get_job_status(job_id)

        if not job_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found"
            )

        return JobStatusResponse(**job_info)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching job status: {str(e)}"
        )


@router.websocket("/correct/stream")
async def correction_stream(websocket: WebSocket):
    """
    Real-time correction streaming for large documents

    **Protocol:**
    1. Client sends: {"text": "...", "validation_results": {...}}
    2. Server streams: {"stage": "...", "progress": 0.0-100.0, "data": {...}}
    3. Server sends final: {"status": "completed", "result": {...}}
    """
    from ...core.streaming_corrector import StreamingCorrector

    await websocket.accept()

    try:
        # Receive request
        data = await websocket.receive_json()
        text = data.get('text')
        validation_results = data.get('validation_results')

        if not text:
            await websocket.send_json({"error": "Missing 'text' field"})
            await websocket.close()
            return

        # Initialize streaming corrector
        streamer = StreamingCorrector(websocket)

        # Stream corrections
        await streamer.stream_corrections(text, validation_results)

    except WebSocketDisconnect:
        print(f"WebSocket disconnected")
    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        try:
            await websocket.close()
        except:
            pass


@router.get(
    "/correct/export/{job_id}",
    summary="Export correction result",
    description="Export correction result in specified format"
)
async def export_correction(
    job_id: str,
    format: CorrectionFormat = Query(CorrectionFormat.JSON, description="Export format")
):
    """Export correction result in various formats"""
    from ...core.correction_exporter import CorrectionExporter

    try:
        # Get cached result
        cache = get_cache()
        cache_key = f"correction:{job_id}"
        result = cache.get(cache_key)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found or expired"
            )

        # Export in requested format
        exporter = CorrectionExporter()
        exported = await exporter.export(result, format)

        # Return appropriate response based on format
        if format == CorrectionFormat.JSON:
            return JSONResponse(content=exported)
        elif format == CorrectionFormat.DOCX:
            return StreamingResponse(
                iter([exported]),
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                headers={"Content-Disposition": f"attachment; filename=correction_{job_id}.docx"}
            )
        elif format == CorrectionFormat.XML:
            return StreamingResponse(
                iter([exported]),
                media_type="application/xml",
                headers={"Content-Disposition": f"attachment; filename=correction_{job_id}.xml"}
            )
        elif format == CorrectionFormat.HTML:
            return StreamingResponse(
                iter([exported]),
                media_type="text/html",
                headers={"Content-Disposition": f"attachment; filename=correction_{job_id}.html"}
            )
        elif format == CorrectionFormat.MARKDOWN:
            return StreamingResponse(
                iter([exported]),
                media_type="text/markdown",
                headers={"Content-Disposition": f"attachment; filename=correction_{job_id}.md"}
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export error: {str(e)}"
        )


@router.get(
    "/correct/quota",
    response_model=QuotaInfo,
    summary="Get quota information",
    description="Get rate limiting and quota information"
)
async def get_quota_info(user_id: str = Query(..., description="User identifier")):
    """Get rate limiting and quota information"""
    from ...core.correction_scheduler import CorrectionScheduler

    try:
        scheduler = CorrectionScheduler()
        quota_info = await scheduler.get_quota_info(user_id)

        return QuotaInfo(**quota_info)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching quota info: {str(e)}"
        )


@router.post(
    "/correct/webhook/test",
    summary="Test webhook",
    description="Test webhook configuration"
)
async def test_webhook(webhook_url: str = Query(..., description="Webhook URL to test")):
    """Test webhook configuration"""
    import httpx

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                webhook_url,
                json={
                    "event": "test",
                    "timestamp": datetime.utcnow().isoformat(),
                    "message": "Webhook test successful"
                },
                timeout=10.0
            )

            return {
                "status": "success",
                "status_code": response.status_code,
                "response": response.text[:500]  # First 500 chars
            }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }


@router.get(
    "/correct/versions",
    summary="Get algorithm versions",
    description="Get available correction algorithm versions"
)
async def get_algorithm_versions():
    """Get available correction algorithm versions"""
    return {
        "versions": [
            {
                "version": "2.0.0",
                "name": "Production",
                "description": "Latest stable version with all features",
                "features": [
                    "Multi-level correction",
                    "Context-aware analysis",
                    "Advanced validation",
                    "Export formats"
                ],
                "default": True
            },
            {
                "version": "1.5.0",
                "name": "Legacy Compatible",
                "description": "Backward compatible with v1 API",
                "features": [
                    "Basic correction",
                    "Legacy patterns"
                ],
                "default": False
            }
        ],
        "latest": "2.0.0"
    }
