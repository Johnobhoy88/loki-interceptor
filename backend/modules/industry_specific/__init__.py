"""
Industry-Specific Compliance Module

Provides specialized compliance checking for key UK industry sectors:
- Healthcare (NHS, CQC, Caldicott principles)
- Education (KCSIE, SEND, safeguarding)
- Finance (AML/KYC, PSD2, SMCR)
- Construction (CDM 2015, Building Regulations)
- Technology (Software licensing, open source, SaaS)
"""

from .gates import (
    HealthcareComplianceGate,
    EducationComplianceGate,
    FinanceComplianceGate,
    ConstructionComplianceGate,
    TechnologyComplianceGate,
)

__version__ = '1.0.0'

__all__ = [
    'HealthcareComplianceGate',
    'EducationComplianceGate',
    'FinanceComplianceGate',
    'ConstructionComplianceGate',
    'TechnologyComplianceGate',
]
