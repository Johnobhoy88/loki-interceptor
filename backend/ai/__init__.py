"""
AI/ML Quality Enhancement Suite for LOKI Interceptor

This package provides comprehensive utilities for enhancing AI integration quality,
including prompt optimization, response validation, caching, cost tracking, and more.
"""

from .prompt_optimizer import PromptOptimizer, OptimizationStrategy
from .response_validator import ResponseValidator, ValidationRule, ValidationResult
from .semantic_cache import SemanticCache, CacheEntry
from .context_manager import ContextWindowManager, ContextStrategy
from .ab_testing import ABTestingFramework, TestVariant, TestResult
from .cost_tracker import CostTracker, CostMetrics
from .quality_metrics import QualityMetrics, MetricsCollector
from .fallback_handler import FallbackHandler, FallbackStrategy
from .explainability import ExplainabilityEngine, ExplainabilityReport
from .prompt_templates import PromptTemplateLibrary, PromptTemplate

__version__ = "1.0.0"

__all__ = [
    "PromptOptimizer",
    "OptimizationStrategy",
    "ResponseValidator",
    "ValidationRule",
    "ValidationResult",
    "SemanticCache",
    "CacheEntry",
    "ContextWindowManager",
    "ContextStrategy",
    "ABTestingFramework",
    "TestVariant",
    "TestResult",
    "CostTracker",
    "CostMetrics",
    "QualityMetrics",
    "MetricsCollector",
    "FallbackHandler",
    "FallbackStrategy",
    "ExplainabilityEngine",
    "ExplainabilityReport",
    "PromptTemplateLibrary",
    "PromptTemplate",
]
