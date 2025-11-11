"""
Statistics and Analytics API models
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class RiskTrend(BaseModel):
    """Risk trend data point"""
    date: str = Field(..., description="Date (ISO format)")
    low_count: int = Field(0, description="Number of LOW risk validations")
    medium_count: int = Field(0, description="Number of MEDIUM risk validations")
    high_count: int = Field(0, description="Number of HIGH risk validations")
    critical_count: int = Field(0, description="Number of CRITICAL risk validations")
    total: int = Field(..., description="Total validations for this date")

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2025-11-11",
                "low_count": 120,
                "medium_count": 45,
                "high_count": 15,
                "critical_count": 3,
                "total": 183
            }
        }


class ModuleStats(BaseModel):
    """Module performance statistics"""
    module_id: str = Field(..., description="Module identifier")
    module_name: str = Field(..., description="Module display name")
    total_executions: int = Field(..., description="Total number of executions")
    total_failures: int = Field(..., description="Total gate failures")
    failure_rate: float = Field(..., description="Failure rate (0-1)", ge=0, le=1)
    average_execution_time_ms: float = Field(..., description="Average execution time")
    most_common_failures: List[Dict[str, Any]] = Field(
        ...,
        description="Most common gate failures in this module"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "module_id": "gdpr_uk",
                "module_name": "GDPR UK Compliance",
                "total_executions": 1250,
                "total_failures": 234,
                "failure_rate": 0.187,
                "average_execution_time_ms": 45.3,
                "most_common_failures": [
                    {"gate_id": "gdpr_uk_consent", "count": 89, "name": "Consent Requirement"}
                ]
            }
        }


class CacheStats(BaseModel):
    """Cache performance statistics"""
    total_entries: int = Field(..., description="Total cached entries")
    cache_hits: int = Field(..., description="Number of cache hits")
    cache_misses: int = Field(..., description="Number of cache misses")
    hit_rate: float = Field(..., description="Cache hit rate (0-1)", ge=0, le=1)
    memory_usage_mb: float = Field(..., description="Estimated memory usage in MB")
    oldest_entry_age_seconds: float = Field(..., description="Age of oldest entry in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "total_entries": 500,
                "cache_hits": 3450,
                "cache_misses": 1250,
                "hit_rate": 0.734,
                "memory_usage_mb": 12.5,
                "oldest_entry_age_seconds": 1800.0
            }
        }


class SystemStats(BaseModel):
    """System-wide statistics"""
    total_validations: int = Field(..., description="Total number of validations")
    total_corrections: int = Field(..., description="Total number of corrections")
    total_modules: int = Field(..., description="Number of loaded modules")
    total_gates: int = Field(..., description="Total number of gates")
    uptime_seconds: float = Field(..., description="System uptime in seconds")
    average_validation_time_ms: float = Field(..., description="Average validation time")
    peak_validations_per_hour: int = Field(..., description="Peak validations in an hour")
    risk_distribution: Dict[str, int] = Field(..., description="Distribution of risk levels")
    cache_stats: Optional[CacheStats] = Field(None, description="Cache statistics")
    recent_trends: List[RiskTrend] = Field(
        default_factory=list,
        description="Recent risk trends (last 7 days)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "total_validations": 15250,
                "total_corrections": 8340,
                "total_modules": 10,
                "total_gates": 234,
                "uptime_seconds": 86400.5,
                "average_validation_time_ms": 234.5,
                "peak_validations_per_hour": 450,
                "risk_distribution": {"LOW": 10000, "MEDIUM": 3000, "HIGH": 2000, "CRITICAL": 250},
                "cache_stats": None,
                "recent_trends": []
            }
        }


class AnalyticsOverview(BaseModel):
    """Analytics overview"""
    period_start: str = Field(..., description="Analysis period start (ISO format)")
    period_end: str = Field(..., description="Analysis period end (ISO format)")
    total_validations: int = Field(..., description="Total validations in period")
    risk_trends: List[RiskTrend] = Field(..., description="Risk trends over period")
    module_performance: List[ModuleStats] = Field(..., description="Module performance statistics")
    top_failing_gates: List[Dict[str, Any]] = Field(..., description="Top failing gates")
    document_type_distribution: Dict[str, int] = Field(
        ...,
        description="Distribution of document types"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "period_start": "2025-11-01T00:00:00Z",
                "period_end": "2025-11-11T23:59:59Z",
                "total_validations": 5420,
                "risk_trends": [],
                "module_performance": [],
                "top_failing_gates": [],
                "document_type_distribution": {"contract": 2000, "policy": 1500, "email": 1920}
            }
        }
