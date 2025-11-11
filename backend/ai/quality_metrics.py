"""
AI Response Quality Metrics Module

Measures and tracks AI response quality across multiple dimensions:
- Response coherence
- Accuracy metrics
- Relevance scoring
- Completeness assessment
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class QualityDimension(str, Enum):
    """Dimensions of quality"""
    COHERENCE = "coherence"
    ACCURACY = "accuracy"
    RELEVANCE = "relevance"
    COMPLETENESS = "completeness"
    SAFETY = "safety"
    CLARITY = "clarity"


@dataclass
class QualityScore:
    """Quality score for response"""
    dimension: QualityDimension
    score: float  # 0-1
    confidence: float  # 0-1, confidence in score
    reasons: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class QualityMetrics:
    """Overall quality metrics"""
    response_id: str
    overall_score: float  # 0-1
    dimension_scores: Dict[str, float]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    individual_scores: List[QualityScore] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


class MetricsCollector:
    """
    Collects and analyzes AI response quality metrics

    Features:
    - Multi-dimensional quality assessment
    - Trend analysis
    - Quality reporting
    - Threshold alerting
    """

    def __init__(self):
        self.metrics_history: List[QualityMetrics] = []
        self.thresholds: Dict[QualityDimension, float] = {
            QualityDimension.COHERENCE: 0.7,
            QualityDimension.ACCURACY: 0.75,
            QualityDimension.RELEVANCE: 0.8,
            QualityDimension.COMPLETENESS: 0.7,
            QualityDimension.SAFETY: 0.95,
            QualityDimension.CLARITY: 0.75
        }

    def assess_quality(
        self,
        response: str,
        prompt: str,
        expected_output: Optional[str] = None
    ) -> QualityMetrics:
        """
        Assess overall quality of a response

        Args:
            response: The AI response
            prompt: The original prompt
            expected_output: Expected output for accuracy check

        Returns:
            QualityMetrics with detailed assessment
        """
        scores = []

        # Assess coherence
        coherence_score = self._assess_coherence(response)
        scores.append(QualityScore(
            dimension=QualityDimension.COHERENCE,
            score=coherence_score,
            confidence=0.85
        ))

        # Assess accuracy
        accuracy_score = self._assess_accuracy(response, expected_output)
        scores.append(QualityScore(
            dimension=QualityDimension.ACCURACY,
            score=accuracy_score,
            confidence=0.8 if expected_output else 0.5
        ))

        # Assess relevance
        relevance_score = self._assess_relevance(response, prompt)
        scores.append(QualityScore(
            dimension=QualityDimension.RELEVANCE,
            score=relevance_score,
            confidence=0.85
        ))

        # Assess completeness
        completeness_score = self._assess_completeness(response, prompt)
        scores.append(QualityScore(
            dimension=QualityDimension.COMPLETENESS,
            score=completeness_score,
            confidence=0.8
        ))

        # Assess safety
        safety_score = self._assess_safety(response)
        scores.append(QualityScore(
            dimension=QualityDimension.SAFETY,
            score=safety_score,
            confidence=0.9
        ))

        # Assess clarity
        clarity_score = self._assess_clarity(response)
        scores.append(QualityScore(
            dimension=QualityDimension.CLARITY,
            score=clarity_score,
            confidence=0.85
        ))

        # Calculate overall score (weighted average)
        dimension_scores = {score.dimension.value: score.score for score in scores}
        weights = {
            "coherence": 0.15,
            "accuracy": 0.25,
            "relevance": 0.25,
            "completeness": 0.15,
            "safety": 0.15,
            "clarity": 0.05
        }

        overall = sum(
            score.score * weights.get(score.dimension.value, 0)
            for score in scores
        )

        metrics = QualityMetrics(
            response_id=self._generate_id(),
            overall_score=overall,
            dimension_scores=dimension_scores,
            individual_scores=scores
        )

        self.metrics_history.append(metrics)
        return metrics

    def _assess_coherence(self, response: str) -> float:
        """Assess response coherence (0-1)"""
        if not response:
            return 0.0

        # Check for proper sentence structure
        sentences = response.split('.')
        if len(sentences) < 2:
            return 0.6

        # Check for logical flow (simple heuristic)
        # Count transition words
        transition_words = [
            'therefore', 'however', 'moreover', 'furthermore',
            'consequently', 'additionally', 'first', 'second',
            'finally', 'in addition', 'for example'
        ]

        response_lower = response.lower()
        transition_count = sum(1 for word in transition_words if word in response_lower)

        # Score based on transitions and length
        coherence = min(0.95, 0.5 + (transition_count * 0.1) + (len(sentences) * 0.05))
        return max(0.5, coherence)

    def _assess_accuracy(self, response: str, expected: Optional[str]) -> float:
        """Assess accuracy against expected output"""
        if not expected:
            # Can't assess without reference - return neutral
            return 0.5

        # Simple string similarity
        response_words = set(response.lower().split())
        expected_words = set(expected.lower().split())

        if not expected_words:
            return 0.5

        overlap = len(response_words & expected_words)
        accuracy = overlap / len(expected_words)

        return min(1.0, accuracy * 0.9 + 0.1)  # Cap at 0.9, add baseline

    def _assess_relevance(self, response: str, prompt: str) -> float:
        """Assess response relevance to prompt"""
        if not prompt or not response:
            return 0.5

        # Extract key concepts from prompt
        prompt_words = set(w.lower() for w in prompt.split() if len(w) > 4)
        response_words = set(w.lower() for w in response.split() if len(w) > 4)

        if not prompt_words:
            return 0.5

        # Measure word overlap
        overlap = len(prompt_words & response_words)
        relevance = overlap / len(prompt_words)

        return min(1.0, relevance * 0.8 + 0.2)

    def _assess_completeness(self, response: str, prompt: str) -> float:
        """Assess response completeness"""
        if not response:
            return 0.0

        # Heuristics for completeness
        has_intro = any(word in response.lower() for word in ['first', 'initially', 'start', 'begin'])
        has_details = len(response) > 100
        has_conclusion = any(word in response.lower() for word in ['conclusion', 'summary', 'finally'])

        completeness = 0.5  # baseline
        if has_intro:
            completeness += 0.2
        if has_details:
            completeness += 0.2
        if has_conclusion:
            completeness += 0.1

        return min(1.0, completeness)

    def _assess_safety(self, response: str) -> float:
        """Assess response safety"""
        # Check for harmful patterns
        harmful_patterns = ['kill', 'harm', 'hack', 'malware', 'illegal']

        response_lower = response.lower()
        harmful_count = sum(1 for pattern in harmful_patterns if pattern in response_lower)

        if harmful_count > 0:
            return max(0.1, 1.0 - (harmful_count * 0.2))

        return 0.95

    def _assess_clarity(self, response: str) -> float:
        """Assess response clarity"""
        if not response:
            return 0.0

        # Clarity heuristics
        avg_word_length = sum(len(w) for w in response.split()) / max(1, len(response.split()))

        # Ideal average word length is 4-5 characters
        word_score = 1.0 - abs(avg_word_length - 4.5) / 10

        # Check for clear structure
        has_bullets = response.count('•') + response.count('-') + response.count('*') > 0
        structure_score = 0.7 if has_bullets else 0.5

        clarity = word_score * 0.6 + structure_score * 0.4
        return max(0.3, min(1.0, clarity))

    def _generate_id(self) -> str:
        """Generate unique ID"""
        import hashlib
        import time
        return hashlib.md5(str(time.time()).encode()).hexdigest()[:8]

    def get_dimension_trend(
        self,
        dimension: QualityDimension,
        limit: int = 100
    ) -> List[float]:
        """Get trend of scores for dimension"""
        scores = []

        for metrics in self.metrics_history[-limit:]:
            if dimension.value in metrics.dimension_scores:
                scores.append(metrics.dimension_scores[dimension.value])

        return scores

    def get_summary(self) -> Dict:
        """Get quality metrics summary"""
        if not self.metrics_history:
            return {}

        all_scores = [m.overall_score for m in self.metrics_history]
        avg_overall = sum(all_scores) / len(all_scores)

        dimension_averages = {}
        for dimension in QualityDimension:
            dim_scores = [
                m.dimension_scores.get(dimension.value, 0)
                for m in self.metrics_history
            ]
            if dim_scores:
                dimension_averages[dimension.value] = sum(dim_scores) / len(dim_scores)

        # Count threshold violations
        violations = []
        for metrics in self.metrics_history:
            for dimension, score in metrics.dimension_scores.items():
                if score < self.thresholds.get(QualityDimension(dimension), 0.5):
                    violations.append((dimension, score))

        return {
            "assessments_total": len(self.metrics_history),
            "average_overall_score": avg_overall,
            "dimension_averages": dimension_averages,
            "threshold_violations": len(violations),
            "best_score": max(all_scores),
            "worst_score": min(all_scores)
        }

    def get_alerts(self) -> List[Dict]:
        """Get quality alerts for responses below thresholds"""
        alerts = []

        for metrics in self.metrics_history[-50:]:  # Check recent assessments
            for dimension, score in metrics.dimension_scores.items():
                threshold = self.thresholds.get(QualityDimension(dimension), 0.5)
                if score < threshold:
                    alerts.append({
                        "response_id": metrics.response_id,
                        "dimension": dimension,
                        "score": score,
                        "threshold": threshold,
                        "severity": "high" if score < threshold * 0.8 else "medium"
                    })

        return alerts
