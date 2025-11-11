"""
WebSocket API models
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from .validation import ValidationResult, RiskLevel


class WebSocketMessageType(str):
    """WebSocket message types"""
    VALIDATION_REQUEST = "validation_request"
    VALIDATION_RESPONSE = "validation_response"
    VALIDATION_PROGRESS = "validation_progress"
    ERROR = "error"
    PING = "ping"
    PONG = "pong"


class WebSocketMessage(BaseModel):
    """Base WebSocket message"""
    type: str = Field(..., description="Message type")
    request_id: Optional[str] = Field(None, description="Request identifier for tracking")
    timestamp: str = Field(..., description="ISO timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "ping",
                "request_id": "REQ_12345",
                "timestamp": "2025-11-11T10:30:00Z"
            }
        }


class WebSocketValidationRequest(WebSocketMessage):
    """WebSocket validation request"""
    text: str = Field(..., description="Document text to validate", min_length=1)
    document_type: str = Field("unknown", description="Document type")
    modules: Optional[List[str]] = Field(None, description="Specific modules to run")
    include_progress: bool = Field(
        True,
        description="Whether to send progress updates"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "validation_request",
                "request_id": "REQ_12345",
                "timestamp": "2025-11-11T10:30:00Z",
                "text": "This employment contract...",
                "document_type": "employment_contract",
                "modules": ["hr_scottish", "uk_employment"],
                "include_progress": True,
                "metadata": {}
            }
        }


class WebSocketValidationProgress(WebSocketMessage):
    """WebSocket validation progress update"""
    module_id: str = Field(..., description="Module currently being processed")
    modules_completed: int = Field(..., description="Number of modules completed")
    modules_total: int = Field(..., description="Total number of modules")
    progress_percent: float = Field(..., description="Progress percentage (0-100)", ge=0, le=100)
    current_status: str = Field(..., description="Current processing status")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "validation_progress",
                "request_id": "REQ_12345",
                "timestamp": "2025-11-11T10:30:01Z",
                "module_id": "gdpr_uk",
                "modules_completed": 3,
                "modules_total": 10,
                "progress_percent": 30.0,
                "current_status": "Processing GDPR UK module..."
            }
        }


class WebSocketValidationResponse(WebSocketMessage):
    """WebSocket validation response"""
    validation: ValidationResult = Field(..., description="Validation results")
    risk: RiskLevel = Field(..., description="Overall risk level")
    success: bool = Field(True, description="Whether validation completed successfully")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "validation_response",
                "request_id": "REQ_12345",
                "timestamp": "2025-11-11T10:30:05Z",
                "validation": {
                    "document_hash": "a1b2c3d4...",
                    "timestamp": "2025-11-11T10:30:05Z",
                    "overall_risk": "MEDIUM",
                    "modules": [],
                    "universal_analyzers": [],
                    "total_gates_checked": 45,
                    "total_gates_failed": 5,
                    "execution_time_ms": 234.5,
                    "cached": False
                },
                "risk": "MEDIUM",
                "success": True
            }
        }


class WebSocketError(WebSocketMessage):
    """WebSocket error message"""
    error: str = Field(..., description="Error type or code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "error",
                "request_id": "REQ_12345",
                "timestamp": "2025-11-11T10:30:00Z",
                "error": "VALIDATION_ERROR",
                "message": "Invalid request parameters",
                "details": {"field": "text", "issue": "Text cannot be empty"}
            }
        }
