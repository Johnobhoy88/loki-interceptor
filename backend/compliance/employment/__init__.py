"""
Employment Law Compliance Module
Comprehensive UK employment law validation
"""

from .era_2023 import EmploymentRightsAct2023Checker
from .flexible_working import FlexibleWorkingRightsValidator
from .worker_status import WorkerStatusDetermination
from .unfair_dismissal import UnfairDismissalProtection
from .equality import EqualityActCompliance
from .adjustments import ReasonableAdjustmentsValidator
from .whistleblowing import PIDAComplianceChecker
from .tupe import TUPETransferValidator
from .settlements import SettlementAgreementCompliance

__all__ = [
    'EmploymentRightsAct2023Checker',
    'FlexibleWorkingRightsValidator',
    'WorkerStatusDetermination',
    'UnfairDismissalProtection',
    'EqualityActCompliance',
    'ReasonableAdjustmentsValidator',
    'PIDAComplianceChecker',
    'TUPETransferValidator',
    'SettlementAgreementCompliance'
]
