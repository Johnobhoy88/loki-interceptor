"""
Modules and Gates API models
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class GateInfo(BaseModel):
    """Compliance gate information"""
    id: str = Field(..., description="Gate identifier")
    name: str = Field(..., description="Human-readable gate name")
    version: str = Field(..., description="Gate version")
    module_id: str = Field(..., description="Parent module identifier")
    severity: str = Field(..., description="Default severity level")
    description: Optional[str] = Field(None, description="Gate description")
    legal_source: Optional[str] = Field(None, description="Legal source reference")
    active: bool = Field(True, description="Whether gate is active")
    deprecated: bool = Field(False, description="Whether gate is deprecated")
    deprecation_date: Optional[str] = Field(None, description="Deprecation date if deprecated")
    replacement_gate: Optional[str] = Field(None, description="Replacement gate ID if deprecated")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "gdpr_uk_consent",
                "name": "GDPR Consent Requirement",
                "version": "2.1.0",
                "module_id": "gdpr_uk",
                "severity": "ERROR",
                "description": "Validates explicit consent requirements under GDPR",
                "legal_source": "GDPR Article 7",
                "active": True,
                "deprecated": False,
                "deprecation_date": None,
                "replacement_gate": None,
                "metadata": {"article": "7", "regulation": "GDPR"}
            }
        }


class ModuleInfo(BaseModel):
    """Compliance module information"""
    id: str = Field(..., description="Module identifier")
    name: str = Field(..., description="Module display name")
    version: str = Field(..., description="Module version")
    description: Optional[str] = Field(None, description="Module description")
    gates_count: int = Field(..., description="Number of gates in module")
    active_gates: int = Field(..., description="Number of active gates")
    deprecated_gates: int = Field(0, description="Number of deprecated gates")
    categories: List[str] = Field(default_factory=list, description="Module categories")
    jurisdictions: List[str] = Field(default_factory=list, description="Applicable jurisdictions")
    industry: Optional[str] = Field(None, description="Industry focus if applicable")
    last_updated: Optional[str] = Field(None, description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "gdpr_uk",
                "name": "GDPR UK Compliance",
                "version": "3.2.1",
                "description": "UK-specific GDPR compliance validation",
                "gates_count": 45,
                "active_gates": 43,
                "deprecated_gates": 2,
                "categories": ["data_protection", "privacy"],
                "jurisdictions": ["UK", "EU"],
                "industry": None,
                "last_updated": "2025-10-15T10:00:00Z",
                "metadata": {}
            }
        }


class GatesResponse(BaseModel):
    """Gates list response"""
    gates: List[GateInfo] = Field(..., description="List of gates")
    total: int = Field(..., description="Total number of gates")
    module_id: Optional[str] = Field(None, description="Filter by module if specified")

    class Config:
        json_schema_extra = {
            "example": {
                "gates": [],
                "total": 234,
                "module_id": None
            }
        }


class ModulesResponse(BaseModel):
    """Modules list response"""
    modules: List[ModuleInfo] = Field(..., description="List of compliance modules")
    total: int = Field(..., description="Total number of modules")
    total_gates: int = Field(..., description="Total number of gates across all modules")

    class Config:
        json_schema_extra = {
            "example": {
                "modules": [],
                "total": 10,
                "total_gates": 234
            }
        }
