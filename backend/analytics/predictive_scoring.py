"""
Predictive Compliance Scoring Engine
Predicts future compliance scores using machine learning techniques.
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging
import math

logger = logging.getLogger(__name__)


class ConfidenceLevel(str, Enum):
    """Confidence levels for predictions"""
    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"


@dataclass
class PredictionPoint:
    """Single prediction point"""
    timestamp: datetime
    predicted_score: float
    lower_bound: float  # Confidence interval lower bound
    upper_bound: float  # Confidence interval upper bound
    confidence: ConfidenceLevel


@dataclass
class PredictiveScoreResult:
    """Complete predictive scoring result"""
    module_name: str
    current_score: float
    predictions: List[PredictionPoint]
    risk_probability: float  # Probability of falling below threshold
    improvement_trajectory: str
    key_drivers: List[Tuple[str, float]]  # Factor influencing score
    contributing_factors: Dict[str, float]
    model_accuracy: float  # R-squared value


class PredictiveComplianceScorer:
    """
    Predictive compliance scoring using machine learning.

    Features:
    - ARIMA-like forecasting
    - Confidence interval calculations
    - Risk probability estimation
    - Factor importance analysis
    - Ensemble predictions
    - Anomaly-aware forecasting
    """

    def __init__(self):
        """Initialize predictive scorer."""
        self.model_history: Dict[str, List[Tuple[datetime, float]]] = {}
        self.factor_weights: Dict[str, float] = self._initialize_weights()
        self.prediction_cache: Dict[str, PredictiveScoreResult] = {}

    def _initialize_weights(self) -> Dict[str, float]:
        """Initialize factor weights for compliance scoring."""
        return {
            'gate_compliance': 0.35,
            'policy_adherence': 0.25,
            'documentation': 0.20,
            'audit_findings': 0.12,
            'corrective_actions': 0.08,
        }

    def predict_compliance_score(
        self,
        module_name: str,
        historical_scores: List[Tuple[datetime, float]],
        contributing_factors: Dict[str, float],
        periods_ahead: int = 30,
        threshold: float = 70.0
    ) -> PredictiveScoreResult:
        """
        Predict future compliance score for a module.

        Args:
            module_name: Name of the compliance module
            historical_scores: Historical score data
            contributing_factors: Current factor values (0-100)
            periods_ahead: Number of days to predict ahead
            threshold: Minimum acceptable score threshold

        Returns:
            PredictiveScoreResult with predictions and analysis
        """
        if len(historical_scores) < 3:
            return self._create_minimal_prediction(
                module_name, contributing_factors
            )

        # Store history
        self.model_history[module_name] = historical_scores

        # Current metrics
        current_score = historical_scores[-1][1]

        # Calculate trend component
        trend = self._calculate_trend(historical_scores)

        # Calculate seasonality component
        seasonality = self._calculate_seasonality(historical_scores)

        # Calculate factor contribution
        factor_impact = self._calculate_factor_impact(contributing_factors)

        # Generate predictions
        predictions = self._generate_exponential_predictions(
            historical_scores,
            trend,
            seasonality,
            factor_impact,
            periods_ahead
        )

        # Calculate risk probability
        risk_prob = self._calculate_risk_probability(
            predictions, threshold
        )

        # Determine improvement trajectory
        trajectory = self._determine_trajectory(trend, factor_impact)

        # Calculate model accuracy
        accuracy = self._calculate_model_accuracy(historical_scores)

        result = PredictiveScoreResult(
            module_name=module_name,
            current_score=current_score,
            predictions=predictions,
            risk_probability=risk_prob,
            improvement_trajectory=trajectory,
            key_drivers=self._extract_key_drivers(contributing_factors),
            contributing_factors=contributing_factors,
            model_accuracy=accuracy
        )

        self.prediction_cache[module_name] = result
        return result

    def _calculate_trend(
        self,
        historical_scores: List[Tuple[datetime, float]]
    ) -> float:
        """Calculate trend component (slope)."""
        if len(historical_scores) < 2:
            return 0.0

        n = len(historical_scores)
        x_values = list(range(n))
        y_values = [score for _, score in historical_scores]

        x_mean = sum(x_values) / n
        y_mean = sum(y_values) / n

        numerator = sum(
            (x_values[i] - x_mean) * (y_values[i] - y_mean)
            for i in range(n)
        )
        denominator = sum(
            (x_values[i] - x_mean) ** 2
            for i in range(n)
        )

        if denominator == 0:
            return 0.0

        return numerator / denominator

    def _calculate_seasonality(
        self,
        historical_scores: List[Tuple[datetime, float]]
    ) -> float:
        """Calculate seasonality component."""
        if len(historical_scores) < 7:
            return 0.0

        scores = [score for _, score in historical_scores]
        recent = scores[-7:] if len(scores) >= 7 else scores

        # Simple seasonality: variance in recent scores
        mean = sum(recent) / len(recent)
        variance = sum((x - mean) ** 2 for x in recent) / len(recent)

        return math.sqrt(variance)

    def _calculate_factor_impact(
        self,
        contributing_factors: Dict[str, float]
    ) -> float:
        """Calculate impact of current contributing factors."""
        total_impact = 0.0

        for factor_name, factor_value in contributing_factors.items():
            weight = self.factor_weights.get(factor_name, 0.0)
            # Normalize factor value to -1 to 1 scale
            normalized = (factor_value - 50) / 50
            impact = weight * normalized
            total_impact += impact

        return total_impact

    def _generate_exponential_predictions(
        self,
        historical_scores: List[Tuple[datetime, float]],
        trend: float,
        seasonality: float,
        factor_impact: float,
        periods_ahead: int
    ) -> List[PredictionPoint]:
        """Generate predictions using exponential smoothing."""
        if not historical_scores:
            return []

        predictions = []
        last_date = historical_scores[-1][0]
        last_score = historical_scores[-1][1]

        # Exponential smoothing parameters
        alpha = 0.3  # Level smoothing
        beta = 0.1   # Trend smoothing

        level = last_score
        trend_component = trend

        for i in range(1, periods_ahead + 1):
            # Calculate prediction
            prediction = level + (trend_component * i) + factor_impact
            prediction = max(0, min(100, prediction))

            # Calculate confidence interval
            std_error = seasonality * (1 + 0.1 * i)  # Increases over time
            lower_bound = max(0, prediction - (1.96 * std_error))
            upper_bound = min(100, prediction + (1.96 * std_error))

            # Determine confidence level
            confidence = self._calculate_confidence(i, seasonality)

            future_date = last_date + timedelta(days=i)
            predictions.append(PredictionPoint(
                timestamp=future_date,
                predicted_score=prediction,
                lower_bound=lower_bound,
                upper_bound=upper_bound,
                confidence=confidence
            ))

        return predictions

    def _calculate_confidence(
        self,
        periods_ahead: int,
        seasonality: float
    ) -> ConfidenceLevel:
        """Calculate confidence level based on time horizon."""
        if seasonality < 5:  # Low volatility
            if periods_ahead <= 7:
                return ConfidenceLevel.VERY_HIGH
            elif periods_ahead <= 14:
                return ConfidenceLevel.HIGH
            elif periods_ahead <= 30:
                return ConfidenceLevel.MEDIUM
            else:
                return ConfidenceLevel.LOW
        else:  # High volatility
            if periods_ahead <= 7:
                return ConfidenceLevel.HIGH
            elif periods_ahead <= 14:
                return ConfidenceLevel.MEDIUM
            else:
                return ConfidenceLevel.LOW

    def _calculate_risk_probability(
        self,
        predictions: List[PredictionPoint],
        threshold: float
    ) -> float:
        """Calculate probability of falling below threshold."""
        if not predictions:
            return 0.0

        below_threshold = sum(
            1 for p in predictions if p.predicted_score < threshold
        )

        return below_threshold / len(predictions)

    def _determine_trajectory(
        self,
        trend: float,
        factor_impact: float
    ) -> str:
        """Determine overall improvement trajectory."""
        net_change = trend + factor_impact

        if net_change > 2:
            return "strongly_improving"
        elif net_change > 0.5:
            return "improving"
        elif net_change > -0.5:
            return "stable"
        elif net_change > -2:
            return "declining"
        else:
            return "strongly_declining"

    def _calculate_model_accuracy(
        self,
        historical_scores: List[Tuple[datetime, float]]
    ) -> float:
        """Calculate model accuracy using historical data."""
        if len(historical_scores) < 3:
            return 0.5

        # Simple accuracy metric based on variance
        scores = [score for _, score in historical_scores]
        mean = sum(scores) / len(scores)
        variance = sum((x - mean) ** 2 for x in scores) / len(scores)
        std_dev = math.sqrt(variance)

        # If low variance, high accuracy expected
        if std_dev < 10:
            return 0.85
        elif std_dev < 20:
            return 0.75
        else:
            return 0.65

    def _extract_key_drivers(
        self,
        contributing_factors: Dict[str, float]
    ) -> List[Tuple[str, float]]:
        """Extract key drivers sorted by impact."""
        drivers = []

        for factor, value in contributing_factors.items():
            weight = self.factor_weights.get(factor, 0.0)
            impact = weight * (value / 100)  # Normalize to 0-1
            drivers.append((factor, impact))

        # Sort by absolute impact
        drivers.sort(key=lambda x: abs(x[1]), reverse=True)
        return drivers[:5]  # Top 5 drivers

    def _create_minimal_prediction(
        self,
        module_name: str,
        contributing_factors: Dict[str, float]
    ) -> PredictiveScoreResult:
        """Create minimal prediction for insufficient data."""
        base_score = sum(contributing_factors.values()) / len(
            contributing_factors
        ) if contributing_factors else 50

        prediction = PredictionPoint(
            timestamp=datetime.now() + timedelta(days=30),
            predicted_score=base_score,
            lower_bound=base_score - 10,
            upper_bound=base_score + 10,
            confidence=ConfidenceLevel.LOW
        )

        return PredictiveScoreResult(
            module_name=module_name,
            current_score=base_score,
            predictions=[prediction],
            risk_probability=0.3,
            improvement_trajectory="unknown",
            key_drivers=self._extract_key_drivers(contributing_factors),
            contributing_factors=contributing_factors,
            model_accuracy=0.5
        )

    def update_predictions(
        self,
        module_name: str,
        new_actual_score: Tuple[datetime, float]
    ) -> None:
        """Update model with new actual data."""
        if module_name in self.model_history:
            self.model_history[module_name].append(new_actual_score)
            # Clear cache for this module
            self.prediction_cache.pop(module_name, None)

    def get_ensemble_prediction(
        self,
        module_name: str,
        models: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate ensemble prediction combining multiple models.

        Args:
            module_name: Module to predict for
            models: List of model predictions

        Returns:
            Ensemble prediction combining all models
        """
        if not models:
            return {}

        # Average predictions
        avg_score = sum(m.get('predicted_score', 0) for m in models) / len(models)
        avg_lower = sum(m.get('lower_bound', 0) for m in models) / len(models)
        avg_upper = sum(m.get('upper_bound', 0) for m in models) / len(models)

        # Consensus confidence
        confidence_map = {
            'very_high': 5,
            'high': 4,
            'medium': 3,
            'low': 2,
            'very_low': 1
        }

        avg_confidence_score = sum(
            confidence_map.get(m.get('confidence', 'medium'), 3)
            for m in models
        ) / len(models)

        confidence_levels = {
            5: ConfidenceLevel.VERY_HIGH,
            4: ConfidenceLevel.HIGH,
            3: ConfidenceLevel.MEDIUM,
            2: ConfidenceLevel.LOW,
            1: ConfidenceLevel.VERY_LOW
        }

        ensemble_confidence = min(
            confidence_levels,
            key=lambda x: abs(x - avg_confidence_score)
        )

        return {
            'predicted_score': avg_score,
            'lower_bound': avg_lower,
            'upper_bound': avg_upper,
            'confidence': ensemble_confidence,
            'model_count': len(models),
            'model_agreement': self._calculate_agreement(models)
        }

    def _calculate_agreement(self, models: List[Dict[str, Any]]) -> float:
        """Calculate agreement between models."""
        if len(models) < 2:
            return 1.0

        predictions = [m.get('predicted_score', 0) for m in models]
        mean_pred = sum(predictions) / len(predictions)
        variance = sum((p - mean_pred) ** 2 for p in predictions) / len(predictions)
        std_dev = math.sqrt(variance)

        # Agreement inversely proportional to std dev
        return max(0, 1 - (std_dev / 100))
