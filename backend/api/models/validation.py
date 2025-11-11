"""
Validation API models
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class RiskLevel(str, Enum):
    """Risk level enumeration"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SeverityLevel(str, Enum):
    """Issue severity level"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class GateResult(BaseModel):
    """Individual gate validation result"""
    gate_id: str = Field(..., description="Gate identifier")
    gate_name: str = Field(..., description="Human-readable gate name")
    passed: bool = Field(..., description="Whether the gate check passed")
    severity: SeverityLevel = Field(..., description="Issue severity if failed")
    message: str = Field(..., description="Validation message")
    legal_source: Optional[str] = Field(None, description="Legal source reference")
    snippets: List[str] = Field(default_factory=list, description="Text snippets that triggered the gate")
    suggestions: List[str] = Field(default_factory=list, description="Suggested corrections")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional gate metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "gate_id": "gdpr_uk_consent",
                "gate_name": "GDPR Consent Requirement",
                "passed": False,
                "severity": "ERROR",
                "message": "Missing explicit consent language",
                "legal_source": "GDPR Article 7",
                "snippets": ["We may use your data"],
                "suggestions": ["Add explicit opt-in consent mechanism"],
                "metadata": {"article": "7", "regulation": "GDPR"}
            }
        }


class ModuleResult(BaseModel):
    """Compliance module validation result"""
    module_id: str = Field(..., description="Module identifier")
    module_name: str = Field(..., description="Module display name")
    gates_checked: int = Field(..., description="Number of gates checked")
    gates_passed: int = Field(..., description="Number of gates passed")
    gates_failed: int = Field(..., description="Number of gates failed")
    risk_level: RiskLevel = Field(..., description="Overall module risk level")
    gates: List[GateResult] = Field(..., description="Individual gate results")
    execution_time_ms: float = Field(..., description="Module execution time in milliseconds")

    class Config:
        json_schema_extra = {
            "example": {
                "module_id": "gdpr_uk",
                "module_name": "GDPR UK Compliance",
                "gates_checked": 10,
                "gates_passed": 8,
                "gates_failed": 2,
                "risk_level": "HIGH",
                "gates": [],
                "execution_time_ms": 45.3
            }
        }


class UniversalAnalyzerResult(BaseModel):
    """Universal analyzer result"""
    name: str = Field(..., description="Analyzer name")
    detected: bool = Field(..., description="Whether issues were detected")
    count: int = Field(0, description="Number of issues found")
    details: Dict[str, Any] = Field(default_factory=dict, description="Detailed results")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "PII Scanner",
                "detected": True,
                "count": 3,
                "details": {"types": ["email", "phone"], "locations": [12, 45, 89]}
            }
        }


class ValidationResult(BaseModel):
    """Complete validation result"""
    document_hash: str = Field(..., description="SHA-256 hash of the document")
    timestamp: str = Field(..., description="ISO timestamp of validation")
    overall_risk: RiskLevel = Field(..., description="Overall risk assessment")
    modules: List[ModuleResult] = Field(..., description="Results from compliance modules")
    universal_analyzers: List[UniversalAnalyzerResult] = Field(
        default_factory=list,
        description="Results from universal analyzers"
    )
    total_gates_checked: int = Field(..., description="Total number of gates checked")
    total_gates_failed: int = Field(..., description="Total number of gates failed")
    execution_time_ms: float = Field(..., description="Total validation time in milliseconds")
    cached: bool = Field(False, description="Whether result was served from cache")

    class Config:
        json_schema_extra = {
            "example": {
                "document_hash": "a1b2c3d4...",
                "timestamp": "2025-11-11T10:30:00Z",
                "overall_risk": "MEDIUM",
                "modules": [],
                "universal_analyzers": [],
                "total_gates_checked": 45,
                "total_gates_failed": 5,
                "execution_time_ms": 234.5,
                "cached": False
            }
        }


class ValidationRequest(BaseModel):
    """Document validation request"""
    text: str = Field(..., description="Document text to validate", min_length=1)
    document_type: str = Field(
        "unknown",
        description="Type of document (e.g., 'contract', 'policy', 'email')"
    )
    modules: Optional[List[str]] = Field(
        None,
        description="Specific modules to run (null = all loaded modules)"
    )
    use_cache: bool = Field(True, description="Whether to use cached results if available")
    include_suggestions: bool = Field(
        True,
        description="Whether to include correction suggestions"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for the validation"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "This employment contract is subject to Scottish law...",
                "document_type": "employment_contract",
                "modules": ["hr_scottish", "uk_employment"],
                "use_cache": True,
                "include_suggestions": True,
                "metadata": {"client_id": "CLIENT123", "industry": "technology"}
            }
        }


class ValidationResponse(BaseModel):
    """Document validation response"""
    validation: ValidationResult = Field(..., description="Validation results")
    risk: RiskLevel = Field(..., description="Overall risk level (convenience field)")
    suggestions_available: bool = Field(..., description="Whether correction suggestions are available")

    class Config:
        json_schema_extra = {
            "example": {
                "validation": {
                    "document_hash": "a1b2c3d4...",
                    "timestamp": "2025-11-11T10:30:00Z",
                    "overall_risk": "MEDIUM",
                    "modules": [],
                    "universal_analyzers": [],
                    "total_gates_checked": 45,
                    "total_gates_failed": 5,
                    "execution_time_ms": 234.5,
                    "cached": False
                },
                "risk": "MEDIUM",
                "suggestions_available": True
            }
        }
