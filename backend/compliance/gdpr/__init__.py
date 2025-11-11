"""
GDPR UK Compliance Validators
Comprehensive data protection validation modules
"""

from .consent_validator import ConsentValidator
from .subject_rights import SubjectRightsValidator
from .retention import RetentionPolicyChecker
from .international_transfer import InternationalTransferValidator
from .dpia_checker import DPIAChecker
from .cookie_consent import CookieConsentValidator
from .breach_checker import BreachNotificationChecker
from .children import ChildrenDataProtection
from .legitimate_interest import LegitimateInterestAssessor
from .privacy_notice import PrivacyNoticeChecker
from .data_minimization import DataMinimizationValidator

__all__ = [
    'ConsentValidator',
    'SubjectRightsValidator',
    'RetentionPolicyChecker',
    'InternationalTransferValidator',
    'DPIAChecker',
    'CookieConsentValidator',
    'BreachNotificationChecker',
    'ChildrenDataProtection',
    'LegitimateInterestAssessor',
    'PrivacyNoticeChecker',
    'DataMinimizationValidator'
]
