"""
Correction Quality Scoring System

Automatically scores the quality of corrections based on multiple criteria.

Scoring Dimensions:
- Completeness: Are all violations addressed?
- Accuracy: Are corrections semantically correct?
- Preservation: Is original meaning preserved?
- Structure: Is document structure maintained?
- Compliance: Does corrected text pass validation?
- Performance: Are corrections efficient?
"""

from typing import Dict, List, Optional, Tuple
import re
from dataclasses import dataclass


@dataclass
class QualityScore:
    """Container for quality scores."""

    overall_score: float  # 0-100
    completeness_score: float  # 0-100
    accuracy_score: float  # 0-100
    preservation_score: float  # 0-100
    structure_score: float  # 0-100
    compliance_score: float  # 0-100
    performance_score: float  # 0-100

    grade: str  # A+, A, B, C, D, F
    issues: List[str]
    recommendations: List[str]

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "overall_score": self.overall_score,
            "grade": self.grade,
            "dimensions": {
                "completeness": self.completeness_score,
                "accuracy": self.accuracy_score,
                "preservation": self.preservation_score,
                "structure": self.structure_score,
                "compliance": self.compliance_score,
                "performance": self.performance_score
            },
            "issues": self.issues,
            "recommendations": self.recommendations
        }


class CorrectionQualityScorer:
    """
    Scores correction quality across multiple dimensions.

    Usage:
        scorer = CorrectionQualityScorer()

        score = scorer.score_correction(
            original_text=original,
            corrected_text=corrected,
            correction_result=result,
            gates_before=gates_before,
            gates_after=gates_after
        )

        print(f"Quality Score: {score.overall_score}/100 ({score.grade})")
    """

    def __init__(self):
        self.weights = {
            'completeness': 0.25,
            'accuracy': 0.20,
            'preservation': 0.20,
            'structure': 0.15,
            'compliance': 0.15,
            'performance': 0.05
        }

    def score_correction(
        self,
        original_text: str,
        corrected_text: str,
        correction_result: Dict,
        gates_before: Optional[List[Tuple[str, Dict]]] = None,
        gates_after: Optional[List[Tuple[str, Dict]]] = None,
        processing_time_ms: Optional[float] = None
    ) -> QualityScore:
        """
        Score a correction across all dimensions.

        Args:
            original_text: Original document text
            corrected_text: Corrected document text
            correction_result: Result from correction synthesizer
            gates_before: Gate results before correction
            gates_after: Gate results after correction
            processing_time_ms: Processing time in milliseconds

        Returns:
            QualityScore object with scores and feedback
        """
        issues = []
        recommendations = []

        # Score each dimension
        completeness = self._score_completeness(
            correction_result, gates_before, gates_after, issues, recommendations
        )

        accuracy = self._score_accuracy(
            original_text, corrected_text, correction_result, issues, recommendations
        )

        preservation = self._score_preservation(
            original_text, corrected_text, issues, recommendations
        )

        structure = self._score_structure(
            original_text, corrected_text, issues, recommendations
        )

        compliance = self._score_compliance(
            gates_before, gates_after, issues, recommendations
        )

        performance = self._score_performance(
            original_text, processing_time_ms, issues, recommendations
        )

        # Calculate weighted overall score
        overall = (
            completeness * self.weights['completeness'] +
            accuracy * self.weights['accuracy'] +
            preservation * self.weights['preservation'] +
            structure * self.weights['structure'] +
            compliance * self.weights['compliance'] +
            performance * self.weights['performance']
        )

        grade = self._calculate_grade(overall)

        return QualityScore(
            overall_score=round(overall, 2),
            completeness_score=round(completeness, 2),
            accuracy_score=round(accuracy, 2),
            preservation_score=round(preservation, 2),
            structure_score=round(structure, 2),
            compliance_score=round(compliance, 2),
            performance_score=round(performance, 2),
            grade=grade,
            issues=issues,
            recommendations=recommendations
        )

    def _score_completeness(
        self,
        correction_result: Dict,
        gates_before: Optional[List[Tuple[str, Dict]]],
        gates_after: Optional[List[Tuple[str, Dict]]],
        issues: List[str],
        recommendations: List[str]
    ) -> float:
        """
        Score completeness: Were all violations addressed?

        Returns: 0-100
        """
        if not gates_before or not gates_after:
            return 100.0  # Can't measure without gate data

        # Count failures before and after
        failures_before = sum(
            1 for _, gate in gates_before
            if gate.get('status') in ['FAIL', 'WARNING']
        )

        failures_after = sum(
            1 for _, gate in gates_after
            if gate.get('status') in ['FAIL', 'WARNING']
        )

        if failures_before == 0:
            return 100.0  # Nothing to fix

        # Calculate completeness ratio
        fixed = failures_before - failures_after
        completeness = (fixed / failures_before * 100)

        if completeness < 50:
            issues.append("Many violations remain unfixed")
            recommendations.append("Review failing gates and add correction patterns")
        elif completeness < 80:
            recommendations.append("Consider additional correction strategies for remaining violations")

        return completeness

    def _score_accuracy(
        self,
        original: str,
        corrected: str,
        correction_result: Dict,
        issues: List[str],
        recommendations: List[str]
    ) -> float:
        """
        Score accuracy: Are corrections semantically correct?

        Returns: 0-100
        """
        score = 100.0

        # Check for common accuracy issues

        # 1. Empty or too-short output
        if len(corrected.strip()) < 10:
            score -= 50
            issues.append("Corrected text is too short or empty")
            return max(score, 0)

        # 2. Excessive deletions (>70% removed)
        if len(corrected) < len(original) * 0.3:
            score -= 30
            issues.append("Excessive content deletion (>70%)")
            recommendations.append("Review corrections - too much content removed")

        # 3. Excessive additions (>300% growth)
        if len(corrected) > len(original) * 3.0:
            score -= 20
            issues.append("Excessive content addition (>300% growth)")
            recommendations.append("Review template insertions - document grew too much")

        # 4. Check for corrupted structure indicators
        corruption_indicators = [
            (r'(\w)\1{10,}', "Repeated characters detected"),
            (r'[^\s]{200,}', "Extremely long words/tokens detected"),
            (r'[\x00-\x08\x0B\x0C\x0E-\x1F]', "Control characters in output")
        ]

        for pattern, message in corruption_indicators:
            if re.search(pattern, corrected):
                score -= 15
                issues.append(message)

        # 5. Metadata quality
        corrections = correction_result.get('corrections', [])
        for correction in corrections:
            if 'strategy' not in correction or 'gate_id' not in correction:
                score -= 5
                issues.append("Incomplete correction metadata")
                break

        return max(score, 0)

    def _score_preservation(
        self,
        original: str,
        corrected: str,
        issues: List[str],
        recommendations: List[str]
    ) -> float:
        """
        Score preservation: Is original meaning/content preserved?

        Returns: 0-100
        """
        score = 100.0

        # 1. Check essential information preservation

        # Email preservation
        original_emails = set(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', original))
        corrected_emails = set(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', corrected))

        if original_emails and not original_emails.issubset(corrected_emails):
            score -= 20
            issues.append("Email addresses were lost or modified")
            recommendations.append("Ensure contact information is preserved")

        # URL preservation
        original_urls = set(re.findall(r'https?://[^\s]+', original))
        corrected_urls = set(re.findall(r'https?://[^\s]+', corrected))

        if original_urls and not original_urls.issubset(corrected_urls):
            score -= 15
            issues.append("URLs were lost or modified")

        # Phone number preservation
        original_phones = set(re.findall(r'\b0\d{3}[- ]?\d{3}[- ]?\d{4}\b', original))
        corrected_phones = set(re.findall(r'\b0\d{3}[- ]?\d{3}[- ]?\d{4}\b', corrected))

        if original_phones and not original_phones.issubset(corrected_phones):
            score -= 10
            issues.append("Phone numbers were lost or modified")

        # 2. Check for semantic preservation (basic)

        # Currency amounts should be preserved
        original_amounts = set(re.findall(r'£\d+(?:,\d{3})*(?:\.\d{2})?', original))
        corrected_amounts = set(re.findall(r'£\d+(?:,\d{3})*(?:\.\d{2})?', corrected))

        if original_amounts:
            preserved_amounts = len(original_amounts & corrected_amounts)
            preservation_rate = preserved_amounts / len(original_amounts)
            if preservation_rate < 0.8:
                score -= 10
                issues.append("Some monetary amounts were changed")

        return max(score, 0)

    def _score_structure(
        self,
        original: str,
        corrected: str,
        issues: List[str],
        recommendations: List[str]
    ) -> float:
        """
        Score structure: Is document structure maintained?

        Returns: 0-100
        """
        score = 100.0

        # 1. Line structure preservation
        original_lines = original.count('\n')
        corrected_lines = corrected.count('\n')

        if original_lines > 0:
            line_change_ratio = abs(corrected_lines - original_lines) / original_lines

            if line_change_ratio > 1.0:  # >100% change
                score -= 20
                issues.append("Document line structure significantly altered")

        # 2. Paragraph structure (double newlines)
        original_paragraphs = original.count('\n\n')
        corrected_paragraphs = corrected.count('\n\n')

        if original_paragraphs > 0:
            para_preservation = corrected_paragraphs / original_paragraphs
            if para_preservation < 0.5:
                score -= 15
                issues.append("Paragraph structure collapsed")
                recommendations.append("Preserve paragraph breaks during corrections")

        # 3. Section headers preservation
        original_headers = len(re.findall(r'^#+\s+.+$', original, re.MULTILINE))
        corrected_headers = len(re.findall(r'^#+\s+.+$', corrected, re.MULTILINE))

        if original_headers > 0 and corrected_headers < original_headers * 0.8:
            score -= 10
            issues.append("Section headers may have been lost")

        # 4. List structure preservation
        original_lists = len(re.findall(r'^\s*[-*•]\s+', original, re.MULTILINE))
        corrected_lists = len(re.findall(r'^\s*[-*•]\s+', corrected, re.MULTILINE))

        if original_lists > 5 and corrected_lists < original_lists * 0.7:
            score -= 10
            issues.append("List structure may have been disrupted")

        return max(score, 0)

    def _score_compliance(
        self,
        gates_before: Optional[List[Tuple[str, Dict]]],
        gates_after: Optional[List[Tuple[str, Dict]]],
        issues: List[str],
        recommendations: List[str]
    ) -> float:
        """
        Score compliance: Does corrected text pass validation?

        Returns: 0-100
        """
        if not gates_after:
            return 100.0  # Can't measure without gate data

        # Count remaining failures
        failures_after = sum(
            1 for _, gate in gates_after
            if gate.get('status') in ['FAIL', 'WARNING']
        )

        if failures_after == 0:
            return 100.0  # Perfect compliance

        total_gates = len(gates_after)
        pass_rate = ((total_gates - failures_after) / total_gates * 100)

        if pass_rate < 70:
            issues.append("Low compliance score after correction")
            recommendations.append("Many gates still failing - review correction strategies")
        elif pass_rate < 90:
            recommendations.append("Consider additional corrections for remaining failures")

        return pass_rate

    def _score_performance(
        self,
        original_text: str,
        processing_time_ms: Optional[float],
        issues: List[str],
        recommendations: List[str]
    ) -> float:
        """
        Score performance: Are corrections efficient?

        Returns: 0-100
        """
        if processing_time_ms is None:
            return 100.0  # Can't measure without timing

        doc_size_kb = len(original_text) / 1024

        # Expected performance (rough baseline)
        # Small docs (<1KB): <100ms
        # Medium docs (1-10KB): <500ms
        # Large docs (10-50KB): <2000ms

        if doc_size_kb < 1:
            expected_ms = 100
        elif doc_size_kb < 10:
            expected_ms = 500
        else:
            expected_ms = 2000

        if processing_time_ms <= expected_ms:
            return 100.0

        # Calculate performance score
        ratio = expected_ms / processing_time_ms
        score = ratio * 100

        if score < 50:
            issues.append(f"Slow processing: {processing_time_ms:.0f}ms (expected <{expected_ms}ms)")
            recommendations.append("Review correction patterns for performance bottlenecks")
        elif score < 80:
            recommendations.append("Consider optimizing correction strategies")

        return max(min(score, 100), 0)

    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from score."""
        if score >= 97:
            return "A+"
        elif score >= 93:
            return "A"
        elif score >= 90:
            return "A-"
        elif score >= 87:
            return "B+"
        elif score >= 83:
            return "B"
        elif score >= 80:
            return "B-"
        elif score >= 77:
            return "C+"
        elif score >= 73:
            return "C"
        elif score >= 70:
            return "C-"
        elif score >= 67:
            return "D+"
        elif score >= 63:
            return "D"
        elif score >= 60:
            return "D-"
        else:
            return "F"


class BatchQualityAnalyzer:
    """Analyze quality across multiple corrections."""

    def __init__(self):
        self.scorer = CorrectionQualityScorer()
        self.scores: List[QualityScore] = []

    def add_score(self, score: QualityScore):
        """Add a quality score to the batch."""
        self.scores.append(score)

    def get_summary(self) -> Dict:
        """Get summary of all scores."""
        if not self.scores:
            return {"error": "No scores collected"}

        overall_scores = [s.overall_score for s in self.scores]

        # Grade distribution
        grade_dist = {}
        for score in self.scores:
            grade_dist[score.grade] = grade_dist.get(score.grade, 0) + 1

        # Common issues
        all_issues = []
        for score in self.scores:
            all_issues.extend(score.issues)

        issue_freq = {}
        for issue in all_issues:
            issue_freq[issue] = issue_freq.get(issue, 0) + 1

        return {
            "total_corrections": len(self.scores),
            "average_score": sum(overall_scores) / len(overall_scores),
            "median_score": sorted(overall_scores)[len(overall_scores) // 2],
            "min_score": min(overall_scores),
            "max_score": max(overall_scores),
            "grade_distribution": grade_dist,
            "common_issues": dict(sorted(issue_freq.items(), key=lambda x: x[1], reverse=True)[:5])
        }


# Convenience function
def quick_quality_score(original: str, corrected: str, correction_result: Dict) -> QualityScore:
    """Quick quality scoring without gate data."""
    scorer = CorrectionQualityScorer()
    return scorer.score_correction(original, corrected, correction_result)
