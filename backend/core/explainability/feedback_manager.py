"""
Feedback Manager
Collects and manages user feedback on corrections for continuous improvement
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import uuid


class FeedbackType(Enum):
    """Types of feedback"""
    ACCEPT = "accept"  # Correction accepted
    REJECT = "reject"  # Correction rejected
    MODIFY = "modify"  # Correction modified
    DEFER = "defer"  # Correction deferred for review


class RejectionReason(Enum):
    """Reasons for rejection"""
    INACCURATE = "inaccurate"  # Correction is factually wrong
    INAPPROPRIATE = "inappropriate"  # Doesn't fit context
    TOO_AGGRESSIVE = "too_aggressive"  # Changes too much
    TOO_CONSERVATIVE = "too_conservative"  # Doesn't go far enough
    WRONG_REGULATION = "wrong_regulation"  # Wrong regulatory interpretation
    STYLE_MISMATCH = "style_mismatch"  # Doesn't match document style
    OTHER = "other"


@dataclass
class CorrectionFeedback:
    """Feedback on a single correction"""

    feedback_id: str
    correction_id: str
    timestamp: datetime

    # Feedback details
    feedback_type: FeedbackType
    user_id: str
    user_role: str  # e.g., "legal_counsel", "compliance_officer", "document_owner"

    # Rejection details (if applicable)
    rejection_reason: Optional[RejectionReason] = None
    rejection_details: str = ""

    # Modification details (if applicable)
    modified_text: Optional[str] = None
    modification_reason: str = ""

    # Additional comments
    comments: str = ""
    suggestions: str = ""

    # Rating (1-5)
    accuracy_rating: Optional[int] = None
    usefulness_rating: Optional[int] = None
    explanation_clarity_rating: Optional[int] = None

    # Metadata
    document_type: str = ""
    gate_id: str = ""
    severity: str = ""


@dataclass
class FeedbackAnalytics:
    """Analytics on feedback patterns"""

    # Overall metrics
    total_feedback: int
    acceptance_rate: float
    rejection_rate: float
    modification_rate: float

    # By gate
    gate_performance: Dict[str, Dict[str, float]]

    # By severity
    severity_performance: Dict[str, Dict[str, float]]

    # Common issues
    top_rejection_reasons: List[tuple[str, int]]
    common_modifications: List[str]

    # Ratings
    average_accuracy_rating: float
    average_usefulness_rating: float
    average_clarity_rating: float

    # Trends
    improvement_trend: str  # "improving", "stable", "declining"
    areas_for_improvement: List[str]


class FeedbackManager:
    """
    Manages user feedback on corrections for continuous improvement

    Features:
    - Structured feedback collection
    - Feedback analytics and reporting
    - Learning from rejections
    - Performance tracking by gate/severity
    - Continuous improvement recommendations
    """

    def __init__(self):
        self.feedback_store: Dict[str, CorrectionFeedback] = {}
        self.correction_feedback_map: Dict[str, List[str]] = {}  # correction_id -> feedback_ids

    def submit_feedback(
        self,
        correction_id: str,
        feedback_type: FeedbackType,
        user_id: str,
        user_role: str,
        **kwargs
    ) -> CorrectionFeedback:
        """
        Submit feedback on a correction

        Args:
            correction_id: ID of the correction
            feedback_type: Type of feedback
            user_id: User submitting feedback
            user_role: Role of user
            **kwargs: Additional feedback details

        Returns:
            CorrectionFeedback object
        """
        feedback_id = str(uuid.uuid4())

        feedback = CorrectionFeedback(
            feedback_id=feedback_id,
            correction_id=correction_id,
            timestamp=datetime.utcnow(),
            feedback_type=feedback_type,
            user_id=user_id,
            user_role=user_role,
            rejection_reason=kwargs.get('rejection_reason'),
            rejection_details=kwargs.get('rejection_details', ''),
            modified_text=kwargs.get('modified_text'),
            modification_reason=kwargs.get('modification_reason', ''),
            comments=kwargs.get('comments', ''),
            suggestions=kwargs.get('suggestions', ''),
            accuracy_rating=kwargs.get('accuracy_rating'),
            usefulness_rating=kwargs.get('usefulness_rating'),
            explanation_clarity_rating=kwargs.get('explanation_clarity_rating'),
            document_type=kwargs.get('document_type', ''),
            gate_id=kwargs.get('gate_id', ''),
            severity=kwargs.get('severity', '')
        )

        # Store feedback
        self.feedback_store[feedback_id] = feedback

        # Map to correction
        if correction_id not in self.correction_feedback_map:
            self.correction_feedback_map[correction_id] = []
        self.correction_feedback_map[correction_id].append(feedback_id)

        return feedback

    def get_feedback(self, feedback_id: str) -> Optional[CorrectionFeedback]:
        """Retrieve specific feedback"""
        return self.feedback_store.get(feedback_id)

    def get_correction_feedback(self, correction_id: str) -> List[CorrectionFeedback]:
        """Get all feedback for a specific correction"""
        feedback_ids = self.correction_feedback_map.get(correction_id, [])
        return [self.feedback_store[fid] for fid in feedback_ids if fid in self.feedback_store]

    def analyze_feedback(
        self,
        gate_id: Optional[str] = None,
        severity: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> FeedbackAnalytics:
        """
        Analyze feedback patterns

        Args:
            gate_id: Filter by gate
            severity: Filter by severity
            start_date: Filter by start date
            end_date: Filter by end date

        Returns:
            FeedbackAnalytics
        """
        # Filter feedback
        feedback_list = list(self.feedback_store.values())

        if gate_id:
            feedback_list = [f for f in feedback_list if f.gate_id == gate_id]
        if severity:
            feedback_list = [f for f in feedback_list if f.severity == severity]
        if start_date:
            feedback_list = [f for f in feedback_list if f.timestamp >= start_date]
        if end_date:
            feedback_list = [f for f in feedback_list if f.timestamp <= end_date]

        total = len(feedback_list)

        if total == 0:
            return FeedbackAnalytics(
                total_feedback=0,
                acceptance_rate=0.0,
                rejection_rate=0.0,
                modification_rate=0.0,
                gate_performance={},
                severity_performance={},
                top_rejection_reasons=[],
                common_modifications=[],
                average_accuracy_rating=0.0,
                average_usefulness_rating=0.0,
                average_clarity_rating=0.0,
                improvement_trend="unknown",
                areas_for_improvement=[]
            )

        # Calculate rates
        accepts = len([f for f in feedback_list if f.feedback_type == FeedbackType.ACCEPT])
        rejects = len([f for f in feedback_list if f.feedback_type == FeedbackType.REJECT])
        modifies = len([f for f in feedback_list if f.feedback_type == FeedbackType.MODIFY])

        acceptance_rate = accepts / total
        rejection_rate = rejects / total
        modification_rate = modifies / total

        # Performance by gate
        gate_performance = self._calculate_gate_performance(feedback_list)

        # Performance by severity
        severity_performance = self._calculate_severity_performance(feedback_list)

        # Top rejection reasons
        rejection_reasons = [
            f.rejection_reason
            for f in feedback_list
            if f.rejection_reason
        ]
        from collections import Counter
        reason_counts = Counter(rejection_reasons)
        top_rejection_reasons = [
            (reason.value, count)
            for reason, count in reason_counts.most_common(5)
        ]

        # Common modifications
        common_modifications = self._identify_common_modifications(feedback_list)

        # Average ratings
        accuracy_ratings = [f.accuracy_rating for f in feedback_list if f.accuracy_rating]
        usefulness_ratings = [f.usefulness_rating for f in feedback_list if f.usefulness_rating]
        clarity_ratings = [f.explanation_clarity_rating for f in feedback_list if f.explanation_clarity_rating]

        avg_accuracy = sum(accuracy_ratings) / len(accuracy_ratings) if accuracy_ratings else 0
        avg_usefulness = sum(usefulness_ratings) / len(usefulness_ratings) if usefulness_ratings else 0
        avg_clarity = sum(clarity_ratings) / len(clarity_ratings) if clarity_ratings else 0

        # Trends
        improvement_trend = self._calculate_trend(feedback_list)

        # Areas for improvement
        areas = self._identify_improvement_areas(
            rejection_rate,
            modification_rate,
            gate_performance,
            top_rejection_reasons,
            avg_accuracy,
            avg_usefulness,
            avg_clarity
        )

        return FeedbackAnalytics(
            total_feedback=total,
            acceptance_rate=acceptance_rate,
            rejection_rate=rejection_rate,
            modification_rate=modification_rate,
            gate_performance=gate_performance,
            severity_performance=severity_performance,
            top_rejection_reasons=top_rejection_reasons,
            common_modifications=common_modifications,
            average_accuracy_rating=avg_accuracy,
            average_usefulness_rating=avg_usefulness,
            average_clarity_rating=avg_clarity,
            improvement_trend=improvement_trend,
            areas_for_improvement=areas
        )

    def _calculate_gate_performance(
        self,
        feedback_list: List[CorrectionFeedback]
    ) -> Dict[str, Dict[str, float]]:
        """Calculate performance metrics by gate"""
        gate_feedback: Dict[str, List[CorrectionFeedback]] = {}

        for feedback in feedback_list:
            gate = feedback.gate_id or 'unknown'
            if gate not in gate_feedback:
                gate_feedback[gate] = []
            gate_feedback[gate].append(feedback)

        performance = {}
        for gate, feedbacks in gate_feedback.items():
            total = len(feedbacks)
            accepts = len([f for f in feedbacks if f.feedback_type == FeedbackType.ACCEPT])

            performance[gate] = {
                'total': total,
                'acceptance_rate': accepts / total if total > 0 else 0,
                'rejection_rate': len([f for f in feedbacks if f.feedback_type == FeedbackType.REJECT]) / total if total > 0 else 0
            }

        return performance

    def _calculate_severity_performance(
        self,
        feedback_list: List[CorrectionFeedback]
    ) -> Dict[str, Dict[str, float]]:
        """Calculate performance metrics by severity"""
        severity_feedback: Dict[str, List[CorrectionFeedback]] = {}

        for feedback in feedback_list:
            sev = feedback.severity or 'unknown'
            if sev not in severity_feedback:
                severity_feedback[sev] = []
            severity_feedback[sev].append(feedback)

        performance = {}
        for sev, feedbacks in severity_feedback.items():
            total = len(feedbacks)
            accepts = len([f for f in feedbacks if f.feedback_type == FeedbackType.ACCEPT])

            performance[sev] = {
                'total': total,
                'acceptance_rate': accepts / total if total > 0 else 0
            }

        return performance

    def _identify_common_modifications(
        self,
        feedback_list: List[CorrectionFeedback]
    ) -> List[str]:
        """Identify common modification patterns"""
        modifications = [
            f.modification_reason
            for f in feedback_list
            if f.feedback_type == FeedbackType.MODIFY and f.modification_reason
        ]

        # Group similar modifications (simplified - would use NLP in production)
        from collections import Counter
        mod_counts = Counter(modifications)
        return [mod for mod, count in mod_counts.most_common(5)]

    def _calculate_trend(self, feedback_list: List[CorrectionFeedback]) -> str:
        """Calculate improvement trend"""
        # Sort by timestamp
        sorted_feedback = sorted(feedback_list, key=lambda f: f.timestamp)

        if len(sorted_feedback) < 10:
            return "insufficient_data"

        # Split into first half and second half
        mid = len(sorted_feedback) // 2
        first_half = sorted_feedback[:mid]
        second_half = sorted_feedback[mid:]

        first_acceptance = len([f for f in first_half if f.feedback_type == FeedbackType.ACCEPT]) / len(first_half)
        second_acceptance = len([f for f in second_half if f.feedback_type == FeedbackType.ACCEPT]) / len(second_half)

        if second_acceptance > first_acceptance + 0.05:
            return "improving"
        elif second_acceptance < first_acceptance - 0.05:
            return "declining"
        else:
            return "stable"

    def _identify_improvement_areas(
        self,
        rejection_rate: float,
        modification_rate: float,
        gate_performance: Dict[str, Dict[str, float]],
        top_rejections: List[tuple[str, int]],
        avg_accuracy: float,
        avg_usefulness: float,
        avg_clarity: float
    ) -> List[str]:
        """Identify areas that need improvement"""
        areas = []

        if rejection_rate > 0.2:
            areas.append("High rejection rate - review correction accuracy")

        if modification_rate > 0.3:
            areas.append("High modification rate - corrections may be too conservative or aggressive")

        # Find underperforming gates
        for gate, perf in gate_performance.items():
            if perf['acceptance_rate'] < 0.7:
                areas.append(f"Gate '{gate}' has low acceptance rate - review patterns")

        # Check ratings
        if avg_accuracy < 3.5:
            areas.append("Low accuracy ratings - improve pattern matching")

        if avg_usefulness < 3.5:
            areas.append("Low usefulness ratings - ensure corrections address real issues")

        if avg_clarity < 3.5:
            areas.append("Low clarity ratings - improve explanation quality")

        # Check rejection reasons
        if top_rejections:
            top_reason, count = top_rejections[0]
            areas.append(f"Most common rejection: '{top_reason}' - prioritize addressing this")

        return areas

    def export_feedback_report(
        self,
        analytics: FeedbackAnalytics
    ) -> Dict[str, Any]:
        """Export feedback analytics as report"""
        return {
            'summary': {
                'total_feedback': analytics.total_feedback,
                'acceptance_rate': f"{analytics.acceptance_rate:.1%}",
                'rejection_rate': f"{analytics.rejection_rate:.1%}",
                'modification_rate': f"{analytics.modification_rate:.1%}"
            },
            'performance': {
                'by_gate': analytics.gate_performance,
                'by_severity': analytics.severity_performance
            },
            'issues': {
                'top_rejection_reasons': [
                    {'reason': reason, 'count': count}
                    for reason, count in analytics.top_rejection_reasons
                ],
                'common_modifications': analytics.common_modifications
            },
            'ratings': {
                'accuracy': f"{analytics.average_accuracy_rating:.1f}/5",
                'usefulness': f"{analytics.average_usefulness_rating:.1f}/5",
                'clarity': f"{analytics.average_clarity_rating:.1f}/5"
            },
            'trends': {
                'improvement_trend': analytics.improvement_trend,
                'areas_for_improvement': analytics.areas_for_improvement
            }
        }

    def get_learning_recommendations(
        self,
        analytics: FeedbackAnalytics
    ) -> List[str]:
        """Generate learning recommendations based on feedback"""
        recommendations = []

        # Based on rejection reasons
        for reason, count in analytics.top_rejection_reasons[:3]:
            if reason == 'inaccurate':
                recommendations.append(
                    "Update pattern library with correct regulatory interpretations"
                )
            elif reason == 'inappropriate':
                recommendations.append(
                    "Improve context detection to better match document types"
                )
            elif reason == 'too_aggressive':
                recommendations.append(
                    "Reduce correction scope - prefer minimal changes"
                )
            elif reason == 'style_mismatch':
                recommendations.append(
                    "Enhance style matching to preserve document voice"
                )

        # Based on ratings
        if analytics.average_accuracy_rating < 4.0:
            recommendations.append(
                "Review and validate all correction patterns with legal experts"
            )

        if analytics.average_clarity_rating < 4.0:
            recommendations.append(
                "Improve explanation templates for better clarity"
            )

        # Based on trends
        if analytics.improvement_trend == 'declining':
            recommendations.append(
                "URGENT: Performance is declining - conduct comprehensive review"
            )

        return recommendations
