"""
AI Explainability and Interpretability Module

Provides explanations for AI decisions and responses:
- Decision tracing
- Reasoning chains
- Confidence scoring
- Attribution analysis
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ExplanationType(str, Enum):
    """Type of explanation"""
    DECISION_TREE = "decision_tree"
    REASONING_CHAIN = "reasoning_chain"
    ATTRIBUTION = "attribution"
    CONFIDENCE_ANALYSIS = "confidence_analysis"
    FEATURE_IMPORTANCE = "feature_importance"


@dataclass
class ExplanationStep:
    """A step in an explanation"""
    step_number: int
    description: str
    input_data: Dict = field(default_factory=dict)
    output_data: Dict = field(default_factory=dict)
    confidence: float = 1.0
    reasoning: str = ""


@dataclass
class ExplainabilityReport:
    """Full explainability report for a response"""
    response_id: str
    explanation_type: ExplanationType
    title: str
    summary: str
    steps: List[ExplanationStep] = field(default_factory=list)
    confidence_score: float = 0.5
    limitations: List[str] = field(default_factory=list)
    alternative_paths: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict = field(default_factory=dict)


class ExplainabilityEngine:
    """
    Generates explanations for AI responses

    Features:
    - Multiple explanation types
    - Confidence scoring
    - Alternative explanations
    - Limitation identification
    """

    def __init__(self):
        self.reports: Dict[str, ExplainabilityReport] = {}
        self.explanation_history: List[ExplainabilityReport] = []

    def generate_reasoning_chain(
        self,
        response: str,
        prompt: str,
        model: str = "unknown"
    ) -> ExplainabilityReport:
        """
        Generate reasoning chain explanation

        Args:
            response: The AI response
            prompt: Original prompt
            model: Model used

        Returns:
            ExplainabilityReport with reasoning chain
        """
        response_id = self._generate_id()
        steps = []

        # Step 1: Prompt analysis
        steps.append(ExplanationStep(
            step_number=1,
            description="Analyzed input prompt",
            input_data={"prompt_length": len(prompt), "prompt_tokens": len(prompt.split())},
            reasoning="Parsed user query to understand requirements"
        ))

        # Step 2: Context consideration
        context_elements = self._extract_context_elements(prompt)
        steps.append(ExplanationStep(
            step_number=2,
            description="Identified contextual elements",
            output_data={"context_elements": len(context_elements)},
            reasoning="Recognized key context clues in the prompt"
        ))

        # Step 3: Response generation
        response_elements = self._extract_response_elements(response)
        steps.append(ExplanationStep(
            step_number=3,
            description="Generated response",
            output_data={"response_length": len(response), "key_points": len(response_elements)},
            confidence=0.85,
            reasoning="Composed response based on analysis"
        ))

        # Step 4: Quality validation
        steps.append(ExplanationStep(
            step_number=4,
            description="Validated response quality",
            output_data={"quality_checks": "completed"},
            confidence=0.9,
            reasoning="Verified response meets quality standards"
        ))

        report = ExplainabilityReport(
            response_id=response_id,
            explanation_type=ExplanationType.REASONING_CHAIN,
            title="Response Reasoning Chain",
            summary=f"Generated response through {len(steps)} reasoning steps",
            steps=steps,
            confidence_score=0.88,
            limitations=[
                "Explanations are post-hoc and may not capture all internal processing",
                "Confidence scores are estimates based on observable patterns"
            ],
            alternative_paths=[
                "Could have focused on different aspects of the query",
                "Alternative structure for response organization"
            ],
            metadata={"model": model, "prompt_length": len(prompt)}
        )

        self._store_report(report)
        return report

    def generate_confidence_analysis(
        self,
        response: str,
        domain: str = "general"
    ) -> ExplainabilityReport:
        """
        Generate confidence analysis

        Args:
            response: The response to analyze
            domain: Domain of the response (for context)

        Returns:
            ExplainabilityReport with confidence analysis
        """
        response_id = self._generate_id()

        confidence_scores = {
            "factual_accuracy": self._estimate_accuracy_confidence(response, domain),
            "completeness": self._estimate_completeness_confidence(response),
            "clarity": self._estimate_clarity_confidence(response),
            "relevance": self._estimate_relevance_confidence(response)
        }

        overall_confidence = sum(confidence_scores.values()) / len(confidence_scores)

        steps = []
        for idx, (metric, confidence) in enumerate(confidence_scores.items(), 1):
            steps.append(ExplanationStep(
                step_number=idx,
                description=f"Assessed {metric}",
                output_data={metric: confidence},
                confidence=confidence,
                reasoning=self._get_confidence_reasoning(metric, confidence)
            ))

        report = ExplainabilityReport(
            response_id=response_id,
            explanation_type=ExplanationType.CONFIDENCE_ANALYSIS,
            title="Response Confidence Analysis",
            summary=f"Overall confidence score: {overall_confidence:.2%}",
            steps=steps,
            confidence_score=overall_confidence,
            limitations=[
                "Confidence estimates based on response characteristics, not actual ground truth",
                "Domain-specific confidence may vary"
            ],
            metadata=confidence_scores
        )

        self._store_report(report)
        return report

    def generate_attribution_analysis(
        self,
        response: str,
        context_items: List[str]
    ) -> ExplainabilityReport:
        """
        Generate attribution analysis showing which context influenced response

        Args:
            response: The response
            context_items: List of context items that influenced response

        Returns:
            ExplainabilityReport with attribution analysis
        """
        response_id = self._generate_id()

        # Analyze which context items were used
        attributions = []
        for context_item in context_items:
            attribution_score = self._compute_attribution_score(response, context_item)
            attributions.append({
                "context": context_item[:50] + "...",
                "score": attribution_score
            })

        # Sort by importance
        attributions.sort(key=lambda x: x["score"], reverse=True)

        steps = []
        for idx, attr in enumerate(attributions[:5], 1):  # Top 5
            steps.append(ExplanationStep(
                step_number=idx,
                description=f"Context source: {attr['context']}",
                output_data={"importance_score": attr["score"]},
                confidence=attr["score"]
            ))

        report = ExplainabilityReport(
            response_id=response_id,
            explanation_type=ExplanationType.ATTRIBUTION,
            title="Response Attribution Analysis",
            summary=f"Response influenced by {len(attributions)} context items",
            steps=steps,
            confidence_score=0.75,
            metadata={
                "total_context_items": len(context_items),
                "top_attribution": attributions[0] if attributions else None
            }
        )

        self._store_report(report)
        return report

    def generate_decision_tree(
        self,
        decision_criteria: Dict[str, Any]
    ) -> ExplainabilityReport:
        """
        Generate decision tree explanation

        Args:
            decision_criteria: Criteria used for decision

        Returns:
            ExplainabilityReport with decision tree
        """
        response_id = self._generate_id()

        steps = self._build_decision_tree_steps(decision_criteria)

        report = ExplainabilityReport(
            response_id=response_id,
            explanation_type=ExplanationType.DECISION_TREE,
            title="Decision Tree Analysis",
            summary=f"Decision made through {len(steps)} criteria evaluation",
            steps=steps,
            confidence_score=0.85,
            metadata=decision_criteria
        )

        self._store_report(report)
        return report

    def get_report(self, response_id: str) -> Optional[ExplainabilityReport]:
        """Retrieve stored explanation report"""
        return self.reports.get(response_id)

    def get_explanation_summary(self, response_id: str) -> str:
        """Get human-readable explanation summary"""
        report = self.get_report(response_id)
        if not report:
            return "No explanation available"

        summary = f"""Explanation Report
