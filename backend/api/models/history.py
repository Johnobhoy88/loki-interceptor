"""
Validation history API models
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from .validation import RiskLevel


class HistoryFilter(BaseModel):
    """History filtering criteria"""
    risk_level: Optional[RiskLevel] = Field(None, description="Filter by risk level")
    document_type: Optional[str] = Field(None, description="Filter by document type")
    module_id: Optional[str] = Field(None, description="Filter by module")
    date_from: Optional[str] = Field(None, description="Start date (ISO format)")
    date_to: Optional[str] = Field(None, description="End date (ISO format)")
    client_id: Optional[str] = Field(None, description="Filter by client ID")

    class Config:
        json_schema_extra = {
            "example": {
                "risk_level": "HIGH",
                "document_type": "contract",
                "module_id": "gdpr_uk",
                "date_from": "2025-11-01T00:00:00Z",
                "date_to": "2025-11-11T23:59:59Z",
                "client_id": "CLIENT123"
            }
        }


class HistoryEntry(BaseModel):
    """Validation history entry"""
    id: str = Field(..., description="Unique entry identifier")
    timestamp: str = Field(..., description="ISO timestamp of validation")
    document_hash: str = Field(..., description="SHA-256 hash of validated document")
    document_type: str = Field(..., description="Type of document")
    overall_risk: RiskLevel = Field(..., description="Overall risk assessment")
    modules_checked: List[str] = Field(..., description="Modules that were run")
    gates_failed: int = Field(..., description="Number of gates failed")
    execution_time_ms: float = Field(..., description="Validation execution time")
    client_id: Optional[str] = Field(None, description="Client identifier")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "HIST_12345",
                "timestamp": "2025-11-11T10:30:00Z",
                "document_hash": "a1b2c3d4...",
                "document_type": "employment_contract",
                "overall_risk": "MEDIUM",
                "modules_checked": ["hr_scottish", "uk_employment"],
                "gates_failed": 3,
                "execution_time_ms": 234.5,
                "client_id": "CLIENT123",
                "metadata": {}
            }
        }


class HistoryStats(BaseModel):
    """History statistics"""
    total_validations: int = Field(..., description="Total number of validations")
    risk_distribution: Dict[str, int] = Field(..., description="Distribution of risk levels")
    document_type_distribution: Dict[str, int] = Field(
        ...,
        description="Distribution of document types"
    )
    average_execution_time_ms: float = Field(..., description="Average execution time")
    peak_usage_hour: Optional[int] = Field(None, description="Peak usage hour (0-23)")
    most_common_failures: List[Dict[str, Any]] = Field(
        ...,
        description="Most common gate failures"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "total_validations": 1250,
                "risk_distribution": {"LOW": 800, "MEDIUM": 300, "HIGH": 120, "CRITICAL": 30},
                "document_type_distribution": {"contract": 500, "policy": 300, "email": 450},
                "average_execution_time_ms": 234.5,
                "peak_usage_hour": 14,
                "most_common_failures": [
                    {"gate_id": "gdpr_uk_consent", "count": 45}
                ]
            }
        }


class HistoryResponse(BaseModel):
    """Paginated history response"""
    entries: List[HistoryEntry] = Field(..., description="History entries")
    total: int = Field(..., description="Total number of entries")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of entries per page")
    total_pages: int = Field(..., description="Total number of pages")
    stats: Optional[HistoryStats] = Field(None, description="Aggregated statistics")

    class Config:
        json_schema_extra = {
            "example": {
                "entries": [],
                "total": 1250,
                "page": 1,
                "page_size": 50,
                "total_pages": 25,
                "stats": None
            }
        }
