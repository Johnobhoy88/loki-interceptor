"""
Scottish Law Compliance Gates

This module contains compliance gates specific to Scots law differences from English law.
Covers employment, contracts, data protection, property, and corporate law in Scotland.
"""

from .scottish_employment import ScottishEmploymentGate
from .scottish_contracts import ScottishContractsGate
from .scottish_data_protection import ScottishDataProtectionGate
from .scottish_property import ScottishPropertyGate
from .scottish_corporate import ScottishCorporateGate

__all__ = [
    'ScottishEmploymentGate',
    'ScottishContractsGate',
    'ScottishDataProtectionGate',
    'ScottishPropertyGate',
    'ScottishCorporateGate'
]