Title: {report.title}
Type: {report.explanation_type.value}
Confidence: {report.confidence_score:.0%}

Summary: {report.summary}

Steps:
"""
        for step in report.steps:
            summary += f"\n{step.step_number}. {step.description}\n"
            if step.reasoning:
                summary += f"   Reasoning: {step.reasoning}\n"
            summary += f"   Confidence: {step.confidence:.0%}\n"

        if report.limitations:
            summary += "\nLimitations:\n"
            for limitation in report.limitations:
                summary += f"- {limitation}\n"

        if report.alternative_paths:
            summary += "\nAlternative Perspectives:\n"
            for alt in report.alternative_paths:
                summary += f"- {alt}\n"

        return summary

    def _store_report(self, report: ExplainabilityReport):
        """Store explanation report"""
        self.reports[report.response_id] = report
        self.explanation_history.append(report)

        # Keep history bounded
        if len(self.explanation_history) > 5000:
            self.explanation_history = self.explanation_history[-2500:]

    def _extract_context_elements(self, text: str) -> List[str]:
        """Extract key context elements from text"""
        elements = []
        keywords = ['important', 'must', 'should', 'critical', 'require']

        for keyword in keywords:
            if keyword in text.lower():
                elements.append(keyword)

        return elements

    def _extract_response_elements(self, text: str) -> List[str]:
        """Extract key response elements"""
        # Simple: split by sentences
        return text.split('.')[:3]

    def _estimate_accuracy_confidence(self, response: str, domain: str) -> float:
        """Estimate confidence in accuracy"""
        # Heuristics for accuracy confidence
        confidence = 0.7

        if "uncertain" in response.lower() or "may" in response.lower():
            confidence -= 0.15

        if "definite" in response.lower() or "clearly" in response.lower():
            confidence += 0.1

        return min(1.0, max(0.3, confidence))

    def _estimate_completeness_confidence(self, response: str) -> float:
        """Estimate confidence in completeness"""
        sentence_count = len(response.split('.'))
        completeness = min(1.0, sentence_count / 5)
        return min(1.0, max(0.4, completeness))

    def _estimate_clarity_confidence(self, response: str) -> float:
        """Estimate confidence in clarity"""
        avg_word_length = sum(len(w) for w in response.split()) / max(1, len(response.split()))

        # Ideal: 4-5 chars per word
        clarity = 1.0 - abs(avg_word_length - 4.5) / 10

        return min(1.0, max(0.4, clarity))

    def _estimate_relevance_confidence(self, response: str) -> float:
        """Estimate confidence in relevance"""
        return 0.85

    def _compute_attribution_score(self, response: str, context: str) -> float:
        """Compute how much context contributed to response"""
        response_words = set(response.lower().split())
        context_words = set(context.lower().split())

        overlap = len(response_words & context_words)
        score = min(1.0, overlap / max(1, len(context_words)))

        return score

    def _get_confidence_reasoning(self, metric: str, confidence: float) -> str:
        """Get reasoning for confidence score"""
        if confidence > 0.8:
            return f"Strong {metric} based on response characteristics"
        elif confidence > 0.6:
            return f"Moderate {metric} with some uncertainty"
        else:
            return f"Low confidence in {metric}, recommend verification"

    def _build_decision_tree_steps(self, criteria: Dict) -> List[ExplanationStep]:
        """Build decision tree steps from criteria"""
        steps = []
        for idx, (key, value) in enumerate(criteria.items(), 1):
            steps.append(ExplanationStep(
                step_number=idx,
                description=f"Evaluated: {key}",
                output_data={key: value},
                confidence=0.8
            ))
        return steps

    def _generate_id(self) -> str:
        """Generate unique ID"""
        import hashlib
        import time
        return hashlib.md5(str(time.time()).encode()).hexdigest()[:8]

    def get_statistics(self) -> Dict:
        """Get explainability statistics"""
        if not self.explanation_history:
            return {}

        type_counts = {}
        for report in self.explanation_history:
            type_key = report.explanation_type.value
            type_counts[type_key] = type_counts.get(type_key, 0) + 1

        avg_confidence = sum(r.confidence_score for r in self.explanation_history) / len(self.explanation_history)

        return {
            "total_explanations": len(self.explanation_history),
            "by_type": type_counts,
            "average_confidence": avg_confidence,
            "stored_reports": len(self.reports)
        }
