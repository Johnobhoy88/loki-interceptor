"""
LOKI Correction Explainability System
Provides transparent, auditable explanations for all document corrections
"""

from .explanation_engine import ExplanationEngine
from .legal_citations import LegalCitationManager
from .confidence_explainer import ConfidenceExplainer
from .impact_analyzer import ImpactAnalyzer
from .reasoning_chain import ReasoningChain
from .report_generator import ReportGenerator
from .feedback_manager import FeedbackManager

__all__ = [
    'ExplanationEngine',
    'LegalCitationManager',
    'ConfidenceExplainer',
    'ImpactAnalyzer',
    'ReasoningChain',
    'ReportGenerator',
    'FeedbackManager'
]

__version__ = '1.0.0'
