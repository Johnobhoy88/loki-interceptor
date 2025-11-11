"""
Document correction API models
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CorrectionIssue(BaseModel):
    """Issue identified for correction"""
    issue_id: str = Field(..., description="Unique issue identifier")
    gate_id: str = Field(..., description="Gate that detected the issue")
    severity: str = Field(..., description="Issue severity level")
    original_text: str = Field(..., description="Original problematic text")
    suggested_text: str = Field(..., description="Suggested corrected text")
    explanation: str = Field(..., description="Explanation of the correction")
    confidence: float = Field(..., description="Confidence score (0-1)", ge=0, le=1)
    applied: bool = Field(False, description="Whether correction was applied")

    class Config:
        json_schema_extra = {
            "example": {
                "issue_id": "ISSUE_001",
                "gate_id": "gdpr_uk_consent",
                "severity": "ERROR",
                "original_text": "We may use your data",
                "suggested_text": "With your explicit consent, we will use your data",
                "explanation": "GDPR requires explicit consent language",
                "confidence": 0.95,
                "applied": False
            }
        }


class CorrectionApplication(BaseModel):
    """Applied correction details"""
    issue_id: str = Field(..., description="Issue identifier")
    position: int = Field(..., description="Character position of correction")
    length: int = Field(..., description="Length of original text replaced")
    original: str = Field(..., description="Original text")
    corrected: str = Field(..., description="Corrected text")

    class Config:
        json_schema_extra = {
            "example": {
                "issue_id": "ISSUE_001",
                "position": 45,
                "length": 20,
                "original": "We may use your data",
                "corrected": "With your explicit consent, we will use your data"
            }
        }


class CorrectionRequest(BaseModel):
    """Document correction request"""
    text: str = Field(..., description="Original document text", min_length=1)
    validation_results: Dict[str, Any] = Field(
        ...,
        description="Validation results from /api/v1/validate endpoint"
    )
    auto_apply: bool = Field(
        False,
        description="Automatically apply all high-confidence corrections"
    )
    confidence_threshold: float = Field(
        0.8,
        description="Minimum confidence threshold for auto-apply",
        ge=0,
        le=1
    )
    issue_ids: Optional[List[str]] = Field(
        None,
        description="Specific issue IDs to correct (null = all issues)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "This employment contract is subject to Scottish law...",
                "validation_results": {
                    "overall_risk": "MEDIUM",
                    "modules": []
                },
                "auto_apply": False,
                "confidence_threshold": 0.8,
                "issue_ids": None
            }
        }


class CorrectionResponse(BaseModel):
    """Document correction response"""
    original_text: str = Field(..., description="Original document text")
    corrected_text: str = Field(..., description="Text with corrections applied")
    issues_found: int = Field(..., description="Total number of issues identified")
    issues_corrected: int = Field(..., description="Number of issues corrected")
    corrections: List[CorrectionApplication] = Field(
        ...,
        description="List of applied corrections"
    )
    suggestions: List[CorrectionIssue] = Field(
        ...,
        description="List of all correction suggestions"
    )
    improvement_score: float = Field(
        ...,
        description="Estimated improvement score (0-1)",
        ge=0,
        le=1
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional correction metadata"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "original_text": "This contract...",
                "corrected_text": "This contract [corrected]...",
                "issues_found": 10,
                "issues_corrected": 8,
                "corrections": [],
                "suggestions": [],
                "improvement_score": 0.75,
                "metadata": {"execution_time_ms": 123.4}
            }
        }
