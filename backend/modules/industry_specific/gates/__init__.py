"""
Industry-Specific Compliance Gates

This package contains specialized compliance gates for key UK industry sectors.
Each gate validates documents against sector-specific regulations and best practices.
"""

from .healthcare_compliance import HealthcareComplianceGate
from .education_compliance import EducationComplianceGate
from .finance_compliance import FinanceComplianceGate
from .construction_compliance import ConstructionComplianceGate
from .technology_compliance import TechnologyComplianceGate

__all__ = [
    'HealthcareComplianceGate',
    'EducationComplianceGate',
    'FinanceComplianceGate',
    'ConstructionComplianceGate',
    'TechnologyComplianceGate',
]
