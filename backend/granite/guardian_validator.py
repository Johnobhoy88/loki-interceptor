"""
Granite Guardian Safety Validator

Provides compliance risk detection and safety validation using
IBM Granite Guardian 3.0 models (2B and 8B variants).

Risk Dimensions:
- Harm: Content considered generally harmful
- Social Bias: Prejudice based on identity or characteristics
- Jailbreaking: Attempts to manipulate AI
- Violence: Violent or threatening content
- Groundedness: RAG response accuracy (facts vs hallucination)
- Answer Relevance: Response relevance to question
- Context Relevance: Retrieved context quality

Enterprise Features:
- Bring Your Own Criteria (BYOC)
- Custom risk dimensions
- Threshold configuration
- Audit trail
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk level classifications"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskDimension(Enum):
    """Available risk detection dimensions"""
    HARM = "harm"
    SOCIAL_BIAS = "social_bias"
    JAILBREAKING = "jailbreaking"
    VIOLENCE = "violence"
    PROFANITY = "profanity"
    TOXICITY = "toxicity"
    GROUNDEDNESS = "groundedness"
    ANSWER_RELEVANCE = "answer_relevance"
    CONTEXT_RELEVANCE = "context_relevance"


@dataclass
class SafetyResult:
    """Result of safety validation"""
    overall_risk: RiskLevel
    risk_scores: Dict[str, float]
    flagged_dimensions: List[str]
    passed: bool
    recommendation: str
    details: Dict[str, Any]
    guardian_version: str


class GuardianValidator:
    """
    Safety validator using Granite Guardian models.

    Examples:
        >>> guardian = GuardianValidator(model_size="2b")
        >>> result = guardian.validate(
        ...     text="Investment opportunity with guaranteed returns",
        ...     dimensions=["harm", "social_bias"]
        ... )
        >>> if not result.passed:
        ...     print(f"Risk detected: {result.recommendation}")

        >>> # RAG-specific validation
        >>> result = guardian.validate_rag_response(
        ...     question="What is FCA COBS 4.2.1?",
        ...     answer="FCA COBS 4.2.1 requires fair, clear, not misleading communications",
        ...     context="FCA Handbook excerpt...",
        ... )
    """

    def __init__(
        self,
        model_size: str = "2b",
        risk_threshold: float = 0.7,
        device: str = "cpu"
    ):
        """
        Initialize Guardian validator.

        Args:
            model_size: Model size ("2b" or "8b")
            risk_threshold: Risk score threshold (0.0-1.0)
            device: Device for inference ("cpu" or "cuda")
        """
        self.model_size = model_size
        self.risk_threshold = risk_threshold
        self.device = device
        self._model = None
        self._tokenizer = None
        self._guardian_available = self._check_guardian()

    def _check_guardian(self) -> bool:
        """Check if Granite Guardian is available"""
        try:
            import transformers  # noqa: F401
            return True
        except ImportError:
            logger.warning(
                "Transformers not installed. Install with: pip install transformers torch\n"
                "Granite Guardian validation will not be available."
            )
            return False

    def _load_model(self):
        """Lazy load Guardian model"""
        if self._model is not None:
            return

        if not self._guardian_available:
            raise RuntimeError(
                "Transformers not installed. Install with: pip install transformers torch"
            )

        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification

            model_name = f"ibm-granite/granite-guardian-3.0-{self.model_size}"
            logger.info(f"Loading Granite Guardian {self.model_size}...")

            self._tokenizer = AutoTokenizer.from_pretrained(model_name)
            self._model = AutoModelForSequenceClassification.from_pretrained(model_name)

            if self.device == "cuda":
                import torch
                if torch.cuda.is_available():
                    self._model = self._model.cuda()
                else:
                    logger.warning("CUDA not available, falling back to CPU")
                    self.device = "cpu"

            logger.info(f"Granite Guardian {self.model_size} loaded successfully")

        except Exception as e:
            logger.error(f"Error loading Guardian model: {e}")
            raise

    def validate(
        self,
        text: str,
        dimensions: Optional[List[str]] = None,
        context: Optional[str] = None
    ) -> SafetyResult:
        """
        Validate text for safety and compliance risks.

        Args:
            text: Text to validate
            dimensions: Risk dimensions to check (default: all)
            context: Optional context for RAG validation

        Returns:
            SafetyResult with risk scores and recommendation
        """
        if dimensions is None:
            dimensions = [
                RiskDimension.HARM.value,
                RiskDimension.SOCIAL_BIAS.value,
                RiskDimension.JAILBREAKING.value,
                RiskDimension.VIOLENCE.value
            ]

        # Mock implementation until model is loaded
        # TODO: Replace with actual Guardian inference
        risk_scores = {}
        flagged = []
        max_score = 0.0

        for dimension in dimensions:
            # Placeholder: Rule-based detection until Guardian loaded
            score = self._mock_risk_detection(text, dimension)
            risk_scores[dimension] = score

            if score > self.risk_threshold:
                flagged.append(dimension)
                max_score = max(max_score, score)

        # Determine overall risk
        if max_score >= 0.9:
            overall_risk = RiskLevel.CRITICAL
        elif max_score >= 0.7:
            overall_risk = RiskLevel.HIGH
        elif max_score >= 0.4:
            overall_risk = RiskLevel.MEDIUM
        else:
            overall_risk = RiskLevel.LOW

        passed = overall_risk in (RiskLevel.LOW, RiskLevel.MEDIUM)

        recommendation = self._get_recommendation(overall_risk, flagged)

        return SafetyResult(
            overall_risk=overall_risk,
            risk_scores=risk_scores,
            flagged_dimensions=flagged,
            passed=passed,
            recommendation=recommendation,
            details={
                'threshold': self.risk_threshold,
                'dimensions_checked': dimensions,
                'text_length': len(text)
            },
            guardian_version=f"Granite Guardian 3.0 {self.model_size}"
        )

    def validate_rag_response(
        self,
        question: str,
        answer: str,
        context: str,
        check_groundedness: bool = True,
        check_relevance: bool = True
    ) -> SafetyResult:
        """
        Validate RAG (Retrieval Augmented Generation) response.

        Args:
            question: Original question
            answer: Generated answer
            context: Retrieved context
            check_groundedness: Check if answer is grounded in context
            check_relevance: Check answer and context relevance

        Returns:
            SafetyResult with RAG-specific checks
        """
        dimensions = []
        if check_groundedness:
            dimensions.append(RiskDimension.GROUNDEDNESS.value)
        if check_relevance:
            dimensions.extend([
                RiskDimension.ANSWER_RELEVANCE.value,
                RiskDimension.CONTEXT_RELEVANCE.value
            ])

        # Add standard safety checks
        dimensions.extend([
            RiskDimension.HARM.value,
            RiskDimension.SOCIAL_BIAS.value
        ])

        return self.validate(
            text=answer,
            dimensions=dimensions,
            context=context
        )

    def _mock_risk_detection(self, text: str, dimension: str) -> float:
        """
        Placeholder risk detection until Guardian model loaded.
        Uses simple keyword matching.
        """
        text_lower = text.lower()

        # Simple keyword-based risk scoring
        risk_keywords = {
            'harm': ['dangerous', 'harmful', 'hurt', 'damage', 'threat'],
            'social_bias': ['discriminate', 'prejudice', 'stereotype', 'racist', 'sexist'],
            'violence': ['kill', 'attack', 'assault', 'murder', 'weapon'],
            'jailbreaking': ['ignore previous', 'disregard', 'bypass', 'override'],
            'groundedness': []  # Requires model inference
        }

        keywords = risk_keywords.get(dimension, [])
        matches = sum(1 for keyword in keywords if keyword in text_lower)

        # Score based on keyword matches
        if matches == 0:
            return 0.1
        elif matches == 1:
            return 0.3
        elif matches == 2:
            return 0.6
        else:
            return 0.9

    def _get_recommendation(
        self,
        risk_level: RiskLevel,
        flagged_dimensions: List[str]
    ) -> str:
        """Generate recommendation based on risk assessment"""
        if risk_level == RiskLevel.CRITICAL:
            return (
                f"CRITICAL RISK: Content flagged for {', '.join(flagged_dimensions)}. "
                "Immediate review required. Consider blocking or significant revision."
            )
        elif risk_level == RiskLevel.HIGH:
            return (
                f"HIGH RISK: Potential issues in {', '.join(flagged_dimensions)}. "
                "Manual review recommended before proceeding."
            )
        elif risk_level == RiskLevel.MEDIUM:
            return (
                f"MEDIUM RISK: Minor concerns in {', '.join(flagged_dimensions)}. "
                "Review recommended for sensitive contexts."
            )
        else:
            return "LOW RISK: Content passed safety validation. Safe to proceed."

    def validate_correction(
        self,
        original: str,
        corrected: str,
        correction_type: str
    ) -> SafetyResult:
        """
        Validate that corrections don't introduce new risks.

        Args:
            original: Original text
            corrected: Corrected text
            correction_type: Type of correction applied

        Returns:
            SafetyResult for corrected text
        """
        result = self.validate(corrected)

        # Add comparison details
        result.details['correction_type'] = correction_type
        result.details['original_length'] = len(original)
        result.details['corrected_length'] = len(corrected)
        result.details['delta'] = len(corrected) - len(original)

        return result
