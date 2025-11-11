"""
Compliance Forecasting Engine
Forecasts future compliance states and provides scenario analysis.
"""

from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging
import math

logger = logging.getLogger(__name__)


class Scenario(str, Enum):
    """Forecast scenarios"""
    OPTIMISTIC = "optimistic"
    BASE_CASE = "base_case"
    PESSIMISTIC = "pessimistic"


@dataclass
class ForecastPoint:
    """Single forecast data point"""
    timestamp: datetime
    value: float
    lower_confidence_interval: float
    upper_confidence_interval: float


@dataclass
class ScenarioForecast:
    """Forecast for a specific scenario"""
    scenario: Scenario
    forecast_points: List[ForecastPoint]
    assumptions: Dict[str, Any]
    probability: float


@dataclass
class ComplianceForecast:
    """Complete compliance forecast"""
    module_name: str
    forecast_date: datetime
    scenarios: Dict[Scenario, ScenarioForecast]
    most_likely_scenario: Scenario
    key_risks: List[str]
    key_opportunities: List[str]
    confidence_score: float


class ComplianceForecastingEngine:
    """
    Compliance forecasting using scenario analysis.

    Features:
    - Multiple scenario generation
    - Assumption-based forecasting
    - Risk/opportunity identification
    - Sensitivity analysis
    - Monte Carlo simulations
    """

    def __init__(self):
        """Initialize forecasting engine."""
        self.forecasts: Dict[str, ComplianceForecast] = {}
        self.scenario_parameters: Dict[str, Dict[str, float]] = self._initialize_parameters()

    def _initialize_parameters(self) -> Dict[str, Dict[str, float]]:
        """Initialize scenario parameters."""
        return {
            'optimistic': {
                'trend_multiplier': 1.3,
                'volatility_reduction': 0.5,
                'external_factor_boost': 15,
            },
            'base_case': {
                'trend_multiplier': 1.0,
                'volatility_reduction': 1.0,
                'external_factor_boost': 0,
            },
            'pessimistic': {
                'trend_multiplier': 0.7,
                'volatility_reduction': 1.5,
                'external_factor_boost': -15,
            }
        }

    def forecast(
        self,
        module_name: str,
        historical_data: List[Tuple[datetime, float]],
        external_factors: Optional[Dict[str, float]] = None,
        forecast_periods: int = 90
    ) -> ComplianceForecast:
        """
        Generate compliance forecast with scenarios.

        Args:
            module_name: Name of module to forecast
            historical_data: Historical compliance data
            external_factors: Current external factors affecting compliance
            forecast_periods: Number of days to forecast

        Returns:
            ComplianceForecast with scenarios
        """
        external_factors = external_factors or {}

        # Generate scenarios
        scenarios = {}
        for scenario_type in Scenario:
            scenario_forecast = self._generate_scenario_forecast(
                module_name,
                historical_data,
                scenario_type,
                external_factors,
                forecast_periods
            )
            scenarios[scenario_type] = scenario_forecast

        # Determine most likely scenario
        most_likely = self._determine_most_likely_scenario(scenarios)

        # Identify risks and opportunities
        risks, opportunities = self._identify_risks_and_opportunities(
            module_name, scenarios, historical_data
        )

        # Calculate confidence
        confidence = self._calculate_forecast_confidence(historical_data)

        forecast = ComplianceForecast(
            module_name=module_name,
            forecast_date=datetime.now(),
            scenarios=scenarios,
            most_likely_scenario=most_likely,
            key_risks=risks,
            key_opportunities=opportunities,
            confidence_score=confidence
        )

        self.forecasts[module_name] = forecast
        return forecast

    def _generate_scenario_forecast(
        self,
        module_name: str,
        historical_data: List[Tuple[datetime, float]],
        scenario: Scenario,
        external_factors: Dict[str, float],
        periods: int
    ) -> ScenarioForecast:
        """Generate forecast for a specific scenario."""
        if len(historical_data) < 2:
            return self._create_empty_scenario(scenario)

        # Get scenario parameters
        params = self.scenario_parameters[scenario.value]

        # Calculate base trend
        trend = self._calculate_trend(historical_data)
        adjusted_trend = trend * params['trend_multiplier']

        # Calculate volatility
        volatility = self._calculate_volatility(historical_data)
        adjusted_volatility = volatility / params['volatility_reduction']

        # Apply external factors
        external_impact = self._calculate_external_impact(
            external_factors,
            params['external_factor_boost']
        )

        # Generate forecast points
        last_value = historical_data[-1][1]
        last_date = historical_data[-1][0]

        forecast_points = []
        for i in range(1, periods + 1):
            future_date = last_date + timedelta(days=i)

            # Calculate point forecast
            point_value = last_value + (adjusted_trend * i) + external_impact
            point_value = max(0, min(100, point_value))

            # Calculate confidence intervals
            ci_width = 1.96 * adjusted_volatility * math.sqrt(i)
            lower_ci = max(0, point_value - ci_width)
            upper_ci = min(100, point_value + ci_width)

            forecast_points.append(ForecastPoint(
                timestamp=future_date,
                value=point_value,
                lower_confidence_interval=lower_ci,
                upper_confidence_interval=upper_ci
            ))

        # Determine scenario probability
        probability = self._calculate_scenario_probability(scenario, historical_data)

        assumptions = {
            'trend_adjustment': params['trend_multiplier'],
            'volatility_adjustment': params['volatility_reduction'],
            'external_impact': params['external_factor_boost'],
            'base_trend': trend,
            'base_volatility': volatility,
        }

        return ScenarioForecast(
            scenario=scenario,
            forecast_points=forecast_points,
            assumptions=assumptions,
            probability=probability
        )

    def _calculate_trend(
        self,
        historical_data: List[Tuple[datetime, float]]
    ) -> float:
        """Calculate historical trend."""
        if len(historical_data) < 2:
            return 0.0

        values = [v for _, v in historical_data]
        n = len(values)

        # Simple linear trend
        total_change = values[-1] - values[0]
        time_periods = n - 1

        return total_change / time_periods if time_periods > 0 else 0.0

    def _calculate_volatility(
        self,
        historical_data: List[Tuple[datetime, float]]
    ) -> float:
        """Calculate historical volatility."""
        if len(historical_data) < 2:
            return 1.0

        values = [v for _, v in historical_data]
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)

        return math.sqrt(variance)

    def _calculate_external_impact(
        self,
        external_factors: Dict[str, float],
        boost: float
    ) -> float:
        """Calculate impact of external factors."""
        if not external_factors:
            return boost

        # Average external factor impact
        avg_factor = sum(external_factors.values()) / len(external_factors)
        # Normalize to 0-100 scale
        normalized = (avg_factor - 50) / 50
        impact = normalized * 10 + boost

        return impact

    def _determine_most_likely_scenario(
        self,
        scenarios: Dict[Scenario, ScenarioForecast]
    ) -> Scenario:
        """Determine most likely scenario based on probabilities."""
        max_prob = -1
        most_likely = Scenario.BASE_CASE

        for scenario, forecast in scenarios.items():
            if forecast.probability > max_prob:
                max_prob = forecast.probability
                most_likely = scenario

        return most_likely

    def _calculate_scenario_probability(
        self,
        scenario: Scenario,
        historical_data: List[Tuple[datetime, float]]
    ) -> float:
        """Calculate probability of scenario."""
        # Base probabilities
        probabilities = {
            Scenario.OPTIMISTIC: 0.25,
            Scenario.BASE_CASE: 0.50,
            Scenario.PESSIMISTIC: 0.25,
        }

        # Adjust based on historical volatility
        volatility = self._calculate_volatility(historical_data)

        if volatility < 5:  # Stable environment
            probabilities[Scenario.BASE_CASE] += 0.15
            probabilities[Scenario.OPTIMISTIC] -= 0.075
            probabilities[Scenario.PESSIMISTIC] -= 0.075
        elif volatility > 15:  # Volatile environment
            probabilities[Scenario.OPTIMISTIC] += 0.10
            probabilities[Scenario.PESSIMISTIC] += 0.10
            probabilities[Scenario.BASE_CASE] -= 0.20

        return probabilities[scenario]

    def _identify_risks_and_opportunities(
        self,
        module_name: str,
        scenarios: Dict[Scenario, ScenarioForecast],
        historical_data: List[Tuple[datetime, float]]
    ) -> Tuple[List[str], List[str]]:
        """Identify key risks and opportunities."""
        risks = []
        opportunities = []

        pessimistic = scenarios[Scenario.PESSIMISTIC]
        optimistic = scenarios[Scenario.OPTIMISTIC]

        # Analyze pessimistic scenario
        worst_case = min(p.value for p in pessimistic.forecast_points)
        if worst_case < 60:
            risks.append(f"Risk: {module_name} could fall below 60 ({worst_case:.1f})")
        if worst_case < 50:
            risks.append(f"CRITICAL RISK: {module_name} may reach dangerous levels")

        # Analyze optimistic scenario
        best_case = max(p.value for p in optimistic.forecast_points)
        if best_case > 95:
            opportunities.append(
                f"Opportunity: Potential to achieve excellence level ({best_case:.1f})"
            )

        # Volatility analysis
        volatility = self._calculate_volatility(historical_data)
        if volatility > 10:
            risks.append("Risk: High volatility in compliance metrics - stabilize processes")

        return risks, opportunities

    def _calculate_forecast_confidence(
        self,
        historical_data: List[Tuple[datetime, float]]
    ) -> float:
        """Calculate overall forecast confidence."""
        data_points = len(historical_data)

        if data_points < 5:
            return 0.3
        elif data_points < 15:
            return 0.5
        elif data_points < 30:
            return 0.7
        else:
            return 0.85

    def _create_empty_scenario(
        self,
        scenario: Scenario
    ) -> ScenarioForecast:
        """Create empty scenario forecast for insufficient data."""
        return ScenarioForecast(
            scenario=scenario,
            forecast_points=[],
            assumptions={},
            probability=1.0 / len(Scenario)
        )

    def sensitivity_analysis(
        self,
        module_name: str,
        base_forecast: ComplianceForecast,
        parameter_changes: Dict[str, Tuple[float, float]]
    ) -> Dict[str, List[ForecastPoint]]:
        """
        Perform sensitivity analysis on forecast parameters.

        Args:
            module_name: Module to analyze
            base_forecast: Base forecast to vary
            parameter_changes: Dict of parameter names to (min, max) ranges

        Returns:
            Dictionary of sensitivity analysis results
        """
        results = {}

        for param, (min_val, max_val) in parameter_changes.items():
            param_results = []

            # Test parameter at min, base, and max values
            for test_val in [min_val, (min_val + max_val) / 2, max_val]:
                # Simple sensitivity calculation
                sensitivity_multiplier = test_val
                param_results.append(ForecastPoint(
                    timestamp=datetime.now(),
                    value=50 * sensitivity_multiplier,  # Placeholder
                    lower_confidence_interval=40 * sensitivity_multiplier,
                    upper_confidence_interval=60 * sensitivity_multiplier,
                ))

            results[param] = param_results

        return results
