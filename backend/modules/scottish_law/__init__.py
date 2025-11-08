"""
Scottish Law Compliance Module

This module provides comprehensive compliance checking for Scots law differences
from English law across multiple legal domains.

Modules:
- scottish_employment: Employment law differences, tribunals, prescription periods
- scottish_contracts: Contract formation, consideration, third-party rights
- scottish_data_protection: FOI Scotland, Scottish Information Commissioner, public records
- scottish_property: Property terminology, tenancies, land registration
- scottish_corporate: Charities (OSCR), Companies House, partnerships

Key Scots Law Differences:
1. Consensus in idem (not offer and acceptance)
2. No consideration requirement
3. Jus quaesitum tertio (third-party rights)
4. 5-year prescription period (not 6-year limitation)
5. Different property law terminology (heritable, not freehold)
6. Scottish Information Commissioner for FOI
7. OSCR for charities (not Charity Commission)
8. Private Residential Tenancies (not ASTs)
"""

from .gates import (
    ScottishEmploymentGate,
    ScottishContractsGate,
    ScottishDataProtectionGate,
    ScottishPropertyGate,
    ScottishCorporateGate
)

__version__ = '1.0.0'

__all__ = [
    'ScottishEmploymentGate',
    'ScottishContractsGate',
    'ScottishDataProtectionGate',
    'ScottishPropertyGate',
    'ScottishCorporateGate'
]
