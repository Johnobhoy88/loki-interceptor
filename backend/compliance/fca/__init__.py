"""
FCA Financial Compliance Modules
Comprehensive suite for UK Financial Conduct Authority compliance
"""

from .consumer_duty import ConsumerDutyChecker
from .cryptoassets import CryptoPromotionValidator
from .esg_validator import ESGGreenwashingDetector
from .pension_validator import PensionTransferValidator
from .smcr import SMCRComplianceChecker
from .suitability import SuitabilityReportValidator
from .target_market import TargetMarketAssessor
from .risk_categorizer import RiskCategorizer

__all__ = [
    'ConsumerDutyChecker',
    'CryptoPromotionValidator',
    'ESGGreenwashingDetector',
    'PensionTransferValidator',
    'SMCRComplianceChecker',
    'SuitabilityReportValidator',
    'TargetMarketAssessor',
    'RiskCategorizer'
]
